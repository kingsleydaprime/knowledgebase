---
id: cb0a731d-2193-4d50-8232-31a666b1f535
---

# Risk and Uncertainty 1: What They Are and the Five Categories

Risk is when the outcome is unknown but its probabilities are known or can be estimated, and uncertainty is when even the probabilities are unknown.

## Before you start
<!-- bite: 085b5777-58e1-4a23-946e-fc8440611a9b -->

You should have finished part 5, ending with [[engineering-economics/21-cost-estimation-3|Cost Estimation 3]].

After this lesson you will be able to:

1. tell risk from uncertainty, with examples, and describe decisions under certainty, risk and uncertainty;
2. describe the five categories of risk in engineering economics, with their causes and examples;
3. explain how each category affects economic decisions.

## What risk and uncertainty are
<!-- bite: ba991fe9-4364-4fc1-ba5f-ad6cc14301e7 -->

All the earlier lessons used estimated numbers as if they were certain. In reality the future is not certain, so this part shows how to deal with that.

Think about two bets. In the first, I toss a fair coin: heads you win ₦1,000, tails you lose ₦1,000. You don't know what will happen, but you know the chances: 50-50. In the second, I ask you to bet on whether a brand-new kind of battery factory in a new country will make a profit. You have no idea of the chances at all. The first is risk. The second is uncertainty.

## Risk vs uncertainty
<!-- bite: 73180f51-b725-42dd-bbed-e518393f31dc -->

- **Risk:** the outcome is unknown, but the probability of each outcome is **known or can be estimated**, because there is data (historical records, failure records, market data). Example: steel price has a 40% chance of rising and 60% of falling; a generator has a 10% chance of needing extra repairs each year. A fair coin and the stock market are the textbook examples.
- **Uncertainty:** the outcome is unknown and the **probability is also unknown**, because there is no history or the situation is new. Example: a brand-new technology, a sudden government policy, a plant in a region with no weather records.

> **Correction:** in one place (section 5.4) the textbook unit defines uncertainty the opposite way, as "probabilities known". That contradicts its own section 5.2 and your lecture. Use the definitions above.

## Certainty, risk and uncertainty
<!-- bite: 36960a22-ef17-4240-8379-efa5f2aa1270 -->

Decisions can be made under three conditions:

1. **Certainty:** you know the alternatives and outcomes. This is rare.
2. **Risk:** you know the probabilities.
3. **Uncertainty:** you don't.

Uncertainty comes in two forms. With **partial ignorance** you can assign subjective probabilities (your best guess at the odds), so it becomes a risk problem. With **complete ignorance** you cannot, so you need the special decision rules in lesson 24.

## The five categories of risk: what they are
<!-- bite: 846cfc8e-c105-4771-bcca-8420765a7370 -->

| Risk | What it is | Typical causes |
| --- | --- | --- |
| Market | Uncertainty from changes in market prices of inputs, outputs or materials | Global supply and demand changes, exchange rates, commodity cycles, inflation shocks, supply chain disruption |
| Technical | Failure of technology, equipment or design | Poor design or testing, manufacturing defects, ageing equipment, poor maintenance, operating conditions different from design |
| Financial | Changes in financial conditions that affect cost or returns | Interest rate changes, exchange rate swings, inflation shocks, loan repayment changes, tighter credit |
| Regulatory or political | Changes in laws or government rules | New tax laws, sudden bans, licensing rules, import duty changes |
| Environmental | Natural events or conditions that affect performance or safety | Extreme weather, flooding, drought, erosion, disasters, climate variability |

## The five categories: engineering examples
<!-- bite: 7530ae24-c39f-476b-9152-989f73f58ca1 -->

- **Market:** steel price rise makes construction dearer; diesel price changes affect running cost; an oil price crash cuts a refinery's revenue.
- **Technical:** a machine that keeps breaking down; a new solar inverter that underperforms; unexpected corrosion in a water plant.
- **Financial:** borrowing cost jumps from 12% to 18%; a company that borrows in dollars sees the naira fall.
- **Regulatory or political:** subsidy removal sharply raises fuel cost; new import tariff on foreign machinery; new building codes force redesign.
- **Environmental:** flooding damages equipment or delays work; high temperature reduces solar panel and turbine efficiency.

## How each category affects economic decisions
<!-- bite: 31b08a42-a679-4e95-8489-314ed45ff0a6 -->

- **Market:** changes cost estimates and operating cost projections, and can turn a good project into a bad one or the reverse.
- **Technical:** unpredictable repairs and downtime, lower output, shorter equipment life, higher replacement cost.
- **Financial:** lower profitability, some projects become unaffordable, loan schedules change, long-term projections become less certain.
- **Regulatory:** higher operating and legal cost, delays or stalls, redesign or retrofit.
- **Environmental:** higher insurance and repair cost, delays, unexpected replacement, less reliable projections.

Other risk types in the textbook unit: business, inflation, interest rate, credit, liquidity, derivative, cultural, currency and government policy risk.

Knowing the kinds of risk is step one. Step two is putting a number on how risky a project is, and that's the next lesson.

## Check your understanding
<!-- bite: b0f3a48e-4603-4ca8-ac7c-540e150ff867 -->

Try each one before you open the answer.

1. <!-- q: mcq id="57a3ce7d" -->
   A water company has 20 years of pump failure records and estimates a 5% chance a pump fails in any year. Is this a situation of risk or uncertainty?

   - [x] Risk, because the probability can be estimated from data
   - [ ] Uncertainty, because the failure might not happen
   - [ ] Certainty, because the records are complete

   <details><summary>Answer</summary>

   Risk. The outcome is unknown, but the probability can be estimated from historical failure records.

   </details>

2. <!-- q: mcq id="c8fcd476" -->
   A firm plans to build the first plant of its kind in a region with no weather records, using a technology never used commercially. Which condition is this?

   - [ ] Certainty
   - [ ] Risk
   - [x] Uncertainty

   <details><summary>Answer</summary>

   Uncertainty: the outcome is unknown and so is the probability, because the situation is new and there is no history.

   </details>

3. <!-- q: mcq id="642a4ffc" -->
   A Nigerian firm borrows in US dollars to buy a plant, and the naira falls sharply against the dollar. Which category of risk is this?

   - [ ] Market
   - [ ] Technical
   - [x] Financial
   - [ ] Environmental

   <details><summary>Answer</summary>

   Financial risk: a change in financial conditions (the exchange rate) that raises the cost of repaying the loan.

   </details>

4. <!-- q: mcq id="a4a0a763" -->
   The government removes the fuel subsidy and a factory's running cost doubles. Which category of risk is this?

   - [ ] Market
   - [x] Regulatory or political
   - [ ] Technical
   - [ ] Environmental

   <details><summary>Answer</summary>

   Regulatory or political: a change in government rules. Subsidy removal is the lecture's own example.

   </details>

5. <!-- q: gap id="719109db" answers="partial;complete" -->
   Fill in the gaps. Under ___ ignorance you can assign subjective probabilities, so the problem becomes one of risk. Under ___ ignorance you cannot, so you need special decision rules.

   <details><summary>Answer</summary>

   Partial; complete.

   </details>

6. <!-- q: open id="2e6e28de" -->
   Write a short note on risk and uncertainty in engineering economic analysis.

   <details><summary>Answer</summary>

   Engineering economic analysis uses estimates of the future, which is not certain. Under risk, the outcome is unknown but the probability of each outcome is known or can be estimated from data (failure records, market data), so tools like expected value and standard deviation can be used. Under uncertainty, the probabilities are also unknown (new technology, sudden policy), so special rules such as maximin, maximax, Laplace and minimax regret are used, unless subjective probabilities can be assigned (partial ignorance). The five categories of risk are market, technical, financial, regulatory or political, and environmental; each can raise cost, delay a project or turn a good project into a bad one. Risk is managed by insurance, hedging, diversification and adjusting for risk (for example a higher MARR or a contingency), and tested with sensitivity analysis.

   </details>

## Before moving on
<!-- bite: 41117bde-edf2-49cb-bab6-69d217a5ef3b -->

You can tell risk from uncertainty, name the five categories of risk with examples, and explain their effects. **Next:** [[engineering-economics/23-risk-and-uncertainty-2|Risk and Uncertainty 2]]: measuring risk.

## Related
<!-- bite: d810be84-c46d-4c69-94a4-219253871fe0 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: 84d19627-ad99-40f9-8081-f390778ad3fc -->

**Level:** Beginner. **Covers:** risk and uncertainty, decisions under certainty, risk and uncertainty, partial and complete ignorance, the five categories of risk with causes, examples and effects, and the textbook's other risk types.

**Where it sits:** lesson 22 of 38, part 1 of 3 on risk and uncertainty.

**Source:** the author's own GEG 501 note, section 9 (lecture and textbook unit 5), with a correction from section 15 of the note.
