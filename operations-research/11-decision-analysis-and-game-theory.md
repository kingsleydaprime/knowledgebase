---
id: 2db87ce4-05b4-439e-8b75-153db41d9372
---

# Decision Analysis and Game Theory

**Source:** `[reference]` — see [[operations-research/index|the domain note]]. The numbers in the worked example were checked by hand; the SciPy script itself has not been run yet — see "Still to run" in [[operations-research/index|the index]].

## Before you start
<!-- bite: 2986baf3-e8e8-4fbf-a821-c23baa0d0ff3 -->

You need basic probability: conditional probability and Bayes' rule, and expected value → [[mathematics/05-probability-statistics/03-probability|probability]]. For the game theory half, you need LP duality → [[operations-research/05-duality-and-sensitivity|note 05]].

After this lesson you will be able to:

1. Draw and solve a decision tree by "rolling back" expected values.
2. Compute the expected value of perfect information, and of an imperfect forecast using Bayes' rule.
3. Explain why expected value isn't always the right criterion, and what a utility function changes.
4. Find the optimal mixed strategy in a two-player zero-sum game, by hand and as an LP.

**Study route:** sections 1–4 (decisions under uncertainty), then stop and redo the survey calculation. Then sections 5–6 (games).

## The kid version
<!-- bite: 5c6d4e80-17ef-453d-b558-2fe5ac916922 -->

You're deciding whether to bring an umbrella. If it rains and you have one, you're fine; if it rains and you don't, you're soaked; if it's sunny, the umbrella is just a nuisance. Draw a little tree: your choice first, then the weather, then how happy you'd be. Weigh each ending by how likely it is, and pick the choice that comes out best on average. **Decision analysis is drawing that tree properly.** And if a friend could tell you the weather in advance, the tree also tells you how much that tip is worth.

**Where the analogy stops working.** The weather doesn't care what you do. In a game, the other side *does* — a rival business or an opponent reacts to your choice. Then "the most likely outcome" stops making sense, because the probabilities depend on what you pick, and you need game theory instead.

## 1. Why this exists
<!-- bite: 8a752a06-4ce9-4047-bd6f-af86e4a276e7 -->

A firm is deciding whether to launch a product. If the market is good, launch earns ₦100 million; if bad, launch loses ₦60 million. Not launching earns nothing. Market research suggests a 60% chance the market is good. And a research agency offers a survey for ₦10 million.

Three questions, all answerable with numbers:

1. Should we launch?
2. How much would *perfect* knowledge of the market be worth?
3. Is the ₦10 million survey worth buying?

## Terms used in decision analysis and game theory
<!-- bite: 1b40bf7f-050e-4570-add5-80a8507c3def -->

1. **Decision node**: This is a point in a tree where *you* choose. Drawn as a square.
2. **Chance node**: This is a point where nature "chooses" at random, with known probabilities. Drawn as a circle.
3. **Expected value**: This is also known as the **expected monetary value** or **EMV**. This is the probability-weighted average of the outcomes: what you'd get on average if you faced the same gamble many times.
4. **Rolling back**: This is the method of solving a tree from the right-hand end backwards: at chance nodes, take the expected value; at decision nodes, take the best option.
5. **Expected value of perfect information**: This is also known as **EVPI**. This is the most you should pay to know the uncertain outcome before deciding.
6. **Utility function**: This is a function that converts money into a measure of how much the outcome is actually *worth to you*, so that attitudes to risk can be included.
7. **Certainty equivalent**: This is the sure amount you'd accept in place of a gamble. If it's less than the gamble's expected value, you're risk-averse.
8. **Zero-sum game**: This is a game where one player's gain is exactly the other's loss, so the payoffs always add to zero.
9. **Pure strategy**: This is a single fixed choice — always play the same move.
10. **Mixed strategy**: This is a strategy of choosing moves at random with fixed probabilities.
11. **Saddle point**: This is a cell in a payoff matrix that's the smallest in its row and the largest in its column. If one exists, both players should play it.
12. **Nash equilibrium**: This is a set of strategies, one per player, where no player can do better by changing theirs alone.

## 2. Decision trees and rolling back
<!-- bite: 3c2ffb43-08e7-466d-9e0d-bdf349183280 -->

```text
                         good (0.6)
                      ┌─────────────── +100
          launch   ○──┤
        ┌─────────────┤ bad (0.4)
   ■ ───┤             └─────────────── −60
        │
        └──────────────────────────────── 0
          don't launch
```

**Roll back.** At the chance node, take the expected value:

$$0.6 \times 100 + 0.4 \times (-60) = 60 - 24 = 36$$

At the decision node, compare 36 (launch) with 0 (don't). **Launch, with expected value ₦36 million.**

Note what the 36 means: not "we'll earn 36." We'll earn either 100 or lose 60. 36 is the long-run average if this were one of many similar bets.

## 3. What information is worth
<!-- bite: e52616e0-53a5-4d31-9cae-76169f1b33e1 -->

### Perfect information

Suppose an oracle would tell you the market before you decide. Then:

1. If the oracle says "good" (probability 0.6), you launch and earn 100.
2. If it says "bad" (probability 0.4), you don't launch and earn 0.

Expected value *with* perfect information: $0.6 \times 100 + 0.4 \times 0 = 60$.

**EVPI = 60 − 36 = ₦24 million.** That's an upper limit: **no forecast, survey or consultant is worth more than ₦24 million for this decision.** It's a useful number for killing proposals quickly.

**Why information has value at all:** it lets you avoid the bad branch. Here, without information you sometimes launch into a bad market and lose 60. The information is worth exactly what it saves you there, on average: $0.4 \times 60 = 24$.

### Imperfect information: the survey

Real surveys aren't oracles. Suppose the agency's track record is:

1. When the market is good, the survey says "positive" 80% of the time.
2. When the market is bad, the survey says "positive" 20% of the time.

To use it, you need the *reverse* probabilities: given a positive survey, how likely is a good market? That's Bayes' rule.

**Step 1 — how often is the survey positive?**

$$P(\text{pos}) = 0.6 \times 0.8 + 0.4 \times 0.2 = 0.48 + 0.08 = 0.56$$

**Step 2 — update the probabilities.**

$$P(\text{good} \mid \text{pos}) = \frac{0.48}{0.56} \approx 0.857, \qquad P(\text{good} \mid \text{neg}) = \frac{0.6 \times 0.2}{0.44} = \frac{0.12}{0.44} \approx 0.273$$

**Step 3 — roll back each branch.**

1. **Positive survey:** launch is worth $0.857 \times 100 + 0.143 \times (-60) \approx 77.1$. Better than 0, so launch.
2. **Negative survey:** launch is worth $0.273 \times 100 + 0.727 \times (-60) \approx -16.4$. Worse than 0, so don't.

**Step 4 — expected value with the survey (before paying for it):**

$$0.56 \times 77.1 + 0.44 \times 0 \approx 43.2$$

**Expected value of the survey's information: 43.2 − 36 = ₦7.2 million.** The survey costs ₦10 million. **Don't buy it.** It's informative, but not informative *enough* for this decision.

**Pause and check:** the survey is worth 7.2, perfect information 24. The survey must always be worth less, because it's never better than knowing.

## 4. When expected value isn't enough
<!-- bite: 172e9959-9ca0-4d64-aaf2-43205690fb2c -->

Expected value treats a sure ₦36 million and the gamble "+100 or −60" as equal. Most people and most firms don't. If losing ₦60 million would bankrupt the firm, the gamble is far worse than its average.

**A utility function** fixes this by scoring outcomes by their value to the decision-maker, then maximising *expected utility*. A risk-averse decision-maker has a concave utility function (each extra naira is worth a little less than the last), so losses hurt more than equal gains help.

In practice:

1. **For small decisions relative to your wealth,** expected value is fine. A large company making many similar bets should mostly use it.
2. **For decisions that could ruin you,** use utility, or at least look at the worst case alongside the average.

**When you don't have probabilities at all**, three classic rules exist. With the launch payoffs:

1. **Maximin (pessimist):** pick the option whose worst outcome is best. Worst of launch: −60. Worst of don't: 0. Choose don't.
2. **Maximax (optimist):** pick the option whose best outcome is best. Launch.
3. **Minimax regret:** for each outcome, "regret" is how much worse you did than the best choice for that outcome. Launch's worst regret: 60 (if bad, you could have had 0). Don't's worst regret: 100 (if good, you missed 100). Choose launch.

They disagree, which is the point: without probabilities, the decision depends on your attitude, and it's better to say so openly than to pretend otherwise.

## 5. Two-player zero-sum games
<!-- bite: 64e913e7-a872-4ec5-8503-07a27e2df521 -->

Now the uncertainty is an opponent. Two firms, Row and Column, each choose a strategy. The matrix gives Row's payoff; Column's is the negative.

```text
                 Column: C1   C2
   Row: R1             3    −1
        R2            −2     1
```

**First, look for a saddle point.** Row, being cautious, looks at the worst of each row: R1 → −1, R2 → −2. The best of those is −1 (the **maximin**). Column looks at the worst for *them* — the largest of each column: C1 → 3, C2 → 1. The best of those is 1 (the **minimax**). Maximin −1 ≠ minimax 1, so **there's no saddle point**. Any fixed choice can be exploited: if Row always plays R1, Column plays C2 and wins 1.

**So both should randomise.** Row plays R1 with probability $p$ and R2 with $1 - p$. Choose $p$ so that Column gets the same result whichever column they choose — then Column can't exploit Row.

1. If Column plays C1, Row's expected payoff is $3p - 2(1 - p) = 5p - 2$.
2. If Column plays C2, it's $-p + (1 - p) = 1 - 2p$.
3. Set them equal: $5p - 2 = 1 - 2p$, so $p = 3/7$.

**Row plays R1 with probability 3/7, R2 with 4/7.** Row's expected payoff: $5(3/7) - 2 = 1/7$ whatever Column does.

By the same reasoning for Column ($q$ = probability of C1): $3q - (1 - q) = -2q + (1 - q)$ gives $q = 2/7$, and the value is again $1/7$.

**The game's value is 1/7**: Row can guarantee an average of at least 1/7, and Column can hold Row to at most 1/7.

### The minimax theorem is LP duality

**Von Neumann's minimax theorem (1928) states that every finite two-player zero-sum game has a value, and both players have mixed strategies that guarantee it.**

Row's problem is an LP: choose probabilities $p_i$ and a value $v$ to

$$\max\; v \quad\text{s.t.}\quad \sum_i p_i a_{ij} \ge v \;\;\text{for every column } j, \qquad \sum_i p_i = 1, \quad p \ge 0$$

In words: maximise the payoff Row is guaranteed, whichever column Column picks. **Column's problem is exactly the dual of Row's**, and strong duality (note 05) says their optimal values are equal. That *is* the minimax theorem. Dantzig reportedly explained LP to von Neumann in 1947, and von Neumann immediately sketched duality from his game theory.

## 6. Beyond zero-sum
<!-- bite: 312fcaa7-502b-4420-9d73-0e4b9710ae13 -->

Most real interactions aren't zero-sum: both firms can do well, or both badly. Then the concept is the **Nash equilibrium** — strategies where no one gains by changing alone.

The famous example is the **prisoner's dilemma**. Two firms each choose a high or low price. If both price high, each earns 5. If one cuts, the cutter earns 7 and the other 1. If both cut, each earns 2. Whatever the other does, cutting pays more (7 > 5 and 2 > 1). So both cut, and both earn 2 — worse for both than (5, 5). **Individually rational choices produce a collectively bad outcome.** This structure explains price wars, arms races and overfishing, and why contracts, regulation and repeated relationships exist.

Nash equilibria of non-zero-sum games aren't LPs in general and can be hard to compute. This is the boundary where operations research hands over to economics.

## Worked example — solving the game as an LP
<!-- bite: a0a405d5-83c3-46c1-bebd-8a1117eb9ae9 -->

**Runnable.** SciPy 1.7+.

```python
# game.py — note 11: solve a zero-sum game for the row player with an LP
import numpy as np
from scipy.optimize import linprog

A = np.array([[3, -1],
              [-2, 1]])        # payoff to the row player
m, n = A.shape
# variables: p_1..p_m, v.  maximise v  ->  minimise -v
c = np.r_[np.zeros(m), -1]
# for every column j:  v - sum_i p_i A[i, j] <= 0
A_ub = np.c_[-A.T, np.ones(n)]
b_ub = np.zeros(n)
A_eq = np.r_[np.ones(m), 0].reshape(1, -1)        # probabilities sum to 1
res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=[1],
              bounds=[(0, None)] * m + [(None, None)], method="highs")
p, v = res.x[:m], res.x[m]
print("row player mixes:", p.round(4), " value:", round(v, 4))
print("column player mixes (from the duals):", (-res.ineqlin.marginals).round(4))
```

```bash
uv run --with scipy python game.py
```

Expected output ($3/7 \approx 0.4286$, $2/7 \approx 0.2857$, $1/7 \approx 0.1429$):

```text
row player mixes: [0.4286 0.5714]  value: 0.1429
column player mixes (from the duals): [0.2857 0.7143]
```

**The column player's strategy comes free from the duals** — one LP solves both sides of the game. Note that $v$ must be allowed to be negative (`(None, None)`), since a game's value can be.

## Common pitfalls and traps
<!-- bite: a457fc98-c0fc-429a-b2d6-c99401946b55 -->

1. **Reading expected value as a forecast.** "Expected ₦36 million" doesn't mean you'll get it; you'll get 100 or −60.
2. **Using the survey's accuracy directly.** "The survey is 80% accurate, so a positive result means 80% chance of success" is wrong. You need Bayes' rule, which also uses the 60% starting belief. Here the right answer was 85.7%.
3. **Paying more than EVPI.** No information source is worth more than perfect information.
4. **Ignoring risk attitude when the stakes are large.** Expected value is right for many small repeated bets, and can be disastrously wrong for one big one.
5. **Playing a fixed strategy without a saddle point.** It can be exploited. Equalising the opponent's payoffs is the defence.
6. **Treating the other side as nature.** A competitor who reacts to you isn't a chance node.

## Check your understanding
<!-- bite: dffb2734-e901-4188-8e42-a384babeb5e7 -->

1. In the launch example, at what probability of a good market does launching stop being worthwhile?
2. Why is the survey worth less than perfect information? Can information ever have negative expected value in a decision tree?
3. In the game, check that if Row plays (3/7, 4/7) and Column plays C2 for certain, Row's expected payoff is 1/7.
4. A matrix is $\begin{pmatrix} 4 & 2 \\ 3 & 1 \end{pmatrix}$ (payoffs to Row). Is there a saddle point? What should each player do?

<details>
<summary>After your attempt — answers</summary>

1. Launch is worth $100p - 60(1 - p) = 160p - 60$. That's above 0 when $p > 0.375$. Below 37.5%, don't launch.
2. The survey sometimes gives the wrong signal, so you sometimes still launch into a bad market or miss a good one; perfect information never does. Free information can't have negative expected value, because you can always ignore it and do what you'd have done anyway — the worst it can do is not change your decision (value 0).
3. Against C2: $(3/7)(-1) + (4/7)(1) = 1/7$. ✓ Against C1: $(3/7)(3) + (4/7)(-2) = 9/7 - 8/7 = 1/7$. ✓
4. Row minimums: 2 and 1, maximin = 2 (R1). Column maximums: 4 and 2, minimax = 2 (C2). They're equal: the saddle point is (R1, C2) with value 2. Row should always play R1 and Column always C2.

</details>

## Practice — independent task
<!-- bite: b89f0793-c159-4e72-b555-f5346c155746 -->

1. **Apply:** a firm can build a large plant (₦200m profit if demand is high, −₦80m if low), a small plant (₦90m high, ₦20m low), or nothing (0). $P(\text{high}) = 0.5$. Draw the tree, roll it back, and compute EVPI.
2. **Bayes:** a test-market costs ₦15m and is correct 75% of the time in both directions. Compute its expected value of information and decide whether to buy it.
3. **Games:** use `game.py` to solve rock–paper–scissors (win 1, lose −1, draw 0). Predict the answer first.

**Done when:** your tree gives a clear decision with its expected value and EVPI, you've decided on the test-market with numbers, and `game.py` confirms your prediction for rock–paper–scissors.

<details>
<summary>Answers to part 1 and part 3 — after your attempt</summary>

Part 1: large $= 0.5(200) + 0.5(-80) = 60$; small $= 0.5(90) + 0.5(20) = 55$; nothing $= 0$. Build large, EV 60. With perfect information: high → large (200), low → small (20), EV $= 110$. EVPI $= 50$.

Part 3: each player plays each move with probability 1/3; the value is 0.

</details>

## Before moving on
<!-- bite: d74b8742-f47d-47a8-8ab4-95f88e5fbcab -->

You're ready when you can roll back a two-stage tree, compute EVPI and the value of an imperfect forecast with Bayes' rule, and find a 2×2 game's mixed strategies by equalising payoffs.

**Recap:**

1. Roll trees back: expected value at chance nodes, best option at decision nodes.
2. EVPI caps what any information is worth; imperfect information needs Bayes' rule.
3. Expected value ignores risk; utility puts it back.
4. Zero-sum games without a saddle point need mixed strategies, and solving one is an LP whose dual is the opponent's problem.

**Next:** [[operations-research/12-queueing-theory|Queueing Theory]] — uncertainty in time: why waiting lines behave the way they do.

## Related
<!-- bite: e86a1b32-d576-4956-aefe-1976996ee2f5 -->

- [[mathematics/05-probability-statistics/03-probability|Probability]] — Bayes' rule and expected value
- [[operations-research/05-duality-and-sensitivity|Duality and Sensitivity]] — the minimax theorem in LP form
- [[operations-research/08-dynamic-programming|Dynamic Programming]] — a decision tree with many stages is a stochastic dynamic program
- [[ai-ml/01-data-scientist/index|Data science]] — where A/B tests are information you pay for
- [[operations-research/index|Operations research map]]

## About this lesson
<!-- bite: 3acb03ce-afc1-458f-a198-d14043a6757a -->

**Level:** Intermediate. **Covers:** Choosing well when the outcome is uncertain: decision trees, expected value, what information is worth, and attitudes to risk. Then the case where the uncertainty is another player choosing against you: zero-sum games, mixed strategies, and why solving a game is an LP.
