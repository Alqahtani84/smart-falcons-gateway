"""Leakage-safe pair and gallery/probe construction.

The single most important rule of the whole POC lives here:

  * Verification genuine pairs are taken **across different sessions** by default
    (`cross_session_only=True`). Same-session genuine pairs mostly measure "same
    photoshoot," not identity that persists over time — reporting those as the
    headline would be self-deception.
  * Identification uses a **gallery session** enrolled once and **probes from other
    sessions**, so no image is ever matched against itself.

Embeddings are assumed L2-normalized, so cosine similarity == dot product.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np


def build_verification_scores(
    embs: np.ndarray,
    ids: list[str],
    sessions: list[str],
    cross_session_only: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (genuine_scores, impostor_scores) as cosine similarities.

    genuine  = same bird (optionally different session)
    impostor = different bird
    """
    embs = np.asarray(embs, dtype=np.float32)
    ids = list(ids)
    sessions = list(sessions)
    genuine: list[float] = []
    impostor: list[float] = []
    for i, j in combinations(range(len(embs)), 2):
        s = float(embs[i] @ embs[j])
        if ids[i] == ids[j]:
            if cross_session_only and sessions[i] == sessions[j]:
                continue
            genuine.append(s)
        else:
            impostor.append(s)
    return np.asarray(genuine, dtype=np.float64), np.asarray(impostor, dtype=np.float64)


def gallery_probe_split(
    embs: np.ndarray,
    ids: list[str],
    sessions: list[str],
    gallery_session: str,
) -> tuple[np.ndarray, list[str], np.ndarray, list[str]]:
    """Enroll `gallery_session`; probe with all other sessions.

    Returns (gallery_embs, gallery_ids, probe_embs, probe_ids).
    """
    embs = np.asarray(embs, dtype=np.float32)
    g_idx = [k for k, s in enumerate(sessions) if s == gallery_session]
    p_idx = [k for k, s in enumerate(sessions) if s != gallery_session]
    g_embs = embs[g_idx] if g_idx else np.empty((0, embs.shape[1] if embs.ndim == 2 else 0))
    p_embs = embs[p_idx] if p_idx else np.empty((0, embs.shape[1] if embs.ndim == 2 else 0))
    g_ids = [ids[k] for k in g_idx]
    p_ids = [ids[k] for k in p_idx]
    return g_embs, g_ids, p_embs, p_ids
