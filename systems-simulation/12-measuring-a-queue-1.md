---
id: cbe51eb7-d2a6-46ad-89cb-8c2c1198b7bf
---

# Measuring a Queue 1: The Performance Measures

A queue is judged by a few numbers, each worked out from every customer's arrival, service start, service time and departure.

## Before you start
<!-- bite: fb35497c-37da-4925-9ece-4d229926ae6f -->

You should have read [[systems-simulation/11-queueing-systems-2|11 — Queueing Systems 2]].

After this lesson you will be able to:

1. compute a customer's inter-arrival time, delay, departure time and time in system;
2. compute mean delay, mean time in system, busy time and utilisation;
3. work out when a customer starts service.

## What the performance measures are
<!-- bite: 3808b7c6-51ab-4b22-bbb0-f6fc4874617e -->

The **performance measures** of a queue are the numbers you judge it by: how long customers wait, how long they spend in total, and how busy the server is. Managers care about them because waiting costs customers and idle servers cost money.

This lesson gives the formulas for one customer, then for the whole run. Lesson 13 applies them to a full table by hand, which is a likely exam question.

## The four times for each customer
<!-- bite: 757e8d85-7ba6-446f-adf7-cc70df3ba7c5 -->

Each customer i has four times recorded: an **arrival** time, a **service start** time, a **service time** (how long service takes) and a **departure** time.

The rule that ties them together: **a customer starts service at the later of their own arrival time and the moment the previous customer leaves.** In symbols, start_i = max(arrival_i, dep_(i−1)), for one server serving in order of arrival.

## The measures for one customer
<!-- bite: b383b9d4-1151-4612-b821-463d2fd6c7ff -->

1. **Inter-arrival time**, $a_i = (\text{arrival of } i) - (\text{arrival of } i-1)$.
2. **Delay** (wait in queue), $w_i = (\text{start of service of } i) - (\text{arrival of } i)$.
3. **Departure time**, dep_i = start of service of i + service time of i.
4. **Time in system** (residence time) = departure of i − arrival of i, which equals delay + service time.

*Notation warning:* the class notes use d for both delay and departure. Use your own symbols in an exam, such as w for delay and dep for departure, so the marker can follow you.

## The measures for the whole run
<!-- bite: bc4ad7f0-ccb3-4e28-abb8-b83b73e7c857 -->

For n customers over a simulation time T:

1. **Mean delay** = sum of the delays ÷ n.
2. **Mean time in system** = sum of the times in system ÷ n.
3. **Busy time**, B = sum of all service times.
4. **Utilisation**, ρ = B ÷ T.
5. **Idle time** = T − B.

Utilisation is always between 0 and 1. It is the proportion of time the server is busy: 0.75 means busy three quarters of the time.

## A small example
<!-- bite: bd1576ef-c2b4-47ea-8674-7a42093a77fd -->

Two customers. Customer 1 arrives at 1 and needs 3 minutes. Customer 2 arrives at 2 and needs 4 minutes. The run ends when customer 2 leaves.

1. Customer 1 starts at max(1, nobody before) = 1, so its delay is 0 and it departs at 1 + 3 = 4. Time in system: 3.
2. Customer 2 starts at max(2, 4) = 4, so its delay is 4 − 2 = 2 and it departs at 4 + 4 = 8. Time in system: 6.
3. Mean delay = (0 + 2) ÷ 2 = 1. Mean time in system = (3 + 6) ÷ 2 = 4.5.
4. Busy time B = 3 + 4 = 7. Taking T = 8, utilisation = 7 ÷ 8 = 0.875.

## Common pitfalls
<!-- bite: ec6354ba-fbca-4a47-ac33-872dd1077c2c -->

1. **Starting service at arrival when the server is busy.** Always take the later of arrival and the previous departure.
2. **Mixing delay and time in system.** Delay is waiting only; time in system adds the service.
3. **Dividing busy time by the wrong T.** T is the whole simulation time, not the sum of service times.
4. **A utilisation above 1.** It can't happen; recheck the busy time.

That example had two customers. Next lesson runs a full four-customer table, the format exams use, and draws it on a timeline.

## Check your understanding
<!-- bite: 8bdcfb49-d8ed-4d1d-b819-b08420b9f49a -->

Try each one before you open the answer.

1. <!-- q: exact id="30f2efb2" answer="7" -->
   The previous customer leaves at minute 7. The next customer arrived at minute 5. At what minute does the next customer start service, with one server?

   <details><summary>Answer</summary>

   7: the later of their arrival (5) and the previous departure (7). They wait 2 minutes.

   </details>

2. <!-- q: exact id="338ccc46" answer="11" -->
   A customer arrives at minute 4, starts service at minute 6 and has a service time of 5 minutes. At what minute do they depart?

   <details><summary>Answer</summary>

   11: start of service + service time = 6 + 5.

   </details>

3. <!-- q: exact id="0bc0bba1" answer="7" -->
   Same customer: arrives at 4, starts at 6, service time 5. How long are they in the system, in minutes?

   <details><summary>Answer</summary>

   7: departure − arrival = 11 − 4, or delay + service time = 2 + 5.

   </details>

4. <!-- q: exact id="c2d6c5c7" answer="0.75" accept="3/4|75%" -->
   Over a 40-minute run, a server's service times add up to 30 minutes. What is its utilisation?

   <details><summary>Answer</summary>

   0.75: busy time ÷ total time = 30 ÷ 40. It was idle for 10 minutes.

   </details>

5. <!-- q: gap id="0c451664" answers="delay;time in system|residence time" -->
   Start of service minus arrival is the customer's ___. Departure minus arrival is the customer's ___.

   <details><summary>Answer</summary>

   Delay (wait in queue), then time in system (residence time).

   </details>

6. <!-- q: open id="2b629b91" -->
   Why must utilisation always be between 0 and 1?

   <details><summary>Answer</summary>

   It is the fraction of the run the server spends busy: busy time divided by total time. A single server can't be busy for longer than the run lasts, so busy time is at most T, and it can't be negative.

   </details>

## Before moving on
<!-- bite: 0ea5aaa3-ebd7-427c-9969-126f5392805e -->

You can compute each customer's delay, departure and time in system, and the run's mean delay and utilisation. **Next:** [[systems-simulation/13-measuring-a-queue-2|13 — Measuring a Queue 2]]: a full hand simulation.

## Related
<!-- bite: 48f4a1de-f540-4a64-99fd-f9f70f56d12f -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: db23bd1f-b796-4814-a798-3cae24364bbf -->

**Level:** Beginner. **Covers:** the four recorded times, the per-customer measures, the run measures, the start-of-service rule, and a two-customer example.

**Where it sits:** lesson 12 of 38, part 1 of 2 on measuring a queue.

**Source:** the author's own SSG 418 and SSG 517 study notes, section 3. The two-customer example is added for this lesson.
