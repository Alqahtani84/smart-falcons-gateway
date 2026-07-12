"""Optional plots for the POC report (ROC + score histograms). No-op if matplotlib absent."""
from __future__ import annotations

from pathlib import Path

import numpy as np


def save_plots(out_dir: Path, roc: dict | None, genuine: np.ndarray, impostor: np.ndarray) -> list[Path]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return []

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    if roc and roc.get("fpr") and roc.get("tpr"):
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.plot(roc["fpr"], roc["tpr"], label="ROC")
        ax.plot([0, 1], [0, 1], "--", color="gray", linewidth=1)
        ax.set_xlabel("FAR (false accept rate)")
        ax.set_ylabel("TAR (true accept rate)")
        ax.set_title("Verification ROC")
        ax.legend()
        p = out_dir / "roc.png"
        fig.savefig(p, dpi=120, bbox_inches="tight")
        plt.close(fig)
        paths.append(p)

    genuine = np.asarray(genuine)
    impostor = np.asarray(impostor)
    if genuine.size and impostor.size:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(impostor, bins=30, alpha=0.6, label="impostor", density=True)
        ax.hist(genuine, bins=30, alpha=0.6, label="genuine", density=True)
        ax.set_xlabel("cosine similarity")
        ax.set_ylabel("density")
        ax.set_title("Genuine vs impostor score distributions")
        ax.legend()
        p = out_dir / "score_hist.png"
        fig.savefig(p, dpi=120, bbox_inches="tight")
        plt.close(fig)
        paths.append(p)

    return paths
