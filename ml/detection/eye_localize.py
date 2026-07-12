"""Eye / iris localization for falcon eye photos — classical CV first pass.

Why classical (not a deep detector): the raw set is already close-ups of falcon
eyes, and no off-the-shelf falcon-eye detector exists. A Hough-circle approach
finds the roughly circular pupil/iris directly, needs only OpenCV (already a
dependency), runs instantly, and requires no model download or GPU. It is a
SCREENING tool — good enough to crop and to judge whether iris texture is
resolvable. A learned keypoint detector is a future upgrade if the pilot needs it.

Pipeline: locate_eye() -> crop_eye() -> (optional) draw_overlay() for human QA.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


def load_bgr(path: Path) -> np.ndarray:
    """Load an image as an OpenCV BGR array (handles HEIC via PIL/pillow-heif)."""
    with Image.open(path) as img:
        arr = np.asarray(img.convert("RGB"))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def _darkness_score(gray: np.ndarray, x: int, y: int, r: int) -> float:
    """How much darker the circle interior (pupil) is than its surrounding ring.

    A real eye has a dark pupil inside a lighter iris/periocular ring, so a high
    score means the circle really sits on an eye rather than on flat background.
    """
    h, w = gray.shape
    r_in = max(1, int(r * 0.6))
    r_out = int(r * 1.4)
    mask_in = np.zeros((h, w), np.uint8)
    cv2.circle(mask_in, (x, y), r_in, 255, -1)
    mask_ring = np.zeros((h, w), np.uint8)
    cv2.circle(mask_ring, (x, y), r_out, 255, -1)
    cv2.circle(mask_ring, (x, y), r, 0, -1)
    inside = gray[mask_in == 255]
    ring = gray[mask_ring == 255]
    if inside.size == 0 or ring.size == 0:
        return -1e9
    return float(ring.mean() - inside.mean())


def locate_eye(image_bgr: np.ndarray, detect_max_dim: int = 1000) -> dict:
    """Locate the eye (pupil/iris circle). Returns a detection dict in FULL-RES coords.

    Keys: found(bool), method, confidence(0..1), cx, cy, r, img_w, img_h,
          darkness (raw interior/ring contrast).
    Never raises for a normal image; falls back to a centered circle if nothing
    convincing is found (found=False) so downstream cropping still works.
    """
    h, w = image_bgr.shape[:2]
    scale = min(1.0, detect_max_dim / float(max(h, w)))
    if scale < 1.0:
        small = cv2.resize(image_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    else:
        small = image_bgr
    gray = cv2.medianBlur(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), 5)
    sh, sw = gray.shape
    min_r = int(0.10 * min(sh, sw))
    max_r = int(0.60 * min(sh, sw))

    best = None
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=min(sh, sw),
        param1=100, param2=30, minRadius=min_r, maxRadius=max_r,
    )
    if circles is not None:
        best_score = -1e18
        for x, y, r in np.around(circles[0]).astype(int):
            dark = _darkness_score(gray, x, y, r)
            centrality = np.hypot(x - sw / 2.0, y - sh / 2.0) / (np.hypot(sw, sh) / 2.0)
            score = dark - 20.0 * centrality  # prefer dark-centered circles
            if score > best_score:
                best_score = score
                best = (float(x), float(y), float(r), float(dark))

    if best is None:
        r = 0.35 * min(sh, sw)
        det = dict(found=False, method="center-fallback", confidence=0.0,
                   cx=sw / 2.0, cy=sh / 2.0, r=r, darkness=0.0)
    else:
        x, y, r, dark = best
        det = dict(found=True, method="hough",
                   confidence=float(np.clip(dark / 60.0, 0.0, 1.0)),
                   cx=x, cy=y, r=r, darkness=dark)

    inv = 1.0 / scale
    det["cx"] *= inv
    det["cy"] *= inv
    det["r"] *= inv
    det["img_w"], det["img_h"] = w, h
    return det


def crop_eye(image_bgr: np.ndarray, det: dict, out_size: int = 512, margin: float = 2.2) -> Optional[np.ndarray]:
    """Square crop centered on the eye, padded by reflection if it runs off-edge."""
    cx, cy, r = det["cx"], det["cy"], det["r"]
    half = r * margin
    x0, y0 = int(round(cx - half)), int(round(cy - half))
    x1, y1 = int(round(cx + half)), int(round(cy + half))
    h, w = image_bgr.shape[:2]
    pad_l, pad_t = max(0, -x0), max(0, -y0)
    pad_r, pad_b = max(0, x1 - w), max(0, y1 - h)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
    crop = image_bgr[ya:yb, xa:xb]
    if crop.size == 0:
        return None
    if pad_l or pad_t or pad_r or pad_b:
        crop = cv2.copyMakeBorder(crop, pad_t, pad_b, pad_l, pad_r, cv2.BORDER_REFLECT)
    return cv2.resize(crop, (out_size, out_size), interpolation=cv2.INTER_AREA)


def draw_overlay(image_bgr: np.ndarray, det: dict, margin: float = 2.2) -> np.ndarray:
    """Draw the detected eye circle + crop box for human QA (green=found, red=fallback)."""
    out = image_bgr.copy()
    cx, cy, r = int(det["cx"]), int(det["cy"]), int(det["r"])
    thick = max(2, r // 40)
    color = (0, 255, 0) if det.get("found") else (0, 0, 255)
    cv2.circle(out, (cx, cy), r, color, thick)
    cv2.circle(out, (cx, cy), max(2, thick), color, -1)
    half = int(r * margin)
    cv2.rectangle(out, (cx - half, cy - half), (cx + half, cy + half), (255, 255, 0), thick)
    return out
