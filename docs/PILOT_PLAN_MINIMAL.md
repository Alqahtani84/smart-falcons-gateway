# Minimal Track B Pilot — start this week

A deliberately small, fast pilot to get the **first real biometric signal**. It exists because no
downloaded dataset can: our screening confirmed the on-hand images are falcon *portraits/full-bird
photos* with **no repeated individuals and no identity labels** — so verification/identification
metrics are undefined on them. The pilot fixes that at the root.

## Goal
Produce **genuine same-bird pairs across ≥2 sessions** for a handful of known falcons, framed as
tight eye close-ups, so we can compute a first honest EER / Top-1 and a cross-session number.

## Minimal spec (v1)
- **Birds:** 10 known individuals to start (grow toward 25). Fewer is fine for a first signal.
- **Sessions:** **2 per bird, on different days** (≥ a few days apart). This is the non-negotiable part.
- **Per session:** both eyes; **8–10 tight close-ups per eye** (fill the frame with the eye).
- **Identity:** record chip/ring/owner per bird → stable `bird_id` (F001, F002, …).

Why tight close-ups: our detector experiment showed portraits make the eye a small, hard-to-isolate
region. Close-ups make eye localization and iris detail trivial — capture solves what code struggled with.

## Equipment
A modern phone is enough (your test images were ~18 MP — plenty). Macro mode or just get close.
Steady hands / good light. No special rig needed for v1.

## Step-by-step (this week)
1. **Day 0 (30 min):** pick 10 accessible falcons; assign `bird_id`s; note chip/ring/owner in
   `docs/pilot_capture_checklist.csv`.
2. **Session 1:** for each bird, 8–10 close-ups per eye; log a checklist row per (bird, eye).
   Save to `falcon-dataset/pilot/<bird_id>/S1/<eye>/`.
3. **Wait ≥ 3 days.**
4. **Session 2:** repeat framing for the same birds → `.../S2/...`.
5. **Tell me** — I run the leakage-safe POC (split by individual **and** session) and report numbers.

## What we compute (first pass)
- **Verification (1:1):** EER, ROC-AUC, TAR@FAR=1% on **held-out-session** pairs.
- **Identification (1:N):** Top-1 / Top-5 on session-2 probes against a session-1 gallery.
- **Cross-session drop:** same-session vs different-session performance — the real-world signal.
- Breakdowns by eye side + capture condition.

## First go / no-go (pre-registered, adjustable with you)
- **Encouraging:** cross-session EER ≲ 15% and Top-1 ≳ 70% on 10 birds → scale the pilot, keep going.
- **Mixed:** better-than-chance but weak → try periocular vs iris, improve capture, re-test.
- **Discouraging:** near-chance even same-session → rethink the eye as the identity anchor.
> 10 birds gives a *signal*, not a certified result. A credible verdict needs ~25–50 birds; v1 tells
> us whether it's worth scaling.

## Handling & privacy
- Get owner **consent** to photograph/store for research.
- Pilot images are private — `falcon-dataset/pilot/` is gitignored; never commit or post publicly.

## Definition of done (v1)
10 birds × 2 sessions (different days) × both eyes × 8–10 close-ups/eye, identities logged,
checklist complete → POC runs → first numbers recorded in
[`DECISION_LOG.md`](DECISION_LOG.md). Full field guide: [`PILOT_CAPTURE_PROTOCOL.md`](PILOT_CAPTURE_PROTOCOL.md).
