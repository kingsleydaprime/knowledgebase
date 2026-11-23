---
id: 21f66c6f-6a9e-4d5b-b349-1d7ad6de7254
---

# Decision Trees 2: Play Tennis, Choosing the Root Node

ID3 builds a decision tree by splitting on the attribute with the highest information gain.

## Before you start
<!-- bite: 1aa03e6c-986c-41b8-8da3-18cc0c848f31 -->

You should be able to calculate entropy and information gain ([[machine-learning/03-classical-ml/05-decision-trees-1|Decision Trees 1]]). Keep a calculator next to you and work each number before you read it.

After this lesson you will be able to:

- calculate the entropy of a whole dataset from its Yes and No counts;
- calculate the information gain of every attribute from its count table;
- choose the root node and say which branches are already finished.

## What we are building
<!-- bite: ae3e09e7-3e11-4760-89e7-97ead816f826 -->

This lesson starts building a whole decision tree by hand with ID3. At every node, we find the information gain of each attribute and split on the one with the highest information gain. Here we do it for the first node, the root.

Next: the data, then the root node, worked one attribute at a time.

## The Play Tennis data
<!-- bite: 4e592bd7-48dd-45ad-b4a3-974b7ed7f479 -->

| Day | Outlook | Temp | Humidity | Wind | Play Tennis |
| --- | --- | --- | --- | --- | --- |
| 1 | Sunny | Hot | High | Weak | No |
| 2 | Sunny | Hot | High | Strong | No |
| 3 | Overcast | Hot | High | Weak | Yes |
| 4 | Rain | Mild | High | Weak | Yes |
| 5 | Rain | Cool | Normal | Weak | Yes |
| 6 | Rain | Cool | Normal | Strong | No |
| 7 | Overcast | Cool | Normal | Strong | Yes |
| 8 | Sunny | Mild | High | Weak | No |
| 9 | Sunny | Cool | Normal | Weak | Yes |
| 10 | Rain | Mild | Normal | Weak | Yes |
| 11 | Sunny | Mild | Normal | Strong | Yes |
| 12 | Overcast | Mild | High | Strong | Yes |
| 13 | Overcast | Hot | Normal | Weak | Yes |
| 14 | Rain | Mild | High | Strong | No |

We will build the decision tree for this data using ID3. At every node, we find the information gain of each attribute and split on the one with the highest information gain.

## Step 1: Choose the root node
<!-- bite: 9dbb87e5-2023-4b1e-9363-384bf28f1f62 -->

We want to decide which attribute to split on for the root node. The attributes are Outlook, Temp, Humidity and Wind, so we find the information gain of all four.

**First, the entropy of the whole dataset.** Out of the 14 days, 9 are Yes and 5 are No.

$$
E (Y) = - \left[(\frac{9}{14} \log_2 \left(\frac{9}{14}\right)) + (\frac{5}{14} \log_2 \left(\frac{5}{14}\right))\right] = 0.94029
$$

## Root node: Outlook
<!-- bite: eae2933e-5d7e-4554-91ae-98de886a8b92 -->

Outlook splits the data into 3 labels:

|  | Sunny | Overcast | Rain | Total |
| --- | --- | --- | --- | --- |
| Yes | 2 | 4 | 3 | 9 |
| No | 3 | 0 | 2 | 5 |
| Total | 5 | 4 | 5 | 14 |

Sunny:

$$
E (\text{Sunny}) = - \left[(\frac{2}{5} \log_2 \left(\frac{2}{5}\right)) + (\frac{3}{5} \log_2 \left(\frac{3}{5}\right))\right] = 0.97095
$$

Overcast: all 4 days are Yes, so P\_c = 1 or 0 and:

$$
E(\text{Overcast}) = 0
$$

Rain:

$$
E (\text{Rain}) = - \left[(\frac{3}{5} \log_2 \left(\frac{3}{5}\right)) + (\frac{2}{5} \log_2 \left(\frac{2}{5}\right))\right] = 0.97095
$$

## Root node: Outlook's information gain
<!-- bite: 1a2ecae7-5ee4-4529-8e33-791e69dfc7ba -->

Now we use the information gain formula. We take the entropy before the split and subtract the entropy after the split. Each part of the split is weighted by how many days it has.

$$
\text{IG} (\text{Outlook}) = E (Y) - \left[(\frac{5}{14} \times E (\text{Sunny})) + (\frac{4}{14} \times E (\text{Overcast})) + (\frac{5}{14} \times E (\text{Rain}))\right]
$$

$$
\text{IG} (\text{Outlook}) = 0.94029 - \left[\left(\frac{5}{14} \times 0.97095\right) + \left(\frac{4}{14} \times 0\right) + \left(\frac{5}{14} \times 0.97095\right)\right]
$$

$$
\text{IG} (\text{Outlook}) = 0.94029 - 0.69354 = 0.2468
$$

## Root node: Temperature
<!-- bite: 04250028-14fc-409e-903f-579321eb8a6e -->

|  | Hot | Mild | Cool | Total |
| --- | --- | --- | --- | --- |
| Yes | 2 | 4 | 3 | 9 |
| No | 2 | 2 | 1 | 5 |
| Total | 4 | 6 | 4 | 14 |

$$
E (\text{Hot}) = - \left[(\frac{2}{4} \log_2 \left(\frac{2}{4}\right)) + (\frac{2}{4} \log_2 \left(\frac{2}{4}\right))\right] = 1
$$

$$
E (\text{Mild}) = - \left[(\frac{4}{6} \log_2 \left(\frac{4}{6}\right)) + (\frac{2}{6} \log_2 \left(\frac{2}{6}\right))\right] = 0.9183
$$

$$
E (\text{Cool}) = - \left[(\frac{3}{4} \log_2 \left(\frac{3}{4}\right)) + (\frac{1}{4} \log_2 \left(\frac{1}{4}\right))\right] = 0.81128
$$

## Root node: Temperature's information gain
<!-- bite: 58a026c1-2e19-4eea-b785-9895804f5c19 -->

Now the information gain for Temperature, using the three entropies from the last bite.

$$
\text{IG} (\text{Temperature}) = 0.94029 - \left[\left(\frac{4}{14} \times 1\right) + \left(\frac{6}{14} \times 0.9183\right) + \left(\frac{4}{14} \times 0.81128\right)\right]
$$

$$
\text{IG} (\text{Temperature}) = 0.94029 - 0.91107 = 0.02922
$$

## Root node: Humidity
<!-- bite: fa26a4e5-a3e1-45a3-8729-9d732972de1c -->

|  | High | Normal | Total |
| --- | --- | --- | --- |
| Yes | 3 | 6 | 9 |
| No | 4 | 1 | 5 |
| Total | 7 | 7 | 14 |

$$
E (\text{High}) = - \left[(\frac{3}{7} \log_2 \left(\frac{3}{7}\right)) + (\frac{4}{7} \log_2 \left(\frac{4}{7}\right))\right] = 0.98523
$$

$$
E (\text{Normal}) = - \left[(\frac{6}{7} \log_2 \left(\frac{6}{7}\right)) + (\frac{1}{7} \log_2 \left(\frac{1}{7}\right))\right] = 0.59167
$$

$$
\text{IG} (\text{Humidity}) = 0.94029 - \left[\left(\frac{7}{14} \times 0.98523\right) + \left(\frac{7}{14} \times 0.59167\right)\right]
$$

$$
\text{IG} (\text{Humidity}) = 0.94029 - 0.78845 = 0.15184
$$

## Root node: Wind
<!-- bite: ddc1c7e0-6a47-4589-b9da-3453d2117945 -->

|  | Weak | Strong | Total |
| --- | --- | --- | --- |
| Yes | 6 | 3 | 9 |
| No | 2 | 3 | 5 |
| Total | 8 | 6 | 14 |

$$
E (\text{Weak}) = - \left[(\frac{6}{8} \log_2 \left(\frac{6}{8}\right)) + (\frac{2}{8} \log_2 \left(\frac{2}{8}\right))\right] = 0.8113
$$

$$
E (\text{Strong}) = - \left[(\frac{3}{6} \log_2 \left(\frac{3}{6}\right)) + (\frac{3}{6} \log_2 \left(\frac{3}{6}\right))\right] = 1
$$

$$
\text{IG} (\text{Wind}) = 0.94029 - \left[\left(\frac{8}{14} \times 0.8113\right) + \left(\frac{6}{14} \times 1\right)\right]
$$

$$
\text{IG} (\text{Wind}) = 0.94029 - 0.89217 = 0.04812
$$

## Root node: picking the winner
<!-- bite: 42de5507-12b1-406d-a688-9107808faf7e -->

Now we pick the one with the highest IG:

| Attribute | Information Gain |
| --- | --- |
| **Outlook** | **0.2468** (highest) |
| Temperature | 0.02922 |
| Humidity | 0.15184 |
| Wind | 0.04812 |

Outlook has the highest information gain, so it is our **root node**.

## The three branches of Outlook
<!-- bite: 732d88f8-48fa-4ece-b1fc-779cbf642eae -->

The root node splits the data into 3 branches:

- **Sunny** (2+, 3−): {D1, D2, D8, D9, D11}
- **Overcast** (4+, 0−): {D3, D7, D12, D13} → **\[Yes\]**
- **Rain** (3+, 2−): {D4, D5, D6, D10, D14}

> **NB:** We already have an answer (leaf node) for Overcast, because all its days are Yes.

Sunny and Rain do not have a final answer yet (they have both Yes and No). So we repeat the same steps for each of them, using only the days in that branch. We start with Sunny.

## Check your understanding
<!-- bite: c97be16f-a4d0-4982-8e62-8a7e002d6af7 -->

Try each one before you open the answer.

1. <!-- q: mcq id="da329657" -->
   Which attribute becomes the root node of the Play Tennis tree?

   - [x] Outlook (IG 0.2468)
   - [ ] Temperature (IG 0.02922)
   - [ ] Humidity (IG 0.15184)
   - [ ] Wind (IG 0.04812)

   <details><summary>Answer</summary>

   Outlook, because it has the highest information gain of the four.

   </details>

2. <!-- q: gap id="8d28f0dc" answers="9;5" -->
   Fill in the gaps. Of the 14 days, ___ are Yes and ___ are No, which gives a dataset entropy of 0.94029.

   <details><summary>Answer</summary>

   9 Yes and 5 No.

   </details>

3. <!-- q: exact id="253a49fa" answer="0" accept="zero" -->
   What is the entropy of the Overcast branch?

   <details><summary>Answer</summary>

   0. All 4 Overcast days are Yes, so the branch is pure. A pure branch becomes a leaf node and needs no more splitting.

   </details>

4. <!-- q: mcq id="0485aeee" -->
   Before reading on, predict: which of Humidity or Wind will give the bigger information gain in the Sunny branch? (Look at the five Sunny days.)

   - [x] Humidity
   - [ ] Wind

   <details><summary>Answer</summary>

   Humidity. In the Sunny branch, High is all No and Normal is all Yes, so both parts are pure and the gain equals the whole entropy, 0.97095. The next lesson works it out.

   </details>

5. <!-- q: open id="3bd8c400" -->
   Temperature has the lowest gain at the root (0.02922). What does a gain that small tell you?

   <details><summary>Answer</summary>

   Splitting on Temperature hardly reduces the entropy: the Hot, Mild and Cool groups are almost as mixed as the whole dataset.

   </details>

## Before moving on
<!-- bite: 2a19c777-f71a-497e-8155-af47d970f7e1 -->

Find the entropy of the whole data, then the weighted entropy after splitting on each attribute. The biggest drop (information gain) wins. For Play Tennis that is Outlook, and Overcast is already a leaf.

**Next:** [[machine-learning/03-classical-ml/07-decision-trees-3|Decision Trees 3]]. Sunny and Rain still have both Yes and No days, so we repeat the same steps for each of them.

## About this lesson
<!-- bite: 7fddff4a-bfd2-417d-976e-737159a12b33 -->

**Level:** Intermediate. **Covers:** the Play Tennis data and the full calculation for the root node with ID3. Part 2 of 6 on decision trees. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
