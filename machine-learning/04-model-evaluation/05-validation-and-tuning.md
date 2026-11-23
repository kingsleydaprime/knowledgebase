---
id: 7632d626-7ddf-4321-8bda-2f655f8709ff
---

# Validation and Tuning

Cross-validation tests a model on several splits of the data, not just one.

## Before you start
<!-- bite: 9b9de903-5d62-43b3-aaee-ec8e94946d07 -->

You should know what a train/test split is and what over-fitting looks like ([[machine-learning/04-model-evaluation/04-overfitting-and-regularization|Overfitting]]).

After this lesson you will be able to:

- explain five-fold cross-validation with the table of folds;
- give the benefits and the cost of cross-validation, and name its variants;
- tune a model's settings without peeking at the test set.

## What cross-validation and tuning are
<!-- bite: 7a6d892b-74e6-404d-a8b6-89f822dfba8b -->

Cross-validation is a statistical method of evaluating generalization performance that is more stable and thorough than using a split into a training and a test set. Tuning is trying different settings of a model to find the ones that work best.

Next: what goes wrong with a single train/test split.

## The problem with a single train/test split
<!-- bite: 521c4fcd-82f0-4099-b9ff-ed9a3c5b8389 -->

A single [[machine-learning/02-working-with-data/03-train-val-test-splits|train/test split]] gives one estimate of performance — and that estimate is noisy. You might have gotten a lucky (or unlucky) test set. Worse, if you tune your model against the test set repeatedly, you start *overfitting to the test set itself*, and your reported number stops meaning anything.

## Cross-validation
<!-- bite: d761afb8-0af6-48af-96ce-eade68f3a1fa -->

Cross-validation is a statistical method of evaluating generalization performance that is more stable and thorough than using a split into a training and a test set. In cross-validation, the data is split repeatedly and multiple models are trained. The most commonly used version of cross-validation is **K-fold cross-validation**, where K is a user-specified number, usually 5 or 10. When performing five-fold cross-validation, the data is first partitioned into five parts of (approximately) equal size called **folds**.

## K-fold cross-validation step by step
<!-- bite: 93387baf-a5c8-4a80-b3c8-d6038f561ef0 -->

Next, a sequence of models is trained. The first model is trained using the first fold as the test set, and the remaining folds (2-5) are used as the training set. The model is built using the data on folds 2-5, and then the accuracy is evaluated on fold 1. Then another model is built, this time using fold 2 as the test set and the data in folds 1, 3, 4, and 5 as the training set. The process is repeated using folds 3, 4, and 5 as test sets. For each of these five splits of the data into training and test sets, we compute the accuracy. In the end, we have collected five accuracy values.

| Split | Fold 1 | Fold 2 | Fold 3 | Fold 4 | Fold 5 |
| --- | --- | --- | --- | --- | --- |
| Split 1 | **Test** | Train | Train | Train | Train |
| Split 2 | Train | **Test** | Train | Train | Train |
| Split 3 | Train | Train | **Test** | Train | Train |
| Split 4 | Train | Train | Train | **Test** | Train |
| Split 5 | Train | Train | Train | Train | **Test** |

*Data splitting in five-fold cross-validation.*

## Benefits of Cross-Validation
<!-- bite: 0d193771-7b47-4260-9ffe-0511dbc7430c -->

- **It reduces randomness bias**
  - A single train-test split may be "lucky" or "unlucky"
  - Cross-validation ensures every sample is used for both training and testing
  - It provides a more reliable estimate of model performance
- **It is a more efficient use of data**
  - More training data usually improves model accuracy
  - A single split (e.g. 75/25) uses less data for training. Note that 5-fold CV uses 80% of data for training each time. 10-fold CV uses 90% of data for training
## More benefits of cross-validation
<!-- bite: cb062c78-e0f3-43ca-a099-8949a5bee167 -->

- **It is a better generalization assessment**
  - Each example is used as a test case exactly once
  - The model must perform well across all folds to achieve a high average score
- **It gives performance variability insight**
  - It shows the range of accuracy scores (e.g. 90%-100%)
  - It helps understand best-case and worst-case performance scenarios
  - It indicates how sensitive the model is to different training sets

## Disadvantage of Cross-Validation
<!-- bite: 40cb10e2-8a1f-4c0b-950a-66f25cca4c78 -->

- It has a higher computation cost
  - It trains the model K times
  - It is approximately K times slower than a single split

> **Note:** Cross-validation does not produce a final model. It is used only to evaluate how well a model is expected to generalize. After cross-validation, you must still train a final model on the full dataset.

## Techniques of Cross-Validation
<!-- bite: d33f1c64-7556-4ac8-ac85-43facf13f117 -->

- **Stratified K-Fold:** A K-fold variation ensuring each fold maintains class proportions, ideal for imbalanced datasets.
- **Leave-one-Out Cross Validation:** Exhaustive method where p (here, one) observation is used for validation, offering low bias but high computational cost.
- **Shuffle-Split Cross Validation:** It is a very flexible strategy for cross validation. This is a technique that generates a user-defined number of independent, random training and testing dataset splits (it randomly splits data into train and validation set multiple times).
- **Stratified ShuffleSplit:** It gives more reliable results for classification tasks.
- **Group K-Fold Cross Validation:** It ensures that data from specific groups (e.g. patients) are not split across train/test sets.

## Cross-validation in scikit-learn
<!-- bite: 60e092e7-1492-4c33-a1da-bd11235fc1ef -->

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5)   # 5-fold
scores.mean(), scores.std()                    # estimate AND its stability
```

- **Stratified k-fold** preserves class proportions in each fold — essential for imbalanced classification.
- **LOOCV** (leave-one-out) is k-fold taken to the extreme (`k` = number of points) — nearly unbiased but expensive and high-variance; rarely worth it over 5- or 10-fold.
- **Time-series data breaks ordinary CV** — you can't validate on the past using a model trained on the future. Use forward-chaining / `TimeSeriesSplit` so validation is always chronologically after training.

The discipline that ties it together: keep a **final test set** completely untouched until the very end. Tune with cross-validation on the training data; touch the test set once, to report the number you'll actually trust.

## Hyperparameter tuning
<!-- bite: c5fc996c-9784-4a52-a7cb-d0ae307e24e1 -->

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
<!-- bite: 6bcdd09e-b2ca-4a22-ab66-51914ffaac77 -->

Choosing *which* model, not just its settings, follows the same logic: compare candidates by cross-validated performance on the training data, then confirm the winner once on the held-out test set. Don't forget the non-accuracy axes — training/inference cost, interpretability ([[machine-learning/09-building-and-fine-tuning/04-explainable-ai|explainability]]), and maintenance — a slightly-less-accurate model that's interpretable and cheap often wins in production.

## Check your understanding
<!-- bite: 465b33b0-6272-460c-bbba-b83cd4927541 -->

Try each one before you open the answer.

1. <!-- q: gap id="d221e660" answers="90%|90|0.9;10|ten" -->
   Fill in the gaps. In 10-fold cross-validation, ___ of the data trains each model, and ___ models are trained.

   <details><summary>Answer</summary>

   90% of the data trains each model, and 10 models are trained.

   </details>

2. <!-- q: mcq id="dc9572c8" -->
   Does cross-validation give you the final model to deploy?

   - [ ] Yes, the best fold's model
   - [x] No, you still train a final model on the full dataset

   <details><summary>Answer</summary>

   No. It only estimates how well a model is expected to generalize. After it, you train a final model on the full dataset.

   </details>

3. <!-- q: mcq id="350864f3" -->
   Your data has 200 patients with several rows each. Which cross-validation keeps one patient's rows out of both train and test at once?

   - [ ] Stratified K-Fold
   - [ ] Leave-one-out
   - [x] Group K-Fold
   - [ ] Shuffle-Split

   <details><summary>Answer</summary>

   Group K-Fold cross-validation.

   </details>

4. <!-- q: mcq id="e52dfcf6" -->
   Which of these are hyperparameters, set before training? Choose all that apply.

   - [x] A tree's `max_depth`
   - [x] `k` in KNN
   - [x] A boosting `learning_rate`
   - [ ] The weights learned by linear regression

   <details><summary>Answer</summary>

   The first three. The weights are parameters: they are learned during training.

   </details>

5. <!-- q: open id="4fc55dfb" -->
   Why must you tune hyperparameters with cross-validation on the training data, and not against the test set?

   <details><summary>Answer</summary>

   If you pick settings by test-set performance, the test set has helped shape the model. It is contaminated, and the final number becomes too optimistic. Tune with cross-validation on the training data, then touch the test set once to report a number you can trust.

   </details>

## Before moving on
<!-- bite: e816fe14-389d-4975-88c0-07823733d068 -->

Cross-validation splits the data repeatedly so every sample is tested once, which gives a steadier score and shows its spread, at K times the cost.

**Next:** [[machine-learning/ssg-535-question-bank|SSG 535 question bank]]. That is the end of the SSG 535 material. Attempt the past paper closed-book.

## Related
<!-- bite: 71661771-2ac7-4e56-a09b-5b3460aad805 -->
- [[machine-learning/04-model-evaluation/01-evaluation-metrics-1|Evaluation Metrics]] — the metrics being cross-validated
- [[machine-learning/04-model-evaluation/04-overfitting-and-regularization|Overfitting & Regularization]] — what honest validation detects
- [[machine-learning/02-working-with-data/03-train-val-test-splits|Train/Val/Test Splits]] — the untouched-test-set discipline

## About this lesson
<!-- bite: 6c695349-96fd-4a69-84da-b57bbea6ee6b -->

**Level:** Intermediate → Advanced. **Covers:** cross-validation and its variants, hyperparameter tuning and model selection. The tuning and model selection parts come from the roadmap.sh machine-learning roadmap. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
