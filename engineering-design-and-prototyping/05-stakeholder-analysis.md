---
id: 86be5372-ef68-4299-8f59-5d0c0d2c3f76
---

# Stakeholder Analysis

Stakeholder analysis finds everyone a design affects or who can affect it, and works out what each of them needs and how much attention they deserve.

## Before you start
<!-- bite: 88b560af-da52-4c36-ae2b-744aaa364491 -->

You should know the four parts of a problem definition ([[engineering-design-and-prototyping/04-problem-definition|04 — Problem Definition]]).

After this lesson you will be able to:

1. say what a stakeholder is, and list the stakeholders of a product;
2. place stakeholders on a power-interest grid and say how to treat each group;
3. turn what stakeholders say into needs, and spot needs that conflict.

## What a stakeholder is
<!-- bite: 2c20ffeb-4d7f-468f-be8a-58f46e3faa0d -->

A **stakeholder** is any person or group who is affected by a design, or who can affect it. The user is the obvious one, but never the only one.

Think of the student backpack from lesson 04. The student carries it. A parent pays for it. The school sets rules about size. The factory has to make it, the shop has to stock it, and one day someone has to throw it away or recycle it. Each of them wants something different, and a backpack that pleases only the student can still fail.

**Stakeholder analysis** is the method for finding all of them, understanding what they need, and deciding how much each one's voice should count. It comes straight after defining the problem, because you can't write requirements (lesson 06) until you know whose needs they serve.

## Kinds of stakeholder
<!-- bite: 79a98930-b084-4d37-9f65-b3df0e0cfc67 -->

Three ways of sorting them help you not miss anyone:

1. **Primary and secondary.** Primary stakeholders use or pay for the product directly: the student and the parent. Secondary stakeholders are affected less directly: the school, the shop, the recycler.
2. **Internal and external.** Internal stakeholders are inside your organisation: designers, the factory, sales, management. External ones are outside it: customers, suppliers, regulators, the public.
3. **Key stakeholders.** These are the few with the power to stop or change the project, such as the client paying for it or a regulator who must approve it.

## The backpack's stakeholders
<!-- bite: 60f4389e-538a-42db-a1ec-431a75d83db5 -->

| Stakeholder | Kind | What they want |
| --- | --- | --- |
| Student | Primary, external | Comfortable, holds a laptop, looks good |
| Parent | Primary, external | Cheap, lasts years |
| School | Secondary, external | Fits in lockers, no dangerous parts |
| Manufacturer | Internal | Easy to make, cheap materials |
| Retailer | Secondary, external | Packs flat, sells well |
| Recycler | Secondary, external | Separable materials |

Notice the needs already pull against each other: the student wants it stylish, the parent wants it cheap, and the manufacturer wants it simple.

## The power-interest grid
<!-- bite: 0fdc8a96-5a16-41ad-8e02-1469c60fb16b -->

Not every stakeholder can be given the same attention. The **power-interest grid** sorts them by two questions: how much **power** do they have over the project, and how much **interest** do they take in it?

![A power-interest grid with power on the vertical axis and interest on the horizontal axis; high power and high interest is manage closely, high power and low interest is keep satisfied, low power and high interest is keep informed, and low power and low interest is monitor; the backpack's stakeholders are placed in the quadrants](images/ed-power-interest.svg)

## Reading the grid
<!-- bite: cca7cd58-e43c-431d-b211-2fcd3bd17c44 -->

Each box says how to treat the stakeholders in it.

1. **High power, high interest: manage closely.** Involve them in decisions and review designs with them. For a school backpack contract, the school buyer.
2. **High power, low interest: keep satisfied.** Meet their requirements without overloading them. A regulator who only cares that safety rules are met.
3. **Low power, high interest: keep informed.** Tell them what is happening and listen to them. Students: individually they can't change the project, but they care a lot.
4. **Low power, low interest: monitor.** Check now and then that this hasn't changed. The recycler, for now.

People move between boxes. If a product is recalled, a regulator's interest jumps.

## Finding out what they need
<!-- bite: 1dba0c01-7209-4e38-b087-2d848a466010 -->

Stakeholders rarely say exactly what they need. Four ways to find out:

1. **Interviews:** talk to a few in depth. Ask about problems, not solutions: "what annoys you about your bag?", not "do you want a bottle pocket?"
2. **Surveys:** reach many people with the same questions.
3. **Observation:** watch them use current products. People often do things they wouldn't think to mention, like carrying a laptop in their hand because the bag has no padded sleeve.
4. **Workshops:** bring several stakeholders together, so conflicts come out early.

Then separate **needs** (what must be true, such as "protects a laptop") from **wants** (nice to have, such as "comes in five colours"), and write each need in the stakeholder's own words before you turn it into a requirement.

## When needs conflict
<!-- bite: f57150d2-27d5-46cc-9437-069e03f52a25 -->

Conflicts are normal. When the parent wants cheap and the student wants waterproof:

1. **Check it's real.** Sometimes a cheaper waterproof fabric exists.
2. **Use the grid.** Needs of manage-closely stakeholders weigh more.
3. **Make the trade-off explicit,** and write down who agreed to it.
4. **Look for a design that removes the conflict,** which is exactly what TRIZ (lesson 08) is for.

## Common pitfalls
<!-- bite: f2f87428-716a-48f9-a3c8-ae98c430f4f2 -->

1. **Only thinking of the user.** The people who make, sell, regulate and dispose of the product are stakeholders too.
2. **Asking stakeholders for solutions.** Ask about their problems; designing the solution is your job.
3. **Treating everyone the same.** Use the grid; a regulator who can block the product needs different handling from a passing customer.
4. **Doing it once.** Stakeholders and their interest change through the project.

Stakeholders tell you what they need in their own words. Next lesson turns those needs into requirements engineers can design to.

## Check your understanding
<!-- bite: 92dc239d-8ff0-4f9f-8fc1-bb9d8311b122 -->

Try each one before you open the answer.

1. <!-- q: mcq id="314b30e2" -->
   For a new hospital bed, which of these are stakeholders? Choose all that apply.

   - [x] Patients
   - [x] Nurses who move and adjust the bed
   - [x] The hospital's purchasing department
   - [x] The health regulator

   <details><summary>Answer</summary>

   All four. Patients and nurses use it, purchasing pays for it, and the regulator must approve it. A stakeholder is anyone affected by the design or able to affect it.

   </details>

2. <!-- q: mcq id="50307e1e" -->
   On a power-interest grid, a government safety regulator has high power but takes little interest beyond the rules being met. How should the design team treat them?

   - [ ] Manage closely
   - [x] Keep satisfied
   - [ ] Keep informed
   - [ ] Monitor

   <details><summary>Answer</summary>

   Keep satisfied: meet their requirements without overloading them. If something goes wrong, their interest rises and they move to manage closely.

   </details>

3. <!-- q: gap id="43da8209" answers="primary;secondary" -->
   Stakeholders who use or pay for a product directly are ___ stakeholders. Those affected less directly, such as a recycler, are ___ stakeholders.

   <details><summary>Answer</summary>

   Primary, then secondary.

   </details>

4. <!-- q: mcq id="f4cab1ee" -->
   Which interview question is best for finding a student's real needs for a backpack?

   - [ ] "Would you like a USB charging port?"
   - [ ] "Do you prefer red or blue?"
   - [x] "What annoys you about the bag you use now?"
   - [ ] "Would you pay ₦20,000 for a better bag?"

   <details><summary>Answer</summary>

   Ask about problems, not solutions. The other questions push your own ideas, so you learn only whether people like them.

   </details>

5. <!-- q: open id="83526b85" -->
   For a school's new water dispenser, name four stakeholders, put each on the power-interest grid, and say how you would treat one of them.

   <details><summary>Answer</summary>

   For example: the school's management (high power, high interest: manage closely, involve them in reviews); students (low power, high interest: keep informed, ask them what they need); the health inspector (high power, low interest: keep satisfied by meeting hygiene rules); the cleaning staff (low power, moderate interest: keep informed, since they must clean it). Any sensible placing with a reason is fine.

   </details>

6. <!-- q: open id="ef4b4f50" -->
   A parent wants a backpack to be cheap, and a student wants it waterproof. How should the designer handle the conflict?

   <details><summary>Answer</summary>

   First check the conflict is real: a cheap waterproof fabric may exist. If it is real, weigh the needs using the power-interest grid (whoever pays and decides may weigh more), make the trade-off explicit and record who agreed. Better still, look for a design that removes the conflict, for example a cheap bag with a waterproof laptop sleeve only.

   </details>

## Before moving on
<!-- bite: 39b9080c-dfa7-4bb6-a9dd-8e6b062074db -->

You can find a design's stakeholders, place them on the power-interest grid, and draw their needs out. **Next:** [[engineering-design-and-prototyping/06-requirements-and-requirement-writing|06 — Requirements and Requirement Writing]]: the kinds of requirements, and how to write ones you can test.

## Related
<!-- bite: bbcaaa20-0e9f-4e90-a637-324736735874 -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[systems-engineering/02-requirements|Requirements]] in systems engineering.

## About this lesson
<!-- bite: 05a389a1-d60b-4514-bbc4-b13832b88281 -->

**Level:** Beginner. **Covers:** what a stakeholder is, three ways to sort stakeholders, the power-interest grid, ways to find needs, needs versus wants, and handling conflicts.

**Where it sits:** lesson 05 of 36, in part 2 (defining the problem).

**Source:** written from general engineering design knowledge, because the SSG 532 lecture notes don't cover stakeholder analysis; it is on the official course outline. The diagram comes from `scripts/diagrams/engineering_design.py`.
