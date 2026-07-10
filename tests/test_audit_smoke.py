"""End-to-end smoke test for the Track A audit.

Synthesizes a tiny dataset (no real falcon images needed) and checks that
inventory, dedup, and quality run and produce sane results. Run with:

    pip install -r requirements.txt pytest
    pytest -q
"""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from ml.audit import dedup, inventory
from ml.quality.quality import assess_quality


def _save(arr: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr.astype("uint8")).save(path)


@pytest.fixture()
def dataset(tmp_path: Path) -> Path:
    root = tmp_path / "raw"
    rng = np.random.RandomState(0)  # deterministic; Math.random-free

    # A sharp, textured "falcon A" image.
    a = rng.randint(0, 255, (400, 400, 3))
    _save(a, root / "sourceX" / "falconA.png")

    # Exact-byte duplicate of A (reposted).
    shutil.copy(root / "sourceX" / "falconA.png", root / "sourceY" / "falconA_repost.png")

    # Near-duplicate of A: same image, slight brightness shift + tiny crop.
    a_near = np.clip(a[2:, 2:, :] + 6, 0, 255)
    _save(a_near, root / "sourceY" / "falconA_edited.jpg")

    # A different, unrelated image "falcon B".
    b = rng.randint(0, 255, (350, 500, 3))
    _save(b, root / "sourceX" / "falconB.png")

    # A tiny, low-res image that should fail the resolution gate.
    small = rng.randint(0, 255, (64, 64, 3))
    _save(small, root / "falconTiny.png")

    return root


def test_inventory_counts_and_groups(dataset: Path):
    records = inventory.build_inventory(dataset)
    assert len(records) == 5
    assert all(r.decode_ok for r in records)
    groups = {r.group for r in records}
    assert {"sourceX", "sourceY", "(root)"} <= groups
    # md5 present for all files
    assert all(r.md5 for r in records)


def test_exact_and_near_duplicates(dataset: Path):
    records = inventory.build_inventory(dataset)
    rel_paths = [r.rel_path for r in records]

    # Exact-byte duplicates: the two identical PNGs.
    exact = dedup.exact_duplicate_groups([r.md5 for r in records])
    exact_sizes = sorted(len(v) for v in exact.values())
    assert exact_sizes == [2]

    # Near-duplicate clustering: A, its repost, and its edit should share a cluster.
    hashes = [dedup.compute_phash(dataset / rp) for rp in rel_paths]
    clusters = dedup.cluster_near_duplicates(hashes, threshold=12)
    by_cluster: dict[int, list[str]] = {}
    for rp, c in zip(rel_paths, clusters):
        by_cluster.setdefault(c, []).append(rp)
    biggest = max(by_cluster.values(), key=len)
    assert len(biggest) >= 3  # the three A-variants collapse together


def test_quality_flags_small_image(dataset: Path):
    q_small = assess_quality(dataset / "falconTiny.png", min_side=256)
    assert q_small["res_ok"] is False
    assert q_small["quality_band"] in {"poor", "unreadable"}

    q_big = assess_quality(dataset / "sourceX" / "falconB.png", min_side=256)
    assert q_big["res_ok"] is True
    assert q_big["error"] is None
