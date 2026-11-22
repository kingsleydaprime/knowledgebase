---
id: d9e1f26e-ab36-4302-a7eb-52d6ed7bf5e3
---

# Decision Trees 1: The Tree, Entropy and Information Gain

A decision tree is a non-parametric supervised learning algorithm, which is utilized for both classification and regression tasks. It has a hierarchical tree structure which consists of a root node, branches, internal nodes and leaf nodes. They learn a hierarchy of if/else questions leading to a decision.

KNN makes decisions using distance. A decision tree uses a different idea: it asks questions about the features, one after the other.

## Before you start
<!-- bite: f448c51b-02eb-4bf7-a2f4-198f48d40e39 -->

You should know what classification is ([[machine-learning/01-foundations-of-ml/01-what-is-ml-and-types|What ML Is]]). You need logarithms in base 2: log₂(0.5) = −1, and your calculator does the rest.

After this lesson you will be able to:

- name the parts of a decision tree;
- say what ID3, C4.5 and CART use to choose a split;
- calculate entropy and information gain for one attribute.

## Parts of a decision tree
<!-- bite: aa548a9d-5174-48b4-97fa-39c57d49c168 -->

The tree branches out into different possibilities based on features in the data:

1. **Root Node**: Starting point representing the whole dataset.
2. **Branches**: Lines connecting nodes showing the flow from one decision to another.
3. **Internal Node**: Points where decisions are made based on data features.
4. **Leaf Node**: Endpoints of the tree where the final decision or prediction is made. It is also known as a terminal node.

## Types of Decision Trees
<!-- bite: a6a5b6a9-3e9d-4056-af41-bafa115c8ce5 -->

| Type | How it works |
| --- | --- |
| **ID3** (Iterative Dichotomizer 3) | This algorithm leverages entropy and information gain as metrics to evaluate candidate splits. **(This is the one we will be using for now)** |
| **C4.5** | It can use information gain or gain ratio to evaluate split points within the decision trees. |
| **CART** (Classification and Regression Trees) | This algorithm typically utilizes Gini impurity to identify the ideal attributes to split on. |

> **Note:** Gini Impurity measures how often a randomly chosen data point is misclassified. When evaluating Gini Impurity, a lower value is more ideal.

## How to Choose the Best Attribute at Each Node
<!-- bite: 2a4ebcef-0c47-496f-a894-8e45afce9ab4 -->

There are multiple ways to select the best attribute at each node:

- Entropy and Information Gain
- Gini Impurity

## Entropy and Information Gain
<!-- bite: 9cd438b8-7369-43d1-9c62-168ab0b3be90 -->

When building a decision tree, the big question is: which attribute should we ask about first? Entropy and information gain help us answer this.

**Entropy** is a concept that stems from information theory which measures the impurity of the sample values. Mathematically represented as:

$$
Entropy(S) = -\sum_{c} P_c \log_2 (P_c)
$$

where:

- **S** – The data set that entropy is calculated
- **C** – represents the classes in set S
- **P\_c** – The proportion of data points that belong to class C to the number of total data in set, S

> **Note:** If P\_c = 1 or 0, the entropy = 0. If P\_c = 0.5, the value of entropy is the highest possible entropy you can get for that set.

> **Note:** Entropy values can fall between 0 and 1 (when there are two classes). If all samples in data set, S, belong to one class, then entropy will equal zero (0). To select the best feature to split on and find the optimal decision tree, the attribute with the smallest amount of entropy should be used. This means the smallest entropy left after the split, which is the same as the highest information gain.

**Information Gain** is the difference in entropy before and after a split on a given attribute.

> **Note:** The attribute with the highest information gain will produce the best split as it's doing the best job at classifying the training data according to its target classification.

Mathematical representation:

$$
IG(S, a) = Entropy(S) - \sum_{v} \frac{|S_v|}{|S|} Entropy(S_v)
$$

where:

- **a** – specific attribute or class label
- **S** – the data set (all the data before the split)
- **S\_v** – the part of S that has value v for attribute a
- **|S\_v|/|S|** – The proportion of values in S\_v, to the number of values in the data set S

## Check your understanding
<!-- bite: ed352f81-72af-4ed9-bff2-b55c880c3556 -->

Try each one before you open the answer.

1. A set has 4 Yes and 4 No. What is its entropy? What if it has 8 Yes and 0 No?

   <details><summary>Answer</summary>

   4 Yes and 4 No: P = 0.5 for each class, so entropy is 1, the highest for two classes. 8 Yes and 0 No: the set is pure, so entropy is 0.

   </details>

2. A set S has entropy 1. An attribute splits it into two halves, each with entropy 0.5. What is the information gain?

   <details><summary>Answer</summary>

   IG = 1 − [(½ × 0.5) + (½ × 0.5)] = 1 − 0.5 = 0.5.

   </details>

3. Which decision tree algorithm uses Gini impurity?

   <details><summary>Answer</summary>

   CART (Classification and Regression Trees). ID3 uses entropy and information gain; C4.5 uses information gain or gain ratio.

   </details>

## Before moving on
<!-- bite: 6aa6b979-14d5-47c2-a8d4-4cf74d18e5f3 -->

A decision tree is a hierarchy of if/else questions. Entropy measures how mixed a set is, and information gain is how much the entropy drops after a split. The attribute with the highest information gain is the best split.

**Next:** [[machine-learning/03-classical-ml/06-decision-trees-2|Decision Trees 2]]. Now we use these two formulas to build a whole tree by hand, on the Play Tennis data.

## About this lesson
<!-- bite: 6cd8087e-24e4-4803-a0ad-7f63cbafdd97 -->

**Level:** Intermediate. **Covers:** the parts of a decision tree, ID3, C4.5 and CART, entropy and information gain. Part 1 of 4 on decision trees. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
