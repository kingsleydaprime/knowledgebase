---
id: adc99fd9-ba20-4271-8c90-eafbd9215c31
---

# Evaluation Metrics 3: Regression Metrics

Regression metrics measure how far predicted numbers are from the actual numbers.

## Before you start
<!-- bite: 6541a25f-9dc9-41ab-b639-4e04a767f787 -->

You should know what regression is ([[machine-learning/01-foundations-of-ml/01-what-is-ml-and-types|What ML Is]]). You need averages, squares and square roots.

After this lesson you will be able to:

- calculate MAE, MSE, RMSE, R² and MAPE from a table of actual and predicted values;
- say what each one tells you and how they differ;
- interpret the results for someone who doesn't know the formulas.

Those metrics were for classification. For regression we use different ones, because the output is a number and not a class.

## What regression metrics are
<!-- bite: 50c46bab-b853-4c46-90ce-efe23eeee35d -->

Regression metrics measure how far a model's predicted numbers are from the actual numbers. In the regression task, we are supposed to predict the target variable which is in the form of continuous values.

Next: five metrics, one per bite, starting with MAE.

## 1. Mean Absolute Error (MAE)
<!-- bite: d1e86f31-add5-4404-9e8c-89589cf1a89b -->

It calculates the average of the absolute difference between the predicted and actual values. It gives a clear view of the model's prediction accuracy but it does not show whether the errors are due to over- or under-prediction.

$$
MAE = \frac{1}{N} \sum_{j=1}^{N} |y_j - \hat{y}_j|
$$

where y\_j = Actual value and ŷ\_j = Predicted value.

## 2. Mean Squared Error (MSE)
<!-- bite: a48d246a-5714-4561-ab84-53ef97080dd5 -->

It calculates the average of the squared difference between the predicted and actual values. Squaring the differences ensures that larger errors are penalized more heavily, which helps in making it sensitive to outliers.

$$
MSE = \frac{1}{N} \sum_{j=1}^{N} (y_j - \hat{y}_j)^2
$$

## 3. Root Mean Squared Error (RMSE)
<!-- bite: ec98a294-7204-42f0-b37c-ec8bdba9b948 -->

This is the square root of MSE, bringing the metric back to the original scale of the data. Like MSE, it heavily penalizes larger errors but is easier to interpret as it is in the same units as the target variable.

$$
RMSE = \sqrt{\frac{\sum_{j=1}^{N} (y_j - \hat{y}_j)^2}{N}}
$$

## 4. R² (R-squared)
<!-- bite: d5fd5163-2eba-4158-ac33-5351289b7bd8 -->

The R² score represents the proportion of the variance in the dependent variable that is predictable from the independent variable(s).

$$
R^2 = 1 - \frac{\sum_{j=1}^{N} (y_j - \hat{y}_j)^2}{\sum_{j=1}^{N} (y_j - \bar{y})^2}
$$

where ȳ = Mean of the actual values, y\_j = Actual value and ŷ\_j = Predicted value.

## 5. Mean Absolute Percentage Error (MAPE)
<!-- bite: 34a2be1c-bcd8-48af-a81c-39bd0ed81ee4 -->

MAPE is a popular percentage-based metric used to measure forecasting accuracy by calculating the average absolute percentage difference between predicted and actual values.

The formula is below, where N = number of observations, A\_i is the actual value and P\_i is the predicted value.

$$
\text{MAPE} = \frac{1}{N} \sum_{i=1}^{N} \left| \frac{A_i - P_i}{A_i} \right| \times 100\%
$$

## Regression metrics in scikit-learn
<!-- bite: fe96f416-6232-489f-9662-67248c2ecbcc -->

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

## Check your understanding
<!-- bite: 02100e52-73e4-4806-85e3-ccc1981e0e6a -->

Try each one before you open the answer.

1. <!-- q: gap id="bcf9c1f7" answers="1.33333333333|4/3;2.66666666667|8/3" sigfigs="2" -->
   Fill in the gaps. Actual = (10, 20, 30), predicted = (12, 18, 30). MAE is ___ and MSE is ___.

   <details><summary>Answer</summary>

   Errors are 2, 2 and 0. MAE = (2 + 2 + 0) / 3 = 1.333. MSE = (4 + 4 + 0) / 3 = 2.667.

   </details>

2. <!-- q: mcq id="05cbd500" -->
   Why is RMSE often easier to explain than MSE?

   - [ ] It is always smaller
   - [x] It is in the same units as the target, because the square root undoes the squaring
   - [ ] It ignores outliers

   <details><summary>Answer</summary>

   It is in the same units as the target variable, because the square root undoes the squaring.

   </details>

3. <!-- q: exact id="e7d57f70" answer="10" accept="10%" tolerance="0.01" -->
   The actual value is 200 and the prediction is 180. With only this one value, what is the MAPE, as a percentage?

   <details><summary>Answer</summary>

   10%. |200 − 180| / 200 × 100% = 20 / 200 × 100% = 10%.

   </details>

4. <!-- q: mcq id="bc0da31c" -->
   A model has R² = 1. What does that mean?

   - [x] Perfect predictions
   - [ ] No better than predicting the mean every time
   - [ ] Every prediction is off by 1

   <details><summary>Answer</summary>

   Perfect predictions. R² = 0 means no better than always predicting the mean.

   </details>

5. <!-- q: open id="fd115cc9" -->
   MAE = 4.1 and RMSE = 4.32 for a forecast. What does it mean that they are so close?

   <details><summary>Answer</summary>

   There are no big, sudden misses. RMSE punishes large errors more, so if it is close to MAE the errors are all about the same size.

   </details>

## Check your understanding: worked problems
<!-- bite: 3dc91ae6-cd88-4cf0-ad43-8be89649475b -->

Work each one out on paper first, then type your answer.

1. <!-- q: exact id="93d301cd" answer="1" accept="one" -->
   Actual = (3, 5, 8), predicted = (2, 5, 10). What is the MAE?

   <details><summary>Answer</summary>

   1. The errors are 1, 0 and 2, so MAE = 3/3 = 1.

   </details>

2. <!-- q: gap id="caf644e3" answers="1.66666666667|5/3;1.29099444874" sigfigs="2" -->
   Fill in the gaps. Actual = (3, 5, 8), predicted = (2, 5, 10). MSE is ___ and RMSE is ___.

   <details><summary>Answer</summary>

   MSE = (1 + 0 + 4)/3 ≈ 1.67. RMSE = √(5/3) ≈ 1.29, in the same units as the target.

   </details>

3. <!-- q: exact id="2b8c2b46" answer="0.605263157895" sigfigs="2" -->
   Actual = (3, 5, 8), predicted = (2, 5, 10). What is R²? (ȳ = 16/3, and Σ(y − ȳ)² = 38/3.)

   <details><summary>Answer</summary>

   About 0.61. R² = 1 − 5 ÷ (38/3) = 1 − 15/38 ≈ 0.605.

   </details>

## Practice — independent task
<!-- bite: bd7d2d80-eb4d-46e5-8019-80cbeed06f20 -->

Practice question 1 and past question 2 in the [[machine-learning/ssg-535-question-bank|SSG 535 question bank]] each give a table of actual and predicted values. Calculate every metric the question asks for, then write two sentences on what they mean. **Done when** your table has the total of the squared errors and the total of (y − ȳ)², because R² needs both.

## Before moving on
<!-- bite: 37ef4aac-65fe-4600-85e5-0242d61e4f75 -->

MAE is the average size of the error, MSE squares the errors so big ones count more, RMSE brings MSE back to the original units, R² compares the model with always guessing the mean, and MAPE gives the error as a percentage.

**Next:** [[machine-learning/04-model-evaluation/04-overfitting-and-regularization|Overfitting and Regularization]]. A metric is only honest if it is measured on unseen data. That brings us back to generalizing, overfitting and underfitting.

## About this lesson
<!-- bite: 071c4099-1b38-4e00-a1fc-03ad4dc0e6da -->

**Level:** Intermediate. **Covers:** MAE, MSE, RMSE, R² and MAPE. Part 3 of 3 on evaluation metrics. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
