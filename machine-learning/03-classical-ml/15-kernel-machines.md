---
id: 1a468ea4-9343-4012-b991-5e1dee4b6711
---

# Kernel Machines and Support Vector Machines

Kernel machines let linear models solve problems a straight line can't.

## Before you start
<!-- bite: b939c4db-d7c9-448a-a70a-25ebbe70b311 -->

You should know what a linear classifier is and why it fails on tangled data ([[machine-learning/03-classical-ml/14-linear-models-and-regression|Linear Models and Regression]]).

After this lesson you will be able to:

- explain the kernel trick in plain words;
- name four common kernels and what each is good for;
- weigh a kernel SVM against a linear classifier for a given dataset.

## What kernel machines are
<!-- bite: 6cfaf886-fe47-4d6d-a3f2-92af4fcaf9f0 -->

Kernel Machines are a class of algorithms for pattern analysis, whose best known member is the **Support-Vector Machine (SVM)**. It uses a mathematical function called a **kernel function**, to process data in an implicit, high-dimensional feature space without explicitly calculating the transformed coordinates. This approach, known as the **kernel trick**, enables linear models to solve complex, non-linear problems efficiently.

Some problems cannot be solved well by simple linear models, because the data cannot be separated by a straight line. Kernel machines are one way to solve this.

Next: what a kernel function computes, then the kernel trick.

## What a kernel function computes
<!-- bite: 0b0b212b-5a2e-4da9-bab1-1b46fc07fa4a -->

Mathematically, a kernel function K(x,y) computes an inner product in a transformed space:

$$
K(x, y) = \phi(x) \cdot \phi(y)
$$

where φ(x) is a transformation that maps input data into a higher-dimensional space.

Kernel methods are especially useful in classification and regression problems where traditional linear models fail. They enable algorithms like Support Vector Machines (SVMs) and Kernel Ridge Regression to capture nonlinear relationships without explicitly performing complex transformations.

## Kernel Trick
<!-- bite: 6512906a-6165-44cb-a310-806055f651e0 -->

The kernel trick is a mathematical technique that allows machine learning models to operate in higher-dimensional spaces without explicitly computing the transformation. Instead of performing expensive feature mapping, the kernel trick directly computes the similarity between data points in the transformed space using kernel functions.

For example, instead of manually transforming two-dimensional data into three-dimensional space, a kernel function calculates the transformed dot product directly. This avoids computational complexity and enables algorithms to work with large datasets efficiently.

Common kernel functions include:

| Kernel | What it is good for |
| --- | --- |
| **Linear Kernel** | Suitable for simple, linearly separable data |
| **Polynomial Kernel** | Captures complex decision boundaries |
| **Radial Basis Function (RBF) Kernel** | Highly effective for nonlinear problems |
| **Sigmoid Kernel** | Neural networks, mimicking the behaviours of activation functions |

## Kernel Methods in Support Vector Machine (SVM)
<!-- bite: 05ca459a-cd5a-440d-b811-eb78786934c4 -->

Support Vector Machines (SVMs) are powerful classification algorithms that separate data points using the optimal hyperplanes. However, when data is not linearly separable, SVMs rely on a kernel function to transform the input space into a higher-dimensional representation where a clear separation exists.

By applying kernel methods, SVMs can efficiently classify complex, nonlinear patterns. The Radial Basis Function (RBF) kernel is the most commonly used because it captures intricate decision boundaries. Polynomial kernels work well when the relationship between features follows a polynomial function.

**Example of kernelized SVM in action:** In handwritten digit recognition, linear SVMs struggle to classify digits due to their complex shapes. By applying an RBF kernel, the SVM effectively differentiates digits by mapping them into a higher-dimensional space where separation becomes possible.

SVMs with kernel functions are widely used in image classification, bioinformatics and text analysis where data is high-dimensional and complex.

## Kernel Ridge Regression: A Regularized Approach
<!-- bite: 0aa3cabe-c684-41e0-9417-63863d0d5782 -->

Kernel Ridge Regression (KRR) extends linear regression by incorporating kernel methods to handle nonlinear relationships in data. Unlike standard regression, which assumes a direct linear relationship between inputs and outputs, KRR transforms the feature space using kernels to model complex functions.

## Applications of Kernel Methods
<!-- bite: 679b0f5d-4224-4255-99d9-c27d9319184b -->

Kernel methods are widely used across various domains due to their ability to handle complex, nonlinear patterns in high-dimensional spaces.

- **Image Classification & Face Recognition:** Support Vector Machine (SVM) with RBF and polynomial kernels are used in facial recognition systems, enabling accurate identity verification.
- **Bioinformatics & Genomic Data Analysis:** Kernel methods help analyze DNA sequences and protein structures, where traditional linear models fail to capture intricate patterns.
- **Text Classification & NLP:** SVMs with kernels are essential for spam filtering, sentiment analysis, and document categorization, as they efficiently process high-dimensional textual data.

## Support vector machines in scikit-learn
<!-- bite: e11fd089-9e1c-4b08-b5d4-9ca67fc59021 -->

An SVM finds the decision boundary that **maximizes the margin** — the widest possible gap between the two classes. The points sitting on the edge of that gap (the "support vectors") are the only ones that matter; the rest don't affect the boundary.

Its superpower is the **kernel trick**: by implicitly mapping data into a higher-dimensional space, an SVM can find a linear boundary there that corresponds to a complex non-linear boundary in the original space — without ever computing the high-dimensional coordinates.

```python
from sklearn.svm import SVC
SVC(kernel="rbf", C=1.0).fit(X_train, y_train)   # rbf = the common non-linear kernel
```

Strong on **small-to-medium datasets with clear margins** and high-dimensional data (text classification historically). The catch: **doesn't scale** to very large datasets (training is roughly quadratic), needs feature scaling, and the kernel/`C`/`gamma` choices need tuning. Largely superseded by gradient boosting for tabular and by deep learning for text/images, but conceptually important and still useful on the right small problem.

## Choosing between SVM, KNN and naive Bayes
<!-- bite: beb3e8cf-9414-4b9b-bd30-42f274a7a78b -->

| Algorithm | Shines when | Avoid when |
|---|---|---|
| **SVM** | small/medium data, clear margins, high-dim | large datasets |
| **KNN** | small data, low dimensions, simple baseline | large data, many features |
| **Naive Bayes** | text, high-dim sparse features, tiny data | features are strongly dependent and you need calibrated probabilities |

All three are worth recognizing, but for most tabular problems [[machine-learning/03-classical-ml/10-decision-trees-6|gradient boosting]] will beat them — these earn their place on specific data shapes (SVM on clean small margins, Naive Bayes on text, KNN as a dead-simple baseline).

## Check your understanding
<!-- bite: 6e9a3f8f-6ce4-4fe5-98d7-c10cf9015b2d -->

Try each one before you open the answer.

1. In one sentence, what does the kernel trick avoid?

   <details><summary>Answer</summary>

   It avoids calculating the transformed, high-dimensional coordinates. The kernel computes the similarity (the dot product) in that space directly.

   </details>

2. Which kernel is the most commonly used for non-linear problems?

   <details><summary>Answer</summary>

   The Radial Basis Function (RBF) kernel.

   </details>

3. You have 5 million rows and need a model you can explain to a manager. Kernel SVM or linear classifier?

   <details><summary>Answer</summary>

   Start with the linear classifier. Kernel SVMs are slow on very large datasets and hard to explain. Move to a kernel only if the linear model performs badly.

   </details>

## Practice — independent task
<!-- bite: aab09a01-40bc-4192-9d2d-b018d55d0184 -->

Past question 4(b) in the [[machine-learning/ssg-535-question-bank|SSG 535 question bank]] asks you to compare a linear classifier with a kernel SVM on complex non-linear data, covering computational complexity, overfitting, interpretability and scalability. **Done when** you have one advantage and one limitation for each of those four headings and a conclusion. Then check the solution.

## Before moving on
<!-- bite: 2040fb04-ca94-434f-b10f-98771aaddc9a -->

A kernel function computes a dot product in a higher-dimensional space without going there. That lets SVMs and kernel ridge regression capture non-linear patterns. RBF is the common default.

**Next:** [[machine-learning/03-classical-ml/16-clustering-1|Clustering 1]]. Everything so far was supervised. Now we go back to unsupervised learning, where there are no labels at all.

## About this lesson
<!-- bite: 9b09ca58-6d9f-46f4-be3a-d39bdee73450 -->

**Level:** Intermediate. **Covers:** kernel functions, the kernel trick, common kernels, kernel SVMs, kernel ridge regression and applications. The scikit-learn SVM part comes from the roadmap.sh machine-learning roadmap. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
