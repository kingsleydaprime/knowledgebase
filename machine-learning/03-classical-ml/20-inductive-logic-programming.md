---
id: 6e5f471a-10b4-4d81-b4c6-d6c36af749b1
---

# Inductive Logic Programming (ILP)

ILP learns rules from examples, instead of numbers.

## Before you start
<!-- bite: af45a0c4-aff7-4311-acf3-84cfbe4886b3 -->

You should know what supervised learning is ([[machine-learning/01-foundations-of-ml/01-what-is-ml-and-types|What ML Is]]). A rule like `parent(X, Y) :- mother(X, Y).` reads "X is a parent of Y if X is the mother of Y".

After this lesson you will be able to:

- name the four core components of ILP;
- say how ILP differs from table-based machine learning;
- induce a simple rule from background knowledge and examples.

## What ILP is
<!-- bite: 28db6999-6c53-4667-ab3a-2cc08821bdc0 -->

Inductive Logic Programming is a subfield of machine learning that uses logic programming (often Prolog) to induce general rules (hypotheses) from examples and background knowledge, merging machine learning with logic programming. It uses First-Order logic to represent data, allowing for complex relational learning in domains like drug design, protein structure prediction, and Semantic Web.

So far, the models we met learn from numbers in tables. ILP learns rules instead.

Next: how ILP is different from the models we have met so far.

## How ILP is different
<!-- bite: 79dddae9-25c5-461f-ae98-ff5a390f00da -->

Unlike most machine learning that focuses on statistical correlation in tables, ILP focuses on deriving interpretable if-then rules from specific examples and background knowledge.

## Core Components
<!-- bite: 28ff02f4-88a5-4ade-85e6-b229b4d1963a -->

- **Background Knowledge (B):** Pre-existing facts or domain-specific information, e.g. ("all humans are mammals").
- **Positive Examples (E+):** Facts that the learned rules must explain (e.g. John is a parent).
- **Negative Examples (E−):** Facts that the learned rules must not cover (e.g. A dog is a parent).
- **Hypothesis (H):** The resulting logic program, a set of rules that, combined with the background knowledge, entails the positive examples but not the negative ones.

## Popular Systems
<!-- bite: d71fd4ba-4bff-4f47-ab45-64539bb93c04 -->

- **FOIL:** An early, influential system that uses a "separate and conquer" strategy to build rules literal by literal.
- **Progol:** It uses inverse entailment to find the most specific clause that explains an example and then generalizes it.
- **Aleph:** One of the most widely used ILP systems for general-purpose rule induction.

## Characteristics
<!-- bite: 2a44e508-bf55-4fb1-8d98-72389ac60953 -->

- **Relational learning:** ILP excels at finding patterns in structured data like graphs, molecules, or family trees, where relationships between entities are more important than individual attributes.
- **Interpretability:** Because the output is a logic program, humans can easily read and verify the why behind a prediction.
- **Data efficiency:** It can often learn complex concepts from just a few examples by leveraging its background knowledge.

## Applications of ILP
<!-- bite: 609bab0e-e46c-47e8-afab-c3933a287b11 -->

1. **Bioinformatics:** It predicts the drug activity by learning the chemical structure (SAR) that makes a molecule effective.
2. **Natural Language Processing:** Learning grammars or rules to translate sentences into database queries.
3. **Robotics:** Allowing robots to learn general rules about their environment (e.g. "key opens lock") from limited observation.

Other applications are program analysis, scientific discovery, vision, games, data curation and transformation, learning from trajectories.

Inductive logic programming tackles a wide variety of problems in machine learning, including classification, regression, clustering and reinforcement learning, often using "upgrades" of existing propositional machine learning systems.

In contrast, machine learning often emphasizes the extraction of correlations from high-dimensional data. The integration of these approaches aims to combine the transparency and adaptability of logical rules with the robustness and efficiency of data-driven algorithms.

## Check your understanding
<!-- bite: fe78ad4c-4e62-4539-9e28-d62b95656970 -->

Try each one before you open the answer.

1. <!-- q: open id="715da26f" -->
   What must the hypothesis H do with the positive and the negative examples?

   <details><summary>Answer</summary>

   Together with the background knowledge, it must entail (cover) all the positive examples and none of the negative ones.

   </details>

2. <!-- q: mcq id="d3416290" -->
   Which of these are the four core components of ILP? Choose all that apply.

   - [x] Background knowledge (B)
   - [x] Positive examples (E+)
   - [x] Negative examples (E−)
   - [x] Hypothesis (H)
   - [ ] Learning rate (α)

   <details><summary>Answer</summary>

   B, E+, E− and H. There is no learning rate: ILP learns rules, not numbers.

   </details>

3. <!-- q: gap id="fffa58e6" answers="prolog" -->
   Fill in the gap. ILP usually writes its rules in the logic programming language ___.

   <details><summary>Answer</summary>

   Prolog. A rule like `parent(X, Y) :- mother(X, Y).` reads "X is a parent of Y if X is the mother of Y".

   </details>

4. <!-- q: mcq id="542c9062" -->
   Which ILP system uses a "separate and conquer" strategy to build rules literal by literal?

   - [x] FOIL
   - [ ] Progol
   - [ ] Aleph

   <details><summary>Answer</summary>

   FOIL. Progol uses inverse entailment, and Aleph is a widely used general-purpose system.

   </details>

5. <!-- q: open id="46b78996" -->
   Give one reason ILP is easy to trust.

   <details><summary>Answer</summary>

   Interpretability: the output is a logic program, so a human can read and check the why behind a prediction.

   </details>

## Practice — independent task
<!-- bite: 2092df96-852f-4d47-9806-6c497bfb0ca5 -->

Past question 5(b) in the [[machine-learning/ssg-535-question-bank|SSG 535 question bank]] gives facts about mary, paul, john and anna and asks for a rule for `sibling(X, Y)`. **Done when** your rule covers sibling(john, anna) and sibling(anna, john) but not sibling(john, john). Then check the solution.

## Before moving on
<!-- bite: 35ec6a83-8443-4633-8c7a-441fb07198f9 -->

ILP induces readable if-then rules from background knowledge, positive examples and negative examples, using logic programming.

**Next:** [[machine-learning/03-classical-ml/21-pattern-recognition-1|Pattern Recognition 1]]. We have now seen many kinds of models. The last four lessons of this section step back and look at them all as pattern recognition, and ask how to compare them fairly.

## About this lesson
<!-- bite: 10c9eeb1-f523-4740-80d1-2c6767e0c8ed -->

**Level:** Intermediate. **Covers:** what ILP is, its core components, popular systems, characteristics and applications. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
