---
id: e381094c-6340-459c-be2f-7acb642f156c
---

# Arena 1: The Environment, Modules and Functions

Arena builds a simulation as a flowchart of modules that entities flow through, with data modules holding the resources and queues they use.

## Before you start
<!-- bite: 977165e6-a08b-4a4f-b45c-f32c215f72da -->

You should have read [[systems-simulation/34-output-analysis|34 — Output Analysis]] and [[systems-simulation/21-generating-random-variates|21 — Generating Random Variates]].

After this lesson you will be able to:

1. describe Arena's working areas;
2. tell a flowchart module from a data module, and say what each main module does;
3. write Arena's distribution and queue functions.

## What Arena is
<!-- bite: ba8a5074-06e2-42e8-bc68-02efc3a4d9d8 -->

**Arena** is commercial simulation software from Rockwell Automation. You build a model by dragging modules into a flowchart, and underneath it runs the **SIMAN** simulation language. You describe the life of an entity as it moves through the system, and Arena handles the clock, the event calendar and the statistics, the same jobs GPSS/H did in lessons 23 and 24.

Arena is in the 2025/26 exam (the bank queue question), the lecturer's notes and the textbook, so these four lessons cover it fully. This one is the vocabulary: the screen, the modules and the functions.

## The environment
<!-- bite: 3a11f4c8-0b27-4693-8e21-24ab28b48a5e -->

1. **Project bar:** the panels of modules, called templates: Basic Process, Advanced Process, Advanced Transfer and Flow Process, plus the Reports and Navigate panels.
2. **Model window:** where you drop and connect flowchart modules.
3. **Spreadsheet (data) window:** a row-and-column view of the selected module, and where data modules are filled in.

## Flowchart modules and data modules
<!-- bite: 1c7ab7c4-2103-4add-aca3-f8c57d93a75d -->

1. **Flowchart modules** are dragged into the model window and connected: CREATE, PROCESS, DISPOSE, DECIDE and so on. They describe the path entities follow.
2. **Data modules** are not dragged; you fill them in the spreadsheet or a dialog: ENTITY, RESOURCE, QUEUE, VARIABLE. They define the things the flowchart uses.

## The main modules
<!-- bite: 5406d630-dc71-4d2b-85a6-6077113eb008 -->

| Module | What it does |
| --- | --- |
| CREATE | Creates entities and brings them into the model in a pattern. Without it nothing happens |
| DISPOSE | Removes entities once they have finished |
| PROCESS | An entity goes through an activity, usually using a resource |
| DECIDE | Sends an entity down one of several paths, by probability or by a condition |
| BATCH | Groups entities together before they continue, like a kit of parts |
| SEPARATE | Copies an entity into several, or splits a batched one back up |
| ASSIGN | Gives values to variables and attributes |
| RECORD | Captures and tabulates custom statistics, such as a count or a tally |
| ENTITY, RESOURCE, QUEUE, VARIABLE | Data modules: entity types and pictures, servers and their capacity, waiting lines, and variables |

A GPSS comparison helps: CREATE is GENERATE, DISPOSE is TERMINATE, and one PROCESS module does the QUEUE, SEIZE, DEPART, ADVANCE and RELEASE of a single-server queue.

## The functions
<!-- bite: 65d4bd75-7b56-4da2-a839-3cd16bc70d6a -->

Distributions (lesson 21):

1. **EXPO(mean):** exponential with that mean.
2. **UNIF(min, max):** uniform.
3. **NORM(mean, sd):** normal.
4. **TRIA(min, mode, max):** triangular.
5. **DISC(cumulative probability, value, ...):** an empirical table.

Model state:

1. **NQ(queue name):** the number currently waiting in that queue.
2. **MN(...)** and **MX(...):** the minimum and maximum of their arguments.

## Common pitfalls
<!-- bite: bb2e6bea-66e6-4052-82ad-cdaf95bea57b -->

1. **Looking for RESOURCE in the flowchart panel.** It is a data module, filled in the spreadsheet.
2. **EXPO with a rate.** EXPO takes the mean.
3. **TRIA in the wrong order.** It is minimum, most likely, maximum.

Next lesson looks under Arena's hood: how it moves time, the five states an entity can be in, and the activity diagram you draw before building.

## Check your understanding
<!-- bite: c6627a52-aa79-47d0-8ce7-989507c83394 -->

Try each one before you open the answer.

1. <!-- q: mcq id="b0bbf327" -->
   Which of these is a data module rather than a flowchart module?

   - [ ] CREATE
   - [ ] DECIDE
   - [x] RESOURCE
   - [ ] DISPOSE

   <details><summary>Answer</summary>

   RESOURCE. Data modules (ENTITY, RESOURCE, QUEUE, VARIABLE) are filled in the spreadsheet, not dragged into the flowchart.

   </details>

2. <!-- q: mcq id="cce0631d" -->
   Which module sends 7% of passengers one way and 93% another?

   - [ ] PROCESS
   - [x] DECIDE
   - [ ] SEPARATE
   - [ ] ASSIGN

   <details><summary>Answer</summary>

   DECIDE, using a probability. It can also decide by a condition.

   </details>

3. <!-- q: exact id="c8498b28" answer="TRIA(2,5,9)" accept="TRIA(2, 5, 9)|tria(2,5,9)" -->
   Write the Arena expression for a triangular service time with minimum 2, most likely 5 and maximum 9 minutes.

   <details><summary>Answer</summary>

   TRIA(2, 5, 9): minimum, most likely (mode), maximum.

   </details>

4. <!-- q: exact id="2034886f" answer="EXPO(4)" accept="EXPO(4.0)|expo(4)" -->
   Customers arrive as a Poisson process at 15 per hour. Write the Arena expression for the time between arrivals, in minutes.

   <details><summary>Answer</summary>

   EXPO(4). Poisson arrivals have exponential gaps, the mean gap is 60 ÷ 15 = 4 minutes, and EXPO takes the mean.

   </details>

5. <!-- q: open id="cd8b2522" -->
   Which single Arena module replaces GPSS's QUEUE, SEIZE, DEPART, ADVANCE and RELEASE, and how is it set up for that?

   <details><summary>Answer</summary>

   PROCESS, with its action set to Seize, Delay, Release. It joins the queue, seizes the resource, delays for the service time and releases the resource, collecting the waiting and utilisation statistics as it goes.

   </details>

## Before moving on
<!-- bite: 01cfec6d-77a8-434b-bd32-0e64752ef6a0 -->

You can describe Arena's screen, its modules and its functions. **Next:** [[systems-simulation/36-arena-2|36 — Arena 2]]: how time works inside Arena.

## Related
<!-- bite: 63831829-f8a5-4bf3-987d-6a43af9fca83 -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: 4e754a54-3709-45b2-9e88-a48852476e78 -->

**Level:** Beginner. **Covers:** what Arena is, its working areas, flowchart and data modules, the main modules, and its functions.

**Where it sits:** lesson 35 of 38, part 1 of 4 on Arena.

**Source:** the author's own SSG 517 study notes, section 8.
