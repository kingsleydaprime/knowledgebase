---
id: d6814aa7-4603-4254-bf14-ff5489a7c120
---

# Dynamic Programming

**Source:** `[reference]` — see [[operations-research/index|the domain note]]. The code below was run and its output checked.

## Before you start
<!-- bite: 36ab5dc0-4053-4cd4-bda8-caa63ceac0bd -->

You should have met dynamic programming as a coding pattern — memoisation and tabulation → [[dsa/03-algorithms/07-dynamic-programming/index|DSA: dynamic programming]]. If you haven't, this note still works, but the DSA version gives you more reps. You should know what an expected value is → [[mathematics/05-probability-statistics/04-random-variables-and-distributions|random variables]].

After this lesson you will be able to:

1. Describe a multi-stage decision problem in terms of stages, states, decisions and a recursion.
2. Solve a resource-allocation problem by backward recursion with tables, by hand.
3. Extend a recursion to uncertain outcomes using expected values.
4. Say when dynamic programming is the right tool and when the state space makes it hopeless.

**Study route:** sections 1–3, then **close the note** and rebuild the allocation tables yourself. Then section 4 (uncertainty) and the code.

## The kid version
<!-- bite: ede9d616-a838-4231-8c56-ff79c3193165 -->

You're walking home through a town and want the shortest route. At every crossroads you have a choice. Here's the trick: whichever crossroads you're at, the best way home *from there* doesn't depend on how you got there. So work backwards: from the crossroads next to your house, the best way is obvious. From one further out, it's "the best first step, then whatever was best from where that lands you." **Dynamic programming is solving a big decision by working backwards one step at a time, remembering the best answer from each place.**

**Where the analogy stops working.** A town has a few hundred crossroads. Many real problems have a "place" (the state) described by several numbers at once — stock of five products, cash, time — and the number of states multiplies until there are too many to remember. That's called the curse of dimensionality, and it's dynamic programming's real limit.

## 1. Why this exists
<!-- bite: 05ad71ea-f49c-42eb-86a0-f7f2b3a58958 -->

A firm has 3 units of budget to spread across three regions. Each region's return depends on how much it gets, and not linearly — the first unit helps most:

```text
   units given:   0    1    2    3
   region R1      0    4    6    7
   region R2      0    3    8    9
   region R3      0    5    6    7
```

The returns aren't proportional, so this isn't an LP. You could list every split (there are 10), but with 10 regions and 20 units there are about 10 million, and with real problems it's worse. **Dynamic programming solves it by deciding one region at a time**, so the work grows with (regions × budget × options) instead of exploding.

Richard Bellman developed the method at RAND in the early 1950s for multi-stage planning. He later said he chose the name "dynamic programming" partly because it sounded impressive and was hard to object to.

## Terms used in dynamic programming
<!-- bite: a9694dbe-1d32-4258-9bfb-91637607b385 -->

1. **Stage**: This is one step of the decision sequence — a region to fund, a month to plan, a city on a route. Stages are usually numbered in the order decisions are made.
2. **State**: This is the information you need at a stage to make the rest of the decisions well. Here, it's "how much budget is left." A good state is the smallest summary of the past that the future depends on.
3. **Decision**: This is the choice made at a stage — how many units to give this region.
4. **Transition**: This is the rule for the next state given the current state and decision. Budget left next = budget left now − units given.
5. **Value function**: This is also known as the **optimal value function** or **cost-to-go**. Written $f_k(s)$, it's the best total you can get from stage $k$ onwards if you arrive in state $s$.
6. **Bellman equation**: This is also known as the **recursion** or the **functional equation**. This is the formula that defines $f_k$ in terms of $f_{k+1}$.
7. **Principle of optimality**: This is Bellman's statement that an optimal policy has the property that whatever the first decision was, the remaining decisions must be optimal for the state that decision leads to.
8. **Policy**: This is a rule giving the best decision for every stage and state — not just a single plan, but what to do in any situation you might find yourself in.

## 2. The principle of optimality
<!-- bite: 1398a3a0-1fc7-4b76-802f-a681cd45c189 -->

**Bellman's principle of optimality states that, whatever the current state and however you got there, the remaining decisions of an optimal plan must themselves be optimal from that state.**

That's what makes working backwards valid. It means you can write the best value from stage $k$ as:

$$f_k(s) = \max_{\text{decisions } d} \Big[\, \text{reward}_k(s, d) + f_{k+1}\big(\text{next state}(s, d)\big) \Big]$$

In words: **the best you can do from here is the best over all choices now of (what this choice earns) plus (the best you can do from where it leaves you).**

The principle fails if the future depends on the past in a way the state doesn't capture. If region R2's returns depended on how much R1 got, "budget left" wouldn't be a sufficient state. The fix is always to enlarge the state until the principle holds — which is where the cost comes from.

## 3. Backward recursion, step by step
<!-- bite: 9ff37c80-7816-46ad-b5ca-33406b98bf34 -->

Set up the allocation problem:

1. **Stages:** region 1, region 2, region 3, in that order.
2. **State $s$:** units of budget still unallocated when you reach that stage.
3. **Decision $k$:** units to give this region, from 0 to $s$.
4. **Transition:** next state $= s - k$.
5. **Recursion:** $f_i(s) = \max_{0 \le k \le s} \big[ R_i(k) + f_{i+1}(s - k) \big]$, with $f_4(s) = 0$ (nothing left to fund).

Work from the last stage backwards.

### Stage 3 — region R3

Whatever's left goes to R3 (giving less would waste it). So $f_3(s) = R_3(s)$:

| $s$ | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| $f_3(s)$ | 0 | 5 | 6 | 7 |

### Stage 2 — region R2

For each possible budget $s$, try each $k$ for R2, and add the best R3 can do with the rest.

| $s$ | $k=0$ | $k=1$ | $k=2$ | $k=3$ | $f_2(s)$ | best $k$ |
|---|---|---|---|---|---|---|
| 0 | 0 + 0 = 0 | — | — | — | 0 | 0 |
| 1 | 0 + 5 = 5 | 3 + 0 = 3 | — | — | 5 | 0 |
| 2 | 0 + 6 = 6 | 3 + 5 = 8 | 8 + 0 = 8 | — | 8 | 1 or 2 |
| 3 | 0 + 7 = 7 | 3 + 6 = 9 | 8 + 5 = **13** | 9 + 0 = 9 | **13** | 2 |

Read the bold cell: with 3 units left for R2 and R3 together, give R2 two units (earning 8) and leave one for R3 (earning 5).

**Pause and predict:** at stage 1 we start with 3 units. What will $f_1(3)$ be, and how much goes to R1?

### Stage 1 — region R1

Only one state matters here: we start with the full budget, $s = 3$.

| $s$ | $k=0$ | $k=1$ | $k=2$ | $k=3$ | $f_1(3)$ |
|---|---|---|---|---|---|
| 3 | 0 + 13 = **13** | 4 + 8 = 12 | 6 + 5 = 11 | 7 + 0 = 7 | **13** |

### Read the plan forwards

1. R1 gets $k = 0$. Budget left: 3.
2. At stage 2 with $s = 3$, the table says give R2 two units. Left: 1.
3. R3 gets the last unit.

**Allocation: R1 = 0, R2 = 2, R3 = 1. Total return: 13.**

Notice R1 gets nothing even though its first unit is worth 4 — more than R2's first unit. That's because R2's *second* unit is worth 5 (from 3 to 8), and greedy "best next unit" reasoning misses it. That's exactly the kind of interaction dynamic programming handles and greedy doesn't → [[dsa/03-algorithms/06-greedy-algorithms/01-when-greedy-works|when greedy works]].

### What it cost

Each stage-2 cell considers at most 4 options, for 4 states: about 16 evaluations. Stage 1: 4. Brute force over all splits: 20 combinations. With $n$ regions and budget $B$, dynamic programming does about $n \times B^2$ work instead of the combinatorial number of splits. For 10 regions and 20 units: about 4,000 evaluations against about 10 million.

## 4. Decisions under uncertainty
<!-- bite: d8a221cf-3df2-4cc7-b9ae-932566935dd7 -->

The real power shows up when outcomes are random. Then the recursion takes an **expected value** over what might happen.

**Example — a two-week stocking problem.** A shop sells a seasonal item for 2 weeks. Each week, demand is 1 unit with probability 0.5, or 2 units with probability 0.5. Each unit sold earns ₦10; each unit ordered costs ₦4; unsold stock at the end is worth nothing. At the start of each week, you can order up to 2 units, and unsold stock carries over.

**State:** stock on hand at the start of the week. **Decision:** how much to order. **Randomness:** demand. Write $f_t(s)$ for the best *expected* profit from week $t$ onwards, starting with $s$ units.

**Week 2 (the last week).** With $y$ units available after ordering, expected sales are: if $y = 0$, 0; if $y = 1$, 1 (both demand outcomes sell it); if $y = 2$, $0.5 \times 1 + 0.5 \times 2 = 1.5$. Expected revenue is $10 \times$ that.

1. From $s = 0$: order 0 → 0. Order 1 → $10 - 4 = 6$. Order 2 → $15 - 8 = 7$. **Best: order 2, $f_2(0) = 7$.**
2. From $s = 1$: order 0 → 10. Order 1 → $15 - 4 = 11$. **Best: order 1, $f_2(1) = 11$.**
3. From $s = 2$: order 0 → 15. **$f_2(2) = 15$.**

**Week 1, starting with 0 stock.** If you order $q$, you then have $y = q$; demand $D$ sells $\min(y, D)$ and leaves $y - \min(y, D)$ for week 2.

1. Order 1 ($y = 1$): always sell 1, leftover 0. Value $= 10 - 4 + f_2(0) = 6 + 7 = 13$.
2. Order 2 ($y = 2$): with probability 0.5 sell 1 and carry 1; with 0.5 sell 2 and carry 0. Expected value $= -8 + 0.5\,(10 + f_2(1)) + 0.5\,(20 + f_2(0)) = -8 + 0.5(21) + 0.5(27) = -8 + 24 = 16$.
3. Order 0: $0 + f_2(0) = 7$.

**Best: order 2 in week 1, expected profit ₦16.** And the policy for week 2 is a *rule*, not a number: order 2 if you have none left, order 1 if you have one. That's the point of a policy — you don't know in advance which state you'll be in.

This structure — states, decisions, random transitions, expected values — is a **Markov decision process**, and it's the mathematical foundation of reinforcement learning → [[mathematics/05-probability-statistics/06-stochastic-processes/01-markov-chains|Markov chains]].

## 5. When to use it, and when not
<!-- bite: 795a6667-a9e2-4036-a741-cb6e046d23e5 -->

**Use dynamic programming when:**

1. Decisions happen in a natural sequence (stages).
2. A small state captures everything the future depends on.
3. Rewards or constraints are nonlinear, so LP doesn't fit.
4. Outcomes are random and you need a policy, not just a plan.

**Don't, when the state is big.** With five products and stock levels 0–100 each, there are $101^5 \approx 10^{10}$ states. That's the **curse of dimensionality**, Bellman's own phrase. Approximate dynamic programming and reinforcement learning exist to deal with it — by learning an approximation to $f$ instead of tabulating it.

**Connections:**

1. Shortest path (note 06) is dynamic programming: Bellman–Ford is literally the Bellman equation applied repeatedly.
2. The knapsack problem (note 07) has a DP solution that's fast when the capacity is small.
3. LQR in control theory is dynamic programming with a quadratic cost, solved in closed form → [[control-theory/11-optimal-control-and-lqr|optimal control and LQR]].

## Worked example — the allocation recursion in Python
<!-- bite: ec595b78-7960-440f-9668-67724294c034 -->

**Runnable**, standard library only.

```python
# allocate.py — note 08's resource-allocation DP, backward recursion
returns = {"R1": [0, 4, 6, 7], "R2": [0, 3, 8, 9], "R3": [0, 5, 6, 7]}
regions = list(returns)
BUDGET = 3

f = {len(regions): {s: 0 for s in range(BUDGET + 1)}}   # nothing left to allocate: value 0
choice = {}
for stage in reversed(range(len(regions))):
    r = returns[regions[stage]]
    f[stage], choice[stage] = {}, {}
    for s in range(BUDGET + 1):
        best_k = max(range(s + 1), key=lambda k: r[k] + f[stage + 1][s - k])
        f[stage][s] = r[best_k] + f[stage + 1][s - best_k]
        choice[stage][s] = best_k
    print(regions[stage], "f =", f[stage])

s = BUDGET
for stage, name in enumerate(regions):
    k = choice[stage][s]
    print(f"give {name} {k} unit(s)")
    s -= k
print("total return:", f[0][BUDGET])
```

```bash
python3 allocate.py
```

Expected output:

```text
R3 f = {0: 0, 1: 5, 2: 6, 3: 7}
R2 f = {0: 0, 1: 5, 2: 8, 3: 13}
R1 f = {0: 0, 1: 5, 2: 9, 3: 13}
give R1 0 unit(s)
give R2 2 unit(s)
give R3 1 unit(s)
total return: 13
```

The `R2` line matches the stage-2 table. The `R1` line fills in all four budgets, though only $s = 3$ is used — the code computes the whole policy, which is what you'd want if the budget might change.

## Common pitfalls and traps
<!-- bite: a49717f1-1138-40dd-830d-404a0ea8f5a3 -->

1. **A state that's too small.** If the future depends on something the state doesn't include, the recursion gives wrong answers without any error. Ask: "if two different histories arrive at the same state, should they make the same future decisions?"
2. **Off-by-one in the transition.** Does stock carried over include this week's order? Write the timeline of a single stage out in words before writing the formula.
3. **Forgetting the boundary.** $f_{n+1} = 0$ (or a salvage value) has to be set. A missing boundary is the commonest bug in tabulated code.
4. **Greedy instinct.** Giving each unit to wherever it earns most right now fails whenever returns interact — as R1 vs R2 showed.
5. **Plan instead of policy.** Under uncertainty, reporting "order 2 then order 2" is wrong: the second order depends on what happened.

## Check your understanding
<!-- bite: bcc0de69-ccbb-4b01-b1e3-20a9c3eb4cbd -->

1. In the allocation problem, what would change if region R3 could only accept at most 1 unit?
2. Why is "budget remaining" a sufficient state for allocation, but "week number" alone is not sufficient for the stocking problem?
3. In week 1 of the stocking problem, ordering 2 gives expected profit 16 but you might end up with stock that has to be carried. Why does carrying stock not show up as a cost in this model? What would change if it did?
4. How many states would the stocking problem have if there were 3 products, each with stock 0–10?

<details>
<summary>After your attempt — answers</summary>

1. $f_3(s)$ becomes $R_3(\min(s, 1))$: $0, 5, 5, 5$. Stage 2 with $s = 3$: options $0 + 5$, $3 + 5$, $8 + 5 = 13$, $9 + 0$ — still 13 at $k = 2$. The plan is unchanged because the optimum only gave R3 one unit anyway.
2. In the allocation problem, the only way past decisions affect the future is through how much budget is left. In the stocking problem, past demand affects the future through how much stock is on hand, so stock must be in the state; the week number tells you how many weeks remain but not what you hold.
3. The model has no holding cost, so the only cost of over-ordering is the chance that stock ends unsold at the end of week 2. With a holding cost $h$ per unit carried, each "carry 1" outcome would subtract $h$, making ordering 2 in week 1 less attractive; above some $h$, ordering 1 would win.
4. $11^3 = 1{,}331$ states per week. Manageable — but with 10 products it would be $11^{10} \approx 2.6 \times 10^{10}$.

</details>

## Practice — independent task
<!-- bite: 1dd96333-6d07-440f-886e-0f0561eda64c -->

1. **Reconstruct:** with the note closed, rebuild the stage-2 and stage-1 tables for the allocation problem with a budget of 4 units, using these returns for 4 units: R1 = 7, R2 = 9, R3 = 7 (no gain beyond 3). Predict whether R1 now gets anything.
2. **Apply:** write `stock.py` to solve the two-week stocking problem by recursion, then extend it to 4 weeks and to demand of 0, 1 or 2 with probabilities 0.2, 0.5, 0.3. Print the policy as a table: for each week and starting stock, the best order.
3. **Check:** for the 2-week case, confirm your code gives $f_1(0) = 16$ and the week-2 rule "order 2 if empty, 1 if holding 1".

**Done when:** your code reproduces the hand answers for 2 weeks, prints a full policy table for 4 weeks, and you can explain one row of it in words.

## Before moving on
<!-- bite: bb437bb9-646d-47ff-9e29-3e26e2a1105f -->

You're ready when you can name the stages, state, decision and transition for a new problem, write its Bellman equation in words, and fill in a small table backwards.

**Recap:**

1. Stage, state, decision, transition, value function — name all five before writing any maths.
2. The principle of optimality makes backward recursion valid: the rest of an optimal plan is optimal from wherever you are.
3. Under uncertainty, the recursion takes expectations and returns a policy.
4. The work grows with the number of states; when the state has many dimensions, it explodes.

**Next:** [[operations-research/09-nonlinear-optimisation|Nonlinear Optimisation]] — when the objective curves, and what replaces corners and shadow prices.

## Related
<!-- bite: 1a2333ce-34c6-4c47-83ec-c412401a4f81 -->

- [[dsa/03-algorithms/07-dynamic-programming/index|DSA: dynamic programming]] — the coding pattern, with practice problems
- [[dsa/04-patterns/15-dynamic-programming|DSA pattern: dynamic programming]] — the interview framing
- [[operations-research/06-network-models|Network Models]] — shortest path is a dynamic program
- [[control-theory/11-optimal-control-and-lqr|Optimal control and LQR]] — dynamic programming in continuous state
- [[operations-research/index|Operations research map]]

## About this lesson
<!-- bite: e2ea9bbe-0e21-44c6-bd14-e79098483838 -->

**Level:** Intermediate. **Covers:** Decisions made in stages, where each choice changes what's possible next. Bellman's principle turns an explosion of combinations into a chain of small tables. This is the operations research origin of the DSA pattern, with the stages, states and uncertainty made explicit.
