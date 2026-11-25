---
id: c6321b49-d9eb-437b-a48b-21e96bf9f150
---

# Pattern Recognition 1: What It Is and the Steps

Pattern recognition is the ability to classify patterns in data and in the environment: finding similarities, trends and regularities, and putting things into categories.

## Before you start
<!-- bite: 5d4efb29-f24a-44f3-b5a6-217c7a41a202 -->

You should have met at least one classifier in this section, such as [[machine-learning/03-classical-ml/01-k-nearest-neighbours-1|K-Nearest Neighbours 1]], and the idea of grouping without labels from [[machine-learning/03-classical-ml/17-clustering-1|Clustering 1]].

After this lesson you will be able to:

1. define pattern recognition, and name the two jobs it involves: classification and clustering;
2. list the four features a pattern-recognition system should have;
3. explain the training set and the testing set, and the difference between data and information;
4. list the five steps of building a pattern-recognition system, in order.

## What pattern recognition is
<!-- bite: 67f7852e-f886-4a38-963c-c43956eae475 -->

Your class notes define it like this: pattern recognition is the ability to classify patterns in data and the environment, and it's a fundamental cognitive skill in humans.

You do it all day. You recognise a friend's face across a busy market, a song from its first two notes, your mother's handwriting on an envelope, the sound of your own phone's ringtone in a room full of phones. In each case your brain finds a **pattern**, a set of regularities, and matches it to something it already knows.

Your notes add that it involves finding similarities, trends and regularities, whether recognising a familiar face or training an algorithm to sort emails. Pattern recognition in computing is getting a machine to do the same.

## The kid version
<!-- bite: 318b2674-1a82-41cb-bd9c-d5bd405d9516 -->

Imagine sorting a big pile of fruit at the market. You don't measure anything; you just look. Round and orange: orange. Long and yellow: banana. Small, green and hard: unripe mango. You've seen so many fruits that you know the pattern of each. Pattern recognition is teaching a computer to look at something it's never seen before and say "that's a mango", the way you do.

**Where the analogy stops working.** You see the whole fruit at once and just *know*. A computer only gets numbers, such as a weight, a colour reading and a size, so someone has to decide which numbers to give it. That choice, the features, decides how well it can ever do.

## How a machine sees a pattern
<!-- bite: c8e8bddd-bc14-4e30-b4e3-d72b17742c58 -->

Your notes say that in a typical pattern-recognition application, the raw data is processed and converted into a form that a machine can use.

That form is a list of numbers called **features**. Your notes define them as the characteristics or attributes of the data that are relevant for pattern recognition. For a mango, the features might be its sweetness, its firmness and its weight. For an email, they might be how many times each word appears. For a face, they might be the distances between the eyes, nose and mouth.

Once every example is a list of features, a pattern is just a region where similar lists cluster together. Ripe mangoes all have high sweetness and low firmness; unripe ones the opposite.

## Classification and clustering
<!-- bite: bafea075-41bc-42c5-bee6-d527f333ca56 -->

Your notes say pattern recognition involves two jobs:

1. **Classification**: the process of putting items into categories. The categories are known in advance, and the system learns them from labelled examples. "Is this mango ripe or unripe?" This is supervised learning.
2. **Clustering**: the system groups similar things together *without any labels*. Nobody tells it the categories; it finds the groups itself. "Here are 1,000 customers; which ones behave alike?" This is unsupervised learning, the subject of [[machine-learning/03-classical-ml/17-clustering-1|Clustering 1]].

Most of this lesson and the next is about classification, because that's where the course spends its time.

## What a pattern-recognition system should do
<!-- bite: dceafbe7-e408-4731-8656-50f4a5929dcd -->

Your notes list four features a good pattern-recognition system should possess:

1. It should recognise **familiar patterns** quickly and accurately.
2. It should recognise and classify **unfamiliar objects**, things it hasn't seen in training.
3. It should accurately recognise shapes and objects from **different angles**.
4. It should identify patterns and objects even when they are **partly hidden**.

Notice how hard the last three are. A face from the side, a mango half-covered by a leaf, a word in a new handwriting: humans manage these easily. A system that only works on exactly the examples it was trained on is useless, which is why testing on *new* data matters so much.

## Training and learning
<!-- bite: f7b8ff1d-afe8-404d-ba51-75090c547113 -->

Your notes describe learning as the phenomenon through which a system gets trained and becomes adaptable to give accurate results. To make that happen, the whole dataset is divided into two parts:

1. **The training set** is used to build the model. It's the set of images or data used to train the system, usually about 80% of the dataset.
2. **The testing set** is used to test the system. It's the data used to check whether the system produces the correct output after being trained.

The two must be kept apart. If you test on the same examples you trained on, you only learn whether the system *memorised* them, not whether it can handle new ones. (Lesson 24 shows a published paper that made exactly this mistake.) [[machine-learning/02-working-with-data/03-train-val-test-splits|Train, Validation and Test Splits]] covers the split in depth.

## Data and information
<!-- bite: 7da05fe2-c575-4b56-9d93-ed3868a737f1 -->

Your notes also separate two words people often mix up:

1. **Data** is raw facts and figures collected from observations or measurements. "Mango 17: sweetness 8, firmness 3."
2. **Information** is data that has been processed and organised in a meaningful way, so that it can be understood and used for decision making. "Mango 17 is ripe, sell it today."

A pattern-recognition system is a machine for turning data into information.

## The steps of pattern recognition
<!-- bite: 79aa6b43-8971-411f-9b85-52db23dfd026 -->

Your notes give the steps for building a pattern-recognition system, from start to termination:

![The steps in pattern recognition: data collection, feature choice, model choice, training the classifier, then evaluating the classifier, after which the process terminates.](../images/pr-steps.svg)

## The five steps, one by one
<!-- bite: 3b2efc1c-2784-48d7-958f-5d95bf997534 -->

Here's what each step in that picture means:

1. **Data collection.** Gather the data you'll use to train and test your system.
2. **Feature choice.** Decide which characteristics of the data are relevant: sweetness and firmness, not the mango's serial number.
3. **Model choice.** Select the pattern-recognition model or algorithm. It depends on the nature of the data and the problem at hand.
4. **Training the classifier.** Train the chosen model on a labelled dataset. During training, it learns to identify patterns in the data and make predictions based on the features.
5. **Evaluation.** Assess the trained system on a separate dataset that the model has not seen before.

## Why the order matters
<!-- bite: d14315e5-edd7-4fc2-9601-1391a9be74a4 -->

Each step depends on the one before. You can't choose features until you've seen the data. You can't choose a model until you know what your features look like: a few numeric features suit a distance-based model like KNN; thousands of word counts suit naive Bayes. And evaluation only means something if it uses data the training step never saw.

When evaluation shows the system isn't good enough, you go back: collect more data, pick better features or try another model. The next lesson adds the phases a system goes through once it's built, and the three families of model you choose between in step 3.

## Terms used in this lesson
<!-- bite: dd58d346-a3d4-4ad0-91c3-f05772f6377f -->

1. **Pattern recognition**: This is the ability to classify patterns in data and the environment, by finding similarities, trends and regularities.
2. **Pattern**: This is a regularity in data, such as the combination of high sweetness and low firmness that marks a ripe mango.
3. **Feature**: This is a characteristic or attribute of the data that is relevant for recognising patterns, such as sweetness.
4. **Classification**: This is putting items into known categories, learned from labelled examples.
5. **Clustering**: This is grouping similar items together without any labels.

## More terms used in this lesson
<!-- bite: 17ed0080-ef8b-4099-85ab-13d1a5fb9331 -->

6. **Training set**: This is the part of the data used to build the model, usually about 80%.
7. **Testing set**: This is the part of the data held back to check the trained model on examples it hasn't seen.
8. **Data**: This is raw facts and figures from observations or measurements.
9. **Information**: This is data that has been processed and organised so it can be understood and used for decisions.

## Common pitfalls and traps
<!-- bite: 003c6c42-736f-4715-b100-5ad0aadac8d5 -->

- **Testing on the training data.** It only shows the model memorised its examples. Always test on data it hasn't seen.
- **Mixing up classification and clustering.** Classification has labels and known categories; clustering has neither.
- **Skipping feature choice.** The best model can't recognise a pattern in features that don't carry it.

## Check your understanding
<!-- bite: 58690e76-ef78-4722-80e0-2b071a63edca -->

Try each one before you open the answer.

1. <!-- q: gap id="dd59070f" answers="classification;clustering" -->
   Pattern recognition involves two jobs: ___, putting items into known categories, and ___, grouping similar things without labels.

   <details><summary>Answer</summary>

   Classification and clustering.

   </details>

2. <!-- q: mcq id="2ff9f413" -->
   Which of these are features your notes say a pattern-recognition system should have? (choose all that apply)

   - [x] Recognise familiar patterns quickly and accurately
   - [x] Recognise objects from different angles
   - [x] Identify objects even when they are partly hidden
   - [ ] Only work on the exact examples it was trained on
   - [x] Classify unfamiliar objects

   <details><summary>Answer</summary>

   All except "only work on the exact examples it was trained on", which is the opposite of what a good system should do.

   </details>

3. <!-- q: exact id="e6e87045" answer="800" -->
   A dataset has 1,000 labelled images. Using the usual split from your notes, how many go into the training set?

   <details><summary>Answer</summary>

   About 80%, so 800. The other 200 form the testing set.

   </details>

4. <!-- q: mcq id="2ea30036" -->
   Put the steps of pattern recognition in order.

   - [ ] Model choice, data collection, feature choice, evaluation, training
   - [x] Data collection, feature choice, model choice, training, evaluation
   - [ ] Feature choice, data collection, training, model choice, evaluation
   - [ ] Training, evaluation, data collection, feature choice, model choice

   <details><summary>Answer</summary>

   Data collection, feature choice, model choice, training the classifier, evaluation.

   </details>

5. <!-- q: open id="5e311332" -->
   Explain the difference between data and information, with an example from a pattern-recognition system.

   <details><summary>Answer</summary>

   Data is raw facts and figures from observation or measurement, such as "email 52 contains the word 'free' 4 times and 'meeting' 0 times". Information is data processed and organised so it can be used for a decision, such as "email 52 is spam, move it to the junk folder". A pattern-recognition system takes in data and produces information.

   </details>

## Before moving on
<!-- bite: 4326aafd-1752-4352-8181-9880c05c105c -->

You're done when you can define pattern recognition, name its two jobs and the four features of a good system, explain the training and testing sets, and list the five steps in order.

Recap: pattern recognition classifies patterns in data by finding similarities and regularities. It involves classification (known categories, labels) and clustering (no labels). A good system recognises familiar and unfamiliar objects, from any angle, even partly hidden. The data is split into a training set (about 80%) and a testing set. The steps are data collection, feature choice, model choice, training and evaluation.

Next, [[machine-learning/03-classical-ml/22-pattern-recognition-2|Pattern Recognition 2]] covers the phases a system goes through, and the three families of model: statistical, structural and neural.

## Related
<!-- bite: 8497bbcb-11dc-4031-8505-077ffb28c9d4 -->

- [[machine-learning/01-foundations-of-ml/01-what-is-ml-and-types|What Is ML, and Its Types]]: supervised and unsupervised learning.
- [[artificial-intelligence/index|Artificial Intelligence]]: SSG 518, the course these lessons come from.

## About this lesson
<!-- bite: ad0f9918-8445-4a69-912b-b6efdbbca8c9 -->

**Level:** introductory. Lesson 21 of the classical ML section, part 1 of 2 on pattern recognition. It covers the definition, classification and clustering, the features of a good system, training and testing sets, data and information, and the steps of pattern recognition.

**Source:** University of Lagos SSG 518 (Artificial Intelligence II) class notes, *Pattern Recognition* (07/02/26), weeks 5–6 of the course outline. The diagram is drawn by `scripts/diagrams/ml_pattern_recognition.py`.
