---
id: 94f3def5-7e4c-4ffa-8647-41d5e63adfdc
---

# Critical Path Method 3: Arrow Diagrams and Event Times

On an arrow diagram, CPM runs on the events, and each activity's times are read off the events at its two ends.

## Before you start
<!-- bite: 21fcf67b-2836-40ee-89ba-11955cd63ac2 -->

You should have read [[planning-and-scheduling/14-critical-path-method-2|14 — Critical Path Method 2]] and [[planning-and-scheduling/09-network-diagrams-2|09 — Network Diagrams 2]].

After this lesson you will be able to:

1. find the earliest and latest time of every event in an arrow diagram;
2. read each activity's ES, EF, LS, LF and float from its events;
3. find the critical path of an arrow diagram, dummies included.

## What changes on an arrow diagram
<!-- bite: 2233becb-d4a1-4be9-afaf-742d8780a991 -->

Last lesson the times lived on the boxes. On an arrow diagram the activities are arrows, and the circles are events, instants with no duration. So the passes are run on the events instead. The ideas are exactly the same; only the bookkeeping moves.

1. **Earliest event time**: This is the soonest an event can happen, meaning the soonest every arrow coming into it can be finished.
2. **Latest event time**: This is the latest an event can happen without delaying the project, meaning late enough that every arrow leaving it can still finish on time.

## The two rules in words
<!-- bite: 4f99ca76-e009-437e-b764-e38f5b151aaf -->

**Forward pass.** An event happens when the last arrow coming into it is done. So its earliest time is the **largest** of (earliest time of the arrow's tail event + the arrow's duration), over all arrows coming in. The first event is at 0.

**Backward pass.** An event must happen early enough for every arrow leaving it. So its latest time is the **smallest** of (latest time of the arrow's head event − the arrow's duration), over all arrows going out. The last event's latest time is the project time.

Then, for an activity running from event i to event j with duration t:

1. ES = earliest time of i, and EF = ES + t.
2. LF = latest time of j, and LS = LF − t.
3. Float = LS − ES.

## The worked example: Craneburg
<!-- bite: b383aa0d-ada0-4b20-aaec-bd6b235c3d85 -->

The 2023/24 paper (Question 3c) gives this arrow network. The arrows, with durations in days:

1-2 = 0 (a dummy), 1-3 = 11, 1-4 = 6, 2-4 = 5, 3-5 = 7, 3-6 = 5, 4-6 = 9, 4-7 = 10, 4-8 = 12, 5-6 = 2, 6-8 = 8, 6-9 = 12, 7-8 = 4, 8-9 = 8.

![The Craneburg arrow network with nine events, each labelled with its earliest and latest time: event 1 0 and 0, event 2 0 and 6, event 3 11 and 11, event 4 6 and 11, event 5 18 and 18, event 6 20 and 20, event 7 16 and 24, event 8 28 and 28, event 9 36 and 36; the critical path 1, 3, 5, 6, 8, 9 is drawn in orange and the dummy 1-2 is dashed](images/ps-aoa-craneburg.svg)

## The forward pass on events
<!-- bite: e21129f6-0ccf-42e5-9f25-c161c259c9c7 -->

Go event by event, in number order.

1. **Event 1**: 0.
2. **Event 2**: only the dummy 1-2 comes in: 0 + 0 = **0**.
3. **Event 3**: only 1-3: 0 + 11 = **11**.
4. **Event 4**: 1-4 gives 0 + 6 = 6, and 2-4 gives 0 + 5 = 5. Largest: **6**.
5. **Event 5**: 3-5 gives 11 + 7 = **18**.
6. **Event 6**: 3-6 gives 16, 4-6 gives 15, 5-6 gives 20. Largest: **20**.
7. **Event 7**: 4-7 gives 6 + 10 = **16**.
8. **Event 8**: 4-8 gives 18, 6-8 gives 28, 7-8 gives 20. Largest: **28**.
9. **Event 9**: 6-9 gives 32, 8-9 gives 36. Largest: **36**.

The project takes **36 days**.

## The backward pass on events
<!-- bite: 1f1ddbce-839b-4972-b8b9-7cbb73b24365 -->

Now right to left, starting with event 9 at 36. Predict event 6 before reading: it has two arrows going out.

1. **Event 9**: 36.
2. **Event 8**: 8-9 gives 36 − 8 = **28**.
3. **Event 7**: 7-8 gives 28 − 4 = **24**.
4. **Event 6**: 6-8 gives 28 − 8 = 20, and 6-9 gives 36 − 12 = 24. Smallest: **20**.
5. **Event 5**: 5-6 gives 20 − 2 = **18**.
6. **Event 4**: 4-6 gives 11, 4-7 gives 14, 4-8 gives 16. Smallest: **11**.
7. **Event 3**: 3-5 gives 11, 3-6 gives 15. Smallest: **11**.
8. **Event 2**: 2-4 gives 11 − 5 = **6**.
9. **Event 1**: 1-2 gives 6, 1-3 gives 0, 1-4 gives 5. Smallest: **0**.

## Reading off the activities
<!-- bite: 9e5bb6af-6484-481a-8052-06824d6d6998 -->

Each activity takes ES from its tail event's earliest time and LF from its head event's latest time.

| Activity | t | ES | EF | LS | LF | Float |
| --- | --- | --- | --- | --- | --- | --- |
| 1-2 (dummy) | 0 | 0 | 0 | 6 | 6 | 6 |
| 1-3 | 11 | 0 | 11 | 0 | 11 | 0 |
| 1-4 | 6 | 0 | 6 | 5 | 11 | 5 |
| 2-4 | 5 | 0 | 5 | 6 | 11 | 6 |
| 3-5 | 7 | 11 | 18 | 11 | 18 | 0 |
| 3-6 | 5 | 11 | 16 | 15 | 20 | 4 |
| 4-6 | 9 | 6 | 15 | 11 | 20 | 5 |
| 4-7 | 10 | 6 | 16 | 14 | 24 | 8 |
| 4-8 | 12 | 6 | 18 | 16 | 28 | 10 |
| 5-6 | 2 | 18 | 20 | 18 | 20 | 0 |
| 6-8 | 8 | 20 | 28 | 20 | 28 | 0 |
| 6-9 | 12 | 20 | 32 | 24 | 36 | 4 |
| 7-8 | 4 | 16 | 20 | 24 | 28 | 8 |
| 8-9 | 8 | 28 | 36 | 28 | 36 | 0 |

## The critical path of Craneburg
<!-- bite: 6f92ac36-4451-4ef8-aa3d-5482b88c7dcd -->

The float column picks out the critical path.

The zero-float activities give the critical path **1-3-5-6-8-9**: 11 + 7 + 2 + 8 + 8 = 36 days.

## A quick check: critical events
<!-- bite: 14a26719-7ca3-4471-99bd-180f510923b3 -->

On the critical path, every event has its earliest time equal to its latest time (events 1, 3, 5, 6, 8 and 9 here). That's a fast way to spot the path on a diagram. But be careful: equal times at both ends of an arrow are necessary, not enough. Arrow 3-6 joins two critical events (3 and 6) yet has 4 days of float, because 11 + 5 = 16 falls short of 20. Always check float = 0 for the arrow itself.

The next lesson puts all of CPM together on a past-paper network, the way an exam answer should be laid out.

## Common pitfalls
<!-- bite: 76329b8a-63d5-4a51-998b-17c5328bca0e -->

1. **Taking ES from the head event.** ES comes from the tail (where the arrow starts), LF from the head (where it ends).
2. **Skipping the dummy.** 1-2 carries event 1's time to event 2 and must be in both passes.
3. **Calling every arrow between two critical events critical.** Check the arrow's own float, as with 3-6.

## Check your understanding
<!-- bite: 846ea621-1ab2-4a44-ab40-a559235545a5 -->

Try each one before you open the answer.

1. <!-- q: exact id="2d9f6b81" answer="12" -->
   An arrow network has activities 1-2 = 4, 1-3 = 6, 2-3 = 0 (dummy), 2-4 = 5, 3-4 = 2, 4-5 = 3 (days). How long does the project take?

   <details><summary>Answer</summary>

   12 days. Event 2 at 4; event 3 at max(6, 4 + 0) = 6; event 4 at max(4 + 5, 6 + 2) = 9; event 5 at 12.

   </details>

2. <!-- q: exact id="a64c0e93" answer="7" -->
   An arrow network has activities 1-2 = 4, 1-3 = 6, 2-3 = 0 (dummy), 2-4 = 5, 3-4 = 2, 4-5 = 3 (days). What is the latest time of event 3?

   <details><summary>Answer</summary>

   7. Backwards: event 5 at 12, event 4 at 9, and event 3 at 9 − 2 = 7.

   </details>

3. <!-- q: exact id="f08b3d27" answer="1" -->
   An arrow network has activities 1-2 = 4, 1-3 = 6, 2-3 = 0 (dummy), 2-4 = 5, 3-4 = 2, 4-5 = 3 (days). What is the float of activity 1-3?

   <details><summary>Answer</summary>

   1 day. ES = 0 (event 1), LF = 7 (event 3's latest time), so LS = 7 − 6 = 1 and float = 1 − 0 = 1.

   </details>

4. <!-- q: mcq id="5b7e2c40" -->
   In an arrow diagram, where does an activity's earliest start come from?

   - [x] The earliest time of its tail event, where the arrow starts
   - [ ] The earliest time of its head event, where the arrow ends
   - [ ] The latest time of its tail event
   - [ ] The sum of all durations before it

   <details><summary>Answer</summary>

   The tail event's earliest time. LF comes from the head event's latest time.

   </details>

5. <!-- q: open id="c93a1f6e" -->
   An arrow joins two events whose earliest and latest times are equal. Must that arrow be critical? Explain.

   <details><summary>Answer</summary>

   No. Equal times at both ends are necessary but not enough. The arrow is critical only if its tail's earliest time plus its duration equals its head's latest time, which means float zero. A short arrow between two critical events, like 3-6 in Craneburg, can have float.

   </details>

## Before moving on
<!-- bite: 6263b461-1ab8-4730-8519-b80715ed596c -->

You can run both passes on events and read off every activity's times and float. **Next:** [[planning-and-scheduling/16-critical-path-method-4|16 — Critical Path Method 4: A Past-Paper Network From Start to Finish]].

## Related
<!-- bite: 568fd088-7ec3-48f5-84a1-7d17c5dcc98d -->

- [[planning-and-scheduling/index|Planning and scheduling map]]

## About this lesson
<!-- bite: 6d654aa8-d60c-471a-828d-d1295e9e1e5a -->

**Level:** Intermediate. **Covers:** earliest and latest event times, reading activity times from events, and the critical path of an arrow diagram.

**Where it sits:** lesson 15 of 35, in part 4 (the critical path method). Part 3 of 4 on CPM.

**Source:** the author's own SSG 513 study notes, section 4 and section 9.2 (the 2023/24 Craneburg network). The diagram comes from `scripts/diagrams/planning_scheduling.py`, which also checks every event time.
