---
id: af37cd7f-5e65-4713-b734-2bcf1cabc2be
---

# The Four Approaches to AI

The four approaches to AI are four different answers to the question "what exactly are we trying to build?"

## Before you start
<!-- bite: 2b90c566-3e28-4f59-8ae8-774327c134d0 -->

Read [[artificial-intelligence/01-foundations/01-what-ai-is|What Artificial Intelligence Is]] first. You need its definition of AI and the idea of symbolic AI.

After this lesson you will be able to:

1. draw the two-by-two grid of approaches and place a definition of AI in the right box;
2. describe the Turing test, and list the six abilities a machine needs to pass the total Turing test;
3. explain why this subject builds rational agents rather than copies of the human mind.

## What the four approaches are
<!-- bite: 83fe70c1-9cbe-4874-a943-d93f4c9e1658 -->

In the last lesson you saw five definitions of AI that all sounded a bit different. They differ because people disagree about what success looks like.

Some people judge an AI by how it **thinks** (the process inside). Others judge it by how it **acts** (what it does). And some measure it against **humans**, while others measure it against an ideal of **rationality**, meaning doing the right thing.

Two questions, two answers each, gives four boxes. This lesson walks through all four and ends with the one this subject uses.

## The kid version
<!-- bite: bd452bce-b60c-43a3-ad64-aff2eb589856 -->

Imagine a cooking competition. One judge says "cook it the way my grandma does, step by step." Another says "follow the recipe book exactly." A third says "I don't care how you cooked it. If it tastes like grandma's, you win." The fourth says "I don't care how you cooked it either. Just make the best meal you can with what's in the kitchen." The four judges are the four approaches to AI. This subject listens to the fourth judge.

**Where the analogy stops working.** A cooking judge tastes once at the end. An AI system acts again and again, with the world changing between actions, so "the best meal" means the best *next* action given what the system knows right now.

## The grid
<!-- bite: cd1d5dfa-497f-47ea-ab73-24afdf5625c1 -->

Here are the four approaches laid out as a grid. Thinking versus acting goes down the side; human versus rational goes across the top.

![A two-by-two grid: the thinking row holds think like humans (cognitive modelling) and think rationally (laws of thought, logic); the acting row holds act like humans (the Turing test) and act rationally (the rational agent), which is outlined as the approach this subject takes.](../images/ai-four-approaches.svg)

## Placing the definitions in the grid
<!-- bite: eb1d9557-7204-4b85-88ee-b42c01495c4e -->

The definitions from lesson 1 fall into the boxes like this:

1. "Machines that perform functions that need intelligence when performed by people" is **acting like humans**.
2. "The automation of activities we associate with human thinking" is **thinking like humans**.
3. "The study of the computations that make it possible to perceive, reason and act" is **thinking rationally**.
4. "The automation of intelligent behaviour" is **acting rationally**.

Let's take the boxes one at a time.

## Acting like humans: the Turing test
<!-- bite: 5d7fbd0a-ca29-4a64-bce4-841bd074d660 -->

In 1950 Alan Turing asked: instead of arguing about what "thinking" means, why not test it?

You enter a room with a computer terminal. For a fixed time you type whatever you like and read the replies. At the other end is either a person or a computer. If it's a computer and, at the end, you can't reliably tell it isn't a person, the computer passes. It's then said to be intelligent.

That's the **Turing test**. Notice it only looks at behaviour. It doesn't care what's going on inside the machine, only whether its answers are as good as a human's.

## What it takes to pass the Turing test
<!-- bite: fee48360-c9c7-40be-998b-d7fe0ff224d0 -->

To pass, a machine needs four abilities:

1. **Natural language processing**, to communicate with the human in their own language.
2. **Knowledge representation**, to store what it knows effectively.
3. **Automated reasoning**, to use what it has stored to answer questions and draw new conclusions.
4. **Machine learning**, to adapt to new situations it wasn't programmed for.

The **total Turing test** adds a camera and a hand, so the examiner can test seeing and touching too. That needs two more:

5. **Computer vision**, to perceive objects.
6. **Robotics**, to move objects.

These six are basically the areas of AI from lesson 1. That's why the Turing test is still taught: trying to pass it touches almost the whole field.

## Thinking like humans: cognitive modelling
<!-- bite: 2b40511b-68c0-4f08-8ed1-2958e7f1ac58 -->

The second box wants the *process* inside the machine to match the human one. This is called **cognitive modelling**, and it belongs to **cognitive science**, where AI and psychology meet.

The problem is: how do you know how humans think? There are two ways to look:

1. **Introspection**: watching your own thoughts as they go by. But you can't see most of your own thinking, and you can't check anyone else's.
2. **Psychological experiments**: watching people solve problems and measuring what they do.

If your program solves a puzzle in the same steps and makes the same mistakes as people, you've got a theory of how people think. That's valuable science, but it's a harder target than just getting the right answer.

## Thinking rationally: the laws of thought
<!-- bite: 22d94450-4b43-4cf0-9d1c-6492aa28d6de -->

The third box wants the machine to think *correctly*, following the laws of logic. This goes back to Aristotle and his patterns of correct argument: "All men are mortal. Socrates is a man. So Socrates is mortal."

The idea is that if you write the problem in logic, a program can reason its way to the answer. There are two problems with this, and the course slides name both:

1. **Not everything fits into logic.** Logic handles "true" and "false" well, but struggles with uncertainty: "the road is *probably* clear."
2. **It can be too slow.** Even when a problem fits, working through every logical step can take more time than you have. The reasoning needs guidance about which steps to try first.

And people aren't always rational anyway, so "rational" and "human" really are two different targets.

## Acting rationally: the rational agent
<!-- bite: a99a39a8-51e4-46d6-98e2-3951fa064972 -->

The fourth box is the one this subject uses. An **agent** is anything that perceives its surroundings and acts on them. A **rational agent** is one that does the right thing, and the course defines the right thing like this:

A one-sentence version for an exam: acting rationally means doing whatever is expected to achieve the goal best, given the information available.

Think about the map app. We don't care whether it thinks about roads the way you do (box 1), whether it reasons in formal logic (box 2), or whether it could pass for a human (box 3). We care that it gives the best route, given the map it has. That's acting rationally.

## Why the rational agent approach wins
<!-- bite: 40c06c14-5896-4f78-87bf-9639879a1c54 -->

The rational agent approach has two advantages over the others:

1. **It's more general than logic alone.** Logic is one tool a rational agent can use, but when logic can't reach a conclusion, the agent can fall back on knowledge about the problem, rules of thumb or probabilities. Rational agent = logic + domain knowledge.
2. **It can be measured and improved scientifically.** "Is it the best action given what it knew?" can be checked. "Is it human-like?" is much harder to pin down.

One honest warning. A perfectly rational agent would always find the very best action, but in a big problem that can take more computing time than the universe has. So in practice we aim for the best program we can run on the machine we have. You'll see this again and again: searches that settle for a good answer fast instead of the perfect answer too late.

## Terms used in this lesson
<!-- bite: 4194008c-5897-4a9e-b305-34b9d641499a -->

1. **Turing test**: This is a test proposed by Alan Turing in 1950. A person types questions to a hidden respondent, and a computer passes if the person can't reliably tell it isn't human.
2. **Total Turing test**: This is the Turing test extended with vision and physical objects, so the machine also needs computer vision and robotics.
3. **Cognitive modelling**: This is building a program whose internal steps match how humans actually think. It's the "think like humans" approach.
4. **Laws of thought**: This is the "think rationally" approach. It means reasoning by the rules of logic, going back to Aristotle.
5. **Agent**: This is anything that perceives its environment and acts on it.
6. **Rational agent**: This is an agent that does whatever is expected to achieve its goal best, given the information it has.

## Common pitfalls and traps
<!-- bite: 5b91d68c-94f7-4838-b17d-ba79a99c3680 -->

- **Mixing up the rows and columns.** Thinking versus acting is about *process versus behaviour*. Human versus rational is about *what you measure against*. The Turing test is acting like humans, not thinking like humans, because it only checks the answers.
- **Thinking "rational" means "uses logic".** Thinking rationally uses logic. Acting rationally is wider: whatever gets the best result, logic or not.
- **Thinking rational means perfect.** A rational agent does the best it can with the information and time it has. It can still be wrong if its information was wrong.

## Check your understanding
<!-- bite: 7dfe481d-4576-4483-bf3a-028ee4624f39 -->

Try each one before you open the answer.

1. <!-- q: mcq id="d9a8a66e" -->
   "AI is the study of how to make computers do things at which, at the moment, people are better." Which approach does this definition belong to?

   - [ ] Thinking like humans
   - [ ] Thinking rationally
   - [x] Acting like humans
   - [ ] Acting rationally

   <details><summary>Answer</summary>

   Acting like humans. It measures the computer against what people *do*, and says nothing about the process inside or about an ideal of rationality.

   </details>

2. <!-- q: mcq id="57a5fbf9" -->
   Which abilities does the total Turing test add to the ordinary Turing test? (choose all that apply)

   - [ ] Natural language processing
   - [x] Computer vision
   - [x] Robotics
   - [ ] Machine learning
   - [ ] Automated reasoning

   <details><summary>Answer</summary>

   Computer vision and robotics, because the examiner can now show objects and pass things through a hatch. The other three are already needed for the ordinary test.

   </details>

3. <!-- q: gap id="557be715" answers="cognitive modelling|cognitive modeling;introspection|psychological experiments" -->
   Building a program whose internal steps match human thinking is called ___. One way to find out how humans think is ___.

   <details><summary>Answer</summary>

   Cognitive modelling. The two ways to study human thinking are introspection (watching your own thoughts) and psychological experiments (watching other people).

   </details>

4. <!-- q: open id="82fa669d" -->
   Give the two weaknesses of the "think rationally" (laws of thought) approach that the course names.

   <details><summary>Answer</summary>

   First, logic can't express everything, especially uncertainty, such as "the road is probably clear". Second, reasoning through logic can take too much computing time unless it's guided about which steps to try first.

   </details>

5. <!-- q: open id="c254f153" -->
   A delivery robot takes a slightly longer route because its map shows a road closure that has actually been lifted. Was it acting rationally? Explain in two sentences.

   <details><summary>Answer</summary>

   Yes. Acting rationally means doing what is expected to achieve the goal best *given the information available*, and its information said the road was closed. It made the wrong choice only because its information was out of date, not because it chose badly.

   </details>

## Before moving on
<!-- bite: 11721a49-86fa-475b-9880-ea2e8791eceb -->

You're done when you can draw the grid from memory, put each of the course's definitions in its box, describe the Turing test and its six abilities, and give the two reasons this subject builds rational agents.

Recap: two questions, thinking or acting and human or rational, give four approaches. Acting like humans is the Turing test. Thinking like humans is cognitive modelling. Thinking rationally is logic, the laws of thought. Acting rationally is the rational agent: do what's expected to achieve the goal best, given what you know. This subject builds rational agents.

Next, [[artificial-intelligence/01-foundations/03-foundations-and-history-of-ai|Foundations and History of AI]] shows where all these ideas came from: the older fields AI borrows from, and the booms and crashes it has been through.

## Related
<!-- bite: 48fd05a0-01bc-4589-8651-5700d6b4ab49 -->

- [[artificial-intelligence/01-foundations/04-agents-and-environments|Agents and Environments]]: the rational agent, in detail.
- [[machine-learning/08-other-architectures/06-rational-decision-making-1|Rational Decision Making 1]]: the same idea of "the best choice given the information", applied to decisions with costs and benefits.

## About this lesson
<!-- bite: cd5c780e-9eae-4e8a-b154-11a465241968 -->

**Level:** introductory, no maths. Lesson 2 of section 01 (foundations). It covers the four approaches to AI, the Turing test and the total Turing test, cognitive modelling, the laws of thought, and the rational agent.

**Source:** University of Lagos SSG 518 Module 1 slides, *Introduction/History* (the four-box grid, the Turing test, and "systems that act rationally"). The grid itself is from Russell and Norvig's *Artificial Intelligence: A Modern Approach*.
