"""Biometric evaluation metrics.

Verification (1:1) from genuine/impostor similarity scores:
  FAR, FRR, EER, ROC-AUC, TAR @ FAR = 1% and 0.1%.
Identification (1:N) via nearest-neighbor over a gallery:
  Top-1, Top-5 (configurable).
"""
from __future__ import annotations

import numpy as np

try:
    from sklearn.metrics import roc_auc_score, roc_curve
    _HAVE_SK = True
except Exception:  # pragma: no cover
    _HAVE_SK = False


def verification_metrics(genuine: np.ndarray, impostor: np.ndarray) -> dict:
    """Threshold-swept verification metrics from similarity scores (higher = more similar)."""
    genuine = np.asarray(genuine, dtype=np.float64)
    impostor = np.asarray(impostor, dtype=np.float64)
    out = {
        "n_genuine": int(genuine.size),
        "n_impostor": int(impostor.size),
        "EER": float("nan"),
        "EER_threshold": float("nan"),
        "ROC_AUC": float("nan"),
        "TAR_at_FAR_1pct": float("nan"),
        "TAR_at_FAR_0.1pct": float("nan"),
        "genuine_mean": float(genuine.mean()) if genuine.size else float("nan"),
        "impostor_mean": float(impostor.mean()) if impostor.size else float("nan"),
        "_roc": None,
    }
    if genuine.size == 0 or impostor.size == 0:
        return out

    y = np.concatenate([np.ones_like(genuine), np.zeros_like(impostor)])
    s = np.concatenate([genuine, impostor])

    if _HAVE_SK:
        fpr, tpr, thr = roc_curve(y, s)
        try:
            out["ROC_AUC"] = float(roc_auc_score(y, s))
        except Exception:
            pass
    else:  # minimal fallback ROC
        thr = np.unique(s)[::-1]
        tpr = np.array([(genuine >= t).mean() for t in thr])
        fpr = np.array([(impostor >= t).mean() for t in thr])
        out["ROC_AUC"] = float(np.trapz(tpr, fpr))

    fnr = 1.0 - tpr
    idx = int(np.nanargmin(np.abs(fpr - fnr)))
    out["EER"] = float((fpr[idx] + fnr[idx]) / 2.0)
    if idx < len(thr):
        out["EER_threshold"] = float(thr[idx])

    def tar_at_far(target: float) -> float:
        ok = np.where(fpr <= target)[0]
        return float(tpr[ok[-1]]) if ok.size else float("nan")

    out["TAR_at_FAR_1pct"] = tar_at_far(0.01)
    out["TAR_at_FAR_0.1pct"] = tar_at_far(0.001)
    out["_roc"] = {"fpr": np.asarray(fpr).tolist(), "tpr": np.asarray(tpr).tolist()}
    return out


def identification_metrics(
    gallery_embs: np.ndarray,
    gallery_ids: list[str],
    probe_embs: np.ndarray,
    probe_ids: list[str],
    ks: tuple[int, ...] = (1, 5),
) -> dict:
    """Nearest-neighbor identification. Assumes L2-normalized embeddings (cosine = dot)."""
    gallery_embs = np.asarray(gallery_embs, dtype=np.float32)
    probe_embs = np.asarray(probe_embs, dtype=np.float32)
    out = {f"Top{k}": float("nan") for k in ks}
    out.update(n_gallery=int(len(gallery_ids)), n_probe=int(len(probe_ids)))
    if gallery_embs.size == 0 or probe_embs.size == 0:
        return out

    gids = np.asarray(gallery_ids)
    pids = np.asarray(probe_ids)
    sims = probe_embs @ gallery_embs.T           # (n_probe, n_gallery)
    order = np.argsort(-sims, axis=1)            # best first
    ranked = gids[order]                         # ranked gallery ids per probe
    max_k = min(max(ks), ranked.shape[1])
    for k in ks:
        kk = min(k, max_k)
        hits = [pids[i] in ranked[i, :kk] for i in range(len(pids))]
        out[f"Top{k}"] = float(np.mean(hits)) if hits else float("nan")
    return out
