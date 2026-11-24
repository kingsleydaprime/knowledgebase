---
id: 0840aca6-111f-4627-a6d0-32a2cd433436
---

# Model Building 2: The Production Control Case

The lecturer's production control problem, a packaging line feeding a warehouse, shows how to list a system's assumptions and trace how its parts affect each other.

## Before you start
<!-- bite: adc482c5-e8af-481d-ad3b-e4f5b78666a3 -->

You should have read [[systems-simulation/25-model-building-1|25 — Model Building 1]].

After this lesson you will be able to:

1. follow the guidelines for collecting data well;
2. list a system's inputs, mark each deterministic or stochastic, and state its logic;
3. explain how production, inventory and demand affect each other, and why variability matters.

## What the production control case is
<!-- bite: bd7ee586-4c70-4286-926b-46ff22586489 -->

This is model-building steps 1 and 2 on a real case. It is the case the lecturer used, and it is very close in style to the exam's manufacturing question, so learn its shape: the assumptions table, the logic, and the performance questions. First, a short set of rules for collecting the data.

## Collecting data well
<!-- bite: d6700d93-5f06-4b0d-9d44-af0997e08eee -->

1. **Plan ahead,** and practise with a trial observing session.
2. **Watch for unusual circumstances** and check accuracy. Analyse the data as you collect it, so mistakes are caught early.
3. **Combine only homogeneous data:** merge samples only if they come from the same conditions. Monday's rush and Sunday's quiet don't belong in one sample.
4. **Check for relationships** and correlation between variables.
5. **Collect input data, not performance data.** You need the raw arrival and service times, not the waiting times they produce, because waiting time is what the model has to predict.

## The case
<!-- bite: 665d7d7c-164f-4cc3-96e0-6fb27672ed4c -->

A packaging and warehousing process. Product is filled and sealed, units go into boxes with stickers, and boxes go to the warehouse to meet customer demand.

| Part of the system | Assumption | Kind |
| --- | --- | --- |
| Raw materials | Always enough; the process never starves | Deterministic |
| Batch size | 5 units per batch | Deterministic |
| Processing time | Uniform between 10 and 20 minutes per unit | Stochastic |
| Time between failures | Exponential, mean 200 minutes | Stochastic |
| Repair time | Normal, mean 90, standard deviation 45 minutes | Stochastic |
| Warehouse capacity | Target level R = 500 units | Deterministic |
| Restart level | Reorder point r = 150 units | Deterministic |
| Customer inter-arrival time | Uniform between 3 and 7 hours | Stochastic |
| Demand size | Uniform between 50 and 100 units | Stochastic |

## How the logic works
<!-- bite: 1f4eaddc-50bb-4331-b178-983533826c36 -->

1. Production runs until the warehouse holds 500 units. Then the process is **blocked** and sits idle.
2. It restarts with a new batch once stock falls to 150.
3. Idle time isn't wasted: the machine can be given to another product outside the model.
4. When a customer arrives, stock is checked at once. If there is enough, the demand is met in full. If not, depending on the **loss policy**, either the available part is sold and the rest lost, or the whole order is lost.

![A flowchart of the production control logic: production adds batches to the warehouse until stock reaches 500, when production is blocked until stock falls to 150; a customer arrival checks whether stock covers the demand and is either served in full or partly served or lost](images/ss-production-control.svg)

## The performance questions
<!-- bite: 22abbab9-b325-498f-89eb-06fce89daa1c -->

1. Can we improve the **customer service level**, the percentage of customers whose demand is fully met?
2. Is the machine under- or over-used? (**machine utilisation**)
3. Is maintenance adequate? (**downtime probabilities**)
4. What is the trade-off between **inventory level** and customer service level?

## How the parts affect each other
<!-- bite: ba7b4da9-912e-4dc3-b935-9678feb329d8 -->

Production rate fills the warehouse; demand drains it.

1. If production is slow or the machine breaks down, stock falls and customers are lost, so service level drops.
2. If production is fast and demand is slow, stock reaches 500 and the process blocks, so utilisation drops.
3. **Variability makes it worse.** A breakdown at the same time as a big order causes a stock-out even when average production is enough.

That last point is why you simulate instead of using averages: the trouble comes from bad timing, and averages can't see timing.

## An assumption to defend
<!-- bite: b6440442-c9de-41ec-a3f9-75430addf937 -->

A normal repair time with mean 90 and standard deviation 45 can, in theory, produce negative values, since 0 is only two standard deviations below the mean. In a real model you would **truncate it at zero**, or use a distribution that can't go negative, such as lognormal. It is a good example of an assumption you should state and defend in an exam answer.

## Common pitfalls
<!-- bite: d430a619-e178-4621-96b5-f1e54ec4f717 -->

1. **Recording waiting times as inputs.** Collect arrival and service times; waits are outputs.
2. **Merging data from different conditions.** Check the samples are homogeneous first.
3. **Using averages only.** The case's problems come from variability, not from the averages.

Step 2 said "make assumptions about the distributions". Next part asks how you choose them properly from data: input analysis.

## Check your understanding
<!-- bite: 944ab6d1-1916-4640-9ef6-e93aec1d7f4a -->

Try each one before you open the answer.

1. <!-- q: mcq id="0c4daa71" -->
   A team modelling a bank collects how long each customer waited in line. Why is this the wrong data to feed the model?

   - [ ] Waiting times are always wrong
   - [x] Waiting time is a performance measure the model must predict; the inputs are arrival and service times
   - [ ] Banks don't record waiting times
   - [ ] Waiting times are deterministic

   <details><summary>Answer</summary>

   Waiting time is an output. Feed in the arrival and service times that produce the waits, then use the real waits to validate the model.

   </details>

2. <!-- q: mcq id="c147249f" -->
   In the production control case, which of these inputs are stochastic? Choose all that apply.

   - [x] Time between machine failures
   - [ ] Batch size of 5 units
   - [x] Customer demand size
   - [ ] Warehouse target level of 500

   <details><summary>Answer</summary>

   Time between failures (exponential) and demand size (uniform 50 to 100) are random. Batch size and target level are fixed.

   </details>

3. <!-- q: exact id="4b929bfc" answer="150" -->
   The warehouse fills to 500 units and production blocks. At what stock level does production restart?

   <details><summary>Answer</summary>

   150 units, the reorder point r.

   </details>

4. <!-- q: open id="18a189c4" -->
   The average production rate is higher than the average demand, yet the model still shows stock-outs. Explain how.

   <details><summary>Answer</summary>

   Variability. A random breakdown can stop production for hours just as a large random order arrives, emptying the warehouse even though production keeps up on average. Averages hide this bad timing, which is why the system is simulated.

   </details>

5. <!-- q: open id="9b05fcb3" -->
   Repair time is assumed normal with mean 90 and standard deviation 45 minutes. What problem does this assumption have, and how would you handle it?

   <details><summary>Answer</summary>

   A normal distribution can produce negative values, and a negative repair time makes no sense. 0 is only two standard deviations below the mean, so it would happen about 2% of the time. Truncate the distribution at zero, or use one that is always positive, such as lognormal, and state the choice.

   </details>

## Before moving on
<!-- bite: 03a35aac-0568-48c7-bbd6-76f0ad782e43 -->

You can collect data properly, write a system's assumptions table and trace how its parts interact. **Next:** [[systems-simulation/27-input-analysis-1|27 — Input Analysis 1]].

## Related
<!-- bite: b436a070-c269-449d-8242-6b421d02a5a9 -->

- [[systems-simulation/index|Systems simulation map]]
- [[operations-research/13-inventory-models|Inventory Models]]: the reorder-point idea from the operations research side.

## About this lesson
<!-- bite: d430735c-4907-4c61-9411-925bde034a5c -->

**Level:** Beginner to intermediate. **Covers:** guidelines for collecting data, the production control case, its logic and performance questions, how its parts interact, and the negative repair time assumption.

**Where it sits:** lesson 26 of 38, part 2 of 2 on model building.

**Source:** the author's own SSG 517 study notes, sections 5 and 9 (Q1). The flowchart comes from `scripts/diagrams/systems_simulation.py`.
