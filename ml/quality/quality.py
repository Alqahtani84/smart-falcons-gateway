"""Whole-image quality proxy for the audit.

IMPORTANT SCOPE NOTE: true *eye-image* quality can only be judged after the eye
region is localized (next slice). Here we score the WHOLE image as a fast triage
proxy — enough to flag obviously unusable photos (tiny, blurred, blown-out, dark)
before we invest in eye detection. Do not treat these scores as biometric quality.

Metrics:
  - sharpness  : variance of the Laplacian (higher = sharper / more detail)
  - brightness : mean gray level (0-255)
  - contrast   : std of gray level
  - min_side   : shorter image dimension in pixels (resolution proxy)
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

# Heuristic thresholds — deliberately lenient; tune once we see real distributions.
SHARPNESS_MIN = 60.0        # variance-of-Laplacian below this ~ likely blurred
SHARPNESS_FULL = 300.0      # score saturates at 1.0 here
BRIGHTNESS_LO = 40.0
BRIGHTNESS_HI = 220.0
DEFAULT_MIN_SIDE = 256      # shorter side below this ~ too small for eye detail


def assess_quality(path: Path, min_side: int = DEFAULT_MIN_SIDE) -> dict:
    result: dict = {
        "quality_ok": False,
        "width": None,
        "height": None,
        "min_side": None,
        "sharpness": None,
        "brightness": None,
        "contrast": None,
        "sharp_score": None,
        "res_ok": None,
        "bright_ok": None,
        "sharp_ok": None,
        "quality_band": "unreadable",
        "error": None,
    }
    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            w, h = img.size
            arr = np.asarray(img)
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result

    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(gray.mean())
    contrast = float(gray.std())
    ms = int(min(w, h))

    res_ok = ms >= min_side
    bright_ok = BRIGHTNESS_LO <= brightness <= BRIGHTNESS_HI
    sharp_ok = sharpness >= SHARPNESS_MIN
    sharp_score = float(np.clip(sharpness / SHARPNESS_FULL, 0.0, 1.0))
    quality_ok = bool(res_ok and bright_ok and sharp_ok)

    if quality_ok and sharp_score >= 0.5 and ms >= min_side * 2:
        band = "good"
    elif quality_ok:
        band = "marginal"
    else:
        band = "poor"

    result.update(
        quality_ok=quality_ok,
        width=w,
        height=h,
        min_side=ms,
        sharpness=round(sharpness, 2),
        brightness=round(brightness, 2),
        contrast=round(contrast, 2),
        sharp_score=round(sharp_score, 3),
        res_ok=res_ok,
        bright_ok=bright_ok,
        sharp_ok=sharp_ok,
        quality_band=band,
        error=None,
    )
    return result
