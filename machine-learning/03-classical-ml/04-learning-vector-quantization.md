---
id: ea867fb4-d8c4-4a7b-b41c-b91f45bd87a9
---

# Learning Vector Quantization (LVQ)

LVQ classifies a point by its nearest prototype, a few points that stand for each class.

## Before you start
<!-- bite: c7dbf8ad-31c6-40a3-a327-75990331b32d -->

You should know KNN ([[machine-learning/03-classical-ml/02-k-nearest-neighbours-2|K-Nearest Neighbours 2]]) and Euclidean distance ([[machine-learning/03-classical-ml/03-distance-measures|Distance Measures]]).

After this lesson you will be able to:

- explain what a prototype is and how LVQ trains its prototypes;
- move a prototype closer or away by hand with the update rule;
- compare LVQ with KNN.

## What LVQ is
<!-- bite: ea96d165-f7e4-48c9-9517-3d0f5d487aa2 -->

Learning Vector Quantization, or LVQ, was introduced by Teuvo Kohonen. It is a supervised method for classification, and it sits between two things we already know. Like KNN, it classifies a new point by finding the closest stored point. But KNN stores the whole training set, which uses a lot of memory and makes predictions slow (see [[machine-learning/03-classical-ml/02-k-nearest-neighbours-2|instance-based learning]]). LVQ instead keeps only a small set of **prototypes** (also called codebook vectors). Each prototype is a point with a class label, and it stands for a whole group of training points. Like K-Means, the prototypes move around during training, but unlike K-Means, LVQ uses the class labels to decide how they move.

Next: how LVQ trains its prototypes, step by step.

## How LVQ works
<!-- bite: 135bf0d7-880b-43f1-8269-5efe3818c8a6 -->

1. Choose how many prototypes each class gets, and start them somewhere, for example at randomly chosen training points of that class.
2. Take one training point x and find the prototype w that is closest to it (using Euclidean distance).
3. If w has the **same class** as x, move w **closer** to x.
4. If w has a **different class** from x, move w **away** from x.
5. Make the learning rate smaller after every pass, and repeat for many passes through the data.
6. To predict a new point, find its nearest prototype and give the point that prototype's class.

## The LVQ update rule
<!-- bite: 25c9d324-a21b-44af-8457-15e4b4ee38c0 -->

Step 3 and step 4 move a prototype. In maths, the two moves are:

$$
w \leftarrow w + \alpha \, (x - w) \qquad \text{(same class: move closer)}
$$

$$
w \leftarrow w - \alpha \, (x - w) \qquad \text{(different class: move away)}
$$

Here α (alpha) is the **learning rate**, a small number such as 0.1 that controls how big each move is.

## LVQ worked example
<!-- bite: 0ac82ca5-2f2b-4b6d-aa3b-3fba4d7c2631 -->

Let the nearest prototype be w = (2, 2) and the training point be x = (4, 3). Let α = 0.1. First, x − w = (2, 1).

If w and x have the same class, w moves closer:

$$
w_{new} = (2, 2) + 0.1 \times (2, 1) = (2.2,\ 2.1)
$$

If they have different classes, w moves away:

$$
w_{new} = (2, 2) - 0.1 \times (2, 1) = (1.8,\ 1.9)
$$

## Strengths and weaknesses
<!-- bite: 22c79b9a-9c00-433c-a579-dfcecc6dcc49 -->

- **Strengths:** it needs little memory (only the prototypes are stored), predictions are fast, and it is easy to understand because each prototype is a typical example of its class.
- **Weaknesses:** we must choose the number of prototypes and the learning rate, the result depends on where the prototypes start, and it needs numeric features that are scaled (see [[machine-learning/03-classical-ml/03-distance-measures|distance measures]] and [[machine-learning/02-working-with-data/02-feature-engineering-and-scaling|feature scaling]]).

**KNN compared with LVQ:** KNN stores every training point and does all the work at prediction time (a lazy learner). LVQ does its work during training and then keeps only a few prototypes, so prediction is much faster.

## Check your understanding
<!-- bite: 3dc9beca-049b-44a2-a96d-7fc6672c1704 -->

Try each one before you open the answer.

1. <!-- q: gap id="cf9996ea" answers="2;3" -->
   Fill in the gaps. w = (1, 1), x = (3, 5), α = 0.5, and they have the same class. w moves to (___, ___).

   <details><summary>Answer</summary>

   x − w = (2, 4). w + 0.5 × (2, 4) = (1, 1) + (1, 2) = (2, 3).

   </details>

2. <!-- q: gap id="78d81a09" answers="0;-1|−1" -->
   Fill in the gaps. Same numbers, but the classes are different. w moves to (___, ___).

   <details><summary>Answer</summary>

   w − 0.5 × (2, 4) = (1, 1) − (1, 2) = (0, −1).

   </details>

3. <!-- q: mcq id="76ab273e" -->
   The nearest prototype has a different class from the training point. What does LVQ do?

   - [ ] Moves the prototype closer to the point
   - [x] Moves the prototype away from the point
   - [ ] Deletes the prototype

   <details><summary>Answer</summary>

   It moves the prototype away. Same class: closer. Different class: away.

   </details>

4. <!-- q: mcq id="d6cc93c6" -->
   How is LVQ different from K-Means?

   - [ ] LVQ doesn't move its points during training
   - [x] LVQ uses the class labels to decide how its prototypes move
   - [ ] LVQ stores the whole training set

   <details><summary>Answer</summary>

   LVQ uses the labels. Both move points around during training, but K-Means has no labels, and LVQ is supervised.

   </details>

5. <!-- q: open id="58f2799e" -->
   Why does LVQ predict faster than KNN?

   <details><summary>Answer</summary>

   KNN compares the new point with every training point. LVQ compares it only with the few prototypes it kept.

   </details>

## Check your understanding: worked problems
<!-- bite: 857a3a93-fbdc-44bb-8ab1-9372b6fb622a -->

Work each one out on paper first, then type your answer.

1. <!-- q: gap id="4746f260" answers="0.5;1" -->
   Fill in the gaps. w = (0, 0), x = (2, 4), α = 0.25, same class. w moves to (___, ___).

   <details><summary>Answer</summary>

   (0.5, 1). x − w = (2, 4), and 0.25 × (2, 4) = (0.5, 1).

   </details>

2. <!-- q: gap id="06bdae75" answers="3.2;3.2" -->
   Fill in the gaps. w = (3, 3), x = (1, 1), α = 0.1, different classes. w moves to (___, ___).

   <details><summary>Answer</summary>

   (3.2, 3.2). x − w = (−2, −2). Moving away: w − 0.1 × (−2, −2) = (3.2, 3.2), further from x.

   </details>

3. <!-- q: gap id="42abdb36" answers="3;2" -->
   Fill in the gaps. w = (4, 2), x = (2, 2), α = 0.5, same class. w moves to (___, ___).

   <details><summary>Answer</summary>

   (3, 2). x − w = (−2, 0), and w + 0.5 × (−2, 0) = (3, 2): halfway to x.

   </details>

4. <!-- q: points id="042e5296" xmin="-1" xmax="4" ymin="0" ymax="6" step="1" snap="0.5" answer="2,3 0,5" labels="same class,different class" tolerance="0.25" ghost="1,4 3,2" -->
   The prototype w = (1, 4) and the training point x = (3, 2) are shown faintly, and α = 0.5. Place where w moves to if they have the same class, then where it moves to if they have different classes.

   <details><summary>Answer</summary>

   x − w = (2, −2). Same class: w + 0.5 × (2, −2) = (2, 3), halfway towards x. Different class: w − 0.5 × (2, −2) = (0, 5), the same distance away from x.

   </details>

## Before moving on
<!-- bite: 559aa7d3-c09f-48d9-be02-372457e79e7c -->

LVQ keeps a few labelled prototypes. In training, the nearest prototype moves closer to a point of its own class and away from a point of another class. To predict, a new point takes the class of its nearest prototype.

**Next:** [[machine-learning/03-classical-ml/05-decision-trees-1|Decision Trees 1]]. KNN and LVQ both decide by distance. Decision trees use a completely different idea: they ask questions.

## About this lesson
<!-- bite: 64011e6d-f3ef-4f22-88f8-dd4439f8e10e -->

**Level:** Intermediate. **Covers:** prototypes, the LVQ training rule, a worked update, and LVQ compared with KNN. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
