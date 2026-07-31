# Train / Validation / Test Splits

A model's whole point is to perform well on data it hasn't seen (see [[ai-ml/00-foundations/02-what-is-a-model|generalization]]) — so evaluating it on the same data it trained on tells you almost nothing useful. Splitting data into separate, non-overlapping sets is how you get an honest read on whether a model actually generalizes.

## The three sets and what each is for

- **Training set** — what the model actually learns from; parameters get updated based on this data (see [[04-optimization|optimization]]).
- **Validation set** — used *during* development to make decisions: which hyperparameters to use, when to stop training, which of several model variants to keep. The model never trains on this directly, but you *do* make choices based on it — which means it gets a little "used up" as a fair test the more decisions you make against it.
- **Test set** — touched exactly once, at the very end, to report a final, honest performance number. If you tune anything based on test-set performance, it stops being a fair test — it's effectively become a second validation set, whether or not that's the intention.

```python
from sklearn.model_selection import train_test_split

X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
# common ratio: 70% train, 15% validation, 15% test
```

## Why the split needs to be random (usually)

A dataset sorted by some incidental order (by date, by category) that gets split by simply taking the first 70% as training risks the training set looking systematically different from the rest — shuffling before splitting (what `train_test_split` does by default) avoids that. The exception is genuinely time-ordered data (see below), where a random shuffle is actually the wrong choice.

## Time series — why random splitting can be wrong

If the data has a time dimension and the model is meant to predict the future from the past, a random split can leak future information into training (the model implicitly "sees" patterns from data chronologically after the point it's meant to predict). The correct split for this case is chronological: train on earlier data, validate/test on strictly later data, matching how the model will actually be used in practice.

```python
# chronological split, not random, for time-dependent data
cutoff_train = "2024-01-01"
cutoff_val = "2024-06-01"
train = df[df["date"] < cutoff_train]
val = df[(df["date"] >= cutoff_train) & (df["date"] < cutoff_val)]
test = df[df["date"] >= cutoff_val]
```

## Cross-validation — squeezing more out of limited data

With a small dataset, a single validation split wastes data and can give a noisy, split-dependent estimate of performance. **K-fold cross-validation** splits the training data into k chunks, trains k times, each time holding out a different chunk as validation, then averages the results — giving a more stable performance estimate at the cost of k times the training compute. Common for smaller, classic-ML-scale datasets; less common for large deep learning models where a single training run is already expensive.

## Gotchas

- **Data leakage** — any information from validation/test data influencing training (fitting a scaler on the whole dataset before splitting, duplicate rows split across train and test, features that implicitly encode the target) inflates reported performance in a way that won't hold up on genuinely new data. This is one of the most common, hardest-to-notice mistakes in applied ML — see the same concern raised in [[01-missing-data-and-cleaning|missing-data-and-cleaning]] and [[02-feature-engineering-and-scaling|feature-engineering-and-scaling]].
- Repeatedly tuning against the same validation set across many iterations can cause a model to indirectly overfit to that validation set, even without ever training on it directly — a large gap between validation performance and true test/production performance is the usual symptom.
- Reusing the test set more than once (checking it, adjusting something, checking again) quietly turns it into another validation set — the final reported number stops being an honest, one-shot estimate.

## Related
- [[01-missing-data-and-cleaning|missing-data-and-cleaning]]
- [[02-feature-engineering-and-scaling|feature-engineering-and-scaling]]
- [[ai-ml/02-ml-engineer/04-model-evaluation/02-overfitting-and-regularization|overfitting-and-regularization]]
