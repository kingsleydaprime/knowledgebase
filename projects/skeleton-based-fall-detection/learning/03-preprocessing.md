# 03 — Preprocessing (the plan, before code)

See also: [[01-research-basics]] · [[02-pose-estimation]] · [[04-python-and-shell]]

Preprocessing turns raw `(frames, 33, 3)` pixel skeletons into windows the classifier can use.
**The same steps run for every dataset, estimator and classifier.** Otherwise a difference in
results could come from preprocessing rather than from the classifier.

## Steps

1. **Pick the person and the joints.** Keep one person (highest mean confidence) and about 13
   body joints. Drop the face and finger points: they're noisy and don't help detect a fall.
2. **Fill short gaps.** If the person is missing for up to 5 frames, fill the gap by
   **interpolation** (draw a straight line between the last known and next known position).
   Keep a **mask** saying which frames were filled, so later you can tell made-up data from real.
   Longer gaps stay missing, because inventing 2 seconds of motion is fiction.
3. **Normalise.** `p' = (p − hip) / L`, where *hip* is the mid-hip point and *L* is torso length
   (mid-shoulder to mid-hip). Subtracting the hip removes *where* in the image the person is.
   Dividing by L removes *how big* they look (near or far from the camera). Clamp L to a minimum,
   because when someone lies flat facing the camera, L can shrink towards 0 and dividing by it blows up.
4. **Cut windows.** Slide a window of W frames forward S frames at a time.
   Count = ⌊(N − W) / S⌋ + 1. Example: N = 180 frames, W = 18 (≈1 s at 18 fps), S = 3 → (162 / 3) + 1 = **55 windows**.
5. **Label windows.** Majority rule: if most frames in the window are inside the marked fall
   period, it's a fall window.

## Two traps

- **Compute hip speed *before* centring.** After centring, the hip is always at (0, 0), so its
  speed is always zero. The fastest signal of a fall (the body dropping) would be gone.
- **Don't min-max normalise over a whole video.** Scaling by the video's own min and max uses
  frames from the *future*, which a live system doesn't have. It also makes a video's numbers
  depend on what happens in it, which quietly hands the classifier a clue.

## In your own words

1. Why do we normalise by torso length instead of by image size?
2. N = 300, W = 18, S = 3. How many windows? (Show the formula.)
