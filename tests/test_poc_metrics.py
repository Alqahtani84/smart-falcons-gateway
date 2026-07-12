"""Metric-math tests on synthetic embeddings (no images, no torch).

Two anchors:
  * separable identities  -> EER near 0, AUC near 1, Top-1 near 1
  * structureless random   -> EER near 0.5 (a detector that "works" on noise is broken)
"""
from __future__ import annotations

import numpy as np

from ml.evaluation.metrics import identification_metrics, verification_metrics
from ml.evaluation.pairs import build_verification_scores, gallery_probe_split


def _make_identity_embeddings(n_ids=6, n_sessions=2, per=4, dim=32, noise=0.05):
    rng = np.random.RandomState(0)
    centers = rng.randn(n_ids, dim)
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)
    embs, ids, sessions = [], [], []
    for b in range(n_ids):
        for s in range(n_sessions):
            for _ in range(per):
                v = centers[b] + noise * rng.randn(dim)
                embs.append(v / np.linalg.norm(v))
                ids.append(f"F{b}")
                sessions.append(f"S{s + 1}")
    return np.asarray(embs), ids, sessions


def test_separable_identities_low_eer_high_top1():
    embs, ids, sessions = _make_identity_embeddings(noise=0.05)
    genuine, impostor = build_verification_scores(embs, ids, sessions, cross_session_only=True)
    ver = verification_metrics(genuine, impostor)
    assert ver["n_genuine"] > 0 and ver["n_impostor"] > 0
    assert ver["EER"] < 0.10
    assert ver["ROC_AUC"] > 0.90
    assert ver["genuine_mean"] > ver["impostor_mean"]

    g_e, g_i, p_e, p_i = gallery_probe_split(embs, ids, sessions, "S1")
    ident = identification_metrics(g_e, g_i, p_e, p_i)
    assert ident["Top1"] > 0.90
    assert ident["Top5"] >= ident["Top1"]


def test_random_embeddings_eer_near_half():
    rng = np.random.RandomState(1)
    n, dim = 80, 32
    embs = rng.randn(n, dim)
    embs /= np.linalg.norm(embs, axis=1, keepdims=True)
    ids = [f"F{k % 8}" for k in range(n)]           # each id appears in both sessions
    sessions = [f"S{(k // 8) % 2 + 1}" for k in range(n)]
    genuine, impostor = build_verification_scores(embs, ids, sessions, cross_session_only=True)
    ver = verification_metrics(genuine, impostor)
    assert 0.35 < ver["EER"] < 0.65    # no real structure -> chance-level


def test_cross_session_excludes_same_session_pairs():
    embs, ids, sessions = _make_identity_embeddings(n_ids=3, n_sessions=2, per=3)
    g_cross, _ = build_verification_scores(embs, ids, sessions, cross_session_only=True)
    g_all, _ = build_verification_scores(embs, ids, sessions, cross_session_only=False)
    assert g_all.size > g_cross.size    # allowing same-session adds genuine pairs
