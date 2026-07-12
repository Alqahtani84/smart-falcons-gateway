"""Smoke test for eye localization on a synthetic eye.

Draws a dark pupil inside a lighter iris ring on a light background — the exact
structure the Hough-circle localizer targets — and checks it's found near the
known center. Run: pytest -q
"""
from __future__ import annotations

import cv2
import numpy as np

from ml.detection.eye_localize import crop_eye, draw_overlay, locate_eye


def _synthetic_eye(h=600, w=700, cx=340, cy=300, pupil_r=55, iris_r=130) -> np.ndarray:
    img = np.full((h, w, 3), 200, np.uint8)          # light background
    cv2.circle(img, (cx, cy), iris_r, (90, 110, 70), -1)   # iris ring (mid)
    cv2.circle(img, (cx, cy), pupil_r, (15, 15, 15), -1)   # dark pupil
    return img


def test_locates_eye_near_center():
    cx, cy = 340, 300
    img = _synthetic_eye(cx=cx, cy=cy)
    det = locate_eye(img)
    assert det["found"] is True
    dist = float(np.hypot(det["cx"] - cx, det["cy"] - cy))
    assert dist < 40, f"eye center off by {dist:.1f}px"
    assert det["confidence"] > 0.1


def test_crop_shape_and_overlay():
    img = _synthetic_eye()
    det = locate_eye(img)
    crop = crop_eye(img, det, out_size=256, margin=2.2)
    assert crop is not None
    assert crop.shape == (256, 256, 3)
    ov = draw_overlay(img, det)
    assert ov.shape == img.shape


def test_fallback_on_blank_image():
    blank = np.full((500, 500, 3), 180, np.uint8)   # no eye structure
    det = locate_eye(blank)
    # Either nothing found (fallback) or a low-confidence guess — must not crash,
    # and cropping must still return a valid square.
    crop = crop_eye(blank, det, out_size=128)
    assert crop is not None and crop.shape == (128, 128, 3)
