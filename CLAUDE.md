# CLAUDE.md — Smart Falcons Gateway

Auto-loaded context + working rules for this repo. Full detail lives in
[`docs/MASTER_BRIEF.md`](docs/MASTER_BRIEF.md) (the single source of truth) and the `docs/` folder.
Read the master brief at the start of a session to reload full context.

## What this is
A **falcon-only** identity & lifecycle platform (biometric ID, digital passport, registry, GPS,
health, digital twin, dashboards; AR-RTL + EN; Saudi deployment). **Never** generalize to other
birds/animals/pets/wildlife. Repo: `Alqahtani84/smart-falcons-gateway` (private).

## The one rule that governs everything
We are in the **Feasibility Phase**. The whole platform is gated on proving:
> **Can the falcon eye region serve as a reliable biometric identifier?**

**Do NOT build platform features until a biometric GO decision** (see
[`docs/BIOMETRIC_FEASIBILITY_PLAN.md`](docs/BIOMETRIC_FEASIBILITY_PLAN.md)). Prove first, build second.

## How to work on this project (owner's rules)
- **Plan before building.** No production code until the owner explicitly approves. The approval
  phrase is **"APPROVE PLAN AND START IMPLEMENTATION."** Stay in plan mode until then.
- Ask questions in **small groups (≤5)**; wait for answers; don't overwhelm.
- Always separate **confirmed facts / assumptions / open questions / risks / decisions**.
- **Challenge weak or premature ideas.** Say when something is unrealistic. Act as a co-founder /
  architect, not a code generator. Present trade-offs as **Option A / B** then recommend one.
- **Never invent facts** about the dataset, users, budget, partners, or infrastructure.
- Prefer **phased** delivery. **Prioritize proving the biometric concept.**
- Design for **Saudi deployment, Arabic RTL, privacy, cybersecurity, possible government adoption.**
- **Blockchain** = out of scope unless justified. **Digital Twin** = structured lifecycle record,
  not a 3D model. **No "first in the world"** claims without formal prior-art analysis.
- Keep five concepts distinct: **eye detection · quality · verification (1:1) · identification
  (1:N) · enrollment.**

## Two-track feasibility (current work)
- **Track A** — audit existing mixed-source images + build the eye-preprocessing pipeline
  (`ml/audit`, `ml/quality`, `scripts/run_audit.py`). Screens only — **never a benchmark.**
- **Track B** — controlled pilot of KNOWN falcons across **≥2 sessions**
  ([`docs/PILOT_CAPTURE_PROTOCOL.md`](docs/PILOT_CAPTURE_PROTOCOL.md)). Only Track B certifies feasibility.

## Repo conventions
- **Dataset lives OUTSIDE git** at `../falcon-dataset/raw/` (copyright/privacy). Never commit images.
- Feasibility code only under `ml/` + `scripts/`. Platform dirs (`apps/`, `services/`, …) are
  **deferred** until the biometric GO.
- Python 3.10+ (`requirements.txt`). Run audit: `python -m scripts.run_audit --raw <path> --out outputs/audit`.
  Tests: `pytest -q`.
- **Keep docs live:** record decisions in [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md) and update
  [`docs/MASTER_BRIEF.md`](docs/MASTER_BRIEF.md) status when things change.

## Current status (2026-07-10)
Repo scaffolded; Track A audit tooling written but **not yet run** (Python not installed on the dev
machine; no images copied in yet). Local folder still named `falcon-smart-gate` (editor lock); GitHub
repo already renamed. Next: install Python + run audit; start Track B; build eye-detection slice.
