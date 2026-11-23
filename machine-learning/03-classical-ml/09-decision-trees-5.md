---
id: 1231abaa-7146-4b2e-a3d1-25251d7cd225
---

# Decision Trees 5: Entropy, Information Gain and Gini on the Same Data

Entropy and the Gini Index both pick the best split; here we use both on the same data.

## Before you start
<!-- bite: 8d3ccad9-f0eb-4f2c-a3f3-39b2e19876f7 -->

You should be able to calculate information gain ([[machine-learning/03-classical-ml/06-decision-trees-2|Decision Trees 2]]) and the Gini Index ([[machine-learning/03-classical-ml/08-decision-trees-4|Decision Trees 4]]).

After this lesson you will be able to:

- choose the root attribute with information gain and with the Gini Index;
- say which direction (highest or smallest) wins for each;
- explain why the two methods usually agree.

## What we are comparing
<!-- bite: df75be08-27b9-43b6-ad72-a5134047b2f4 -->

This lesson uses both methods on the same small dataset, so we can compare them. This is how to compute Entropy, Information Gain and Gini Index.

Next: the data, then entropy and information gain, then the Gini Index.

## The a1 and a2 data
<!-- bite: ece2b9d9-be7f-4e88-a93e-d04763504262 -->

| Instance | a1 | a2 | Target Class |
| --- | --- | --- | --- |
| 1 | T | T | + |
| 2 | T | T | + |
| 3 | T | F | − |
| 4 | F | F | + |
| 5 | F | T | − |
| 6 | F | T | − |
| 7 | F | F | − |
| 8 | T | F | + |
| 9 | F | T | − |

## Entropy and information gain on a1 and a2
<!-- bite: 67834a42-d3f2-44b3-9f2b-d3f43df784aa -->

$$
Entropy = -\sum_{i=1}^{n} P_i \log_2 (P_i)
$$

**Target class:** (+) = 4, (−) = 5, total = 9.

$$
\text{Entropy} (S) = - \left[(\frac{4}{9} \log_2 \left(\frac{4}{9}\right)) + (\frac{5}{9} \log_2 \left(\frac{5}{9}\right))\right] = 0.9911
$$

## Information gain of a1
<!-- bite: d28a6ea5-2ec0-4b1c-bce3-ffae60382a6d -->

| a1 | T | F | Total |
| --- | --- | --- | --- |
| + | 3 | 1 | 4 |
| − | 1 | 4 | 5 |
| Total | 4 | 5 | 9 |

$$
\text{Entropy} (a_{1}, \text{True}) = - \left[(\frac{3}{4} \log_2 \left(\frac{3}{4}\right)) + (\frac{1}{4} \log_2 \left(\frac{1}{4}\right))\right] = 0.8113
$$

$$
\text{Entropy} (a_{1}, \text{False}) = - \left[(\frac{1}{5} \log_2 \left(\frac{1}{5}\right)) + (\frac{4}{5} \log_2 \left(\frac{4}{5}\right))\right] = 0.7219
$$

$$
\text{Information Gain for a1} = 0.9911 - \left[\left(\frac{4}{9} \times 0.8113\right) + \left(\frac{5}{9} \times 0.7219\right)\right] = 0.2295
$$

## Information gain of a2
<!-- bite: 9a97a51d-c810-4367-90fe-2d225e7405c7 -->

| a2 | T | F | Total |
| --- | --- | --- | --- |
| + | 2 | 2 | 4 |
| − | 3 | 2 | 5 |
| Total | 5 | 4 | 9 |

$$
\text{Entropy} (a_{2}, \text{True}) = - \left[(\frac{2}{5} \log_2 \left(\frac{2}{5}\right)) + (\frac{3}{5} \log_2 \left(\frac{3}{5}\right))\right] = 0.97095
$$

$$
\text{Entropy} (a_{2}, \text{False}) = - \left[(\frac{2}{4} \log_2 \left(\frac{2}{4}\right)) + (\frac{2}{4} \log_2 \left(\frac{2}{4}\right))\right] = 1
$$

$$
\text{Information Gain for a2} = 0.9911 - \left[\left(\frac{5}{9} \times 0.97095\right) + \left(\frac{4}{9} \times 1\right)\right] = 0.00724
$$

| Attribute | Information Gain |
| --- | --- |
| **a1** | **0.2295** (highest, root node) |
| a2 | 0.00724 |

So a1 has an information gain of 0.2295, which is the highest information gain.

## The Gini Index on a1 and a2
<!-- bite: 3631e796-b9e9-480d-a90c-4b21063bf3cf -->

$$
G = 1 - \sum_{i=1}^{n} (P_i)^2
$$

## Gini Index of a1
<!-- bite: 6dbac135-86ee-4ff6-b38c-a5c0d3ac51b5 -->

$$
\text{Gini} (T) = 1 - \left[\left(\frac{3}{4}\right)^2 + \left(\frac{1}{4}\right)^2\right] = 0.375
$$

$$
\text{Gini} (F) = 1 - \left[\left(\frac{1}{5}\right)^2 + \left(\frac{4}{5}\right)^2\right] = 0.32
$$

$$
\text{Weighted Average of a1} = \left(\frac{4}{9} \times 0.375\right) + \left(\frac{5}{9} \times 0.32\right) = 0.3444
$$

## Gini Index of a2
<!-- bite: af2d089f-3936-4cc3-83ad-29d1e47b6797 -->

$$
\text{Gini} (T) = 1 - \left[\left(\frac{2}{5}\right)^2 + \left(\frac{3}{5}\right)^2\right] = 0.48
$$

$$
\text{Gini} (F) = 1 - \left[\left(\frac{2}{4}\right)^2 + \left(\frac{2}{4}\right)^2\right] = 0.5
$$

$$
\text{Weighted Average of a2} = \left(\frac{5}{9} \times 0.48\right) + \left(\frac{4}{9} \times 0.5\right) = 0.4889
$$

| Attribute | Gini Index |
| --- | --- |
| **a1** | **0.3444** (smallest, root node) |
| a2 | 0.4889 |

So a1 is the best split attribute for the Gini Index too.

> **Note:**
>
> - Higher information gain produces the better split
> - Smaller the Gini Index produces the better split

Both methods picked the same attribute here. They are two different ways of measuring the same thing: how pure the groups are after the split.

## Check your understanding
<!-- bite: b070d3c2-c83a-46cc-afe4-21cebf03a72d -->

Try each one before you open the answer.

1. <!-- q: mcq id="3e61b7ae" -->
   Before you calculate: in the table, a1 = T has 3 + and 1 −. a2 = T has 2 + and 3 −. Which attribute do you expect to split better?

   - [x] a1
   - [ ] a2

   <details><summary>Answer</summary>

   a1. Its groups are much less mixed (3 to 1 and 1 to 4) than a2's (2 to 3 and 2 to 2). Both methods confirm it.

   </details>

2. <!-- q: gap id="50e08c68" answers="information gain;gini index|gini" -->
   Fill in the gaps. Higher ___ produces the better split, and smaller ___ produces the better split.

   <details><summary>Answer</summary>

   Higher information gain; smaller Gini Index.

   </details>

3. <!-- q: exact id="c6593080" answer="0.32" accept="8/25" tolerance="0.001" -->
   a1 = F has 1 + and 4 −. What is its Gini impurity?

   <details><summary>Answer</summary>

   0.32. G = 1 − [(1/5)² + (4/5)²] = 1 − (0.04 + 0.64) = 0.32.

   </details>

4. <!-- q: open id="d43777a2" -->
   Entropy and the Gini Index picked the same attribute here. Why do the two methods usually agree?

   <details><summary>Answer</summary>

   They are two different ways of measuring the same thing: how pure the groups are after the split. A split that makes purer groups scores well on both.

   </details>

## Before moving on
<!-- bite: 661d52cb-1466-4365-a68a-ec27ab9e7a27 -->

Information gain and the Gini Index are two different ways of measuring the same thing: how pure the groups are after the split. Here both picked a1.

**Next:** [[machine-learning/03-classical-ml/10-decision-trees-6|Decision Trees 6]]. A tree grown until every leaf is pure fits the training data too closely. Next: how to stop that, and how many trees together do even better.

## About this lesson
<!-- bite: 549fb2c9-1f94-4838-8341-d515b610292b -->

**Level:** Intermediate. **Covers:** entropy, information gain and the Gini Index calculated on one dataset and compared. Part 5 of 6 on decision trees. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
