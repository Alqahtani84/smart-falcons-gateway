# Backlog

> **Status: stub — gated on a biometric GO.** This document is intentionally a placeholder.
> We will fill it in when the [roadmap](ROADMAP.md) reaches the relevant phase, so we do not
> design the platform on top of an unproven biometric premise. See
> [`PROJECT_VISION.md`](PROJECT_VISION.md) and [`BIOMETRIC_FEASIBILITY_PLAN.md`](BIOMETRIC_FEASIBILITY_PLAN.md).

## Active now (feasibility phase)
- [x] Repo + scaffold + gitignore
- [x] Track A audit tooling (inventory, dedup, quality)
- [x] Pilot capture protocol + checklist
- [x] Install Python + run audit on real data (325 images; portraits, no identities)
- [x] Eye detection + cropping slice (classical CV; coarse — see D-007)
- [x] Leakage-safe POC harness (embedder + cross-session pairs + EER/AUC/TAR + Top-1/5, DINOv2 verified)
- [ ] **Track B pilot capture** (10 birds x 2 sessions) — CRITICAL PATH, blocks the verdict
- [ ] Run POC on pilot data → first real numbers
- [ ] Pre-register Go/No-Go thresholds (draft in PILOT_PLAN_MINIMAL.md)
- [ ] (Later) learned eye detector when precise crops needed

## When unlocked
Full epics/features/user stories/technical/AI/data/security/devops/testing/docs tasks, each story with role, value, acceptance criteria, dependencies, priority, complexity.
