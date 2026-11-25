---
id: 380b91da-5a66-4022-a351-adc16ce4d7ca
---

# Pattern Recognition 2: Phases and the Three Kinds of Model

A pattern-recognition system goes through four phases (preprocessing, training, testing and deployment), and its model is one of three kinds: statistical, structural or neural.

## Before you start
<!-- bite: d34eae74-077d-4e93-ba10-305c0dac6e16 -->

Read [[machine-learning/03-classical-ml/21-pattern-recognition-1|Pattern Recognition 1]] first. You need features, the training and testing sets, and the five steps. The worked example uses Euclidean distance from [[machine-learning/03-classical-ml/03-distance-measures|Distance Measures]].

After this lesson you will be able to:

1. name and describe the four phases of the pattern-recognition process;
2. describe statistical, structural and neural-network models, with the advantages and disadvantages of each;
3. classify a new example by hand with a minimum-distance (nearest-mean) classifier;
4. choose a kind of model for a described problem.

## What this lesson covers
<!-- bite: bc594927-f673-46ab-a0cd-bc2e5120b7a1 -->

Lesson 21 gave you the steps for *building* a pattern-recognition system. Your notes also describe the **phases** of the process, which follow the system from raw data all the way to being used for real. And in step 3, model choice, there are three broad families of model to choose from.

This lesson covers both, and works one simple statistical model by hand, so the word "model" stops being abstract.

## The kid version
<!-- bite: 769fc459-e1ec-48f5-b861-8480132251f8 -->

Think about three ways to teach a child to recognise a house in a drawing. One: show them hundreds of drawings and let them get a feel for "how house-like" a picture is on average (statistical). Two: give them a rule, "a house is a triangle sitting on top of a square, with a small rectangle for the door" (structural). Three: show them thousands of pictures and let their brain work it out without ever saying a rule (neural). All three work. Each is better for different kinds of picture.

**Where the analogy stops working.** A child mixes all three ways at once without noticing. A computer system is usually built around one of them, and you have to choose which.

## The four phases
<!-- bite: 9f1f67c3-4f6a-4b45-b1e6-e255e0fdfcc5 -->

Your notes list the phases of the pattern-recognition process:

1. **Preprocessing.** Preparing the data for analysis. This may involve cleaning the data, scaling it, or transforming it in some way to make it more suitable. For example, removing blurry photos, or rescaling weights in grams and sizes in cm so neither swamps the other.
2. **Training.** Fitting a model to the data. This typically involves selecting a model, choosing appropriate hyperparameters, and optimising the model's parameters to minimise a loss function.
3. **Testing.** Evaluating the model's performance on a held-out dataset. This lets us estimate how well the model will do on new data (its generalisation) and compare it with other models.
4. **Deployment.** Putting the trained model into a production environment: integrating it into an existing system, or building a new system around it. For example, the ripeness checker goes into the camera on a fruit-sorting machine.

## Parameters and hyperparameters
<!-- bite: 4a70dddc-735f-4de2-a5eb-9c42a48f3170 -->

Two words in phase 2 need explaining. **Parameters** are the numbers the model learns from the data, such as the mean of each class. **Hyperparameters** are settings you choose before training, such as $k$ in KNN. Phase 2 sets both.

## Model 1: statistical models
<!-- bite: 4ff0d416-14b6-484e-9d2d-6a207eda285d -->

Your notes describe statistical models as based on mathematics and probability, classifying data based on its features. Examples include the Bayes classifier and Gaussian models. [[machine-learning/03-classical-ml/11-naive-bayes-1|Naive Bayes]] from this section is one.

**Advantages:**

1. They give optimal results when the data's distribution is known.
2. They are mathematically well defined and reliable.

**Disadvantages:**

1. They require large training data.
2. Their performance drops when the assumptions about the data's distribution are wrong.

That second disadvantage is the whole subject of lesson 23. Hold on to it.

## A worked statistical model: nearest mean
<!-- bite: c879791a-f219-4476-b84f-cc5928962857 -->

The simplest statistical-style classifier is the **minimum-distance classifier**, also called the **nearest-mean classifier**. It's in the parametric list of your course's classifier tree. Training it means finding the average (mean) feature values of each class. Classifying means assigning a new example to the class whose mean is closest.

Take mangoes with two features, both scored from 1 to 10: sweetness and firmness.

1. Ripe: (8, 3), (9, 2), (7, 4).
2. Unripe: (3, 8), (2, 9), (4, 7).

**Training.** The ripe mean is ((8 + 9 + 7)/3, (3 + 2 + 4)/3) = (8, 3). The unripe mean is ((3 + 2 + 4)/3, (8 + 9 + 7)/3) = (3, 8). The whole model is now just two points.

## Classifying a new mango
<!-- bite: 4851a04d-7ddf-4cef-8d46-4d8850f94ea2 -->

A new mango scores (6, 5). Predict before reading on: ripe or unripe?

Distance to the ripe mean: $\sqrt{(6-8)^2 + (5-3)^2} = \sqrt{4 + 4} = \sqrt{8} \approx 2.83$.

Distance to the unripe mean: $\sqrt{(6-3)^2 + (5-8)^2} = \sqrt{9 + 9} = \sqrt{18} \approx 4.24$.

It's closer to the ripe mean, so it's classed **ripe**.

## Seeing the nearest means
<!-- bite: 6724d7b7-e4d2-4dd8-8eaa-51b4a06f77d8 -->

Here are the mangoes, the two means and the new mango on one plot.

![A scatter plot of mangoes by sweetness (across) and firmness (up): ripe mangoes at (8, 3), (9, 2) and (7, 4) with mean (8, 3); unripe at (3, 8), (2, 9) and (4, 7) with mean (3, 8); the new mango at (6, 5) is 2.83 from the ripe mean and 4.24 from the unripe mean, so it is classed ripe.](../images/pr-mango-nearest-mean.svg)

Compare it with [[machine-learning/03-classical-ml/01-k-nearest-neighbours-1|KNN]], which keeps every training point. The nearest-mean classifier throws the points away after training and keeps only one mean per class. That's very fast and very small, but it assumes each class is one round blob around its mean. Lesson 23 shows what happens when that's false.

## Model 2: structural models
<!-- bite: cde3edd5-7c3e-464e-b3d1-b455e7088870 -->

Your notes describe structural models, also called **syntactic** models, as representing patterns using symbols and relationships, similar to grammar rules.

Instead of numbers, a structural model breaks a pattern into simple parts, called **primitives**, and describes how they fit together. A house in a drawing might be: *a triangle above a square, sharing its top edge*. A handwritten letter A: *two slanted strokes meeting at the top, joined by a horizontal stroke in the middle*. Recognising a pattern means checking whether the parts and their relationships match the rule, much as a grammar checks whether a sentence is well formed.

## Structural models: advantages and disadvantages
<!-- bite: ad85724c-4607-4b00-b1d8-7d2921b7b4f2 -->

Here's what your notes say structural models are good and bad at.

**Advantages:**

1. Good for complex patterns with a clear structure, such as characters, chemical diagrams or circuit drawings.
2. They can represent relationships between pattern components, which a list of numbers can't.

**Disadvantages:**

1. They are computationally complex.
2. The grammar rules are difficult to design.

## Model 3: neural network models
<!-- bite: 5704a724-164c-4e14-9db9-f28c8ef4db68 -->

Your notes describe neural network models as imitating the human brain and learning patterns automatically. You don't write any rules or choose a distribution; the network adjusts its weights from many labelled examples until it gives the right outputs. [[machine-learning/05-deep-learning/01-neural-network-fundamentals|Neural Network Fundamentals]] covers how.

**Advantages** (from your notes):

1. High accuracy.
2. They can handle noisy and complex data, such as photos and speech.

**Disadvantages** (the notes are cut off here, so these are the standard ones):

1. They need a lot of training data and computing power.
2. They are hard to interpret: you can't easily say *why* the network made a decision.

## Choosing a kind of model
<!-- bite: a2ebdb00-2bc6-4127-921d-c2f3b2eb91dd -->

Put the three side by side:

| | Statistical | Structural | Neural |
|---|---|---|---|
| Describes a pattern as | numbers and probabilities | parts and rules | learned weights |
| Best when | the data's distribution is known | the pattern has clear parts | data is plentiful, noisy and complex |
| Main weakness | wrong assumptions hurt it | rules are hard to write | needs lots of data; hard to explain |

So: sorting mangoes by a few measured features, start statistical. Reading circuit diagrams, structural. Recognising faces in photos, neural.

## Terms used in this lesson
<!-- bite: 57ea9928-a3d8-4bc0-a018-d930444b89ef -->

1. **Preprocessing**: This is preparing data for analysis by cleaning, scaling or transforming it.
2. **Deployment**: This is putting a trained model into a real system where it's used.
3. **Parameter**: This is a number the model learns from the data during training, such as a class mean.
4. **Hyperparameter**: This is a setting chosen before training, such as $k$ in KNN.
5. **Generalisation**: This is how well a model performs on new data it wasn't trained on.

## More terms used in this lesson
<!-- bite: 00cb4cc4-08b2-4993-bdad-04c3f28ea95b -->

6. **Statistical model**: This is a pattern-recognition model based on mathematics and probability, such as a Bayes or Gaussian classifier.
7. **Minimum-distance classifier**: This is also known as the **nearest-mean classifier**. It assigns a new example to the class whose mean feature values are closest.
8. **Structural model**: This is also known as a **syntactic model**. It represents a pattern as simple parts (primitives) and the rules joining them, like a grammar.
9. **Primitive**: This is one of the simple parts a structural model builds a pattern from, such as a straight stroke.
10. **Neural network model**: This is a model that imitates the brain and learns patterns automatically by adjusting weights from examples.

## Common pitfalls and traps
<!-- bite: 498482b0-6e58-4bda-81d0-d2289120820d -->

- **Mixing up phases and steps.** The *steps* (lesson 21) build the system: collect, choose features, choose model, train, evaluate. The *phases* follow the process through to use: preprocess, train, test, deploy.
- **Mixing up parameters and hyperparameters.** The model learns parameters; you choose hyperparameters.
- **Thinking structural means "uses a tree".** It means describing a pattern as parts and rules, like a grammar.

## Check your understanding
<!-- bite: 70f4d996-e66a-4e33-a283-cf834334385b -->

Try each one before you open the answer.

1. <!-- q: mcq id="bae97f12" -->
   Which list gives the four phases of the pattern-recognition process from your notes?

   - [x] Preprocessing, training, testing, deployment
   - [ ] Data collection, feature choice, model choice, evaluation
   - [ ] Classification, clustering, training, testing
   - [ ] Statistical, structural, neural, hybrid

   <details><summary>Answer</summary>

   Preprocessing, training, testing, deployment. The second list is the steps for building a system; the last is the three kinds of model.

   </details>

2. <!-- q: mcq id="d470d068" -->
   Ripe mangoes have mean (8, 3) and unripe mangoes have mean (3, 8), in (sweetness, firmness). A new mango scores (5, 6). How does the nearest-mean classifier label it?

   - [ ] Ripe, because it is about 2.83 from the ripe mean
   - [x] Unripe, because it is about 2.83 from the unripe mean and about 4.24 from the ripe mean
   - [ ] It can't be classified without the training points
   - [ ] Ripe, because sweetness matters more

   <details><summary>Answer</summary>

   Distance to ripe: $\sqrt{(5-8)^2 + (6-3)^2} = \sqrt{18} \approx 4.24$. Distance to unripe: $\sqrt{(5-3)^2 + (6-8)^2} = \sqrt{8} \approx 2.83$. It's closer to the unripe mean.

   </details>

3. <!-- q: gap id="089ce0e1" answers="syntactic;grammar|grammar rules" -->
   Structural models are also called ___ models, because they describe patterns with symbols and relationships, like ___.

   <details><summary>Answer</summary>

   Syntactic models, like grammar rules.

   </details>

4. <!-- q: mcq id="74838189" -->
   Which are disadvantages of statistical models listed in your notes? (choose all that apply)

   - [x] They require large training data
   - [x] Their performance drops when assumptions about the data's distribution are wrong
   - [ ] The grammar rules are difficult to design
   - [ ] They can't handle numbers

   <details><summary>Answer</summary>

   Needing large training data, and suffering when the distribution assumptions are wrong. Difficult grammar rules belong to structural models.

   </details>

5. <!-- q: open id="789890d1" -->
   A company wants to read handwritten postcodes on envelopes. Another wants to sort oranges into three sizes by weight and diameter. Which kind of pattern-recognition model would you suggest for each, and why?

   <details><summary>Answer</summary>

   Handwritten postcodes: a neural network model. Handwriting is noisy and varies a lot between people, and there's plenty of example data, which is where neural models do well (a structural model describing each digit's strokes would also be a reasonable answer). Oranges: a statistical model, such as nearest mean or naive Bayes. There are only two clean numeric features, and their distribution for each size is easy to estimate.

   </details>

## Before moving on
<!-- bite: 2d951557-d137-4239-83bc-8cf48db3ba8a -->

You're done when you can name the four phases, describe the three kinds of model with their advantages and disadvantages, and classify a new example with a nearest-mean classifier by hand.

Recap: the phases are preprocessing, training, testing and deployment. Statistical models use probability and are best when the distribution is known; structural models use parts and grammar-like rules; neural models learn automatically from lots of data. The nearest-mean classifier keeps only each class's mean and picks the closest: the mango (6, 5) is ripe, at 2.83 from the ripe mean against 4.24.

Next, [[machine-learning/03-classical-ml/23-parametric-and-non-parametric-classifiers-1|Parametric and Non-Parametric Classifiers 1]] asks the question the nearest-mean classifier raises: what happens when you assume the wrong shape for your data?

## Related
<!-- bite: e403f9f6-c225-4f58-bf51-fe3b999c800f -->

- [[machine-learning/03-classical-ml/03-distance-measures|Distance Measures]]: the Euclidean distance used here.
- [[machine-learning/03-classical-ml/04-learning-vector-quantization|Learning Vector Quantization]]: keeping a few typical points per class, between nearest mean and KNN.

## About this lesson
<!-- bite: 0c64c2ae-baa6-4919-beac-ba6ff191fdd7 -->

**Level:** introductory. Lesson 22 of the classical ML section, part 2 of 2 on pattern recognition. It covers the four phases, statistical, structural and neural models, and a worked nearest-mean classifier.

**Source:** University of Lagos SSG 518 class notes, *Pattern Recognition* (07/02/26: phases, and the three models with their advantages and disadvantages). The notes' list of neural-network disadvantages is cut off on the page, so the two given are the standard ones and labelled as such. The mango example is computed and asserted by `scripts/diagrams/ml_pattern_recognition.py`.
