# Falcon Eye Biometric Feasibility Plan

The scientific test of whether the falcon eye region is a reliable biometric. This plan defines
the workflow, models, metrics, and the go/no-go gate. **No platform work begins until this gate
returns GO.**

## Five distinct problems (never conflate them)
| Term | Question | Needs |
|------|----------|-------|
| **Eye detection** | Where is the eye in the photo? | Detector / keypoints |
| **Quality assessment** | Is this eye image good enough to use? | Sharpness/occlusion/resolution scoring |
| **Verification (1:1)** | Is this the falcon it claims to be? | Genuine + impostor pairs |
| **Identification (1:N)** | Which falcon is this? | Multiple images per identity |
| **Enrollment** | Create a template for a new falcon. | Embedding + storage + threshold |

## 1. Data readiness (prerequisite)
- Track A audit complete; duplicates collapsed.
- Track B pilot images available: known individuals, **≥2 sessions each**, recorded ground truth.

## 2. Leakage-safe evaluation design (non-negotiable)
- **Deduplicate** before splitting.
- **Split by individual AND session:** test genuine pairs come from **held-out sessions** of birds
  the model did not see in that configuration. A bird's images from one session must never be
  split across train and test as an easy pair.
- Keep **left/right eye** separable until cross-eye transfer is explicitly tested.
- Report on **pilot** data for the verdict; scraped data may screen but **cannot** satisfy the gate.

## 3. Approach & model comparison
Start simple, escalate only if justified (D-003).

**Stage 1 — Zero-training embeddings + cosine similarity.** Frozen pretrained backbones as feature
extractors; kNN / threshold for matching. Compare fairly:

| Model | Type | Why consider | Notes |
|-------|------|-------------|-------|
| **DINOv2** | Self-supervised ViT | Strong general features, robust transfer | Likely front-runner |
| ResNet-50 | Supervised CNN | Familiar baseline | Reference point |
| EfficientNet | Supervised CNN | Efficiency/accuracy trade | |
| ConvNeXt | Modern CNN | Strong ImageNet features | |
| ViT (supervised) | Transformer | Compare vs DINOv2 | |

**Stage 2 — Metric learning (only if pilot volume allows).** Siamese / triplet-loss / **ArcFace**
head trained on eye crops for identity-discriminative embeddings.

**Transfer vs domain training:** begin with transfer learning (Stage 1). Domain-specific training
(Stage 2) is warranted only when we have enough images per identity from the pilot — otherwise it
overfits and misleads.

## 4. Verification (1:1)
Compute genuine vs impostor similarity distributions →
- **FAR**, **FRR**, **EER**, **ROC-AUC**, **TAR @ FAR = 1% and 0.1%**.

## 5. Identification (1:N)
Enroll a gallery, query probes →
- **Top-1**, **Top-5** accuracy; **precision / recall / F1**; **confusion matrix**.

## 6. Required breakdowns
Report every headline metric sliced by: **eye side**, **session**, **image-quality band**,
**lighting / camera condition**.

## 7. Analyses
- **Failure analysis** — where and why it breaks.
- **Bias / capture-condition analysis** — performance skew by source/lighting/device.
- **Longitudinal stability** — cross-session performance drop (the real-world signal).
- **Spoofing / liveness** — document that photo-only data **cannot** test liveness; flag as a
  separate future study.

## 8. Enrollment & thresholds
- Template = embedding(s) per enrolled falcon.
- Calibrate an operating threshold from the genuine/impostor distributions; state the chosen
  FAR operating point and the resulting FRR.

## 9. Go / No-Go gate
- **Pre-register** target thresholds before running (Q-15) — e.g., an EER band and Top-1 band on
  **pilot cross-session** data agreed with the owner.
- Outcome recorded in [`DECISION_LOG.md`](DECISION_LOG.md):
  - **GO** — meets thresholds → proceed to Biometric API (Phase D).
  - **PIVOT** — iris-texture fails but periocular is promising → re-scope and re-test.
  - **NO-GO** — eye biometrics not reliable → rethink the identity anchor before any platform build.

## Deliverables
- `outputs/eval/` metrics tables + plots (ROC, score histograms, confusion matrix).
- A short feasibility report + the minimal visual wrapper (input → eye crop → quality → top-k match).
