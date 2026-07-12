# Decision Log

Append-only record of important decisions. Newest at the bottom of each section.

| ID | Decision | Rationale | Date | Status |
|----|----------|-----------|------|--------|
| D-001 | **Two-track feasibility phase**: Track A (screen existing images + build pipeline) and Track B (controlled pilot). Only Track B can *certify* feasibility; Track A screens & tools up and its numbers are never presented as a benchmark. | A mixed-source scrape lacks genuine same-bird pairs, so it cannot yield valid verification/identification metrics. A pilot is the only credible source. | 2026-07-10 | Adopted |
| D-002 | **Milestone 1 = credible feasibility verdict** (real numbers) with a *thin* visual wrapper, not an application. | Building UI first would polish a product on an unproven premise. Prove first, prettify cheaply from POC outputs. | 2026-07-10 | Adopted |
| D-003 | **Transfer learning first** — frozen pretrained backbones as embedding extractors + cosine similarity; escalate to a trained metric-learning head (ArcFace/triplet) only if pilot data volume justifies it. | Domain-specific training is premature without enough per-identity samples; transfer learning gives a fast, honest baseline. | 2026-07-10 | Adopted |
| D-004 | **Blockchain out of scope** for feasibility; revisit only if an ownership-transfer trust requirement genuinely demands it. **Digital Twin = structured lifecycle record**, not a 3D visual model. | Avoid premature complexity; keep focus on the biometric proof. | 2026-07-10 | Adopted |
| D-005 | **Dataset stored outside git** at `falcon-dataset/raw/`, read-only; repo holds code + docs only. | Size, copyright of scraped images, and future privacy of pilot falcons. | 2026-07-10 | Adopted |
| D-006 | **Repo renamed** `falcon-smart-gate` → `smart-falcons-gateway`. Local folder rename deferred (editor lock). | Name should match the product. | 2026-07-10 | Adopted |
| D-007 | **Classical (Hough/darkness) eye localization is a coarse region-finder, not a precise eye detector.** Keep it as a screening tool; plan a small **learned** eye detector (hand-label ~30–50 eyes) when precise crops are needed. | Verified on real data: on falcon portraits it latches onto the dark facial mask/body, not the eye. Works acceptably only on tight eye close-ups. | 2026-07-12 | Adopted |
| F-audit | **On-hand images are portraits/full-bird, not eye close-ups, with no identity labels or repeats.** Kaggle set is a 64-animal *classification* dataset. Neither can certify biometrics. | Track A audit + eye-crop visual review. | 2026-07-12 | Finding |

## Pending decisions (to record when made)
- **Go/No-Go thresholds** (target EER, Top-1@…): pre-register before running the POC (Q-15).
- **Iris-texture vs periocular** primary approach: decide after eye-crop resolution review (Q-04).
- **Biometric GO / NO-GO / PIVOT**: the gate at the end of the feasibility phase.
