# Regression & Regularization

**[reference]** — from the roadmap.sh `machine-learning` roadmap. The starting point of the algorithm zoo, and often the right ending point too.

## Linear regression — the foundation

Fit a straight line (or hyperplane) through the data: predict `y = w₁x₁ + w₂x₂ + … + b`, choosing weights `w` that minimize the squared error between predictions and actuals ([[ai-ml/00-foundations/03-mathematics/04-optimization|optimization]]). Simple, fast, and interpretable — each weight tells you how much that feature moves the prediction.

```python
from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(X_train, y_train)
model.coef_        # the weights — directly interpretable
model.predict(X_test)
```

It's the baseline you should almost always try first on a regression problem: if a linear model does well, you're done, and you have an interpretable result. Assumes a roughly linear relationship — its main limitation.

## Polynomial regression — curved relationships

Still linear *in the weights*, but you add powers of features (`x², x³`) so the model can fit curves. Powerful but the classic overfitting trap: a high enough degree fits the training points perfectly and generalizes terribly ([[ai-ml/02-ml-engineer/04-model-evaluation/02-overfitting-and-regularization|overfitting]]). Degree is a hyperparameter to tune, not maximize.

## Logistic regression — classification, despite the name

Despite "regression" in the name, this is the **classification** workhorse. It runs a linear combination through a sigmoid to output a **probability** (0–1), then thresholds it into a class:

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression().fit(X_train, y_train)
model.predict_proba(X_test)   # calibrated-ish probabilities, not just labels
```

Fast, interpretable, outputs probabilities (useful when you care about confidence, not just the label), and a genuinely strong baseline for binary classification. Extends to multi-class. Trained by minimizing **log-loss** ([[ai-ml/02-ml-engineer/04-model-evaluation/03-validation-and-tuning|log-loss]]) rather than squared error.

## Regularization — the cure for overfitting

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

Regularization is the concrete mechanism behind the bias-variance tradeoff ([[ai-ml/02-ml-engineer/04-model-evaluation/02-overfitting-and-regularization|overfitting & regularization]]): more penalty = simpler model = more bias, less variance. `alpha` is tuned via [[ai-ml/02-ml-engineer/04-model-evaluation/03-validation-and-tuning|cross-validation]]. The same L1/L2 idea reappears in deep learning as weight decay.

## When regression is the right tool

For **structured/tabular data**, a regularized linear or logistic model is often competitive with far fancier methods, trains instantly, and is interpretable — a real advantage when you need to *explain* a decision ([[ai-ml/02-ml-engineer/09-building-and-fine-tuning/04-explainable-ai|explainable AI]]). Reach past it to [[ai-ml/02-ml-engineer/03-classical-ml/02-trees-and-ensembles|trees/ensembles]] when relationships are strongly non-linear, or to [[ai-ml/02-ml-engineer/05-deep-learning/README|deep learning]] for unstructured data (text/images).

## Related
- [[ai-ml/02-ml-engineer/04-model-evaluation/02-overfitting-and-regularization|Overfitting & Regularization]] — what regularization fights
- [[ai-ml/02-ml-engineer/03-classical-ml/02-trees-and-ensembles|Trees & Ensembles]] — the non-linear alternative
- [[ai-ml/00-foundations/03-mathematics/04-optimization|Optimization]] — how the weights are fit
