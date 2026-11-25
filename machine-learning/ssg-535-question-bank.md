# SSG 535 Question Bank

Every practice and exam question from SSG 535 (Introduction to Machine Learning, 2025/2026 first semester) in one place. Each question points to the lesson that teaches the method, and the worked solution is hidden under **Solution** so you attempt it first.

**How to use this:** attempt each question closed-book, on paper, with a calculator. Open the solution only after you have an answer, then compare step by step. Where the notes only kept a worked solution, the question wording here was rebuilt from it, so check it against the original paper if you have it.

---

## Practice questions

### Practice question 1 (regression metrics)

→ [[machine-learning/04-model-evaluation/03-evaluation-metrics-3|Evaluation Metrics 3]]

**Given the table below, calculate the Mean Absolute Percentage Error (MAPE), R-squared (R²) score and RMSE.**

> **Note:** MAPE is a popular percentage-based metric used to measure forecasting accuracy by calculating the average absolute percentage difference between predicted and actual values.
>
> The formula is below, where N = number of observations, A\_i is the actual value and P\_i is the predicted value.

$$
\text{MAPE} = \frac{1}{N} \sum_{i=1}^{N} \left| \frac{A_i - P_i}{A_i} \right| \times 100\%
$$

| Index | Actual Value (y) | Predicted Value (ŷ) |
| --- | --- | --- |
| 0 | 88 | 77.95 |
| 1 | 78 | 75.54 |
| 2 | 64 | 65.96 |
| 3 | 92 | 87.35 |
| 4 | 57 | 57.40 |
| 5 | 70 | 69.20 |
| 6 | 88 | 88.11 |
| 7 | 68 | 65.86 |
| 8 | 72 | 69.34 |
| 9 | 60 | 59.41 |

<details><summary>Solution</summary>

$$
MAPE = \frac{1}{N} \sum_{i=1}^{N} \left| \frac{y_i - \hat{y}_i}{y_i} \right| \times 100\%
$$

$$
RMSE = \sqrt{\frac{\sum_{i=1}^{N} (y_i - \hat{y}_i)^2}{N}}
$$

$$
R^2 = 1 - \frac{\sum_{i=1}^{N} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{N} (y_i - \bar{y})^2}
$$

First, the mean of the actual values:

$$
\bar{y} = \frac{\sum y}{N} = \frac{737}{10} = 73.7
$$

Now N = 10. We work out each row:

| Index | y | ŷ | \|y − ŷ\| | (y − ŷ)² | \|y − ŷ\| / y | y − ȳ | (y − ȳ)² |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 88 | 77.95 | 10.05 | 101.0025 | 0.1142 | 14.3 | 204.49 |
| 1 | 78 | 75.54 | 2.46 | 6.0516 | 0.0315 | 4.3 | 18.49 |
| 2 | 64 | 65.96 | 1.96 | 3.8416 | 0.0306 | −9.7 | 94.09 |
| 3 | 92 | 87.35 | 4.65 | 21.6225 | 0.0505 | 18.3 | 334.89 |
| 4 | 57 | 57.40 | 0.40 | 0.1600 | 0.0070 | −16.7 | 278.89 |
| 5 | 70 | 69.20 | 0.80 | 0.6400 | 0.0114 | −3.7 | 13.69 |
| 6 | 88 | 88.11 | 0.11 | 0.0121 | 0.0013 | 14.3 | 204.49 |
| 7 | 68 | 65.86 | 2.14 | 4.5796 | 0.0315 | −5.7 | 32.49 |
| 8 | 72 | 69.34 | 2.66 | 7.0756 | 0.0369 | −1.7 | 2.89 |
| 9 | 60 | 59.41 | 0.59 | 0.3481 | 0.0098 | −13.7 | 187.69 |
| **Total** | **737** |  |  | **145.3336** | **0.3247** |  | **1372.1** |

Then:

$$
\text{MAPE} = \frac{0.3247}{10} \times 100\% = 3.247\%
$$

$$
R^2 = 1 - \frac{145.3336}{1372.1} = 0.8941
$$

$$
\text{RMSE} = \sqrt{\frac{145.3336}{10}} = 3.8123
$$

</details>

### Practice question 2 (classification metrics)

→ [[machine-learning/04-model-evaluation/01-evaluation-metrics-1|Evaluation Metrics 1]] and [[machine-learning/04-model-evaluation/02-evaluation-metrics-2|Evaluation Metrics 2]]

**A data scientist is evaluating different binary classification models. A false positive result is 10 times more expensive (from a business perspective) than a false negative result. The models should be evaluated based on the following criteria:**

1. Must have a recall rate of at least 60%
2. Must have a false positive rate (FPR) of 20% or less
3. Must minimize business costs

After creating each binary classification model, the data scientist generates the corresponding confusion matrix. Assuming we have 10,000 total instances in our dataset, calculate the precision, recall, and F1-score.

<details><summary>Solution</summary>

Since the specific counts are not given, let us assume a balanced dataset (5,000 positives, 5,000 negatives) and use the minimum requirements to see what the scores would look like.

**Recall rate (True Positive Rate) ≥ 60%**

Total Positives (P) = 5,000 and Recall must be at least 60%:

$$
\text{TP} = 5{,}000 \times 0.60 = 3{,}000
$$

$$
\text{FN} = 5{,}000 - 3{,}000 = 2{,}000
$$

**Calculate FP and TN (using FPR ≤ 20%)**

Total Negatives (N) = 5,000 and FPR must be 20% or less:

$$
\text{FP} = 5{,}000 \times 0.20 = 1{,}000
$$

$$
\text{TN} = 5{,}000 - 1{,}000 = 4{,}000
$$

**Then the scores:**

$$
\text{Precision} = \frac{TP}{TP + FP} = \frac{3{,}000}{3{,}000 + 1{,}000} = 0.75
$$

$$
\text{Recall} = 0.60
$$

$$
\text{F1-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}} = 2 \times \frac{0.75 \times 0.60}{0.75 + 0.60} = 0.667
$$

</details>

---

## Past questions (2025/2026 first semester exam)

The exam had six questions, and you answer any four, in 2 hours.

### Question 1: Decision tree

→ [[machine-learning/03-classical-ml/05-decision-trees-1|Decision Trees 1]], [[machine-learning/03-classical-ml/06-decision-trees-2|Decision Trees 2]], [[machine-learning/03-classical-ml/07-decision-trees-3|Decision Trees 3]], [[machine-learning/03-classical-ml/10-decision-trees-6|Decision Trees 6]]

**a)** Evaluate decision trees. *(2 marks)*

**b)** Using the table below, find the best attribute for the root node and build the decision tree. *(13 marks)*

| Day | Age | Income | Student | Credit Rating | Buy Laptop |
| --- | --- | --- | --- | --- | --- |
| 1 | Youth | High | No | Fair | No |
| 2 | Youth | High | No | Excellent | No |
| 3 | Middle | High | No | Fair | Yes |
| 4 | Senior | Medium | No | Fair | Yes |
| 5 | Senior | Low | Yes | Fair | Yes |
| 6 | Senior | Low | Yes | Excellent | No |
| 7 | Middle | Low | Yes | Excellent | Yes |
| 8 | Youth | Medium | No | Fair | No |
| 9 | Youth | Low | Yes | Fair | Yes |
| 10 | Senior | Medium | Yes | Fair | Yes |

*The table was rebuilt from the day lists in the worked solution, because the notes did not copy it out. Check it against the original paper if you have it.*

<details><summary>Solution</summary>

**a) Evaluate decision trees (2 marks).**

A decision tree is a supervised learning method that makes a decision by asking a chain of if/else questions about the data. It has a root node, branches, internal nodes and leaf nodes. Each internal node tests one attribute, each branch is one answer to that test, and each leaf gives the final result. It can be used for classification and regression. Its strengths are that it is easy to understand and to draw, and it needs little data preparation. Its weaknesses are that it overfits easily if it grows too deep (pruning helps) and a small change in the data can change the whole tree. (See [[machine-learning/03-classical-ml/05-decision-trees-1|Decision Trees 1]] and [[machine-learning/03-classical-ml/10-decision-trees-6|Decision Trees 6]].)

**b) Find the best attribute for the root node and build the tree (13 marks).**

The table has 10 days. The target is Buy Laptop. Yes appears 6 times (days 3, 4, 5, 7, 9, 10) and No appears 4 times (days 1, 2, 6, 8). We use entropy and information gain, the same way we did in the Play Tennis example.

**Step 1: Entropy of the whole data.**

Entropy of the whole data:

$$
\text{Entropy}(S) = -\frac{6}{10}\log_2\frac{6}{10} - \frac{4}{10}\log_2\frac{4}{10} = 0.44218 + 0.52877 = 0.97095
$$

**Step 2: Information gain for each attribute.**

**Age**

- Youth (days 1, 2, 8, 9): 1 Yes, 3 No. Entropy = 0.81128
- Middle (days 3, 7): 2 Yes, 0 No. Entropy = 0 (pure)
- Senior (days 4, 5, 6, 10): 3 Yes, 1 No. Entropy = 0.81128

$$
\text{Weighted entropy} = \frac{4}{10}(0.81128) + \frac{2}{10}(0) + \frac{4}{10}(0.81128) = 0.64902
$$

$$
\text{Gain}(\text{Age}) = 0.97095 - 0.64902 = 0.32193
$$

**Income**

- High (days 1, 2, 3): 1 Yes, 2 No. Entropy = 0.91830
- Medium (days 4, 8, 10): 2 Yes, 1 No. Entropy = 0.91830
- Low (days 5, 6, 7, 9): 3 Yes, 1 No. Entropy = 0.81128

$$
\text{Weighted entropy} = \frac{3}{10}(0.91830) + \frac{3}{10}(0.91830) + \frac{4}{10}(0.81128) = 0.87549
$$

$$
\text{Gain}(\text{Income}) = 0.97095 - 0.87549 = 0.09546
$$

**Student**

- No (days 1, 2, 3, 4, 8): 2 Yes, 3 No. Entropy = 0.97095
- Yes (days 5, 6, 7, 9, 10): 4 Yes, 1 No. Entropy = 0.72193

$$
\text{Weighted entropy} = \frac{5}{10}(0.97095) + \frac{5}{10}(0.72193) = 0.84644
$$

$$
\text{Gain}(\text{Student}) = 0.97095 - 0.84644 = 0.12451
$$

**Credit Rating**

- Fair (days 1, 3, 4, 5, 8, 9, 10): 5 Yes, 2 No. Entropy = 0.86312
- Excellent (days 2, 6, 7): 1 Yes, 2 No. Entropy = 0.91830

$$
\text{Weighted entropy} = \frac{7}{10}(0.86312) + \frac{3}{10}(0.91830) = 0.87967
$$

$$
\text{Gain}(\text{Credit Rating}) = 0.97095 - 0.87967 = 0.09128
$$

**Step 3: Pick the root.**

| Attribute | Information Gain |
| --- | --- |
| Age | 0.32193 |
| Student | 0.12451 |
| Income | 0.09546 |
| Credit Rating | 0.09128 |

Age has the highest gain, so **Age is the best attribute for the root node.**

**Step 4: Grow each branch.**

- **Middle:** both days (3 and 7) are Yes. This branch is pure, so it becomes a leaf: **Yes**.
- **Youth** (days 1, 2, 8, 9: No, No, No, Yes): we test the remaining attributes on these 4 days. Student splits them perfectly: Student = No gives days 1, 2, 8, which are all No, and Student = Yes gives day 9, which is Yes. So the Youth branch uses **Student**. (Income would also split them perfectly, so it ties with Student. We choose Student because it has only two branches, which gives a simpler tree.)
- **Senior** (days 4, 5, 6, 10: Yes, Yes, No, Yes): Credit Rating splits them perfectly: Fair gives days 4, 5, 10, which are all Yes, and Excellent gives day 6, which is No. Student and Income do not split them cleanly, so the Senior branch uses **Credit Rating**.

**Final decision tree:**

- **Age = Youth** → test Student
  - Student = No → **No**
  - Student = Yes → **Yes**
- **Age = Middle** → **Yes**
- **Age = Senior** → test Credit Rating
  - Credit Rating = Fair → **Yes**
  - Credit Rating = Excellent → **No**

All 10 days are classified correctly by this tree, because every leaf is pure.

</details>

### Question 2: Sales forecast error metrics

→ [[machine-learning/04-model-evaluation/03-evaluation-metrics-3|Evaluation Metrics 3]]

A company recorded its actual monthly sales, and a model forecast them:

| Month | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Actual | 120 | 135 | 150 | 160 | 170 | 165 | 180 | 175 | 190 | 200 |
| Forecast | 115 | 140 | 148 | 155 | 172 | 160 | 178 | 180 | 185 | 205 |

Calculate **a)** the Mean Squared Error (MSE), **b)** the Root Mean Squared Error (RMSE), **c)** the Mean Absolute Error (MAE) and **d)** the R² score. Then interpret the results and give recommendations.

<details><summary>Solution</summary>

**Step 1: Work out the error for each month.** Error = Actual − Forecast.

| Month | Actual | Forecast | Error | Absolute Error | Squared Error |
| --- | --- | --- | --- | --- | --- |
| Jan | 120 | 115 | 5 | 5 | 25 |
| Feb | 135 | 140 | −5 | 5 | 25 |
| Mar | 150 | 148 | 2 | 2 | 4 |
| Apr | 160 | 155 | 5 | 5 | 25 |
| May | 170 | 172 | −2 | 2 | 4 |
| Jun | 165 | 160 | 5 | 5 | 25 |
| Jul | 180 | 178 | 2 | 2 | 4 |
| Aug | 175 | 180 | −5 | 5 | 25 |
| Sep | 190 | 185 | 5 | 5 | 25 |
| Oct | 200 | 205 | −5 | 5 | 25 |
| **Total** |  |  | **7** | **41** | **187** |

There are n = 10 months.

**a) Mean Squared Error (MSE)**

$$
\text{MSE} = \frac{\text{sum of squared errors}}{n} = \frac{187}{10} = 18.7
$$

**b) Root Mean Squared Error (RMSE)**

$$
\text{RMSE} = \sqrt{18.7} = 4.32
$$

**c) Mean Absolute Error (MAE)**

$$
\text{MAE} = \frac{\text{sum of absolute errors}}{n} = \frac{41}{10} = 4.1
$$

**d) R-Square (R²) Score**

R² compares our model's errors with the errors we would make if we just guessed the average every time.

Mean of actual sales:

$$
\bar{y} = \frac{1645}{10} = 164.5
$$

Total variation:

$$
SS_{tot} = \sum (\text{Actual} - 164.5)^2
$$

$$
SS_{tot} = 1980.25 + 870.25 + 210.25 + 20.25 + 30.25 + 0.25 + 240.25 + 110.25 + 650.25 + 1260.25 = 5372.5
$$

Unexplained variation (the sum of squared errors):

$$
SS_{res} = \sum (\text{Actual} - \text{Forecast})^2 = 187
$$

$$
R^2 = 1 - \frac{SS_{res}}{SS_{tot}} = 1 - \frac{187}{5372.5} = 1 - 0.0348 = 0.965
$$

**Interpretation**

- On average the forecast is off by about 4.1 units (MAE). Monthly sales are between 120 and 200 units, so that is only about 2.5% of the average sales of 164.5. This is a small error.
- RMSE (4.32) is only a little higher than MAE (4.1). RMSE punishes big errors more than MAE does, so the two being close tells us there are no big, sudden misses. The errors are all small and about the same size (never more than 5).
- R² of 0.965 means the model explains about 96.5% of how sales go up and down from month to month. That is very good.
- The errors do not lean strongly one way. Six months were under-forecast (actual higher than forecast) and four were over-forecast, with the total error only 7 (an average of 0.7 per month).

**Recommendations**

- The model is reliable enough to use for planning. Keep using it.
- Keep checking the errors every month. If MAE starts growing or one error suddenly becomes large, retrain the model with newer data.
- Add a small safety stock, around 5 units, since the forecast can miss by about that much in either direction.
- To improve it further, look at the months with the biggest misses (Jan, Feb, Apr, Jun, Aug, Sep and Oct, all off by 5) and check whether something like promotions or holidays explains them.

</details>

### Question 3: Confusion matrix for 100 patients

→ [[machine-learning/04-model-evaluation/01-evaluation-metrics-1|Evaluation Metrics 1]]

The test set has 100 patients. In reality, 30 have the condition and 70 are healthy. The model predicts that 40 have the condition and 60 are healthy. Build the confusion matrix, calculate accuracy, precision, recall, F1-score and specificity, interpret them and make recommendations.

<details><summary>Solution</summary>

**A note before we start.** The question gives only the totals (how many are actually sick and how many were predicted sick). It does not say how many of the 40 predicted-sick patients were really sick. That number is the True Positives (TP), and we need it to fill the matrix. So I have **assumed TP = 25**. If your lecturer gave a different number in class, use that one. The method is exactly the same, only the numbers change. The general rules below show how everything follows from TP.

Predicted sick but actually healthy:

$$
\text{FP} = 40 - \text{TP}
$$

Actually sick but predicted healthy:

$$
\text{FN} = 30 - \text{TP}
$$

Actually healthy and predicted healthy:

$$
\text{TN} = 70 - \text{FP}
$$

With TP = 25:

$$
\text{FP} = 40 - 25 = 15 \qquad \text{FN} = 30 - 25 = 5 \qquad \text{TN} = 70 - 15 = 55
$$

**Confusion matrix**

|  | Predicted: Has condition | Predicted: Healthy | Total |
| --- | --- | --- | --- |
| **Actual: Has condition** | TP = 25 | FN = 5 | 30 |
| **Actual: Healthy** | FP = 15 | TN = 55 | 70 |
| **Total** | 40 | 60 | 100 |

Check: the rows add to 30 and 70, and the columns add to 40 and 60, which matches the question.

**Metrics**

$$
\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{total}} = \frac{25 + 55}{100} = 0.80 = 80\%
$$

$$
\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}} = \frac{25}{40} = 0.625 = 62.5\%
$$

$$
\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}} = \frac{25}{30} = 0.833 = 83.3\%
$$

$$
\text{F1-score} = 2 \times \frac{0.625 \times 0.833}{0.625 + 0.833} = 0.714
$$

$$
\text{Specificity} = \frac{\text{TN}}{\text{TN} + \text{FP}} = \frac{55}{70} = 0.786 = 78.6\%
$$

**Interpretation**

- The model is right 80% of the time overall, but accuracy alone can hide problems because 70% of the patients are healthy anyway.
- Recall is 83.3%. The model finds 25 of the 30 sick patients, so it misses 5 sick people. In medicine this is the most dangerous error, because a sick person is told they are fine.
- Precision is 62.5%. Out of every 8 patients the model flags, about 3 are actually healthy. These are false alarms.
- Specificity is 78.6%. The model correctly clears about 79% of the healthy patients, and wrongly flags the other 21%.

**Recommendations**

- For a medical test, missing a sick patient costs more than a false alarm, so the priority is to push recall higher (fewer false negatives), even if precision drops a little.
- Treat a positive result as a reason for a second, more accurate test, not as a final diagnosis. This handles the false alarms.
- Improve the model with more data or better features, and check the metrics again on new patients.

</details>

### Question 4: Instance-based learning and kernel machines

→ [[machine-learning/03-classical-ml/02-k-nearest-neighbours-2|K-Nearest Neighbours 2]] and [[machine-learning/03-classical-ml/16-kernel-machines|Kernel Machines]]

**a)** A company wants to use instance-based learning to predict customer purchase behaviour. Explain how it differs from model-based learning, give its advantages, and discuss its limitations on a large customer dataset in terms of memory usage, computation time and prediction accuracy.

**b)** For complex non-linear data, compare a linear classifier with a kernel-based model (SVM). Discuss the advantages and the limitations of kernel machines in terms of computational complexity, overfitting, interpretability and scalability.

<details><summary>Solution</summary>

**a) Instance-based learning for predicting customer purchase behaviour.** (See [[machine-learning/03-classical-ml/01-k-nearest-neighbours-1|K-Nearest Neighbours 1]] and [[machine-learning/03-classical-ml/02-k-nearest-neighbours-2|K-Nearest Neighbours 2]].)

**How it differs from model-based learning.**

- A model-based method (like a decision tree or linear model) uses the training data to build a model, a small set of rules or numbers. After training, it can throw the data away and predict using only the model.
- An instance-based method (like k-NN) does not build a model. It simply stores the training data. When a new customer comes, it looks for the k most similar customers in the stored data (using a distance like Euclidean distance) and predicts from them: the majority class for classification, or the average for regression. This is why it is called a lazy learner: it does no work at training time and does all the work at prediction time.

**Advantages**

- Very simple to understand and to set up. There is almost no training.
- It makes no assumption about the shape of the data, so it can handle complex, non-linear patterns.
- New customer data can be added easily, with no need to retrain.

**Limitations on a large customer dataset**

- **Memory usage:** it must keep the whole dataset. With millions of customers this takes a lot of storage.
- **Computation time:** every prediction needs a distance calculation to every stored customer, so predictions become slow as the data grows. This is the opposite of model-based methods, which are slow to train but fast to predict.
- **Prediction accuracy:** it depends heavily on the scaling of features (a feature like income in thousands can drown out a feature like age) and on the choice of k. Irrelevant features and noisy data hurt it. It also struggles when there are many features, because distances become less meaningful.

**Ways to reduce the problems:** scale the features, remove useless features, choose k with cross-validation, and use faster search structures or a smaller sample of representative customers.

**b) Linear classifier or kernel-based model (SVM) for complex non-linear data.** (See [[machine-learning/03-classical-ml/16-kernel-machines|Kernel Machines]].)

A linear classifier separates the classes with a straight line (or flat plane). A kernel machine such as an SVM uses a kernel function to work as if the data were moved into a higher-dimensional space where a clean separation exists, without actually calculating the new coordinates (the kernel trick). Common kernels are linear, polynomial and RBF.

**Advantages of kernel machines**

- They can capture complex, non-linear relationships that a linear classifier cannot, such as the handwritten digits example.
- They work well in high-dimensional data, and the kernel trick keeps the calculation efficient.
- The SVM looks for the best separating boundary (the optimal hyperplane with the widest margin), which helps it generalize well.

**Limitations**

- **Computational complexity:** training gets slow as the data grows, because the method compares data points with each other. It is heavy on very large datasets.
- **Overfitting:** a very flexible kernel (for example an RBF kernel with the wrong settings) can fit the noise in the training data. The kernel type and its settings must be chosen carefully, usually with cross-validation.
- **Interpretability:** a linear classifier is easy to explain, since each feature has a clear weight. A kernel model is much harder to explain, since the decision boundary lives in a space we cannot see.
- **Scalability:** memory and training time grow quickly with the number of samples, so it does not scale well to very large datasets.

**Conclusion:** if the data is truly complex and non-linear and the dataset is small to medium, use the kernel-based SVM. If the dataset is very large, or we need an easy explanation, start with the linear classifier and move to a kernel model only if the linear one performs badly.

</details>

### Question 5: Clustering and ILP

→ [[machine-learning/03-classical-ml/17-clustering-1|Clustering 1]], [[machine-learning/03-classical-ml/18-clustering-2|Clustering 2]] and [[machine-learning/03-classical-ml/20-inductive-logic-programming|Inductive Logic Programming]]

**a)** A telecommunications company wants to segment its customers. The features are monthly call duration, data usage, number of SMS messages and monthly billing amount.

- i) Explain how clustering helps the company.
- ii) Discuss the suitability of K-Means and hierarchical clustering for this problem.
- iii) Design a clustering approach: data preprocessing, algorithm selection, and evaluation of cluster quality.

**b)** Background knowledge: `mother(mary, john)`, `mother(mary, anna)`, `father(paul, john)`, `father(paul, anna)`, with the rules `parent(X, Y) :- mother(X, Y).` and `parent(X, Y) :- father(X, Y).` Positive examples: `sibling(john, anna)`, `sibling(anna, john)`. Negative example: `sibling(john, john)`. Induce a rule for `sibling(X, Y)`.

<details><summary>Solution</summary>

**a) Customer segmentation for a telecommunications company.** The features are monthly call duration, data usage, number of SMS messages and monthly billing amount. (See [[machine-learning/03-classical-ml/17-clustering-1|Clustering 1]] and [[machine-learning/03-classical-ml/18-clustering-2|Clustering 2]].)

**i) How clustering helps the company.**

Clustering is unsupervised learning, so we do not need any labels. We give the algorithm the usage data and it groups customers who behave alike. The company can then study each group and learn who its customers really are. For example, it might find:

- heavy data users who barely call (young people who stream a lot),
- heavy callers with high bills (business users),
- low-usage customers with small bills (likely to leave, or on cheap plans).

With these groups the company can design different marketing for each: a big data bundle for the first group, a loyalty or call package for the second, and a discount to keep the third. It also helps to spot customers who might leave and to price plans better. The result is better targeted offers and less wasted advertising.

**ii) Suitability of K-Means and Hierarchical Clustering.**

- **K-Means:** it assigns each customer to the nearest centroid and recalculates the centroids until they stop changing. It is fast and scales well to many customers. It suits this problem because the features are numbers. Its weaknesses are that we must choose the number of clusters (k) before we start, it can be thrown off by outliers (a few customers with extremely high usage), and it works best when groups are roughly round and similar in size.
- **Hierarchical clustering (agglomerative):** it starts with each customer as its own cluster and keeps merging the closest clusters, and the result is shown in a dendrogram. We do not have to decide the number of clusters first, because we can look at the dendrogram and cut where it makes sense. It is good for seeing how groups are related. Its weakness is that it is slow and uses a lot of memory on a very large customer base, and it has no predict method for new customers.
- **Verdict:** a telecom company usually has a very large number of customers, so K-Means is the more practical choice. Hierarchical clustering is better used on a small sample to get a feel for how many groups there are, and that number can then be used as k in K-Means.

**iii) Design of a clustering approach.**

1. **Data preprocessing:** remove duplicates and fill or remove missing values. Check for outliers and decide whether to cap or remove them. Scale all four features to the same range (for example standardization), because billing amount and data usage are on very different scales, and distance-based clustering would otherwise be dominated by the biggest numbers. Remove features that carry the same information twice if they are strongly related.
2. **Algorithm selection:** use K-Means as the main method. Choose k using the elbow method (plot the total within-cluster distance for different k and pick the point where it stops dropping quickly), and optionally confirm with a dendrogram from hierarchical clustering on a sample.
3. **Evaluation of cluster quality:** use the silhouette score, which measures how close each customer is to its own cluster compared with the nearest other cluster (closer to 1 is better). Also check that clusters are stable when run again with different starting centroids or a different sample. Finally, check that the groups make business sense: look at the average values of each group and see if each one can be described and used by the marketing team.

**b) ILP: finding a rule for sibling(X, Y).** (See [[machine-learning/03-classical-ml/20-inductive-logic-programming|Inductive Logic Programming]].)

**What we know.** The background knowledge says that mary is the mother of john and anna, and paul is the father of john and anna. The two rules say that a mother or a father is a parent. So from the background, parent(mary, john), parent(mary, anna), parent(paul, john) and parent(paul, anna) are all true.

**What we want.** A rule for sibling that is true for the positive examples sibling(john, anna) and sibling(anna, john), and false for the negative example sibling(john, john).

**Reasoning.** John and anna are siblings because they share a parent. Take Z = mary: parent(mary, john) and parent(mary, anna) are both true. This covers both positive examples (in the second one, X = anna and Y = john). But if we only write "X and Y share a parent", then sibling(john, john) would also be true, since mary is a parent of john on both sides. That breaks the negative example. So we must add the condition that X and Y are different people.

**Induced rule:**

`sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.`

In words: X is a sibling of Y if some person Z is a parent of both of them, and X and Y are not the same person.

**Check.** sibling(john, anna) is true (Z = mary, john is not anna). sibling(anna, john) is true. sibling(john, john) is false because of X = Y, so the negative example is not covered. The rule covers all positives and no negatives.

</details>

### Question 6: Overfitting and a decision tree workflow

→ [[machine-learning/04-model-evaluation/04-overfitting-and-regularization|Overfitting]] and [[machine-learning/03-classical-ml/10-decision-trees-6|Decision Trees 6]]

**a)** Model A has 98% training accuracy and 60% test accuracy. Model B has 85% training accuracy and 82% test accuracy. Compare them and say which is better.

**b)** Describe a workflow for predicting student academic performance with a decision tree: i) data preprocessing, ii) model selection, iii) evaluation method.

<details><summary>Solution</summary>

**a) Comparing Model A and Model B.** (See [[machine-learning/04-model-evaluation/04-overfitting-and-regularization|Overfitting]].)

| Model | Training Accuracy | Test Accuracy | Gap |
| --- | --- | --- | --- |
| Model A | 98% | 60% | 38% |
| Model B | 85% | 82% | 3% |

- **Model A** is almost perfect on the data it learned from (98%) but poor on new data (60%). This big gap means it has memorized the training data, including its noise, instead of learning the real pattern. This is **overfitting**. It is too complex, and it will not do well on new students.
- **Model B** scores a little lower on training data (85%) but almost the same on test data (82%). The small gap means it learned the real pattern and carries it over to data it has never seen. It **generalizes** well.

**Which is better:** **Model B**. What we care about is how the model performs on new students, which is what the test accuracy measures. Model B's 82% beats Model A's 60%, even though Model A looks better on the training data.

To fix Model A we could use a simpler model, get more training data, remove unneeded features, use cross-validation, or add regularization (or pruning, if it is a decision tree).

**b) Workflow for predicting student academic performance with a decision tree.** (See [[machine-learning/03-classical-ml/05-decision-trees-1|Decision Trees 1]] and [[machine-learning/03-classical-ml/10-decision-trees-6|Decision Trees 6]].)

**i) Data preprocessing**

- Collect the data: each student is a row, with features like study hours, attendance rate and previous GPA, and the label (pass or fail).
- Clean it: remove duplicates, fix wrong values (for example attendance above 100%), and handle missing values by filling them in (for example with the average) or removing the rows.
- Encode any text categories as numbers if needed. Decision trees do not need feature scaling, so no scaling is required.
- Split the data into a training set and a test set (for example 80% and 20%), so we can check the model on students it has not seen.

**ii) Model selection**

- Use a decision tree classifier, since the output is a class (pass or fail). It is easy to explain: each path from the root to a leaf is a clear rule, such as "if attendance is high and study hours are above a value, then pass".
- It chooses the best attribute at each step using information gain (entropy) or Gini impurity, as in our earlier examples.
- To stop overfitting, limit the tree with pre-pruning (a maximum depth or a minimum number of samples in a node) or prune it after it is built (post-pruning). Choose these settings using cross-validation.

**iii) Evaluation method**

- Train on the training set and test on the test set. Use k-fold cross-validation to get a more reliable score.
- Build a confusion matrix and calculate accuracy, precision, recall and F1-score. Recall for the "fail" class is especially useful, because we want to catch students who are at risk.
- Compare training and test accuracy. If training is much higher than test, the tree is overfitting (as with Model A) and needs more pruning.

</details>
