# 03 — Classical ML

Classical machine learning is the set of models that came before deep learning: models that predict from the closest examples, ask questions in a tree, use probability, or draw a line through the data. They are still the right tool for most spreadsheet-style data, they train in seconds, and you can usually explain why they made a prediction.

Start at lesson 1 and go in order. Big topics are split into numbered parts (Decision Trees 1 to 6), and each part builds on the one before.

## Predicting from the closest examples

1. [[machine-learning/03-classical-ml/01-k-nearest-neighbours-1|01 — K-Nearest Neighbours 1]] — how KNN predicts from the closest training points, and your first model on the Iris dataset
2. [[machine-learning/03-classical-ml/02-k-nearest-neighbours-2|02 — K-Nearest Neighbours 2]] — predicting numbers with KNN, and instance-based (lazy) learning
3. [[machine-learning/03-classical-ml/03-distance-measures|03 — Distance Measures]] — the ways of measuring how close two points are, worked by hand
4. [[machine-learning/03-classical-ml/04-learning-vector-quantization|04 — Learning Vector Quantization]] — keeping a few typical points instead of the whole training set

## Asking questions: decision trees

5. [[machine-learning/03-classical-ml/05-decision-trees-1|05 — Decision Trees 1]] — the parts of a tree, and how to measure how mixed a group is
6. [[machine-learning/03-classical-ml/06-decision-trees-2|06 — Decision Trees 2]] — Play Tennis by hand: choosing the first question
7. [[machine-learning/03-classical-ml/07-decision-trees-3|07 — Decision Trees 3]] — Play Tennis by hand: growing the branches to the final tree
8. [[machine-learning/03-classical-ml/08-decision-trees-4|08 — Decision Trees 4]] — the second way of choosing a question (Gini), on the Weekend Decision data
9. [[machine-learning/03-classical-ml/09-decision-trees-5|09 — Decision Trees 5]] — both ways side by side on the same small table
10. [[machine-learning/03-classical-ml/10-decision-trees-6|10 — Decision Trees 6]] — stopping a tree from memorising, and many trees working together

## Using probability

11. [[machine-learning/03-classical-ml/11-naive-bayes-1|11 — Naive Bayes 1]] — fast classifiers that look at each feature on its own
12. [[machine-learning/03-classical-ml/12-naive-bayes-2|12 — Naive Bayes 2]] — multinomial naive Bayes: a spam filter built by hand from word counts
13. [[machine-learning/03-classical-ml/13-bayesian-networks-1|13 — Bayesian Networks 1]] — a graph of how variables affect each other, and Bayes theorem
14. [[machine-learning/03-classical-ml/14-bayesian-networks-2|14 — Bayesian Networks 2]] — working out real probabilities from the network

## Drawing lines and curves

15. [[machine-learning/03-classical-ml/15-linear-models-and-regression|15 — Linear Models and Regression]] — predicting from a weighted sum of the features
16. [[machine-learning/03-classical-ml/16-kernel-machines|16 — Kernel Machines]] — handling data a straight line can't separate

## Finding structure without labels

17. [[machine-learning/03-classical-ml/17-clustering-1|17 — Clustering 1]] — grouping similar data points, and the five kinds of clustering
18. [[machine-learning/03-classical-ml/18-clustering-2|18 — Clustering 2]] — choosing the number of groups and checking they are good
19. [[machine-learning/03-classical-ml/19-dimensionality-reduction-pca|19 — Dimensionality Reduction with PCA]] — shrinking many columns down to a few

## Learning rules

20. [[machine-learning/03-classical-ml/20-inductive-logic-programming|20 — Inductive Logic Programming]] — learning readable if-then rules from examples

When you finish, try the past paper in the [[machine-learning/ssg-535-question-bank|SSG 535 question bank]].

## Related

- [[machine-learning/04-model-evaluation/index|Model Evaluation]] — how to judge these models
- [[machine-learning/05-deep-learning/index|Deep Learning]] — when to reach past classical ML
- [[machine-learning/00-foundations/03-mathematics/index|Mathematics]] — the maths underneath

## About this course

Lessons 1–11, 13–18 and 20 follow the SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester, in the order they were taught. Lesson 12 follows the class slides on multinomial naive Bayes (added 2026-11-25). Lesson 19 and the ensembles, regularization and scikit-learn SVM parts come from the roadmap.sh machine-learning roadmap. Rebuilt from the class notes on 2026-11-22.
