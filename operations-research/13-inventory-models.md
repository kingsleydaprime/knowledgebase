---
id: c0cad2a8-0f7b-4a8d-b46d-be9cf98261ac
---

# Inventory Models

**Source:** `[reference]` — see [[operations-research/index|the domain note]]. The code below was run and its output checked.

## Before you start
<!-- bite: 64ee4f7a-4d2b-4696-bd85-178599b3427b -->

You need to be able to differentiate a simple function and set the derivative to zero → [[mathematics/06-calculus/02-calculus-1/07-derivative-rules/01-rules|derivative rules]], and know the normal distribution and what a percentile is → [[mathematics/05-probability-statistics/04-random-variables-and-distributions|distributions]].

After this lesson you will be able to:

1. Derive and use the economic order quantity, and explain why getting it slightly wrong barely matters.
2. Set a reorder point with safety stock for a target service level.
3. Solve a newsvendor problem with the critical ratio, and explain the answer in terms of the costs of too much and too little.

**Study route:** sections 1–3 (EOQ) with a pencil; stop and derive the formula yourself. Then sections 4–5.

## The kid version
<!-- bite: cab120e3-0381-4a9a-832d-e22c72956380 -->

You keep snacks in your cupboard. Every trip to the shop is a hassle, so you'd like to buy a lot at once. But a huge pile of snacks takes up space and some go stale. Buy too little and you're always at the shop; buy too much and the cupboard is full of stale crisps. **Inventory models find the amount to buy each time that balances the hassle of shopping against the cost of keeping stuff.** And because you never know exactly how many snacks you'll eat this week, they also tell you how many spare to keep so you don't run out.

**Where the analogy stops working.** For you, running out of crisps is a small annoyance. For a hospital running out of blood, or a factory running out of a part that stops a production line, the cost of running out can be huge — and the models make you put a number on it, which is often the hardest and most important step.

## 1. Why this exists
<!-- bite: b47a5400-7919-4dc1-a19b-6293773a3326 -->

A shop sells 1,200 units of a product a year. Each order costs ₦50 to place (admin, delivery), whatever its size. Holding one unit in stock for a year costs ₦2 (storage, insurance, the money tied up).

1. **Order every week** (about 23 units each time): 52 orders cost ₦2,600 a year; average stock is low.
2. **Order once a year** (1,200 units): one order costs ₦50; but average stock is 600 units, costing ₦1,200 a year to hold.

Somewhere between is a minimum. Inventory is one of the largest assets on most companies' balance sheets, so these trade-offs move real money — and the same logic covers cash balances, cache sizes and batch sizes in software.

## Terms used in inventory models
<!-- bite: 983d05fa-d090-4720-b51d-83ce8adf31dc -->

1. **Demand rate**: This is how many units are used or sold per unit time, written $D$ (here, per year).
2. **Ordering cost**: This is also known as **setup cost**. Written $S$, it's the fixed cost of placing one order, regardless of its size.
3. **Holding cost**: Written $H$, it's the cost of keeping one unit in stock for one unit of time. It's often 15–30% of the item's value per year, mostly the cost of the money tied up.
4. **Order quantity**: Written $Q$, it's how many units are ordered each time.
5. **Lead time**: Written $L$, it's the delay between placing an order and receiving it.
6. **Reorder point**: This is the stock level at which you place the next order, so it arrives before you run out.
7. **Safety stock**: This is extra stock held to cover demand during the lead time being higher than average.
8. **Service level**: This is also known as **cycle service level**. This is the probability of *not* running out during a replenishment cycle — 95% means you run out in about one cycle in twenty.
9. **Stockout**: This is running out of stock when there's demand for it.
10. **Critical ratio**: This is the number that decides the newsvendor order: the cost of having too little divided by the total cost of being wrong in either direction.

## 2. The economic order quantity
<!-- bite: cfff1708-7591-4a1c-9f02-39f2e4e6c557 -->

Assume demand is steady and known, and orders arrive instantly. Stock then follows a sawtooth: it jumps to $Q$ when an order arrives, falls steadily to 0, and jumps again.

```
 stock
   Q ┤╲        ╲        ╲
     │  ╲        ╲        ╲
 Q/2 ┤ ─ ─╲─ ─ ─ ─ ╲─ ─ ─ ─ ╲─ ─   average stock = Q/2
     │      ╲        ╲        ╲
   0 ┼───────●────────●────────●──── time
          order    order    order
```

The annual cost has two parts:

1. **Ordering:** you place $D/Q$ orders a year, each costing $S$: $\dfrac{DS}{Q}$. This falls as $Q$ rises.
2. **Holding:** average stock is $Q/2$, each costing $H$ a year: $\dfrac{HQ}{2}$. This rises with $Q$.

$$\text{TC}(Q) = \frac{DS}{Q} + \frac{HQ}{2}$$

**Find the minimum.** Differentiate and set to zero: $-\dfrac{DS}{Q^2} + \dfrac{H}{2} = 0$. So:

**The economic order quantity is the square root of twice the demand times the ordering cost, divided by the holding cost.**

$$Q^* = \sqrt{\frac{2DS}{H}}$$

At $Q^*$, the two cost parts are exactly equal — a useful check.

**The shop's numbers:** $Q^* = \sqrt{2 \times 1200 \times 50 / 2} = \sqrt{60{,}000} \approx 245$ units. That's about 4.9 orders a year, every 10–11 weeks. Total cost: $\sqrt{2DSH} = \sqrt{240{,}000} \approx$ ₦490 a year. (Check: ordering cost $1200 \times 50 / 245 \approx 245$; holding cost $2 \times 245/2 = 245$. Equal. ✓)

**Pause and predict:** if you ordered 300 instead of 245 — 22% more — how much would total cost rise?

## 3. Why EOQ is so forgiving
<!-- bite: 7aba93e0-f1ad-4e09-b46f-4eab23d9f76e -->

| Order quantity | 150 | 200 | 245 | 300 | 400 |
|---|---|---|---|---|---|
| Annual cost (₦) | 550 | 500 | 490 | 500 | 550 |
| Above optimum | +12% | +2% | — | +2% | +12% |

**Ordering 22% too much raises cost by only 2%.** The cost curve is very flat near the bottom, because of the square root.

That has big practical consequences:

1. **You can round $Q$ to a convenient pack size, pallet or truckload** at almost no cost.
2. **Rough estimates of $S$ and $H$ are good enough.** If you estimate the ordering cost as double its true value, $Q^*$ rises by a factor of $\sqrt{2} \approx 1.41$, and the cost penalty is only about 6%.
3. **The square root halves the relative error**: a 20% error in $D$ gives about a 10% error in $Q^*$.

So EOQ is used not because its assumptions are true (they rarely are) but because its answer is robust to their being wrong.

## 4. Random demand: reorder points and safety stock
<!-- bite: ceca030e-273d-44d2-acef-92891f169683 -->

Now suppose orders take $L = 4$ days to arrive, and daily demand is random with mean 20 and standard deviation 5.

**Without uncertainty**, reorder when stock falls to the demand during the lead time: $4 \times 20 = 80$ units.

**With uncertainty**, demand during those 4 days might be more than 80. If daily demands are independent, the lead-time demand has:

1. Mean $= L \times 20 = 80$.
2. Standard deviation $= \sqrt{L} \times 5 = 2 \times 5 = 10$. (Variances add over independent days, so the standard deviation grows with the *square root* of the number of days.)

To run out in at most 5% of cycles (a 95% service level), set the reorder point at the 95th percentile of lead-time demand. For a normal distribution that's the mean plus $z = 1.645$ standard deviations:

**The reorder point is the average lead-time demand plus a safety stock of $z$ standard deviations of lead-time demand.**

$$\text{ROP} = \mu_L + z\,\sigma_L = 80 + 1.645 \times 10 \approx 96.5$$

**Reorder when stock falls to about 97 units.** The extra 17 is the safety stock.

**What the safety stock costs.** Higher service levels get expensive fast:

| Service level | 90% | 95% | 99% | 99.9% |
|---|---|---|---|---|
| $z$ | 1.28 | 1.645 | 2.33 | 3.09 |
| Safety stock (units) | 13 | 17 | 23 | 31 |

Going from 95% to 99.9% almost doubles the safety stock. Whether it's worth it depends on what a stockout costs — which is the business question the formula forces you to answer.

**Two levers reduce safety stock:** reduce demand variability (better forecasts) or reduce lead time (faster suppliers). Halving the lead time cuts $\sigma_L$ by a factor of $\sqrt{2}$, not 2.

## 5. The newsvendor: one chance to order
<!-- bite: d3715953-43c9-49ae-a2da-dfca6e1826a0 -->

Some products can't be sold later: newspapers, fresh bread, fashion items, event tickets, flu vaccines. You order once, before demand is known. Order too many and you're stuck with leftovers; too few and you lose sales.

**A bakery's numbers.** A cake sells for ₦10, costs ₦4 to bake, and unsold cakes are sold off at the end of the day for ₦1. Daily demand is uniformly random between 50 and 150.

The two costs of being wrong:

1. **Underage cost** $C_u$: the profit lost on each cake you *could* have sold but didn't bake. $C_u = 10 - 4 = 6$.
2. **Overage cost** $C_o$: the loss on each cake baked but not sold. $C_o = 4 - 1 = 3$.

**The argument, in words.** Consider baking one more cake than you planned. It sells if demand exceeds your quantity $Q$, with probability $P(D > Q)$, gaining $C_u$. It goes unsold otherwise, losing $C_o$. Keep adding cakes while the expected gain exceeds the expected loss. You stop exactly where they balance:

$$C_u\,P(D > Q) = C_o\,P(D \le Q)$$

**The newsvendor rule states that the best order quantity is the one where the probability of demand being at or below it equals the critical ratio.**

$$P(D \le Q^*) = \frac{C_u}{C_u + C_o}$$

**Bakery:** critical ratio $= 6 / (6 + 3) = 0.667$. For demand uniform on [50, 150], the 66.7th percentile is $50 + 0.667 \times 100 \approx 117$. **Bake 117 cakes** — well above the average demand of 100.

**Why above average?** Running short costs ₦6 a cake; over-baking costs ₦3. Shortage is twice as expensive, so you lean towards having too many. If unsold cakes had to be thrown away *and* cost something to dispose of, $C_o$ would rise and the order would fall.

**If demand is normal** with mean $\mu$ and standard deviation $\sigma$: $Q^* = \mu + z\sigma$, where $z$ is the critical ratio's percentile of the standard normal. For a ratio of 0.667, $z \approx 0.43$.

This one idea — balance the cost of too little against the cost of too much, weighted by probability — also sets airline overbooking, hotel room allocation, cloud capacity reservations and how many servers to pre-provision.

## Worked example — EOQ and the newsvendor in Python
<!-- bite: 9828591d-2493-4470-b2c4-22160a6a8442 -->

**Runnable**, standard library only.

```python
# inventory.py — note 13: EOQ and the newsvendor
import math
D, S, H = 1200, 50, 2                  # units/year, cost per order, holding cost per unit-year
Q = math.sqrt(2 * D * S / H)
cost = lambda q: D * S / q + H * q / 2
print(f"EOQ = {Q:.1f} units, annual cost {cost(Q):.1f}")
for q in (150, 200, 300, 400):
    print(f"  order {q}: cost {cost(q):.1f} ({100 * (cost(q) / cost(Q) - 1):+.1f}%)")

price, unit_cost, salvage = 10, 4, 1
cu, co = price - unit_cost, unit_cost - salvage
ratio = cu / (cu + co)
lo, hi = 50, 150                        # demand uniform between 50 and 150
print(f"critical ratio {ratio:.3f} -> order {lo + ratio * (hi - lo):.1f}")
```

```bash
python3 inventory.py
```

Expected output:

```
EOQ = 244.9 units, annual cost 489.9
  order 150: cost 550.0 (+12.3%)
  order 200: cost 500.0 (+2.1%)
  order 300: cost 500.0 (+2.1%)
  order 400: cost 550.0 (+12.3%)
critical ratio 0.667 -> order 116.7
```

## Common pitfalls and traps
<!-- bite: f0e19130-b99d-4b3c-ab1c-7224b117d798 -->

1. **Units mismatch.** $D$ per year with $H$ per month gives a $Q^*$ that's off by $\sqrt{12}$. Put everything on the same time base.
2. **Leaving out the cost of money.** Holding cost isn't just warehouse rent; the capital tied up in stock is usually the biggest part.
3. **Adding standard deviations across days.** Variances add, standard deviations don't. Four days of $\sigma = 5$ gives $\sigma_L = 10$, not 20.
4. **Confusing service level definitions.** "95% cycle service level" (run out in 5% of cycles) is not "95% fill rate" (meet 95% of demand from stock). The fill rate is usually much higher for the same safety stock.
5. **Ordering the mean in a newsvendor problem.** The mean is only right when $C_u = C_o$. Otherwise the costs push you up or down.
6. **Ignoring the bullwhip effect.** Small swings in customer demand become larger swings in orders up a supply chain, as each stage adds safety stock and batches orders. Sharing demand data across the chain is the standard cure.

## Check your understanding
<!-- bite: b6c14690-1140-43fa-994e-ec0bb493a1d7 -->

1. If demand doubles, by what factor does the EOQ change? The total cost?
2. Why is the EOQ cost curve so flat near the minimum?
3. A supplier cuts lead time from 9 days to 4. Daily demand has $\sigma = 6$. By how much does the safety stock for a 95% service level fall?
4. In the bakery, unsold cakes now have to be thrown away (salvage 0). What's the new order quantity?

<details>
<summary>After your attempt — answers</summary>

1. Both by $\sqrt{2} \approx 1.41$. Demand doubled, but EOQ and its cost each rise by only 41%: economies of scale in ordering.
2. Near the minimum, an increase in one cost part is almost exactly offset by a decrease in the other: their slopes are equal and opposite at $Q^*$. Mathematically, the first derivative is zero there, so the cost changes only with the square of the deviation.
3. $\sigma_L$ falls from $\sqrt{9} \times 6 = 18$ to $\sqrt{4} \times 6 = 12$. Safety stock falls from $1.645 \times 18 \approx 29.6$ to $1.645 \times 12 \approx 19.7$ — about 10 units, a third.
4. $C_o$ becomes $4 - 0 = 4$. Critical ratio $= 6/10 = 0.6$. Order $50 + 0.6 \times 100 = 110$.

</details>

## Practice — independent task
<!-- bite: afcf0c5c-e13b-41d4-97cf-91b62277e1c7 -->

1. **Derive:** with the note closed, derive the EOQ formula from the total cost, and show the two cost parts are equal at the optimum.
2. **Apply:** a pharmacy sells 5,000 boxes of a medicine a year. Each order costs ₦2,000; each box costs ₦800, and holding cost is 25% of value per year. Lead time is 10 days; daily demand has standard deviation 4 boxes. Find the EOQ, the reorder point for a 98% service level (assume 365 days a year), and the annual ordering and holding costs.
3. **Simulate:** write a short script that simulates the bakery for 10,000 days with uniform random demand, for every bake quantity from 80 to 150, and plots (or prints) average profit. Confirm the peak is near 117.

**Done when:** your derivation is on paper, your pharmacy numbers are internally consistent (ordering cost ≈ cycle-stock holding cost), and the simulation's best quantity is within a couple of cakes of the formula.

## Before moving on
<!-- bite: 51d60ceb-cf53-4ef8-9e0d-145ee707dd39 -->

You're ready when you can derive EOQ, explain its flatness, compute a reorder point with safety stock, and explain the newsvendor answer in one sentence about the two costs of being wrong.

**Recap:**

1. EOQ $= \sqrt{2DS/H}$ balances ordering and holding costs, and is robust to errors in its inputs.
2. Safety stock $= z\,\sigma_L$, with $\sigma_L = \sigma_{\text{daily}}\sqrt{L}$. High service levels get expensive fast.
3. The newsvendor orders where $P(D \le Q) = C_u / (C_u + C_o)$ — above the mean when shortages cost more than leftovers.

**Next:** [[operations-research/14-simulation|Simulation]] — when the system is too messy for any formula, build it in code and run it many times.

## Related
<!-- bite: c2fbecf6-fd91-4995-8cc8-4ac0e9bd33cf -->

- [[operations-research/08-dynamic-programming|Dynamic Programming]] — multi-period stocking under uncertainty
- [[operations-research/12-queueing-theory|Queueing Theory]] — the other classic stochastic model
- [[mathematics/05-probability-statistics/04-random-variables-and-distributions|Distributions]] — the normal and uniform used here
- [[operations-research/index|Operations research map]]

## About this lesson
<!-- bite: 98fbe8b6-3bbb-42ca-9f94-86007d282b7f -->

**Level:** Intermediate. **Covers:** How much stock to order and when: the economic order quantity and why it's so forgiving, reorder points and safety stock when demand is random, and the newsvendor model for things that can't be sold later. Small formulas with a lot of business behind them.
