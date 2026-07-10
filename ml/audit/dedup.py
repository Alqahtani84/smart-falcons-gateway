"""Duplicate & near-duplicate detection.

Two layers:
  1. Exact-byte duplicates via MD5 (same file reposted).
  2. Near-duplicates via perceptual hashing (pHash) + Hamming clustering
     (crops, re-encodes, resizes, light edits of the same photo).

Why this matters: a mixed-source scrape is full of reposts. If two copies of the
same photo land on opposite sides of a train/test split they create a FAKE
"genuine pair" and the biometric metrics become meaningless. We must find and
collapse duplicates BEFORE any split or matching.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageFile

import imagehash

ImageFile.LOAD_TRUNCATED_IMAGES = True


def compute_phash(path: Path, hash_size: int = 16) -> Optional[imagehash.ImageHash]:
    """Perceptual hash of an image, or None if it cannot be read."""
    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            return imagehash.phash(img, hash_size=hash_size)
    except Exception:
        return None


def _bits(h: imagehash.ImageHash) -> np.ndarray:
    return h.hash.flatten().astype(np.uint8)


class _UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def cluster_near_duplicates(
    hashes: list[Optional[imagehash.ImageHash]],
    threshold: int = 8,
) -> list[int]:
    """Assign a cluster id to each hash; near-duplicates share an id.

    `threshold` = max Hamming distance (in bits) to treat two images as the same
    photo. With hash_size=16 the hash is 256 bits; 8 is a conservative default
    (only very close matches merge). `None` hashes get unique singleton ids.

    Returns a list of cluster ids aligned to the input order.
    """
    n = len(hashes)
    cluster_ids = [-1] * n

    valid_idx = [i for i, h in enumerate(hashes) if h is not None]
    if valid_idx:
        M = np.stack([_bits(hashes[i]) for i in valid_idx])  # (m, nbits) uint8 0/1
        uf = _UnionFind(len(valid_idx))
        # Pairwise Hamming via broadcasting, upper triangle only.
        for a in range(len(valid_idx)):
            if a + 1 >= len(valid_idx):
                break
            dist = np.count_nonzero(M[a] != M[a + 1:], axis=1)
            close = np.nonzero(dist <= threshold)[0]
            for k in close:
                uf.union(a, a + 1 + int(k))
        # Map union-find roots to compact, deterministic cluster ids.
        root_to_id: dict[int, int] = {}
        for local, global_i in enumerate(valid_idx):
            root = uf.find(local)
            if root not in root_to_id:
                root_to_id[root] = len(root_to_id)
            cluster_ids[global_i] = root_to_id[root]

    # Give unreadable images their own singleton cluster ids after the valid ones.
    next_id = (max(cluster_ids) + 1) if any(c >= 0 for c in cluster_ids) else 0
    for i in range(n):
        if cluster_ids[i] < 0:
            cluster_ids[i] = next_id
            next_id += 1
    return cluster_ids


def exact_duplicate_groups(md5s: list[Optional[str]]) -> dict[str, list[int]]:
    """Group image indices by identical MD5 (byte-identical files)."""
    groups: dict[str, list[int]] = {}
    for i, m in enumerate(md5s):
        if not m:
            continue
        groups.setdefault(m, []).append(i)
    return {m: idxs for m, idxs in groups.items() if len(idxs) > 1}
