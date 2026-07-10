"""Track A dataset audit — entrypoint.

Runs, over a read-only raw image folder:
  1. Inventory      -> manifest.csv
  2. Dedup          -> duplicates.csv  (exact MD5 + perceptual near-dup clusters)
  3. Quality proxy  -> quality.csv
  4. Human summary  -> summary.md

Usage:
  python -m scripts.run_audit --raw "C:/.../falcon-dataset/raw" --out outputs/audit

Nothing in the raw folder is modified. All outputs go under --out.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

# Make repo root importable when run as a plain script too.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.audit import dedup, inventory  # noqa: E402
from ml.audit.inventory import column_order  # noqa: E402
from ml.quality.quality import assess_quality  # noqa: E402


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Smart Falcons Gateway — Track A dataset audit")
    p.add_argument("--raw", required=True, help="Path to the raw image folder (read-only)")
    p.add_argument("--out", default="outputs/audit", help="Output directory for reports")
    p.add_argument("--hash-size", type=int, default=16, help="Perceptual hash size (default 16 -> 256-bit)")
    p.add_argument("--dup-threshold", type=int, default=8, help="Max Hamming distance for near-dup merge")
    p.add_argument("--min-side", type=int, default=256, help="Min shorter-side px for quality res_ok")
    p.add_argument("--limit", type=int, default=None, help="Cap number of images (quick test runs)")
    p.add_argument("--no-dedup", action="store_true", help="Skip duplicate detection")
    p.add_argument("--no-quality", action="store_true", help="Skip quality scoring")
    return p.parse_args(argv)


def run_inventory(raw: Path, limit) -> pd.DataFrame:
    print(f"[1/4] Inventorying images under: {raw}")
    records = inventory.build_inventory(raw, limit=limit)
    df = pd.DataFrame(inventory.records_to_rows(records), columns=column_order())
    if not inventory.HEIF_SUPPORTED:
        print("      (note: pillow-heif not installed — HEIC/HEIF files will fail to decode)")
    print(f"      found {len(df)} image files "
          f"({int(df['decode_ok'].sum())} decodable)")
    return df


def run_dedup(raw: Path, manifest: pd.DataFrame, hash_size: int, threshold: int) -> pd.DataFrame:
    print("[2/4] Detecting exact + near-duplicates ...")
    rel_paths = manifest["rel_path"].tolist()
    hashes = [
        dedup.compute_phash(raw / rp, hash_size=hash_size)
        for rp in tqdm(rel_paths, desc="      phash", unit="img")
    ]
    cluster_ids = dedup.cluster_near_duplicates(hashes, threshold=threshold)
    sizes: dict[int, int] = {}
    for c in cluster_ids:
        sizes[c] = sizes.get(c, 0) + 1

    exact = dedup.exact_duplicate_groups(manifest["md5"].tolist())
    idx_to_md5group = {}
    for md5, idxs in exact.items():
        for i in idxs:
            idx_to_md5group[i] = md5

    out = pd.DataFrame({
        "rel_path": rel_paths,
        "phash_cluster_id": cluster_ids,
        "phash_cluster_size": [sizes[c] for c in cluster_ids],
        "is_near_duplicate": [sizes[c] > 1 for c in cluster_ids],
        "exact_md5_group": [idx_to_md5group.get(i, "") for i in range(len(rel_paths))],
        "is_exact_duplicate": [i in idx_to_md5group for i in range(len(rel_paths))],
    })
    n_near = int(out["is_near_duplicate"].sum())
    n_clusters = sum(1 for s in sizes.values() if s > 1)
    print(f"      {n_near} images in {n_clusters} near-duplicate clusters; "
          f"{out['is_exact_duplicate'].sum()} exact-byte duplicates")
    return out


def run_quality(raw: Path, manifest: pd.DataFrame, min_side: int) -> pd.DataFrame:
    print("[3/4] Scoring whole-image quality (proxy) ...")
    rows = []
    for rp in tqdm(manifest["rel_path"].tolist(), desc="      quality", unit="img"):
        q = assess_quality(raw / rp, min_side=min_side)
        q["rel_path"] = rp
        rows.append(q)
    df = pd.DataFrame(rows)
    cols = ["rel_path"] + [c for c in df.columns if c != "rel_path"]
    df = df[cols]
    band_counts = df["quality_band"].value_counts().to_dict()
    print(f"      quality bands: {band_counts}")
    return df


def write_summary(out_dir: Path, raw: Path, manifest, dup, qual) -> Path:
    print("[4/4] Writing summary ...")
    lines: list[str] = []
    a = lines.append
    a("# Track A — Dataset Audit Summary\n")
    a(f"Source: `{raw}`\n")
    a("> Track A screens the mixed-source collection and builds tooling. "
      "It **cannot** certify biometric feasibility — that requires the Track B pilot.\n")

    total = len(manifest)
    decodable = int(manifest["decode_ok"].sum()) if total else 0
    a("## Inventory\n")
    a(f"- Total image files: **{total}**")
    a(f"- Decodable: **{decodable}**  |  Failed to decode: **{total - decodable}**")

    if total:
        a("\n### By source group (top-level subfolder)\n")
        grp = manifest["group"].value_counts()
        a("| group | images |")
        a("|---|---|")
        for name, cnt in grp.items():
            a(f"| {name} | {cnt} |")

        a("\n### By format\n")
        fmt = manifest["ext"].value_counts()
        a("| ext | images |")
        a("|---|---|")
        for name, cnt in fmt.items():
            a(f"| {name} | {cnt} |")

        ok = manifest[manifest["decode_ok"]]
        if len(ok):
            a("\n### Resolution (decodable images)\n")
            mp = ok["megapixels"].dropna()
            if len(mp):
                a(f"- Megapixels — min {mp.min():.2f}, median {mp.median():.2f}, max {mp.max():.2f}")
            a(f"- Images with EXIF camera model: "
              f"**{int(ok['camera_model'].notna().sum())} / {len(ok)}**")
            a(f"- Images with EXIF capture datetime: "
              f"**{int(ok['exif_datetime'].notna().sum())} / {len(ok)}**")

    if dup is not None:
        n_near = int(dup["is_near_duplicate"].sum())
        n_clusters = int(dup.loc[dup["is_near_duplicate"], "phash_cluster_id"].nunique())
        n_exact = int(dup["is_exact_duplicate"].sum())
        a("\n## Duplicates\n")
        a(f"- Exact-byte duplicates: **{n_exact}**")
        a(f"- Images in near-duplicate clusters: **{n_near}** across **{n_clusters}** clusters")
        a("- ⚠️ Duplicates must be collapsed before any train/test split to avoid fake genuine pairs.")

    if qual is not None:
        a("\n## Quality (whole-image proxy)\n")
        bands = qual["quality_band"].value_counts().to_dict()
        for band in ("good", "marginal", "poor", "unreadable"):
            a(f"- {band}: **{bands.get(band, 0)}**")
        a("\n> Real eye-region quality is assessed after eye detection (next slice).")

    a("\n## Key questions this audit answers\n")
    a("- How many images / how many usable? (see inventory + quality)")
    a("- How contaminated by reposts? (see duplicates)")
    a("- Any capture metadata to lean on? (EXIF camera/datetime counts above)")
    a("\n## Next\n")
    a("- Confirm near-duplicate clusters by eye, then mine clusters for *recurring individuals*.")
    a("- Kick off Track B pilot capture (see `docs/PILOT_CAPTURE_PROTOCOL.md`).")

    summary_path = out_dir / "summary.md"
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return summary_path


def main(argv=None) -> int:
    args = parse_args(argv)
    raw = Path(args.raw)
    if not raw.exists():
        print(f"ERROR: raw path does not exist: {raw}", file=sys.stderr)
        print("Create it and copy images in, then re-run. See README.", file=sys.stderr)
        return 2

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = run_inventory(raw, args.limit)
    manifest.to_csv(out_dir / "manifest.csv", index=False, encoding="utf-8")

    if len(manifest) == 0:
        print("No images found. Nothing else to do.")
        write_summary(out_dir, raw, manifest, None, None)
        return 0

    dup = None if args.no_dedup else run_dedup(raw, manifest, args.hash_size, args.dup_threshold)
    if dup is not None:
        dup.to_csv(out_dir / "duplicates.csv", index=False, encoding="utf-8")

    qual = None if args.no_quality else run_quality(raw, manifest, args.min_side)
    if qual is not None:
        qual.to_csv(out_dir / "quality.csv", index=False, encoding="utf-8")

    summary_path = write_summary(out_dir, raw, manifest, dup, qual)
    print(f"\nDone. Reports in: {out_dir}")
    print(f"  - manifest.csv   ({len(manifest)} rows)")
    if dup is not None:
        print("  - duplicates.csv")
    if qual is not None:
        print("  - quality.csv")
    print(f"  - {summary_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
