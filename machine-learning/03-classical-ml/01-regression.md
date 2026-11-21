---
id: cdcae978-c828-4db6-b1f9-830a9252bcd2
---

# Regression & Regularization

Regression is a way of predicting a number by fitting a line (or a curve) through past data. For example, you can predict a house price from its size and location. This lesson also covers logistic regression, which predicts a yes or no answer, and regularization, which stops a model from memorising its training data.

## Linear regression — the foundation
<!-- bite: 395ef0c8-6181-424c-b3a5-59a101825860 -->

Fit a straight line (or hyperplane) through the data: predict `y = w₁x₁ + w₂x₂ + … + b`, choosing weights `w` that minimize the squared error between predictions and actuals ([[machine-learning/00-foundations/03-mathematics/04-optimization|optimization]]). Simple, fast, and interpretable — each weight tells you how much that feature moves the prediction.

```python
from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(X_train, y_train)
model.coef_        # the weights — directly interpretable
model.predict(X_test)
```

It's the baseline you should almost always try first on a regression problem: if a linear model does well, you're done, and you have an interpretable result. Assumes a roughly linear relationship — its main limitation.

## Polynomial regression — curved relationships
<!-- bite: bdb044f9-8221-4080-874f-d899ddac2a84 -->

Still linear *in the weights*, but you add powers of features (`x², x³`) so the model can fit curves. Powerful but the classic overfitting trap: a high enough degree fits the training points perfectly and generalizes terribly ([[machine-learning/04-model-evaluation/02-overfitting-and-regularization|overfitting]]). Degree is a hyperparameter to tune, not maximize.

## Logistic regression — classification, despite the name
<!-- bite: 5bbe4c6d-9222-4f67-af9c-c10eff1209ab -->

Despite "regression" in the name, this is the **classification** workhorse. It runs a linear combination through a sigmoid to output a **probability** (0–1), then thresholds it into a class:

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression().fit(X_train, y_train)
model.predict_proba(X_test)   # calibrated-ish probabilities, not just labels
```

Fast, interpretable, outputs probabilities (useful when you care about confidence, not just the label), and a genuinely strong baseline for binary classification. Extends to multi-class. Trained by minimizing **log-loss** ([[machine-learning/04-model-evaluation/03-validation-and-tuning|log-loss]]) rather than squared error.

## Regularization — the cure for overfitting
<!-- bite: 01370fe4-0bb5-40c5-bba1-805e3f71c58b -->

The single most important idea attached to linear models: add a penalty on large weights to the loss, discouraging the model from fitting noise. Three flavors:

| Method | Penalty | Effect |
|---|---|---|
| **Ridge (L2)** | sum of squared weights | shrinks all weights toward zero, none exactly zero — handles correlated features well |
| **Lasso (L1)** | sum of absolute weights | drives some weights to *exactly* zero → automatic **feature selection** |
| **Elastic Net** | mix of L1 + L2 | best of both; the pragmatic default when unsure |

```python
from sklearn.linear_model import Ridge, Lasso
Ridge(alpha=1.0).fit(X_train, y_train)   # alpha = regularization strength, a key hyperparameter
```

Regularization is the concrete mechanism behind the bias-variance tradeoff ([[machine-learning/04-model-evaluation/02-overfitting-and-regularization|overfitting & regularization]]): more penalty = simpler model = more bias, less variance. `alpha` is tuned via [[machine-learning/04-model-evaluation/03-validation-and-tuning|cross-validation]]. The same L1/L2 idea reappears in deep learning as weight decay.

## When regression is the right tool
<!-- bite: 9cbc75d4-b30f-4f95-853c-08e95ff64043 -->

For **structured/tabular data**, a regularized linear or logistic model is often competitive with far fancier methods, trains instantly, and is interpretable — a real advantage when you need to *explain* a decision ([[machine-learning/09-building-and-fine-tuning/04-explainable-ai|explainable AI]]). Reach past it to [[machine-learning/03-classical-ml/02-trees-and-ensembles|trees/ensembles]] when relationships are strongly non-linear, or to [[machine-learning/05-deep-learning/index|deep learning]] for unstructured data (text/images).

## Related
<!-- bite: bc95fe44-a3c8-485e-bef2-7f2b04778566 -->
- [[machine-learning/04-model-evaluation/02-overfitting-and-regularization|Overfitting & Regularization]] — what regularization fights
- [[machine-learning/03-classical-ml/02-trees-and-ensembles|Trees & Ensembles]] — the non-linear alternative
- [[machine-learning/00-foundations/03-mathematics/04-optimization|Optimization]] — how the weights are fit

## About this lesson
<!-- bite: f015331b-f67e-4f00-8faf-11a5cb42039e -->

**Level:** reference. **Covers:** from the roadmap.sh `machine-learning` roadmap. The starting point of the algorithm zoo, and often the right ending point too.
