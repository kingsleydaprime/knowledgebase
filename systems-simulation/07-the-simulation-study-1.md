---
id: 6758d8b0-1121-48aa-bb2c-8bc4d5e52966
---

# The Simulation Study 1: The Twelve Steps

A simulation study follows twelve steps in four phases, from stating the problem to putting the answer into practice.

## Before you start
<!-- bite: 143d2fc6-e734-4b35-830e-b08796e14ba0 -->

You should have read [[systems-simulation/06-types-and-components-of-simulation-models|06 — Types and Components of Simulation Models]].

After this lesson you will be able to:

1. list the twelve steps of a simulation study in order;
2. group them into the four phases;
3. say what each step produces and why some steps loop back.

## What a simulation study is
<!-- bite: ef9ce292-4087-453c-970f-70ded2ade8b3 -->

A **simulation study** is the whole project around a model: understanding the problem, building the model, running it and getting the answer used. Writing the code is one step out of twelve. The list here comes from Banks, Carson, Nelson and Nicol, the standard textbook, and it is the list the SSG 418 lectures use. Exams ask for it directly ("list the steps") and inside case questions ("describe how you would carry out this study").

## Phase 1: Planning
<!-- bite: 74d2ce76-0e78-4490-a154-04b8c181ae02 -->

1. **Problem formulation.** State the problem clearly. If the client and the analyst understand the problem differently, everything after is wasted.
2. **Setting of objectives and overall design.** Write the questions the simulation must answer, and plan the project: people, time and cost.

## Phase 2: Building the model
<!-- bite: d10a49a6-207c-4aa2-9e48-422a1d94f5df -->

3. **Model conceptualisation.** Abstract the essential features of the system and choose the assumptions. Start with a simple model and enrich it later.
4. **Data collection.** Collect the data the model needs. Start early, alongside step 3, because it can take a long time.
5. **Model translation.** Turn the conceptual model into a computer program, in a language like GPSS or a package like Arena.
6. **Verification.** Is the computer program working properly, the way the conceptual model says?
7. **Validation.** Does the model accurately represent the real system?

## Phase 3: Running it
<!-- bite: e7ad79cf-16e4-4fcd-9ef1-045ac560ce46 -->

8. **Experimental design.** Decide which alternatives to simulate, how long each run lasts, and how many runs.
9. **Production runs and analysis.** Run the experiments and estimate the performance measures: averages, probabilities, frequencies.
10. **More runs?** Check whether the results are accurate enough statistically. If not, go back and run more.

## Phase 4: Reporting
<!-- bite: 0b08256e-f9ee-430b-84b3-518b03275805 -->

11. **Documentation and reporting.** Document the program (so it can be reused) and report the progress and results.
12. **Implementation.** Put the recommendation into practice. Its success depends on how well the earlier steps were done.

## The steps as a flow
<!-- bite: 882356e6-b352-4787-9263-058e4b2715e4 -->

The twelve steps aren't a straight line. Verification and validation send you back when they fail, and step 10 sends you back for more runs.

![A flowchart of the twelve steps of a simulation study in four phases: planning (problem formulation, objectives), building (conceptualisation, data collection, translation, verification, validation), running (experimental design, production runs, more runs) and reporting (documentation, implementation), with loops back from verification to translation, from validation to conceptualisation and data collection, and from more runs to production runs](images/ss-simulation-study.svg)

Follow the arrows: a failed verification goes back to translation (fix the code), a failed validation goes back to conceptualisation and data (fix the model or its inputs), and "more runs? yes" goes back to production runs.

## Common pitfalls
<!-- bite: d3097e10-8fb2-4082-a5d3-d0bd597f61d2 -->

1. **Treating it as a straight line.** The loops at verification, validation and more runs are part of the method.
2. **Starting data collection late.** It is step 4, but it should start as early as possible.
3. **Confusing verification and validation.** Verification compares the program with the conceptual model; validation compares the model with the real system. Lesson 31 covers both in depth.
4. **Forgetting implementation.** A model nobody acts on has done nothing.

These twelve steps are the textbook version. Your SSG 517 class used a ten-step version, and the next lesson lines the two up so you can answer with either.

## Check your understanding
<!-- bite: 97f283cf-9eed-429b-8ed9-0b0e74e615e5 -->

Try each one before you open the answer.

1. <!-- q: mcq id="9444db84" -->
   Which step comes straight after model translation?

   - [ ] Data collection
   - [x] Verification
   - [ ] Validation
   - [ ] Experimental design

   <details><summary>Answer</summary>

   Verification: once the model is a program, check the program works as the conceptual model says. Validation comes next.

   </details>

2. <!-- q: gap id="e06c8037" answers="planning;building|building the model|model building;running|running it|experimentation;reporting" -->
   The twelve steps fall into four phases: ___, ___, ___ and ___.

   <details><summary>Answer</summary>

   Planning (steps 1–2), building the model (3–7), running it (8–10) and reporting (11–12).

   </details>

3. <!-- q: mcq id="f0845707" -->
   During validation, the model's average queue at a bank is three times what the real bank shows. Where does the study go back to?

   - [ ] Implementation
   - [ ] More runs
   - [x] Model conceptualisation and data collection
   - [ ] Documentation

   <details><summary>Answer</summary>

   Back to conceptualisation and data. A model that doesn't match reality has a wrong assumption or wrong input data, not just a bug.

   </details>

4. <!-- q: open id="256d1a95" -->
   Why should data collection start as early as possible, even though it is step 4?

   <details><summary>Answer</summary>

   It often takes a long time: observing arrivals, timing service, getting records from busy staff. Starting it alongside conceptualisation stops the whole project waiting for data, and early data also helps shape the conceptual model.

   </details>

5. <!-- q: open id="d73bd7a4" -->
   A team has built and validated a model of a factory. Describe what happens in steps 8 to 10.

   <details><summary>Answer</summary>

   Step 8, experimental design: choose the alternatives to compare (for example one shift or two), the run length and the number of replications. Step 9, production runs: run them and estimate the performance measures such as throughput and utilisation. Step 10, more runs: check whether the estimates are precise enough, for example with confidence intervals, and run more if not.

   </details>

## Before moving on
<!-- bite: 98b0b2c5-6bf6-47b5-b746-221b2b04ed4f -->

You can list the twelve steps, group them into phases and explain the loops. **Next:** [[systems-simulation/08-the-simulation-study-2|08 — The Simulation Study 2]]: the ten-step class version, the challenges, and choosing software.

## Related
<!-- bite: fef75c80-ba49-4599-8543-c7fe1fcc8665 -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: c9c92d75-c88d-452e-a3eb-87349556e3b4 -->

**Level:** Beginner. **Covers:** the twelve steps of a simulation study (Banks, Carson, Nelson and Nicol) in four phases, and the loops between them.

**Where it sits:** lesson 07 of 38, part 1 of 2 on the simulation study.

**Source:** the author's own SSG 418 and SSG 517 study notes, section D. The flowchart comes from `scripts/diagrams/systems_simulation.py`.
