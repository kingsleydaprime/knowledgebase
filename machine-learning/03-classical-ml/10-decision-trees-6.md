---
id: db728c1f-21ef-4d34-942b-12b335ee0bc2
---

# Decision Trees 6: Pruning, Strengths and Ensembles

Pruning is how we stop a decision tree from over-fitting. If we let the tree grow until every leaf is pure, it fits the training data too closely and will not generalize well.

## Before you start
<!-- bite: 74f478d0-7a92-454c-ac1b-e9c73fb71d57 -->

You should be able to build a tree with entropy or Gini ([[machine-learning/03-classical-ml/08-decision-trees-4|Decision Trees 4]]) and know what over-fitting means ([[machine-learning/04-model-evaluation/04-overfitting-and-regularization|Overfitting]]).

After this lesson you will be able to:

- name pre-pruning and post-pruning and three pre-pruning criteria;
- list the advantages, disadvantages and applications of decision trees;
- explain how random forests and gradient boosting combine many trees.

## Pruning: Preventing Over-fitting in Decision Trees
<!-- bite: c0f0e488-ba1f-48cb-9a1c-edc84c637f3e -->

Remember that decision trees are prone to over-fitting. If we let the tree grow until every leaf is pure, it fits the training data too closely and will not generalize well.

> **Note:** There are two common strategies to prevent over-fitting:
>
> - stopping the creation of the tree early (also called **pre-pruning**)
> - building the tree but then removing or collapsing nodes that contain little information (also called **post-pruning** or just **pruning**)

Possible criteria for pre-pruning include:

- Limiting the maximum depth of the tree
- Limiting the maximum number of leaves
- Requiring a minimum number of points in a node to keep splitting it

## Advantages and Disadvantages of Decision Trees
<!-- bite: b67ea0bc-7a34-4275-b560-07d42ecc1464 -->

| Advantages | Disadvantages |
| --- | --- |
| 1. It is easy to interpret | 1. Prone to over-fitting |
| 2. It is more flexible | 2. It has high variance estimators |
| 3. It requires little to no data preparation | 3. It can be costly |

## Applications
<!-- bite: dffb0f46-74d6-464b-b4bf-e5967565fd37 -->

1. Fraud detection
2. Loan Approval in Banking
3. Medical diagnosis
4. Predicting exam results in education

## Decision trees in scikit-learn
<!-- bite: a12f15e3-e5ad-4b36-92b3-61262ccc00d4 -->

A decision tree learns a sequence of yes/no questions on the features, splitting the data at each node to separate the classes (or reduce variance, for regression):

```text
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

More powerful than random forests but more tuning-sensitive (learning rate, tree depth, number of trees interact — [[machine-learning/04-model-evaluation/05-validation-and-tuning|hyperparameter tuning]] matters here), and it *can* overfit without care.

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

For **structured/tabular data** — the most common real-world business case (spreadsheets, transactions, logs) — gradient-boosted trees frequently **outperform deep learning** while training in a fraction of the time, needing no GPU, no feature scaling, and giving feature importances for free. The reflex to reach for a neural network on tabular data is usually wrong ([[machine-learning/01-foundations-of-ml/01-what-is-ml-and-types|choosing the approach]]); start here.

## Check your understanding
<!-- bite: c4ec5e08-2b36-4f92-8a4f-8ca3531918d5 -->

Try each one before you open the answer.

1. Name the two strategies to prevent over-fitting in decision trees.

   <details><summary>Answer</summary>

   Pre-pruning (stopping the creation of the tree early) and post-pruning (building the tree, then removing or collapsing nodes that contain little information).

   </details>

2. Give two pre-pruning criteria.

   <details><summary>Answer</summary>

   Any two of: limit the maximum depth, limit the maximum number of leaves, require a minimum number of points in a node to keep splitting it.

   </details>

3. Why does a random forest over-fit less than one deep tree?

   <details><summary>Answer</summary>

   Each tree is trained on a random part of the data and features, so the trees over-fit in different ways. Averaging their answers cancels much of that noise.

   </details>

## Practice — independent task
<!-- bite: 57c3dc48-e6a3-4540-8103-27f36d3c85f6 -->

Past question 6(b) in the [[machine-learning/ssg-535-question-bank|SSG 535 question bank]] asks for a full decision tree workflow for predicting student performance: preprocessing, model choice, evaluation. Write your answer as three short lists. **Done when** your answer mentions the train/test split, a pruning setting and at least two metrics. Then compare with the solution.

## Before moving on
<!-- bite: 1c395886-dbb2-4b1b-9542-f383344edac3 -->

Pruning stops a tree memorising its training data. Trees are easy to interpret and need little data preparation, but they over-fit and have high variance. Many trees together (random forests, boosting) fix most of that.

**Next:** [[machine-learning/03-classical-ml/11-naive-bayes|Naive Bayes]]. KNN used distance and decision trees used questions. Naive Bayes uses probability.

## About this lesson
<!-- bite: 5e918c84-ef8d-48da-97e5-400005ddd3f6 -->

**Level:** Intermediate. **Covers:** pre-pruning and post-pruning, advantages, disadvantages and applications of decision trees, random forests and gradient boosting. Part 6 of 6 on decision trees. The ensembles part comes from the roadmap.sh machine-learning roadmap, not the class notes. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
