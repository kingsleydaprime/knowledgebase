---
id: 0bf37d32-1718-4457-aa0d-39e5b9101ce9
---

# K-Nearest Neighbours 2: Regression and Instance-Based Learning

KNN regression predicts a number by averaging the K closest training examples.

## Before you start
<!-- bite: ef2bace4-b5b4-4e8a-a25e-aaa34e1b652d -->

Read [[machine-learning/03-classical-ml/01-k-nearest-neighbours-1|K-Nearest Neighbours 1]] first.

After this lesson you will be able to:

- predict a number with KNN regression and say what the R² score means;
- explain instance-based (lazy) learning and how it differs from building a model;
- list its advantages and disadvantages, especially on large datasets.

## What KNN regression is
<!-- bite: 7bed4915-59a4-494b-8d53-a11b96865ca3 -->

K-neighbours regression predicts a number by averaging the outcomes of the K closest training examples. It is the same KNN from part 1, except the neighbours are averaged instead of voting.

Next: KNN regression in more detail, then the bigger idea behind KNN, instance-based learning.

## K-Neighbors Regression
<!-- bite: 69426826-9fd5-4d40-956a-886a03756ed4 -->

So far we used KNN for classification. There is also a regression variant of the k-nearest neighbors algorithm. This is a non-parametric, instance-based machine learning algorithm that predicts continuous target values by averaging the outcomes of the K closest training examples in the feature space.

> **Note:** When using multiple nearest neighbors, the prediction is the average, or mean, of the relevant neighbors.

It uses distance metrics, commonly Euclidean distance, to determine proximity. It is effective for complex, non-linear data without making underlying distribution assumptions.

## The R² score
<!-- bite: 8abd8935-2259-4bfd-89bd-fe11e0e072bb -->

We can also evaluate the model using the score method, which for regressors returns the **R² score**. The R² score, also known as the **coefficient of determination**, is a measure of goodness of a prediction for a regression model, and yields a score between 0 and 1. A value of 1 corresponds to a perfect prediction and a value of 0 corresponds to a constant model that just predicts the mean of the training set responses. (It can even go below 0 when the model does worse than that constant guess.)

## Strengths, Weaknesses and Parameters of KNN
<!-- bite: f839a4bc-f6f0-47d5-aeea-661b17796fff -->

Two important parameters to the KNeighbors classifiers:

- The number of neighbours
- How you measure distance between points

Strengths and weaknesses:

- It is very easy to understand, often gives reasonable performance without a lot of adjustments.
- It is very fast, but when the training set is very large (meaning a large number of features or samples) prediction can be slow.

> **Note:** A sparse dataset is a dataset in which most features are 0 most of the time.

## Instance-Based Learning
<!-- bite: efdfddbc-1579-457b-9af9-345abaacb9fc -->

KNN is one example of a bigger idea called instance-based learning. Instance-based learning, also known as **memory-based learning** or **lazy learning**, is a type of machine learning where the algorithm stores instances of training data and uses them to make predictions on new data. Instead of explicitly creating a model during the training phase, instance-based learning methods delay the generalization process until a query is made during the prediction phase.

## Key characteristics of instance-based learning
<!-- bite: fad4364f-1071-4b7b-95ae-6e369691e847 -->

- **Lazy learning:** No explicit model is built during training. The algorithm simply stores the training instances. Generalization occurs at the time of prediction.
- **Similarity-based:** Predictions are made based on the similarity between the new data instance and stored training instances. Common similarity measures include Euclidean distance, Manhattan distance, cosine similarity.
- **Local decision making:** Decisions are made based on the local neighbourhood of the input instance. The algorithm considers only a subset of the training data (e.g. k-nearest neighbours) to make a prediction.

## How instance-based learning works
<!-- bite: eca69ad0-f3dd-44fd-81e1-399203eeb3bf -->

1. Store all training data (instances)
2. When a new query instance arrives:
   - compute distance/similarities to the stored instances
   - select the nearest neighbours
3. Predict output using the neighbours (vote or average)

## Advantages of instance-based learning
<!-- bite: d8cdec6c-0502-4a52-ba27-dab1ddc40447 -->

- It is easy to implement and understand
- It does not need a complex model training phase
- It can adapt quickly to new data without retraining the entire model
- It is useful for applications where the data distribution changes over time
- It is effective for problems where the decision boundary is irregular and cannot be easily captured by a global model

## Disadvantages of instance-based learning
<!-- bite: 4a8ad553-a10f-4857-8f4f-bb993b01b68b -->

- It has high storage requirements since all training instances are retained
- Prediction can be slow for large datasets due to the need to compute distances to all stored instances
- It can be sensitive to noisy data, as outliers can affect the prediction
- Its performance depends on the proper scaling of features, as different scales can distort distance calculations

## Choosing K, and why too many features hurt
<!-- bite: 42ba8cfb-2b50-424b-8750-60088c72e759 -->

The laziest algorithm, and the most intuitive: to classify a new point, find its `k` nearest points in the training data and take the majority vote (or average, for regression). There's **no training** — it just stores the data and does all the work at prediction time.

```python
from sklearn.neighbors import KNeighborsClassifier
KNeighborsClassifier(n_neighbors=5).fit(X_train, y_train)
```

- Simple, no assumptions about the data's shape, naturally handles multi-class.
- **Prediction is slow** (must compare to all training points) and it degrades in high dimensions (the "curse of dimensionality" — distances become meaningless when there are many features). Needs scaling, since it's distance-based.
- `k` is the key hyperparameter: small `k` overfits (noisy), large `k` oversmooths.

The *idea* — "similar inputs have similar outputs, measured by distance" — is exactly the intuition behind [[ai-engineering/06-rag-and-embeddings/index|semantic search over embeddings]], which is essentially KNN in a learned vector space.

## Check your understanding
<!-- bite: 31048c75-e589-497f-bbb3-00b08d30851e -->

Try each one before you open the answer.

1. <!-- q: exact id="8e2636d9" answer="120" accept="120 thousand|120000|120,000" -->
   K = 3 regression. The three nearest houses sold for 100, 120 and 140 (thousand). What is the prediction, in thousands?

   <details><summary>Answer</summary>

   The average: (100 + 120 + 140) / 3 = 120 thousand.

   </details>

2. <!-- q: mcq id="ce5a7c9d" -->
   An R² of 0 on the test set means what?

   - [ ] A perfect prediction
   - [x] The model is no better than always predicting the mean of the training responses
   - [ ] The model got every prediction wrong

   <details><summary>Answer</summary>

   The model is no better than a constant model that always predicts the mean of the training set responses. An R² of 1 is a perfect prediction.

   </details>

3. <!-- q: mcq id="2d83e0cb" -->
   K is the key hyperparameter. What happens when K is very small?

   - [x] The model overfits and is noisy
   - [ ] The model oversmooths
   - [ ] Nothing, K doesn't matter

   <details><summary>Answer</summary>

   Small K overfits (noisy). Large K oversmooths.

   </details>

4. <!-- q: gap id="d1f03417" answers="memory-based|memory based;lazy" -->
   Fill in the gaps. Instance-based learning is also known as ___ learning or ___ learning.

   <details><summary>Answer</summary>

   Memory-based, then lazy. The algorithm stores the training instances and delays generalization until a query is made.

   </details>

5. <!-- q: open id="bd3d3374" -->
   A shop has 10 million customers. Name two problems KNN will have, and say why.

   <details><summary>Answer</summary>

   High storage, because all training instances are kept. Slow predictions, because every prediction computes the distance to all stored instances. (Also: it needs scaled features and is hurt by noisy data.)

   </details>

## Before moving on
<!-- bite: 23628932-cdda-4a16-9f03-a23f2f1c81ae -->

KNN regression averages the K nearest outputs and is scored with R². KNN is one example of instance-based learning: store the data, delay the work until a query arrives.

**Next:** [[machine-learning/03-classical-ml/03-distance-measures|Distance Measures]]. Every step of KNN said "closest". Next we see exactly how that closeness is measured.

## About this lesson
<!-- bite: 67e826f3-6b3e-4e75-af93-de3d68056478 -->

**Level:** Beginner. **Covers:** K-neighbours regression, the R² score, strengths and parameters of KNN, and instance-based learning. Part 2 of 2 on KNN; past question 4(a) in the [[machine-learning/ssg-535-question-bank|SSG 535 question bank]] is on this lesson. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
