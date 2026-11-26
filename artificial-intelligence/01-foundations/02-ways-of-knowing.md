---
id: 36cc1d03-1799-476b-986f-a76ee90593a2
---

# Ways of Knowing: Recall, Calculation and Reasoning

You know things in three ways (recall, calculation and reasoning), and only reasoning really needs intelligence.

## Before you start
<!-- bite: cf24f020-7e30-4609-abe0-e2d6454ef644 -->

Read [[artificial-intelligence/01-foundations/01-what-ai-is|What Artificial Intelligence Is]] first. You need its definition of intelligence: the ability to acquire knowledge and use it.

After this lesson you will be able to:

1. explain why intelligence is defined by intelligent behaviour rather than exactly;
2. name the three ways of knowing and say which demands intelligence, and why;
3. relate them to how people sense, perceive and act on the world;
4. explain the data–information–knowledge continuum, and what a concept is and why it makes us efficient.

## What ways of knowing are
<!-- bite: 7a52cf2e-6d09-43e9-9df9-37d3b0eba65d -->

Ask a friend three questions. "What's your mother's maiden name?" She just remembers. "What's 37 times 12?" She works it out with a method she learned in primary school. "If the road to Ibadan is flooded and the bus is full, how will you get to the wedding?" Now she has to *think*: combine what she knows in a way nobody taught her for this exact case.

Those are the three ways of knowing from your SSG 503 notes: **recall**, **calculation** and **reasoning**. They come up in almost every SSG 503 exam, because they explain what AI is actually trying to copy.

## The kid version
<!-- bite: 43752673-8e00-47f0-bc4f-eafc9861e978 -->

Imagine three helpers in a kitchen. The first has a huge recipe book and can find any recipe you name. The second can follow any recipe perfectly, measuring and timing exactly. The third, when you say "we have yam, eggs and pepper, and no recipe", can invent a dish. The first two are very useful, but a machine can do their jobs. The third is the one that's intelligent.

**Where the analogy stops working.** Real people mix all three at once without noticing, and good reasoning leans on lots of recall. The three aren't separate people; they're three things one mind does.

## Defining intelligence
<!-- bite: a716c7fa-d550-416d-b770-34981570bf19 -->

Your notes start with an honest admission: intelligence **cannot be defined exactly**, but it **can be identified or recognised**. You know an intelligent answer when you see one, even if you can't write a formula for "intelligent".

So we define intelligence by **intelligent behaviour**: what an intelligent person (or system) does, and how they use their sources of knowledge. That's the same move the course makes for AI in [[artificial-intelligence/01-foundations/03-the-four-approaches-to-ai|The Four Approaches to AI]]: judge the system by what it does.

Why do we need to know things at all? Your notes answer in one line: **we need to know in order to make decisions, and take the necessary actions.**

## Way 1: recall
<!-- bite: e36bd8f7-2ebf-426b-aa3c-9e175f252fa0 -->

**Recall** is knowing by remembering: you know it from experience, so you bring it back.

Your notes make a sharp point: **books have more recall capacity than humans**. A library remembers more than any person, and on a computer, recall is handled by a **database** (a collection of data). So recall, on its own, doesn't demand intelligence. Storing and fetching is something machines do better than we do.

Recall also has problems, which your notes list:

1. There are **too many things** to recall.
2. Some experiences are **better not recalled** at all.

## Way 2: calculation
<!-- bite: 684bf2f6-1627-421f-935a-d50027878356 -->

**Calculation** is knowing by working it out with a fixed procedure, like long multiplication.

Your notes point out that **tabulation (calculation) can be routinely mechanised**: a calculator does it faster and more reliably than you. But calculating machines **cannot offer solutions that have not been anticipated**. They do exactly what the procedure says, nothing more.

And calculation has its own problem: it's **restricted to numbers**. It's numerical manipulation. It can tell you that 1 + 1 = 2, but not what to *conclude* from that, unless someone has written the rule in advance.

## Way 3: reasoning
<!-- bite: 9f0d8834-75af-48c8-aa5b-f084af35d503 -->

**Reasoning** is knowing by inferring something new from what you already know. Your notes say it **involves a lot of symbolic manipulation, and it involves intelligence**.

Their example: 1 apple and 1 cherry. Calculation on its own is stuck: an apple and a cherry aren't the same thing, so you can't just add them. Reasoning says: both are **fruits**, so that's 2 fruits. It manipulates *symbols* (the idea "fruit"), not just numbers, and reaches a conclusion nobody wrote down for this case.

So, to answer the exam question directly: **reasoning is the way of knowing that demands intelligence.** Recall can be done by a database and calculation by a calculator, but reasoning needs the ability to use knowledge in new situations. That's what AI is about.

## From the world to a decision
<!-- bite: 626af27f-ce14-4890-b5be-5c369d7fe8ec -->

How do these ways of knowing connect to the world? Your notes describe a chain:

![How a person turns the environment into action: sensing, then perception, then knowing by recall, calculation or reasoning, then a decision and an action.](../images/gp-knowing-loop.svg)

## The chain, step by step
<!-- bite: a1116f18-5e06-4bc6-8dcd-c167ffcef4dc -->

Here's what each box in that chain means:

1. **Sensing** is the stimulation of the sense organs by excitation from the environment: light on your eyes, sound in your ears. Humans adapt to the environment because we can collect data from it by sensing.
2. **Perception** is interpreting the sensed data: the light becomes "a bus", the sound becomes "my name".
3. **Cognition** is the totality of sensing, interpreting and using data, knowledge and information. It's intelligent behaviour. Here you know by recall, calculation or reasoning.
4. **Decision and action**: you decide, and act on the environment, which changes what you sense next.

That's the agent loop you'll meet properly in [[artificial-intelligence/01-foundations/05-agents-and-environments|Agents and Environments]], seen from the human side.

## Data, information and knowledge
<!-- bite: a6da32e3-58ea-4d85-802d-add1a295dd2a -->

The exams also ask you to explain the three ways of knowing "in the light of the data–knowledge continuum". Your notes define the three steps:

![The data to knowledge continuum: data, raw facts and figures, becomes information when processed and organised, and information becomes knowledge when it comes with rules for applying it.](../images/gp-data-knowledge.svg)

1. **Data** is raw facts and figures. "Temperature: 39°C."
2. **Information** is processed data. "The patient has a high fever."
3. **Knowledge** is applied information: information together with rules for applying it. "High fever plus these symptoms means test for malaria." And knowledge is **dynamic**: it changes as we learn.

## Connecting knowing to the continuum
<!-- bite: 2d2c89a3-970c-4f26-8be1-f3e20ced9a03 -->

Now connect the continuum to the three ways of knowing. Recall mostly brings back stored **data**. Calculation turns data into **information**. Reasoning turns information into **knowledge** that can be applied to situations nobody planned for. The further along the continuum you go, the more intelligence it takes.

## Concepts and cognitive efficiency
<!-- bite: 1c67d210-cadd-4ae7-a24e-74e1a8925c26 -->

How does reasoning manage the apple-and-cherry trick? With a **concept**.

A **concept** is a meaningful representation of a class of like objects, based on their core features. "Fruit" is a concept; so is "bird". Using concepts is a way of engaging in symbolic manipulation. Your notes add that **cognition is based on propositions**: statements that connect two or more concepts, such as "birds can fly".

Concepts matter because **we do not have enough memory** to remember every single object separately. With the concept "bird", you know a lot about a bird you've never seen. That's **cognitive efficiency**: the ability to know a lot from the little you know. It measures how much you get out compared with how much you put in.

Concepts have one problem: **for every concept there is an exception**. "All birds can fly", but penguins and ostriches can't. A reasoning system has to handle exceptions, which is one reason knowledge representation is hard.

## Why take a cue from humans
<!-- bite: e20d0b37-02a0-4019-b3b7-19d7ef867c05 -->

A 2017/18 question asks why we take a cue from humans in solving some engineering problems. You can answer it from this lesson. Some problems can't be solved by recall (no stored answer exists) or by calculation (no formula exists), such as recognising a face, reading handwriting, or planning around a flood. Humans solve these every day by reasoning with concepts. Copying how humans do it, by using concepts, rules of thumb and search, is often the only way in. That's the starting point of AI.

## Terms used in this lesson
<!-- bite: e8920b4b-d621-41a7-b489-1192da6e2599 -->

1. **Recall**: This is knowing by remembering something from experience. A database does it on a computer.
2. **Calculation**: This is also known as **tabulation**. It's knowing by working something out with a fixed procedure. It can be mechanised.
3. **Reasoning**: This is knowing by inferring something new from what you know, by symbolic manipulation. It demands intelligence.
4. **Sensing**: This is the stimulation of the sense organs by the environment.
5. **Perception**: This is interpreting the data that was sensed.
6. **Cognition**: This is the totality of sensing, interpreting and using data, information and knowledge. It's intelligent behaviour.

## More terms used in this lesson
<!-- bite: 08718cc1-9693-4203-99ea-971cb36a63f4 -->

7. **Data**: This is raw facts and figures.
8. **Information**: This is data that has been processed.
9. **Knowledge**: This is information together with rules for applying it. It is dynamic.
10. **Concept**: This is a meaningful representation of a class of like objects, based on their core features, such as "fruit".
11. **Proposition**: This is a statement connecting two or more concepts, such as "birds can fly".
12. **Cognitive efficiency**: This is the ability to know a lot from the little you know.

## Common pitfalls and traps
<!-- bite: 5b050b8e-a2e5-447f-a9f7-e116fd18610b -->

- **Saying recall needs intelligence.** A database recalls better than any person. Recall alone isn't intelligent.
- **Mixing up information and knowledge.** Information is processed data; knowledge is information *with rules for applying it*.
- **Forgetting exceptions.** Every concept has exceptions, and a good answer about concepts mentions them.

## Check your understanding
<!-- bite: d5403644-1c7f-487f-914c-2ad22aaa73fc -->

Try each one before you open the answer.

1. <!-- q: mcq id="f9268b7e" -->
   Which of the three ways of knowing demands intelligence?

   - [ ] Recall
   - [ ] Calculation
   - [x] Reasoning
   - [ ] All three equally

   <details><summary>Answer</summary>

   Reasoning. Recall can be done by a database and calculation by a calculator, but reasoning infers something new by symbolic manipulation.

   </details>

2. <!-- q: mcq id="13a294f0" -->
   A shop's system reads "Item 4471: 12 sold today", turns it into "Rice is selling fast this week", and then applies the rule "reorder anything that sells fast" to order more rice. Which statement is in the knowledge stage?

   - [ ] "Item 4471: 12 sold today"
   - [ ] "Rice is selling fast this week"
   - [x] "Reorder anything that sells fast", applied to order more rice
   - [ ] None of them

   <details><summary>Answer</summary>

   Knowledge is information together with rules for applying it. The raw count is data; "selling fast" is information; applying the reorder rule is knowledge.

   </details>

3. <!-- q: gap id="075bd025" answers="sensing;perception|perceiving" -->
   Stimulation of the sense organs by the environment is called ___. Interpreting the sensed data is called ___.

   <details><summary>Answer</summary>

   Sensing, then perception. Cognition is the totality of both plus using data, information and knowledge.

   </details>

4. <!-- q: open id="3e22765d" -->
   Using the example "1 orange and 1 mango", explain the difference between calculation and reasoning.

   <details><summary>Answer</summary>

   Calculation manipulates numbers by a fixed procedure, so it can't add an orange to a mango: they aren't the same kind of thing, and no rule was given. Reasoning manipulates symbols: it uses the concept "fruit" to conclude there are 2 fruits. That's a new conclusion nobody wrote down for this case, which is why reasoning demands intelligence.

   </details>

5. <!-- q: open id="534a8a84" -->
   What is cognitive efficiency, and how do concepts give it to us?

   <details><summary>Answer</summary>

   Cognitive efficiency is the ability to know a lot from the little you know: getting a lot out for little put in. Concepts give it because one concept, such as "bird", stands for a whole class of objects, so learning it once tells you about every member, even ones you've never met. We don't have enough memory to remember every object separately, so concepts let us know far more than we could store.

   </details>

## Before moving on
<!-- bite: 3a8c4589-5dfc-4959-9960-9049d94aedcb -->

You're done when you can say why intelligence is defined by behaviour, name the three ways of knowing and pick the one that needs intelligence, draw the sensing-to-action chain and the data–information–knowledge chain, and explain concepts and cognitive efficiency.

Recap: intelligence is recognised by intelligent behaviour, not defined exactly. We know by recall (a database can do it), calculation (a calculator can do it) or reasoning (symbolic manipulation, which needs intelligence). Sensing, perception and cognition lead to decisions and actions. Data becomes information when processed, and knowledge when it comes with rules for applying it. Concepts let us know a lot from a little, but every concept has exceptions.

Next, [[artificial-intelligence/01-foundations/03-the-four-approaches-to-ai|The Four Approaches to AI]] sorts the definitions of AI by whether they judge a system by how it thinks or by how it acts.

## Related
<!-- bite: 3c11c914-7c69-49af-8aa2-6d945299a8ee -->

- [[machine-learning/03-classical-ml/21-pattern-recognition-1|Pattern Recognition 1]]: data and information in pattern recognition.

## About this lesson
<!-- bite: 7bbeba52-37e2-46f8-bccb-ba9fd8cb99ca -->

**Level:** introductory, no maths. Lesson 2 of section 01 (foundations). It covers defining intelligence, the three ways of knowing, sensing, perception and cognition, the data–information–knowledge continuum, concepts and cognitive efficiency.

**Source:** University of Lagos SSG 503 (Artificial Intelligence) class notes, first note (intelligence, ways of knowing, problems of recall, reasoning, data, information and knowledge, concepts and cognitive efficiency), and the SSG 503 past papers 2012/13 to 2017/18, which ask about these every year (see the [[artificial-intelligence/ssg-518-question-bank|SSG 518 question bank]]). The notes' example of a bird that can't fly ("pigeon") is replaced with penguins and ostriches, which really can't.
