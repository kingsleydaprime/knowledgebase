# Skeleton-Based Fall Detection — Learning

Final year project (Systems Engineering, UNILAG). A pretrained pose estimator turns
video frames into skeletons; a classifier reads a short window of skeletons and says
fall or not fall. Three classifier types are compared on unseen people and timed on
edge hardware.

Repo: `~/code/school/skeleton-based-fall-detection`. Proposal: `project-details.md` in the repo.

Read in order:

1. [[01-research-basics]]: aim vs objectives, what an evaluation protocol is, subject-wise splits and data leakage, the metrics (sensitivity, specificity, G-mean, F2, false alarms per hour) with worked numbers
2. [[02-pose-estimation]]: what a pose estimator outputs, MediaPipe's 33 landmarks and visibility, VIDEO mode and timestamps, the first real finding (36% vs 61% detection)
3. [[03-preprocessing]]: gap filling, hip-centred torso-scaled normalisation, sliding windows and the window-count formula, labelling windows, what *not* to normalise
4. [[04-python-and-shell]]: `uv`, the `src/` layout and `python -m`, writing files safely with `.part` + rename, commands used so far

Each file ends with **In your own words**: questions to answer in writing. Your answers go
in under the question, then the sharpened version.

See also (general vault): [[machine-learning/index|Machine Learning]] · [[devops/01-linux/index|linux]]
