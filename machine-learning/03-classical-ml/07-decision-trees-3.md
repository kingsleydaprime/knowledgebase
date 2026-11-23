---
id: ba98dc34-d8c0-4def-8a76-8e7de6b41a77
---

# Decision Trees 3: Play Tennis, Growing the Branches

Growing a branch means repeating the root-node steps, using only that branch's days.

## Before you start
<!-- bite: 7e7543b9-8514-4ccd-b0d3-071b42269603 -->

Finish [[machine-learning/03-classical-ml/06-decision-trees-2|Decision Trees 2]] first: you need its root node (Outlook) and the entropy of 0.97095 for a 2-and-3 split.

After this lesson you will be able to:

- repeat ID3 on a branch using only that branch's rows;
- stop when every leaf is pure;
- draw the final tree and read a prediction from it.

## What growing the branches means
<!-- bite: f969644c-fd8f-4ed8-9a7e-4328078a639d -->

This lesson finishes the Play Tennis tree. Sunny and Rain do not have a final answer yet, so we repeat the same steps for each of them, using only the days in that branch.

Next: the Sunny branch, then the Rain branch.

## Step 2: Sunny branch
<!-- bite: c60b70b5-1805-4bee-8b86-b44c31054b64 -->

We no longer use Outlook, because every day here is Sunny.

| Day | Temp | Humidity | Wind | Play Tennis |
| --- | --- | --- | --- | --- |
| 1 | Hot | High | Weak | No |
| 2 | Hot | High | Strong | No |
| 8 | Mild | High | Weak | No |
| 9 | Cool | Normal | Weak | Yes |
| 11 | Mild | Normal | Strong | Yes |

There are 2 Yes and 3 No, so

$$
E (\text{Play Tennis}) = - \left[(\frac{2}{5} \log_2 \left(\frac{2}{5}\right)) + (\frac{3}{5} \log_2 \left(\frac{3}{5}\right))\right] = 0.97095
$$

Now we find the IG for each attribute.

## Sunny branch: Temp
<!-- bite: 738714a2-288a-483e-bd57-a9a4dfd92bf9 -->

Hot: D1, D2 are both No, so

$$
E (\text{Hot}) = 0
$$

Mild: D8 is No, D11 is Yes, so

$$
E (\text{Mild}) = 1
$$

Cool: D9 is Yes, so

$$
E (\text{Cool}) = 0
$$

$$
\text{IG} (\text{Temp}) = 0.97095 - \left[\left(\frac{2}{5} \times 0\right) + \left(\frac{2}{5} \times 1\right) + \left(\frac{1}{5} \times 0\right)\right] = 0.97095 - 0.4 = 0.57095
$$

## Sunny branch: Humidity
<!-- bite: 241c5cf5-3919-460e-ad37-a746b0daf297 -->

High: D1, D2, D8 are all No, so

$$
E (\text{High}) = 0
$$

Normal: D9, D11 are both Yes, so

$$
E (\text{Normal}) = 0
$$

$$
\text{IG} (\text{Humidity}) = 0.97095 - \left[\left(\frac{3}{5} \times 0\right) + \left(\frac{2}{5} \times 0\right)\right] = 0.97095
$$

## Sunny branch: Wind
<!-- bite: 39c0a647-a92a-4d9c-a235-2dd80b4875be -->

Weak: D1 is No, D8 is No, D9 is Yes, so

$$
E (\text{Weak}) = - \left[(\frac{1}{3} \log_2 \left(\frac{1}{3}\right)) + (\frac{2}{3} \log_2 \left(\frac{2}{3}\right))\right] = 0.9183
$$

Strong: D2 is No, D11 is Yes, so

$$
E (\text{Strong}) = 1
$$

$$
\text{IG} (\text{Wind}) = 0.97095 - \left[\left(\frac{3}{5} \times 0.9183\right) + \left(\frac{2}{5} \times 1\right)\right] = 0.97095 - 0.95098 = 0.01997
$$

| Attribute | Information Gain |
| --- | --- |
| Temp | 0.57095 |
| **Humidity** | **0.97095** (highest) |
| Wind | 0.01997 |

Since Humidity has the highest IG, it becomes the attribute we use to split at this node.

## Sunny branch: the winner
<!-- bite: 476e31d9-bd3a-4c18-bef5-3e5c2bda1e24 -->

**\[Sunny / Humidity\]** node splits to: High → **No**, Normal → **Yes**

Both branches are pure (all No or all Yes), so they become leaf nodes and we stop here.

## Step 3: Rain branch
<!-- bite: ea9c821a-3943-4142-a1cd-312f18dbc924 -->

We do the same for Rain.

| Day | Temp | Humidity | Wind | Play Tennis |
| --- | --- | --- | --- | --- |
| 4 | Mild | High | Weak | Yes |
| 5 | Cool | Normal | Weak | Yes |
| 6 | Cool | Normal | Strong | No |
| 10 | Mild | Normal | Weak | Yes |
| 14 | Mild | High | Strong | No |

There are 3 Yes and 2 No, so

$$
E (\text{Play Tennis}) = - \left[(\frac{3}{5} \log_2 \left(\frac{3}{5}\right)) + (\frac{2}{5} \log_2 \left(\frac{2}{5}\right))\right] = 0.97095
$$

## Rain branch: Temperature
<!-- bite: 92dbf3c5-626d-4da4-ac63-c7357a366b22 -->

There is no Hot day in this branch.

Mild: D4, D10 are Yes, D14 is No, so

$$
E (\text{Mild}) = 0.9183
$$

Cool: D5 is Yes, D6 is No, so

$$
E (\text{Cool}) = 1
$$

$$
\text{IG} (\text{Temp}) = 0.97095 - \left[\left(\frac{3}{5} \times 0.9183\right) + \left(\frac{2}{5} \times 1\right)\right] = 0.97095 - 0.95098 = 0.01997
$$

## Rain branch: Humidity
<!-- bite: d61f63be-a28c-4b5e-881c-1e742ba659d4 -->

High: D4 is Yes, D14 is No, so

$$
E (\text{High}) = 1
$$

Normal: D5, D10 are Yes, D6 is No, so

$$
E (\text{Normal}) = 0.9183
$$

$$
\text{IG} (\text{Humidity}) = 0.97095 - \left[\left(\frac{2}{5} \times 1\right) + \left(\frac{3}{5} \times 0.9183\right)\right] = 0.97095 - 0.95098 = 0.01997
$$

## Rain branch: Wind
<!-- bite: 2b6ccad3-ce56-446f-8b54-91c53b360e38 -->

Weak: D4, D5, D10 are all Yes, so

$$
E (\text{Weak}) = 0
$$

Strong: D6, D14 are both No, so

$$
E (\text{Strong}) = 0
$$

$$
\text{IG} (\text{Wind}) = 0.97095 - \left[\left(\frac{3}{5} \times 0\right) + \left(\frac{2}{5} \times 0\right)\right] = 0.97095
$$

| Attribute | Information Gain |
| --- | --- |
| Temp | 0.01997 |
| Humidity | 0.01997 |
| **Wind** | **0.97095** (highest) |

Wind has the highest IG, so we split on it.

## Rain branch: the winner
<!-- bite: 4f57bf45-d66c-4e9d-aa5a-ddbe6d5c838b -->

**\[Rain / Wind\]** node splits to: Strong → **No**, Weak → **Yes**

Both branches are pure, so they become leaf nodes.

## The final decision tree
<!-- bite: 0e90d6d0-122c-4001-88b3-25ff24e8e699 -->

Every branch now ends in a leaf node (a final answer), so the tree is complete. That gives us our decision tree diagram:

- **Outlook** (root node) \[9+, 5−\]
  - Sunny (2+, 3−) → **Humidity**
    - High \[0+, 3−\] → **No**
    - Normal \[2+, 0−\] → **Yes**
  - Overcast \[4+, 0−\] → **Yes**
  - Rain (3+, 2−) → **Wind**
    - Strong \[0+, 2−\] → **No**
    - Weak \[3+, 0−\] → **Yes**

The numbers in brackets count the Yes days (+) and No days (−) at each node. A leaf node is pure when one of the two numbers is 0.

## Check your understanding
<!-- bite: 0d11b373-e4cf-4b99-a6cb-87c0a520aa74 -->

Try each one before you open the answer.

1. <!-- q: mcq id="79d3081f" -->
   Using the final tree, predict Play Tennis for: Outlook = Rain, Temp = Hot, Humidity = High, Wind = Weak.

   - [x] Yes
   - [ ] No

   <details><summary>Answer</summary>

   Yes. Outlook = Rain sends us to the Wind node. Wind = Weak gives Yes. (Temp and Humidity are never asked on this path.)

   </details>

2. <!-- q: gap id="5f1b1fe3" answers="humidity;wind" -->
   Fill in the gaps. The Sunny branch splits on ___ and the Rain branch splits on ___.

   <details><summary>Answer</summary>

   Humidity, then Wind. Each had a gain of 0.97095 in its branch, far higher than the other attributes.

   </details>

3. <!-- q: mcq id="5122fa1e" -->
   Predict Play Tennis for: Outlook = Sunny, Temp = Cool, Humidity = High, Wind = Weak.

   - [ ] Yes
   - [x] No

   <details><summary>Answer</summary>

   No. Sunny sends us to the Humidity node, and High gives No.

   </details>

4. <!-- q: open id="68bc13bd" -->
   In the Sunny branch, why do we no longer use Outlook?

   <details><summary>Answer</summary>

   Every day in that branch is already Sunny, so asking about Outlook again gives no information.

   </details>

5. <!-- q: open id="d76c4d56" -->
   In the Rain branch, Temp and Humidity both had a gain of 0.01997. Why didn't the tie matter?

   <details><summary>Answer</summary>

   Wind had a gain of 0.97095, far higher than both, so Wind was chosen.

   </details>

## Practice — independent task
<!-- bite: a25aa3f3-c5e3-4b18-9477-2655d1119d8d -->

Past question 1(b) in the [[machine-learning/ssg-535-question-bank|SSG 535 question bank]] gives a 10-day Buy Laptop table. Build its tree on paper with ID3, the same way as in this lesson and the last one. **Done when** you have the gain of all four attributes at the root, a test on every impure branch, and a tree that classifies all 10 days correctly. Then open the solution.

## Before moving on
<!-- bite: f40ae0b3-5563-4565-82f5-a974b17ab174 -->

ID3 repeats on each impure branch with only that branch's rows, and stops when every leaf is pure. Play Tennis ends as Outlook at the root, Humidity under Sunny and Wind under Rain.

**Next:** [[machine-learning/03-classical-ml/08-decision-trees-4|Decision Trees 4]]. We built this tree with entropy. Next is the other way of choosing the best attribute: Gini impurity.

## About this lesson
<!-- bite: 90c435bf-99be-4138-a090-09e63af194e7 -->

**Level:** Intermediate. **Covers:** the Sunny and Rain branches of the Play Tennis tree and the final decision tree. Part 3 of 6 on decision trees. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
