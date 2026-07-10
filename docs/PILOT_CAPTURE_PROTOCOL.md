# Pilot Capture Protocol (Track B)

The pilot is the **only** source of trustworthy biometric metrics. Its whole job is to produce
**genuine same-bird pairs across different sessions**, with reliable identity ground truth, so we
can measure verification, identification, and — critically — **cross-session stability**.

If you follow one rule, follow this: **photograph each falcon on at least two separate days.**
Two sessions on the same day do not test real-world stability.

## Targets
- **Individuals:** aim for **20–50 known falcons** (more is better; even 20 is enough to start).
- **Sessions per falcon:** **≥ 2**, on **different days** (ideally ≥ 1 week apart).
- **Images per eye per session:** **5–10** sharp, close-up frames.
- **Eyes:** capture **both** the left and right eye every session.

## Identity ground truth (record for every falcon)
Use whatever exists — this is what makes the labels trustworthy:
- Microchip / PIT tag number, **and/or**
- Leg ring number, **and/or**
- Owner + the owner's own name/ID for the bird.
Assign each falcon a stable `bird_id` (e.g., `F001`) and reuse it across all sessions.

## Capture guidance (per image)
- **Fill the frame with the eye** — get close; the iris/periocular region should be large and sharp.
- **In focus**, no motion blur; tap-to-focus on the eye.
- **Even lighting**; avoid harsh glare/reflections on the eye. Vary lighting *across* sessions
  (indoor/outdoor) but record it — variation is useful, hidden variation is not.
- Keep the head reasonably straight-on; capture a few slight angles too.
- One eye per photo, filling the frame; note which eye.

## Folder & naming convention
Store pilot images **outside git** under:
```
falcon-dataset\pilot\<bird_id>\<session>\<eye>\<image files>
# example:
falcon-dataset\pilot\F001\S1\left\F001_S1_left_01.jpg
falcon-dataset\pilot\F001\S1\right\F001_S1_right_01.jpg
falcon-dataset\pilot\F001\S2\left\F001_S2_left_01.jpg
```
`session` = `S1`, `S2`, … (one per capture day). This structure encodes identity + session + eye
so the leakage-safe split can be built automatically.

## Session log (fill the checklist for every session)
Record each session in [`pilot_capture_checklist.csv`](pilot_capture_checklist.csv):
`bird_id, session, date, eye, num_images, device, lighting, location, chip_id, ring_id, owner,
species, notes`.

## Consent & privacy
- Get the owner's **consent** to photograph and store images of their falcon for research.
- Pilot images are **privacy-sensitive** — never commit them; keep them in `falcon-dataset\pilot\`.

## Why each rule exists (so nobody "optimizes" them away)
- **≥2 sessions/day-apart** → the *only* way to measure whether identity holds over time.
- **Recorded chip/ring/owner** → trustworthy labels; without them the metrics are unanchored.
- **Both eyes, labeled** → lets us test whether left/right generalize or must be enrolled separately.
- **Consistent close-up** → gives the iris/periocular enough pixels to be discriminative.

## Definition of done (pilot batch 1)
- ≥ 20 birds, each with ≥ 2 sessions on different days, both eyes, 5–10 images/eye/session,
  identity ground truth recorded, checklist complete. Then we run the leakage-safe POC.
