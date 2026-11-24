---
id: 675e1295-9a60-4e9e-89bd-54f9bf6558f3
---

# Crashing 1: Cost Slope and the Time-Cost Curve

Crashing is shortening a project by spending extra money on some of its activities, and the cost slope tells you how much each day saved on an activity costs.

## Before you start
<!-- bite: 6fd4e849-979f-4a9e-9b4d-875609b8daa6 -->

You should have read [[planning-and-scheduling/14-critical-path-method-2|14 — Critical Path Method 2]] and [[planning-and-scheduling/03-the-triple-constraint|03 — The Triple Constraint]].

After this lesson you will be able to:

1. define normal and crash time and cost, direct and indirect cost;
2. compute an activity's cost slope;
3. explain why total cost against duration is U-shaped, and where the cheapest duration is.

## What crashing is
<!-- bite: 5c6cb0fb-7716-418e-8faa-cd61316e6c9d -->

The fence takes 12 days. The owner now has a party in 10 days and wants it finished before then. Remember the triple constraint: if scope stays fixed and time is cut, cost must rise. Crashing is how you decide *where* to spend the money.

You can shorten an activity by throwing resources at it: extra workers, overtime, a hired post-hole digger. But each activity has a limit, a point past which more money buys no more speed. And each has its own price for a day saved. Crashing finds the cheapest days to buy.

## Terms used in crashing
<!-- bite: 7b0307a3-7fe1-408d-af52-38ad013a6d03 -->

1. **Normal time (Tn)**: This is how long the activity takes under ordinary working conditions. Digging the holes: 3 days.
2. **Normal cost (Cn)**: This is what the activity costs at its normal time.
3. **Crash time (Tc)**: This is the shortest the activity can possibly take, however much you spend. With a hired digger, the holes take 1 day.
4. **Crash cost (Cc)**: This is what it costs at its crash time.
5. **Direct cost**: This is the cost of doing the activities themselves: labour, materials, equipment. It **rises** when you crash.
6. **Indirect cost**: This is also called **fixed cost** or overhead. It is the cost of running the project per day, such as supervision, site security and hired toilets. It is charged per day, so it **falls** when the project is shorter.

## The cost slope
<!-- bite: fc5c8917-bf8f-428d-955a-486e76c2e613 -->

**The cost slope is the extra cost of saving one day on an activity: how much more crashing costs, divided by how many days it saves.**

$$\text{Cost slope} = \frac{C_c - C_n}{T_n - T_c}$$

Say digging the holes costs N30,000 in 3 days normally, and N70,000 in 1 day with a hired digger. Then:

Cost slope = (70,000 − 30,000) / (3 − 1) = **N20,000 per day**.

So each day cut from the digging costs N20,000. The method assumes the cost rises in a straight line between normal and crash, which is why one slope describes the whole range.

If Tn = Tc, the activity **can't be crashed** at all: there's no day to save. The formula would divide by zero, so just write "cannot crash".

## Why total cost is U-shaped
<!-- bite: a884706c-e558-4eaa-a70b-be5c944dd3b8 -->

As you shorten the project, two costs pull against each other.

1. **Direct cost goes up**, because you're paying for speed.
2. **Indirect cost goes down**, because there are fewer days of overhead.

Add them and you get the total cost, which falls at first (each crashed day saves more overhead than it costs) and then rises (the cheap days are used up and the remaining ones cost more than they save).

## The time-cost curve
<!-- bite: 7af3e52b-1772-47cc-ac7e-e58edfd9a4de -->

Here is that tug of war drawn as three curves.

![Cost against project duration: direct cost rises as the duration is cut, indirect cost falls in a straight line, and total cost forms a U with its lowest point marked as the optimum duration, between the crash duration on the left and the normal duration on the right](images/ps-time-cost-u.svg)

The cheapest duration is at the bottom of the U, and it is usually **not** the fastest possible one. Crashing everything to the limit gives the shortest project at a high price.

## The rule that follows
<!-- bite: f63e4227-05bb-40d8-8c9f-ca0c3c0f40d0 -->

Keep crashing only while the cost slope of the day you're buying is **less than the indirect cost you save per day**. If a day of crashing costs N20,000 and overhead is N25,000 a day, crashing that day saves N5,000 overall. If overhead is N15,000 a day, that day loses N5,000.

One more rule, from lesson 14: crash **only critical activities**. Shortening a non-critical activity just adds float to it; the project doesn't finish any sooner, so the money is wasted.

The next lesson turns these two rules into a step-by-step algorithm and applies it to the table that has appeared in three papers.

## Common pitfalls
<!-- bite: 97eb37f3-ec57-46c6-aed2-e288f36089c0 -->

1. **Turning the slope upside down.** It is cost difference over time difference: naira per day.
2. **Crashing a non-critical activity.** It spends money and saves nothing.
3. **Assuming the fastest plan is the cheapest.** The bottom of the U is usually well short of full crash.
4. **Counting indirect cost as rising with crashing.** It falls, because it is per day.

## Check your understanding
<!-- bite: 7aa8320d-4d7b-4435-9f38-e25fd061a099 -->

Try each one before you open the answer.

1. <!-- q: exact id="9d4e1f36" answer="300" -->
   An activity normally takes 6 days and costs N800. Crashed, it takes 4 days and costs N1,400. What is its cost slope, in naira per day?

   <details><summary>Answer</summary>

   300: (1,400 − 800) / (6 − 4) = 600 / 2.

   </details>

2. <!-- q: mcq id="62b0a8e5" -->
   An activity has normal time 3 days, crash time 3 days. What does that mean?

   - [ ] Its cost slope is zero, so crash it first
   - [x] It cannot be crashed
   - [ ] It is always critical
   - [ ] Its crash cost equals zero

   <details><summary>Answer</summary>

   There is no day to save, so it can't be crashed.

   </details>

3. <!-- q: mcq id="c7f31d0b" -->
   As a project is crashed from its normal duration towards its crash duration, which costs fall?

   - [ ] Direct cost
   - [x] Indirect cost
   - [ ] Both
   - [ ] Neither

   <details><summary>Answer</summary>

   Indirect cost, because it is charged per day and there are fewer days.

   </details>

4. <!-- q: mcq id="1f8e6c24" -->
   Overhead is N4,000 per day. The cheapest critical activity has a cost slope of N5,000 per day. Should you crash it?

   - [ ] Yes, crashing always saves money
   - [x] No, it costs N1,000 more than the overhead it saves
   - [ ] Yes, because it is critical
   - [ ] Only if it is not critical

   <details><summary>Answer</summary>

   No, if the aim is the lowest total cost: the day costs 5,000 and saves only 4,000. (If a deadline forces it, you'd crash anyway and accept the extra cost.)

   </details>

5. <!-- q: open id="b5d29a73" -->
   Explain why the total cost of a project against its duration is U-shaped.

   <details><summary>Answer</summary>

   Total cost is direct plus indirect. Shortening the project raises direct cost (paying for speed) and lowers indirect cost (fewer days of overhead). At first the cheap crash days save more overhead than they cost, so total cost falls; once those are used up, each further day costs more than it saves, so total cost rises. The bottom of the U is the cheapest duration.

   </details>

## Before moving on
<!-- bite: e309bd6f-b34c-4fce-9820-28a1677c29f9 -->

You can compute cost slopes and explain the U-shaped curve. **Next:** [[planning-and-scheduling/23-crashing-2|23 — Crashing 2: The Crashing Algorithm]].

## Related
<!-- bite: d040c09a-131a-4b23-8a70-a418ae1b405f -->

- [[planning-and-scheduling/index|Planning and scheduling map]]
- [[planning-and-scheduling/03-the-triple-constraint|03 — The Triple Constraint]]: the idea crashing puts into numbers.

## About this lesson
<!-- bite: 8005fc25-2d41-49af-aac1-017378779794 -->

**Level:** Intermediate. **Covers:** normal and crash time and cost, direct and indirect cost, the cost slope, the U-shaped total cost and the two crashing rules.

**Where it sits:** lesson 22 of 35, in part 6 (crashing). Part 1 of 3 on crashing.

**Source:** the author's own SSG 513 study notes, section 6. The fence digging costs are added for this lesson. The curve comes from `scripts/diagrams/planning_scheduling.py` and shows the shape, not a particular project.
