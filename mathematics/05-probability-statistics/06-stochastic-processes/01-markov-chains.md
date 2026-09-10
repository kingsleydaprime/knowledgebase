# Stochastic Processes

**[Advanced]** — probability that evolves over time, and why a system forgets where it started.

## Before you start

- You know distributions and expectation — [[04-random-variables-and-distributions/01-distributions|distributions]].
- You can find eigenvalues and a steady state — [[06-eigenvalues/01-eigenvalues-and-eigenvectors|eigenvalues and eigenvectors]]. This lesson is the probabilistic reading of that one.
- You know conditional probability — [[03-probability/01-probability|probability]].

**What you will be able to do after this lesson:**

1. Model a system as a **Markov chain**, and state the memorylessness assumption it requires.
2. Find a **steady state** two ways — as an eigenvector and by iterating — and say when one is guaranteed to exist.
3. Analyse a **random walk**, and explain why its expected position is zero while its expected *distance* grows as $\sqrt{n}$.
4. Use the **Poisson process** and a simple queue, and explain why utilisation near $100\%$ makes waiting times explode.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 5 is the result that governs every capacity decision you will ever make.

---

## 1. Why this exists

Everything so far has been static: one sample, one distribution, one answer. Real systems **evolve**. A queue grows and shrinks, a share price moves, a molecule diffuses, a user clicks from page to page.

A **stochastic process** is a family of random variables indexed by time. The general case is intractable, so the subject lives on one enormously productive simplification: assume the future depends only on the **present**, not on the whole history. That is the Markov property, and it is both a strong assumption and a surprisingly good approximation for a lot of real systems.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Stochastic process** | A sequence of random variables over time | $X_0, X_1, X_2, \dots$ |
| **State** | The condition the system is in | "sunny", "queue length 3" |
| **Markov property** | The future depends only on the present state | "memorylessness" |
| **Transition matrix** $P$ | $P_{ij} = P(\text{next} = i \mid \text{now} = j)$ | Columns sum to $1$ |
| **Steady state** | A distribution unchanged by a step | The eigenvector for $\lambda = 1$ |
| **Irreducible** | Every state reachable from every other | Needed for a unique steady state |
| **Aperiodic** | Not locked into a fixed cycle | Also needed |
| **Random walk** | Steps of $\pm1$ with given probabilities | The simplest non-trivial process |
| **Poisson process** | Events at a constant rate, independently | Gaps are exponential |
| **Utilisation** $\rho$ | Arrival rate ÷ service rate | The queue's single most important number |

## 3. Markov chains

The defining property:

$$
P(X_{n+1} = j \mid X_n = i,\ X_{n-1}, \dots, X_0) = P(X_{n+1} = j \mid X_n = i)
$$

Given the present, the past is irrelevant. That is a real restriction — a queue's next length depends only on its current length, but a share price's next move arguably depends on momentum — and it is what makes the mathematics tractable.

Represent it as a matrix $P$ where column $j$ holds the probabilities of moving from state $j$. Then the distribution after one step is $P\mathbf{x}$, after $n$ steps $P^n\mathbf{x}$.

**Steady state.** A distribution $\boldsymbol{\pi}$ with $P\boldsymbol{\pi} = \boldsymbol{\pi}$ — precisely an eigenvector with eigenvalue $1$. Every Markov matrix has one, because its columns sum to $1$ (the argument is in [[06-eigenvalues/01-eigenvalues-and-eigenvectors|eigenvalues]]).

**When is it unique, and reached from anywhere?** When the chain is **irreducible** (you can get from any state to any other) and **aperiodic** (it is not trapped in a rigid cycle). Then $P^n\mathbf{x} \to \boldsymbol{\pi}$ for *every* starting $\mathbf{x}$ — the chain **forgets its initial condition**.

The rate of forgetting is $\lvert\lambda_2\rvert$, the second-largest eigenvalue magnitude. Closer to $1$ means slower mixing. This single number is what PageRank's convergence speed and a shuffling algorithm's quality both come down to.

**When it fails:** a chain with an **absorbing** state (one you can never leave) is not irreducible, and it converges to that state regardless of the rest. A strictly alternating chain is periodic and never settles — it oscillates forever. The lab shows both.

## 4. Random walks

Start at $0$; each step is $+1$ or $-1$ with probability $\tfrac12$. Then:

$$
E[X_n] = 0, \qquad \operatorname{Var}(X_n) = n, \qquad E[\lvert X_n\rvert] \approx \sqrt{\frac{2n}{\pi}}
$$

The expectation is zero by symmetry — but that does **not** mean the walker stays near the origin. The typical *distance* grows as $\sqrt{n}$, because variances of independent steps add.

This is the same $\sqrt{n}$ as the standard error in [[05-inference-and-estimation/01-inference|inference]], and for the same reason. It also governs diffusion: a molecule's distance from its start grows with the square root of time, which is why diffusion is fast over microns and hopeless over metres — and why your body needs a circulatory system rather than relying on diffusion.

> [!TIP]
> **Predict before section 5.** A service can handle $10$ requests per second. Requests arrive at $9$ per second — comfortably under capacity. Then traffic rises by $10\%$, to $9.9$ per second, still under capacity. Roughly what happens to the average queue length: up by $10\%$, doubles, or something else? Decide before opening the answers.

## 5. Queues, and why the last 10% of capacity is unusable

A **Poisson process** has events at a constant average rate $\lambda$, independently. The number in a window is Poisson; the **gaps between events are exponential**, and exponential gaps are memoryless — having waited five minutes tells you nothing about how much longer you will wait.

The simplest queue, **M/M/1**, has Poisson arrivals at rate $\lambda$, exponential service at rate $\mu$, and one server. With utilisation $\rho = \lambda/\mu < 1$:

$$
L = \frac{\rho}{1-\rho} \quad\text{(average number in the system)}, \qquad W = \frac{1}{\mu - \lambda} \quad\text{(average time in it)}
$$

Look at the denominator. As $\rho \to 1$, $L \to \infty$ — **not linearly, but hyperbolically**:

| $\rho$ | $L$ |
| ---: | ---: |
| $0.5$ | $1$ |
| $0.8$ | $4$ |
| $0.9$ | $9$ |
| $0.95$ | $19$ |
| $0.99$ | $99$ |

Going from $90\%$ to $99\%$ utilisation multiplies the queue by **eleven**. This is why systems are provisioned at $60$–$70\%$: the headroom is not waste, it is the entire defence against latency collapse. It is also why a motorway at $95\%$ capacity jams from one brake tap.

**Little's Law**, $L = \lambda W$, holds far more generally than M/M/1 — for essentially any stable queue, regardless of distributions. It is the most useful formula in capacity planning.

## Worked example — runnable

**Runnable example:** save as `stochastic.py` in any empty directory and run `python3 stochastic.py`. Standard library only; writes no files.

```python
"""Markov chains, random walks, and why queues explode near full utilisation."""
import math
import random


def step(P, x):
    return [sum(P[i][j] * x[j] for j in range(len(x))) for i in range(len(P))]


def steady_state(P, iters=2000):
    x = [1.0 / len(P)] * len(P)
    for _ in range(iters):
        x = step(P, x)
    return x


def eigen2(A):
    tr = A[0][0] + A[1][1]
    de = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    disc = tr * tr - 4 * de
    if disc < -1e-12:
        return []
    s = math.sqrt(max(0.0, disc))
    return sorted({(tr + s) / 2, (tr - s) / 2}, key=abs, reverse=True)


def mm1(lam, mu):
    rho = lam / mu
    return rho, rho / (1 - rho), 1 / (mu - lam)


if __name__ == "__main__":
    print("Block 1 - a Markov chain forgets where it started")
    # columns: from sunny -> (0.9, 0.1); from rainy -> (0.5, 0.5)
    P = [[0.9, 0.5], [0.1, 0.5]]
    pi = steady_state(P)
    print(f"  transition matrix {P}")
    print(f"  steady state: sunny {pi[0]:.9f}  rainy {pi[1]:.9f}   (exact 5/6, 1/6)")
    assert abs(pi[0] - 5 / 6) < 1e-9
    for start, label in [([1.0, 0.0], "certainly sunny"), ([0.0, 1.0], "certainly rainy"),
                         ([0.5, 0.5], "an even split")]:
        x = start[:]
        for _ in range(60):
            x = step(P, x)
        print(f"    from {label:16}: {x[0]:.9f}, {x[1]:.9f}")
        assert abs(x[0] - 5 / 6) < 1e-9
    lam = eigen2(P)
    print(f"  eigenvalues {[round(v, 6) for v in lam]} - the 1 guarantees a steady state,")
    print(f"  and |lambda2| = {abs(lam[1]):.3f} sets how fast it is reached")

    print()
    print("  the convergence rate really is |lambda2| per step:")
    x = [1.0, 0.0]
    prev_err = None
    for k in range(1, 13):
        x = step(P, x)
        err = abs(x[0] - 5 / 6)
        if k in (1, 2, 4, 8, 12):
            ratio = "" if prev_err is None else ""
            print(f"    step {k:2}: error {err:.3e}   |lambda2|^{k} = {abs(lam[1])**k:.3e}")
        prev_err = err

    print()
    print("Block 2 - when the steady state is NOT unique or NOT reached")
    absorbing = [[1.0, 0.3], [0.0, 0.7]]     # state 0 can never be left
    print(f"  absorbing chain {absorbing}: everything ends in state 0")
    for start in ([0.0, 1.0], [0.5, 0.5]):
        x = start[:]
        for _ in range(400):
            x = step(absorbing, x)
        print(f"    from {start} -> {[round(v, 9) for v in x]}")
    periodic = [[0.0, 1.0], [1.0, 0.0]]      # strict alternation
    print(f"  periodic chain {periodic}: it oscillates and never settles")
    x = [1.0, 0.0]
    seen = []
    for _ in range(6):
        x = step(periodic, x)
        seen.append(round(x[0], 3))
    print(f"    state-0 probability over 6 steps: {seen}")
    assert seen == [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
    print("    its eigenvalues are 1 and -1: the -1 is what makes it oscillate forever")
    assert sorted(eigen2(periodic)) == [-1.0, 1.0]

    print()
    print("Block 3 - random walk: mean zero, typical distance sqrt(n)")
    rng = random.Random(20260910)
    TRIALS = 20000
    print("        n     mean position    mean |position|    sqrt(2n/pi)")
    for n in (10, 100, 1000, 10000):
        finals = []
        for _ in range(TRIALS // 4):
            pos = 0
            for _ in range(n):
                pos += 1 if rng.random() < 0.5 else -1
            finals.append(pos)
        mean_pos = sum(finals) / len(finals)
        mean_abs = sum(abs(v) for v in finals) / len(finals)
        pred = math.sqrt(2 * n / math.pi)
        print(f"  {n:8}   {mean_pos:13.4f}    {mean_abs:15.4f}    {pred:11.4f}")
        assert abs(mean_abs / pred - 1) < 0.06
        assert abs(mean_pos) < 0.5 * math.sqrt(n)
    print("  the mean is ~0 by symmetry, yet the walker is typically sqrt(n) from home")
    print("  this is why diffusion works over microns and fails over metres")

    print()
    print("Block 4 - exponential gaps are memoryless")
    rng2 = random.Random(31337)
    waits = [rng2.expovariate(1.0) for _ in range(200000)]
    print(f"  mean wait {sum(waits)/len(waits):.4f} (should be 1.0)")
    for already in (0.0, 1.0, 3.0):
        remaining = [w - already for w in waits if w > already]
        print(f"    given you have already waited {already}: mean REMAINING wait"
              f" {sum(remaining)/len(remaining):.4f}")
    surv = [w - 3.0 for w in waits if w > 3.0]
    assert abs(sum(surv) / len(surv) - 1.0) < 0.05
    print("  the remaining wait is always the same - the process has no memory")

    print()
    print("Block 5 - the last 10% of capacity is unusable")
    MU = 10.0
    print("   arrivals/s   utilisation   avg in system L   avg wait W (s)")
    for lam in (5.0, 8.0, 9.0, 9.5, 9.9, 9.99):
        rho, L, W = mm1(lam, MU)
        print(f"   {lam:10.2f}   {rho:11.3f}   {L:15.2f}   {W:14.4f}")
    _, L90, _ = mm1(9.0, MU)
    _, L99, _ = mm1(9.9, MU)
    print(f"  raising arrivals by 10% (9.0 -> 9.9) multiplies the queue by {L99/L90:.1f}x")
    assert abs(L99 / L90 - 11.0) < 0.01
    print("  a 10% traffic increase, an 11x queue. Utilisation is not a linear dial.")

    print()
    print("  Little's Law, L = lambda * W, checked at each point above:")
    for lam in (5.0, 9.0, 9.9):
        rho, L, W = mm1(lam, MU)
        print(f"    lambda={lam:5.2f}: L={L:8.3f}   lambda*W={lam*W:8.3f}")
        assert abs(L - lam * W) < 1e-9

    print()
    print("stochastic: passed")
```

Expected output:

```
Block 1 - a Markov chain forgets where it started
  transition matrix [[0.9, 0.5], [0.1, 0.5]]
  steady state: sunny 0.833333333  rainy 0.166666667   (exact 5/6, 1/6)
    from certainly sunny : 0.833333333, 0.166666667
    from certainly rainy : 0.833333333, 0.166666667
    from an even split   : 0.833333333, 0.166666667
  eigenvalues [1.0, 0.4] - the 1 guarantees a steady state,
  and |lambda2| = 0.400 sets how fast it is reached

  the convergence rate really is |lambda2| per step:
    step  1: error 6.667e-02   |lambda2|^1 = 4.000e-01
    step  2: error 2.667e-02   |lambda2|^2 = 1.600e-01
    step  4: error 4.267e-03   |lambda2|^4 = 2.560e-02
    step  8: error 1.092e-04   |lambda2|^8 = 6.554e-04
    step 12: error 2.796e-06   |lambda2|^12 = 1.678e-05

Block 2 - when the steady state is NOT unique or NOT reached
  absorbing chain [[1.0, 0.3], [0.0, 0.7]]: everything ends in state 0
    from [0.0, 1.0] -> [1.0, 0.0]
    from [0.5, 0.5] -> [1.0, 0.0]
  periodic chain [[0.0, 1.0], [1.0, 0.0]]: it oscillates and never settles
    state-0 probability over 6 steps: [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
    its eigenvalues are 1 and -1: the -1 is what makes it oscillate forever

Block 3 - random walk: mean zero, typical distance sqrt(n)
        n     mean position    mean |position|    sqrt(2n/pi)
        10          0.0888             2.4656         2.5231
       100         -0.1792             7.9952         7.9788
      1000          0.6416            25.6488        25.2313
     10000          0.7268            79.8668        79.7885
  the mean is ~0 by symmetry, yet the walker is typically sqrt(n) from home
  this is why diffusion works over microns and fails over metres

Block 4 - exponential gaps are memoryless
  mean wait 1.0005 (should be 1.0)
    given you have already waited 0.0: mean REMAINING wait 1.0005
    given you have already waited 1.0: mean REMAINING wait 1.0029
    given you have already waited 3.0: mean REMAINING wait 0.9929
  the remaining wait is always the same - the process has no memory

Block 5 - the last 10% of capacity is unusable
   arrivals/s   utilisation   avg in system L   avg wait W (s)
         5.00         0.500              1.00           0.2000
         8.00         0.800              4.00           0.5000
         9.00         0.900              9.00           1.0000
         9.50         0.950             19.00           2.0000
         9.90         0.990             99.00          10.0000
         9.99         0.999            999.00         100.0000
  raising arrivals by 10% (9.0 -> 9.9) multiplies the queue by 11.0x
  a 10% traffic increase, an 11x queue. Utilisation is not a linear dial.

  Little's Law, L = lambda * W, checked at each point above:
    lambda= 5.00: L=   1.000   lambda*W=   1.000
    lambda= 9.00: L=   9.000   lambda*W=   9.000
    lambda= 9.90: L=  99.000   lambda*W=  99.000

stochastic: passed
```

Block 5 is the practical payoff. Arrivals rise by ten per cent — from $9.0$ to $9.9$ against a capacity of $10$ — and the queue grows **eleven-fold**. No component got slower and nothing failed; the arithmetic of $\frac{\rho}{1-\rho}$ did it.

## Common pitfalls and traps

- **Assuming the Markov property without checking.** If the next state depends on how you arrived, the model is wrong. The usual repair is to enlarge the state so it carries the needed history.
- **Expecting every chain to converge.** Absorbing states and periodicity both break it. Irreducible *and* aperiodic is the condition.
- **Reading $E[X_n] = 0$ as "stays near zero".** The mean is zero; the typical distance grows as $\sqrt{n}$. Mean and magnitude are different questions.
- **Sizing a system by average utilisation.** Averages hide the queue. At $\rho = 0.9$ the average queue is already nine deep, and bursts make it far worse.
- **Assuming exponential service times.** M/M/1 assumes them, and real service times are often much more variable — which makes queues *worse* than the formula predicts, not better.
- **Confusing rate with probability.** $\lambda = 5$ per second is a rate, not a probability, and can exceed $1$.

## Check your understanding

1. A chain has $P = \begin{pmatrix}0.7 & 0.4\\ 0.3 & 0.6\end{pmatrix}$. Find its steady state.
2. Why does every Markov transition matrix have $\lambda = 1$?
3. After $100$ steps of a symmetric random walk, what is the expected position, and roughly the typical distance from the origin?
4. A server handles $20$ requests/s; arrivals are $16$/s. Find $\rho$, $L$ and $W$.
5. You have waited $10$ minutes for a bus whose arrivals are Poisson with mean gap $10$ minutes. What is the expected further wait?

<details><summary>Answers — open only after an attempt</summary>

1. Solve $P\boldsymbol{\pi} = \boldsymbol{\pi}$: $0.7\pi_1 + 0.4\pi_2 = \pi_1$ gives $0.4\pi_2 = 0.3\pi_1$, so $\pi_1 = \tfrac43\pi_2$. With $\pi_1+\pi_2 = 1$: $\boldsymbol{\pi} = (\tfrac47, \tfrac37)$.
2. Because each column sums to $1$, the all-ones vector satisfies $\mathbf{1}^{T}P = \mathbf{1}^{T}$ — so $P^{T}$ has eigenvalue $1$, and a matrix shares eigenvalues with its transpose.
3. $E[X_{100}] = 0$ by symmetry. Typical distance $\approx \sqrt{2(100)/\pi} \approx 7.98$, so around $8$ steps from home.
4. $\rho = 16/20 = 0.8$. $L = \frac{0.8}{0.2} = 4$ requests. $W = \frac{1}{20-16} = 0.25$ s. Check: $L = \lambda W = 16 \times 0.25 = 4$. ✓
5. **Ten minutes.** Exponential waits are memoryless — the time already spent carries no information. This is genuinely counter-intuitive and genuinely true for a Poisson process.

**And the prediction from section 4:** the queue grows by a factor of about **eleven**, not ten per cent. $L$ goes from $\frac{0.9}{0.1} = 9$ to $\frac{0.99}{0.01} = 99$. The $1-\rho$ in the denominator shrank by a factor of ten, and that denominator is what governs the answer.
</details>

## Practice — independent task

Simulate an M/M/1 queue event by event, and check the formulas you have been handed.

1. Implement a discrete-event simulation: draw exponential inter-arrival gaps at rate $\lambda$ and exponential service times at rate $\mu$, and track each customer's arrival, service-start and departure times.
2. Measure the average number in the system and the average time in it. Compare against $\frac{\rho}{1-\rho}$ and $\frac{1}{\mu-\lambda}$ at $\rho = 0.5, 0.8, 0.9, 0.95$.
3. **Handle the warm-up.** A simulation starting from an empty queue under-reports until it settles. Discard an initial transient, justify the length you chose, and show the difference it makes to your $\rho = 0.95$ answer.
4. Verify **Little's Law** directly from your event log, without using either formula.
5. Then break the M/M/1 assumption: replace exponential service with a **constant** service time at the same mean (an M/D/1 queue). Measure $L$ and compare with M/M/1 at the same $\rho$. Theory says the wait halves — confirm or refute it with your numbers, and explain what property of the service distribution is responsible.

**Edge cases:** $\rho \ge 1$ (the queue is unstable — what does your simulation do, and what *should* it do?); $\rho$ very small; a run too short to be meaningful at high $\rho$.

**Done when:** your simulated $L$ and $W$ match theory at every stable $\rho$, Little's Law holds on your raw event log, and your M/D/1 result is explained by service-time variability rather than just reported.

## Tradeoffs, limits and extensions

**The Markov property is an approximation, and a load-bearing one.** Real arrivals are bursty and correlated, not Poisson; real service times are more variable than exponential. Both make queues **worse** than M/M/1 predicts. The Pollaczek–Khinchine formula generalises to arbitrary service distributions and shows the wait grows with service-time *variance* — which is why reducing variability often beats making the average faster.

**Continuous time and the diffusion limit.** Let a random walk's steps shrink and its rate grow and you get **Brownian motion**, the continuous-time analogue, which underlies both physical diffusion and the Black–Scholes model. The $\sqrt{n}$ becomes $\sqrt{t}$.

**Where this connects.** The steady state is an eigenvector, so everything from [[06-eigenvalues/01-eigenvalues-and-eigenvectors|eigenvalues]] applies — including that convergence speed is $\lvert\lambda_2\rvert$, and PageRank is this lesson at web scale. Hidden Markov models add unobserved states and are the basis of a great deal of speech and sequence modelling.

## Before moving on

You are done with this lesson when you can:

- Write a transition matrix, find its steady state both ways, and state the conditions for uniqueness.
- Explain why a random walk has zero mean and $\sqrt{n}$ typical distance.
- Explain memorylessness and why the remaining wait never changes.
- Use $\frac{\rho}{1-\rho}$ and Little's Law, and say why systems are not run near full utilisation.

**Recap for later lookup:** Markov property — the future depends only on the present; steady state is the eigenvector for $\lambda=1$, unique and reached when the chain is irreducible and aperiodic, at rate $\lvert\lambda_2\rvert$; random walk has $E[X_n]=0$, $\operatorname{Var}=n$, typical distance $\sqrt{2n/\pi}$; Poisson process has exponential, memoryless gaps; M/M/1 gives $L = \frac{\rho}{1-\rho}$, $W = \frac{1}{\mu-\lambda}$; **Little's Law $L=\lambda W$ holds almost always**.

**Where next:** this is the last lesson in probability and statistics. It connects directly to [[06-eigenvalues/01-eigenvalues-and-eigenvectors|eigenvalues]] and to queueing in [[architecture/index|architecture]] and [[os/index|operating systems]].

## Related

- [[06-eigenvalues/01-eigenvalues-and-eigenvectors|Eigenvalues]] — the steady state, algebraically
- [[05-inference-and-estimation/01-inference|Inference]] — the same $\sqrt{n}$, in a different setting
- [[04-random-variables-and-distributions/01-distributions|Distributions]] — Poisson and exponential
- [[architecture/index|architecture/]] — where queueing decides capacity in practice
