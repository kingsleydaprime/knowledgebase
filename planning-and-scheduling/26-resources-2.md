---
id: 899548c4-641b-42fc-b770-3d9276e8c434
---

# Resources 2: Kinds of Resource and Why They Constrain the Schedule

Resources come as labour, equipment and materials, and because almost no project has unlimited amounts of them, availability decides when activities can really start.

## Before you start
<!-- bite: e838e24b-99bd-4082-b5ec-6245dd99022a -->

You should have read [[planning-and-scheduling/25-resources-1|25 — Resources 1]].

After this lesson you will be able to:

1. sort resources into labour, equipment and materials, and say which need levelling;
2. explain the significance of resource constraints on a schedule;
3. compare a time-constrained project with a resource-constrained one.

## What kinds of resources there are
<!-- bite: bae2845c-2532-4663-b69a-d99b51d25fdc -->

The fence's histogram counted workers. But workers aren't the only thing in short supply. Three kinds of resource:

1. **Labour**: This is people, either salaried staff or hourly workers.
2. **Equipment**: This is machines and tools: a post-hole digger, a crane, scaffolding.
3. **Materials**: This is what goes into the work: wood, cement, paint.

Equipment and materials can be split once more:

1. **Construction items** are used and then removed: cranes, scaffolding, formwork.
2. **Installed items** stay in the finished work: generators, concrete, steel bars.

## Which resources need levelling?
<!-- bite: c9e382ea-40dd-4d52-b607-79d0e93611e8 -->

Not every resource is worth smoothing out.

1. **Hired labour and major equipment do.** Uneven demand wastes money: you pay to hire, bring to site and set up, then pay again when you send them away (demobilisation). A digger hired for day 2 and day 9 costs far more than one hired for two days in a row.
2. **Materials generally don't.** Delivery can be lumpy without much cost: 100 cubic metres of concrete one day, none the next week. The supplier delivers what you order when you order it.

So when the lessons ahead talk about smoothing a profile, think workers and big machines.

## Why resources constrain the schedule
<!-- bite: 1b75e816-0c9a-4f48-abcd-f1399b2947ba -->

Asked in 2019/20 and 2023/24 for 4 marks. Virtually every real project needs resources that are not always available in the right amount, and **availability decides when an activity can really start**. CPM ignores this. It lets every activity start as soon as its predecessors are done, so a CPM schedule can need more workers on some days than exist, which makes it impossible to carry out.

**Resource-constrained scheduling** takes availability into account. The usual result is a **longer** project, because activities that compete for the same resource must wait for each other, even if the logic says they could run together. Limits can also come from technical logic, physical space (only two crews fit in a room) or a single piece of equipment.

The fence showed this already: with only three workers, B and C can't both run on day 3, so one must wait.

## Time-constrained or resource-constrained?
<!-- bite: 19ead140-e47b-4220-85a7-d3fbcf5daeda -->

Every project has to decide which one gives way when they clash: the date, or the resources.

1. **Time-constrained project.** The end date is fixed. Resources are flexible: add more to hit the date. The typical tool is **resource smoothing**, moving non-critical work within its float to even out demand without moving the finish.
2. **Resource-constrained project.** The amount of resources is fixed. Time is flexible: a shortage delays the project. The typical tool is **priority rules** (heuristics), which decide which waiting activity gets the scarce resource first.

Example: a stadium needed for a tournament on a fixed date is time-constrained; the contractor hires as many crews as it takes. A church building its hall with volunteer labour is resource-constrained; it finishes when the volunteers can get it done.

The next lesson does smoothing and levelling. Lessons 28 to 31 do priority rules.

## Common pitfalls
<!-- bite: f563f2ed-ebe5-4fae-93b9-06df1f85270f -->

1. **Saying resource constraints shorten a project.** They usually lengthen it, because activities wait for each other.
2. **Levelling materials.** Lumpy delivery is usually fine; it's hired labour and equipment that cost money when uneven.
3. **Mixing the two project types.** Time-constrained: fix the date, flex the resources. Resource-constrained: fix the resources, flex the date.

## Check your understanding
<!-- bite: 4cfc2282-ffc8-40e1-b50f-0e4c403eb102 -->

Try each one before you open the answer.

1. <!-- q: mcq id="2e7c0a95" -->
   Which of these is an installed item rather than a construction item?

   - [ ] Scaffolding
   - [ ] A tower crane
   - [x] A standby generator
   - [ ] Formwork

   <details><summary>Answer</summary>

   The generator stays in the finished building. The others are used and removed.

   </details>

2. <!-- q: mcq id="b6d84f13" -->
   Which resource usually gains the least from levelling?

   - [ ] Hired bricklayers
   - [ ] A rented excavator
   - [x] Sand delivered by tipper
   - [ ] A mobile crane

   <details><summary>Answer</summary>

   Sand, a material: uneven deliveries cost little. Hired labour and big equipment cost money to bring, set up and send away.

   </details>

3. <!-- q: mcq id="9f05e2c8" -->
   A firm must finish a polling-unit fit-out before a fixed election date, whatever it costs. What kind of project is this, and what tool fits?

   - [x] Time-constrained; resource smoothing, adding resources as needed
   - [ ] Resource-constrained; priority rules
   - [ ] Resource-constrained; resource smoothing
   - [ ] Time-constrained; crashing is impossible

   <details><summary>Answer</summary>

   The date is fixed and resources are flexible, so it is time-constrained.

   </details>

4. <!-- q: open id="5a31d7b6" -->
   Explain the significance of resource constraints in project scheduling.

   <details><summary>Answer</summary>

   Real projects rarely have unlimited resources, and an activity can only start when the resources it needs are free. CPM ignores this and may produce a schedule needing more resources at once than exist, which can't be carried out. Resource-constrained scheduling takes availability into account; activities competing for a resource must wait, so the project usually takes longer than the CPM duration. Ignoring this gives an over-optimistic finish date.

   </details>

## Before moving on
<!-- bite: 20007be3-dbac-470d-a355-98e59a917d74 -->

You can sort resources, say which need levelling, and explain why limits lengthen projects. **Next:** [[planning-and-scheduling/27-smoothing-and-levelling|27 — Resource Smoothing and Levelling]].

## Related
<!-- bite: 0e368b8a-519f-4e39-8939-912b2a819c4e -->

- [[planning-and-scheduling/index|Planning and scheduling map]]

## About this lesson
<!-- bite: 75e04569-c7c1-4162-8962-00b90df3d5a6 -->

**Level:** Intermediate. **Covers:** labour, equipment and materials, which resources need levelling, why resources constrain the schedule, and time- against resource-constrained projects.

**Where it sits:** lesson 26 of 35, in part 7 (resources). Part 2 of 7 on resources.

**Source:** the author's own SSG 513 study notes, section 7 (including the MGMT 4135 slides on resource types).
