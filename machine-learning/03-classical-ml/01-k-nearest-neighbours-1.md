---
id: 37f13a4d-8388-4ae1-80a5-c47be5b7e1ba
---

# K-Nearest Neighbours 1: Predicting from the Closest Points

KNN predicts from the closest points in the training data.

## Before you start
<!-- bite: 1adc21c7-1c23-40ef-a22b-e6b90d54a635 -->

You should know what supervised learning, classification and features are ([[machine-learning/01-foundations-of-ml/01-what-is-ml-and-types|What ML Is]]).

After this lesson you will be able to:

- explain how KNN makes a prediction, step by step;
- say what K means and what changes when K goes from 1 to 3 or 5;
- build and score a first KNN model on the Iris dataset in scikit-learn.

## What KNN is
<!-- bite: 4e199812-ac7a-4c40-860f-50191c40a438 -->

The KNN algorithm is arguably the simplest machine learning algorithm. To make a prediction for a new data point, the algorithm finds the closest data point in the training dataset.

KNN is our first supervised algorithm. It can do both types of supervised learning we saw earlier, classification and regression.

KNN is a supervised learning algorithm used for classification and regression. It is simple, and often used as baseline model in ML.

> **Note:**
>
> - A datapoint is classified based on the majority class of its K-nearest neighbors
> - K = number of nearest data points considered
> - Uses distance
> - No explicit training phase – lazy learner

## How KNN Works (step by step)
<!-- bite: 54ffbd34-a60f-46df-bdb1-8800e0dca5d4 -->

1. Choose a value for K
2. Calculate the distance between the new point and all training points
3. Select the K closest points

**Classification** → Majority vote. **Regression** → Average value.

## K-Neighbors Classification
<!-- bite: 4258d2f8-5e0d-45b2-819d-5f4e8b1648ed -->

In its simplest version, the KNN algorithm only considers exactly one nearest neighbor, which is the closest training data point to the point we want to make the prediction for. The prediction is then simply the known output for this training point.

## Building my first model
<!-- bite: 75d45fb7-4336-4aec-b594-70b259a1634d -->

> **Note:**
>
> - K-nearest neighbors classifier is easy to understand
> - Building this model only consists of storing the training set
> - To make a prediction for a new data point, the algorithm finds the point on the training set that is closest to the new point, then it assigns the label of the training point to the new data point.
> - The K in K-nearest neighbors signifies that instead of using only the closest neighbor to the new data point, we can consider any fixed number K of neighbors in the training. For example, the closest 3 or 5 neighbors.

All machine learning models in scikit-learn are implemented in their own classes which are called **estimator classes**.

The most important parameter of K-Neighbors Classifier is the number of neighbors, which we will set to 1.

In code, that looks like this:

```python
knn = KNeighborsClassifier(n_neighbors=1)
```

## The Iris dataset
<!-- bite: 00cc89e9-85ce-4f17-a419-c583320a3a82 -->

Our first model learns from the Iris dataset of flowers. Two words first:

- The possible species are called **classes**
- The species of a single iris is called its **label**

The Iris dataset consists of 2 NumPy arrays, one containing the data which is referred to as **X** in scikit-learn, one containing the correct or desired outputs, which is called **y**.

1. **X**: A 2D array of features, with one row per data point and one column per feature.
2. **y**: A one dimensional array which here contains one class label, an integer ranging from 0-2, for each of the samples.

## K-Neighbors Algorithm Using scikit-learn
<!-- bite: 50c1ff28-3960-485b-a2c2-d0fd0e3b1a06 -->

- Split the data into a training and a test set so we can evaluate generalization performance.

> **Note:** **Decision boundary** is the divide between where the algorithm assigns class 0 versus where it assigns class 1.

> **Note:** **Random state** controls the shuffling applied to the data before applying the split.

## Worked example: the whole first model
<!-- bite: c066c3c8-3869-47a1-a980-ddde551e48ef -->

Here is the whole first model in one file. Save it as `knn_iris.py` and run `python3 knn_iris.py` from the folder you saved it in (you need `pip install scikit-learn`).

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

iris = load_iris()                      # a Bunch: iris.data is X, iris.target is y
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, random_state=0)   # random_state fixes the shuffle

knn = KNeighborsClassifier(n_neighbors=1)     # K = 1
knn.fit(X_train, y_train)                     # "training" = storing the training set
print("Test set score:", knn.score(X_test, y_test))
```

The score is the fraction of test flowers it got right. With this split it should be about 0.97. A different `random_state` gives a different split, so the number moves a little.

**Predict before you run it:** change `n_neighbors=1` to `n_neighbors=3`. Will every prediction stay the same? Write your guess down, then run it and compare.

## Check your understanding
<!-- bite: 7fa7563d-7fa1-4962-9f43-103c9c9c81d4 -->

Try each one before you open the answer.

1. K = 3. The three nearest training points to a new flower have the labels setosa, versicolor, versicolor. What does KNN classification predict?

   <details><summary>Answer</summary>

   Versicolor. Classification uses a majority vote, and two of the three neighbours are versicolor.

   </details>

2. Why is KNN called a lazy learner?

   <details><summary>Answer</summary>

   Because it has no explicit training phase. Building the model only consists of storing the training set; all the work (computing distances) happens when we ask for a prediction.

   </details>

3. In the Iris dataset, what are X and y?

   <details><summary>Answer</summary>

   X is a 2D array of features, one row per flower and one column per measurement. y is a one-dimensional array holding the class label (0, 1 or 2) for each flower.

   </details>

## Before moving on
<!-- bite: 195e6d85-e4ce-4ac7-9088-bcc4ddc4ffdd -->

KNN stores the training set. To predict, it measures the distance to every training point, takes the K closest, and votes (classification) or averages (regression).

**Next:** [[machine-learning/03-classical-ml/02-k-nearest-neighbours-2|K-Nearest Neighbours 2]]. We used KNN for classification here. Next is the regression version, and the bigger idea KNN belongs to: instance-based learning.

## About this lesson
<!-- bite: 806ad64a-23f7-4cb1-91c3-90a85f1b6216 -->

**Level:** Beginner. **Covers:** how KNN works, K-neighbours classification, estimator classes in scikit-learn, the Iris dataset, decision boundaries and random state. Part 1 of 2 on KNN. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
