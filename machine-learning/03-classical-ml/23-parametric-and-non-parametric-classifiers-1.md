---
id: 55841861-753f-4e7e-b730-81d682331b3b
---

# Parametric and Non-Parametric Classifiers 1: Assuming a Shape or Not

A parametric classifier assumes a fixed shape for each class's data; a non-parametric one lets the data decide the shape.

## Before you start
<!-- bite: d451536e-2250-4b25-912a-b9153c028c7c -->

Read [[machine-learning/03-classical-ml/22-pattern-recognition-2|Pattern Recognition 2]] first, especially the nearest-mean classifier and the disadvantages of statistical models. It helps to know the normal distribution from [[machine-learning/00-foundations/03-mathematics/index|Mathematics]].

After this lesson you will be able to:

1. draw the course's tree of classifiers and place parametric and non-parametric classifiers on it;
2. define parametric and non-parametric classifiers, in the course's words and the standard statistical way;
3. fit a Gaussian to a class (mean and variance) and estimate a density with a Parzen window, by hand;
4. show with an example how a wrong shape assumption makes a parametric classifier fail.

## What parametric and non-parametric mean
<!-- bite: b8ea9f78-957c-4157-a695-02da884adf9a -->

Many classifiers work by asking, for a new example: how likely is this value under class A, and how likely under class B? Then they pick the more likely class. To answer, they need each class's **probability density**: a curve showing which values are common in that class and which are rare.

There are two ways to get that curve:

1. **Assume its shape**, usually a bell curve (Gaussian), and just estimate a few numbers that pin it down, such as the mean and the variance. That's **parametric**.
2. **Don't assume a shape.** Build the curve directly from the training points: lots of points nearby means high density. That's **non-parametric**.

The paper your course uses puts it simply: a parametric classifier is based on the statistical probability distribution of each class; non-parametric classifiers are used when the density function is unknown, and they estimate it.

## The kid version
<!-- bite: ec498567-62a1-4f5a-bddb-99b86f0abaa5 -->

You want to describe where children in your class live. One way: "most of them live around the school, spread out roughly evenly in all directions", which needs only two facts, the centre and how spread out. Another way: mark every child's house on a map. The first is quick and tidy, but if half the class actually lives in one estate to the north and half in another to the south, "around the school" is badly wrong: almost nobody lives right at the school. The map with every house is bigger, but it can't be wrong about the shape.

**Where the analogy stops working.** A map with every house is perfect for the children you have. A classifier must also guess about *new* children, and with very few houses marked, the map can be patchy and noisy. That's where the simple description can win.

## The course's tree of classifiers
<!-- bite: 5474df9e-6395-43aa-9fe8-71235fe1a718 -->

Your notes and the course paper (Kumar and Sahoo, 2012) arrange classifiers in this tree:

![The course tree of classifiers: classification splits into supervised and unsupervised; supervised splits into probabilistic and geometric; probabilistic is density based, which splits into parametric (Bayesian, multivariate Gaussian, MLC, naive Bayes, decision tree, SVM, minimal distance) and non-parametric (KNN, kernel density or Parzen, logistic regression, MLP, neural network); unsupervised lists ART, ISODATA, fuzzy C-means, K-means and genetic algorithms.](../images/pr-classifier-tree.svg)

## Reading the tree
<!-- bite: ea9f0a2b-ca15-45a9-94af-bd16ec0a1a6a -->

Read the tree from the top:

1. **Classification** splits into **supervised** (learning from labelled examples, "with a supervisor") and **unsupervised** (learning from observations without labels, which is clustering).
2. Supervised splits into **probabilistic based** (using probability densities) and **geometric based** (using distances and boundaries).
3. Probabilistic classifiers are **density based**, and those split into **parametric** and **non-parametric**.

## The two lists in the tree
<!-- bite: 101e9f9c-7456-4bdc-ab61-bffb515d041d -->

The tree's lists, as the course gives them, which you should know for the exam:

1. **Parametric:** Bayesian, multivariate Gaussian, MLC (maximum likelihood classifier), naive Bayes, decision tree, SVM, classification tree, minimal distance classifier.
2. **Non-parametric:** K-nearest neighbour, kernel density estimation, logistic regression, multilayer perceptron, Parzen, artificial neural network, Euclidean distance, neural network.
3. **Unsupervised:** ART 1, ART 2, ART 3, ART Star, fuzzy ART, ISODATA, fuzzy C-means, bootstrapping local, K-means, genetic algorithm.

## The standard definition
<!-- bite: e78200fd-9ca5-4379-be34-2a45ffe52d2b -->

Statisticians define the two words more precisely, and it's worth knowing because it explains *why* a classifier is one or the other:

1. **A parametric model** has a **fixed number of parameters**, decided before seeing the data. However much data you give it, the model stays the same size. A Gaussian class model has 2 numbers per feature (mean and variance), whether you train on 10 points or 10 million.
2. **A non-parametric model** has no fixed form; its size **grows with the data**. KNN keeps every training point; a Parzen window estimate is built from every point.

By this standard definition, naive Bayes with Gaussians, the multivariate Gaussian and minimal-distance classifiers are parametric, and KNN, Parzen windows and kernel density estimation are non-parametric, exactly as in the course's tree.

## Where the course's tree disagrees
<!-- bite: f4d77e35-3c9e-4192-9a69-ffbd9ba7a288 -->

A few entries in the course's tree go against the standard definition:

1. **Logistic regression** and a **multilayer perceptron** of fixed size have a fixed number of weights, so statisticians call them *parametric*. The tree lists them as non-parametric.
2. **Decision trees** grow more branches as data grows, and **kernel SVMs** keep a subset of training points (the support vectors), so both are usually called *non-parametric*. The tree lists them as parametric.

For the SSG 518 exam, give the course's lists. In a viva or a job interview, say the standard definition and note the difference. Knowing why they disagree shows you understand the idea, not just the list.

## Parametric in action: fit a Gaussian
<!-- bite: 3a42dc17-046c-4fa5-8e79-92b75602b5a7 -->

Here's a one-feature problem. Class A has values 1, 2, 2, 9, 10. Class B has 5, 5, 6, 6, 7. A new example has value **7.5**. Which class?

A parametric classifier assumes each class is a Gaussian (bell curve) and estimates two parameters per class:

**Class A.** Mean = (1 + 2 + 2 + 9 + 10) / 5 = **4.8**. Variance = the average squared distance from the mean = (3.8² + 2.8² + 2.8² + 4.2² + 5.2²) / 5 = 74.8 / 5 = **14.96**.

**Class B.** Mean = (5 + 5 + 6 + 6 + 7) / 5 = **5.8**. Variance = (0.8² + 0.8² + 0.2² + 0.2² + 1.2²) / 5 = 2.8 / 5 = **0.56**.

## The Gaussian's verdict
<!-- bite: 2c962c7f-e4c2-4bc1-96f4-6746d6476989 -->

The Gaussian density, stated in words first: it's highest at the mean, and falls away the further you go, faster when the variance is small.

$$p(x) = \frac{1}{\sqrt{2\pi\sigma^2}} \, e^{-(x-\mu)^2 / 2\sigma^2}$$

where $\mu$ is the mean and $\sigma^2$ the variance. Put in $x = 7.5$:

1. Class A ($\mu = 4.8$, $\sigma^2 = 14.96$): $p \approx 0.081$.
2. Class B ($\mu = 5.8$, $\sigma^2 = 0.56$): $p \approx 0.040$.

Class A's density is higher, so the parametric classifier says **A**.

Now look at the data again. The nearest A value to 7.5 is 9, which is 1.5 away. The nearest B value is 7, only 0.5 away. Does "A" look right to you?

## Non-parametric in action: a Parzen window
<!-- bite: 0cc01e2d-1ceb-4e4a-bed0-629fe7307b0e -->

A **Parzen window** estimate makes no assumption about shape. To estimate the density at $x$, put a window of fixed width around $x$, count the training points of each class inside it, and divide by (number of points × window width).

Use a window from 6.5 to 8.5 (1 either side of 7.5, so width 2):

1. Class A: no points inside (A's points are 1, 2, 2, 9, 10). Density = 0 / (5 × 2) = **0**.
2. Class B: one point inside, the 7. Density = 1 / (5 × 2) = **0.1**.

The Parzen window says **B**. So does KNN with $k = 3$: the three nearest points to 7.5 are 7, 6 and 6, all class B.

## Why they disagree
<!-- bite: 365ba4f3-9c67-4744-9f50-5629f8fb54ac -->

Here's the picture:

![One feature from 0 to 11. Class A points at 1, 2, 2, 9 and 10 sit in two clumps; class B points at 5, 5, 6, 6 and 7 sit in one. The Gaussian fitted to A is a wide hump centred on 4.8, covering the empty middle; the Gaussian fitted to B is a narrow peak at 5.8. At the new point 7.5 the wide A curve is higher, but the only nearby data point, 7, is B.](../images/pr-parametric-vs-parzen.svg)

Class A isn't one bell. It's two clumps, one at 1–2 and one at 9–10, with *nothing* in between. A single Gaussian can't represent that, so it draws one wide hump right across the empty middle, and claims A is fairly likely at 7.5, where A has no data at all. That's exactly the disadvantage from lesson 22: performance drops when the assumptions about the distribution are wrong.

The Parzen window and KNN look only at the points actually near 7.5, so they get it right.

## Terms used in this lesson
<!-- bite: 4dcd3c96-759e-4599-bdd5-ebf896ec58b0 -->

1. **Probability density**: This is a curve showing how common each value is in a class. High density means values like that are common.
2. **Parametric classifier**: This is a classifier that assumes each class's density has a fixed shape, such as a Gaussian, and learns a fixed number of parameters that describe it.
3. **Non-parametric classifier**: This is a classifier that assumes no fixed shape and estimates the density from the training points themselves, so its size grows with the data.
4. **Gaussian**: This is also known as the **normal distribution** or bell curve. It's described by two parameters, the mean and the variance.

## More terms used in this lesson
<!-- bite: 5ef328f5-aaf5-4531-874c-ca4d9caf25b1 -->

5. **Variance ($\sigma^2$)**: This is the average squared distance of the values from their mean. It measures spread.
6. **Parzen window**: This is also known as **kernel density estimation** with a box-shaped kernel. It estimates density at a point by counting training points inside a fixed window around it.
7. **MLC (maximum likelihood classifier)**: The letters stand for those words. It's a parametric classifier that assigns an example to the class under whose fitted distribution it is most likely.

## Common pitfalls and traps
<!-- bite: 1e8e7f1d-3d4d-4a9b-8261-d656c4170539 -->

- **Thinking non-parametric means "no parameters at all".** It means no *fixed* number of parameters; the model's size grows with the data. A Parzen window still has a width you choose.
- **Mixing up the course's lists and the standard definition.** For the exam, use the course's tree. Know where they disagree.
- **Thinking parametric is always worse.** When the assumed shape is right, parametric classifiers need far less data and are more reliable. They fail only when the shape is wrong.

## Check your understanding
<!-- bite: a6d8cec5-a2ea-48d2-968a-a4e100c50204 -->

Try each one before you open the answer.

1. <!-- q: mcq id="c104c87e" -->
   In the course's tree of classifiers, which are listed as parametric? (choose all that apply)

   - [x] Naive Bayes
   - [x] Multivariate Gaussian
   - [ ] K-nearest neighbour
   - [x] Minimal distance classifier
   - [ ] Parzen

   <details><summary>Answer</summary>

   Naive Bayes, multivariate Gaussian and the minimal distance classifier. KNN and Parzen are non-parametric.

   </details>

2. <!-- q: exact id="0894d622" answer="2.66667" sigfigs="3" accept="8/3" -->
   A class has the values 2, 4 and 6. A parametric classifier fits a Gaussian, using the average squared distance from the mean as the variance. What is the variance?

   <details><summary>Answer</summary>

   The mean is 4. The squared distances are 4, 0 and 4, which add to 8. Divided by 3 values: 8/3 ≈ 2.67.

   </details>

3. <!-- q: exact id="bc4a0e45" answer="0.25" accept="1/4" -->
   A class has six training values: 3, 4, 4, 8, 9, 10. Using a Parzen window from 3 to 5 (1 either side of 4, width 2), estimate the density at 4 as (points in window) / (number of points × width).

   <details><summary>Answer</summary>

   Points in [3, 5]: 3, 4 and 4, so 3 points. Density = 3 / (6 × 2) = 3/12 = 0.25.

   </details>

4. <!-- q: mcq id="67a7f9e4" -->
   By the standard statistical definition, what makes a model non-parametric?

   - [ ] It has no settings at all
   - [x] Its size (number of parameters) grows with the amount of training data
   - [ ] It is always a neural network
   - [ ] It assumes every class is a Gaussian

   <details><summary>Answer</summary>

   Its size grows with the data, as KNN keeps every training point. A parametric model has a fixed number of parameters however much data it sees.

   </details>

5. <!-- q: open id="b709fbd0" -->
   In this lesson's example, the Gaussian classifier labelled 7.5 as class A, while the Parzen window and KNN said class B. Explain why the Gaussian got it wrong.

   <details><summary>Answer</summary>

   Class A's data is in two separate clumps (1–2 and 9–10) with nothing in between, but a single Gaussian can only make one bell shape. It fits a wide hump centred on 4.8 that spreads right across the empty middle, so it gives A a fairly high density at 7.5 even though no A point is near there. The assumption about the shape of A's distribution was wrong. The non-parametric methods only look at the points actually near 7.5, where the closest is a B.

   </details>

## Before moving on
<!-- bite: f70cc489-0bba-4918-809e-7a8dd218cd21 -->

You're done when you can draw the course's classifier tree, give both definitions and where they disagree, fit a Gaussian and a Parzen window by hand, and explain why they can disagree.

Recap: parametric classifiers assume a fixed shape (usually a Gaussian) and learn a few parameters; non-parametric ones estimate the density from the points, so they grow with the data. The course's tree splits supervised, probabilistic, density-based classifiers into the two lists; a few of its entries differ from the standard definition. On the two-clump example, the Gaussian says A at 7.5 while the Parzen window and KNN correctly say B, because A isn't one bell.

Next, [[machine-learning/03-classical-ml/24-parametric-and-non-parametric-classifiers-2|Parametric and Non-Parametric Classifiers 2]] covers the process of building and testing a supervised classifier, the measures used to compare classifiers, and what the course paper's own results really show.

## Related
<!-- bite: e74476d3-092f-4093-8e58-e549d9b88798 -->

- [[machine-learning/03-classical-ml/01-k-nearest-neighbours-1|K-Nearest Neighbours 1]]: the most common non-parametric classifier.
- [[machine-learning/03-classical-ml/11-naive-bayes-1|Naive Bayes 1]]: Gaussian naive Bayes, a parametric classifier.

## About this lesson
<!-- bite: 3f5ceb9f-e866-4d79-99a8-3e8bc3cafea6 -->

**Level:** intermediate. Lesson 23 of the classical ML section, part 1 of 2 on parametric and non-parametric classifiers. It covers the course's classifier tree, both definitions, a Gaussian fit and a Parzen window by hand, and an example where they disagree.

**Source:** University of Lagos SSG 518 class notes (the classification tree, 07/02/26) and the course paper, Y. Kumar and G. Sahoo, *Analysis of Parametric & Non Parametric Classifiers for Classification Technique using WEKA*, International Journal of Information Technology and Computer Science, 2012 (figure 1 and section I). The standard definition and the notes on where the paper's lists differ from it are added. Every number is computed and asserted by `scripts/diagrams/ml_pattern_recognition.py`.
