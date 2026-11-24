---
id: 8cff0a2f-6000-4581-abd5-b2e54a220a59
---

# Model Building 1: The Eight Steps and the Questions to Ask

Model building takes a messy real problem through eight steps to a working model, starting with careful questions about the problem itself.

## Before you start
<!-- bite: acc1351c-1ca5-4c01-9538-0b2ea26d17cb -->

You should have read [[systems-simulation/24-gpss-2|24 — GPSS/H 2]] and [[systems-simulation/08-the-simulation-study-2|08 — The Simulation Study 2]].

After this lesson you will be able to:

1. list the lecturer's eight model-building steps and what each produces;
2. carry out step 1, problem analysis, as a sequence of questions;
3. write good study questions for a system, starting with What, How, Why, Can, Does and Should.

## What model building is
<!-- bite: bc9ad457-7345-490f-b12a-46bc70d9ffd7 -->

**Model building** is the sequence of steps that turns a real problem into a model you can run and trust. Lessons 07 and 08 gave the twelve-step and ten-step versions of the whole study. The SSG 517 lecturer teaches this eight-step version, which is the same journey seen from the modeller's desk. Each step feeds the next, and you often go back a step when something doesn't fit.

This lesson covers the eight steps and goes deep on the first one, because exam case questions mostly test it.

## The eight steps
<!-- bite: 8dd5e56a-f05a-4d51-bdef-a45fe4973aa6 -->

1. **Problem analysis and information collection.** Study the problem: the input parameters, the performance measures you care about, how parameters and variables relate, and the rules for how the parts operate. Write it down as flow diagrams, hierarchy trees, a narrative, or whatever communicates best.
2. **Data collection.** Gather data to estimate the input parameters, and make assumptions about the distributions of the random variables. This leads into input analysis (lessons 27–29).
3. **Model construction.** Build the model and implement it as a computer program, for example in Arena.
4. **Model verification.** Check it is built correctly: it matches its specification and does what it should.
## The eight steps: checking and using the model
<!-- bite: 01925df4-f9f6-4de5-8cb6-c34e5ca3a6cc -->

The last four steps check the model against reality, then use it.

5. **Model validation.** Treat every model as a proposal until it has been checked against the real system's measurements.
6. **Designing and running experiments.** Once it is judged valid, design the runs (length, replications, scenarios) and run them.
7. **Output analysis.** Analyse the results logically and statistically, for example to pick the best of several designs.
8. **Final recommendations.** Turn the analysis into recommendations for the real problem.

Steps 4 and 5 get their own part (lessons 31–33), because they are where credibility is won or lost.

## Step 1 in practice
<!-- bite: 63582125-4b25-4a50-95c6-caeb6a40638e -->

The class notes give this sequence for problem analysis:

1. Identify the system of interest, and decide the performance measures you care about.
2. Generate likely questions, decide which one you want to answer, then define the problem.
3. List all the components of the system, and write down its assumptions and properties.
4. Draw a complete flow chart showing every parameter needed.
5. Decide the input parameters, then collect the data.

Notice the order. You don't collect data first and look for a question later; the question decides what data you need.

## Ways to write the model down
<!-- bite: 94a42047-d2f3-4015-a2f5-e336a99c99e5 -->

Step 1 says to write the problem down in whatever form communicates best. Three representation techniques come up in the exam, each suited to a different job:

1. **Flow diagram:** use it when the logic and the order of decisions matter. In a microgrid: use renewable power first, then the battery, then the grid.
2. **State chart:** use it when equipment moves between modes. A battery is charging, discharging or idle; the grid connection is connected or islanded.
3. **Entity-relationship model:** use it when you need to show how the data and components relate, such as generators, loads and meters and their attributes.

## Writing good study questions
<!-- bite: 166d9c56-3f80-47b4-bbfb-d48745a936b0 -->

The lecturer's exercise: a job shop makes two products, A and B, on three machines, M1, M2 and M3, with different routes and processing times. Write six relevant questions.

A good set starts with **What, How, Why, Can, Does and Should**:

1. **What** is the utilisation of each machine?
2. **How** long does a job spend in the system?
3. **Why** do jobs queue at M2?
4. **Can** a different routing reduce delay?
5. **Does** a breakdown at one machine block the others?
6. **Should** we add a machine?

The six words push you from describing the system (What, How), through understanding it (Why, Does), to deciding (Can, Should), which is where the value is.

## Common pitfalls
<!-- bite: b9d903ef-75e8-4805-8df3-55ceed50c76a -->

1. **Collecting data before defining the problem.** You end up with the wrong data.
2. **Questions that can't be measured.** "Is the shop good?" has no performance measure; "what is M2's utilisation?" does.
3. **Skipping the flow chart.** It is where missing parameters show up.

Steps 1 and 2 are easiest to understand on a real case. Next lesson works through the lecturer's production control problem: a packaging line with breakdowns, a warehouse and random customers.

## Check your understanding
<!-- bite: 153ba044-b058-4e72-8e30-6c344c55e9b2 -->

Try each one before you open the answer.

1. <!-- q: mcq id="36da9edf" -->
   In the eight-step model-building process, which step comes straight after model construction?

   - [ ] Data collection
   - [x] Model verification
   - [ ] Output analysis
   - [ ] Final recommendations

   <details><summary>Answer</summary>

   Model verification: check the program is built correctly before checking it against reality (validation).

   </details>

2. <!-- q: open id="1e139fd4" -->
   A university wants to model its main cafeteria at lunchtime. Write four study questions, starting with What, Why, Can and Should.

   <details><summary>Answer</summary>

   For example. What is the average wait from joining the line to getting food? Why does the line build up at the cash point? Can a second payment point cut the wait below 5 minutes? Should the cafeteria open 30 minutes earlier?

   </details>

3. <!-- q: mcq id="8e4ccd92" -->
   In step 1 (problem analysis), what comes before collecting the data?

   - [ ] Running the experiments
   - [ ] Validating the model
   - [x] Deciding the question, listing the components and assumptions, and drawing a flow chart of the parameters
   - [ ] Writing the final recommendations

   <details><summary>Answer</summary>

   The question, the components and assumptions, and the flow chart. They decide which data is worth collecting.

   </details>

4. <!-- q: open id="bae7fcc4" -->
   Why does the lecturer say to treat every model as a proposal until it is validated?

   <details><summary>Answer</summary>

   A model is only someone's idea of how the system works until it has been compared with the real system's measurements. It may run perfectly and still be wrong about reality, so decisions shouldn't rest on it until it has been checked.

   </details>

5. <!-- q: gap id="af684f0e" answers="output analysis;final recommendations|recommendations" -->
   The last two model-building steps are ___, where results are analysed statistically, and ___, where they are turned into advice for the real problem.

   <details><summary>Answer</summary>

   Output analysis, then final recommendations.

   </details>

## Before moving on
<!-- bite: 5b3fdc52-7ae8-460a-bdc3-63413fece291 -->

You can list the eight steps, carry out problem analysis, and write good study questions. **Next:** [[systems-simulation/26-model-building-2|26 — Model Building 2]]: the production control case.

## Related
<!-- bite: a183963a-3f84-45e5-89a0-66170d85691d -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: fc0a46cc-390a-49c2-9d0a-7ff0b535ebcf -->

**Level:** Beginner. **Covers:** the eight model-building steps, the step 1 sequence, three ways to represent a model, and the What/How/Why/Can/Does/Should questions.

**Where it sits:** lesson 25 of 38, part 1 of 2 on model building.

**Source:** the author's own SSG 517 study notes, sections 5 and 9 (Q5). The cafeteria quiz question is added for this lesson.
