---
id: 810bdab8-7464-4cdd-9b83-de095e22bdcf
---

# Distance Measures

KNN, clustering and LVQ all depend on one idea: how close are two points? A **distance measure** gives that closeness as a number. Smaller means more alike. Let p and q be two points, each with n features.

## Before you start
<!-- bite: c14b1766-c8df-46bd-90c8-c35cbce35cdd -->

You should know how KNN works ([[machine-learning/03-classical-ml/01-k-nearest-neighbours-1|K-Nearest Neighbours 1]]). The only maths is squaring, square roots and absolute values.

After this lesson you will be able to:

- calculate Euclidean and Manhattan distance by hand;
- say how Minkowski distance includes both, and when to use Hamming distance;
- explain why features must be scaled before measuring distance.

## The four distance measures
<!-- bite: d24d31e4-dbc0-4876-857e-188585e49daa -->

**Euclidean distance** is the straight-line distance, the one we normally think of:

$$
d(p, q) = \sqrt{\sum_{i=1}^{n} (p_i - q_i)^2}
$$

**Manhattan distance** adds up the differences along each feature, like walking along city blocks:

$$
d(p, q) = \sum_{i=1}^{n} |p_i - q_i|
$$

**Minkowski distance** is a general form. When r = 1 it becomes Manhattan, and when r = 2 it becomes Euclidean:

$$
d(p, q) = \left( \sum_{i=1}^{n} |p_i - q_i|^r \right)^{1/r}
$$

**Hamming distance** is for categories. It counts the number of features where the two points are different.

## Worked example
<!-- bite: 0d004b99-0d89-4b84-a613-5fd5f4f863ca -->

**Worked example.** Let p = (1, 2) and q = (4, 6).

$$
d_{Euclidean} = \sqrt{(4-1)^2 + (6-2)^2} = \sqrt{9 + 16} = \sqrt{25} = 5
$$

$$
d_{Manhattan} = |4-1| + |6-2| = 3 + 4 = 7
$$

Distances only make sense when the features are on a similar scale, which is why scaling (see [[machine-learning/02-working-with-data/02-feature-engineering-and-scaling|feature scaling]]) matters so much for these methods.

## Check your understanding
<!-- bite: a4f4fd3c-d630-4a0c-a5d7-ea8321add602 -->

Try each one before you open the answer.

1. Find the Euclidean and Manhattan distance between p = (2, 1) and q = (5, 5).

   <details><summary>Answer</summary>

   Euclidean: √((5−2)² + (5−1)²) = √(9 + 16) = 5. Manhattan: |5−2| + |5−1| = 3 + 4 = 7.

   </details>

2. What is the Hamming distance between (Red, Small, Round) and (Red, Large, Square)?

   <details><summary>Answer</summary>

   2, because the two points differ on two features (size and shape).

   </details>

3. Minkowski distance with r = 2 is which distance?

   <details><summary>Answer</summary>

   Euclidean distance. With r = 1 it is Manhattan.

   </details>

## Before moving on
<!-- bite: 3a073940-d19c-4037-9b38-d3a1aa7e3786 -->

A distance measure turns "how alike are these two points?" into a number. Euclidean is the straight line, Manhattan adds up the differences, Minkowski is the general form and Hamming counts differences between categories.

**Next:** [[machine-learning/03-classical-ml/04-learning-vector-quantization|Learning Vector Quantization]]. KNN measures distance to every stored point. LVQ uses the same distances but keeps only a few points.

## About this lesson
<!-- bite: 4a959887-400d-4880-8b35-e2c81cf4c808 -->

**Level:** Beginner. **Covers:** Euclidean, Manhattan, Minkowski and Hamming distance, with a worked example. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
