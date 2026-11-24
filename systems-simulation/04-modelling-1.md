---
id: 7821b634-632a-47a4-9979-11073dd7003c
---

# Modelling 1: Why We Model and How Purpose Shapes the Model

Modelling is abstracting a real system into a form you can study, and the question you are asking decides what the model must keep.

## Before you start
<!-- bite: 2a9deb0d-e222-4b2a-8699-1befc67657fe -->

You should have read [[systems-simulation/03-systems-and-their-components|03 — Systems and Their Components]].

After this lesson you will be able to:

1. explain why models are needed, with examples of questions you can't answer by measuring;
2. describe the trade-off between simplicity and accuracy;
3. show how the same object gets different models for different purposes, and classify a model.

## What modelling is
<!-- bite: 104c4899-8889-4508-9985-722c61d97dc6 -->

**Modelling** is the process of abstracting a real system: organising what you know about it into a form useful for science and engineering. The word comes from the Latin for a mould or pattern.

This lesson is about the thinking behind a model, before any equations. Why build one at all, what pulls a model in two directions at once, and how to pick the right kind of model for your question. Lesson 05 then builds mathematical models from physical laws.

## Why we need models
<!-- bite: d9fa928f-0a6f-4f3b-9649-ba239961c033 -->

Some questions can't be answered by direct measurement. The lecture opens with examples like these:

1. How tall is that tower, without climbing it?
2. How wide is the river, without crossing it?
3. What is the mass of the Earth?
4. What is the temperature at the centre of the sun?
5. What will Nigeria's population be in 2050?
6. What would a 30% income tax cut do?
7. How long does a light bulb last on average?
8. How many insurance claims will come in next year?

You can't put the Earth on a scale or wait until 2050. A model lets you answer anyway: trigonometry for the tower, gravity equations for the Earth, a population growth model for 2050.

## Simplicity against accuracy
<!-- bite: 4fd0ab46-cd88-4d87-9195-4815d3c2842d -->

Every model is a balance between two things that pull against each other:

1. **Simplicity:** a simple model is quick to build, easy to understand and cheap to run.
2. **Accuracy (faithfulness):** an accurate model behaves like the real system in more situations.

Add detail and the model gets more faithful, but slower, harder to check and more hungry for data. Strip detail and it gets easier, but may miss the very effect you care about. The skill is keeping just enough detail to answer the question.

## The purpose decides the model
<!-- bite: 26dbbe99-a694-401e-98da-47c1f164122b -->

The same aircraft can be modelled three ways, depending on what you want to know.

1. **As a particle,** a single point with mass, if you only want its flight path to work out fuel use. Simple, and enough.
2. **As a system of rigid bodies,** if you want flight stability: how it reacts to small disturbances such as a gust.
3. **As a system of deformable bodies,** for flutter analysis: finding the critical speed at which the wings start to vibrate dangerously.

None of the three is "the" model of an aircraft. Each is right for its question, and the other two would be either too crude or wastefully detailed.

What goes into developing a model, from the lecture figure: the system and its boundaries, the purpose, the level of detail, the performance measure, and the design alternatives you want to compare.

## Classifying models
<!-- bite: 689ecbc3-631f-4419-8759-0843592f84ea -->

Models split first into two families.

1. **Physical models:** prototypes, models at reduced scale, real models you can touch.
2. **Abstract models:** mathematical, descriptive, logical and neural network models.

Mathematical models are then split in five ways: static or dynamic, continuous or discrete, ordinary or partial differential equations (ODE or PDE), linear or nonlinear, and deterministic or stochastic. These are the same labels lesson 03 used for systems.

## How kinds of model compare
<!-- bite: 20dcd223-8c71-408b-9793-a2e307e1a703 -->

Different kinds of model suit different jobs.

| Kind | Good at describing? | Ambiguous? | Used for |
| --- | --- | --- | --- |
| English text | Well | Very | Explanations and directions |
| Drawings and block diagrams | Well | No | Design and assembly |
| Flow charts and decision tables | Fairly | Not much | Turning into computer programs |
| Curves, tables, nomographs | Fairly | Not much | Simple relations between a few variables |
| Mathematical models | Poorly, in words | No | Solving problems and optimising |

A mathematical model is hard to read like prose, but it has one meaning only and you can manipulate it, which is why simulation is built on it.

## Common pitfalls
<!-- bite: cb4130cd-caab-4097-b96e-c3c484b884e3 -->

1. **Thinking more detail is always better.** Detail costs time, data and checking. Keep only what the question needs.
2. **Picking the model before the question.** Decide the purpose first; the purpose picks the model.
3. **Treating "model" as only equations.** Drawings, flow charts and scale prototypes are models too.

So far the model is an idea. Next lesson turns it into equations: how to build a mathematical model from physical laws, and when a simple linear version is good enough.

## Check your understanding
<!-- bite: 1b4aaafd-775c-4ef1-9474-fe65c408a25c -->

Try each one before you open the answer.

1. <!-- q: gap id="054a4114" answers="simplicity|simple;accuracy|faithfulness|accurate" -->
   When building a model you must balance two things that pull against each other: ___ and ___.

   <details><summary>Answer</summary>

   Simplicity and accuracy (faithfulness). More detail makes a model more faithful but slower and harder to check.

   </details>

2. <!-- q: mcq id="887dff4d" -->
   An engineer only wants to estimate how much fuel an aircraft uses on a flight. Which model is enough?

   - [x] A particle: a single point with mass following the flight path
   - [ ] A system of rigid bodies
   - [ ] A system of deformable bodies
   - [ ] A full-size prototype

   <details><summary>Answer</summary>

   A particle. The flight path is all fuel use needs. Rigid bodies are for stability and deformable bodies for flutter.

   </details>

3. <!-- q: mcq id="7e6a7efc" -->
   Which of these is a physical model rather than an abstract one?

   - [ ] A set of equations for heat flow
   - [ ] A flow chart of a hospital's triage
   - [x] A one-tenth scale model of a bridge tested in a wind tunnel
   - [ ] A neural network that predicts demand

   <details><summary>Answer</summary>

   The scale bridge. Equations, flow charts and neural networks are all abstract models.

   </details>

4. <!-- q: mcq id="d4b6cda9" -->
   Which kind of model is poor at describing a system in words, but not ambiguous and excellent to manipulate?

   - [ ] English text
   - [ ] Drawings
   - [ ] Curves and nomographs
   - [x] Mathematical models

   <details><summary>Answer</summary>

   Mathematical models. That is why they are used for solving problems and optimising, and why simulation is built on them.

   </details>

5. <!-- q: open id="e78c8ab2" -->
   A city wants to model traffic to decide whether to add a lane on one road. Name two things that should go into developing this model, using the lecture's list.

   <details><summary>Answer</summary>

   Any two of: the system and its boundaries (which roads and junctions are inside), the purpose (decide on the extra lane), the level of detail (individual cars, or flows per minute), the performance measure (average journey time or queue length), and the design alternatives (with and without the lane).

   </details>

## Before moving on
<!-- bite: 2dd38b68-a5e7-4256-a12d-f0736411ef75 -->

You can say why we model, describe the simplicity–accuracy balance, and match a model to its purpose. **Next:** [[systems-simulation/05-modelling-2|05 — Modelling 2]]: building mathematical models from physical laws.

## Related
<!-- bite: edc3e1e8-b90a-418f-82d5-31a796ac8c13 -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: 792aa187-e547-4e2c-95ca-c179e309dd43 -->

**Level:** Beginner. **Covers:** why models are needed, what modelling is, simplicity versus accuracy, the three aircraft models, classifying models, and how kinds of model compare.

**Where it sits:** lesson 04 of 38, part 1 of 2 on modelling.

**Source:** the author's own SSG 418 and SSG 517 study notes, section C.
