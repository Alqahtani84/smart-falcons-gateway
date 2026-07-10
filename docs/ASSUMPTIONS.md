# Assumptions

Working assumptions — **not** confirmed facts. Each must be validated or retired. When one is
confirmed, move it to [`CONFIRMED_FACTS.md`](CONFIRMED_FACTS.md); when disproven, note it here.

| # | Assumption | Basis | How we validate | Status |
|---|-----------|-------|-----------------|--------|
| A-01 | The collection is heterogeneous in resolution, camera, lighting, and pose. | "Different sources" | Track A audit (manifest + quality) | Open |
| A-02 | The collection is **mostly one-image-per-individual**, with few genuine same-bird pairs. | Typical of scraped sets | Audit recurring-individual mining | Open |
| A-03 | Significant **near-duplicate / repost** contamination is present. | Multi-source scraping | Audit dedup (pHash + MD5) | Open |
| A-04 | **No independent ground truth** (chip/ring/owner) exists inside the current dataset. | Owner said labels untrusted | Audit + owner confirmation | Open |
| A-05 | Iris pixel density in typical images may be **too low for iris-texture** recognition, forcing a **periocular** approach. | Web imagery resolution | Audit resolution stats + eye-crop inspection (next slice) | Open |
| A-06 | Falcons are Gulf hunting/racing species (saker, peregrine, gyr, hybrids). | Regional context | Owner confirmation | Open |
| A-07 | Team is small/solo for the feasibility phase. | Current signals | Owner confirmation | Open |
| A-08 | Photo-only data means **no liveness/anti-spoofing** can be tested in the POC. | Data modality | Inherent limitation, documented | Accepted limitation |

> Golden rule: **do not invent facts** about the dataset, users, budget, partners, or
> infrastructure. Label everything uncertain as an assumption until measured or confirmed.
