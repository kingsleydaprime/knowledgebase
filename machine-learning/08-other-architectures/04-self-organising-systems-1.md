---
id: 51d16908-8469-4b82-bbb5-37c416caac98
---

# Self-Organising Systems 1: Order Without a Boss

A self-organising system is one where order appears on its own, from parts reacting to their neighbours.

## Before you start
<!-- bite: c6fb1008-ab4d-412b-8969-6dac23863c8d -->

You don't need anything new for this part. It helps to have met [[machine-learning/03-classical-ml/17-clustering-1|clustering]] and [[machine-learning/03-classical-ml/04-learning-vector-quantization|LVQ]], because self-organising maps come up at the end and they are close cousins of both.

After this lesson you will be able to:

- define a self-organising system, in plain words and in the exam version;
- explain local interactions, feedback loops and emergence with one example;
- give five examples of self-organisation from nature and people;
- name the four types of self-organising system used in AI and what each is for.

## What a self-organising system is
<!-- bite: 46592ad3-51c7-4401-a8e2-3da0575ee5e2 -->

Think about a flock of birds. Hundreds of them turn together in the sky like one animal, and there is no leader bird shouting "turn left now!". Each bird only watches the few birds right next to it: stay close, don't crash, fly the same way they're flying. That's all. Yet the whole flock ends up moving in one smooth shape.

That is self-organisation. No one is in charge, nobody outside the flock is giving orders, and each part only follows simple local rules. Still, order appears.

A one-sentence version for an exam: Self-organising systems are structures that spontaneously form without external guidance. Put another way, a self-organising system is one in which overall order arises from local interactions between parts of an initially disordered system, without external intervention.

We'll keep the flock with us through this whole lesson. Every idea that follows, you can check against it.

## Why AI cares about self-organisation
<!-- bite: 5850208b-5169-474b-92f5-30e53d431692 -->

Most programs work like a boss with a to-do list: one central piece of code decides everything. Self-organising systems work the other way, and AI is interested in them for three reasons:

1. **More intelligent and adaptable systems.** A system that organises itself can keep reorganising when things change, without a programmer stepping in.
2. **Inspiration from nature.** Flocks, ant colonies and brains already solve hard problems this way, and have been doing it for a long time.
3. **Fixing limits of traditional AI.** A central controller is a single point of failure and gets slow as the system grows. Spreading the work across many simple parts avoids both.

This is why self-organisation matters for AI tasks like **clustering**, **pattern recognition** and **decentralised decision-making** (decisions made by many parts together, with no central decider).

## Terms used in self-organising systems
<!-- bite: 6c6d111f-d8db-49b3-bc25-b5ab210df6c0 -->

1. **Self-organisation**: This is the process by which a system forms structures and patterns on its own, with nobody outside arranging them.
2. **Local interactions**: This means each part reacts only to its immediate neighbours, not to the whole system. A bird watches the few birds beside it, not the entire flock.
3. **Feedback loop**: This is when the result of an action comes back and affects the next action. A **positive feedback** loop strengthens a change: the more birds turn, the more of their neighbours turn too. A **negative feedback** loop holds a change back: a bird that gets too close to its neighbour moves away.
4. **Emergence**: This is when a complex pattern appears from simple rules, a pattern that no single part planned or can even see. The flock's shape is emergent: no bird is drawing it.
5. **Adaptability**: This means the system adjusts when its environment changes. When a hawk dives in, the flock splits and re-forms without anyone directing it.

## How it works: the three components
<!-- bite: 94efeff2-8301-4ec4-a024-5554c13e16d3 -->

Every self-organising system is built from the same three pieces, and the flock shows all of them:

1. **Local interactions.** The parts (agents or components) act only on local information, what their neighbours are doing right now. No bird knows the shape of the flock.
2. **Feedback loops.** Positive feedback spreads and strengthens a pattern, like a turn rippling through the flock. Negative feedback keeps the pattern stable, like birds keeping their spacing. Positive feedback can destabilise a structure and negative feedback can stabilise it, and the system needs both.
3. **Emergence.** Put many local interactions and feedback loops together, and a pattern appears at the level of the whole system: the flock.

So local interactions and feedback loops are the **mechanisms**, the way it happens. Emergence is the **result**, what you see. Remember this one: simple local rules plus feedback give emergent order.

## Examples from nature and people
<!-- bite: 6a85fed8-8b87-4e48-a165-3bb0bf2618b4 -->

Once you know what to look for, self-organisation is everywhere:

1. **Birds in flight.** Each bird follows its neighbours, and the flock moves smoothly through the air as one.
2. **Spontaneous magnetism.** In a magnet, tiny magnetic units start pointing in random directions. Each one tends to line up with its neighbours, the alignments reinforce each other (positive feedback), and the whole piece of metal ends up with one overall magnetic effect.
3. **Cellular automata.** These are grids of cells where each cell changes its state using simple rules about its neighbours. The states evolve and can settle into an equilibrium after some time.
4. **Herd mentality.** Animals herd together and move together without guidance from outside.
5. **Groupthink.** People in a group sometimes reach an irrational conclusion because each person wants to conform to the others' ideas.

The last one is a warning. Self-organisation doesn't always produce *good* order. Groupthink is positive feedback with nothing to hold it back, and the group arrives somewhere no one would have gone alone.

## Types of self-organising system in AI, part 1
<!-- bite: 3ffaa927-4932-44fa-a7b0-8bc74ff4955b -->

The examples above are found in nature. AI borrows the same idea and builds four types of system with it. The first two:

1. **Self-organising maps (SOMs).** These are neural networks that learn to map high-dimensional data (data with many columns) onto a low-dimensional space, usually a flat grid. Similar data points end up on nearby spots of the grid. They are used for data visualisation, pattern recognition and clustering.
2. **Cellular automata.** These are discrete models made of a grid of cells, where each cell has a finite number of states and changes state according to rules about its neighbours. They are used to simulate complex systems and for artificial life.

## Types of self-organising system in AI, part 2
<!-- bite: 0ddfccdb-8d66-4ffd-8c4d-508f2a4c0e96 -->

The other two types:

3. **Multi-agent systems.** These are groups of agents (independent programs or robots) that interact and adapt to achieve a shared goal. A team of warehouse robots sharing out deliveries among themselves is one.
4. **Evolutionary algorithms.** These are optimisation algorithms inspired by natural selection. Many candidate solutions compete, the better ones are kept and combined, and over many generations good solutions emerge. They are used for optimisation problems and in machine learning.

Notice that every type has the three components again: parts, local rules, and order that emerges.

## Check your understanding
<!-- bite: d25b2b7c-db21-4e16-8486-a668c7143fe4 -->

Try each one before you open the answer.

1. <!-- q: open id="6c3d9720" -->
   Define a self-organising system.

   <details><summary>Answer</summary>

   A system in which overall order arises from local interactions between the parts of an initially disordered system, without any external guidance or intervention.

   </details>

2. <!-- q: mcq id="939bbe4d" -->
   In a school of fish, each fish swims away from any fish that comes too close. Which mechanism is this?

   - [ ] Positive feedback
   - [x] Negative feedback
   - [ ] Emergence

   <details><summary>Answer</summary>

   Negative feedback. It holds a change back (fish getting too close) and keeps the school stable.

   </details>

3. <!-- q: gap id="11799428" answers="emergence" -->
   Fill in the gap. When a complex pattern that no single part planned appears from simple local rules, it is called ___.

   <details><summary>Answer</summary>

   Emergence.

   </details>

4. <!-- q: mcq id="10330329" -->
   Which type of self-organising system is a neural network that maps data with many columns onto a flat grid?

   - [x] Self-organising map
   - [ ] Cellular automaton
   - [ ] Evolutionary algorithm
   - [ ] Multi-agent system

   <details><summary>Answer</summary>

   A self-organising map (SOM). It puts similar data points on nearby spots of a low-dimensional grid.

   </details>

5. <!-- q: mcq id="7d472a7d" -->
   Which of these are examples of self-organisation? Choose all that apply.

   - [x] Tiny magnetic units lining up into one overall magnet
   - [x] A herd of animals moving together with no leader
   - [ ] A traffic warden directing every car at a junction
   - [x] A group reaching a bad decision because everyone conforms

   <details><summary>Answer</summary>

   Magnetism, herding and groupthink. The traffic warden is external guidance, the opposite of self-organisation.

   </details>

6. <!-- q: open id="e9289232" -->
   Give two reasons AI researchers are interested in self-organising systems.

   <details><summary>Answer</summary>

   Any two of: they can make AI more intelligent and adaptable, because the system reorganises itself when things change; nature already solves hard problems this way, so it is a source of ideas; and they avoid the limits of a central controller, which is a single point of failure and slows down as the system grows.

   </details>

## Before moving on
<!-- bite: ca93e79f-1dcb-448c-8065-d403a28abb7f -->

You're done when you can explain a flock of birds using the words local interactions, feedback loops and emergence, and name the four types of self-organising system in AI.

The short version: order appears without a boss when simple parts follow local rules and feedback loops spread or steady the pattern. AI uses this in self-organising maps, cellular automata, multi-agent systems and evolutionary algorithms.

**Next:** [[machine-learning/08-other-architectures/05-self-organising-systems-2|Self-Organising Systems 2]]. Now that you know what self-organisation is, part 2 shows it doing real work: a self-organising map learning by hand, swarms finding short paths, and where all this is used.

## About this lesson
<!-- bite: fac2c80e-b149-41c3-9af9-e2e817053000 -->

**Level:** Intermediate. Part 1 of 2 on self-organising systems. **Covers:** the definition, why AI cares, the key characteristics, the three components, five examples and the four types of self-organising system. **Source:** SSG 518 (Introduction to Artificial Intelligence Systems), Module 2: Self-Organising System, class slides. The flock of birds as one running example was added to tie the slides' points together.
