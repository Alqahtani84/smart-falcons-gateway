"""Embedding extractors.

Two backends behind one interface (`embed_image(path) -> L2-normalized vector`):

- **DummyEmbedder** — deterministic, dependency-light (PIL only). A 16x16 grayscale
  signature. NOT for real biometrics — it exists so the whole POC harness (splits,
  metrics, report) can be tested end-to-end without torch or pilot data.

- **TimmEmbedder** — a frozen pretrained backbone via `timm` (DINOv2 by default;
  the plan's front-runner). Lazy-imports torch/timm so the harness loads without them.

Use `get_embedder(name)`: "dummy", or "dinov2" / "timm:<model_name>".
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


def _l2(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float32)
    return v / (np.linalg.norm(v) + 1e-8)


class DummyEmbedder:
    """Deterministic placeholder embedding (16x16 grayscale signature)."""

    name = "dummy"
    dim = 256

    def embed_image(self, path: Path) -> np.ndarray:
        with Image.open(path) as im:
            im = im.convert("L").resize((16, 16))
            v = np.asarray(im, dtype=np.float32).flatten()
        v = v - v.mean()
        return _l2(v)


class TimmEmbedder:
    """Frozen pretrained backbone (timm). Real embeddings; needs torch + timm."""

    def __init__(self, model_name: str = "vit_small_patch14_dinov2.lvd142m", device: str = "cpu"):
        try:
            import timm
            import torch
        except Exception as exc:  # pragma: no cover - depends on optional deps
            raise RuntimeError(
                "TimmEmbedder needs torch + timm. Install with:\n"
                "  pip install torch torchvision timm\n"
                f"(import error: {exc})"
            )
        self._torch = torch
        self.name = f"timm:{model_name}"
        self.device = device
        self.model = timm.create_model(model_name, pretrained=True, num_classes=0)
        self.model.eval().to(device)
        cfg = timm.data.resolve_data_config({}, model=self.model)
        self.transform = timm.data.create_transform(**cfg)
        self.dim = int(getattr(self.model, "num_features", 0)) or None

    def embed_image(self, path: Path) -> np.ndarray:
        with Image.open(path) as im:
            x = self.transform(im.convert("RGB")).unsqueeze(0).to(self.device)
        with self._torch.no_grad():
            feat = self.model(x).squeeze(0).cpu().numpy()
        return _l2(feat)


def get_embedder(name: str = "dummy", device: str = "cpu"):
    key = (name or "dummy").strip().lower()
    if key in ("dummy", "none"):
        return DummyEmbedder()
    if key in ("dinov2", "dino", "default"):
        return TimmEmbedder(device=device)
    if key.startswith("timm:"):
        return TimmEmbedder(model_name=name.split(":", 1)[1], device=device)
    raise ValueError(f"Unknown embedder '{name}'. Use 'dummy', 'dinov2', or 'timm:<model>'.")
