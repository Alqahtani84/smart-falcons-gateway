"""Leakage-safe biometric POC over the Track B pilot data.

Flow: parse pilot/ -> embed eye crops -> cross-session verification (EER/AUC/TAR)
+ gallery/probe identification (Top-1/5) -> report.md + plots.

Usage (once pilot images exist):
  python -m scripts.run_poc --pilot ".../falcon-dataset/pilot" --embedder dinov2 --out outputs/poc

Until real embeddings are wanted, use --embedder dummy to exercise the full harness.
This script REFUSES to fabricate a verdict: if the pilot lacks ≥2 birds or any bird
with ≥2 sessions, it explains what's missing and exits without fake metrics.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.embeddings.extractor import get_embedder  # noqa: E402
from ml.evaluation.metrics import identification_metrics, verification_metrics  # noqa: E402
from ml.evaluation.pairs import build_verification_scores, gallery_probe_split  # noqa: E402
from ml.evaluation.plots import save_plots  # noqa: E402
from ml.poc.pilot_data import parse_pilot_dir, summarize  # noqa: E402


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Falcon eye biometric POC (leakage-safe)")
    p.add_argument("--pilot", required=True, help="Path to pilot/ folder")
    p.add_argument("--out", default="outputs/poc", help="Output directory")
    p.add_argument("--embedder", default="dummy", help="'dummy' | 'dinov2' | 'timm:<model>'")
    p.add_argument("--eye", default="both", choices=["both", "left", "right"], help="Eye side filter")
    p.add_argument("--gallery-session", default=None, help="Session to enroll (default: smallest label)")
    p.add_argument("--same-session", action="store_true",
                   help="ALSO allow same-session genuine pairs (NOT recommended; inflates results)")
    p.add_argument("--no-plots", action="store_true")
    return p.parse_args(argv)


def _fail(out: Path, msg: str) -> int:
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text(f"# POC — insufficient data\n\n{msg}\n", encoding="utf-8")
    print(msg)
    return 1


def main(argv=None) -> int:
    args = parse_args(argv)
    pilot = Path(args.pilot)
    out = Path(args.out)
    if not pilot.exists():
        return _fail(out, f"Pilot path does not exist: {pilot}\nSee docs/PILOT_PLAN_MINIMAL.md.")

    records = parse_pilot_dir(pilot)
    if args.eye != "both":
        records = [r for r in records if r.eye == args.eye]
    summ = summarize(records)

    # Guardrails — refuse to produce a verdict on inadequate data.
    if summ["n_images"] == 0:
        return _fail(out, "No pilot images found. Capture some per docs/PILOT_PLAN_MINIMAL.md.")
    if summ["n_birds"] < 2:
        return _fail(out, f"Need ≥2 distinct birds for any metric; found {summ['n_birds']}.")
    if not summ["birds_with_multiple_sessions"] and not args.same_session:
        return _fail(
            out,
            "No bird has ≥2 sessions, so cross-session (the honest) evaluation is impossible.\n"
            "Capture a second session on a different day (docs/PILOT_PLAN_MINIMAL.md), or re-run "
            "with --same-session to get an OPTIMISTIC same-session-only sanity check.",
        )

    # Embed.
    print(f"Embedding {summ['n_images']} images with '{args.embedder}' ...")
    embedder = get_embedder(args.embedder)
    embs, ids, sessions, eyes = [], [], [], []
    for r in tqdm(records, desc="embed", unit="img"):
        try:
            embs.append(embedder.embed_image(Path(r.abs_path)))
            ids.append(r.bird_id)
            sessions.append(r.session)
            eyes.append(r.eye)
        except Exception as exc:
            print(f"  skip {r.rel_path}: {exc}")
    embs = np.vstack(embs)
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "embeddings.npy", embs)
    (out / "embeddings_meta.json").write_text(
        json.dumps({"ids": ids, "sessions": sessions, "eyes": eyes}, ensure_ascii=False), encoding="utf-8"
    )

    # Verification (cross-session by default).
    genuine, impostor = build_verification_scores(
        embs, ids, sessions, cross_session_only=not args.same_session
    )
    ver = verification_metrics(genuine, impostor)

    # Identification (enroll one session, probe the rest).
    gallery_session = args.gallery_session or min(summ["sessions"])
    g_e, g_i, p_e, p_i = gallery_probe_split(embs, ids, sessions, gallery_session)
    ident = identification_metrics(g_e, g_i, p_e, p_i)

    plots = [] if args.no_plots else save_plots(out, ver.get("_roc"), genuine, impostor)

    _write_report(out, args, summ, ver, ident, gallery_session, plots)
    print(f"\nDone. Report: {out / 'report.md'}")
    print(f"  Verification: EER={ver['EER']:.3f}  AUC={ver['ROC_AUC']:.3f}  "
          f"TAR@FAR1%={ver['TAR_at_FAR_1pct']:.3f}  (genuine={ver['n_genuine']}, impostor={ver['n_impostor']})")
    print(f"  Identification: Top1={ident['Top1']:.3f}  Top5={ident['Top5']:.3f}  "
          f"(gallery={ident['n_gallery']}, probe={ident['n_probe']})")
    return 0


def _write_report(out, args, summ, ver, ident, gallery_session, plots) -> None:
    L = []
    a = L.append
    a("# Falcon Eye Biometric — POC Report\n")
    a(f"- Embedder: **{args.embedder}**  |  Eye filter: **{args.eye}**  |  "
      f"Genuine pairs: **{'cross-session' if not args.same_session else 'same-session ALLOWED'}**")
    if args.embedder == "dummy":
        a("\n> ⚠️ **Dummy embedder** — this is a plumbing/sanity run, NOT a real biometric result. "
          "Re-run with `--embedder dinov2` for meaningful numbers.")
    if args.same_session:
        a("\n> ⚠️ **Same-session genuine pairs allowed** — optimistic; does not prove identity over time.")

    a("\n## Dataset")
    a(f"- Images: **{summ['n_images']}**  |  Birds: **{summ['n_birds']}**  |  Sessions: **{summ['n_sessions']}**")
    a(f"- Birds with ≥2 sessions: **{len(summ['birds_with_multiple_sessions'])}**")

    a("\n## Verification (1:1)")
    a(f"- **EER: {ver['EER']:.3f}**  (lower is better)")
    a(f"- ROC-AUC: {ver['ROC_AUC']:.3f}")
    a(f"- TAR @ FAR=1%: {ver['TAR_at_FAR_1pct']:.3f}   |   TAR @ FAR=0.1%: {ver['TAR_at_FAR_0.1pct']:.3f}")
    a(f"- genuine pairs: {ver['n_genuine']}  |  impostor pairs: {ver['n_impostor']}")
    a(f"- mean genuine sim: {ver['genuine_mean']:.3f}  |  mean impostor sim: {ver['impostor_mean']:.3f}")

    a("\n## Identification (1:N)")
    a(f"- Gallery session: **{gallery_session}**  (probes = other sessions)")
    a(f"- **Top-1: {ident['Top1']:.3f}**   |   Top-5: {ident['Top5']:.3f}")
    a(f"- gallery size: {ident['n_gallery']}  |  probes: {ident['n_probe']}")

    if plots:
        a("\n## Plots")
        for p in plots:
            a(f"- `{Path(p).name}`")

    a("\n## Read this before trusting the numbers")
    a("- Metrics are only as good as the pilot. Small bird counts → wide error bars.")
    a("- Compare against pre-registered go/no-go bands in `docs/PILOT_PLAN_MINIMAL.md`.")
    a("- Deduplicate captures and keep left/right separable if you filtered by eye.")
    (out / "report.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
