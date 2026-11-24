---
id: 1ce3803a-0891-465c-80e6-2ada5a4a5815
---

# When to Simulate

Simulation is worth it when experimenting on the real system is impossible or unwise, and not worth it when something simpler gives the answer.

## Before you start
<!-- bite: 317854be-0165-4727-b105-bf20e6ca443d -->

You should have read [[systems-simulation/01-what-simulation-is|01 — What Simulation Is]].

After this lesson you will be able to:

1. give the seven reasons you often can't experiment on the real system;
2. group the advantages of simulation into four kinds, and name its three disadvantages;
3. say when simulation is the wrong tool.

## What the case for simulation is
<!-- bite: b30c01b5-50eb-4959-94e2-525653ce9764 -->

Lesson 01 said simulation is what you use when you can't easily study the real system. This lesson makes that precise. First, the reasons real experiments fail. Then what simulation gives you in return, what it costs, and the cases where you should not use it at all. Exams like to ask all three as lists, so each one is grouped to make it easy to remember.

## Why not just experiment on the real thing?
<!-- bite: 2e2dba81-7589-4b51-9906-6f6b1e7d296c -->

Experimenting is the first way people learn about their world, but often it isn't possible. Seven reasons:

1. **Ethics:** it isn't acceptable. You can't cause a nuclear leak to measure how radiation spreads.
2. **Risk:** it is too dangerous. Testing a new way to control a reactor, an epidemic or a fire evacuation on real people could kill someone.
3. **Cost:** it is too expensive. Upgrading every switch in a large data network just to see what happens costs a fortune.
4. **Time:** it is too slow. The effect of a hunting season on wildlife takes years to show.
## Why not experiment: three more reasons
<!-- bite: 411921ad-4f37-40ac-b8aa-c3dc82440fdd -->

Three more reasons, and a way to remember all seven.

5. **Disruption:** it would upset normal life. Trying a new one-way street grid in the city centre jams traffic for everyone.
6. **Irreversible:** you can't undo it. A fiscal policy change on a whole economy can't be taken back.
7. **Impossible:** you can't manipulate a star, and you can't experiment on a building that doesn't exist yet.

A memory hook: **E**very **R**eal **C**hange **T**akes **D**ays, **I**s **I**rreversible, or **I**mpossible.

## The advantages of simulation
<!-- bite: 282c9228-5d49-4975-b337-998e42f3505e -->

The lecture lists 18 advantages. Grouped into four, they are easier to recall.

1. **Cheap, safe testing of decisions.** You check a decision artificially without committing resources. The real system isn't disturbed, a study costs far less than changing the real system, and design cycles get shorter.
2. **Flexibility.** The same model can be reused, its rules are easy to change, you can try special cases while it runs, it needs fewer simplifications than a formula, and you can compress or stretch time (a year in seconds, or a millisecond in slow motion).
3. **Understanding.** It helps you diagnose problems by showing how variables interact, find constraints (is this delay the cause of the problem or a result of it?), see *how* the system works rather than only predicting it, and show it all as an animation.
4. **Planning and training.** It prepares you for change by answering "what if" questions, helps you write requirements, and gives cheaper, less disruptive training than learning on the job.

## The disadvantages
<!-- bite: ed2ddf55-18cd-4378-be6a-5e5cbb41c71f -->

There are three, and the second matters most.

1. **Building models needs special training.** It is a skill, not just programming.
2. **Results are hard to interpret.** The inputs are random, so the outputs are random too. When you see a long queue in one run, it is hard to tell whether it comes from how the system is built or just from chance. Lessons 33 and 34 deal with this using replications and confidence intervals.
3. **It can be time consuming and expensive.** Collecting data and building a credible model takes weeks.

## When simulation is not appropriate
<!-- bite: daeb7fe9-749b-448c-b840-44f4d8a383a7 -->

Don't simulate when:

1. common sense solves the problem;
2. it can be solved analytically, with a formula;
3. a direct experiment is cheaper;
4. the cost of modelling is more than the savings it would bring;
5. you don't have the resources or the time;
6. the data you need is missing;
7. the system is so complex that it can't be defined.

Notice that point 2 links back to the tree in lesson 01: if the analytical branch works, take it.

## Where simulation is used
<!-- bite: c42a24ce-f19f-40c2-a1f6-f68622091e19 -->

You only need two or three examples per area in an exam.

1. **Manufacturing:** dispatching rules, batch sizes, cycle time and machine utilisation.
2. **Construction:** dam embankments, tunnel construction.
3. **Military:** recruiting, controllers for underwater vehicles.
4. **Logistics and transport:** rail capacity, airport passenger flow, toll plaza design, flight schedules.
5. **Business processes:** gate assignment at airports, workforce planning.
6. **Human systems:** human performance in complex systems, traffic control.

## Common pitfalls
<!-- bite: 1bef718e-61fe-44a5-ba3e-3ea16432e117 -->

1. **Listing advantages with no example.** In a case question, tie each advantage to the case: "the hospital can test a new triage rule without risking patients".
2. **Forgetting the interpretation problem.** Random outputs mean one run proves nothing on its own.
3. **Simulating what a formula already answers.** It wastes time and adds sampling error.

Now we know when simulation is worth it. Next lesson looks inside a system: the different types of system, and the five components every system is described with.

## Check your understanding
<!-- bite: 57cb846c-94e4-4446-be84-044d1af1391a -->

Try each one before you open the answer.

1. <!-- q: mcq id="bad28052" -->
   A government wants to know how a large tax cut would affect the economy. Which reason against experimenting on the real system fits best?

   - [ ] Too slow
   - [x] Irreversible: once the policy is applied, it can't be undone
   - [ ] Impossible
   - [ ] Too expensive

   <details><summary>Answer</summary>

   Irreversible. A fiscal policy change on a whole economy can't be taken back, so you model it first.

   </details>

2. <!-- q: mcq id="c1bb530f" -->
   Which of these are disadvantages of simulation? Choose all that apply.

   - [x] Building models needs special training
   - [x] Outputs are random, so it is hard to tell a real effect from chance
   - [ ] It always disturbs the real system
   - [x] It can be time consuming and expensive

   <details><summary>Answer</summary>

   The first, second and fourth. Simulation does not disturb the real system; that is one of its advantages.

   </details>

3. <!-- q: mcq id="d03bf5a5" -->
   A shop owner asks whether two cashiers serve customers faster than one. Arrivals and service follow the neat patterns a standard queueing formula needs. Should you simulate?

   - [ ] Yes, simulation is always more accurate
   - [x] No, the analytical formula answers it more cheaply
   - [ ] Yes, because the system can't be defined
   - [ ] No, because simulation can't model cashiers

   <details><summary>Answer</summary>

   No. When a problem can be solved analytically, simulation is not appropriate: the formula is quicker and has no sampling error.

   </details>

4. <!-- q: open id="17bbd05d" -->
   Give the four groups of simulation advantages, with one example of each.

   <details><summary>Answer</summary>

   1. Cheap, safe testing of decisions: try a new factory layout without moving a single machine.
   2. Flexibility: change a rule and rerun, or compress a year into seconds.
   3. Understanding: see whether a delay causes a problem or results from it.
   4. Planning and training: answer "what if demand doubles?", or train staff on the model instead of on the job.

   </details>

5. <!-- q: open id="24606c03" -->
   A city wants to try a new one-way street grid in the city centre. Using two of the seven reasons, explain why it should simulate first.

   <details><summary>Answer</summary>

   Disruption: changing the real streets would jam traffic for everyone while the experiment runs. Cost: re-signing and re-marking roads, then changing them back if it fails, is expensive. A simulation lets the city compare grids without touching the roads.

   </details>

## Before moving on
<!-- bite: ba0a6e30-e9fd-42cc-9ce5-e8d2002bfc2e -->

You can say why real experiments often fail, what simulation gives and costs, and when not to use it. **Next:** [[systems-simulation/03-systems-and-their-components|03 — Systems and Their Components]]: the types of system and the five components used to describe one.

## Related
<!-- bite: 49417751-c373-4cad-8c28-887b0cadcc93 -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: ec4529b3-07ef-4015-aed7-b64131abafc8 -->

**Level:** Beginner. **Covers:** the seven reasons real experiments fail, the advantages grouped in four, the three disadvantages, when simulation is not appropriate, and where it is used.

**Where it sits:** lesson 02 of 38, in part 1 (systems and models).

**Source:** the author's own SSG 418 and SSG 517 study notes, sections A and 1. The memory hook is added for this lesson.
