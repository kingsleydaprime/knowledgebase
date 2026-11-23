---
id: 7d2becbe-6623-43a7-a00e-0fcfaeda496f
---

# Naive Bayes Classifiers

Naive Bayes predicts a class using probability.

## Before you start
<!-- bite: bd228c71-9f6e-4173-9efb-aad57e8b2d9c -->

You should know what a probability is and have met Bayes theorem ([[machine-learning/03-classical-ml/12-bayesian-networks-1|Bayesian Networks 1]] derives it, or see the [[machine-learning/00-foundations/03-mathematics/03-probability-and-statistics/03-bayes-theorem|Bayes theorem]] maths lesson).

After this lesson you will be able to:

- say why naive Bayes models are so fast;
- choose between GaussianNB, BernoulliNB and MultinomialNB for a dataset;
- explain the "naive" assumption and its cost.

## What naive Bayes is
<!-- bite: e51bedca-eef1-44cb-86fa-d5cef5315d72 -->

Naive Bayes classifiers predict a class using probability. KNN used distance and decision trees used questions; naive Bayes looks at each feature on its own and collects simple statistics for each class.

Next: why naive Bayes is so fast, then its three kinds.

## Why naive Bayes is fast
<!-- bite: 9339db7f-12f7-435d-8484-06bf1ed76f23 -->

The reason that naive Bayes models are efficient is that they learn parameters by looking at each feature individually and collect simple per-class statistics from each feature.

## The three naive Bayes classifiers
<!-- bite: 7cbec1c3-99cd-498b-ad60-310dbb2b3cdd -->

There are three kinds of naive Bayes classifiers implemented in scikit-learn: **GaussianNB**, **BernoulliNB** and **MultinomialNB**.

| Classifier | What it assumes | What it stores or is used for |
| --- | --- | --- |
| **GaussianNB** | Can be applied to any continuous data | Stores the average value as well as the standard deviation of each feature for each class |
| **BernoulliNB** | Assumes binary data | Mostly used in text data classification |
| **MultinomialNB** | Assumes count data (that is, each feature represents an integer count of something, like how often a word appears in a sentence) | Takes into account the average value of each feature for the class. Mostly used in text data classification |

The naive Bayes models share many strengths and weaknesses of the linear models. They are very fast to train and predict.

## The naive assumption, and when to use it
<!-- bite: 33fab239-45f7-436a-84e7-8e7eda1e4676 -->

Applies [[machine-learning/00-foundations/03-mathematics/03-probability-and-statistics/03-bayes-theorem|Bayes' theorem]] with a "naive" assumption: that all features are independent given the class. That assumption is almost always false, yet the model works surprisingly well anyway — especially for **text classification** (spam filtering, sentiment):

```python
from sklearn.naive_bayes import MultinomialNB
MultinomialNB().fit(X_train, y_train)   # great for word-count / TF-IDF text features
```

Extremely fast to train and predict, works with little data, and a strong baseline for text. Its probability estimates are poorly calibrated (the independence assumption), so trust the *ranking* more than the exact probabilities.

## Check your understanding
<!-- bite: 35e1a9fa-e459-4c05-8793-5d8be775d2b2 -->

Try each one before you open the answer.

1. Your features are word counts in emails (how often each word appears). Which naive Bayes classifier fits?

   <details><summary>Answer</summary>

   MultinomialNB, because it assumes count data.

   </details>

2. Your features are heights and weights in centimetres and kilograms. Which one fits?

   <details><summary>Answer</summary>

   GaussianNB, because it can be applied to any continuous data.

   </details>

3. What is "naive" about naive Bayes?

   <details><summary>Answer</summary>

   It assumes every feature is independent of the others once we know the class. That is almost never fully true, yet the model still works well, especially for text.

   </details>

## Before moving on
<!-- bite: e489fc59-53e0-4004-a62e-faadcb69c7fa -->

Naive Bayes learns per-class statistics from each feature on its own, which makes it very fast to train and predict. GaussianNB is for continuous data, BernoulliNB for binary data and MultinomialNB for counts.

**Next:** [[machine-learning/03-classical-ml/12-bayesian-networks-1|Bayesian Networks 1]]. Naive Bayes treats features as unconnected. A Bayesian network goes further and shows how the variables are connected to each other.

## About this lesson
<!-- bite: a3a71c10-1d13-47cb-9e53-b4b8262ed090 -->

**Level:** Intermediate. **Covers:** why naive Bayes is efficient, the three scikit-learn naive Bayes classifiers, and the independence assumption. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
