# 02 — Pose estimation

See also: [[01-research-basics]] · [[03-preprocessing]] · [[04-python-and-shell]]

## What a pose estimator gives you

A **pose estimator** is a pretrained neural network. It takes one image and returns where a
person's body joints (landmarks) are. We never train it. We just use its output.

MediaPipe's PoseLandmarker (BlazePose) returns **33 landmarks** per person: face points, shoulders,
elbows, wrists, hips, knees, ankles, heels and toes. For each one:

- `x`, `y`: position, given as a fraction of image width/height (0 to 1). `extract.py` multiplies
  by width and height to store **pixels**.
- `visibility`: 0 to 1, how confident the model is that this joint is visible (not hidden).

So one frame becomes an array of shape `(33, 3)`, and a video becomes `(frames, 33, 3)`.
That's the `keypoints` array in every `.npz` file.

**Why skeletons instead of raw video?** A skeleton is about 100 numbers per frame instead of
640×480×3 ≈ 920,000 pixels. Clothing, lighting and background mostly disappear. The classifier
gets smaller and faster, which matters on edge hardware. The catch is that the whole system can
only be as good as the skeletons. If the pose estimator misses the person, the classifier sees nothing.

## Variants: lite, full, heavy

The same model in three sizes. Bigger is more accurate but slower. This is the
**speed–accuracy trade-off** that runs through the whole project: on edge hardware, pose
estimation can be about 90% of the total processing time (Hoang et al., 2023).

## VIDEO mode and timestamps (from `extract.py`)

MediaPipe has three running modes. IMAGE treats every frame alone. VIDEO **tracks** the person
between frames, which is faster and steadier, but it needs a timestamp for every frame, and the
timestamps must keep increasing. That's why `extract.py`:

- creates a **new landmarker per video**: the timestamps restart at 0 for each video, and an old landmarker would reject them as going backwards;
- computes `ts = max(int(i * 1000 / fps), last_ts + 1)`: rounding at high fps could give two frames the same millisecond, so the `+1` forces it to increase.

## First real finding: detection drops on the fall clip

| Video | Frames | Person found | ms per frame (lite) |
|---|---|---|---|
| URFD fall-01-cam0 | 160 | 36% | 56.0 |
| URFD adl-01-cam0 | 150 | 61% | 40.8 |

Unexplained so far. Candidate causes: BlazePose struggles with people lying down (it's trained
mostly on upright people), the person is small or partly out of frame, or it's the camera angle.
**A guess isn't a finding.** Check it with the overlay video before acting on it.

**adl-01, checked by eye:** empty room for frames 0–57, then a man walks in and bends.
MediaPipe found him in every frame he was in (92/92). The 61% came from the empty room, not
from the model failing.

**Lesson: a percentage is only as good as its denominator.** "Found in 61% of frames" divides
by *all* frames, so an empty room counts as a miss. The fair measure divides by the frames where
a person is actually present. Always ask "61% *of what*?" before trusting a rate.

**fall-01, checked by eye:** the man is there from frame 0, yet he's missed, and at frame 62
the skeleton is drawn on an **office chair**. The real cause: URFD's `.mp4` is a **side-by-side
composite**, with depth on the left and RGB on the right. MediaPipe was given both halves as one
picture, so the person is small, there's a grey depth "ghost" of him on the left, and furniture
gets mistaken for a body.

Two lessons:
1. **Look at your input before trusting your output.** One frame opened by eye would have shown
   this before any extraction. Garbage in, garbage out. The numbers looked like a model problem,
   but it was a data problem.
2. **"Detected" is not "correct".** A skeleton on a chair is worse than no skeleton: the
   classifier would treat chair positions as body positions. Counting detections without
   checking where they land measures nothing.

## In your own words

1. Why does a pose estimator failing on lying-down people hurt a *fall* detector in particular?
2. What does `visibility` tell you, and why keep it rather than throwing it away?
