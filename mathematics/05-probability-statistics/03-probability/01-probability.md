# Probability

**[Beginner → Intermediate]** — reasoning about what has not happened yet, and the conditional rule that almost everyone gets backwards.

## Before you start

- You can count arrangements and combinations — [[02-discrete-math/06-combinatorics-and-counting|combinatorics and counting]].
- You know set notation, union, intersection and complement — [[04-sets/01-sets|sets]].
- Helpful: [[01-descriptive-statistics/01-descriptive-statistics|descriptive statistics]], for the language of data.

**What you will be able to do after this lesson:**

1. Build a **sample space** and compute probabilities from it, including when outcomes are not equally likely.
2. Apply the addition and multiplication rules, and distinguish **mutually exclusive** from **independent** — two things that sound similar and are nearly opposites.
3. Use **conditional probability** and tree diagrams, and state Bayes' theorem.
4. Explain why a test that is "99% accurate" can still be wrong most of the time it fires.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 4 is the result most people refuse to believe.

---

## 1. Why this exists

Statistics describes data you have. Probability reasons about data you do not — the next request, the next patient, the next roll.

Two things make it worth doing carefully rather than by instinct. The first is that human intuition about chance is **reliably** wrong, and wrong in predictable directions: we overweight vivid outcomes, we see patterns in noise, and we confuse "the chance of the evidence given the cause" with "the chance of the cause given the evidence". The second is that the correct answers are usually short — a few lines of arithmetic — so there is no excuse for guessing.

Sections 4 and 5 are both cases where the arithmetic and the instinct disagree sharply, and the arithmetic is right.

## 2. Terminology

| Term | Plain-English definition | Example |
| :--- | :--- | :--- |
| **Experiment** | A process with an uncertain outcome | Rolling a die |
| **Outcome** | One thing that can happen | Rolling a $4$ |
| **Sample space** $S$ | The set of all outcomes | $\{1,2,3,4,5,6\}$ |
| **Event** | A subset of the sample space | "even" $= \{2,4,6\}$ |
| **Complement** $A'$ | Everything not in $A$ | "not even" $= \{1,3,5\}$ |
| **Mutually exclusive** | Cannot both happen | "even" and "odd" |
| **Independent** | One happening tells you nothing about the other | Two separate coin flips |
| **Conditional** $P(A\mid B)$ | Probability of $A$ **given that** $B$ happened | — |
| **Prior / posterior** | Belief before / after seeing evidence | The heart of Bayes |

For equally likely outcomes:

$$
P(A) = \frac{\text{number of outcomes in } A}{\text{number of outcomes in } S}
$$

The phrase "equally likely" is doing real work and is often false. A drawing pin does not land point-up half the time just because there are two possibilities.

## 3. The rules

**Complement.** $P(A') = 1 - P(A)$. Often far easier than the direct count — "at least one" problems are nearly always best done as $1 - P(\text{none})$.

**Addition.**

$$
P(A \cup B) = P(A) + P(B) - P(A \cap B)
$$

Subtract the overlap, or it is counted twice. This is inclusion–exclusion from [[04-sets/01-sets|sets]]. When $A$ and $B$ are **mutually exclusive** the overlap is empty and it simplifies to $P(A) + P(B)$.

**Multiplication.**

$$
P(A \cap B) = P(A)\,P(B \mid A)
$$

and when $A$ and $B$ are **independent**, $P(B\mid A) = P(B)$, so it becomes $P(A)P(B)$.

### Mutually exclusive is not independent

These get confused constantly, and they are close to opposites.

- **Mutually exclusive:** they cannot both happen. $P(A\cap B) = 0$.
- **Independent:** one tells you nothing about the other. $P(A\cap B) = P(A)P(B)$.

If $A$ and $B$ are mutually exclusive and both have non-zero probability, then knowing $A$ happened tells you $B$ definitely did **not** — which is the strongest possible dependence. So mutually exclusive events with positive probability are **never** independent.

### Conditional probability and Bayes

$$
P(A \mid B) = \frac{P(A \cap B)}{P(B)}
$$

Rearranging both forms of the multiplication rule gives **Bayes' theorem**:

$$
P(A\mid B) = \frac{P(B\mid A)\,P(A)}{P(B)}
$$

Its purpose is to **reverse the conditioning**. You usually know $P(\text{evidence} \mid \text{cause})$ — a test's accuracy given the disease — and you want $P(\text{cause}\mid \text{evidence})$ — the chance of disease given a positive test. These are different numbers, and treating them as the same is the *base rate fallacy*.

> [!TIP]
> **Predict before section 4.** A disease affects $1$ in $1{,}000$ people. A test detects it $99\%$ of the time when present, and gives a false positive only $1\%$ of the time when absent. You test positive. Roughly what is the chance you have the disease — $99\%$, $90\%$, $50\%$, or under $10\%$? Commit before opening the answers.

## 4. Why "99% accurate" is not 99% confidence

Take $100{,}000$ people and count.

- **Have the disease:** $100$. The test catches $99$ of them.
- **Do not have it:** $99{,}900$. The test wrongly flags $1\%$ — that is **$999$ people**.

So $99 + 999 = 1{,}098$ people test positive, and only $99$ are ill:

$$
P(\text{disease} \mid \text{positive}) = \frac{99}{1098} \approx 9.0\%
$$

**The false positives outnumber the true positives ten to one**, because the healthy group is a thousand times larger. A small error rate applied to a huge group beats a large success rate applied to a tiny one.

This is not a trick. It is why screening programmes for rare conditions need confirmatory tests, and why the same test is far more informative when given to people who already have symptoms — that raises the prior, and the prior is half the calculation.

## 5. Where intuition fails again

**The Monty Hall problem.** Three doors, a prize behind one. You pick a door. The host — who knows where the prize is — opens a *different* door revealing no prize, and offers you the switch. Switching wins $\tfrac23$ of the time.

The reason is that the host's action is **not random**: he never opens the prize door. Your first pick is right $\tfrac13$ of the time, and that never changes. So the prize is behind the other unopened door the remaining $\tfrac23$. The lab simulates it, and also simulates a variant where the host opens a door *at random* — where switching genuinely does not help, which shows the host's knowledge is the whole mechanism.

**The birthday problem.** In a room of $23$ people, the chance two share a birthday exceeds $\tfrac12$. Compute the complement: all birthdays different is

$$
\frac{365}{365}\times\frac{364}{365}\times\cdots\times\frac{343}{365} \approx 0.493
$$

so at least one match has probability $\approx 0.507$. The count that matters is not $23$ people but $\binom{23}{2} = 253$ **pairs**.

## Worked example — runnable

**Runnable example:** save as `probability.py` in any empty directory and run `python3 probability.py`. Standard library only; writes no files.

```python
"""Probability rules, Bayes, Monty Hall and birthdays - theory against simulation."""
import math
import random
from itertools import product

TRIALS = 200000


def p_at_least_one(p_single, n):
    """The complement trick: 1 - P(none)."""
    return 1 - (1 - p_single) ** n


def bayes(prior, sensitivity, false_positive_rate):
    """P(disease | positive)."""
    true_pos = prior * sensitivity
    false_pos = (1 - prior) * false_positive_rate
    return true_pos / (true_pos + false_pos)


def birthday_match(n, days=365):
    p_all_different = 1.0
    for k in range(n):
        p_all_different *= (days - k) / days
    return 1 - p_all_different


def monty(switch, host_knows, rng):
    prize = rng.randrange(3)
    pick = rng.randrange(3)
    if host_knows:
        opts = [d for d in range(3) if d != pick and d != prize]
    else:
        opts = [d for d in range(3) if d != pick]
    opened = rng.choice(opts)
    if not host_knows and opened == prize:
        return False                    # the host revealed the prize: that game is void
    if switch:
        pick = next(d for d in range(3) if d != pick and d != opened)
    return pick == prize


if __name__ == "__main__":
    print("Block 1 - the sample space, and 'equally likely' doing real work")
    two_dice = list(product(range(1, 7), repeat=2))
    print(f"  rolling two dice: {len(two_dice)} equally likely outcomes")
    for target in (2, 7, 12):
        hits = sum(1 for a, b in two_dice if a + b == target)
        print(f"    P(sum = {target:2}) = {hits}/36 = {hits/36:.4f}")
    assert sum(1 for a, b in two_dice if a + b == 7) == 6
    print("  7 is six times more likely than 2, though both are 'a possible total'")

    print()
    print("Block 2 - addition, complement, and 'at least one'")
    print(f"  P(at least one 6 in 4 rolls) = 1 - (5/6)^4 = {p_at_least_one(1/6, 4):.6f}")
    rng = random.Random(20260910)
    hits = sum(1 for _ in range(TRIALS) if any(rng.randrange(6) == 0 for _ in range(4)))
    print(f"  simulated over {TRIALS:,} trials:            {hits/TRIALS:.6f}")
    assert abs(hits / TRIALS - p_at_least_one(1 / 6, 4)) < 0.005
    # the direct count would need four separate cases; the complement needs one line
    print("  the direct sum needs four cases; the complement needs one line")

    print()
    print("  mutually exclusive is NOT independent:")
    # A = 'even', B = 'odd' on one die
    pa, pb, pab = 0.5, 0.5, 0.0
    print(f"    P(A)={pa}  P(B)={pb}  P(A and B)={pab}  P(A)P(B)={pa*pb}")
    print("    0 != 0.25, so they are dependent - knowing A tells you B did NOT happen")
    assert pab != pa * pb

    print()
    print("Block 3 - conditional probability from a two-way table")
    #                  rain   no rain
    table = {("umbrella", "rain"): 60, ("umbrella", "dry"): 30,
             ("none", "rain"): 15, ("none", "dry"): 95}
    total = sum(table.values())
    rain = sum(v for (u, w), v in table.items() if w == "rain")
    umb_and_rain = table[("umbrella", "rain")]
    print(f"  {total} days: {rain} rainy, {umb_and_rain} of those with an umbrella")
    print(f"    P(umbrella)            = {sum(v for (u,w),v in table.items() if u=='umbrella')/total:.4f}")
    print(f"    P(umbrella | rain)     = {umb_and_rain/rain:.4f}")
    print(f"    P(rain | umbrella)     = {umb_and_rain/sum(v for (u,w),v in table.items() if u=='umbrella'):.4f}")
    print("  the last two are DIFFERENT numbers - that is the whole point of Bayes")
    assert abs(umb_and_rain / rain - 0.8) < 1e-9

    print()
    print("Block 4 - the base rate fallacy, counted out")
    prior, sens, fpr = 1 / 1000, 0.99, 0.01
    POP = 100000
    ill = int(POP * prior)
    detected = int(ill * sens)
    healthy = POP - ill
    false_pos = int(healthy * fpr)
    print(f"  {POP:,} people, disease rate 1 in 1,000, test 99% sensitive, 1% false positive")
    print(f"    truly ill            {ill:>6,}   of whom the test catches {detected:,}")
    print(f"    healthy              {healthy:>6,}   of whom the test wrongly flags {false_pos:,}")
    print(f"    total positives      {detected + false_pos:>6,}")
    print(f"    P(ill | positive) = {detected}/{detected+false_pos} = {detected/(detected+false_pos):.4f}")
    print(f"  Bayes gives the same: {bayes(prior, sens, fpr):.4f}")
    assert abs(bayes(prior, sens, fpr) - detected / (detected + false_pos)) < 0.001
    assert bayes(prior, sens, fpr) < 0.10
    print("  under 10%, from a test that is 99% accurate in both directions")

    print()
    print("  the prior is half the calculation - the same test on symptomatic people:")
    for prior_i in (0.001, 0.01, 0.1, 0.3, 0.5):
        print(f"    prior {prior_i:5.3f}  ->  P(ill | positive) = {bayes(prior_i, sens, fpr):.4f}")
    assert bayes(0.5, sens, fpr) > 0.98

    print()
    print("Block 5 - Monty Hall: the host's knowledge is the mechanism")
    for knows in (True, False):
        for switch in (False, True):
            rng = random.Random(99)
            wins = sum(monty(switch, knows, rng) for _ in range(TRIALS))
            label = "knows where the prize is" if knows else "opens at random"
            print(f"  host {label:24}  switch={str(switch):5}  win rate {wins/TRIALS:.4f}")
    rng = random.Random(99)
    stay = sum(monty(False, True, rng) for _ in range(TRIALS)) / TRIALS
    rng = random.Random(99)
    swap = sum(monty(True, True, rng) for _ in range(TRIALS)) / TRIALS
    assert abs(stay - 1/3) < 0.01 and abs(swap - 2/3) < 0.01
    print("  with a knowing host: 1/3 staying, 2/3 switching")
    print("  with a random host the advantage disappears (games where he reveals")
    print("  the prize are void, and the rest are an even split)")

    print()
    print("Block 6 - the birthday problem: pairs, not people")
    print("    n    P(shared birthday)    pairs")
    for n in (10, 23, 30, 50, 70):
        print(f"   {n:3}    {birthday_match(n):18.4f}    {n*(n-1)//2:5}")
    assert birthday_match(23) > 0.5 and birthday_match(22) < 0.5
    rng = random.Random(4242)
    hits = 0
    for _ in range(50000):
        bs = [rng.randrange(365) for _ in range(23)]
        hits += len(set(bs)) < 23
    print(f"  simulated at n=23 over 50,000 rooms: {hits/50000:.4f}")
    assert abs(hits / 50000 - birthday_match(23)) < 0.01
    print("  23 people make 253 pairs, and it is the pairs that get compared")

    print()
    print("probability: passed")
```

Expected output:

```
Block 1 - the sample space, and 'equally likely' doing real work
  rolling two dice: 36 equally likely outcomes
    P(sum =  2) = 1/36 = 0.0278
    P(sum =  7) = 6/36 = 0.1667
    P(sum = 12) = 1/36 = 0.0278
  7 is six times more likely than 2, though both are 'a possible total'

Block 2 - addition, complement, and 'at least one'
  P(at least one 6 in 4 rolls) = 1 - (5/6)^4 = 0.517747
  simulated over 200,000 trials:            0.517990
  the direct sum needs four cases; the complement needs one line

  mutually exclusive is NOT independent:
    P(A)=0.5  P(B)=0.5  P(A and B)=0.0  P(A)P(B)=0.25
    0 != 0.25, so they are dependent - knowing A tells you B did NOT happen

Block 3 - conditional probability from a two-way table
  200 days: 75 rainy, 60 of those with an umbrella
    P(umbrella)            = 0.4500
    P(umbrella | rain)     = 0.8000
    P(rain | umbrella)     = 0.6667
  the last two are DIFFERENT numbers - that is the whole point of Bayes

Block 4 - the base rate fallacy, counted out
  100,000 people, disease rate 1 in 1,000, test 99% sensitive, 1% false positive
    truly ill               100   of whom the test catches 99
    healthy              99,900   of whom the test wrongly flags 999
    total positives       1,098
    P(ill | positive) = 99/1098 = 0.0902
  Bayes gives the same: 0.0902
  under 10%, from a test that is 99% accurate in both directions

  the prior is half the calculation - the same test on symptomatic people:
    prior 0.001  ->  P(ill | positive) = 0.0902
    prior 0.010  ->  P(ill | positive) = 0.5000
    prior 0.100  ->  P(ill | positive) = 0.9167
    prior 0.300  ->  P(ill | positive) = 0.9770
    prior 0.500  ->  P(ill | positive) = 0.9900

Block 5 - Monty Hall: the host's knowledge is the mechanism
  host knows where the prize is  switch=False  win rate 0.3341
  host knows where the prize is  switch=True   win rate 0.6659
  host opens at random           switch=False  win rate 0.3341
  host opens at random           switch=True   win rate 0.3324
  with a knowing host: 1/3 staying, 2/3 switching
  with a random host the advantage disappears (games where he reveals
  the prize are void, and the rest are an even split)

Block 6 - the birthday problem: pairs, not people
    n    P(shared birthday)    pairs
    10                0.1169       45
    23                0.5073      253
    30                0.7063      435
    50                0.9704     1225
    70                0.9992     2415
  simulated at n=23 over 50,000 rooms: 0.5031
  23 people make 253 pairs, and it is the pairs that get compared

probability: passed
```

Block 4 is worth reading twice. Every number in it is favourable — $99\%$ detection, only $1\%$ false positives — and the answer is still under $10\%$. Block 5's second half is the control: remove the host's knowledge and the Monty Hall advantage vanishes, which proves the advantage came from his knowledge rather than from the number of doors.

## Common pitfalls and traps

- **Confusing mutually exclusive with independent.** Mutually exclusive events with positive probability are maximally *dependent*.
- **Assuming outcomes are equally likely.** "There are two possibilities, so it is 50–50" is wrong for drawing pins, weather, and almost everything real.
- **Reversing the conditional.** $P(\text{positive}\mid\text{ill})$ and $P(\text{ill}\mid\text{positive})$ are different numbers. Block 3 shows two that differ by a factor of more than two.
- **Ignoring the base rate.** The prior is not a detail you add at the end; it is half the calculation, as block 4's table of priors shows.
- **Adding probabilities that overlap.** Without subtracting $P(A\cap B)$ you can produce a probability above $1$ — a useful self-check.
- **Multiplying probabilities that are not independent.** The multiplication rule needs $P(B\mid A)$; using $P(B)$ when the events are linked is how correlated risks get badly underestimated.

## Check your understanding

1. A bag has 5 red and 3 blue balls. Two are drawn **without** replacement. Find $P(\text{both red})$.
2. $P(A) = 0.6$, $P(B) = 0.5$, $P(A\cup B) = 0.8$. Find $P(A\cap B)$. Are $A$ and $B$ independent?
3. Why is "at least one" usually computed via the complement?
4. A test is 95% sensitive with a 5% false-positive rate, for a condition affecting 2% of people. What is $P(\text{condition}\mid\text{positive})$?
5. Why does switching win $\tfrac23$ in Monty Hall?

<details><summary>Answers — open only after an attempt</summary>

1. $P = \frac{5}{8}\times\frac{4}{7} = \frac{20}{56} = \frac{5}{14} \approx 0.357$. The second fraction changed because the draw was without replacement — the events are not independent.
2. From $P(A\cup B) = P(A)+P(B)-P(A\cap B)$: $0.8 = 0.6+0.5-P(A\cap B)$, so $P(A\cap B) = 0.3$. Independence would need $P(A)P(B) = 0.6\times0.5 = 0.30$. It is $0.3$, so **yes**, they are independent.
3. Because "at least one" has many disjoint cases (exactly one, exactly two, ...) but exactly one complement: *none*. One subtraction replaces a sum over cases.
4. True positives $0.02\times0.95 = 0.019$; false positives $0.98\times0.05 = 0.049$. So $P = \frac{0.019}{0.019+0.049} = \frac{0.019}{0.068} \approx 0.279$ — about $28\%$, from a test that is "95% accurate".
5. Your initial pick is correct with probability $\tfrac13$, and nothing the host does changes that — he always opens a non-prize door, so his action carries no information about *your* door. The remaining $\tfrac23$ must therefore sit on the one other unopened door.

**And the prediction from section 3:** **under 10%** — about $9\%$. The healthy group is a thousand times larger, so its $1\%$ false-positive rate produces $999$ false alarms against only $99$ true ones.
</details>

## Practice — independent task

Implement `simulate(experiment, trials, seed)` plus a small library of experiments, and use it to check theory against simulation systematically.

1. Write experiments for: rolling two dice and summing; drawing without replacement from a bag; a run of $n$ coin flips; the birthday problem for arbitrary $n$.
2. For each, compute the **exact** probability as well, and report both alongside the absolute difference.
3. Report a **margin of error**: with $N$ trials the standard error of a proportion is $\sqrt{p(1-p)/N}$. Assert your simulated value is within three standard errors of the exact one, and explain why that is the right kind of check rather than a fixed tolerance.
4. Show the error shrinking: run each experiment at $N = 10^2, 10^3, 10^4, 10^5$ and tabulate the difference. Confirm it falls roughly as $1/\sqrt{N}$ — **not** as $1/N$.
5. Then a case with no simple closed form: the expected number of rolls of a fair die until **all six faces** have appeared. Simulate it, then compare against the exact answer $6\left(1+\tfrac12+\cdots+\tfrac16\right) = 14.7$ — the coupon collector's problem.

**Edge cases:** probability $0$ and $1$ events (the standard error is zero — what does your check do?); very small probabilities where $N$ trials may produce zero successes; a seed that makes one run unrepresentative.

**Done when:** every experiment passes the three-standard-error check, your step-4 table shows the $1/\sqrt{N}$ trend, and you can explain why quadrupling the trials only halves the error.

## Tradeoffs, limits and extensions

**Two readings of "probability".** The **frequentist** reading is a long-run frequency: the probability of heads is what the proportion converges to. The **Bayesian** reading is a degree of belief updated by evidence, which is what Bayes' theorem formalises. Most working practice mixes them; the distinction becomes sharp in [[05-inference-and-estimation/01-inference|inference]], where the two schools give different answers to "what does this data tell me".

**Simulation is evidence, not proof.** Every simulated figure here carries sampling error of order $1/\sqrt{N}$. With $200{,}000$ trials that is about $0.1\%$ — good enough to confirm a theoretical value, never good enough to establish one. The exact calculations in the text are what make the claims; the simulations check the arithmetic.

**Independence is an assumption, and usually the weakest one.** Multiplying probabilities is easy and often wrong: mortgage defaults were modelled as near-independent, and the 2008 crisis was in large part the discovery that they were not. When an estimate seems impossibly small, an unjustified independence assumption is the first place to look.

## Before moving on

You are done with this lesson when you can:

- Build a sample space and compute from it without assuming equal likelihood.
- Distinguish mutually exclusive from independent, and say why they are close to opposites.
- Apply Bayes' theorem, and explain the base rate fallacy with a count rather than a formula.
- Explain Monty Hall in terms of the host's knowledge.

**Recap for later lookup:** $P(A) = \frac{|A|}{|S|}$ for equally likely outcomes; $P(A') = 1-P(A)$; $P(A\cup B) = P(A)+P(B)-P(A\cap B)$; $P(A\cap B) = P(A)P(B\mid A)$, and $=P(A)P(B)$ only when independent; $P(A\mid B) = \frac{P(B\mid A)P(A)}{P(B)}$; mutually exclusive events with positive probability are never independent; a rare condition makes false positives dominate.

**Next:** [[04-random-variables-and-distributions/01-distributions|Random Variables and Distributions]] — attaching numbers to outcomes, and the handful of distributions that describe most of reality.

## Related

- [[02-discrete-math/06-combinatorics-and-counting|Combinatorics]] — the counting every sample space needs
- [[04-sets/01-sets|Sets]] — where inclusion–exclusion comes from
- [[06-stochastic-processes/01-markov-chains|Stochastic Processes]] — probability that evolves over time
- [[05-inference-and-estimation/01-inference|Inference]] — using probability to reason back from data
