# Roadmap (Gated)

Everything from Phase D onward is **gated on a biometric GO** (see
[`BIOMETRIC_FEASIBILITY_PLAN.md`](BIOMETRIC_FEASIBILITY_PLAN.md)). We fill in each phase's full
detail (objective, inputs, activities, deliverables, dependencies, effort, roles, risks,
acceptance criteria, decision gate) when we reach it — not before.

| Phase | Name | Gate to enter | Status |
|-------|------|---------------|--------|
| A | Dataset readiness (audit, dedup, quality) | — | 🟡 tooling built |
| B | Eye detection & preprocessing (crop, quality, L/R) | Audit done | ⏳ next slice |
| **C** | **Biometric POC (verification + identification)** | **Pilot data ready** | ⏳ |
| — | **★ DECISION GATE: GO / PIVOT / NO-GO ★** | POC metrics vs pre-registered thresholds | ⏳ |
| D | Biometric API (enroll / verify / identify) | Biometric GO | ⛔ gated |
| E | Falcon Registry | D | ⛔ gated |
| F | Digital Falcon Passport | E | ⛔ gated |
| G | GPS & geofencing (simulation first) | E | ⛔ gated |
| H | Health records & Digital Twin | E | ⛔ gated |
| I | Genealogy & competitions | E | ⛔ gated |
| J | Government & investor dashboards | F–I | ⛔ gated |
| K | Security, deployment & production readiness | J | ⛔ gated |

## Current focus
Phase A (audit tooling ✅) → run audit on real data → Phase B (eye detection) → Track B pilot
collection in parallel → Phase C POC → **decision gate.**

> Candidate platform stack (evaluated at Phase D, not committed now): Next.js + TypeScript +
> Tailwind + ShadCN / FastAPI / PostgreSQL + pgvector / MinIO (S3) / PyTorch + FAISS /
> Docker + Compose + GitHub Actions / Saudi-hosted or hybrid deployment.
