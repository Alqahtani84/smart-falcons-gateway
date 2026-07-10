"""Image inventory: walk the raw dataset and record per-image facts.

Read-only over the source directory. Produces one record per image file with
dimensions, format, filesize, EXIF (camera + capture datetime when present) and a
`group` = the top-level subfolder under the dataset root (a weak provenance/identity
hint we preserve on purpose).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict, fields
from pathlib import Path
from typing import Iterator, Optional

from PIL import Image, ExifTags, ImageFile

# Allow loading of slightly-truncated files rather than crashing the whole audit.
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Register HEIC/HEIF (common from phones) if the optional dependency is present.
try:  # pragma: no cover - depends on optional dep
    import pillow_heif

    pillow_heif.register_heif_opener()
    HEIF_SUPPORTED = True
except Exception:  # pragma: no cover
    HEIF_SUPPORTED = False

IMAGE_EXTS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp",
    ".tif", ".tiff", ".gif", ".heic", ".heif",
}

# EXIF tag ids we care about (top-level IFD unless noted).
_TAG_MAKE = 271
_TAG_MODEL = 272
_TAG_DATETIME = 306
_EXIF_IFD = 0x8769
_TAG_DATETIME_ORIGINAL = 36867


@dataclass
class ImageRecord:
    rel_path: str
    group: str
    ext: str
    decode_ok: bool
    width: Optional[int]
    height: Optional[int]
    megapixels: Optional[float]
    mode: Optional[str]
    filesize_bytes: int
    md5: Optional[str]
    camera_make: Optional[str]
    camera_model: Optional[str]
    exif_datetime: Optional[str]
    error: Optional[str]


def _clean(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, bytes):
        try:
            value = value.decode("utf-8", "ignore")
        except Exception:
            value = str(value)
    text = str(value).replace("\x00", "").strip()
    return text or None


def _read_exif(img: Image.Image):
    """Return (make, model, datetime) — best effort, never raises."""
    make = model = dt = None
    try:
        exif = img.getexif()
        if exif:
            make = exif.get(_TAG_MAKE)
            model = exif.get(_TAG_MODEL)
            dt = exif.get(_TAG_DATETIME)
            try:
                sub = exif.get_ifd(_EXIF_IFD)
                if sub:
                    dt = sub.get(_TAG_DATETIME_ORIGINAL, dt)
            except Exception:
                pass
    except Exception:
        pass
    return _clean(make), _clean(model), _clean(dt)


def _md5(path: Path, chunk: int = 1 << 20) -> Optional[str]:
    try:
        h = hashlib.md5()
        with open(path, "rb") as fh:
            for block in iter(lambda: fh.read(chunk), b""):
                h.update(block)
        return h.hexdigest()
    except Exception:
        return None


def iter_image_paths(root: Path) -> Iterator[Path]:
    """Yield image files under root, recursively, in a stable sorted order."""
    root = Path(root)
    for p in sorted(root.rglob("*"), key=lambda x: str(x).lower()):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            yield p


def inspect_image(path: Path, root: Path) -> ImageRecord:
    path, root = Path(path), Path(root)
    rel = path.relative_to(root)
    parts = rel.parts
    group = parts[0] if len(parts) > 1 else "(root)"
    try:
        size = path.stat().st_size
    except Exception:
        size = 0

    rec = ImageRecord(
        rel_path=str(rel).replace("\\", "/"),
        group=group,
        ext=path.suffix.lower(),
        decode_ok=False,
        width=None,
        height=None,
        megapixels=None,
        mode=None,
        filesize_bytes=size,
        md5=_md5(path),
        camera_make=None,
        camera_model=None,
        exif_datetime=None,
        error=None,
    )

    try:
        with Image.open(path) as img:
            rec.width, rec.height = int(img.width), int(img.height)
            rec.mode = img.mode
            rec.megapixels = round(img.width * img.height / 1e6, 3)
            rec.camera_make, rec.camera_model, rec.exif_datetime = _read_exif(img)
            img.load()  # force full decode to catch corrupt files
            rec.decode_ok = True
    except Exception as exc:  # keep the row, record the failure
        rec.error = f"{type(exc).__name__}: {exc}"

    return rec


def build_inventory(root: Path, limit: Optional[int] = None) -> list[ImageRecord]:
    """Inventory every image under root. `limit` caps count for quick test runs."""
    records: list[ImageRecord] = []
    for i, path in enumerate(iter_image_paths(root)):
        if limit is not None and i >= limit:
            break
        records.append(inspect_image(path, root))
    return records


def records_to_rows(records: list[ImageRecord]) -> list[dict]:
    return [asdict(r) for r in records]


def column_order() -> list[str]:
    return [f.name for f in fields(ImageRecord)]
