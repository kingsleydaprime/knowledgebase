# 01 — Research basics for this project

See also: [[02-pose-estimation]] · [[03-preprocessing]] · [[04-python-and-shell]]

## Aim vs objectives

- **Aim:** the one sentence saying what the project is *for*. Ours: find which of three
  classifier types gives the best balance of detection on unseen people and speed on edge
  hardware, and how much it drops in ward-like conditions.
- **Objectives:** the 3 to 4 concrete, checkable steps that achieve the aim. Your supervisor's
  rule is that the project succeeds when the objectives are completed, so each one has to be
  something you can point at and say "done". That's also why objectives don't name equipment
  ("edge computing", not "Jetson Orin Nano"): if the hardware changes, the objective still holds.

## Classifier vs model vs pipeline

- **Pipeline:** the whole chain: video → pose estimator → skeletons → preprocessing → classifier → fall / not fall.
- **Pose estimator:** a *pretrained* model we use as is (MediaPipe). We don't train it.
- **Classifier:** the part we build and train. It takes a window of skeletons and outputs a label.
- "Model" is the loose word for any trained thing. In the write-up, say "pose estimator" and "classifier" so nobody has to guess which one you mean.

## The classifier ladder

Three rungs of increasing complexity, all fed the **same** skeleton windows, so any difference
in results comes from the classifier and not the data:

| Rung | What it is | Why it's on the ladder |
|---|---|---|
| A | Handcrafted features (joint angles, speeds, body width/height ratio) + random forest or gradient boosting | Cheap, explainable, fast on edge. The baseline to beat. |
| B | Small LSTM/GRU (recurrent network) | Learns how the skeleton changes over time, with no hand-designed features |
| C | Lightweight ST-GCN (graph convolution) | Treats the skeleton as a graph of joints. Uses both body structure and time |

The research question is whether climbing the ladder is *worth it*. If A is nearly as good and
3× faster, that's a real finding.

## Evaluation protocol

An **evaluation protocol** is the written rulebook for how results are measured. You write it
*before* training, so you can't bend the rules after seeing the numbers. It says: how the data
is split, which metrics, how settings (thresholds, window length) are chosen, and what counts as
a fall being "detected". It will live in `docs/protocol.md`.

## Subject-wise splits and data leakage

**Data leakage** means information from the test set sneaks into training, so the test score
looks better than the real-world score.

Scenario: subject 7 does a fall. You cut that video into 50 overlapping one-second windows and
split the *windows* randomly, 80% train / 20% test. Window 12 lands in training and window 13
in test. They overlap by most of their frames, so the classifier has effectively seen the test
answer. You get 99% accuracy that means nothing.

Splitting **by subject** (a person is entirely in train, or entirely in test) means the test
measures what you care about: *does it work on someone it has never seen?* Most published
95%+ results don't do this, and that's part of the research gap.

**Folds:** with only 17 UP-Fall subjects, one split is noisy (maybe the 3 test people happen
to be easy). So we rotate: 5 folds, each with a different 3 to 4 test subjects, and report the
mean and spread.

## The metrics, with numbers

Counting on a test set: **TP** = falls caught, **FN** = falls missed, **TN** = non-falls
correctly ignored, **FP** = false alarms.

| Metric | Formula | Plain meaning |
|---|---|---|
| Sensitivity (recall) | TP / (TP + FN) | Of the real falls, how many did we catch? |
| Specificity | TN / (TN + FP) | Of the non-falls, how many did we correctly leave alone? |
| Precision | TP / (TP + FP) | When it raised an alarm, how often was it real? |
| G-mean | √(sensitivity × specificity) | One number that's low if *either* one is low |
| F1 | 2PR / (P + R) | Balance of precision and recall |
| F2 | 5PR / (4P + R) | Like F1 but **recall counts more**: a missed fall is worse than a false alarm |
| False alarms per hour | FP / hours of footage | What a nurse actually experiences |

Worked example: 15 falls, 12 caught → sensitivity = 12/15 = 0.80. 100 non-fall clips,
10 false alarms → specificity = 90/100 = 0.90. G-mean = √(0.80 × 0.90) = √0.72 ≈ 0.85.

**Why not plain accuracy?** Falls are rare. If 95% of windows are "not fall", a classifier that
always says "not fall" scores 95% accuracy and catches zero falls. Sensitivity = 0 exposes it.

## In your own words

1. Why does splitting by window instead of by subject make the results look better than they really are?
2. A system catches every fall but raises 40 false alarms an hour. Which metric shows the problem, and why would a hospital switch it off?
3. Why does F2 suit fall detection better than F1?
