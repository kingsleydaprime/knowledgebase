---
id: 8e4428c2-3ecb-4aa5-95df-44a0146895bb
---

# The Simulation Study 2: The Ten Steps, the Challenges and the Tools

The SSG 517 class uses a ten-step version of the simulation study, which says the same thing as the twelve steps in fewer words.

## Before you start
<!-- bite: d8e496fc-64e5-4b18-b9ce-32c0a02e5e4d -->

You should have read [[systems-simulation/07-the-simulation-study-1|07 — The Simulation Study 1]].

After this lesson you will be able to:

1. list the ten steps of the class version, and match them to the twelve;
2. name the challenges that run through every simulation study;
3. sort simulation software into kinds and choose one for a job.

## What the ten-step version is
<!-- bite: 67566106-c569-4bb4-938f-0e7df57b36be -->

The twelve steps came from the textbook. Your class notes use ten, and an exam may ask for either. This lesson gives the ten, shows exactly where they merge the twelve, then covers two things every study meets whatever list you use: the challenges, and the choice of software.

## The ten steps
<!-- bite: 9f025e70-4010-4506-81c7-2013db43d29d -->

1. **Problem definition:** identify the basic problem or question the model must answer.
2. **Setting of objectives:** define the criteria the system must optimise or satisfy.
3. **Model conceptualisation (system analysis):** analyse the system's components, variables, parameters, relationships, outputs and behaviours.
4. **Data collection:** gather and process the data needed to describe the system.
5. **Model formulation:** design the model: structure, logic, assumptions, equations, the modelling approach and the software tool.
## The ten steps: building and using the model
<!-- bite: 8aec2899-6c14-41fe-a30e-24dc81dea8c8 -->

The second half builds, checks, runs and presents the model.

6. **Model implementation (translation):** build it in the chosen software, including coding, testing and documenting.
7. **Model verification:** check it is implemented correctly and completely. Did we build it right?
8. **Model validation:** check it is accurate and credible enough to stand for the real system. Did we build the right model?
9. **Model experimentation:** run it under different scenarios to answer the problem, including analysis and optimisation.
10. **Documentation and communication:** present the model and its results to the audience.

Steps 1 to 3 are circled together in the class notes: they are the "understand the problem" block. A memory hook: **define, aim, analyse, gather, formulate, build, verify, validate, experiment, communicate.**

## How the two lists line up
<!-- bite: 5bdbed7d-8c90-42c0-99d7-5a1ff4db62a9 -->

The model-building core is the same in both. The ten-step version merges at the two ends, and splits one step in the middle.

| Ten steps | Twelve steps |
| --- | --- |
| 1 Problem definition | 1 Problem formulation |
| 2 Setting of objectives | 2 Objectives and overall design |
| 3 Conceptualisation | 3 Conceptualisation |
| 4 Data collection | 4 Data collection |
| 5 Formulation, 6 Implementation | 5 Translation |
| 7 Verification | 6 Verification |
| 8 Validation | 7 Validation |
| 9 Experimentation | 8 Experimental design, 9 Production runs, 10 More runs |
| 10 Documentation and communication | 11 Documentation, 12 Implementation |

## How the topics of this subject connect
<!-- bite: fc2a6b10-90c7-46fe-896e-99a43fac9da8 -->

The steps also give the order of this subject. Each link feeds the next:

1. **Problem and system definition:** what question, and what's inside the boundary? (lessons 01–08)
2. **Model building:** inputs, outputs, relationships and rules (lessons 25–26)
3. **Data and input analysis:** the distributions that describe the randomness (lessons 27–30)
4. **Random numbers:** turning those distributions into numbers a computer can make (lessons 16–22)
5. **Build and run:** a discrete-event model, such as a queue (lessons 09–15 and 35–38)
6. **Verify and validate:** built right, and the right model? (lessons 31–33)
7. **Experiment, analyse, recommend:** replications, confidence intervals, comparisons (lesson 34)

If one link is weak, everything after it is weak. That is the idea behind **garbage in, garbage out**.

## The challenges
<!-- bite: 8b7a8b5b-8afc-4547-8f09-9f9a99296bd0 -->

Both courses name the same challenges, which apply at every step:

1. **Data availability and quality:** the data may be missing, thin or messy.
2. **Model complexity and realism:** more realism means more to build, check and explain.
3. **Uncertainty and sensitivity:** random inputs and uncertain parameters make results vary.
4. **Scalability and efficiency:** big models can take a long time to run.
5. **Usability and accessibility:** the people who need the model must be able to use and trust it.
6. **Communication of results:** presenting random, technical results to managers. The class notes tick this one, so it was probably stressed.

## Simulation software
<!-- bite: 4316b257-ce76-44e2-a68a-087ec71146ee -->

Software can be sorted four ways:

1. **General purpose** (MATLAB, Python, Excel) or **specific purpose** (Arena, Stella, NetLogo).
2. **Graphical** (Simulink, AnyLogic, Vensim) or **textual** (R, C++, Java).
3. **Discrete-event** (Arena, SimPy, SimEvents) or **continuous** (Stella, Simulink, Berkeley Madonna).
4. **Desktop** or **web based**.

Choose by the type of system, the level of detail you need, the purpose, your budget and your experience. Good software gives ready-made building blocks, input and output analysis tools and animation, so models are built and checked faster, and results are easier to show to stakeholders.

## Common pitfalls
<!-- bite: 596b4369-af2d-4402-9b09-0d65961b2a1e -->

1. **Mixing the two lists in one answer.** Pick one and use it all the way through.
2. **Leaving out communication.** Both lists end with telling people; the ten-step version names it outright.
3. **Choosing software by habit.** A continuous process doesn't belong in a discrete-event package.

That completes the overview. Next lesson starts the core of SSG 517: discrete-event simulation, and how a computer jumps from one event to the next.

## Check your understanding
<!-- bite: 3278e43d-ac6e-4096-9de0-d727cb72742a -->

Try each one before you open the answer.

1. <!-- q: mcq id="ab767319" -->
   In the ten-step version, which single step covers the twelve-step list's experimental design, production runs and more runs?

   - [ ] Model formulation
   - [ ] Model validation
   - [x] Model experimentation
   - [ ] Documentation and communication

   <details><summary>Answer</summary>

   Model experimentation, step 9: running scenarios, analysing and optimising.

   </details>

2. <!-- q: gap id="21c25187" answers="verification;validation" -->
   "Did we build it right?" is the question of model ___. "Did we build the right model?" is the question of model ___.

   <details><summary>Answer</summary>

   Verification, then validation.

   </details>

3. <!-- q: mcq id="54e099ad" -->
   A team needs to model heat flowing through a furnace wall, a continuous process. Which tool suits it best?

   - [ ] Arena
   - [ ] SimPy
   - [x] Simulink
   - [ ] GPSS

   <details><summary>Answer</summary>

   Simulink, a continuous simulation tool. Arena, SimPy and GPSS are discrete-event.

   </details>

4. <!-- q: open id="8644d4db" -->
   Explain "garbage in, garbage out" using the chain of topics in this lesson.

   <details><summary>Answer</summary>

   Each link feeds the next: the problem shapes the model, the data shapes the input distributions, the distributions shape the random numbers, and the run produces results. If one link is poor, for example the input data is wrong, every later link inherits the error, so the results are wrong however good the model and software are.

   </details>

5. <!-- q: open id="71356574" -->
   Name three of the challenges common to all simulation studies, with a one-line example of each.

   <details><summary>Answer</summary>

   Any three, for example. Data quality: a hospital's records miss the patients who left before being seen. Complexity: modelling every machine part makes the model too slow to check. Uncertainty: random arrivals give different results each run. Communication: managers want one number, but the model gives a range.

   </details>

## Before moving on
<!-- bite: 70be6d25-f409-4e65-9c8d-11934fbee4f2 -->

You can give the ten steps, map them onto the twelve, name the challenges and choose a tool. **Next:** [[systems-simulation/09-discrete-event-simulation|09 — Discrete-Event Simulation]].

## Related
<!-- bite: 432f3da1-b587-4245-8a3e-24e96b953ea8 -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: df1a105e-bda9-4ee1-9ae3-d04f2eb4e1f9 -->

**Level:** Beginner. **Covers:** the ten-step class version, how it maps onto the twelve steps, how the topics of the subject connect, the challenges, and kinds of simulation software.

**Where it sits:** lesson 08 of 38, part 2 of 2 on the simulation study.

**Source:** the author's own SSG 418 and SSG 517 study notes, sections 1 and D.
