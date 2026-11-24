---
id: 456e0417-3f69-4481-b894-09bbdfa9b206
---

# Queueing Systems 2: Behaviour, Discipline and Kendall's Notation

How customers behave in a line, the rule for who goes next, and a short code for writing any queue down.

## Before you start
<!-- bite: d01a15ab-5c3d-4500-afd8-820b8fe73295 -->

You should have read [[systems-simulation/10-queueing-systems-1|10 — Queueing Systems 1]].

After this lesson you will be able to:

1. tell balking, reneging and jockeying apart;
2. name five queue disciplines;
3. read and write Kendall's notation, such as M/M/1 or M/D/2/10.

## What queue behaviour and discipline are
<!-- bite: fe56a3b8-6785-4131-94d5-6122788ff3b7 -->

Lesson 10 described a queue from the outside. This lesson looks inside the line. First, three things impatient customers do. Then the rules that decide who is served next. Then **Kendall's notation**, a few letters that describe a whole queueing system, so "M/M/1" tells another analyst exactly what you mean.

## Queue behaviour
<!-- bite: 54302f25-1501-4349-84ee-494f6f55f315 -->

1. **Balking:** the customer sees the line is too long and never joins.
2. **Reneging:** the customer joins, feels the line is moving too slowly, and leaves.
3. **Jockeying:** the customer leaves one line to join another they think is faster. This only makes sense when there are several queues.

At a fuel station: the driver who sees six cars and drives past has balked; the driver who waits ten minutes then leaves has reneged; the driver who moves to the next pump's shorter line is jockeying.

## Queue discipline
<!-- bite: 70b3b96b-a27f-4ab3-8ed4-c256f14445f1 -->

The rule for choosing the next customer when a server becomes free:

1. **FIFO, first in first out:** serve in order of arrival. This is the default, and it is the queue data structure.
2. **LIFO, last in first out:** serve the newest first, like plates on a stack.
3. **SIRO, service in random order:** pick anyone at random.
4. **SPT, shortest processing time first:** serve the quickest job next.
5. **PR, service by priority:** serve the most important first, such as emergencies in a hospital.

## Kendall's notation
<!-- bite: 092c0cab-b8f1-45e9-a94a-8a04d5156bfd -->

A queue is written **A/B/c/N/K**:

| Letter | Meaning |
| --- | --- |
| A | Inter-arrival time distribution |
| B | Service time distribution |
| c | Number of servers |
| N | System capacity |
| K | Size of the calling population |

The letters used for distributions:

1. **M:** exponential (the M is for "Markovian", or memoryless). Exponential gaps between arrivals mean the arrivals form a Poisson process.
2. **D:** deterministic, a constant time.
3. **G:** general, any distribution.
4. **E_k:** Erlang with k phases.

When N and K are infinite you leave them off and write just A/B/c.

## Reading some examples
<!-- bite: 242fb7f5-4603-4d61-938f-2d1d82355a8d -->

1. **M/M/1:** exponential inter-arrival times, exponential service times, one server, unlimited capacity and population. The classic queue of lesson 14.
2. **M/D/2:** exponential arrivals, constant service time, two servers.
3. **M/G/1:** exponential arrivals, any service distribution, one server. Lesson 37 uses it for a bank with normal service times.
4. **M/M/3/10:** exponential arrivals and service, three servers, at most 10 customers in the system.
5. **M/M/1/∞/50:** one server, unlimited capacity, a calling population of 50.

## Common pitfalls
<!-- bite: 929ef363-8559-45a8-8e0d-733b49ee4e1f -->

1. **Mixing up balking and reneging.** Balking never joins; reneging joins, then leaves.
2. **Jockeying with one queue.** It needs at least two lines to switch between.
3. **Reading M as "many".** M means exponential (memoryless).
4. **Forgetting N and K default to infinity** when they are left off.

We can now describe a queue fully. Next lesson gives the numbers to judge one by: delay, time in system and utilisation, and how to compute each from arrival and service times.

## Check your understanding
<!-- bite: a1ea1e93-e61d-4e56-8a2c-76ca13843c22 -->

Try each one before you open the answer.

1. <!-- q: mcq id="d27c9c30" -->
   A customer waits in a supermarket line for 15 minutes, gets fed up and walks out without buying. What is this?

   - [ ] Balking
   - [x] Reneging
   - [ ] Jockeying
   - [ ] LIFO

   <details><summary>Answer</summary>

   Reneging: joining, then leaving before service. Balking would be never joining at all.

   </details>

2. <!-- q: mcq id="52b4d310" -->
   A hospital emergency room treats the most seriously ill patient first, whatever their arrival time. Which discipline is this?

   - [ ] FIFO
   - [ ] SIRO
   - [ ] SPT
   - [x] PR

   <details><summary>Answer</summary>

   PR, service by priority.

   </details>

3. <!-- q: open id="f1628cf0" -->
   Write out in words what M/D/3/20 means.

   <details><summary>Answer</summary>

   Exponential inter-arrival times (so Poisson arrivals), constant (deterministic) service times, three servers, and room for at most 20 customers in the system. The calling population is infinite, since K is left off.

   </details>

4. <!-- q: exact id="d89c4ce3" answer="M/M/2" accept="m/m/2" -->
   A post office has two counters and one shared line. Arrivals are Poisson and service times are exponential. There is no limit on the line or the population. Write it in Kendall's notation.

   <details><summary>Answer</summary>

   M/M/2: M for exponential gaps between arrivals, M for exponential service, 2 servers. N and K are infinite, so they are left off.

   </details>

5. <!-- q: mcq id="a5380f69" -->
   In which configuration can jockeying happen?

   - [ ] Single queue, single server
   - [ ] Single queue, multiple servers
   - [x] Multiple queues, multiple servers
   - [ ] Any of them

   <details><summary>Answer</summary>

   Only with multiple queues: there must be another line to move to.

   </details>

## Before moving on
<!-- bite: b08de0a9-e262-46b1-9321-5b6b9092c931 -->

You can name queue behaviours and disciplines, and read and write Kendall's notation. **Next:** [[systems-simulation/12-measuring-a-queue-1|12 — Measuring a Queue 1]]: the performance measures and how to compute them.

## Related
<!-- bite: 908e9947-8829-4aa7-b6df-a2298a6aa5dd -->

- [[systems-simulation/index|Systems simulation map]]
- [[dsa/index|Data Structures and Algorithms]]: FIFO is the queue, LIFO the stack.

## About this lesson
<!-- bite: bc828ad0-08de-4964-a688-f4a60e500649 -->

**Level:** Beginner. **Covers:** balking, reneging and jockeying, five queue disciplines, and Kendall's A/B/c/N/K notation.

**Where it sits:** lesson 11 of 38, part 2 of 2 on queueing systems.

**Source:** the author's own SSG 418 and SSG 517 study notes, sections 2 and 3. The fuel station illustration and the extra Kendall examples are added for this lesson.
