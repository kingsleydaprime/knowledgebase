---
id: 1d2a8899-e981-4339-9942-02ab0fc14076
---

# Dimensionality Reduction with PCA

PCA shrinks data with many columns down to a few that keep most of the information.

## Before you start
<!-- bite: 23900c06-725c-49c8-a2e9-5885e053ddf0 -->

You should know what features are ([[machine-learning/01-foundations-of-ml/01-what-is-ml-and-types|What ML Is]]). The maths behind PCA uses [[machine-learning/00-foundations/03-mathematics/01-linear-algebra/index|linear algebra]], but you can use it without that.

After this lesson you will be able to:

- say what PCA does and three reasons to reduce dimensions;
- run PCA in scikit-learn;
- explain what is lost when you use principal components.

## What PCA is
<!-- bite: edcfe4cc-5033-4ab1-b98b-701f23df48a0 -->

PCA (principal component analysis) is a way of shrinking data with many columns down to a few that still keep most of the information. It is unsupervised, like clustering: no labels are needed.

Next: how PCA works, then why you would use it.

## PCA — dimensionality reduction
<!-- bite: c6b13f10-f877-431a-a16a-1f97b1c3b132 -->

**Principal Component Analysis** compresses many features into fewer, keeping as much of the variation as possible. It finds the directions (principal components) along which the data varies most — mathematically, the [[machine-learning/00-foundations/03-mathematics/01-linear-algebra/index|eigenvectors]] of the data's covariance — and projects the data onto the top few:

```python
from sklearn.decomposition import PCA
X_reduced = PCA(n_components=2).fit_transform(X)   # e.g. 100 features → 2, for plotting
```

## Why reduce dimensions
<!-- bite: 0f227db0-f2f0-4d3f-89a5-dc32fa5eb780 -->

There are three main reasons:

- **Visualization** — squash high-dimensional data to 2D/3D to actually see it.
- **Speed & the curse of dimensionality** — fewer features means faster training and less overfitting; many algorithms (like [[machine-learning/03-classical-ml/01-k-nearest-neighbours-1|KNN]]) degrade badly in high dimensions.
- **Denoising** — dropping low-variance components discards noise.

The cost: the new components are **linear combinations** of original features, so interpretability is lost (a component isn't "age" anymore, it's a blend). For non-linear structure, **t-SNE** and **UMAP** are the go-to visualization alternatives (great for seeing clusters, but for plotting only, not as features).

## Where these fit
<!-- bite: 577d40a8-5851-4b56-b400-ec0770582481 -->

Unsupervised methods are often a *step* in a pipeline rather than the end: cluster to create segment labels, or PCA to compress features before feeding a supervised model. They're also central to the [[data-science/index|Data Scientist]] path's exploratory analysis. And the "compress to a meaningful lower-dimensional representation" idea reappears, learned rather than linear, in [[machine-learning/08-other-architectures/01-autoencoders-and-gans|autoencoders]] and in [[ai-engineering/06-rag-and-embeddings/index|embeddings]].

## Check your understanding
<!-- bite: 3a1174cf-3603-47f7-9639-0c3ea3a61165 -->

Try each one before you open the answer.

1. Give two reasons to reduce 100 features to 2.

   <details><summary>Answer</summary>

   Any two of: to plot and actually see the data, to train faster and over-fit less, to remove noise.

   </details>

2. Why is a principal component harder to explain than an original feature?

   <details><summary>Answer</summary>

   It is a blend (a linear combination) of the original features, so it is no longer just "age" or "income".

   </details>

## Before moving on
<!-- bite: e85c6b8b-c8c0-4e4e-9118-bf7bed311eab -->

PCA projects the data onto the few directions where it varies most. It helps plotting, speed and noise, at the cost of interpretability.

**Next:** [[machine-learning/03-classical-ml/19-inductive-logic-programming|Inductive Logic Programming]]. So far every model learned from numbers in tables. ILP learns rules instead.

## About this lesson
<!-- bite: 846aba36-cbdc-4c20-ac00-5d9db8a8f6ae -->

**Level:** Intermediate. **Covers:** PCA and where unsupervised methods fit in a pipeline. This part was not in the SSG 535 notes; it comes from the roadmap.sh machine-learning roadmap.
