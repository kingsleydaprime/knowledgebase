---
id: 6e708829-7d8c-485e-b160-a6ae24376e58
---

# Discrete-Event Simulation

Discrete-event simulation moves a model forward by jumping from one event to the next, because nothing changes in between.

## Before you start
<!-- bite: ade937bf-a4b2-4acc-8527-8ed69eff7b6e -->

You should have read [[systems-simulation/08-the-simulation-study-2|08 — The Simulation Study 2]].

After this lesson you will be able to:

1. define event, state variable, clock and event list;
2. explain how the clock jumps from event to event;
3. step through a small event list by hand.

## What discrete-event simulation is
<!-- bite: e4e059b8-c456-4a25-a158-b5637f829d67 -->

**Discrete-event simulation (DES)** models a system as a sequence of events in time order, each one changing the state at an instant. Between events nothing changes, so the simulation skips straight to the next event instead of ticking through every second.

That skipping is why a model can cover weeks of a real bank in a few seconds: if the next customer arrives in 7 minutes, the computer jumps 7 minutes in one step. This lesson gives the four building blocks, then runs a tiny example by hand.

## The four building blocks
<!-- bite: 8512efe5-ea4c-4251-aac5-63ba24bf736a -->

1. **Event:** This is an instant that may change the state of the system, such as an arrival, the start of service, a departure, a breakdown or a repair.
2. **State variable:** This is one of the variables that together completely describe the system at a moment. Their values are the state.
3. **Clock:** This keeps track of simulation time and triggers events. Simulation time is not wall-clock time: a model can run much faster than real life.
4. **Event list:** This is a list of when each future event will happen, in increasing time order.

## The traffic light
<!-- bite: 642e24d9-6f4d-423c-ba04-52717bb4ba69 -->

The standard small example. The state variable is the light's colour, and its value at any moment completely describes the state. The events are switch to red, switch to yellow and switch to green. Between switches the light just stays one colour, so the simulation only needs to visit the switch times.

## How the clock moves
<!-- bite: fdf523e0-9050-4bfb-af82-52a66aee2400 -->

The whole method is one loop:

1. Look at the event list and take the event with the earliest time.
2. Move the clock straight to that time.
3. Run the event: change the state instantly.
4. Remove it from the list, and add any new events it causes (an arrival schedules the next arrival).
5. Repeat until a stopping time or condition.

## Example: a one-teller bank, by hand
<!-- bite: f538539f-85f3-4327-9abe-feb1dcb69d35 -->

Customers arrive at minutes 0, 3 and 4. Each service takes 5 minutes. The state is the number in the system and whether the teller is busy.

| Clock | Event | What happens | In system | Teller | Event list after |
| --- | --- | --- | --- | --- | --- |
| 0 | Arrival 1 | Teller free, so service starts | 1 | Busy | arrive 3, depart 1 at 5 |
| 3 | Arrival 2 | Teller busy, so 2 waits | 2 | Busy | arrive 4, depart 1 at 5 |
| 4 | Arrival 3 | Teller busy, so 3 waits | 3 | Busy | depart 1 at 5 |
| 5 | Departure 1 | 2 starts service | 2 | Busy | depart 2 at 10 |
| 10 | Departure 2 | 3 starts service | 1 | Busy | depart 3 at 15 |
| 15 | Departure 3 | Queue empty | 0 | Idle | (empty) |

Notice the clock went 0, 3, 4, 5, 10, 15. It never visited minutes 1, 2, 6 to 9 or 11 to 14, because nothing happened then. Each departure scheduled the next customer's departure, 5 minutes later.

## Common pitfalls
<!-- bite: 42eddd4a-a088-4a86-b899-996bb7e8584f -->

1. **Ticking through every time unit.** That is not discrete-event; the clock jumps.
2. **Confusing simulation time with real time.** A 15-minute bank day may take a millisecond to simulate.
3. **Forgetting the events an event causes.** A service start must schedule its departure, or the customer never leaves.

Every example so far has been a queue, and that is no accident: queues are the most common thing simulated. Next lesson describes queueing systems properly.

## Check your understanding
<!-- bite: dd45a75f-9ac6-4927-9a87-04131235aeab -->

Try each one before you open the answer.

1. <!-- q: mcq id="2962cee1" -->
   An event list holds: depart at 12, arrive at 9, breakdown at 15. The clock is at 8. What happens next?

   - [ ] The clock moves to 12 and the departure runs
   - [x] The clock jumps to 9 and the arrival runs
   - [ ] The clock moves to 9, then ticks one minute at a time
   - [ ] All three events run at once

   <details><summary>Answer</summary>

   The clock jumps to 9, the earliest time on the list, and the arrival runs. The list is kept in increasing time order.

   </details>

2. <!-- q: exact id="8fb079dc" answer="12" -->
   A one-teller bank: customers arrive at minutes 0, 2 and 3, and each service takes 4 minutes. Customers are served in order of arrival. At what minute does the third customer leave?

   <details><summary>Answer</summary>

   12. Customer 1 is served from 0 to 4. Customer 2 arrived at 2, waits, and is served from 4 to 8. Customer 3 arrived at 3, waits, and is served from 8 to 12.

   </details>

3. <!-- q: gap id="2a6d8345" answers="clock;event list" -->
   The ___ keeps track of simulation time, and the ___ holds the times of future events in increasing order.

   <details><summary>Answer</summary>

   The clock, then the event list.

   </details>

4. <!-- q: open id="946a57cd" -->
   For a traffic light, name the state variable and the events.

   <details><summary>Answer</summary>

   The state variable is the light's colour; its value completely describes the state. The events are switch to red, switch to yellow and switch to green.

   </details>

5. <!-- q: open id="2987a5a4" -->
   Why can a discrete-event simulation cover a month of a factory's operation in a few seconds?

   <details><summary>Answer</summary>

   Nothing changes between events, so the clock jumps straight from one event to the next instead of stepping through every second. A month with a few thousand events needs only a few thousand steps, each one fast for a computer.

   </details>

## Before moving on
<!-- bite: 09d65cf0-f220-4f48-b3f9-34ecf0f31ac6 -->

You can name the four building blocks and step a small event list by hand. **Next:** [[systems-simulation/10-queueing-systems-1|10 — Queueing Systems 1]].

## Related
<!-- bite: 6465f345-5287-416a-bb66-c1968be53310 -->

- [[systems-simulation/index|Systems simulation map]]
- [[operations-research/12-queueing-theory|Queueing Theory]]: the formulas behind queues, from the operations research side.

## About this lesson
<!-- bite: 48629771-2e89-4595-9bc3-167eecbe73fc -->

**Level:** Beginner. **Covers:** what discrete-event simulation is, event, state variable, clock and event list, the traffic light, the clock loop, and a hand-run bank example.

**Where it sits:** lesson 09 of 38, the start of part 3 (discrete-event simulation and queues).

**Source:** the author's own SSG 418 and SSG 517 study notes, sections E and 2. The hand-run bank example is added for this lesson.
