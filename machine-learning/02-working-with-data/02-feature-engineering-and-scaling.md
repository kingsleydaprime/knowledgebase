---
id: 3638bc99-baee-4710-8dbd-dee0f38a854a
---

# Feature Engineering & Scaling

Feature engineering is reshaping raw columns so a model can learn from them more easily.

## What feature engineering is
<!-- bite: 405ebe05-b703-4aa8-92d1-181be9837607 -->

Once data is clean (see [[01-missing-data-and-cleaning|missing-data-and-cleaning]]), the next question is what form it should actually take before a model sees it. Raw columns straight from a database or spreadsheet are rarely the ideal input — feature engineering reshapes them into a form that makes the underlying pattern easier for a model to learn.

Next: scaling, encoding categories, and making new features.

## Why scaling matters
<!-- bite: 840754e1-27de-4b3a-a3ea-6206569a3f49 -->

Features on wildly different numeric scales (income in the tens of thousands, age in double digits) cause real problems for [[04-optimization|gradient-based training]]: a feature with a large numeric range can dominate the loss purely because of its scale, not because it's actually more important, and it can make the loss surface badly shaped for gradient descent to navigate efficiently.

## Scaling in scikit-learn
<!-- bite: 29d92405-2f74-4a94-b03d-2a2332400ebb -->

scikit-learn has a ready-made scaler for each of the two common ways to scale.

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
<!-- bite: 8e933864-87bd-4109-8833-3885adf7eb47 -->

Models operate on numbers, not category labels — "red," "blue," "green" has to become numeric before it can be fed to a model, but naively mapping them to 0, 1, 2 implies an ordering (blue is "between" red and green) that usually doesn't exist.

```python
import pandas as pd
pd.get_dummies(df["color"])   # one-hot encoding: a separate 0/1 column per category, no false ordering implied
```

**One-hot encoding** is the standard fix — turn one categorical column into several binary columns, one per possible value, avoiding the false-ordering problem entirely. For categories with a genuine order (small/medium/large), an explicit ordinal mapping (0, 1, 2) is appropriate specifically because the ordering is real.

## Creating new features from existing ones
<!-- bite: b68f3ede-b022-426e-96b5-67fd9ffbabc3 -->

Feature engineering isn't just reformatting existing columns — it's often deriving new, more informative ones: a "days since last purchase" feature computed from a raw timestamp, a "price per square foot" feature computed by dividing two existing columns, a "day of week" feature extracted from a date. A well-designed derived feature can make a pattern the model would otherwise need many training examples to infer instead directly visible from a single column.

```python
df["price_per_sqft"] = df["price"] / df["sqft"]
df["day_of_week"] = df["purchase_date"].dt.dayofweek
```

## Why this still matters in the deep learning era
<!-- bite: 21859fa1-5e7a-413d-b3af-d487700970b3 -->

Deep learning is often described as reducing the need for hand-crafted features, since neural networks can learn useful representations directly from raw data (raw pixels, raw text) given enough data — this is largely true for images/text/audio. For structured/tabular data, though, classic ML approaches (and the feature engineering that goes with them, see [[ai-engineering/03-the-model-landscape|other-model-types]]) still frequently outperform deep learning, which is exactly why this remains a core, non-obsolete skill rather than a pre-deep-learning relic.

## Feature scaling worked by hand
<!-- bite: 58924192-ead3-4bee-9399-8250e14c191d -->

Imagine one feature is age (about 20 to 60) and another is income (about 50,000 to 500,000). When we measure distance, income would completely drown out age. Methods that use distance, like KNN, K-Means and SVM, would then ignore age. Scaling puts all features on a similar range. Two common ways:

## Min-max scaling worked by hand
<!-- bite: 1f9ef3e1-8eef-429c-bec9-00577ea636a1 -->

**Min-max scaling** squeezes every value into the range 0 to 1:

$$
x_{new} = \frac{x - x_{min}}{x_{max} - x_{min}}
$$

Example: ages 20, 30 and 60. For the age 30:

$$
x_{new} = \frac{30 - 20}{60 - 20} = 0.25
$$

So 20 becomes 0, 30 becomes 0.25 and 60 becomes 1.

## Standardization worked by hand
<!-- bite: 3795d959-2fdc-41c4-adf3-69b3b4990882 -->

**Standardization** moves the average to 0 and the spread to 1:

$$
z = \frac{x - \mu}{\sigma}
$$

where the mean and the standard deviation are:

$$
\mu = \frac{1}{n} \sum_{i=1}^{n} x_i \qquad \sigma = \sqrt{\frac{\sum_{i=1}^{n} (x_i - \mu)^2}{n}}
$$

Example: the values 10, 20 and 30 have a mean of 20, so:

$$
\sigma = \sqrt{\frac{(10-20)^2 + (20-20)^2 + (30-20)^2}{3}} = \sqrt{\frac{200}{3}} = 8.165
$$

Then 10 becomes (10 − 20) / 8.165 = −1.225, 20 becomes 0, and 30 becomes +1.225.

## Which models need scaling?
<!-- bite: c07257e4-4c88-43f6-8fbe-d141a839cf51 -->

KNN, K-Means, LVQ and SVM do, because they use distances. Decision trees and Naive Bayes do not, because they look at one feature at a time.

## Gotchas
<!-- bite: a1c0d347-0015-4c92-a8a9-915b4f352000 -->

- **Fit scalers/encoders on training data only**, then apply the already-fitted transformation to validation/test data (same leakage concern as in [[01-missing-data-and-cleaning|missing-data-and-cleaning]]) — computing a scaler's mean/std on the full dataset including test data leaks test-set information into training.
- One-hot encoding a category with very many distinct values (postal codes, user IDs) produces an impractically wide feature set — for high-cardinality categories, alternatives like target encoding or learned embeddings are usually more appropriate than plain one-hot.
- Creating too many engineered features relative to the number of training examples increases overfitting risk (see [[machine-learning/04-model-evaluation/04-overfitting-and-regularization|overfitting-and-regularization]]) — more features isn't automatically better.

## Check your understanding
<!-- bite: ed766264-1cf9-4d79-8c16-7aa2620f20bc -->

Try each one before you open the answer.

1. <!-- q: exact id="907b3e64" answer="0.25" accept="1/4" tolerance="0.001" -->
   Ages are 20, 30 and 60. With min-max scaling, what does 30 become?

   <details><summary>Answer</summary>

   0.25. (30 − 20) ÷ (60 − 20) = 10 ÷ 40 = 0.25.

   </details>

2. <!-- q: gap id="bda10ce2" answers="0|zero;1|one" -->
   Fill in the gaps. After standardization, every feature has a mean of ___ and a standard deviation of ___.

   <details><summary>Answer</summary>

   0, then 1. Standardization subtracts the mean and divides by the standard deviation.

   </details>

3. <!-- q: mcq id="5de0bfe9" -->
   Why is mapping red, blue and green to 0, 1 and 2 usually a bad idea?

   - [ ] Models can't read numbers that small
   - [x] It implies an order (blue is "between" red and green) that doesn't exist
   - [ ] It uses too many columns

   <details><summary>Answer</summary>

   It invents a false order. One-hot encoding fixes this by giving each colour its own 0/1 column. For categories with a real order, like small, medium and large, a 0, 1, 2 mapping is fine.

   </details>

4. <!-- q: mcq id="600ccc17" -->
   Which models need their features scaled? Choose all that apply.

   - [x] KNN
   - [x] K-Means
   - [x] SVM
   - [ ] Decision trees
   - [ ] Naive Bayes

   <details><summary>Answer</summary>

   KNN, K-Means and SVM. They use distances, so a feature with a big range drowns out the others. Decision trees and Naive Bayes look at one feature at a time, so scale doesn't matter to them.

   </details>

5. <!-- q: open id="b9f214d3" -->
   Give one example of creating a new feature from existing columns, and say why it can help the model.

   <details><summary>Answer</summary>

   For example, price ÷ square footage gives "price per square foot", and a date can give "day of week". A good derived feature puts a pattern into one column, where the model would otherwise need many examples to work it out by itself.

   </details>

## Check your understanding: worked problems
<!-- bite: 105b938a-6edd-4424-abca-88e3f3038690 -->

Work each one out on paper first, then type your answer.

1. <!-- q: exact id="7113dd27" answer="0.25" accept="1/4" -->
   A feature runs from a minimum of 50 to a maximum of 150. With min-max scaling, what does 75 become?

   <details><summary>Answer</summary>

   0.25. (75 − 50) ÷ (150 − 50) = 25 ÷ 100 = 0.25.

   </details>

2. <!-- q: exact id="9bfb5fa4" answer="1.22474487139" sigfigs="2" -->
   The values are 2, 4 and 6 (mean 4, standard deviation √(8/3) ≈ 1.633). What does 6 become after standardization?

   <details><summary>Answer</summary>

   About 1.22. z = (6 − 4) ÷ 1.633 ≈ 1.225. Then 2 becomes about −1.22, and 4 becomes 0.

   </details>

3. <!-- q: gap id="cb334a82" answers="0;0.5;1" -->
   Fill in the gaps. Ages 10, 50 and 90 are min-max scaled. They become ___, ___ and ___.

   <details><summary>Answer</summary>

   0, 0.5 and 1. The smallest value always becomes 0 and the largest becomes 1; 50 is halfway.

   </details>

## Related
<!-- bite: 581e30ed-eba3-4b48-b863-f60bce460d73 -->
- [[01-missing-data-and-cleaning|missing-data-and-cleaning]]
- [[03-train-val-test-splits|train-val-test-splits]]
- [[machine-learning/04-model-evaluation/04-overfitting-and-regularization|overfitting-and-regularization]]
