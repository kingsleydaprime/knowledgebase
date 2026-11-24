---
id: c4ad4b3e-08c0-40cb-af42-f4a0be182155
---

# Queueing Theory

**Source:** `[reference]` — see [[operations-research/index|the domain note]]. The code below was run and its output checked.

## Before you start
<!-- bite: ff980b67-4cf3-481e-9bab-76a1bb6f6a86 -->

You should know what a probability distribution and its mean are → [[mathematics/05-probability-statistics/04-random-variables-and-distributions|random variables and distributions]]. Knowing what a Markov chain is helps but isn't required → [[mathematics/05-probability-statistics/06-stochastic-processes/01-markov-chains|Markov chains]].

After this lesson you will be able to:

1. Use Little's law to get one of (number in system, arrival rate, time in system) from the other two, for any stable system.
2. Compute waiting times for M/M/1 and M/M/c queues.
3. Explain, with numbers, why waiting time blows up as utilisation approaches 1, and why pooling servers helps.
4. Say how variability in arrivals and service changes waiting, and what that means for capacity planning.

**Study route:** sections 1–3, then stop and do check question 1. Then M/M/c and pooling (section 5), variability, and the code.

## The kid version
<!-- bite: efbda929-48d7-443b-b26e-59f29ae1f613 -->

At a school tuck shop, one person serves and each customer takes about a minute. If a customer arrives every two minutes, there's hardly ever a queue. If one arrives every 70 seconds, sometimes two turn up close together and a small queue forms, then clears. But if one arrives every 62 seconds, the server is busy almost all the time, and whenever a little bunch of customers arrives, the queue has no time to clear before the next bunch. **Queues don't grow steadily as a shop gets busier. They stay small, then suddenly get huge as the server gets close to never resting.**

**Where the analogy stops working.** It sounds like it's about averages: "the server can handle it, on average". But queues are caused by *randomness* — customers bunching up and some taking longer than others. A perfectly regular shop with a customer exactly every 62 seconds would never have a queue at all.

## 1. Why this exists
<!-- bite: 26b8187b-8da9-41d9-82a6-5ad3787b5166 -->

Queues are everywhere: bank tellers, call centres, hospital beds, toll booths — and in software, request handlers, thread pools, database connection pools, message brokers and CPU run queues. The questions are always the same:

1. How long will people (or requests) wait?
2. How many servers do we need to keep waits below a target?
3. What happens when demand rises 10%?

The simple approach is to compare average capacity with average demand: "we can serve 10 an hour and get 8, so we're fine." Queueing theory shows why that reasoning fails: **at 80% utilisation the average customer already spends five times the service time in the system**, and at 95% it's twenty times.

## Terms used in queueing theory
<!-- bite: bf1a7b7b-cd69-419a-945d-c2689857a30c -->

1. **Arrival rate**: This is the average number of arrivals per unit time, written $\lambda$ (lambda). 8 customers an hour means $\lambda = 8$.
2. **Service rate**: This is the average number of customers one server can finish per unit time, written $\mu$ (mu). A service taking 6 minutes on average means $\mu = 10$ per hour.
3. **Server**: This is whatever does the work — a cashier, a CPU core, a worker thread. $c$ is the number of servers.
4. **Utilisation**: This is also known as **traffic intensity** or **load**. Written $\rho$ (rho), it's the fraction of time a server is busy: $\rho = \lambda / (c\mu)$. A queue is only stable — doesn't grow forever — when $\rho < 1$.
5. **Poisson arrivals**: This means arrivals happen independently and at random at a steady average rate, so the time between them follows an **exponential distribution**. Many independent customers each deciding on their own give approximately Poisson arrivals.
6. **Memoryless**: The exponential distribution is memoryless: how long you've already waited tells you nothing about how much longer it'll be. This property is what makes the M/M/1 formulas simple.
7. **Kendall notation**: This is the shorthand A/S/c for queue types: arrival process / service distribution / number of servers. **M** means Markovian (Poisson arrivals or exponential service), **D** means deterministic (fixed), **G** means general (any distribution).
8. **$L$, $L_q$, $W$, $W_q$**: $L$ is the average number in the system (queueing plus being served); $L_q$ is the average number queueing. $W$ is the average time in the system; $W_q$ is the average time queueing. So $W = W_q + 1/\mu$.
9. **Steady state**: This is the long-run behaviour after the effect of the starting conditions has faded. The formulas in this note describe steady state.

## 2. Little's law
<!-- bite: 695be25e-c1ef-4606-8f3e-e82219a9a673 -->

**Little's law states that, for any stable system, the average number of items in it equals the arrival rate multiplied by the average time each item spends in it.**

$$L = \lambda W$$

It holds for any arrival pattern, any service distribution, any number of servers, and any queue discipline. It's as close to a conservation law as queueing has.

**Using it.** A coffee shop has 6 customers inside on average and serves 30 an hour. Then each customer spends $W = L / \lambda = 6 / 30 = 0.2$ hours, 12 minutes, inside — measured without timing anyone.

**In software:** a service handles 500 requests per second with an average latency of 40 ms. Then on average $L = 500 \times 0.04 = 20$ requests are in flight. If the thread pool has 16 threads, requests must be queueing somewhere. Little's law is the fastest sanity check for concurrency settings.

It also applies to just the queue ($L_q = \lambda W_q$), or just the servers ($\lambda / \mu$ busy servers on average).

## 3. The M/M/1 queue
<!-- bite: eef3538d-7e3b-495f-bb0f-b5c6d1a19cfc -->

One server, Poisson arrivals at rate $\lambda$, exponential service at rate $\mu$, first-come first-served, unlimited waiting room. The results, for $\rho = \lambda / \mu < 1$:

$$L = \frac{\rho}{1 - \rho}, \qquad W = \frac{1}{\mu - \lambda}, \qquad L_q = \frac{\rho^2}{1 - \rho}, \qquad W_q = \frac{\rho}{\mu - \lambda}$$

**Where they come from, in words.** Track the number in the system as a Markov chain: it goes up by one at rate $\lambda$ and down by one at rate $\mu$. In steady state, the flow from "$n$ in system" up to "$n+1$" must equal the flow back down, so $P(n+1) = \rho\,P(n)$. That makes the probabilities geometric: $P(n) = (1 - \rho)\rho^n$. The mean of that distribution is $\rho / (1 - \rho)$, which is $L$, and Little's law gives $W$.

### A worked example

A help desk gets $\lambda = 8$ calls an hour; each takes 6 minutes on average, so $\mu = 10$ per hour.

1. Utilisation: $\rho = 8/10 = 0.8$. The agent is busy 80% of the time.
2. Average number in system: $L = 0.8 / 0.2 = 4$.
3. Average time in system: $W = 1 / (10 - 8) = 0.5$ hours, 30 minutes. Check with Little's law: $L = \lambda W = 8 \times 0.5 = 4$. ✓
4. Average wait before being served: $W_q = 0.8 / 2 = 0.4$ hours, 24 minutes — **four times the 6-minute call itself.**

**Pause and predict:** calls rise to 9 an hour (12.5% more). What happens to $W$?

$W = 1/(10 - 9) = 1$ hour. **12.5% more demand doubled the time in the system.** At 9.5 calls an hour, it's 2 hours.

## 4. Why utilisation is a cliff
<!-- bite: 999d9281-93bd-445c-988e-822c54e1a66f -->

Write $W$ as a multiple of the service time $1/\mu$:

$$\frac{W}{1/\mu} = \frac{1}{1 - \rho}$$

| Utilisation $\rho$ | 0.5 | 0.7 | 0.8 | 0.9 | 0.95 | 0.99 |
|---|---|---|---|---|---|---|
| Time in system ÷ service time | 2 | 3.3 | 5 | 10 | 20 | 100 |

```text
 time in system, in multiples of the service time (one █ = 1×)

 ρ = 0.50  ██                       2×
 ρ = 0.70  ███                      3.3×
 ρ = 0.80  █████                    5×
 ρ = 0.90  ██████████               10×
 ρ = 0.95  ████████████████████     20×
 ρ = 0.99  ███████████████████…     100× — off the chart
```

**The relationship is $1/(1-\rho)$: flat at first, then vertical.** This is the most important picture in capacity planning:

1. **"We're only at 85% CPU" is not comfortable** for a latency-sensitive service. Small surges push it into the steep part.
2. **The last 10% of utilisation costs the most latency.** Running at 70% instead of 90% roughly triples the headroom against surges.
3. **It's why autoscalers target 50–70%**, not 95% → [[control-theory/01-what-control-theory-is-1|control theory]] explains why they oscillate as well.

## 5. Multiple servers and pooling
<!-- bite: e65b5b11-c203-4f05-ba71-3aa491da7702 -->

### The M/M/c queue

$c$ identical servers share one queue. The formula for the probability that an arrival has to wait is the **Erlang C formula**, from A. K. Erlang's 1917 work on telephone exchanges. With $a = \lambda/\mu$ (the average number of busy servers) and $\rho = a/c$:

$$P_0 = \left[\sum_{n=0}^{c-1} \frac{a^n}{n!} + \frac{a^c}{c!\,(1 - \rho)}\right]^{-1}, \qquad P(\text{wait}) = \frac{a^c}{c!\,(1 - \rho)}\,P_0, \qquad L_q = P(\text{wait})\,\frac{\rho}{1 - \rho}$$

Then $W_q = L_q / \lambda$ (Little) and $W = W_q + 1/\mu$. Call centres size their staff with exactly these formulas.

### Three designs with the same total capacity

The help desk still gets 8 calls an hour. Compare three designs, each able to handle 10 calls an hour in total:

1. **One fast agent** ($\mu = 10$): from section 3, $W = 0.5$ hours.
2. **Two slower agents sharing one queue** ($\mu = 5$ each, M/M/2). $a = 1.6$, $\rho = 0.8$. $P_0 = 1/(1 + 1.6 + 2.56/0.4) = 1/9$. $P(\text{wait}) = 6.4/9 \approx 0.711$. $L_q \approx 0.711 \times 4 = 2.84$. $W_q \approx 0.356$ h, $W \approx 0.556$ h.
3. **Two slower agents, each with their own queue**, calls split evenly (two M/M/1 with $\lambda = 4$, $\mu = 5$): $W = 1/(5 - 4) = 1$ hour.

| Design | Time in system |
|---|---|
| One fast server | 30 min |
| Two slow servers, **one shared queue** | 33 min |
| Two slow servers, **separate queues** | 60 min |

Two lessons:

1. **Pooling nearly halves the wait.** With separate queues, one agent can sit idle while the other has a line. A shared queue never wastes an idle server. That's why banks and airports use a single snake queue, and why a shared work queue beats pinning requests to a worker.
2. **One fast server beats several slow ones** for total time, because when there are few customers, the fast server finishes each one sooner. But the gap is small, and two servers give resilience if one fails.

## 6. Variability is the enemy
<!-- bite: 292c3f4d-da17-4d75-bc77-9e724d64ee60 -->

The M/M formulas assume *exponential* service times, which are highly variable. What if every call took exactly 6 minutes (M/D/1)?

The **Pollaczek–Khinchine formula** handles any service distribution (M/G/1). With $C_s$ the coefficient of variation of service time (standard deviation ÷ mean):

$$L_q = \frac{\rho^2 (1 + C_s^2)}{2(1 - \rho)}$$

For exponential service, $C_s = 1$, which gives the M/M/1 result. For fixed service, $C_s = 0$, **halving** the queue. For very variable service — most calls quick, a few very long — $C_s$ can be 3 or more, and queues are five times worse than M/M/1.

**So there are two levers on waiting time: utilisation and variability.** Reducing either works. In software terms: cutting tail latency (a few slow requests) shortens the queue for *everyone*, which is why one slow query can degrade a whole service.

## Worked example — the formulas in Python
<!-- bite: 6bff03f2-0ad5-4ba0-bc04-35b91b8282b7 -->

**Runnable**, standard library only.

```python
# queues.py — note 12: M/M/1 and M/M/c formulas, and the price of high utilisation
from math import factorial

def mmc(lam, mu, c):
    """Return (utilisation, P(wait), Lq, Wq, W) for an M/M/c queue."""
    a, rho = lam / mu, lam / (c * mu)
    if rho >= 1:
        raise ValueError("unstable: arrivals at least as fast as total service")
    tail = a ** c / (factorial(c) * (1 - rho))
    p0 = 1 / (sum(a ** n / factorial(n) for n in range(c)) + tail)
    p_wait = tail * p0                        # Erlang C formula
    lq = p_wait * rho / (1 - rho)
    wq = lq / lam                             # Little's law on the queue
    return rho, p_wait, lq, wq, wq + 1 / mu

print("one fast server   (M/M/1, mu=10):", [round(x, 3) for x in mmc(8, 10, 1)])
print("two slow, pooled  (M/M/2, mu=5): ", [round(x, 3) for x in mmc(8, 5, 2)])
print("two slow, separate (each M/M/1, lam=4, mu=5): W =", round(mmc(4, 5, 1)[4], 3))
print()
for rho in (0.5, 0.7, 0.8, 0.9, 0.95, 0.99):
    w = mmc(rho * 10, 10, 1)[4]
    print(f"utilisation {rho:.2f}: time in system = {w / 0.1:5.1f} x the service time")
```

```bash
python3 queues.py
```

Expected output:

```text
one fast server   (M/M/1, mu=10): [0.8, 0.8, 3.2, 0.4, 0.5]
two slow, pooled  (M/M/2, mu=5):  [0.8, 0.711, 2.844, 0.356, 0.556]
two slow, separate (each M/M/1, lam=4, mu=5): W = 1.0

utilisation 0.50: time in system =   2.0 x the service time
utilisation 0.70: time in system =   3.3 x the service time
utilisation 0.80: time in system =   5.0 x the service time
utilisation 0.90: time in system =  10.0 x the service time
utilisation 0.95: time in system =  20.0 x the service time
utilisation 0.99: time in system = 100.0 x the service time
```

For M/M/1, $P(\text{wait}) = \rho$, which is why the first line shows 0.8 twice.

## Common pitfalls and traps
<!-- bite: a1c06d5f-3b44-478f-ba0b-5e816185cf5f -->

1. **Planning on averages.** "Capacity 10, demand 8, fine" ignores randomness. The queue at 80% utilisation is already large.
2. **Forgetting $\rho < 1$.** At $\rho \ge 1$ there's no steady state — the queue grows without limit, and the formulas give nonsense (negative waits).
3. **Assuming exponential everything.** Real service times are often more variable (heavy tails), real arrivals often burstier. M/M formulas can then be optimistic.
4. **Steady state that never arrives.** A lunchtime rush lasting 30 minutes may never reach steady state. Simulation (note 14) handles time-varying demand better.
5. **Separate queues by accident.** Sharding requests to workers by hash creates separate queues. Pooling the work usually cuts latency for the same hardware.
6. **Little's law on the wrong boundary.** $L$, $\lambda$ and $W$ must all describe the same system — all of it, or just the queue.

## Check your understanding
<!-- bite: 8ee675de-eb4d-46b1-950f-b21cfbd22f7c -->

Attempt these without the note, then compare your reasoning with the answers.

1. <!-- q: exact id="b6a26138" answer="30" -->
   A database connection pool holds each request for an average of 15 ms, and the service makes 2,000 queries a second. How many connections are in use on average?

   <details><summary>Answer</summary>

   30, by Little's law: $L = \lambda W = 2000 \times 0.015$. A pool of 20 would be a bottleneck.

   </details>

2. <!-- q: exact id="4499fc26" answer="0.2" accept="20%|1/5" -->
   An M/M/1 help desk gets $\lambda = 8$ calls an hour and serves $\mu = 10$ an hour. What is the probability the agent is idle?

   <details><summary>Answer</summary>

   0.2: $P(0) = 1 - \rho$, with $\rho = 8/10 = 0.8$.

   </details>

3. <!-- q: exact id="e0ff60fb" answer="0.512" -->
   Same help desk, $\rho = 0.8$. What is the probability there are 3 or more people in the system?

   <details><summary>Answer</summary>

   0.512: $P(n \ge 3) = \rho^3 = 0.8^3$. More than half the time, a caller finds at least two others ahead of or with them.

   </details>

4. <!-- q: open id="39f70a11" -->
   Why does one shared queue feeding several servers beat a separate queue per server, even with identical servers and arrivals?

   <details><summary>Answer</summary>

   With separate queues, one server can sit idle while customers wait in another's queue. A shared queue never lets a server idle while anyone waits, so the same capacity is used more fully exactly when it matters.

   </details>

5. <!-- q: open id="f2bbab43" -->
   A service has 60% average utilisation but serves a mix of 1 ms and 200 ms requests. Why might its latency be worse than M/M/1 predicts?

   <details><summary>Answer</summary>

   Its service times vary far more than M/M/1 assumes (coefficient of variation $C_s$ well above 1), and by Pollaczek–Khinchine the queue grows with $1 + C_s^2$. Short requests get stuck behind long ones.

   </details>

## Practice — independent task
<!-- bite: 447daca9-5a08-4635-a4a7-787c0a30b7ff -->

1. **Predict, then compute:** a clinic gets 12 patients an hour, each doctor sees 5 an hour, and the target is an average wait in the queue under 10 minutes. Predict the number of doctors needed, then use `mmc` to find the smallest $c$ that meets the target.
2. **Apply to software:** estimate, for a service you know (or an invented one with stated numbers): arrival rate, mean service time, number of workers. Use Little's law to check in-flight requests, and `mmc` to estimate queueing at today's load and at 1.5× load.
3. **Extend:** add an `mg1(lam, mu, cs)` function using the Pollaczek–Khinchine formula, and print $W_q$ for $C_s = 0, 1, 2$ at $\rho = 0.8$.

**Done when:** part 1 gives a number with a justification; part 2 produces a short paragraph saying at what load the service gets into trouble; part 3 shows $W_q$ for $C_s = 0$ is exactly half of $C_s = 1$.

<details>
<summary>Answer to part 1 — after your attempt</summary>

$c = 3$ gives $\rho = 0.8$ and $W_q \approx 0.215$ h (13 minutes) — not enough. $c = 4$ gives $\rho = 0.6$ and $W_q \approx 0.036$ h (about 2.2 minutes). So 4 doctors. Note the jump: adding one doctor cut the wait by about 80%, because 3 doctors sat in the steep part of the curve.

</details>

## Before moving on
<!-- bite: 95134f8c-9026-4bd8-ac1b-25589a4bd0c4 -->

You're ready when you can apply Little's law in your head, compute M/M/1 waits, sketch the $1/(1-\rho)$ curve from memory and say what it means for capacity planning, and explain why pooling helps.

**Recap:**

1. Little's law, $L = \lambda W$, holds for any stable system.
2. M/M/1: $W = 1/(\mu - \lambda)$; time in system is $1/(1 - \rho)$ service times — a cliff near $\rho = 1$.
3. M/M/c with Erlang C sizes multi-server systems; pooled queues beat separate ones.
4. Variability matters as much as utilisation: queue length scales with $1 + C_s^2$.

**Next:** [[operations-research/13-inventory-models|Inventory Models]] — the other classic stochastic problem: how much to keep in stock, and when to reorder.

## Related
<!-- bite: 58de96bd-1ff2-4ce8-95fb-f16bbf92eeb8 -->

- [[mathematics/05-probability-statistics/06-stochastic-processes/01-markov-chains|Markov chains]] — the machinery under M/M/1
- [[operations-research/14-simulation|Simulation]] — for queues the formulas can't handle
- [[backend/index|Backend]] — thread pools, connection pools and queues in practice
- [[devops/index|DevOps]] — autoscaling targets and capacity planning
- [[operations-research/index|Operations research map]]

## About this lesson
<!-- bite: ca6dc0ac-6632-4e46-85ae-6443495c1324 -->

**Level:** Intermediate. **Covers:** Why waiting lines behave as they do: Little's law, the M/M/1 and M/M/c queues, why waiting explodes as utilisation approaches 100%, and why one shared queue beats several separate ones. The note that explains your server's latency graph.
