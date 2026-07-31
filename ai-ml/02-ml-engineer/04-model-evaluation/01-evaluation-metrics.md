# Evaluation Metrics

A single "accuracy" number is often the least informative way to evaluate a model — it can look great while hiding a model that's useless for the actual problem. Which metric to use depends entirely on what kind of task it is and what mistakes actually cost.

## Classification metrics

For a binary classifier, every prediction falls into one of four buckets:

```
                  Actual: Positive    Actual: Negative
Predicted: Positive    True Positive (TP)    False Positive (FP)
Predicted: Negative    False Negative (FN)    True Negative (TN)
```

- **Accuracy** = (TP + TN) / total — the fraction of predictions that were correct. Misleading on imbalanced data: a model that always predicts "no fraud" on a dataset that's 99% non-fraud gets 99% accuracy while being completely useless.
- **Precision** = TP / (TP + FP) — of everything predicted positive, how much actually was? High precision means few false alarms.
- **Recall** = TP / (TP + FN) — of everything that actually was positive, how much did the model catch? High recall means few missed cases.
- **F1 score** — the harmonic mean of precision and recall, a single number balancing both when neither can be prioritized in isolation.

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
accuracy_score(y_true, y_pred)
precision_score(y_true, y_pred)
recall_score(y_true, y_pred)
f1_score(y_true, y_pred)
```

## Why precision/recall tradeoffs matter more than accuracy

A spam filter and a cancer-screening test have opposite priorities even though both are binary classifiers. A spam filter that occasionally lets spam through (false negative) is a minor annoyance; one that occasionally blocks a legitimate email (false positive) can be a real problem — so precision matters more there. A cancer screen that misses an actual case (false negative) is far worse than one that flags a healthy patient for further (more expensive, more precise) testing (false positive) — so recall matters more there. Picking the right metric means understanding which error type is actually more costly for the specific problem, not defaulting to whichever number looks best.

## Regression metrics

For predicting a continuous number rather than a class:

- **Mean Absolute Error (MAE)** — average of `|prediction - actual|`, in the original units, easy to interpret directly ("predictions are off by $8,000 on average").
- **Mean Squared Error (MSE)** — average of `(prediction - actual)²` — penalizes large errors disproportionately more than small ones, since the error is squared before averaging (see [[02-expectation-and-variance|expectation-and-variance]] for the variance-flavored reasoning behind this).
- **R² (R-squared)** — the fraction of variance in the target that the model explains, from 0 (no better than predicting the mean every time) to 1 (perfect predictions).

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
mean_absolute_error(y_true, y_pred)
mean_squared_error(y_true, y_pred)
r2_score(y_true, y_pred)
```

## Confusion matrices — seeing the errors, not just a summary number

A confusion matrix lays out every combination of predicted vs. actual class as a grid, for problems with more than two classes as well as binary ones — it shows *which* classes get confused with which, information a single accuracy number discards entirely. Worth generating routinely, not just when something looks wrong.

```python
from sklearn.metrics import confusion_matrix
confusion_matrix(y_true, y_pred)
```

## Gotchas

- Always compute metrics on the **validation/test set** (see [[03-train-val-test-splits|train-val-test-splits]]), never on training data — training-set metrics measure memorization, not generalization.
- On imbalanced classification data, accuracy alone can be actively misleading (the "always predict the majority class" trap above) — precision, recall, and F1 (or their per-class breakdowns) tell a much more honest story.
- A single aggregate metric can hide poor performance on an important minority subgroup of the data — worth checking metrics broken out by subgroup when different segments matter differently, not just the overall number.

## Related
- [[03-train-val-test-splits|train-val-test-splits]]
- [[ai-ml/02-ml-engineer/04-model-evaluation/02-overfitting-and-regularization|overfitting-and-regularization]]
- [[02-expectation-and-variance|expectation-and-variance]]
