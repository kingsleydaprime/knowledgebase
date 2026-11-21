---
id: db728c1f-21ef-4d34-942b-12b335ee0bc2
---

# Trees & Ensembles

## Decision trees
<!-- bite: a12f15e3-e5ad-4b36-92b3-61262ccc00d4 -->

A decision tree learns a sequence of yes/no questions on the features, splitting the data at each node to separate the classes (or reduce variance, for regression):

```
              age < 30?
             /         \
          yes           no
       income<40k?    owns_home?
        /    \          /    \
     ...     ...      ...    ...
```

At each node the tree picks the split that best separates the target (by Gini impurity or entropy for classification). The result is **highly interpretable** — you can read the decision path — and handles non-linear relationships and feature interactions naturally, with no scaling needed.

```python
from sklearn.tree import DecisionTreeClassifier
DecisionTreeClassifier(max_depth=5).fit(X_train, y_train)   # max_depth limits overfitting
```

The catch: a single unconstrained tree **overfits badly** — grown deep enough, it memorizes the training data. `max_depth` and `min_samples_leaf` constrain it, but the real fix is ensembles.

## Random forests — many trees, averaged
<!-- bite: 16c2c210-2d18-4b05-b093-80317ae6c055 -->

Train many decision trees, each on a random subset of the data *and* a random subset of features, then average their predictions (or majority-vote). This **bagging** (bootstrap aggregating) dramatically reduces the overfitting of a single tree — individual trees overfit in *different* ways, and averaging cancels the noise:

```python
from sklearn.ensemble import RandomForestClassifier
RandomForestClassifier(n_estimators=200).fit(X_train, y_train)
model.feature_importances_    # which features mattered — a built-in interpretability win
```

Robust, strong out-of-the-box with little tuning, resistant to overfitting, and gives feature importances. A superb default for tabular data.

## Gradient boosting — the tabular-data champion
<!-- bite: 285a7176-2e58-4f4b-b5db-a028e5a8a78a -->

Instead of averaging independent trees, **boosting** builds trees *sequentially*, each new tree correcting the errors of the ensemble so far. This is usually the **most accurate** approach on structured/tabular data, full stop:

- **XGBoost**, **LightGBM**, **CatBoost** — the dominant, highly-optimized implementations. LightGBM is fast on large data; CatBoost handles categorical features gracefully.

```python
from lightgbm import LGBMClassifier
LGBMClassifier(n_estimators=500, learning_rate=0.05).fit(X_train, y_train)
```

More powerful than random forests but more tuning-sensitive (learning rate, tree depth, number of trees interact — [[ai-ml/02-ml-engineer/04-model-evaluation/03-validation-and-tuning|hyperparameter tuning]] matters here), and it *can* overfit without care.

## Bagging vs boosting — the distinction
<!-- bite: 71318f7d-df18-430c-a337-4e9ac4d0ff9e -->

| | Bagging (Random Forest) | Boosting (XGBoost/LightGBM) |
|---|---|---|
| Trees built | independently, in parallel | sequentially, each fixing the last |
| Reduces | variance (overfitting) | bias (underfitting) *and* variance |
| Tuning | forgiving | sensitive — tune it |
| Default? | great safe default | best accuracy, more effort |

## Why this family matters so much
<!-- bite: e6ed63d0-c50b-4997-89c9-6e6d6feb97b6 -->

For **structured/tabular data** — the most common real-world business case (spreadsheets, transactions, logs) — gradient-boosted trees frequently **outperform deep learning** while training in a fraction of the time, needing no GPU, no feature scaling, and giving feature importances for free. The reflex to reach for a neural network on tabular data is usually wrong ([[ai-ml/02-ml-engineer/01-foundations-of-ml/01-what-is-ml-and-types|choosing the approach]]); start here.

## Related
<!-- bite: 70846b5a-33d5-4cb2-88b4-a38755e3ae32 -->
- [[ai-ml/02-ml-engineer/03-classical-ml/01-regression|Regression]] — the interpretable linear alternative
- [[ai-ml/02-ml-engineer/04-model-evaluation/03-validation-and-tuning|Validation & Tuning]] — essential for boosting
- [[ai-ml/02-ml-engineer/09-building-and-fine-tuning/04-explainable-ai|Explainable AI]] — SHAP is the standard way to explain boosted-tree predictions

## About this lesson
<!-- bite: d4b8a493-f902-40d6-a4ba-2ce455687cf9 -->

**Level:** reference. **Covers:** from the roadmap.sh `machine-learning` roadmap. The most important family for tabular data — and the one that most often quietly beats deep learning there.
