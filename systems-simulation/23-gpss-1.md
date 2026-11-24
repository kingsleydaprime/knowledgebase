---
id: 36321a70-9da7-4d43-94d5-4d6c38b8c655
---

# GPSS/H 1: Transactions, Resources and Blocks

GPSS/H builds a discrete-event model as a list of blocks that moving transactions flow through, competing for resources on the way.

## Before you start
<!-- bite: 55ba7ec1-eb93-49e3-b9ca-18020d5d70fe -->

You should have read [[systems-simulation/22-monte-carlo-simulation|22 — Monte Carlo Simulation]], and [[systems-simulation/09-discrete-event-simulation|09 — Discrete-Event Simulation]] for events and the clock.

After this lesson you will be able to:

1. name the elements of a GPSS/H model: transactions, resources, blocks, control statements and the rest;
2. tell a facility from a storage;
3. say what each main block does, and read a GENERATE or ADVANCE operand.

## What GPSS/H is
<!-- bite: 48290022-ddb9-4bb6-98fb-81d450716f37 -->

**GPSS** (General Purpose Simulation System) is a language for discrete-event simulation, and GPSS/H is a widely taught version of it. You build a model by describing the **path** a moving thing follows through a series of blocks: it is created, it joins a queue, it grabs a server, it is delayed, it lets go, it leaves.

You don't write the clock or the event list; GPSS handles them, as lesson 09 described. This lesson gives the vocabulary. Lesson 24 puts it together into two complete models.

## The elements of a GPSS/H model
<!-- bite: 07124800-8b08-46ef-a3bb-d6e3ee5947bd -->

1. **Transactions:** These are the moving entities, such as a shopper, a car on an assembly line or a casting. Most are temporary: created, do their job, destroyed. A transaction has attributes, some built in and some you define, such as a shopper's number of items.
2. **Resources:** These are static, permanent entities that transactions compete for. There are two types, below.
3. **Blocks:** These are the statements that say how a transaction moves. The whole set is the model's logic, and drawn as a picture it is a **block diagram**.
## The elements of a GPSS/H model: control and bookkeeping
<!-- bite: 1b72ac68-8b85-47b7-8442-a473823119c7 -->

The other three elements control the run and keep its numbers.

4. **Control statements:** These tell GPSS how to run, such as `START 100` (stop after 100 transactions have left). They also define entities and give looping and if-then logic. They have no picture.
5. **Compiler directives:** These give information needed to compile the model but cause nothing to happen when it runs, such as declaring a variable an integer.
6. **Standard numerical attributes (SNAs):** These are values GPSS keeps for each entity, such as a queue's current length, which the model's logic can read.

There are also **computational entities** (variables and functions) and **statistical entities** (queues and tables). When several transactions wait for the same thing, GPSS serves the **highest priority first, then first in first out**.

## Facility and storage
<!-- bite: 6d8fcc2e-57a0-4586-97e1-880ff258f34c -->

The two kinds of resource:

1. **Facility:** a single-unit resource, such as one cashier or one drill. A transaction **SEIZE**s it and **RELEASE**s it.
2. **Storage:** a group of identical parallel resources, such as three identical machines, defined as a storage of capacity 3. A transaction **ENTER**s it (taking one unit) and **LEAVE**s it.

## The main blocks
<!-- bite: 0f667127-2419-47f4-972f-2cc0b358292b -->

| Block | What it does |
| --- | --- |
| GENERATE | Creates transactions. Its operands give the inter-arrival time |
| QUEUE | The transaction joins a named queue, so waiting statistics are collected |
| SEIZE | The transaction captures a facility, or waits if it is busy |
| DEPART | The transaction leaves the queue |
| ADVANCE | Delays the transaction for a time, such as a service time |
| RELEASE | The transaction gives up the facility |
| TERMINATE | Destroys the transaction; `TERMINATE 1` counts one towards the START count |
| ENTER / LEAVE | Take and give back a unit of a storage |
| GATE | Lets a transaction through only if a condition holds, such as a storage not being full |
| TRANSFER | Sends the transaction to another block |
| TABULATE | Adds a value to a table, which builds a histogram |

## Reading the operands
<!-- bite: 2c08054f-d594-41bb-8a84-5c8aafacd730 -->

GENERATE and ADVANCE take two operands, **A,B**, meaning a time **uniform between A − B and A + B**.

1. `GENERATE 15,4.5` means arrivals every 10.5 to 19.5 time units, evenly spread.
2. `ADVANCE 13.5,3` means a delay of 10.5 to 16.5.

## The heart of a single-server queue
<!-- bite: 3a2f872b-6612-4f5f-a34f-74ed8ccdc22b -->

The order **QUEUE, SEIZE, DEPART, ADVANCE, RELEASE** is the core of every one-server queue:

1. QUEUE: start counting the wait.
2. SEIZE: get the server (waiting here if it's busy).
3. DEPART: stop counting the wait; the transaction has the server.
4. ADVANCE: the service time.
5. RELEASE: free the server for the next one.

So the **wait** is measured between QUEUE and DEPART, and the **service** between SEIZE and RELEASE.

## Common pitfalls
<!-- bite: f9d21911-7fda-4f53-9219-006f7dccd0f3 -->

1. **Reading A,B as "mean A, standard deviation B".** It is uniform from A − B to A + B.
2. **Using SEIZE with a storage.** Storages use ENTER and LEAVE.
3. **DEPART before SEIZE.** The transaction must hold the server before it stops being counted as waiting.
4. **Forgetting START.** Without it the model doesn't know when to stop.

Next lesson writes two complete GPSS/H models, a drill and a telephone exchange, and reads the report one produces.

## Check your understanding
<!-- bite: 2f2c3310-b891-4ee8-893d-93bf6906dba9 -->

Try each one before you open the answer.

1. <!-- q: open id="2de314c1" -->
   A GPSS/H model has the block `GENERATE 20,5`. Between what times do transactions arrive?

   <details><summary>Answer</summary>

   Uniformly between 15 and 25 time units apart: A − B = 15 and A + B = 25.

   </details>

2. <!-- q: mcq id="2cf9bdc2" -->
   A garage has four identical repair bays. How should they be defined in GPSS/H?

   - [ ] As four separate facilities used with SEIZE
   - [x] As a storage of capacity 4, used with ENTER and LEAVE
   - [ ] As a queue
   - [ ] As a table

   <details><summary>Answer</summary>

   A storage of capacity 4. A facility is a single unit; a storage is a group of identical parallel units.

   </details>

3. <!-- q: mcq id="7ba1ea09" -->
   In a one-server GPSS model, between which two blocks is the waiting time measured?

   - [ ] SEIZE and RELEASE
   - [x] QUEUE and DEPART
   - [ ] GENERATE and TERMINATE
   - [ ] ADVANCE and RELEASE

   <details><summary>Answer</summary>

   QUEUE and DEPART. The service time sits between SEIZE and RELEASE.

   </details>

4. <!-- q: gap id="aa2183ed" answers="transactions|transaction;resources|resource" -->
   In GPSS/H, the moving entities such as shoppers or castings are ___, and the permanent things they compete for, such as a cashier, are ___.

   <details><summary>Answer</summary>

   Transactions, then resources (facilities and storages).

   </details>

5. <!-- q: open id="07f15461" -->
   Put these blocks in the right order for a single-server queue: RELEASE, QUEUE, ADVANCE, SEIZE, DEPART.

   <details><summary>Answer</summary>

   QUEUE, SEIZE, DEPART, ADVANCE, RELEASE. Join the queue, capture the server, leave the queue, be served, free the server.

   </details>

## Before moving on
<!-- bite: ccd34370-ce56-4cdf-bc3b-fd87e5d825d9 -->

You can name GPSS/H's elements, tell a facility from a storage and say what each block does. **Next:** [[systems-simulation/24-gpss-2|24 — GPSS/H 2]]: two complete models.

## Related
<!-- bite: 2c96f8ee-f05e-4470-8f7c-67e14dff816a -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: 0a8b2df5-c7c5-444e-88cf-7e714ede41d7 -->

**Level:** Beginner. **Covers:** GPSS/H's elements, facilities and storages, the main blocks, reading A,B operands, and the core single-server sequence.

**Where it sits:** lesson 23 of 38, part 1 of 2 on GPSS/H.

**Source:** the author's own SSG 418 study notes, section F.
