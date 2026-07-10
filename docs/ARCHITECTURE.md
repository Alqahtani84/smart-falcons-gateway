# Architecture

> **Status: stub — gated on a biometric GO.** This document is intentionally a placeholder.
> We will fill it in when the [roadmap](ROADMAP.md) reaches the relevant phase, so we do not
> design the platform on top of an unproven biometric premise. See
> [`PROJECT_VISION.md`](PROJECT_VISION.md) and [`BIOMETRIC_FEASIBILITY_PLAN.md`](BIOMETRIC_FEASIBILITY_PLAN.md).

## Scope when unlocked
Web app (Next.js), FastAPI services (API, biometrics, gps, notifications), PostgreSQL + pgvector, S3/MinIO object storage, embedding search (FAISS/pgvector), auth + RBAC, audit logs, AR localization, API gateway, monitoring, backup/recovery, security controls. Evaluated with Option A/B trade-offs per component.
