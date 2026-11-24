---
id: ed9de37c-d0c7-44bc-9679-dedd93655d3c
---

# Resource Smoothing and Levelling

Smoothing uses float to flatten peaks in demand without moving the finish; levelling delays work to fit what is available.

## Before you start
<!-- bite: 1a844c8e-6be1-4605-b314-0fea3c0f6c34 -->

You should have read [[planning-and-scheduling/26-resources-2|26 — Resources 2]] and [[planning-and-scheduling/14-critical-path-method-2|14 — Critical Path Method 2]] (float).

After this lesson you will be able to:

1. tell smoothing from levelling;
2. smooth a resource profile by shifting activities within their float;
3. apply the levelling rule: delay the activity with the most float first;
4. name ways of managing resources shared across projects.

## What smoothing and levelling are
<!-- bite: be011425-a331-403c-aced-20fc8c24e957 -->

Remember the fence's histogram from lesson 25: 4 workers on days 3 to 5, then 1 worker on days 5 to 8. That's a peak and a valley. If you could move some of the peak into the valley, the builder would need fewer people at any one time.

Float is what makes that possible. C (Buy gate) and E (Buy paint) each have 3 days of float. They don't have to happen at their earliest start.

## Smoothing or levelling: which word means what
<!-- bite: 48711a4d-dec9-40c2-9ca4-890ee7c0c6e0 -->

The two words are close, and the sources don't use them quite the same way.

Your sources use the two words slightly differently, so check which one your lecturer means:

1. **Resource smoothing** (in the SIMS and Makwana slides): the end date must not move. Shift non-critical activities within their float to flatten peaks.
2. **Resource levelling**: demand is limited by what is available. If demand exceeds supply, delay activities, starting with the one with the **most float**. The project may finish later. If two activities tie on float, reschedule the one with the shorter duration. (Lecture 10 and the MGMT 4135 slides use "levelling" more loosely, for any attempt to make daily use as even as possible.)

## Smoothing the fence
<!-- bite: f7d4cb7b-cf67-48d4-bb00-5917d99bf76c -->

At earliest start, B runs 3 to 5 alongside C (3 to 4) and then E (4 to 5): 4 workers. D runs 5 to 8 with just 1 worker.

Pause and predict: where could C and E go instead?

C can start as late as day 6 (its LS), and E as late as day 7. Move them into D's quiet stretch: **C to days 5 to 6**, **E to days 6 to 7**. Now:

1. **Days 3 to 5**: only B, 2 workers.
2. **Day 5 to 6**: D and C, 1 + 2 = 3.
3. **Day 6 to 7**: D and E, 1 + 2 = 3.
4. **Day 7 to 8**: only D, 1.

## Before and after
<!-- bite: 74d771d2-04dc-4aa1-a50c-4862634d5a70 -->

![Two resource histograms for the fence. Before smoothing, at earliest start, the profile peaks at 4 workers on days 3 to 5. After smoothing, with Buy gate moved to days 5 to 6 and Buy paint to days 6 to 7, the peak is 3 workers and the project still ends on day 12](images/ps-fence-smoothed.svg)

The peak drops from **4 workers to 3**, a 25% cut, and the project still finishes on **day 12**. The total work hasn't changed: 27 worker-days either way. It has only been moved. And no critical activity moved, because they have no float to move with.

## A slide example: the botanical garden
<!-- bite: e7f5b1cb-63ab-4c1a-8e78-d0eddafd4bf6 -->

The MGMT 4135 slides give the same move on a bigger project. One resource, backhoes (digging machines), peaked at 4 in periods 4 to 10. Only two activities had float: Irrigation, and Fence and Walls. The manager delayed Fence and Walls (the less risky one to delay) from period 4 to period 10. The peak fell from 4 backhoes to 3, a 25% saving, with no change in the finish date.

Notice the manager's judgement in there: both activities had float, but one was riskier to push late. The rules pick candidates; the manager still chooses.

## Levelling when there isn't enough
<!-- bite: 5eb79775-7287-488a-ad16-8c634bef6af9 -->

Now say the builder has only **3 workers**, full stop. The earliest-start fence needs 4 on day 3, so something must wait. The levelling rule says: delay the activity with the **most float** first. B has none (it's critical); C has 3. So C waits, and as it happens, delaying C and E within their float fixes the problem with no change to the finish.

If the shortage were worse, float would run out, and activities would have to wait past their latest start. Then the project finishes later. That's the resource-constrained case, and lessons 28 to 31 give a full method for it.

## Sharing resources across projects
<!-- bite: 74e4478c-1f9e-43ff-9c76-0bc496d2fb74 -->

When several projects share staff or equipment, you get overall slippage, uneven demand and bottlenecks. Ways to manage it, from the slides:

1. **A project office** that controls the shared resources centrally.
2. **First come, first served.**
3. **Treat all the projects as one "megaproject"** and schedule them together.
4. **Outsource** some of the work.

Lecture 10 adds a cost example: one engineer shared between two sites is cheaper than two engineers, but only while the travel time and mileage cost less than a second salary.

## Common pitfalls
<!-- bite: 4b0363be-2752-4ac3-aeea-2945ca2c563b -->

1. **Moving a critical activity to smooth.** It has no float, so the finish moves.
2. **Moving an activity past its latest start** in smoothing. That's levelling, and it delays the project.
3. **Forgetting successors.** Moving C later also pushes E, since E follows C.
4. **Thinking smoothing cuts the total work.** It moves work; the total stays the same.

## Check your understanding
<!-- bite: 38133f4d-1888-4ca2-83dc-5038ed6eaebd -->

Try each one before you open the answer.

1. <!-- q: mcq id="8c4a1e57" -->
   Which statement describes resource smoothing?

   - [x] The end date is fixed; non-critical work moves within its float to flatten peaks
   - [ ] Resources are fixed; the project is delayed until demand fits
   - [ ] Critical activities are delayed first
   - [ ] Extra money is spent to shorten activities

   <details><summary>Answer</summary>

   Smoothing keeps the date and uses float only. The second option is levelling; the last is crashing.

   </details>

2. <!-- q: mcq id="3f9d6b02" -->
   Demand exceeds supply on day 4. Three activities are running: X (float 0), Y (float 5), Z (float 2). Under the levelling rule, which is delayed first?

   - [ ] X
   - [x] Y
   - [ ] Z
   - [ ] All three equally

   <details><summary>Answer</summary>

   Y, the activity with the most float.

   </details>

3. <!-- q: exact id="d1e07a6c" answer="25" accept="25%" -->
   Smoothing cuts a crane's peak demand from 4 cranes to 3. By what percentage did the peak fall?

   <details><summary>Answer</summary>

   25%: (4 − 3) / 4.

   </details>

4. <!-- q: exact id="a6b52f18" answer="3" -->
   P (3 workers) runs days 0 to 6 and is critical. R (1 worker) is critical and runs days 6 to 8. Q (2 workers) runs days 0 to 2 at its earliest start and has 6 days of float. If Q is moved within its float to make the peak as low as possible, what is the new peak?

   <details><summary>Answer</summary>

   3. At earliest start, days 0 to 2 need 3 + 2 = 5. With 6 days of float, Q can move to days 6 to 8, next to R: 1 + 2 = 3. P alone needs 3, so the peak is 3, and the finish stays at day 8.

   </details>

5. <!-- q: open id="70e3c9d4" -->
   Why do hired labour and major equipment need levelling more than materials do?

   <details><summary>Answer</summary>

   Uneven demand for hired people or machines wastes money on hiring, bringing to site, setting up and sending away, and on idle days between peaks. Materials can be delivered in lumps when needed at little extra cost, so an uneven profile matters much less.

   </details>

## Before moving on
<!-- bite: 0a2573e3-3edd-407d-977d-e13d90fd8917 -->

You can smooth a profile within float, apply the levelling rule and name ways to share resources. **Next:** [[planning-and-scheduling/28-priority-rules-1|28 — Priority Rules 1: ACTRES, ROT, TIMRES, GENRES, RAF and SAF]].

## Related
<!-- bite: cdf60c32-c4ff-4260-bd95-08679edcc9a3 -->

- [[planning-and-scheduling/index|Planning and scheduling map]]

## About this lesson
<!-- bite: 697f80cc-ae24-4b1d-9fe9-9f5dade82245 -->

**Level:** Intermediate. **Covers:** smoothing against levelling, the fence smoothed from 4 workers to 3, the botanical garden, the levelling rule, and sharing resources across projects.

**Where it sits:** lesson 27 of 35, in part 7 (resources). Part 3 of 7 on resources.

**Source:** the author's own SSG 513 study notes, section 7. The fence's worker numbers and its smoothing are added for this lesson. The histograms come from `scripts/diagrams/planning_scheduling.py`, which checks both profiles and the 27 worker-days.
