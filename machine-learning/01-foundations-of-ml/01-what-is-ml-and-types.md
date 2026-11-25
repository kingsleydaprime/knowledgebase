---
id: 1a40de71-3a12-44be-9dad-207800bb85c9
---

# What ML Is, and the Types of Learning

Machine learning is about extracting knowledge from data, and there are three main types of it.

## Before you start
<!-- bite: 7051d644-480e-4c52-afab-bee332513b6a -->

You don't need any machine learning yet. If you can read a table of rows and columns, you are ready.

After this lesson you will be able to:

- say what machine learning is in one sentence, and name its three types;
- tell a classification problem from a regression problem by looking at the output;
- point at the samples and the features in any dataset.

## What machine learning is
<!-- bite: 48abf378-a45e-48a1-ae1f-ad8afed4adc5 -->

Machine learning is about extracting knowledge from data. It is also known as predictive analytics or statistical learning. ML teaches systems to think and understand like humans by learning from the data.

### Types of Machine Learning

1. Supervised
2. Unsupervised
3. Reinforcement

The next bites take them one at a time: supervised first, then unsupervised, then reinforcement.

## Supervised Learning
<!-- bite: 8cf34540-5ac1-4166-8ceb-e37c9d91ce41 -->

Supervised learning is ML that learns from input/output pairs. This is used to predict a certain outcome from a given input. It trains a model on labeled data to predict and classify new, unseen data.

Supervised learning is used whenever we want to predict a certain outcome from a given input. The machine learns from these input/output pairs, which comprise our training set. Our goal is to make accurate predictions for new, never-before-seen data.

> **NB:** The user provides the algorithm with pairs of inputs and desired outputs and the algorithm finds a way to produce the desired output given the input.

## Supervised learning examples: spam and zip codes
<!-- bite: 8a519944-4222-44e5-92b1-ce12ccc73515 -->

Each example below names the input, the output, and the data the machine learns from.

**1. Identifying spams in emails**

- **Inputs:** large number of email content/features
- **Output:** Whether any emails are spam
- **Goal:** When given a new email, the algorithm will then produce a prediction as to whether the new email is spam.

**2. Identifying the zip code from handwritten digits on an envelope**

- **Inputs:** scan of the handwriting
- **Outputs:** The actual digits in the zip code
- **Data set:** Collection of many envelopes

## Supervised learning examples: tumours and fraud
<!-- bite: e6600306-6028-49fd-8327-8ed1eb2fa4f5 -->

Two more, in the same shape: input, output, dataset.

**3. Determining whether a tumor is benign based on a medical image**

- **Input:** the image
- **Output:** The tumor is benign
- **Dataset:** Database of medical images

**4. Detecting fraudulent activity in credit card transactions**

- **Inputs:** Credit card transaction
- **Output:** Fraudulent or not
- **Dataset:** Storing all transactions

## How supervised learning works
<!-- bite: 0b89bb84-a81a-4b63-b2bb-b8dbbbdd33f2 -->

These are the steps from my notes, in order.

1. Collect a dataset
2. Split the dataset
3. Train the data
4. Build the model
5. Test set
6. Evaluate

## Types of supervised learning
<!-- bite: a8c0b5d2-91af-4596-a575-1989e84d788e -->

There are two major types of supervised machine learning which are:

1. Classification
2. Regression

The difference is the output: a class label for classification, a number for regression. The next two bites take each one.

## Classification
<!-- bite: 3245de0e-e4a1-4520-ac95-665b367b4d03 -->

*The output is a categorical value, e.g. spam vs not spam.*

The goal is to predict a class label, which is a choice from a predefined list of possibilities.

Classification is sometimes separated into:

- **Binary classification:** the special case of distinguishing between exactly two classes. Example is classifying emails either as spam or not spam or trying to answer a yes or no answer.
- **Multiclass classification:** the classification between more than 2 classes. Example is the iris dataset.

## Regression
<!-- bite: c2743efe-6719-45ea-bba1-217afd756357 -->

*The output is a continuous variable, e.g. predicting stock prices.*

The goal is to predict a continuous number or a floating-point number in programming terms (or real number in mathematical terms).

## Unsupervised Learning
<!-- bite: 0eaef7fd-26a9-4d85-a21f-2f788a94c93e -->

In supervised learning we gave the algorithm the answers (outputs). In unsupervised learning we do not.

This uses only input data (known) and no known output data is given to the algorithm.

In other words: here is data, figure out what is going on!

### Examples

- Identifying the topics in a set of blog posts
- Segmenting customers into groups with similar preferences
- Detecting the abnormal access patterns to a website

## Reinforcement learning
<!-- bite: 48fb103e-9911-403a-a252-351fa341a03f -->

Reinforcement learning is learning from reward. My class notes name it as the third type but don't go into it, so here it is briefly.

No fixed dataset of answers at all — an agent takes actions in an environment and receives a reward signal, adjusting behavior to maximize cumulative reward over time. Fundamentally different from supervised and unsupervised. Game-playing (AlphaGo), robotics, and — notably — the RLHF step that makes LLMs follow instructions. Covered in [[machine-learning/08-other-architectures/03-reinforcement-learning|reinforcement learning]].

## Self-supervised learning
<!-- bite: 8f4fa880-ffdf-4657-9f04-1233c821551f -->

Self-supervised learning is learning where the labels come from the data itself. It is not one of the three types in my notes, but it comes up a lot outside class. It is a hugely important modern middle ground: the model generates its *own* labels from unlabeled data by hiding part of the input and predicting it. **This is how LLMs are pretrained** — "predict the next token" is a label the text provides for free ([[ai-engineering/02-how-llms-work/index|how LLMs work]]). It unlocked training on internet-scale unlabeled data. **Semi-supervised** learning (a little labeled data + a lot of unlabeled) is the related cousin.

## Samples and Features
<!-- bite: e6f1a3f7-7b4e-4ef9-a116-a6fc270ad6b4 -->

Every dataset in ML, supervised or unsupervised, is made of these two things, so we need these words before we go further.

1. **Sample** (data point): Each entity or row.
2. **Features**: Columns, the properties that describe these entities.

## How Machine Learning Works
<!-- bite: 2851566a-84aa-47da-b05e-d5c974753131 -->

Now that we know the types of ML and what a dataset is made of, here are the steps of a typical ML project.

1. Problem statement
2. Data collection
3. Data cleaning
4. Feature engineering
5. Explorative Data Analysis
6. Data Modeling
7. Model evaluation
8. Optimization and Deployment

## Check your understanding
<!-- bite: 21235145-d5f9-4c98-b8fa-7a0c2a4bffbe -->

Try each one before you open the answer.

1. <!-- q: mcq id="4f22f857" -->
   A bank wants to predict tomorrow's exchange rate from today's data. Which type of supervised learning is that?

   - [ ] Classification
   - [x] Regression

   <details><summary>Answer</summary>

   Regression. The output is a continuous number (a floating-point number), not a choice from a list of classes.

   </details>

2. <!-- q: mcq id="b6cb98ac" -->
   A shop gives you all its customers' purchases, with no labels, and asks you to find groups of similar customers. Which type of learning is this?

   - [ ] Supervised learning
   - [x] Unsupervised learning
   - [ ] Reinforcement learning

   <details><summary>Answer</summary>

   Unsupervised learning. We have only the inputs and no known outputs, so it is "here is data, figure out what is going on".

   </details>

3. <!-- q: gap id="f272b40b" answers="binary;multiclass|multi-class" -->
   Fill in the gaps. Sorting emails into spam or not spam picks between exactly two classes, so it is ___ classification. Sorting iris flowers into three species is ___ classification.

   <details><summary>Answer</summary>

   Binary, then multiclass. Binary classification is the special case of distinguishing between exactly two classes. Multiclass classification is between more than two classes, like the iris dataset.

   </details>

4. <!-- q: exact id="9ada9ff0" answer="50" accept="fifty" -->
   A table holds 50 students, and for each one it has Age, Study Hours and GPA. How many samples does the dataset have?

   <details><summary>Answer</summary>

   50. Each student is one row, and each row is a sample. Age, Study Hours and GPA are the 3 features (the columns).

   </details>

5. <!-- q: mcq id="54425739" -->
   Which of these are supervised learning? Choose all that apply.

   - [x] Detecting fraud in credit card transactions, from past transactions marked fraud or not
   - [ ] Finding the topics in a set of blog posts
   - [x] Reading the zip code from a scan of handwritten digits
   - [ ] An agent learning to play a game from a reward score

   <details><summary>Answer</summary>

   Fraud and zip codes. Both learn from input/output pairs: we have the answers for past examples. Finding topics has no outputs, so it is unsupervised. Learning from a reward is reinforcement learning.

   </details>

6. <!-- q: open id="27fe333d" -->
   In your own words, what is the difference between supervised and unsupervised learning? Give one example of each.

   <details><summary>Answer</summary>

   Supervised learning learns from input/output pairs: we give the algorithm the inputs and the desired outputs, and it learns to produce the output for new inputs. For example, spam detection from emails marked spam or not spam. Unsupervised learning gets only the inputs, with no known outputs, and has to find the structure itself. For example, grouping customers with similar preferences.

   </details>

## Before moving on
<!-- bite: c64df41e-252f-4bc0-9d41-6cbf13fbe185 -->

Machine learning extracts knowledge from data. Supervised learning learns from input/output pairs and is either classification (a class label) or regression (a number). Unsupervised learning gets only inputs. Reinforcement learning learns from reward instead of answers. Every dataset is samples (rows) and features (columns).

**Next:** [[machine-learning/01-foundations-of-ml/02-the-ml-toolkit|The ML Toolkit]]. Before the first algorithm, we need the Python tools that every example uses.

## Related
<!-- bite: 4064b29b-b67b-468f-8fc7-a8a24836cc0f -->

- [[machine-learning/03-classical-ml/01-k-nearest-neighbours-1|K-Nearest Neighbours 1]] — the first supervised algorithm
- [[machine-learning/03-classical-ml/17-clustering-1|Clustering 1]] — the main unsupervised technique
- [[machine-learning/04-model-evaluation/04-overfitting-and-regularization|Overfitting]] — what "generalize" means

## About this lesson
<!-- bite: d8db04ef-4326-41c6-bba8-ce1d676ec9e4 -->

**Level:** Beginner. **Covers:** what machine learning is, supervised, unsupervised and reinforcement learning, classification and regression, samples and features, and the steps of an ML project. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
