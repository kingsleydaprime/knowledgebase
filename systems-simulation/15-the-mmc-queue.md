---
id: 1cc47624-e826-40bf-ab9a-3a1cd6366887
---

# The M/M/c Queue

The M/M/c queue has c identical servers sharing one line, and its formulas give the chance of waiting and the average queue.

## Before you start
<!-- bite: 6c1b326f-07fd-48be-b196-817f9aa2cb87 -->

You should have read [[systems-simulation/14-littles-law-and-the-mm1-queue|14 — Little's Law and the M/M/1 Queue]].

After this lesson you will be able to:

1. state the stability condition for c servers;
2. compute P0, the probability of waiting, Lq, Wq, W and L for an M/M/c queue;
3. check the formulas collapse to M/M/1 when c = 1.

## What the M/M/c queue is
<!-- bite: 695c7031-1996-4913-b9d1-6e60195672dc -->

The **M/M/c queue** is the multi-server version of M/M/1: exponential gaps between arrivals, exponential service, and **c identical servers** fed by one shared line. A bank with three tellers and one snake line is M/M/3.

The formulas here are the standard textbook results, often called Erlang C after the probability of waiting. **The author's notebook photos for this part were unreadable, so these were added from standard queueing theory: compare them with your own notes.**

## Two loads to keep apart
<!-- bite: 6c386cd1-5e99-4ac4-a35d-024b27a5d827 -->

1. **Offered load:** a = λ/μ. It is how many servers' worth of work arrives. With a = 1.5, the arrivals would keep one and a half servers busy.
2. **Utilisation per server:** ρ = λ/(cμ) = a/c. It must be **less than 1** for the queue to be stable.

## The formulas
<!-- bite: 4f263afe-bd69-49c5-8247-d68038ee9291 -->

1. **Probability the system is empty:**
$$P_0 = \left[\sum_{n=0}^{c-1}\frac{a^n}{n!} + \frac{a^c}{c!}\cdot\frac{1}{1-\rho}\right]^{-1}$$
2. **Probability an arriving customer has to wait** (Erlang C):
$$P(\text{wait}) = \frac{a^c}{c!\,(1-\rho)}\,P_0$$
3. **Average queue length:** $L_q = P(\text{wait})\cdot\dfrac{\rho}{1-\rho}$
4. **Average wait in queue:** $W_q = \dfrac{L_q}{\lambda}$
5. **Average time in system:** $W = W_q + \dfrac{1}{\mu}$
6. **Average number in system:** $L = L_q + a$, which is Little's law again.

## Example: two servers
<!-- bite: be29a56e-800c-4c5a-bb56-2c53f090ae47 -->

λ = 2 per minute, μ = 1.5 per minute, c = 2.

1. a = 2 ÷ 1.5 = 1.333, and ρ = 1.333 ÷ 2 = 0.667, which is below 1, so the queue is stable.
2. The sum has n = 0 and n = 1: 1 + 1.333 = 2.333. The last term is (1.333² ÷ 2!) × 1/(1 − 0.667) = 0.889 × 3 = 2.667. So P0 = 1 ÷ (2.333 + 2.667) = 1 ÷ 5 = 0.2.
3. P(wait) = 2.667 × 0.2 = 0.533. About half of arrivals have to wait.
4. Lq = 0.533 × (0.667 ÷ 0.333) = 0.533 × 2 = 1.07 customers.
5. Wq = 1.07 ÷ 2 = 0.53 minutes.

**Correction:** the source notes work this example as P0 = 1/(1 + 1.333 + 1.778/0.333) = 0.130, which leaves out the 2! in the last term (1.778/0.333 should be 1.778/2 × 3 = 2.667). With the 2! put back, P0 = 0.2 and the figures above follow.

## The sanity check: c = 1
<!-- bite: 8766e3cc-673a-41e9-9475-06f69547f30b -->

With one server the formulas should give M/M/1. With c = 1, a = ρ and the sum is just 1, so P0 = 1 ÷ (1 + ρ/(1 − ρ)) = 1 − ρ. Then P(wait) = ρ/(1 − ρ) × (1 − ρ) = ρ, and Lq = ρ × ρ/(1 − ρ) = ρ²/(1 − ρ). Both match lesson 14. ✓

## Common pitfalls
<!-- bite: 0a244435-78fb-4cb1-a62f-94a723c60566 -->

1. **Using λ/μ as the stability test.** For c servers it is λ/(cμ) < 1. Two servers can handle a = 1.5, one cannot.
2. **Forgetting the factorials.** Both $a^n/n!$ in the sum and $a^c/c!$ in the last term need them.
3. **Thinking c servers means c times less waiting.** Pooling helps more than that at high load, and less at low load; compute it.

That ends the queueing theory. Every one of these formulas assumed random arrival and service times. Next part asks where randomness in a simulation comes from: random numbers, starting with what makes a number "random" at all.

## Check your understanding
<!-- bite: c9069c67-dcac-41bc-a891-96a440edc2cd -->

Try each one before you open the answer.

1. <!-- q: mcq id="ca7aa7ba" -->
   Customers arrive at λ = 5 per minute, each server handles μ = 2 per minute. What is the fewest servers that keeps the queue stable?

   - [ ] 2
   - [x] 3
   - [ ] 4
   - [ ] 5

   <details><summary>Answer</summary>

   3. Stability needs ρ = λ/(cμ) < 1, so c > 5/2 = 2.5. Two servers give ρ = 1.25; three give 0.83.

   </details>

2. <!-- q: exact id="807c7d24" answer="0.142857" sigfigs="2" accept="1/7" -->
   An M/M/2 queue has λ = 3 per minute and μ = 2 per minute. What is P0, the probability the system is empty?

   <details><summary>Answer</summary>

   1/7 ≈ 0.14. a = 1.5 and ρ = 0.75. The sum is 1 + 1.5 = 2.5. The last term is (1.5²/2!) × 1/(1 − 0.75) = 1.125 × 4 = 4.5. P0 = 1/(2.5 + 4.5) = 1/7.

   </details>

3. <!-- q: exact id="c03cdb04" answer="0.642857" sigfigs="2" accept="9/14" -->
   Same M/M/2 queue: λ = 3, μ = 2 per minute, so a = 1.5, ρ = 0.75 and P0 = 1/7. What is the probability an arriving customer has to wait?

   <details><summary>Answer</summary>

   9/14 ≈ 0.64: P(wait) = a²/(2!(1 − ρ)) × P0 = 2.25/0.5 × 1/7 = 4.5/7.

   </details>

4. <!-- q: exact id="a652bac6" answer="1.928571" sigfigs="2" accept="27/14" -->
   Same M/M/2 queue: ρ = 0.75 and P(wait) = 9/14. What is Lq, the average number waiting?

   <details><summary>Answer</summary>

   About 1.93: Lq = P(wait) × ρ/(1 − ρ) = (9/14) × 3 = 27/14.

   </details>

5. <!-- q: open id="3f881067" -->
   Show that the M/M/c formula for P0 becomes 1 − ρ when c = 1.

   <details><summary>Answer</summary>

   With c = 1, a = λ/μ = ρ. The sum runs from n = 0 to 0, so it is just 1. The last term is ρ¹/1! × 1/(1 − ρ) = ρ/(1 − ρ). So P0 = 1/(1 + ρ/(1 − ρ)) = 1/(1/(1 − ρ)) = 1 − ρ, the M/M/1 result.

   </details>

## Before moving on
<!-- bite: 00f93f18-de30-420e-b5fb-dc7585d4fbad -->

You can test an M/M/c queue for stability and compute its measures. **Next:** [[systems-simulation/16-random-numbers-1|16 — Random Numbers 1]].

## Related
<!-- bite: 7d781e04-720f-4b89-984e-63498a346d08 -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: 0beb6205-7ca0-408a-a22b-192c6ebc518c -->

**Level:** Intermediate. **Covers:** offered load and utilisation, the M/M/c (Erlang C) formulas, a two-server example and the c = 1 check.

**Where it sits:** lesson 15 of 38, the end of part 3 (discrete-event simulation and queues).

**Source:** the author's own SSG 517 study notes, section 3. The formulas are standard queueing theory added in the notes because the notebook photos were unreadable; check them against your own notes. The worked example is corrected as stated above.
