# Risk Register

Likelihood (L) and Impact (I): Low / Med / High. Ordered roughly by exposure.

| ID | Risk | L | I | Mitigation | Owner |
|----|------|---|---|-----------|-------|
| R-01 | **No genuine same-bird pairs** in existing data → verification/identification metrics undefined. | High | High | Track B pilot provides real pairs; Track A only screens. | Owner + us |
| R-02 | **Near-duplicate leakage** produces fake, spectacular accuracy. | High | High | Dedup (pHash + MD5) before any split; split by individual **and** session. | Us |
| R-03 | **Insufficient iris resolution** → iris-texture approach fails. | Med | High | Measure resolution in audit; pivot to **periocular** if needed. | Us |
| R-04 | **Label noise** → any accuracy computed on scraped labels is meaningless. | High | Med | Treat scraped labels as untrusted; anchor metrics to pilot ground truth only. | Us |
| R-05 | **Longitudinal instability** — eye appearance changes with age/molt/health, breaking matching over time. | Med | High | Pilot captures ≥2 sessions/bird; report cross-session performance explicitly. | Us |
| R-06 | **Scope creep** — the 15-feature vision pulls focus off the biometric proof. | High | Med | Gate all platform work behind a biometric GO (D-002). | Owner + us |
| R-07 | **No liveness/anti-spoofing** testable on photos → real-world spoof risk understated. | High | Med | Document limitation; plan liveness as a separate later study. | Us |
| R-08 | **Regulatory/data-governance gaps** if government adoption pursued (biometric + ownership data in KSA). | Med | High | Legal review before platform; privacy-by-design; data minimization. | Owner + legal |
| R-09 | **Pilot logistics** (access, handler cooperation, consistent capture) slip. | Med | Med | One-page protocol + checklist; start small (20–50 birds). | Owner |
| R-10 | **Dev environment gaps** (Python/toolchain not installed) delay running the audit. | Med | Low | Documented setup in README; pinned requirements. | Us |
| R-11 | **Over-claiming novelty** ("first in the world") without prior-art analysis harms credibility. | Med | Med | Require formal prior-art review before any such claim. | Owner + us |
