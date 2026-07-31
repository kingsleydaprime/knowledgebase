# Validation & Tuning

**[reference]** — from the roadmap.sh `machine-learning` roadmap. How to estimate real-world performance reliably and pick the best model/settings without fooling yourself.

## The problem with a single train/test split

A single [[ai-ml/02-ml-engineer/02-working-with-data/03-train-val-test-splits|train/test split]] gives one estimate of performance — and that estimate is noisy. You might have gotten a lucky (or unlucky) test set. Worse, if you tune your model against the test set repeatedly, you start *overfitting to the test set itself*, and your reported number stops meaning anything.

## Cross-validation

**K-fold cross-validation** solves the noise problem: split the data into `k` folds, train on `k-1` and validate on the held-out one, rotate through all `k`, and average. Every point is used for both training and validation (in different rounds), giving a more robust estimate and a sense of its variance:

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5)   # 5-fold
scores.mean(), scores.std()                    # estimate AND its stability
```

- **Stratified k-fold** preserves class proportions in each fold — essential for imbalanced classification.
- **LOOCV** (leave-one-out) is k-fold taken to the extreme (`k` = number of points) — nearly unbiased but expensive and high-variance; rarely worth it over 5- or 10-fold.
- **Time-series data breaks ordinary CV** — you can't validate on the past using a model trained on the future. Use forward-chaining / `TimeSeriesSplit` so validation is always chronologically after training.

The discipline that ties it together: keep a **final test set** completely untouched until the very end. Tune with cross-validation on the training data; touch the test set once, to report the number you'll actually trust.

## More classification metrics: ROC-AUC and log-loss

Beyond the accuracy/precision/recall/F1 in [[ai-ml/02-ml-engineer/04-model-evaluation/01-evaluation-metrics|evaluation metrics]], two threshold-independent measures:

- **ROC-AUC** — a classifier outputs a *score*; where you set the threshold trades false positives against false negatives. The ROC curve plots that tradeoff across all thresholds, and **AUC** (area under it) summarizes it: 1.0 is perfect, 0.5 is random. Great for comparing models independent of a specific threshold, and robust to class imbalance.
- **Log-loss** — penalizes *confident wrong* predictions heavily, rewarding well-**calibrated** probabilities (a model that says "90%" should be right ~90% of the time). The metric to watch when you care about the probability, not just the label. It's also what [[ai-ml/02-ml-engineer/03-classical-ml/01-regression|logistic regression]] optimizes.

## Hyperparameter tuning

**Parameters** are learned during training (the weights); **hyperparameters** are set *before* training and control the learning (a tree's `max_depth`, regularization `alpha`, a boosting `learning_rate`, `k` in KNN). Finding good ones is a search, evaluated by cross-validation:

```python
from sklearn.model_selection import GridSearchCV
grid = GridSearchCV(model, {"max_depth": [3, 5, 10], "n_estimators": [100, 300]}, cv=5)
grid.fit(X_train, y_train)
grid.best_params_
```

- **Grid search** — try every combination. Exhaustive but explodes combinatorially.
- **Random search** — sample random combinations; often finds near-best settings far faster, because usually only a few hyperparameters actually matter.
- **Bayesian optimization** (Optuna, Hyperopt) — model which settings are promising and search intelligently; the efficient choice for expensive models.

**The cardinal rule: tune using cross-validation on the training data, never on the test set.** The moment you pick hyperparameters by test-set performance, the test set is contaminated and your final number is optimistic. Nesting (an inner CV loop for tuning, an outer for evaluation) makes this rigorous.

## Model selection

Choosing *which* model, not just its settings, follows the same logic: compare candidates by cross-validated performance on the training data, then confirm the winner once on the held-out test set. Don't forget the non-accuracy axes — training/inference cost, interpretability ([[ai-ml/02-ml-engineer/09-building-and-fine-tuning/04-explainable-ai|explainability]]), and maintenance — a slightly-less-accurate model that's interpretable and cheap often wins in production.

## Related
- [[ai-ml/02-ml-engineer/04-model-evaluation/01-evaluation-metrics|Evaluation Metrics]] — the metrics being cross-validated
- [[ai-ml/02-ml-engineer/04-model-evaluation/02-overfitting-and-regularization|Overfitting & Regularization]] — what honest validation detects
- [[ai-ml/02-ml-engineer/02-working-with-data/03-train-val-test-splits|Train/Val/Test Splits]] — the untouched-test-set discipline
