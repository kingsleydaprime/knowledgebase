---
id: 96e4c1a0-0c5b-4c4b-8745-72e0c8b518c8
---

# Types and Components of Simulation Models

There are five types of simulation model, and every one is assembled from the same set of components.

## Before you start
<!-- bite: 2d964f8e-647f-41b8-a1f2-c8a49fdd55dc -->

You should have read [[systems-simulation/05-modelling-2|05 — Modelling 2]].

After this lesson you will be able to:

1. name the five types of simulation model and match each to a problem;
2. list the components of a simulation model;
3. name common tools for building simulation models.

## What a simulation model is
<!-- bite: 37f9cfe2-bb27-441a-9e58-590177f3f65c -->

Lessons 03 to 05 were about systems and models in general. From here on the focus is simulation models specifically, the ones you run over time on a computer. This lesson is the map of what kinds exist and what they are made of. Part 2 of the course (SSG 517) mostly uses one type, discrete-event simulation, so that one gets the most space later.

## The five types
<!-- bite: ee50be98-13c9-4728-8dac-4dfeb5d01b61 -->

1. **Discrete-event:** the system changes only at specific moments, such as a customer arriving or a machine breaking. Used for hospitals, queues and assembly lines. This is the main type in this subject, from lesson 09 on.
2. **Continuous:** the system changes smoothly with time and is described by differential equations, like the RC filter in lesson 05. Used for fluids, heat and chemical reactions.
3. **Agent-based:** the system is many autonomous agents, each following its own rules and reacting to the others and its surroundings. Used for markets, social systems and epidemics.
4. **Monte Carlo:** repeated random sampling to get a numerical answer, usually where time doesn't matter. Used for risk assessment, or estimating an area or a profit. Lesson 22 builds one.
5. **Hybrid:** a mix of the above, for a system with both discrete and continuous parts. The author's class notes mark it "not included most times".

## Choosing the type
<!-- bite: 5a61b793-a6a8-4023-8a88-c184a9e76bc7 -->

Ask what changes, and how.

1. Things happen at instants, and you care about queues and waiting? **Discrete-event.**
2. Quantities flow smoothly, like temperature or level? **Continuous.**
3. The interesting behaviour comes from many individuals reacting to each other? **Agent-based.**
4. There is no clock, just uncertainty to average over? **Monte Carlo.**
5. Both instants and smooth flows matter? **Hybrid.**

## The components of a simulation model
<!-- bite: cccad0f7-46df-4767-9fca-81d47a5d7032 -->

Every simulation model is built from these parts. They extend the five components of lesson 03.

1. **Entities:** These are the dynamic objects that move through the system, such as customers or parts.
2. **Attributes:** These are properties of one entity, such as a part's type.
3. **Events:** These are instants that change the state, such as an arrival.
4. **States:** A state is a snapshot of the whole system at one moment.
5. **Variables:** These describe the system at large, not tied to any one entity, such as the number in the queue.
## The components of a simulation model: measures, resources and logic
<!-- bite: 2ae7de26-730f-40a3-a425-6f0891f8124d -->

The last four components say how the model is judged and how it runs.

6. **Performance measures:** These are the numbers you judge the system by, such as waiting time, utilisation and throughput.
7. **Resources:** These provide service or capacity to entities, such as a teller or a machine, and have an availability and a utilisation.
8. **Queues:** These hold entities waiting for a resource.
9. **Activities and logic:** Activities are work that takes time. The logic, or functional relationships, are the rules saying how the parts interact and how entities flow.

The model also needs a **boundary**: what is inside the system, and what is outside in its environment.

## Example: a clinic, in components
<!-- bite: 11290442-64bc-4e0b-aa47-357506c2e43f -->

A small clinic, described with the list:

| Component | In the clinic |
| --- | --- |
| Entities | Patients |
| Attributes | Age, illness, arrival time |
| Events | Patient arrives, consultation starts, patient leaves |
| Variables | Number waiting, doctor busy or free |
| Resources | Doctor, consulting room |
| Queues | The waiting room |
| Activities | Consultation |
| Logic | Serve in order of arrival, but emergencies first |
| Performance measures | Average wait, doctor utilisation |
| Boundary | Inside: reception to exit. Outside: the pharmacy down the road |

## Tools
<!-- bite: 3d3a8457-0aa7-4631-9e51-8118cb9950b9 -->

Common tools for building and running simulation models: **Arena**, **AnyLogic**, **Simulink**, **NetLogo** and **Python** (for example with the SimPy library). Lessons 35 to 38 use Arena, and lesson 08 says how to choose a tool.

## Common pitfalls
<!-- bite: 86cce1b2-8200-4f71-955b-a573a4291f2d -->

1. **Using discrete-event for everything.** A dam's water level is continuous; an epidemic driven by individual contacts may need agent-based.
2. **Forgetting resources and queues.** In a queueing model they are where the waiting happens.
3. **No boundary.** Without one, the model keeps growing.

We know what a simulation model is made of. Next lesson is about the *process* of a simulation study: the twelve steps from stating the problem to putting the answer into practice.

## Check your understanding
<!-- bite: a2c327d0-a764-4fbf-8d53-c4559e423350 -->

Try each one before you open the answer.

1. <!-- q: mcq id="c8becc63" -->
   A health agency wants to see how a flu spreads through a town, where each person meets others and may get infected. Which type of simulation fits best?

   - [ ] Continuous
   - [x] Agent-based
   - [ ] Monte Carlo
   - [ ] Hybrid

   <details><summary>Answer</summary>

   Agent-based. The spread comes from individuals interacting, each following simple rules, which is what agent-based models capture.

   </details>

2. <!-- q: mcq id="ef3853d5" -->
   An insurer wants the probability that total claims next year exceed ₦2 billion, by sampling possible claims thousands of times. There is no clock in the model. Which type is this?

   - [ ] Discrete-event
   - [ ] Continuous
   - [x] Monte Carlo
   - [ ] Agent-based

   <details><summary>Answer</summary>

   Monte Carlo: repeated random sampling with no role for time.

   </details>

3. <!-- q: gap id="6b78f533" answers="resources|resource;queues|queue" -->
   In a simulation model, ___ give service or capacity to entities and have a utilisation, and ___ hold the entities waiting for them.

   <details><summary>Answer</summary>

   Resources, then queues. A teller is a resource; the line in front of the teller is a queue.

   </details>

4. <!-- q: open id="86838952" -->
   For a car wash with two washing bays, name the entities, one resource, one queue, one activity and two performance measures.

   <details><summary>Answer</summary>

   Entities: cars. Resource: a washing bay (or the staff). Queue: the line of cars waiting at the entrance. Activity: washing a car. Performance measures: average waiting time, bay utilisation, or cars washed per hour.

   </details>

5. <!-- q: mcq id="d1fbd132" -->
   Which tool is most associated with drag-and-drop discrete-event models built from modules like CREATE, PROCESS and DISPOSE?

   - [x] Arena
   - [ ] NetLogo
   - [ ] Simulink
   - [ ] A spreadsheet

   <details><summary>Answer</summary>

   Arena. NetLogo is mainly agent-based, and Simulink mainly continuous.

   </details>

## Before moving on
<!-- bite: 1496d764-8dab-4f63-adf6-5c9de43874ef -->

You can name the five types of simulation model, choose between them, and list the components. **Next:** [[systems-simulation/07-the-simulation-study-1|07 — The Simulation Study 1]]: the twelve steps of a study.

## Related
<!-- bite: 05da7ebc-4494-40c4-8abf-839059fec633 -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: 2b644eb0-0cdd-4739-af40-689ae0b52797 -->

**Level:** Beginner. **Covers:** the five types of simulation model and how to choose, the components of a simulation model, and common tools.

**Where it sits:** lesson 06 of 38, the end of part 1 (systems and models).

**Source:** the author's own SSG 418 and SSG 517 study notes, section 1 and the class 1 review. The clinic and car wash examples are added for this lesson.
