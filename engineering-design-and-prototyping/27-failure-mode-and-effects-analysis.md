---
id: 7904f5bc-289b-42c9-a6cc-4a032df63c56
---

# Failure Mode and Effects Analysis

Failure Mode and Effects Analysis (FMEA) is a structured way to ask, for each part of a product: how could it fail, what would happen if it did, and what can we do about it.

## Before you start
<!-- bite: ae67cb20-304e-42ac-8b34-b7875d17e47e -->

You should know what a testing protocol is ([[engineering-design-and-prototyping/25-prototyping-and-testing-protocols|lesson 25]]).

After this lesson you will be able to:

1. justify the purpose of FMEA and where it sits in the product development cycle;
2. follow the seven steps of FMEA and calculate a risk priority number;
3. give failure modes, effects and mitigating actions for a simple product.

## What FMEA is
<!-- bite: d596cd0d-7261-42dd-9bdd-334e315982ef -->

Testing asks "does it pass?" FMEA asks a sharper question: "how could it fail?" And it asks it early, before tooling and production, because fixing problems then is cheap.

FMEA is a structured way to ask, for each part of a product:

1. How could it fail? (the **failure mode**)
2. What would happen if it did? (the **effect**)
3. What can we do about it? (the **action**)

Remember from lesson 1: uncertainty about performance in real conditions is one reason design is complex. FMEA is how you hunt that uncertainty down on paper.

## Why FMEA is done early
<!-- bite: a0939823-2ae0-42bd-ba34-24e1fe21d8ce -->

Think of the cost of fixing one mistake at each stage:

- **On paper**, during design: change a line on a drawing.
- **After tooling**: remake an expensive mould.
- **After release**: recall thousands of products, and maybe someone got hurt.

That's the justification for FMEA. It is done early in product development, before tooling and production, because the earlier a failure is found, the cheaper it is to fix. It also tells the team which tests to put in the testing protocol.

## The seven steps of FMEA
<!-- bite: 284568e9-6f3a-45ff-92a9-3f3fcdc07520 -->

1. List the parts and their functions.
2. List the possible failure modes of each.
3. List the effects of each failure.
4. Rate each failure on three scales, usually 1 to 10:
   - **Severity (S)**: how bad the effect is.
   - **Occurrence (O)**: how likely it is to happen.
   - **Detection (D)**: how hard it is to catch before it reaches the user (10 = almost impossible to catch).
5. Calculate the **risk priority number**: RPN = S × O × D.
6. Act first on the highest RPN.
7. Re-rate after the fix.

## The risk priority number
<!-- bite: e139827b-2020-4ca1-a021-75510de9fac9 -->

The risk priority number tells you which failure to fix first: the higher the number, the bigger the risk.

$$RPN = S \times O \times D$$

A failure that is severe, likely and hard to detect gets a very high RPN. A failure that is minor, rare or easy to catch gets a low one. Because it multiplies, a low score on any one of the three pulls the whole number down.

## Example: a retractable ballpoint pen
<!-- bite: 079a050d-5bcf-474b-9da3-9f9ca5b9fa9c -->

Here are two failure modes for a retractable ballpoint pen, the kind you click to push the tip out:

| Failure mode | Effect | Action the design team might take |
| --- | --- | --- |
| The spring weakens or breaks | The tip does not retract, the pen leaks into pockets, or the user cannot click it | Use a better spring material and wire size, and run click-cycle testing (for example tens of thousands of clicks) |
| The click cam or plunger wears or cracks | The tip will not lock out, or locks out and slips back while writing | Use a harder, wear-resistant plastic, tighten tolerances and test for wear |

## Rating the pen's failures
<!-- bite: 53de97b3-6438-4f1a-be8c-f806828010ae -->

To show the RPN step, here are example ratings for the two pen failures. (These numbers are made up to show the method; a real team would get them from data and testing.)

| Failure mode | S | O | D | RPN |
| --- | --- | --- | --- | --- |
| Spring weakens or breaks | 6 | 4 | 5 | 6 × 4 × 5 = **120** |
| Click cam or plunger wears | 5 | 3 | 4 | 5 × 3 × 4 = **60** |

The spring has the higher RPN, so the team fixes it first. After the better spring, occurrence might drop from 4 to 2, and the re-rated RPN becomes 6 × 2 × 5 = 60.

That's every phase of the design process covered. The last two lessons put them all together on one real problem.

## Common pitfalls
<!-- bite: 41c1b6d8-fabf-4616-876f-89442b5f21c9 -->

1. **Mixing up failure mode and effect.** The mode is what goes wrong with the part (the spring breaks). The effect is what the user experiences (the pen leaks into the pocket).
2. **Getting detection backwards.** A high detection score means the failure is *hard* to catch, which is worse.
3. **Doing FMEA after production.** Its whole value is finding problems before tooling, when fixes are cheap.

## Check your understanding
<!-- bite: c6b5aacd-9eae-4b67-9549-908993a872e7 -->

Try each one before you open the answer.

1. <!-- q: exact id="3d8b1f06" answer="168" -->
   An FMEA rates a bicycle brake cable snapping as Severity 7, Occurrence 3, Detection 8. What is its risk priority number?

   <details><summary>Answer</summary>

   7 × 3 × 8 = 168.

   </details>

2. <!-- q: mcq id="a62e9c41" -->
   An FMEA for a kettle has three failures with RPN 90 (lid hinge breaks), 240 (switch fails to turn off) and 36 (handle colour fades). Which should the team act on first?

   - [ ] Lid hinge breaks (90)
   - [x] Switch fails to turn off (240)
   - [ ] Handle colour fades (36)

   <details><summary>Answer</summary>

   The switch, with the highest RPN. A kettle that doesn't switch off is severe and dangerous.

   </details>

3. <!-- q: mcq id="5f0d7b93" -->
   In an FMEA of a phone charger, "the cable insulation cracks" is a ___ and "the user gets an electric shock" is its ___.

   - [x] failure mode; effect
   - [ ] effect; failure mode
   - [ ] action; failure mode

   <details><summary>Answer</summary>

   The cracking insulation is the failure mode (what goes wrong with the part). The shock is the effect (what happens because of it).

   </details>

4. <!-- q: mcq id="e81c4a2d" -->
   When in the product development cycle should FMEA be done?

   - [x] Early, before tooling and production
   - [ ] After the first products are sold
   - [ ] Only after testing finds a problem

   <details><summary>Answer</summary>

   Early, before tooling and production, because fixing problems then is cheap.

   </details>

5. <!-- q: open id="0c9f3e57" -->
   Give two failure modes for a simple stapler, with the effect of each and an action the design team could take.

   <details><summary>Answer</summary>

   For example. (1) Failure mode: the spring that pushes the staples forward weakens. Effect: staples don't feed, so it clicks without stapling. Action: a stronger spring material and cycle testing. (2) Failure mode: the anvil (the metal plate that bends the staple) wears or bends. Effect: staples don't fold flat and snag paper. Action: a harder steel anvil and wear testing. Any answer works if each mode is about a part, each effect is what the user sees, and each action reduces the risk.

   </details>

## Before moving on
<!-- bite: 907c307b-b242-4d9b-b8e8-e60844ecc76c -->

You can justify FMEA, follow its seven steps, calculate an RPN, and give failure modes, effects and actions for a simple product. **Next:** [[engineering-design-and-prototyping/28-reliability|28 — Reliability]]: how likely a product is to keep working, and how to design that in.

## Related
<!-- bite: 35c52abe-d8f5-4848-b2c5-05cebf6eacaf -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[systems-engineering/08-risk-and-failure-analysis|Risk and Failure Analysis]]: FMEA and fault trees from the systems engineering side.

## About this lesson
<!-- bite: f866f4fe-2eeb-4813-adb0-7f25614ac223 -->

**Level:** Intermediate. **Covers:** the purpose of FMEA, its seven steps, the risk priority number, and the retractable ballpoint pen example.

**Where it sits:** lesson 27 of 36, in part 8 (making it safe and proving it works).

**Source:** written for the SSG 532 exam from general engineering knowledge. It is not in the lecture notes, so check it against any slides the lecturer gave. The pen's S, O and D ratings are illustrative.
