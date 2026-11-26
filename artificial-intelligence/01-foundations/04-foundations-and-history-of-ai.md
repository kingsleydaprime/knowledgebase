---
id: 25ab4e43-35bb-4fa7-9e81-6176153090d4
---

# Foundations and History of AI

AI is built on ideas borrowed from six older fields, and it grew in stages, with funding booms and crashes along the way.

## Before you start
<!-- bite: a29087e1-d076-4b56-b7b3-de578e82b611 -->

Read [[artificial-intelligence/01-foundations/03-the-four-approaches-to-ai|The Four Approaches to AI]] first. This lesson refers to the Turing test and the rational agent.

After this lesson you will be able to:

1. name the six fields AI is founded on, and say what each one gave it;
2. put the main events of AI's history in order, starting from the Dartmouth conference of 1956;
3. explain the boom-and-crash pattern in AI and the lesson the course draws from it;
4. list the advantages and disadvantages of AI that the course gives.

## What this lesson covers
<!-- bite: a2a2becc-899f-41a5-ad9d-d361df7a0911 -->

AI didn't come from nowhere. Before anyone built a computer, philosophers were asking whether the mind works like a machine, and mathematicians were inventing logic and probability. AI took those ideas and turned them into programs.

This lesson has two halves. First, the six fields AI stands on. Then the story of how the field grew, including the times it promised too much and lost its funding. Both halves explain why the field looks the way it does today.

## The kid version
<!-- bite: 3132d6f4-d962-4bc4-9b66-59ec78c72c8a -->

Think of AI as a new house built with bricks from six older houses. Philosophy gave the question "can thinking be done by a machine?" Maths gave the tools to write thinking down exactly. Psychology showed how people actually think. Computer engineering built the machine to run it on. Control theory showed how a machine can correct itself. Linguistics showed how language is put together. And like any building project, AI had good years when money poured in, and bad years when the builders overpromised and the money stopped.

**Where the analogy stops working.** A house is finished one day. AI keeps borrowing new bricks, from statistics, from neuroscience, from economics, and it also hands its own ideas back to the older fields.

## The six foundations, part 1: philosophy, maths, psychology
<!-- bite: 812f23a0-0485-4234-9673-9e1c663154a4 -->

1. **Philosophy** asked the first question: is the mind a kind of machine? Long before computers, philosophers started describing thinking as a process with internal steps. Without that idea, "artificial intelligence" makes no sense.
2. **Mathematics** made those steps exact, in three areas. **Logic** gave rules for correct reasoning. **Computation** asked which problems can be computed at all, which led to complexity theory: which problems are fast and which are hopelessly slow. **Probability** gave a "degree of belief" for handling uncertainty. And **decision theory** joined probability with utility (how much you value an outcome) to say how to choose well.
3. **Psychology** studied how humans and animals think and act, and gave AI models of reasoning. It also strengthened the idea that people and animals can be seen as information-processing machines.

## The six foundations, part 2: computers, control, language
<!-- bite: 817653e8-7892-489c-9caf-6d49b53c3a8d -->

4. **Computer engineering** built the machine. Without fast computers, AI is just theory, and every jump in computer power has let AI attack bigger problems. AI gave back too: time-sharing, the linked list and object-oriented programming all came partly out of AI research.
5. **Control theory and cybernetics** asked how a machine can run itself. A thermostat measures the room, compares it with what you want, and adjusts. That loop of acting, getting feedback and adjusting to do better over time is exactly what an AI agent does.
6. **Linguistics** studied how language is built: formal grammars, syntax (structure) and semantics (meaning). AI needs all three to understand language, and they also shaped knowledge representation.

Notice how the six map onto the four approaches from the last lesson. Psychology feeds "think like humans". Logic feeds "think rationally". Decision theory and control theory feed "act rationally".

## The birth of AI: Turing and Dartmouth
<!-- bite: f288c4ef-ff98-4505-a089-abfb443d426e -->

People have dreamed of thinking machines since ancient Greece. Aristotle's logic, Al-Khwarizmi's step-by-step methods (the word "algorithm" comes from his name), George Boole's algebra of true and false, Charles Babbage's mechanical computer and John von Neumann's design for the stored-program computer all fed in. But AI as a field is only as old as electronic computers, from around 1940.

Two dates matter most:

1. **1950: the Turing test.** Alan Turing's paper proposed the test you met in the last lesson.
2. **1956: the Dartmouth conference.** A summer workshop organised by John McCarthy, who coined the name "artificial intelligence". Marvin Minsky, Herbert Simon, Allen Newell and Arthur Samuel were there. Most histories count 1956 as the year AI was born.

## The periods of AI
<!-- bite: 3730297d-ca8d-47f9-aa98-e0fd67951ab5 -->

Here's the story on one line. Read it left to right.

![A timeline of AI: the Turing test paper in 1950, the Dartmouth conference in 1956, game playing and theorem proving around 1960, the Lighthill report and an AI winter in 1973, the expert-systems boom in 1980, neural nets returning in 1986, Deep Blue beating Kasparov in 1997, and deep learning taking over in 2012.](../images/ai-history-timeline.svg)

## The four periods
<!-- bite: 4eba7320-3b7e-4a84-b91e-981e0a9e48f2 -->

The course splits the history into periods:

1. **The early period, 1950s and 60s.** Game playing by brute force (calculate your way out), theorem proving by manipulating symbols, and the first biological models: neural nets.
2. **The symbolic period, 1970s.** The first expert systems: programs built from a human expert's knowledge.
3. **The commercial period, 1980s.** A boom in rule-based and knowledge-based systems sold to businesses.
4. **The 1990s onwards.** Real-world applications backed by better theory and evidence: data mining, genetic algorithms, fuzzy logic, agents, neural nets and autonomous systems. From about 2012, deep learning took over much of the field.

## Booms and crashes
<!-- bite: 3fb248ab-5c9b-416d-9ba1-95e387b753b7 -->

AI's progress hasn't been smooth. It goes in stages that follow the money: a boom of promises and funding, then a crash when the promises aren't kept. The crashes are called **AI winters**. The course gives three examples:

1. **Machine translation.** Translators based on grammar rules were built from the 1950s. In 1966 a US government report found they weren't working, and all US funding was cancelled. Working commercial translators only appeared around 1980.
2. **Neural networks.** The first neural-net work was McCulloch and Pitts in 1943. In 1969 Minsky and Papert's book *Perceptrons* showed the limits of simple nets, and work on them nearly stopped. In 1986 a way to train deeper nets was rediscovered, and neural-net research grew massively. It's the root of today's deep learning.
3. **The UK freeze.** In 1973 the Lighthill report told the UK government that AI hadn't delivered, and AI funding there was cut hard.

The course's lesson from all three: **don't claim too much for your discipline.** Overpromising brings the money in fast and drives it out just as fast.

## Advantages and disadvantages of AI
<!-- bite: 2cef5d7c-76e6-46ea-888a-f6e83330467f -->

The course lists these. Learn them as lists, because they're asked for directly.

**Advantages:**

1. More powerful and more useful computers.
2. New and improved interfaces, such as speaking to a device instead of typing.
3. Solving new problems that ordinary programs can't handle.
4. Better handling of information.
5. Relief from information overload: the system sorts and filters so you don't have to.
6. Turning information into knowledge.

## The disadvantages of AI
<!-- bite: 770dff57-8003-419b-9816-a27ebf200ad0 -->

And here are the disadvantages the course lists:

1. Increased costs.
2. Software development is difficult, slow and expensive.
3. There are few experienced programmers.
4. Few practical products have reached the market yet.

The last two points date from when the slides were written. Today there are many AI products, but the cost and difficulty points still hold.

## Terms used in this lesson
<!-- bite: 579a325c-c7e5-4eb8-9682-46e016f654ea -->

1. **Decision theory**: This is the mathematics of choosing well. It combines probability (how likely each outcome is) with utility (how much you value each outcome).
2. **Cybernetics**: This is the study of machines and living things that control themselves through feedback, such as a thermostat or a body keeping its temperature steady.
3. **Dartmouth conference**: This is the 1956 summer workshop where the name "artificial intelligence" was first used. It's usually taken as the birth of the field.
4. **Expert system**: This is a program that captures a human expert's knowledge as rules and applies them, such as a program that suggests a diagnosis from symptoms.
5. **AI winter**: This is a period when funding and interest in AI collapsed after it failed to deliver what was promised.

## Common pitfalls and traps
<!-- bite: 7b5b8634-a9c2-4209-98d9-c620eb42c203 -->

- **Mixing up the Turing test date and the Dartmouth date.** The Turing test is 1950. The name "AI" and the Dartmouth conference are 1956.
- **Thinking AI history is a straight line upwards.** It has crashed several times. Neural nets were nearly abandoned and later came back to dominate.
- **Listing only computer science as a foundation.** The course names six fields. Philosophy, psychology and linguistics are just as much a part of it as maths and engineering.

## Check your understanding
<!-- bite: 42d142c7-138a-48ca-bda5-c4cadd765d20 -->

Try each one before you open the answer.

1. <!-- q: mcq id="a5c2bec9" -->
   Which foundation of AI gave it the "degree of belief" used to handle uncertainty?

   - [ ] Philosophy
   - [x] Mathematics (probability)
   - [ ] Linguistics
   - [ ] Computer engineering

   <details><summary>Answer</summary>

   Mathematics, through probability. Decision theory then combines probability with utility to decide what to do.

   </details>

2. <!-- q: exact id="d2acba8c" answer="1956" -->
   In what year was the Dartmouth conference, where the name "artificial intelligence" was first used?

   <details><summary>Answer</summary>

   1956, organised by John McCarthy. Don't confuse it with 1950, the year of Turing's paper.

   </details>

3. <!-- q: gap id="c405bdef" answers="Lighthill;1973" -->
   In the UK, AI funding was cut hard after the ___ report of the year ___.

   <details><summary>Answer</summary>

   The Lighthill report, 1973. It said AI had not delivered what it promised.

   </details>

4. <!-- q: mcq id="652119b8" -->
   A thermostat measures the room, compares it with the setting, and switches the heater to close the gap. Which foundation of AI studies machines like this?

   - [ ] Linguistics
   - [ ] Psychology
   - [x] Control theory and cybernetics
   - [ ] Philosophy

   <details><summary>Answer</summary>

   Control theory and cybernetics: machines that run themselves through feedback. An AI agent's loop of acting, sensing and adjusting comes from the same idea.

   </details>

5. <!-- q: open id="f24e45eb" -->
   Using one of the course's examples of booms and crashes, explain the lesson "don't claim too much for your discipline."

   <details><summary>Answer</summary>

   Any one of the three works. For example: machine translation was promised in the 1950s, but the grammar-based translators didn't work well, so in 1966 all US funding was cancelled and working translators only arrived around 1980. Overpromising brings funding in quickly, but when results fall short the funding is cut and the whole field suffers, including the good work.

   </details>

6. <!-- q: mcq id="b856c883" -->
   Which of these are disadvantages of AI listed in the course? (choose all that apply)

   - [x] Increased costs
   - [x] Software development is difficult, slow and expensive
   - [ ] It relieves information overload
   - [x] There are few experienced programmers
   - [ ] It gives new and improved interfaces

   <details><summary>Answer</summary>

   Increased costs, slow and expensive development, and few experienced programmers are disadvantages. Relieving information overload and new interfaces are on the advantages list.

   </details>

## Before moving on
<!-- bite: a5af8a03-ebec-4d1b-a6af-c4ee2e8266f9 -->

You're done when you can name the six foundations with one thing each gave AI, put 1950, 1956, 1973 and 1986 in order with what happened, and recite the advantages and disadvantages.

Recap: AI stands on philosophy, mathematics (logic, computation, probability, decision theory), psychology, computer engineering, control theory and linguistics. It was named at Dartmouth in 1956. Its history runs through early game playing and theorem proving, expert systems, a commercial boom, and data-driven AI, with winters in between when it overpromised.

Next, [[artificial-intelligence/01-foundations/05-agents-and-environments|Agents and Environments]] takes the rational agent from lesson 3 and makes it precise: what an agent is made of, and the kinds of world it can live in.

## Related
<!-- bite: cbd9bcc2-3b29-4bf3-8465-6d5146dd0077 -->

- [[control-theory/index|Control Theory]]: the feedback idea that AI borrowed, in depth.
- [[information-theory/index|Information Theory]]: another branch of the mathematics AI stands on.

## About this lesson
<!-- bite: 7e1b13dd-cda4-4242-beb7-5f90a6de6e99 -->

**Level:** introductory, no maths. Lesson 4 of section 01 (foundations). It covers the six foundations of AI, the main historical periods, booms and AI winters, and the advantages and disadvantages of AI.

**Source:** University of Lagos SSG 518 Module 1 slides, *Introduction/History* (the foundations, periods of AI, "fashions in AI", and advantages and disadvantages). Two dates are corrected from the slides: *Perceptrons* by Minsky and Papert was published in 1969, not in the 1950s; and the 1966 US funding cut followed the ALPAC report. Deep Blue (1997) and deep learning (2012) are added to bring the timeline up to date.
