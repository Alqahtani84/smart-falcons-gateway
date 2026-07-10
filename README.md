# Smart Falcons Gateway

A falcon-only identity & lifecycle platform. The long-term vision spans falcon eye-biometric
identification, a Digital Falcon Passport, registry & ownership records, GPS/geofencing, health &
veterinary records, a Digital Twin, AI readiness/risk indicators, genealogy & breeding,
competitions, ownership transfer, alerts, and government/investor dashboards — with Arabic (RTL)
and English interfaces, targeted at Saudi Arabian deployment.

> **This platform is exclusively for falcons.** It is not generalized to other birds, animals,
> pets, or wildlife.

## ⚠️ We are in the Feasibility Phase — not building the platform yet

The entire platform rests on **one unproven scientific question**:

> **Can the falcon eye region serve as a reliable biometric identifier?**

Until that is answered with credible numbers, we do **not** build the 15-feature platform. This
repository currently contains only the **feasibility infrastructure**. See
[`docs/BIOMETRIC_FEASIBILITY_PLAN.md`](docs/BIOMETRIC_FEASIBILITY_PLAN.md) and the vision summary
in [`docs/PROJECT_VISION.md`](docs/PROJECT_VISION.md).

### Two-track feasibility approach

- **Track A — Screen & build** (on the existing mixed-source image collection): audit the data,
  remove duplicates, hunt for recurring individuals, score eye-image quality, and build the
  reusable eye-preprocessing pipeline. *Track A screens and tools up; it cannot certify feasibility.*
- **Track B — Controlled pilot** (known falcons, ≥2 sessions each): the only source of trustworthy
  verification/identification metrics and longitudinal stability. See
  [`docs/PILOT_CAPTURE_PROTOCOL.md`](docs/PILOT_CAPTURE_PROTOCOL.md).

A formal **GO / NO-GO / PIVOT** decision is recorded in [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md)
before any platform work begins.

## Repository layout (feasibility phase)

```
smart-falcons-gateway/
├── ml/
│   ├── audit/        # inventory, duplicate detection, recurring-individual mining
│   ├── detection/    # eye localization + cropping (next slice)
│   ├── quality/      # eye-image quality scoring
│   ├── embeddings/   # backbone feature extraction (next slice)
│   ├── evaluation/   # leakage-safe splits, metrics, plots (next slice)
│   ├── poc/          # verification + identification harness (next slice)
│   └── experiments/  # tracked runs/configs
├── docs/             # planning + result documents
├── scripts/          # CLI entrypoints
├── tests/
└── requirements.txt
```

Platform code (`apps/`, `services/`, `packages/`, `infrastructure/`) is **deferred** until the
biometric GO decision.

## Data location (never committed)

Raw images live **outside git**:

```
C:\Users\dell\Desktop\TestingClaudeCode\falcon-dataset\raw\
```

This is the read-only source of truth. The audit reads from it and writes results to `outputs/`.
Both `falcon-dataset/` and `outputs/` are gitignored (size, copyright, privacy).

## Quick start (Track A audit)

Requires **Python 3.10+** (see note below — not yet installed on the dev machine).

```bash
python -m venv .venv
# Windows PowerShell:  .venv\Scripts\Activate.ps1
# Git Bash:            source .venv/Scripts/activate
pip install -r requirements.txt

# Run the audit over the raw dataset
python -m scripts.run_audit --raw "C:/Users/dell/Desktop/TestingClaudeCode/falcon-dataset/raw" --out outputs/audit
```

Outputs: an image **manifest CSV**, **duplicate-cluster** report, and **quality-score** table,
plus a short human-readable summary. See [`docs/DATASET_AUDIT_PLAN.md`](docs/DATASET_AUDIT_PLAN.md).

> **Note:** Python is not yet installed on the development machine. Install Python 3.10+ from
> https://www.python.org/downloads/ (check "Add python.exe to PATH") before running the audit.

## Status

| Item | State |
|------|-------|
| GitHub repo renamed to `smart-falcons-gateway` | ✅ |
| Feasibility plan approved | ✅ |
| Track A audit tooling | 🟡 built, awaiting Python + data to run |
| Track B pilot protocol | ✅ documented, ready to collect |
| Eye detection / embeddings / POC harness | ⏳ next slice |
| Platform features (registry, passport, GPS, …) | ⛔ gated on biometric GO |
