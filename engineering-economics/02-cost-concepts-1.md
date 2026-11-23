---
id: 7956b252-296c-4ce6-a8e1-374e8041a2ae
---

# Cost Concepts 1: The Types of Cost

A cost is a resource you give up to achieve something, and engineers sort costs into types so they know which ones matter for a decision.

## Before you start
<!-- bite: 12b0082f-3721-4e9b-8361-76ec8c4da79e -->

You should have read [[engineering-economics/01-introduction-to-engineering-economics|Introduction to Engineering Economics]].

After this lesson you will be able to:

1. define fixed, variable, sunk, opportunity and incremental cost, with an example of each;
2. read the fixed and variable parts from a cost equation like y = 10 + 5x;
3. describe the other classifications: semi-variable, direct and indirect, product and period, relevant and irrelevant, and real cost.

## What cost concepts are
<!-- bite: ebc7375c-c00b-48ca-80c7-1e5d7610c2ec -->

Every decision in engineering economics is a comparison of costs and benefits, so you need to know the types of cost. A cost is a resource you give up to achieve something.

Why sort them into types? Because not every cost should affect every decision. A fee you've already paid can't be got back whichever option you pick, so it shouldn't sway you. A cost that rises with every unit you make matters a lot when you're deciding how much to make. This lesson gives the types, and lesson 03 puts numbers on them.

## Basic cost concepts (from your lectures)
<!-- bite: 011d8d29-95cb-4375-a58e-a43af4a6f4c8 -->

| Cost | Meaning | Example |
| --- | --- | --- |
| Fixed cost | Stays the same whatever the output | Rent, salary of permanent staff, insurance |
| Variable cost | Changes with the level of output or activity | Raw materials: build more bridges, buy more material |
| Sunk cost | Already committed and cannot be recovered, so it should not affect future decisions | A government fee paid before you build a refinery |
| Opportunity cost | The value of the next best alternative you give up | Money put in one project cannot be used in another |
| Incremental cost | The extra cost of one specific action | Expanding production, adopting a new technology |

## How the basic costs connect
<!-- bite: 0f17edac-9c46-445a-87cf-ad999f4d51c4 -->

A few connections between these:

- Because resources are scarce, every choice has an opportunity cost. That is why opportunity cost forces engineers to think about trade-offs. It is a concept, so you usually cannot put a figure on it.
- Variable cost can go up or down with output. Incremental cost deals only with the **increase** caused by a decision, and it can include a new fixed cost (for example buying a new machine to expand).
- Variable cost is tied to production only. Maintaining a car is not a variable cost of production.
- Sunk costs are ignored in comparisons because they are the same whichever option you pick. This comes back as "relevant cash flows only" when we compare alternatives in lesson 11.

## The simple cost equation
<!-- bite: 666cd161-174d-45d8-b6db-ee39eb843919 -->

Total cost is the fixed cost plus the variable cost of every unit you make. In symbols:

$$\text{Total cost} = \text{fixed cost} + \text{variable cost per unit} \times \text{output}$$

For example y = 10 + 5x has a fixed cost of 10 (the intercept) and a variable cost of 5 per unit (the slope). Making 20 units costs 10 + 5 × 20 = 110. The 10 is there even if you make nothing.

Keep this straight line in your head. It comes back in break-even analysis (lesson 26), where it meets a revenue line.

## Other cost classifications (from the textbook material)
<!-- bite: fafe1e3c-1031-4b76-beb4-d760f47ce6a0 -->

The textbook sorts costs in a few more ways. Each pair answers a different question.

- **Semi-variable (mixed) cost:** has a fixed part and a variable part. A phone bill is the usual example: a fixed line rental plus a charge for use. It moves in the same direction as output but not in direct proportion.
- **Direct and indirect cost:** direct costs can be traced to a product (raw materials, wages of the workers who make it). Indirect costs are shared overheads (factory manager's salary, rent, supervision, security, utilities, depreciation of machines).
- **Product and period cost:** product costs are tied to making the goods (direct materials, direct labour, variable factory overhead). Period costs are not tied to production, such as fixed costs for the period.

## Relevant, irrelevant and real cost
<!-- bite: 99160ae5-f171-4be4-a9d6-eb86319a7238 -->

- **Relevant and irrelevant cost:** relevant costs change with a decision (incremental costs, opportunity costs, out-of-pocket costs). Irrelevant costs will not change whatever you decide, so you ignore them.
- **Real cost:** the sacrifice society makes to produce something (the worker's effort, pollution, the saver's waiting), beyond the money paid. It is hard to measure, so money cost is used in practice.

Notice that sunk cost is the classic irrelevant cost: it's gone, whatever you choose.

## Common pitfalls
<!-- bite: da876a3c-a49a-442e-9c6e-0520540d2acd -->

1. **Letting a sunk cost decide.** "We've already spent ₦2 million on this design, so we must finish it" is the trap. The ₦2 million is gone either way. Compare only what happens from now on.
2. **Calling every rising cost variable.** Variable cost is tied to production. A cost that rises because the car is getting old is not a variable cost of production.
3. **Confusing incremental with variable.** Incremental cost is the extra cost of one decision, and it can include a new fixed cost like a machine.

So we have the types. Lesson 03 does the arithmetic: cost per unit, the cost of one more unit, and the cost sheet that builds a total cost up in layers.

## Check your understanding
<!-- bite: 21a58ac3-0efc-4755-8fdc-fb960287c8ad -->

Try each one before you open the answer.

1. <!-- q: mcq id="ac037070" -->
   A firm spent ₦3 million on a feasibility study last year. It is now choosing between two plant designs. How should the ₦3 million be treated?

   - [ ] As a fixed cost of both designs
   - [x] Ignored, because it is a sunk cost
   - [ ] As an opportunity cost
   - [ ] Added to whichever design is cheaper

   <details><summary>Answer</summary>

   Ignored. It is a sunk cost: already committed and not recoverable, and it is the same whichever design is chosen, so it cannot change the decision.

   </details>

2. <!-- q: gap id="9f1ab857" answers="25;8" -->
   A workshop's total cost is y = 25 + 8x, where x is the number of chairs made. Fill in the gaps. The fixed cost is ___ and the variable cost per chair is ___.

   <details><summary>Answer</summary>

   The fixed cost is 25 (the intercept) and the variable cost is 8 per chair (the slope).

   </details>

3. <!-- q: exact id="b14cb3aa" answer="345" -->
   A workshop's total cost is y = 25 + 8x, where x is the number of chairs made. What is the total cost of making 40 chairs?

   <details><summary>Answer</summary>

   25 + 8 × 40 = 25 + 320 = 345.

   </details>

4. <!-- q: mcq id="e94ccd49" -->
   A factory's electricity bill has a fixed monthly charge plus a charge for every kilowatt-hour used. What kind of cost is it?

   - [ ] Fixed cost
   - [ ] Sunk cost
   - [x] Semi-variable (mixed) cost
   - [ ] Opportunity cost

   <details><summary>Answer</summary>

   Semi-variable: a fixed part plus a variable part, like the phone bill example. It moves with use but not in direct proportion.

   </details>

5. <!-- q: mcq id="9751df9b" -->
   Which of these is an indirect cost of making bicycles?

   - [ ] Steel tubing for the frames
   - [ ] Wages of the welders who build the frames
   - [x] The factory security guard's salary
   - [ ] Tyres fitted to each bicycle

   <details><summary>Answer</summary>

   The security guard's salary. It is a shared overhead that can't be traced to one bicycle. The tubing, tyres and welders' wages are direct costs.

   </details>

6. <!-- q: open id="12ec1dc5" -->
   What is opportunity cost, and why does it force engineers to think about trade-offs?

   <details><summary>Answer</summary>

   Opportunity cost is the value of the next best alternative you give up. Because resources are scarce, money or effort used in one project cannot be used in another, so every choice has an opportunity cost. That makes engineers weigh what they lose by not choosing the other option, which is a trade-off. It is a concept, so it usually can't be given an exact figure.

   </details>

## Before moving on
<!-- bite: 07950c10-c09b-4af6-8a8d-729c048f0a28 -->

You can name and define the basic cost types, read fixed and variable cost from a cost equation, and say which costs are relevant to a decision. **Next:** [[engineering-economics/03-cost-concepts-2|Cost Concepts 2]]: average cost, marginal cost and the cost sheet.

## Related
<!-- bite: 400cd98a-49ba-4fd8-bd3c-31e5ce8b38a4 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: b314aee5-c2b6-405e-be01-b37963bc6212 -->

**Level:** Beginner. **Covers:** fixed, variable, sunk, opportunity and incremental cost, the cost equation, and the textbook's other classifications (semi-variable, direct and indirect, product and period, relevant and irrelevant, real cost).

**Where it sits:** lesson 02 of 38, part 1 of 2 on cost concepts.

**Source:** the author's own GEG 501 note, section 2.
