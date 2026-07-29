# Feature Engineering & Scaling

Once data is clean (see [[01-missing-data-and-cleaning|missing-data-and-cleaning]]), the next question is what form it should actually take before a model sees it. Raw columns straight from a database or spreadsheet are rarely the ideal input — feature engineering reshapes them into a form that makes the underlying pattern easier for a model to learn.

## Why scaling matters

Features on wildly different numeric scales (income in the tens of thousands, age in double digits) cause real problems for [[04-optimization|gradient-based training]]: a feature with a large numeric range can dominate the loss purely because of its scale, not because it's actually more important, and it can make the loss surface badly shaped for gradient descent to navigate efficiently.

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# standardization: mean 0, standard deviation 1
scaler = StandardScaler()
scaled = scaler.fit_transform(df[["age", "income"]])

# min-max scaling: squash into [0, 1]
minmax = MinMaxScaler()
scaled_minmax = minmax.fit_transform(df[["age", "income"]])
```

- **Standardization** (subtract mean, divide by standard deviation) is the common default — puts every feature on a comparable scale regardless of its original units.
- **Min-max scaling** squashes values into a fixed range (commonly [0, 1]) — useful when a bounded range is specifically required (some neural network activation functions expect bounded inputs).

## Encoding categorical features

Models operate on numbers, not category labels — "red," "blue," "green" has to become numeric before it can be fed to a model, but naively mapping them to 0, 1, 2 implies an ordering (blue is "between" red and green) that usually doesn't exist.

```python
import pandas as pd
pd.get_dummies(df["color"])   # one-hot encoding: a separate 0/1 column per category, no false ordering implied
```

**One-hot encoding** is the standard fix — turn one categorical column into several binary columns, one per possible value, avoiding the false-ordering problem entirely. For categories with a genuine order (small/medium/large), an explicit ordinal mapping (0, 1, 2) is appropriate specifically because the ordering is real.

## Creating new features from existing ones

Feature engineering isn't just reformatting existing columns — it's often deriving new, more informative ones: a "days since last purchase" feature computed from a raw timestamp, a "price per square foot" feature computed by dividing two existing columns, a "day of week" feature extracted from a date. A well-designed derived feature can make a pattern the model would otherwise need many training examples to infer instead directly visible from a single column.

```python
df["price_per_sqft"] = df["price"] / df["sqft"]
df["day_of_week"] = df["purchase_date"].dt.dayofweek
```

## Why this still matters in the deep learning era

Deep learning is often described as reducing the need for hand-crafted features, since neural networks can learn useful representations directly from raw data (raw pixels, raw text) given enough data — this is largely true for images/text/audio. For structured/tabular data, though, classic ML approaches (and the feature engineering that goes with them, see [[04-other-model-types|other-model-types]]) still frequently outperform deep learning, which is exactly why this remains a core, non-obsolete skill rather than a pre-deep-learning relic.

## Gotchas

- **Fit scalers/encoders on training data only**, then apply the already-fitted transformation to validation/test data (same leakage concern as in [[01-missing-data-and-cleaning|missing-data-and-cleaning]]) — computing a scaler's mean/std on the full dataset including test data leaks test-set information into training.
- One-hot encoding a category with very many distinct values (postal codes, user IDs) produces an impractically wide feature set — for high-cardinality categories, alternatives like target encoding or learned embeddings are usually more appropriate than plain one-hot.
- Creating too many engineered features relative to the number of training examples increases overfitting risk (see [[03-overfitting-and-regularization|overfitting-and-regularization]]) — more features isn't automatically better.

## Related
- [[01-missing-data-and-cleaning|missing-data-and-cleaning]]
- [[03-train-val-test-splits|train-val-test-splits]]
- [[03-overfitting-and-regularization|overfitting-and-regularization]]
