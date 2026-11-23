---
id: 1493d13e-b8fe-45a0-a29d-85294493b9f7
---

# Evaluation Metrics 1: The Confusion Matrix, Accuracy, Precision, Recall and F1

Evaluation is checking how good a model is on data it has not seen.

## Before you start
<!-- bite: be6fb5b3-d8dd-41b8-a615-8cb5f57cd8ba -->

You should know what classification is and why we keep a test set ([[machine-learning/02-working-with-data/03-train-val-test-splits|Train/Val/Test Splits]]).

After this lesson you will be able to:

- fill in a confusion matrix and name TP, TN, FP and FN;
- calculate accuracy, precision, recall and F1-score from it;
- choose between precision and recall from the cost of each mistake.

## What evaluation is
<!-- bite: a22c4640-e431-4dac-9e5c-77afcf0c8f4d -->

Evaluation is the crucial process of assessing a model's performance, accuracy, and generalization capabilities on unseen data using metrics like precision, recall and F1-score. It involves techniques such as cross-validation and holdout methods to prevent overfitting and ensure reliability, ultimately enabling the selection of the best-performing model for deployment.

We have now seen many kinds of models. The next question is: how do we know if a model is any good? That is what evaluation is about. It connects back to generalization, because we want to know how the model does on data it has not seen.

Next: the metrics and methods we use, starting with the confusion matrix.

## Evaluation Metrics and Methods
<!-- bite: 727603fb-126f-4d92-8d96-ca532e59a941 -->

- **Classification metrics:** Accuracy, Precision, Recall, F1-score, and Confusion Matrix.
- **Regression metrics:** Mean Absolute Error (MAE), Mean Squared Error (MSE), Root Mean Squared Error (RMSE), and R².
- **Evaluation techniques:** Holdout method (e.g. 70/30 or 80/20 train-test split) and K-fold Cross Validation.

## Why Evaluation is Essential
<!-- bite: 6d538aef-3908-4e51-9ff4-a242faccd64a -->

- **Performance measurement:** It determines how well the model predicts outcomes.
- **Prevents overfitting:** It ensures the model generalizes to new data rather than just memorizing training data.
- **Bias & fairness detection:** Identifies if the model behaves unfairly across different demographic groups.
- **Model comparison:** It enables comparison between different models to select the best one.

## Evaluation Phases
<!-- bite: 20dab3bc-fcaa-423a-8690-bb75ea01400b -->

- **Offline evaluation:** It is performed during training/experimentation.
- **Online evaluation / monitoring:** It is conducted after deployment to detect issues like data drift.

## Classification Metrics
<!-- bite: 29c6edc4-76bc-4056-bf28-6254288301be -->

Classification problems aim to predict discrete categories. To evaluate the performance of classification models, we use the metrics below. Most of them are built from the confusion matrix, so we start there.

## Confusion Matrix
<!-- bite: 017584a3-5ff2-49e1-8a34-811b208c4cf2 -->

A confusion matrix creates an N×N matrix, where N is the number of classes or categories that can be predicted.

**Example:**

| N = 165 | Predicted No | Predicted Yes |
| --- | --- | --- |
| **Actual No** | 50 | 10 |
| **Actual Yes** | 5 | 100 |

- **True Positive (TP):** It is the case where we predicted Yes and the real output was also Yes.
- **True Negative (TN):** It is the case where we predicted No and the real output was also No.
- **False Positive (FP):** It is the case where we predicted Yes but it is actually No.
- **False Negative (FN):** It is the case where we predicted No but it is actually Yes.

> **Note:** Type I error is a False Positive. Type II error is a False Negative.

## 1. Accuracy
<!-- bite: c706eb8d-4ae4-42b1-97cf-0f398b4e73d1 -->

This is a fundamental metric used for evaluating the performance of classification models. It tells us the proportion of correct predictions made by the model out of all predictions.

$$
Accuracy = \frac{\text{Number of Correct Predictions}}{\text{Total Number of Predictions}}
$$

While accuracy provides a quick snapshot, it can be misleading in cases of imbalanced datasets. For example, in a dataset with 90% of class A and 10% of class B, a model predicting only Class A will still achieve 90% accuracy but it will fail to identify any class B instances.

> **Note:** Accuracy is good but it gives a false sense of achieving high accuracy. The problem arises due to the possibility of misclassification of minor class samples being very high.

## 2. Precision
<!-- bite: 89c43161-5490-4ff8-84db-5534e2e05be4 -->

It measures how many of the positive predictions made by the model are actually correct. It is useful when the cost of false positive is high such as in medical diagnoses where predicting a disease when it is not present can have serious consequences.

$$
Precision = \frac{TP}{TP + FP}
$$

where TP = True Positives and FP = False Positives.

Precision helps ensure that when the model predicts a positive outcome, it is likely to be correct.

## 3. Recall
<!-- bite: 2a59c97b-97b4-4018-9f73-bd67bebe987c -->

Recall or sensitivity measures how many of the actual positive cases were correctly identified by the model. It is important when missing a positive case (false negative) is more costly than false positives.

$$
Recall = \frac{TP}{TP + FN}
$$

where FN = False Negatives.

In scenarios where catching all positive cases is important (like disease detection), recall is a key metric.

## 4. F1-Score
<!-- bite: 0b599b4e-9aaa-4bae-a3d2-40cdc35c5623 -->

The F1 score is the harmonic mean of precision and recall. It is useful when we need a balance between precision and recall as it combines both into a single number. A high F1 score means the model performs well on both metrics. It ranges in \[0, 1\]. Lower recall and higher precision gives us great accuracy but then it misses a large number of instances. The more the F1 score, the better the performance will be.

$$
F1\ Score = 2 \times \frac{Precision \times Recall}{Precision + Recall}
$$

## Why precision/recall tradeoffs matter more than accuracy
<!-- bite: 0663d107-3229-4fd5-9e76-c1e75f5de849 -->

A spam filter and a cancer-screening test have opposite priorities even though both are binary classifiers. A spam filter that occasionally lets spam through (false negative) is a minor annoyance; one that occasionally blocks a legitimate email (false positive) can be a real problem — so precision matters more there. A cancer screen that misses an actual case (false negative) is far worse than one that flags a healthy patient for further (more expensive, more precise) testing (false positive) — so recall matters more there. Picking the right metric means understanding which error type is actually more costly for the specific problem, not defaulting to whichever number looks best.

## The same metrics in scikit-learn
<!-- bite: 266b52b9-2641-4312-ac79-67dfd88ec2ed -->

For a binary classifier, every prediction falls into one of four buckets:

```text
                  Actual: Positive    Actual: Negative
Predicted: Positive    True Positive (TP)    False Positive (FP)
Predicted: Negative    False Negative (FN)    True Negative (TN)
```

- **Accuracy** = (TP + TN) / total — the fraction of predictions that were correct. Misleading on imbalanced data: a model that always predicts "no fraud" on a dataset that's 99% non-fraud gets 99% accuracy while being completely useless.
- **Precision** = TP / (TP + FP) — of everything predicted positive, how much actually was? High precision means few false alarms.
- **Recall** = TP / (TP + FN) — of everything that actually was positive, how much did the model catch? High recall means few missed cases.
- **F1 score** — the harmonic mean of precision and recall, a single number balancing both when neither can be prioritized in isolation.

## The four metrics in code
<!-- bite: e34095f7-525d-4796-8dd3-49dd046eb50b -->

scikit-learn has a function for each of the four metrics.

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
accuracy_score(y_true, y_pred)
precision_score(y_true, y_pred)
recall_score(y_true, y_pred)
f1_score(y_true, y_pred)
```

## Confusion matrices with more than two classes
<!-- bite: c56f3e65-a6e2-4008-ba2f-c5e0fd0feba8 -->

A confusion matrix lays out every combination of predicted vs. actual class as a grid, for problems with more than two classes as well as binary ones — it shows *which* classes get confused with which, information a single accuracy number discards entirely. Worth generating routinely, not just when something looks wrong.

```python
from sklearn.metrics import confusion_matrix
confusion_matrix(y_true, y_pred)
```

## Gotchas
<!-- bite: 59f22aa6-6cee-4d04-9518-8ca2f208b45d -->

- Always compute metrics on the **validation/test set** (see [[03-train-val-test-splits|train-val-test-splits]]), never on training data — training-set metrics measure memorization, not generalization.
- On imbalanced classification data, accuracy alone can be actively misleading (the "always predict the majority class" trap above) — precision, recall, and F1 (or their per-class breakdowns) tell a much more honest story.
- A single aggregate metric can hide poor performance on an important minority subgroup of the data — worth checking metrics broken out by subgroup when different segments matter differently, not just the overall number.

## Check your understanding
<!-- bite: 2f81571d-f28f-4fd7-8fc9-47bc2cff8b52 -->

Try each one before you open the answer.

1. <!-- q: gap id="b681e0db" answers="0.909090909091|90.9%;0.909090909091|90.9%;0.952380952381|95.2%" sigfigs="2" -->
   Fill in the gaps. From the N = 165 example (TN = 50, FP = 10, FN = 5, TP = 100): accuracy is ___, precision is ___ and recall is ___.

   <details><summary>Answer</summary>

   Accuracy = (100 + 50) / 165 = 0.909. Precision = 100 / (100 + 10) = 0.909. Recall = 100 / (100 + 5) = 0.952.

   </details>

2. <!-- q: mcq id="4196b6c5" -->
   A disease test must not miss sick people. Which metric matters most?

   - [ ] Accuracy
   - [ ] Precision
   - [x] Recall

   <details><summary>Answer</summary>

   Recall, because a false negative (a sick person told they are fine) is the costly mistake.

   </details>

3. <!-- q: exact id="33dafbb9" answer="0.666666666667" accept="2/3|66.7%" sigfigs="2" -->
   Precision = 0.5 and recall = 1.0. What is the F1-score?

   <details><summary>Answer</summary>

   F1 = 2 × (0.5 × 1.0) / (0.5 + 1.0) = 1.0 / 1.5 = 0.667.

   </details>

4. <!-- q: mcq id="c1cb1ce9" -->
   The model predicted Yes, but the real answer was No. What is that, and which error type?

   - [x] A false positive, a Type I error
   - [ ] A false negative, a Type II error
   - [ ] A true negative

   <details><summary>Answer</summary>

   A false positive (Type I error). A false negative, predicting No when it is actually Yes, is a Type II error.

   </details>

5. <!-- q: open id="a3288b10" -->
   A fraud dataset is 99% "not fraud". A model that always predicts "not fraud" gets 99% accuracy. Why is it useless, and what should you look at instead?

   <details><summary>Answer</summary>

   It never catches a single fraud case, so its recall for fraud is 0. On imbalanced data, accuracy hides the minority class. Look at precision, recall and F1, or the confusion matrix.

   </details>

## Practice — independent task
<!-- bite: 066d48f1-d938-466f-b868-b30d5473de6f -->

Past question 3 in the [[machine-learning/ssg-535-question-bank|SSG 535 question bank]] gives 100 patients and asks for the confusion matrix and all the metrics. **Done when** your rows and columns add up to the totals in the question and you have said which error is most dangerous. Then check the solution.

## Before moving on
<!-- bite: 97002fd2-8f98-4fda-9623-5dfe4759cdec -->

Every classification metric here comes from the confusion matrix. Accuracy can mislead on imbalanced data; precision counts false alarms, recall counts misses, and F1 balances the two.

**Next:** [[machine-learning/04-model-evaluation/02-evaluation-metrics-2|Evaluation Metrics 2]]. These metrics judge the final yes/no answer. Next are two metrics that judge the model's probabilities and scores: log loss and AUC.

## About this lesson
<!-- bite: a9463041-cafb-45a1-b2b2-db5f67637e5a -->

**Level:** Intermediate. **Covers:** what evaluation is and why it matters, the confusion matrix, accuracy, precision, recall and F1-score. Part 1 of 3 on evaluation metrics. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
