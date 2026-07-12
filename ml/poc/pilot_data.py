"""Parse the pilot dataset layout into structured records.

Expected layout (see docs/PILOT_CAPTURE_PROTOCOL.md):
    pilot/<bird_id>/<session>/<eye>/<image>
e.g. pilot/F001/S1/left/F001_S1_left_01.jpg

`eye` is optional in the path; if absent it is recorded as "unknown". Identity
(bird_id) and session are the fields the leakage-safe split depends on, so a
record is only usable if BOTH are present.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path

from ml.audit.inventory import iter_image_paths


@dataclass
class PilotRecord:
    rel_path: str
    bird_id: str
    session: str
    eye: str  # "left" | "right" | "unknown"
    abs_path: str


def _norm_eye(value: str) -> str:
    v = value.strip().lower()
    if v in ("left", "l", "os"):
        return "left"
    if v in ("right", "r", "od"):
        return "right"
    return "unknown"


def parse_pilot_dir(root: Path) -> list[PilotRecord]:
    """Return one PilotRecord per image under a pilot/ tree (both id + session required)."""
    root = Path(root)
    records: list[PilotRecord] = []
    for p in iter_image_paths(root):
        parts = p.relative_to(root).parts
        if len(parts) < 3:
            continue  # need at least bird_id/session/file
        bird_id, session = parts[0], parts[1]
        eye = _norm_eye(parts[2]) if len(parts) >= 4 else "unknown"
        records.append(
            PilotRecord(
                rel_path=str(p.relative_to(root)).replace("\\", "/"),
                bird_id=bird_id,
                session=session,
                eye=eye,
                abs_path=str(p),
            )
        )
    return records


def summarize(records: list[PilotRecord]) -> dict:
    birds = sorted({r.bird_id for r in records})
    sessions = sorted({r.session for r in records})
    per_bird_sessions = {
        b: sorted({r.session for r in records if r.bird_id == b}) for b in birds
    }
    birds_multi_session = [b for b, s in per_bird_sessions.items() if len(s) >= 2]
    return {
        "n_images": len(records),
        "n_birds": len(birds),
        "n_sessions": len(sessions),
        "birds": birds,
        "sessions": sessions,
        "per_bird_sessions": per_bird_sessions,
        "birds_with_multiple_sessions": birds_multi_session,
    }


def records_to_rows(records: list[PilotRecord]) -> list[dict]:
    return [asdict(r) for r in records]
