# Smart Falcons Gateway — Master Brief & Context (single source of truth)

> **Purpose of this file:** the one place to recall the full context in any future session — the
> vision, the owner's instructions, all planning phases, the working rules, every key decision, the
> current status, and links to the detailed docs. Read this first. Keep it updated as we progress.

**Repo:** `Alqahtani84/smart-falcons-gateway` (private) · **Owner:** Alqahtani84 ·
**Deployment target:** Saudi Arabia (Arabic RTL + English) · **Last updated:** 2026-07-10

---

## 0. How to use this file
- New session? Read this top-to-bottom to reload context.
- It **summarizes and links**; the authoritative detail lives in the linked docs.
- When a decision is made → update [`DECISION_LOG.md`](DECISION_LOG.md) **and** the status here.
- We are in the **Feasibility Phase**. No platform code until a biometric **GO** (see §8).

---

## 1. Vision (what we are ultimately building)
A **falcon-only** identity & lifecycle platform. **Never** generalize to other birds, animals,
pets, or wildlife. Long-term capabilities:

1. Falcon eye-biometric identification
2. Digital Falcon Passport
3. Falcon registry & ownership records
4. GPS tracking & geofencing
5. Health & veterinary records
6. Digital Twin per falcon (structured lifecycle record, **not** merely a 3D model)
7. AI readiness / risk / performance indicators
8. Genealogy & breeding records
9. Competition & race records
10. Ownership-transfer workflows
11. Alerts & notifications
12. Government dashboards
13. Investor & commercial dashboards
14. Reporting & analytics
15. Arabic + English interfaces (RTL + LTR)

Full version: [`PROJECT_VISION.md`](PROJECT_VISION.md).

---

## 2. The gating question (why we don't build yet)
> **Can the falcon eye region serve as a reliable biometric identifier?**

The whole platform's value depends on this. We **prove it before building**. Keep these five
concepts distinct — never conflate them:
**eye detection · eye-image quality · verification (1:1) · identification (1:N) · enrollment.**

---

## 3. Current situation (confirmed)
- Owner has a dataset of falcon photos **collected from mixed/different sources**, in a local folder.
- **Labels are not trusted**; metadata may be incomplete. Do not assume identities are correct.
- Owner **has access now** to known, repeat-photographable falcons (enables the pilot).
- Milestone-1 success = **a credible feasibility verdict with real numbers** (not a demo-first app).

Discovery Q&A and the fact/assumption tables: [`CONFIRMED_FACTS.md`](CONFIRMED_FACTS.md),
[`ASSUMPTIONS.md`](ASSUMPTIONS.md), [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md).

---

## 4. Two-track feasibility approach (Decision D-001)
- **Track A — screen & build** on existing images: audit, dedup, recurring-individual mining,
  quality scoring, and the reusable eye-preprocessing pipeline. *Screens only — never a benchmark.*
- **Track B — controlled pilot**: known falcons, **≥2 sessions each**, recorded identity ground
  truth. **Only Track B can certify feasibility** and cross-session stability.
- Owner chose **BOTH**, run in parallel.

Details: [`DATASET_AUDIT_PLAN.md`](DATASET_AUDIT_PLAN.md) ·
[`PILOT_CAPTURE_PROTOCOL.md`](PILOT_CAPTURE_PROTOCOL.md).

---

## 5. Owner's planning rules (must follow)
1. Ask questions in **small groups (≤5)**; wait for answers; don't overwhelm.
2. **No production code** until the planning phase is approved.
3. **Do not invent facts** about dataset, users, budget, partners, or infrastructure.
4. Clearly label **confirmed facts / assumptions / open questions / risks / decisions**.
5. Say when an idea is **technically unrealistic or premature**.
6. Prefer **phased** implementation over building everything at once.
7. **Prioritize proving the biometric identity concept.**
8. Design for **Saudi deployment, Arabic RTL, privacy, cybersecurity, possible government adoption**.
9. **Blockchain = optional**; justify if genuinely needed (currently out of scope — D-004).
10. **Digital Twin = structured lifecycle representation**, not merely a 3D visual model.
11. **No "first in the world"** claims without formal prior-art analysis.
12. Explicit approval gate: build only after the owner says **"APPROVE PLAN AND START IMPLEMENTATION."**

Working style: challenge weak assumptions; present options in **Option A / B** format
(description, advantages, disadvantages, cost/effort, risks, recommendation), then state a
preferred option and why. See [[user-planning-style]] (agent memory) and
[`RISK_REGISTER.md`](RISK_REGISTER.md).

---

## 6. The nine planning phases (owner's framework)
Status legend: ✅ done · 🟡 in progress · ⏳ queued · ⛔ gated on biometric GO.

| Phase | Name | What it must contain | Status | Doc |
|-------|------|----------------------|--------|-----|
| 1 | **Discovery** | Business objective, users, use cases, dataset condition, labels, counts, quality, sessions, biometric workflow, legal, deadline, budget, deployment | 🟡 core answered | `CONFIRMED_FACTS`, `OPEN_QUESTIONS` |
| 2 | **Feasibility Plan** | 20-step biometric plan; metrics (FAR/FRR/EER/ROC-AUC/TAR@FAR, Top-1/5, P/R/F1, confusion, breakdowns); model comparison; go/no-go | ✅ written | [`BIOMETRIC_FEASIBILITY_PLAN.md`](BIOMETRIC_FEASIBILITY_PLAN.md) |
| 3 | **Product Roadmap** | Phases A–K, each: objective/inputs/activities/deliverables/deps/effort/roles/risks/acceptance/gate | 🟡 table done, detail gated | [`ROADMAP.md`](ROADMAP.md) |
| 4 | **System Architecture** | Web, auth, RBAC, registry, biometric svc, model registry, storage, embeddings, passport, GPS, geofence, health, twin, genealogy, competitions, alerts, reporting, audit, AR i18n, gateway, backup, monitoring, security | ⛔ stub | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| 5 | **Data Model** | ~40 entities w/ purpose, fields, PK/FKs, sensitive fields, retention, audit | ⛔ stub | [`DATA_MODEL.md`](DATA_MODEL.md) |
| 6 | **MVP Definition** | Challenged, trimmed MVP (cut anything not needed to validate) | ⛔ stub | [`MVP_SCOPE.md`](MVP_SCOPE.md) |
| 7 | **Project Backlog** | Epics/features/stories/technical/AI/data/security/devops/testing/docs; stories w/ role, value, acceptance, deps, priority, complexity | ⛔ stub | [`BACKLOG.md`](BACKLOG.md) |
| 8 | **Repository Plan** | Monorepo structure (apps/services/packages/ml/infra) — improve, don't accept blindly | 🟡 feasibility subset built | [`README.md`](../README.md) |
| 9 | **Documentation Outputs** | The 18 docs below, kept live | 🟡 seeded | this `docs/` folder |

### Phase 2 — model candidates to compare (transfer learning first, D-003)
DINOv2 (front-runner), ResNet, EfficientNet, ConvNeXt, ViT → frozen embeddings + cosine similarity;
escalate to Siamese / triplet-loss / **ArcFace** metric-learning head only if pilot data volume
justifies it.

### Phase 8 — candidate full monorepo (grow only when gated in)
```
smart-falcons-gateway/
├── apps/{web,admin}/            # ⛔ gated
├── services/{api,biometrics,gps,notifications}/   # ⛔ gated
├── packages/{ui,shared-types,config}/             # ⛔ gated
├── ml/{audit,detection,quality,embeddings,evaluation,poc,experiments}/  # 🟡 active
├── infrastructure/  scripts/  tests/  docs/  docker-compose.yml
```

---

## 7. Key decisions (see DECISION_LOG for full rationale)
- **D-001** Two-track feasibility (A screens+builds, B certifies).
- **D-002** Milestone 1 = feasibility verdict + thin visual wrapper, not an app.
- **D-003** Transfer learning first; domain training only if pilot volume allows.
- **D-004** Blockchain out of scope; Digital Twin = structured lifecycle record.
- **D-005** Dataset stored outside git at `falcon-dataset/raw/` (read-only).
- **D-006** Repo renamed `falcon-smart-gate` → `smart-falcons-gateway` (local folder rename pending editor unlock).

---

## 8. Biometric Go / No-Go gate
Pre-register target thresholds (EER band, Top-1 band) on **pilot cross-session** data before running
the POC. Outcome → [`DECISION_LOG.md`](DECISION_LOG.md): **GO** (→ Phase D), **PIVOT** (iris→periocular),
or **NO-GO** (rethink the identity anchor). Track-A numbers may screen but cannot satisfy the gate.

---

## 9. Current status & next steps
**Built & verified (Python 3.12 venv, 10 tests passing):**
- Track A audit (`scripts/run_audit.py`) — ran on **325 real images**: portraits/full-bird, `.jpg`,
  median ~18 MP, low duplicates, **no identity labels, no repeated individuals**.
- Eye-detection slice (`scripts/run_eye_crops.py`) — classical CV; verified **coarse** (lands on
  dark facial mask on portraits), screening only (D-007). A learned detector is the real fix.
- **Leakage-safe POC harness** (`scripts/run_poc.py`) — pluggable embedder (**DINOv2 verified**,
  384-dim), cross-session genuine/impostor pairs, verification (EER/AUC/TAR@FAR) + identification
  (Top-1/5), report + plots. Refuses to produce a verdict without ≥2 birds & a 2nd session.

**The wall (confirmed):** existing data cannot certify biometrics — no genuine same-bird pairs.
**Critical path:** the **Track B pilot** ([`PILOT_PLAN_MINIMAL.md`](PILOT_PLAN_MINIMAL.md)) — the
only source of a real verdict. POC harness is ready to run the moment Session-2 images exist.

**Housekeeping:** local folder still named `falcon-smart-gate` (Cursor lock); GitHub repo already
renamed. Live task list: [`BACKLOG.md`](BACKLOG.md).

---

## 10. Document index (the 18 living docs)
| Doc | Purpose |
|-----|---------|
| [`PROJECT_VISION.md`](PROJECT_VISION.md) | Vision & strategy |
| [`CONFIRMED_FACTS.md`](CONFIRMED_FACTS.md) | What's confirmed |
| [`ASSUMPTIONS.md`](ASSUMPTIONS.md) | Working assumptions to validate |
| [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md) | Tracked unknowns |
| [`DECISION_LOG.md`](DECISION_LOG.md) | Decisions (append-only) |
| [`RISK_REGISTER.md`](RISK_REGISTER.md) | Risks & mitigations |
| [`DATASET_AUDIT_PLAN.md`](DATASET_AUDIT_PLAN.md) | Track A plan |
| [`BIOMETRIC_FEASIBILITY_PLAN.md`](BIOMETRIC_FEASIBILITY_PLAN.md) | The biometric test |
| [`PILOT_CAPTURE_PROTOCOL.md`](PILOT_CAPTURE_PROTOCOL.md) | Track B capture guide (+ checklist CSV) |
| [`ROADMAP.md`](ROADMAP.md) | Gated phases A–K |
| [`PRODUCT_REQUIREMENTS.md`](PRODUCT_REQUIREMENTS.md) | PRD (gated stub) |
| [`MVP_SCOPE.md`](MVP_SCOPE.md) | MVP (gated stub) |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Architecture (gated stub) |
| [`DATA_MODEL.md`](DATA_MODEL.md) | Data model (gated stub) |
| [`API_PLAN.md`](API_PLAN.md) | API plan (gated stub) |
| [`SECURITY_PLAN.md`](SECURITY_PLAN.md) | Security (gated stub) |
| [`TEST_STRATEGY.md`](TEST_STRATEGY.md) | Testing |
| [`DEPLOYMENT_PLAN.md`](DEPLOYMENT_PLAN.md) | Deployment (gated stub) |
| [`BACKLOG.md`](BACKLOG.md) | Backlog / task list |
