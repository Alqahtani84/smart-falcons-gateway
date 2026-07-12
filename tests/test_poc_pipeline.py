"""End-to-end POC pipeline test with the dummy embedder on a synthetic pilot tree.

Verifies folder parsing, embedding, cross-session pairing, and both metric paths
run and behave sanely (same-bird more similar than different-bird).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from ml.embeddings.extractor import get_embedder
from ml.evaluation.metrics import identification_metrics, verification_metrics
from ml.evaluation.pairs import build_verification_scores, gallery_probe_split
from ml.poc.pilot_data import parse_pilot_dir, summarize


def _bird_image(bird: int, session: int, size: int = 64) -> np.ndarray:
    yy, xx = np.mgrid[0:size, 0:size].astype(float)
    base = np.sin(2 * np.pi * (xx / size * (bird + 1))) + np.cos(2 * np.pi * (yy / size * (bird + 1)))
    img = ((base + 2) / 4 * 255).astype(np.uint8)
    img = np.clip(img.astype(int) + session * 3, 0, 255).astype(np.uint8)  # tiny per-session shift
    return np.stack([img, img, img], axis=-1)


def _make_pilot(root: Path, n_birds=4, n_sessions=2, per=3) -> None:
    for b in range(n_birds):
        for s in range(1, n_sessions + 1):
            for eye in ("left", "right"):
                d = root / f"F{b:02d}" / f"S{s}" / eye
                d.mkdir(parents=True, exist_ok=True)
                for k in range(per):
                    Image.fromarray(_bird_image(b, s)).save(d / f"img{k}.png")


def test_pipeline_parses_and_scores(tmp_path: Path):
    root = tmp_path / "pilot"
    _make_pilot(root)

    records = parse_pilot_dir(root)
    summ = summarize(records)
    assert summ["n_birds"] == 4 and summ["n_sessions"] == 2
    assert len(summ["birds_with_multiple_sessions"]) == 4
    assert {r.eye for r in records} == {"left", "right"}

    embedder = get_embedder("dummy")
    embs = np.vstack([embedder.embed_image(Path(r.abs_path)) for r in records])
    ids = [r.bird_id for r in records]
    sessions = [r.session for r in records]

    genuine, impostor = build_verification_scores(embs, ids, sessions, cross_session_only=True)
    ver = verification_metrics(genuine, impostor)
    assert ver["n_genuine"] > 0 and ver["n_impostor"] > 0
    # distinct per-bird patterns -> same bird should look more alike than different birds
    assert ver["genuine_mean"] > ver["impostor_mean"]

    g_e, g_i, p_e, p_i = gallery_probe_split(embs, ids, sessions, "S1")
    ident = identification_metrics(g_e, g_i, p_e, p_i)
    assert ident["n_gallery"] > 0 and ident["n_probe"] > 0
    assert ident["Top1"] >= 0.5    # well above 1/4 chance
