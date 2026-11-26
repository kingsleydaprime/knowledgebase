---
id: d6ad986f-9187-42f1-a66d-08a87c25dc08
---

# CPM and PERT Compared

CPM and PERT both find a project's critical path from a network, but CPM uses one fixed time per activity while PERT uses three and gives probabilities.

## Before you start
<!-- bite: 32cb103c-e8c4-4da6-a1e4-b0a625f0bd1d -->

You should have read [[planning-and-scheduling/18-pert-2|18 — PERT 2]] and [[planning-and-scheduling/14-critical-path-method-2|14 — Critical Path Method 2]].

After this lesson you will be able to:

1. compare CPM and PERT on five points;
2. say which suits a given project, and why;
3. name the limits both methods share, and what GERT adds.

## What the two have in common
<!-- bite: 3aaa42f6-a5ef-406e-9d51-1a94e11e58f5 -->

Look back at parts 4 and 5. Both methods start the same way: list the activities, draw the network, run a forward and backward pass, find the critical path. PERT even uses CPM's passes, just with $t_e$ as the durations. They are two versions of one idea. The difference is in how much they trust the durations.

## The five differences
<!-- bite: 391848a5-4dfe-467f-a6d6-a8e7e8658abd -->

Asked in 2024/25 for 4 marks.

1. **The duration estimate.** CPM uses one fixed time for each activity: it is deterministic. PERT uses three times on a beta distribution: it is probabilistic.
2. **What it suits.** CPM suits repetitive, well-known work where durations are known from experience, such as construction. PERT suits new or uncertain work where nobody can give one confident time, such as research and development.
3. **The main question it answers.** CPM: "how can I trade time against cost?" PERT: "what is the chance of finishing by a given date?"
4. **Where it came from.** CPM: Du Pont, 1957, for plant construction and shutdowns. PERT: the US Navy, 1958, for the Polaris missile programme.
5. **What it adds.** CPM has time-cost crashing (part 6). PERT handles uncertainty and gives probabilities.

## Which would you use?
<!-- bite: a6470e1d-6d5e-49d3-aa82-2221e8ff9b92 -->

1. **Building the hundredth bungalow of the same design.** CPM: the builder knows exactly how long each step takes, and the useful question is whether overtime is worth paying for.
2. **Developing the first vaccine for a new disease.** PERT: nobody knows how long the trials take, and the funder wants the chance of being ready by winter.
3. **The fence and gate.** CPM is enough for a routine fence. If the site were in a flood zone and the weather mattered a lot, PERT would show how risky the deadline is.

Many real projects use both: PERT estimates for the uncertain activities, CPM for the rest, and crashing on top.

## What both methods assume
<!-- bite: 6723827e-8b2b-4f37-bd54-6c61d7abe0af -->

Both rest on the same simplifications. The slides list them:

1. **Every predecessor must finish before an activity starts.** Plain CPM and PERT use only finish-to-start links. (The precedence relationships of lessons 11 and 12 relax this.)
2. **Activities can't repeat or loop back.** There is no "if the test fails, redo the design" in the network.
3. **The critical path is always the longest path.** Nothing else, such as a shortage of workers, sets the finish. (Part 7 shows how resources break this.)
4. **There is only one end event.** The project finishes in one way.

## Beyond both: GERT
<!-- bite: 340f22f7-fad8-47ae-b835-e9548ecaf2e3 -->

GERT, the graphical evaluation and review technique, is a rarely used extension that drops some of those limits. It allows **branching** (an activity may or may not happen, with a probability) and **loops** (a test that fails sends the work back). That makes it fit research projects better, but the networks are much harder to solve by hand, which is why it is rarely used.

The comparison showed one thing only CPM offers: trading time against cost. Part 6 is that trade, called crashing.

## Common pitfalls
<!-- bite: 2fe72aec-778c-49e7-a2ee-01f0272909a2 -->

1. **Saying PERT has no critical path.** It does, found with CPM's passes on the expected times.
2. **Swapping the origins.** CPM: Du Pont 1957. PERT: US Navy 1958.
3. **Calling CPM probabilistic.** CPM is deterministic.

## Check your understanding
<!-- bite: 0ad74a59-b51a-44a0-af05-6f129519e9db -->

Try each one before you open the answer.

1. <!-- q: mcq id="0e4a7d92" -->
   A firm builds the same model of transformer substation for the tenth time and wants to know whether paying for overtime is worth it. Which method fits best?

   - [x] CPM
   - [ ] PERT
   - [ ] GERT
   - [ ] None, it needs simulation

   <details><summary>Answer</summary>

   CPM: the work is repetitive with known durations, and the question is a time-cost trade, which CPM's crashing answers.

   </details>

2. <!-- q: gap id="5d81c3fb" answers="deterministic;probabilistic" -->
   CPM is ___ because it uses one fixed time; PERT is ___ because it uses three times on a distribution.

   <details><summary>Answer</summary>

   Deterministic, probabilistic.

   </details>

3. <!-- q: mcq id="a3f62e07" -->
   Which of these do CPM and PERT both assume? Choose all that apply.

   - [x] Activities cannot loop back
   - [x] Every predecessor must finish before an activity starts
   - [ ] Durations follow a normal distribution
   - [x] There is only one end event

   <details><summary>Answer</summary>

   The three limits from the slides. Neither assumes normal activity durations; PERT assumes beta.

   </details>

4. <!-- q: open id="f8c25b19" -->
   Give four differences between CPM and PERT.

   <details><summary>Answer</summary>

   Any four: CPM uses one fixed time (deterministic), PERT three times on a beta distribution (probabilistic); CPM suits repetitive work like construction, PERT new or uncertain work like research and development; CPM answers how to trade time and cost, PERT the chance of finishing by a date; CPM came from Du Pont in 1957, PERT from the US Navy in 1958 (Polaris); CPM has crashing, PERT handles uncertainty.

   </details>

5. <!-- q: open id="1b9e4d6a" -->
   What does GERT allow that CPM and PERT don't, and why is it rarely used?

   <details><summary>Answer</summary>

   GERT allows branching with probabilities (an activity may or may not happen) and loops (work sent back after a failed test). It is rarely used because such networks are much harder to build and solve by hand.

   </details>

## Before moving on
<!-- bite: 1b4138e7-6a7b-46b9-a5a4-6e042aa9ed16 -->

You can compare CPM and PERT, pick one for a project, and name their shared limits. **Next:** [[planning-and-scheduling/22-crashing-1|22 — Crashing 1: Cost Slope and the Time-Cost Curve]].

## Related
<!-- bite: 3c5590d8-0813-4eef-ad99-07e41662cde3 -->

- [[planning-and-scheduling/index|Planning and scheduling map]]

## About this lesson
<!-- bite: 6094e573-b507-414b-88c1-e36aae3f513f -->

**Level:** Intermediate. **Covers:** the five differences between CPM and PERT, choosing between them, their shared limits and GERT.

**Where it sits:** lesson 21 of 35, in part 5 (PERT).

**Source:** the author's own SSG 513 study notes, section 5 (including the SIMS slides' list of limits).
