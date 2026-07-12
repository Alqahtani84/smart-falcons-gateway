"""Eye localization + cropping over a folder of falcon eye photos.

Produces, under --out:
  crops/<rel>.png      standardized square eye crops (for the biometric POC later)
  overlays/<rel>.png    original with detected circle + crop box (human QA)
  detections.csv        one row per image: found, method, confidence, geometry, crop sharpness

Usage:
  python -m scripts.run_eye_crops --raw ".../falcon-dataset/raw" --out outputs/eye_crops --limit 20

Read-only over --raw. This is a SCREENING pass, not a certified detector.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.audit.inventory import iter_image_paths  # noqa: E402
from ml.detection.eye_localize import (  # noqa: E402
    crop_eye,
    draw_overlay,
    load_bgr,
    locate_eye,
)


def _laplacian_var(img_bgr) -> float:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def _imwrite(path: Path, img_bgr) -> bool:
    """Unicode-safe image write. cv2.imwrite fails silently on non-ASCII paths
    (e.g. Arabic folder names) on Windows; encode + ndarray.tofile does not."""
    ext = path.suffix if path.suffix else ".png"
    ok, buf = cv2.imencode(ext, img_bgr)
    if not ok:
        return False
    buf.tofile(str(path))
    return True


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Falcon eye localization + cropping (screening)")
    p.add_argument("--raw", required=True, help="Folder of eye photos (read-only)")
    p.add_argument("--out", default="outputs/eye_crops", help="Output directory")
    p.add_argument("--out-size", type=int, default=512, help="Crop side length in px")
    p.add_argument("--margin", type=float, default=2.2, help="Crop half-size = margin * eye radius")
    p.add_argument("--min-confidence", type=float, default=0.15, help="Threshold for the 'usable' flag")
    p.add_argument("--limit", type=int, default=None, help="Cap number of images (quick runs)")
    p.add_argument("--no-overlays", action="store_true", help="Skip overlay images")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    raw = Path(args.raw)
    if not raw.exists():
        print(f"ERROR: raw path does not exist: {raw}", file=sys.stderr)
        return 2

    out = Path(args.out)
    crops_dir = out / "crops"
    overlays_dir = out / "overlays"
    crops_dir.mkdir(parents=True, exist_ok=True)
    if not args.no_overlays:
        overlays_dir.mkdir(parents=True, exist_ok=True)

    paths = list(iter_image_paths(raw))
    if args.limit is not None:
        paths = paths[: args.limit]

    rows = []
    n_found = 0
    for path in tqdm(paths, desc="eye-crops", unit="img"):
        rel = path.relative_to(raw)
        rel_key = str(rel).replace("\\", "/")
        row = {
            "rel_path": rel_key, "found": False, "method": None, "confidence": None,
            "cx": None, "cy": None, "r": None, "img_w": None, "img_h": None,
            "crop_sharpness": None, "usable": False, "error": None,
        }
        try:
            img = load_bgr(path)
            det = locate_eye(img)
            crop = crop_eye(img, det, out_size=args.out_size, margin=args.margin)

            stem = rel.with_suffix(".png")
            crop_path = crops_dir / stem
            crop_path.parent.mkdir(parents=True, exist_ok=True)
            crop_sharp = None
            if crop is not None:
                _imwrite(crop_path, crop)
                crop_sharp = round(_laplacian_var(crop), 2)

            if not args.no_overlays:
                ov = draw_overlay(img, det, margin=args.margin)
                ov_path = overlays_dir / stem
                ov_path.parent.mkdir(parents=True, exist_ok=True)
                # overlays can be huge; downscale long side to <=1400 for quick viewing
                h, w = ov.shape[:2]
                s = min(1.0, 1400.0 / max(h, w))
                if s < 1.0:
                    ov = cv2.resize(ov, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
                _imwrite(ov_path, ov)

            row.update(
                found=bool(det["found"]), method=det["method"],
                confidence=round(float(det["confidence"]), 3),
                cx=round(det["cx"], 1), cy=round(det["cy"], 1), r=round(det["r"], 1),
                img_w=det["img_w"], img_h=det["img_h"], crop_sharpness=crop_sharp,
                usable=bool(det["found"] and det["confidence"] >= args.min_confidence),
            )
            n_found += int(bool(det["found"]))
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(out / "detections.csv", index=False, encoding="utf-8")

    total = len(df)
    usable = int(df["usable"].sum()) if total else 0
    print(f"\nProcessed {total} images")
    print(f"  eye located (found): {n_found}")
    print(f"  usable (found & conf >= {args.min_confidence}): {usable}")
    if total and df["confidence"].notna().any():
        c = df["confidence"].dropna()
        print(f"  confidence — min {c.min():.2f}, median {c.median():.2f}, max {c.max():.2f}")
    print(f"  crops   -> {crops_dir}")
    if not args.no_overlays:
        print(f"  overlays-> {overlays_dir}")
    print(f"  table   -> {out / 'detections.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
