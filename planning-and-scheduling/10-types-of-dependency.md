---
id: 66f41d8d-4e9a-409b-a0da-a26fcac4ebf5
---

# Types of Dependency

A dependency is the reason one activity must wait for another, and project teams sort those reasons into four types: mandatory, discretionary, external and internal.

## Before you start
<!-- bite: 3e52d1e6-211d-425b-93da-ae3ab3fb2c97 -->

You should have read [[planning-and-scheduling/09-network-diagrams-2|09 — Network Diagrams 2]].

After this lesson you will be able to:

1. name and explain the four types of dependency;
2. classify a given dependency, with a reason;
3. explain why discretionary dependencies must be written down.

## What a dependency is
<!-- bite: 657ae315-6ab9-45fc-baf0-683ceadfb448 -->

Every arrow in a network diagram says "this waits for that". But arrows don't say *why*. The why matters, because some waits can never be changed, some are just the team's preference, and some depend on people outside the project. When the plan is late and you need to save time, you look first at the waits you are free to change.

The four types are decided by the project team when it puts the activities in order (activity sequencing). They appear in four past papers (2019/20, 2020/21, 2023/24, 2024/25), so learn each with an example.

## Mandatory dependency
<!-- bite: a0e2b11b-dfdb-4707-8df1-0cdb6086e70c -->

A mandatory dependency is required by a contract or by the nature of the work itself, often by physics. It is also called **hard logic**, because there is no way round it.

Example: you can't erect the fence (D) before the holes are dug (A). You can't build the ceiling before the walls. You can't paint what isn't up.

These waits can't be removed when the project runs late.

## Discretionary dependency
<!-- bite: 73dbee94-59fc-4b07-b499-6cd96bad4f71 -->

A discretionary dependency is an order the team has chosen, because it is good practice or experience says it works better, not because the work demands it. It is also called **preferred logic** or **soft logic**.

Example: the team chooses to paint the fence (G) before the gate (H) so one painter can do both in a row. The gate could physically be painted first.

These must be **documented**, because they limit later options. Six months later, nobody remembers it was only a preference, and the team treats a soft wait as a hard one when it could have been changed to save time.

## External dependency
<!-- bite: 13c64e9d-f4ae-4f39-a2a3-2ebab447efdc -->

An external dependency links a project activity to something outside the team's control.

Examples: waiting for the supplier to deliver the wood; waiting for the estate association to approve the fence height; waiting for a government building permit.

The team can't speed these up directly, but it can plan around them: order early, chase the supplier, apply for the permit before it is needed.

## Internal dependency
<!-- bite: 5f1f3d92-ce6d-43ef-9a3d-9bd5a72e7719 -->

An internal dependency is a wait between two activities that are both inside the project and both under the team's control.

Examples: the team's own carpenter can't hang the gate until the team's own builders finish the fence. In software, testing can't start until the team's code is written.

## The four side by side
<!-- bite: 4814c8ee-290e-4c6e-8b71-4c51e286edaf -->

1. **Mandatory** (hard logic): required by contract or by the nature of the work. You can't build the ceiling before the walls.
2. **Discretionary** (preferred or soft logic): the team's chosen order, which must be documented. Painting rooms in a set order.
3. **External**: depends on something outside the team's control. A delivery or a permit.
4. **Internal**: between two activities inside the project. Testing after coding.

The four can overlap. "Erect fence after the wood is delivered" is external (the supplier) and also mandatory (no wood, no fence).

So far every wait has been "finish, then start". In practice a job can often start before the one before it finishes, and that is what precedence relationships describe, next lesson.

## Common pitfalls
<!-- bite: 697feeaf-971e-4997-86e1-2fb4437235b1 -->

1. **Swapping mandatory and discretionary.** Ask: "would it be physically or legally impossible the other way?" If yes, mandatory; if it is only better, discretionary.
2. **Not saying why discretionary ones are documented.** The mark is for "because they limit later scheduling options".
3. **Thinking types can't overlap.** One wait can be both external and mandatory.

## Check your understanding
<!-- bite: 24e14fe3-9b64-48be-beb3-150232aef8e4 -->

Try each one before you open the answer.

1. <!-- q: mcq id="b0e27f4c" -->
   A building's roof cannot be laid until its walls are up. What type of dependency is this?

   - [x] Mandatory
   - [ ] Discretionary
   - [ ] External
   - [ ] None, it is a resource limit

   <details><summary>Answer</summary>

   Mandatory, or hard logic: the nature of the work requires it.

   </details>

2. <!-- q: mcq id="58d3a1e9" -->
   A project can't start drilling until the state government issues an environmental permit. What type of dependency is this?

   - [ ] Internal
   - [ ] Discretionary
   - [x] External
   - [ ] Mandatory only

   <details><summary>Answer</summary>

   External: it depends on a body outside the team's control. It is also mandatory in the legal sense, since the law requires the permit.

   </details>

3. <!-- q: gap id="e6c90b25" answers="soft|preferred" -->
   A discretionary dependency is also called preferred logic or ___ logic.

   <details><summary>Answer</summary>

   Soft logic.

   </details>

4. <!-- q: open id="1a7f4d03" -->
   Why must discretionary dependencies be documented?

   <details><summary>Answer</summary>

   Because they are the team's choice, not a necessity, and they limit later scheduling options. If they aren't written down, later planners treat them as fixed, and miss the chance to reorder those activities when the project needs to save time.

   </details>

5. <!-- q: open id="c4e8b296" -->
   Explain the four types of dependency, with one example of each from building a classroom block.

   <details><summary>Answer</summary>

   Mandatory: required by the work itself, such as the roof can't go on before the walls. Discretionary: the team's chosen order, such as plastering the left wing before the right. External: outside the team's control, such as waiting for the electricity company to connect the supply. Internal: between two project activities, such as the team's electricians wiring after the team's masons finish the walls.

   </details>

## Before moving on
<!-- bite: a044701e-ab32-4ea1-a2a5-ef69c63918b7 -->

You can name the four types, classify a dependency and explain why soft logic is written down. **Next:** [[planning-and-scheduling/11-precedence-relationships-1|11 — Precedence Relationships 1]].

## Related
<!-- bite: b739d92c-9e90-4603-a83a-f0cdef2c4dfb -->

- [[planning-and-scheduling/index|Planning and scheduling map]]

## About this lesson
<!-- bite: b4b86ec8-68f0-472b-8c95-a51db763b186 -->

**Level:** Beginner. **Covers:** mandatory, discretionary, external and internal dependencies, with examples.

**Where it sits:** lesson 10 of 35, in part 3 (network diagrams).

**Source:** the author's own SSG 513 study notes, section 3.
