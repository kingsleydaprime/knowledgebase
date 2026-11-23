---
id: e5912c11-a485-41a0-b7c3-cd75781a643c
---

# Risk and Uncertainty 3: Decisions Under Risk and Ignorance

Decision rules are ways of choosing a strategy from a payoff table, with or without knowing the probabilities.

## Before you start
<!-- bite: adfabbf0-3cd7-482b-b2d6-15565795c09f -->

You should know expected value and standard deviation from [[engineering-economics/23-risk-and-uncertainty-2|Risk and Uncertainty 2]].

After this lesson you will be able to:

1. read a payoff table, and choose a strategy under risk with expected value and standard deviation;
2. apply the Laplace, Wald (maximin), maximax, Savage (minimax regret) and Hurwicz rules under complete ignorance;
3. name the four ways to manage risk.

## What a payoff table is
<!-- bite: f6c8c483-6ab5-4cce-94e6-f74c97ad70dc -->

A **payoff table** lists your strategies down the side and the possible states of the world across the top. Each cell is what you'd get if you chose that strategy and that state happened.

The whole lesson uses one example. A firm chooses between three pricing strategies. The payoffs are rates of return (%) in three states of the economy.

| Strategy | Expansion | Stability | Contraction |
| --- | --- | --- | --- |
| Raise price | 25 | 15 | −10 |
| No change | 15 | 20 | −5 |
| Lower price | 15 | 0 | 5 |

## Deciding under risk
<!-- bite: 6bf21602-2a3d-406a-ae69-b553975f78fc -->

Under risk the firm knows the probabilities: 35% expansion, 50% stability, 15% contraction. So it works out the expected value and standard deviation of each strategy (lesson 23).

| Strategy | Mean | Std dev |
| --- | --- | --- |
| Raise price | 14.75 | 11.34 |
| No change | 14.5 | 8.5 |
| Lower price | 6.0 | 6.8 |

For example, Raise price: 0.35 × 25 + 0.5 × 15 + 0.15 × (−10) = 8.75 + 7.5 − 1.5 = 14.75.

## Deciding under risk: reading the result
<!-- bite: fcc33509-842f-44a0-aee8-a597213712d0 -->

So which strategy wins under risk? Raise price has the highest expected return, but it also has the highest spread, and expected value ignores the manager's attitude to risk. A risk-averse manager might take No change: almost the same mean, much less spread.

> **Correction:** your handout shows 9.5 and 9.86 for "No change". Those two numbers are wrong. The mean is 14.5 and the standard deviation is about 8.5. The other two rows are right.

## Complete ignorance 1: Laplace
<!-- bite: 61aaae1c-5b27-440c-a063-b853e2e93495 -->

Now suppose the firm has no idea of the probabilities. Under complete ignorance there are four rules, all on the same payoff table.

**Laplace:** assume all states are equally likely and take the average.

- Raise price = (25 + 15 − 10)/3 = 10.
- No change = (15 + 20 − 5)/3 = 10.
- Lower price = (15 + 0 + 5)/3 = 6.67.

Raise and No change tie, so choose **No change** because its spread is smaller (σ 10.80 against 14.72, taking the three states as equally likely).

> **Correction:** the handout simply says "No change is chosen". It is a tie on the average, and No change wins on lower spread.

## Complete ignorance 2: maximin and maximax
<!-- bite: b5afac57-f0a7-40f9-b63d-595635d0a20f -->

**Wald (maximin):** for each strategy take the worst payoff, then pick the best of those. Worst payoffs are −10, −5 and 0, so choose **Lower price**. It is very pessimistic and risk averse.

**Maximax:** for each strategy take the best payoff, then pick the best of those. Best payoffs are 25, 20 and 15, so choose **Raise price**. It is very optimistic, for risk lovers.

Maximin asks "what's the worst that can happen?" and maximax asks "what's the best?". They're the two extremes, and they pick opposite strategies here.

## Complete ignorance 3: Savage (minimax regret)
<!-- bite: 1f6b86ab-a1a9-4605-b010-cfd0df38993d -->

**Regret** is the gap between a payoff and the best payoff in that state: how much you'd kick yourself for not choosing the best strategy. Build a regret table, take each strategy's largest regret, and choose the smallest of those.

The best payoffs are 25 (expansion), 20 (stability) and 5 (contraction).

| Strategy | Expansion | Stability | Contraction | Max regret |
| --- | --- | --- | --- | --- |
| Raise price | 0 | 5 | 15 | 15 |
| No change | 10 | 0 | 10 | **10** |
| Lower price | 10 | 20 | 0 | 20 |

Choose **No change**. Savage is neither too optimistic nor too pessimistic, so it suits long-term capital projects where you want a satisfactory return with moderate risk.

> **Correction:** the handout gives Lower price a contraction regret of 10. It is 0, because the best payoff in contraction is 5 and Lower price earns 5. Its maximum regret is still 20, so No change is still the Savage choice.

## Hurwicz: between the extremes
<!-- bite: 9f683ef7-e2e5-4618-b8e4-03df1b13a8ab -->

**Hurwicz** (general knowledge, the handout only names it) is a blend of the two extremes. Pick an optimism index α between 0 and 1 and score each strategy as α × best + (1 − α) × worst.

α = 1 is maximax and α = 0 is maximin. The handout notes that maximax and maximin are the two extreme cases of Hurwicz.

With α = 0.6: Raise price = 0.6 × 25 + 0.4 × (−10) = 11, No change = 0.6 × 20 + 0.4 × (−5) = 10, Lower price = 0.6 × 15 + 0.4 × 0 = 9. So Raise price, for a fairly optimistic manager. (This α = 0.6 working was added for this lesson.)

No rule suits every situation. Pick the one that fits the circumstances and the organisation's attitude to risk.

## Four ways to manage risk
<!-- bite: f1a96b97-cc6b-4063-b1cb-76d81e3b88bb -->

1. **Insurance:** transfer the risk through a policy.
2. **Hedging:** offset an expected loss with an expected profit from another contract.
3. **Diversification:** spread money over several investments so each carries less risk.
4. **Adjusting for risk:** make a provision (such as a contingency allowance or a higher MARR) to offset the expected loss. This connects back to the MARR in lesson 11 and to contingency in lesson 21.

All these rules need probabilities or a full payoff table. There's a simpler test that needs neither, and it's the most used of all: sensitivity analysis.

## Check your understanding
<!-- bite: 10e24fda-113e-4601-bc36-789c22465837 -->

Try each one before you open the answer. Every question uses this payoff table (returns in %):

| Plant size | Boom | Normal | Slump |
| --- | --- | --- | --- |
| Big | 40 | 20 | −15 |
| Medium | 25 | 18 | 0 |
| Small | 12 | 10 | 6 |

1. <!-- q: mcq id="9f1ab859" -->
   Plant sizes and their returns (%) are: Big 40 boom, 20 normal, −15 slump; Medium 25, 18, 0; Small 12, 10, 6. Which plant does the Wald (maximin) rule choose?

   - [ ] Big
   - [ ] Medium
   - [x] Small

   <details><summary>Answer</summary>

   Small. The worst payoffs are −15, 0 and 6, and the best of those is 6.

   </details>

2. <!-- q: mcq id="b14cb3ac" -->
   Plant sizes and their returns (%) are: Big 40 boom, 20 normal, −15 slump; Medium 25, 18, 0; Small 12, 10, 6. Which plant does the maximax rule choose?

   - [x] Big
   - [ ] Medium
   - [ ] Small

   <details><summary>Answer</summary>

   Big. The best payoffs are 40, 25 and 12, and the best of those is 40.

   </details>

3. <!-- q: gap id="e94ccd4b" answers="21;15;28;Medium|medium" -->
   Plant sizes and their returns (%) are: Big 40 boom, 20 normal, −15 slump; Medium 25, 18, 0; Small 12, 10, 6. Fill in the gaps for the Savage rule. The maximum regret of Big is ___, of Medium is ___, of Small is ___, so the rule chooses ___.

   <details><summary>Answer</summary>

   The best payoffs per state are 40, 20 and 6.
   - Big: regrets 0, 0, 21, max 21.
   - Medium: regrets 15, 2, 6, max 15.
   - Small: regrets 28, 10, 0, max 28.
   The smallest maximum regret is 15, so Medium.

   </details>

4. <!-- q: exact id="9751df9d" answer="19" -->
   Plant sizes and their returns (%) are: Big 40 boom, 20 normal, −15 slump; Medium 25, 18, 0; Small 12, 10, 6. The probabilities are 30% boom, 50% normal and 20% slump. What is the expected return of the Big plant, in percent?

   <details><summary>Answer</summary>

   0.3 × 40 + 0.5 × 20 + 0.2 × (−15) = 12 + 10 − 3 = 19%. (Medium gives 16.5% and Small 9.8%.)

   </details>

5. <!-- q: exact id="12ec1dc7" answer="18" -->
   Plant sizes and their returns (%) are: Big 40 boom, 20 normal, −15 slump; Medium 25, 18, 0; Small 12, 10, 6. Using the Hurwicz rule with optimism index α = 0.6, what is the Big plant's score?

   <details><summary>Answer</summary>

   α × best + (1 − α) × worst = 0.6 × 40 + 0.4 × (−15) = 24 − 6 = 18. (Medium scores 15 and Small 9.6, so Big is chosen.)

   </details>

6. <!-- q: mcq id="8dfcb9a7" -->
   A firm buys fuel on a contract that fixes next year's price, so a price rise won't hurt it. Which way of managing risk is this?

   - [ ] Insurance
   - [x] Hedging
   - [ ] Diversification
   - [ ] Adjusting for risk

   <details><summary>Answer</summary>

   Hedging: a contract that offsets an expected loss (a fuel price rise) with a gain on the contract.

   </details>

## Before moving on
<!-- bite: 7d56efd9-b05f-462c-8a82-5d91ab07cc3b -->

You can choose a strategy under risk and under complete ignorance with five rules, and name the four ways to manage risk. **Next:** [[engineering-economics/25-sensitivity-analysis|Sensitivity Analysis]]: which estimate, if wrong, would change your decision.

## Related
<!-- bite: d5c2dbdf-7c8d-4ebe-b08d-709ded481806 -->

- [[engineering-economics/index|Engineering economics map]]
- [[operations-research/index|Operations Research]]: decision analysis in more depth.

## About this lesson
<!-- bite: 67206bbf-4634-4b1a-89ff-bc7d6234b798 -->

**Level:** Beginner to intermediate. **Covers:** payoff tables, decisions under risk with expected value and standard deviation, the Laplace, Wald, maximax, Savage and Hurwicz rules, and the four ways to manage risk, with three corrections to the handout.

**Where it sits:** lesson 24 of 38, part 3 of 3 on risk and uncertainty.

**Source:** the author's own GEG 501 note, section 9 (textbook unit 5). The Hurwicz formula is general knowledge. The Laplace standard deviations are 10.80 and 14.72, slightly different from the note's 10.79 and 14.71, which were rounding slips; they are checked by `scripts/diagrams/engineering_economics.py`.
