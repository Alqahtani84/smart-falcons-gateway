# Dataset Audit Plan (Track A)

Goal: turn a pile of mixed-source falcon photos into **known facts** + a reusable
eye-preprocessing pipeline — *without* pretending it can certify biometric feasibility.

## Inputs
- Raw images at `C:\Users\dell\Desktop\TestingClaudeCode\falcon-dataset\raw\` (read-only).
- Existing subfolder structure preserved (weak provenance/identity hint → `group` column).

## Steps

### 1. Inventory  — `ml/audit/inventory.py`
Enumerate every image; record path, source group, format, dimensions, megapixels, filesize,
MD5, EXIF camera make/model + capture datetime, decode success/failure.
→ `outputs/audit/manifest.csv`.

### 2. Duplicate / near-duplicate detection — `ml/audit/dedup.py`
- **Exact-byte** duplicates via MD5.
- **Near-duplicates** via perceptual hash (pHash, 256-bit) clustered by Hamming distance
  (union-find, default threshold 8).
→ `outputs/audit/duplicates.csv` (cluster id, cluster size, exact-group).
**Why:** reposts create fake genuine pairs; they must be collapsed before any split.

### 3. Whole-image quality proxy — `ml/quality/quality.py`
Sharpness (variance of Laplacian), brightness, contrast, resolution → usable/marginal/poor band.
→ `outputs/audit/quality.csv`.
**Scope caveat:** this is a *whole-image* triage proxy. True eye-region quality comes after eye
detection (next slice).

### 4. Recurring-individual mining — *(next slice)*
Cluster non-duplicate images by embedding similarity to surface candidate "same bird twice" sets
for **human confirmation**. These are candidates, not labels — there is no ground truth here.

### 5. Eye localization + crop — *(next slice)*
Detect and crop the eye region; inspect crops to judge whether iris texture is resolvable
(iris-texture vs periocular decision, Q-04).

### 6. Left/right-eye handling — *(next slice)*
Label eye side where possible; keep sides separable in every downstream split.

## Outputs
`outputs/audit/{manifest.csv, duplicates.csv, quality.csv, summary.md}`

## How to run
```bash
pip install -r requirements.txt
python -m scripts.run_audit --raw "C:/Users/dell/Desktop/TestingClaudeCode/falcon-dataset/raw" --out outputs/audit
```
Quick test on a subset: add `--limit 200`.

## What the audit answers
- Q-01 count/usable, Q-03 duplicate rate, Q-04 resolution (partial), Q-05 EXIF metadata.
- Feeds Q-02 (recurring individuals) once the mining step runs.

## Verification
- Row count in `manifest.csv` equals the number of image files under `raw/`.
- Spot-check 5–10 near-duplicate clusters by eye — they should be visually the same photo.
- Spot-check quality bands against a few obviously sharp vs blurred images.
- Confirm the smoke test passes: `pytest -q` (see `tests/test_audit_smoke.py`).
