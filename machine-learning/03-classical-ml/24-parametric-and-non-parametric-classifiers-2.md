---
id: 8cb2d74f-51b9-4f8d-8fa5-a9b4b5e1553d
---

# Parametric and Non-Parametric Classifiers 2: Training, Testing and Comparing

Comparing classifiers fairly means testing them on data they haven't seen and scoring them with the same measures.

## Before you start
<!-- bite: 577507c5-e3a9-483d-910e-b36d0825b9e5 -->

Read [[machine-learning/03-classical-ml/23-parametric-and-non-parametric-classifiers-1|Parametric and Non-Parametric Classifiers 1]] first. It helps to have met the confusion matrix in [[machine-learning/04-model-evaluation/01-evaluation-metrics-1|Evaluation Metrics 1]].

After this lesson you will be able to:

1. draw the process of supervised classification, including its four test options;
2. compute Cohen's kappa from a confusion matrix, and MAE and RMSE from a list of errors;
3. describe the course paper's experiment and its results;
4. explain why the paper's "use training set" results are misleading, and which results to trust.

## What this lesson covers
<!-- bite: 7267e530-823c-4a0c-8da5-325a489c5901 -->

Lesson 23 compared a parametric and a non-parametric classifier on one point. Real comparisons use whole datasets, and the course paper (Kumar and Sahoo, 2012) does exactly that: it trains two parametric and two non-parametric classifiers on a real dataset, using the WEKA data-mining tool, and compares them.

To read that paper properly, you need its process and its four measures. And once you have them, you'll spot a serious problem in its conclusion, which teaches the most important lesson in evaluating any classifier.

## The kid version
<!-- bite: e67846c3-bd1a-4a26-adde-d6f8b585f5db -->

Two students are preparing for an exam. One memorises the answers to last year's paper word for word. The other actually learns the topics. If you test them on last year's paper, the memoriser scores 100% and looks like a genius. Test them on a *new* paper, and the memoriser falls apart while the other student does fine. To know who really learned, you must test on questions they haven't seen.

**Where the analogy stops working.** A student who memorised knows they're bluffing. A classifier has no idea; it reports its training score as confidently as its real one, so it's entirely up to you to test it properly.

## The process of supervised classification
<!-- bite: f1a1a4e5-f040-4e7e-8d85-5d7a98e88738 -->

The course paper gives this process for building a supervised classifier:

![The process of supervised classification: problem, data identification, data preprocessing, training set, classifier selection, training, evaluation on test data using one of four test options, then if good enough the classifier, otherwise parameter tuning and back to training.](../images/pr-supervised-process.svg)

## The process, step by step
<!-- bite: c98a48c0-e52f-4c8f-9f89-6985fe20e3e1 -->

Here's what each box in that picture means:

1. **Problem**: decide what you're classifying.
2. **Data identification**: find the data that bears on it.
3. **Data preprocessing**: clean and transform it.
4. **Training set**: set aside the data to learn from.
5. **Classifier selection**: choose a classifier.
6. **Training**: fit it to the training set.
7. **Evaluation of the test set**: measure how well it does.
8. **Result**: if it's good enough, you have your classifier. If not, **parameter tuning** and back to training.

The paper also lists the general stages of a classification task: data acquisition, data preprocessing, data presentation, decision making and performance evaluation.

## The four test options
<!-- bite: 6a117f73-1c9e-4b75-81b0-e74f3ab00223 -->

Step 7 can be done four ways in WEKA, and the paper's whole argument turns on which one you choose:

1. **Use training set**: test on the same data the classifier was trained on.
2. **Supplied test set**: test on a separate set of data you provide.
3. **Cross-validation**: split the data into, say, 10 parts (**folds**). Train on 9 and test on the 10th, ten times over, so every part is tested once by a model that didn't see it. Average the ten scores. This is **10-fold cross-validation**.
4. **Percentage split**: train on one percentage of the data (say 66%) and test on the rest.

Options 2, 3 and 4 all test on data the model hasn't seen. Option 1 doesn't. Remember the kid version.

## Measure 1: Cohen's kappa
<!-- bite: 2ef4efdf-83a5-4c57-ad22-5ca2d65a5956 -->

**Kappa** measures how well the predictions agree with the true classes, *after removing the agreement you'd get by luck*. The paper says it runs from 0 to 1: 1 is perfect agreement, 0 is no better than chance, 0.40–0.59 is moderate, 0.60–0.79 substantial, and above 0.80 outstanding.

In words: kappa is how much better than chance the classifier did, divided by how much better than chance it *could* have done.

$$\kappa = \frac{p_o - p_e}{1 - p_e}$$

where $p_o$ is the fraction of predictions that are correct and $p_e$ is the fraction you'd expect to be correct by chance.

## Computing kappa
<!-- bite: 2cba1b37-0f87-43d5-a71c-1f529e5e2bd1 -->

A classifier is tested on 100 cases. Its confusion matrix: 40 true positives, 10 false negatives, 20 false positives, 30 true negatives.

1. **Observed agreement:** $p_o = (40 + 30) / 100 = 0.70$.
2. **Chance agreement.** 50 cases are really positive (40 + 10) and the classifier said "positive" 60 times (40 + 20). 50 are really negative and it said "negative" 40 times. So $p_e = (50 \times 60 + 50 \times 40) / 100^2 = (3{,}000 + 2{,}000) / 10{,}000 = 0.50$.
3. **Kappa:** $\kappa = (0.70 - 0.50) / (1 - 0.50) = 0.20 / 0.50 = \mathbf{0.40}$.

The classifier is 70% accurate, but half of that could happen by luck, so its kappa is a merely moderate 0.40. That's why kappa is more honest than plain accuracy.

## Measures 2 and 3: MAE and RMSE
<!-- bite: 8ae7e973-816b-4e01-8320-7f5583626b00 -->

When a classifier outputs a probability, such as "0.9 chance of class 1", each prediction has an error: the gap between the probability and the true answer (1 or 0).

1. **MAE (mean absolute error)** is the sum of the absolute errors divided by the number of predictions.
2. **RMSE (root mean square error)** is the square root of the average squared error. Squaring punishes big errors more than small ones.

For both, smaller is better. Example: four predictions with errors 0.1, 0.4, 0.2 and 0.3.

1. MAE = (0.1 + 0.4 + 0.2 + 0.3) / 4 = **0.25**.
2. RMSE = $\sqrt{(0.01 + 0.16 + 0.04 + 0.09)/4} = \sqrt{0.075} \approx$ **0.274**.

RMSE is a bit larger than MAE because the 0.4 error counts extra when squared.

## Measure 4: ROC area
<!-- bite: 007d4eac-9ae7-4499-ad43-198a412fe2b5 -->

The **ROC area** (area under the ROC curve) summarises how well a classifier separates the classes across every possible decision threshold. The paper explains that by default a binary classifier predicts a class when its probability is 0.5 or more; moving that threshold, say to 0.7, makes fewer positive predictions and changes the confusion matrix. The ROC curve plots the trade-off across all thresholds. The area runs from 0 to 1; 0.5 is no better than guessing and 1 is perfect. [[machine-learning/04-model-evaluation/02-evaluation-metrics-2|Evaluation Metrics 2]] draws the curve.

## The paper's experiment
<!-- bite: c63f86f7-2629-4ada-8999-deb784d98b47 -->

The paper uses a breast-feeding dataset from the US National Longitudinal Survey of Youth: 927 first-born children, with 10 attributes about the mother and birth, such as the mother's age, education, and whether she smoked or was in poverty. It compares four classifiers:

1. **Parametric** (in the paper's terms): naive Bayes and Bayesian network.
2. **Non-parametric** (in the paper's terms): multilayer perceptron (MLP) and logistic regression.

It tests each one twice: with "use training set" and with 10-fold cross-validation.

## The paper's results
<!-- bite: 37c9661d-0e90-4b84-b34c-293c99b6f046 -->

Here are the paper's figures for kappa:

| Classifier | Kappa, use training set | Kappa, 10-fold cross-validation |
|---|---|---|
| Naive Bayes | 0.2724 | 0.1165 |
| Bayesian net | 0.2724 | 0.1165 |
| Logistic regression | 0.2232 | 0.1165 |
| Multilayer perceptron | **0.9144** | **0.045** |

The paper concludes that the "use training set" method performs better than 10-fold cross-validation, and that the MLP performs best of all.

Before reading on, look at the MLP row. What do you think happened?

## What the results really show
<!-- bite: 46c04556-07e4-4ef2-b980-541fb3259bce -->

The MLP scored an "outstanding" 0.91 kappa on the data it was trained on, and a nearly worthless 0.045 on data it hadn't seen. That's the memorising student from the kid version. A neural network has enough weights to memorise 927 examples, so it learned the training set, not the pattern. This is **overfitting**.

So the "use training set" method didn't *perform* better. It *flattered* every classifier, by marking them on questions they'd already seen. The 10-fold cross-validation numbers are the honest ones, and they say something quite different: all four classifiers do poorly on this dataset (kappa around 0.1 or below), and the MLP does worst.

## Two more things to notice
<!-- bite: 73479e98-8ae2-41e3-87f3-94a7c566658d -->

The table shows two more things worth noticing:

1. Naive Bayes and the Bayesian net scored exactly the same. The paper notes it without explaining; most likely WEKA's Bayesian net learned the same structure as naive Bayes here.
2. The paper's comparison can't show parametric beating non-parametric or the reverse: with honest testing, the differences are tiny and the dataset is simply hard.

The lesson for every classifier you'll ever build: **report the score on unseen data.** A training-set score tells you about memory, not about skill. [[machine-learning/04-model-evaluation/04-overfitting-and-regularization|Overfitting and Regularization]] covers how to prevent it.

## Terms used in this lesson
<!-- bite: 8aa4afa5-bc7b-43bb-afcd-7d902f7e3acb -->

1. **Test option**: This is the way a classifier is evaluated: on the training set, a supplied test set, by cross-validation or by a percentage split.
2. **Cross-validation**: This is splitting the data into $k$ folds and, $k$ times, training on all but one fold and testing on the one left out, then averaging the scores.
3. **Cohen's kappa ($\kappa$)**: This is the agreement between predictions and true classes after removing the agreement expected by chance: $(p_o - p_e) / (1 - p_e)$.
4. **MAE (mean absolute error)**: The letters stand for those words. It's the average size of the errors.
5. **RMSE (root mean square error)**: The letters stand for those words. It's the square root of the average squared error, which punishes large errors more.
6. **ROC area**: This is the area under the ROC curve, summarising how well a classifier separates the classes across all thresholds. 0.5 is guessing; 1 is perfect.
7. **Overfitting**: This is when a model learns its training examples, including their noise, so well that it does badly on new data.
8. **WEKA**: This is a free data-mining tool with many ready-made classifiers, used in the course paper.

## Common pitfalls and traps
<!-- bite: 4aadac27-613c-4e30-af4e-a85523074e07 -->

- **Trusting a training-set score.** It measures memory, not skill. The paper's MLP went from 0.91 to 0.045.
- **Reading kappa like accuracy.** A 70% accurate classifier can have a kappa of only 0.40, because chance alone would give 50%.
- **Forgetting which way MAE and RMSE go.** Smaller is better for both. Bigger is better for kappa and ROC area.

## Check your understanding
<!-- bite: dbf2a821-1c6b-4b83-b801-d4e2da0daa5b -->

Try each one before you open the answer.

1. <!-- q: exact id="9ae3da52" answer="0.8" accept="0.80" -->
   A classifier is tested on 100 cases: 45 true positives, 5 false negatives, 5 false positives and 45 true negatives. What is its kappa?

   <details><summary>Answer</summary>

   $p_o = (45 + 45)/100 = 0.9$. There are 50 real positives and 50 predicted positives, and 50 real and 50 predicted negatives, so $p_e = (50 \times 50 + 50 \times 50)/10{,}000 = 0.5$. $\kappa = (0.9 - 0.5)/(1 - 0.5) = 0.8$.

   </details>

2. <!-- q: exact id="912255e8" answer="0.25" -->
   Four predictions have errors 0.2, 0.2, 0.6 and 0.0. What is the MAE?

   <details><summary>Answer</summary>

   (0.2 + 0.2 + 0.6 + 0.0) / 4 = 1.0 / 4 = 0.25.

   </details>

3. <!-- q: exact id="3a209308" answer="0.331662" sigfigs="2" -->
   For the same errors, 0.2, 0.2, 0.6 and 0.0, what is the RMSE?

   <details><summary>Answer</summary>

   Squares: 0.04, 0.04, 0.36, 0. Sum 0.44, average 0.11, square root ≈ 0.33. It's higher than the MAE (0.25) because the 0.6 error is squared.

   </details>

4. <!-- q: mcq id="a0c13c38" -->
   Which test options evaluate a classifier on data it was not trained on? (choose all that apply)

   - [ ] Use training set
   - [x] Supplied test set
   - [x] Cross-validation
   - [x] Percentage split

   <details><summary>Answer</summary>

   Supplied test set, cross-validation and percentage split. "Use training set" tests on the training data itself.

   </details>

5. <!-- q: open id="1d273b8d" -->
   In the course paper, the multilayer perceptron had a kappa of 0.9144 with "use training set" and 0.045 with 10-fold cross-validation. The paper concludes that "use training set" performs better. What's wrong with that conclusion?

   <details><summary>Answer</summary>

   "Use training set" tests the classifier on the same examples it learned from, so it measures how well it memorised them, not how well it handles new data. The MLP overfitted: it memorised the 927 training examples (0.91) but did almost no better than chance on unseen data (0.045). Cross-validation tests on data each model hasn't seen, so its numbers are the honest ones. The right conclusion is that the MLP overfits badly and all four classifiers perform poorly on this dataset.

   </details>

## Before moving on
<!-- bite: f901ffc1-3e82-4fdf-b10e-26b96b119fba -->

You're done when you can draw the supervised classification process with its four test options, compute kappa, MAE and RMSE by hand, and explain why the paper's training-set results can't be trusted.

Recap: the process runs problem → data → preprocessing → training set → classifier selection → training → evaluation → tune or finish. Test options are use training set, supplied test set, cross-validation and percentage split; only the last three test on unseen data. Kappa removes chance agreement; MAE and RMSE measure probability errors; ROC area summarises separation. In the course paper, the MLP's kappa fell from 0.91 on training data to 0.045 under cross-validation: overfitting, not good performance.

That completes the classical ML section, and the SSG 518 pattern-recognition topics (the whole course is mapped week by week in the [[artificial-intelligence/index|Artificial Intelligence]] subject index). Next, [[machine-learning/04-model-evaluation/01-evaluation-metrics-1|Evaluation Metrics 1]] takes the measures you met here, and the confusion matrix behind them, much further.

## Related
<!-- bite: b97dd7dd-6e7f-41a0-bc9e-8f22fbad3681 -->

- [[machine-learning/04-model-evaluation/05-validation-and-tuning|Validation and Tuning]]: cross-validation and tuning in depth.
- [[machine-learning/04-model-evaluation/04-overfitting-and-regularization|Overfitting and Regularization]]: what went wrong for the MLP, and how to prevent it.

## About this lesson
<!-- bite: eb9afe05-fcc8-402d-bbd1-86402258801b -->

**Level:** intermediate. Lesson 24 of the classical ML section, part 2 of 2 on parametric and non-parametric classifiers. It covers the process of supervised classification, the four test options, kappa, MAE, RMSE and ROC area with worked numbers, and a critical reading of the course paper's results.

**Source:** Y. Kumar and G. Sahoo, *Analysis of Parametric & Non Parametric Classifiers for Classification Technique using WEKA*, International Journal of Information Technology and Computer Science, 2012 (figure 2, sections III and IV, and table 1), the paper SSG 518 uses for weeks 8–9. The paper's figures are quoted as published; the reading of its results as overfitting is this lesson's, not the paper's. The worked kappa, MAE and RMSE examples are computed and asserted by `scripts/diagrams/ml_pattern_recognition.py`.
