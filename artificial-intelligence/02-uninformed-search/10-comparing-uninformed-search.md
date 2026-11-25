---
id: e8ddad3e-efad-4791-8c70-0f0f98897de5
---

# Comparing Uninformed Search Methods

The six uninformed search methods differ only in which node they expand next, and that one choice decides everything else.

## Before you start
<!-- bite: 2e29daec-22cf-42c6-88c4-20a505925456 -->

Read the six method lessons first, from [[artificial-intelligence/02-uninformed-search/03-breadth-first-search|Breadth-First Search]] to [[artificial-intelligence/02-uninformed-search/09-bidirectional-search|Bidirectional Search]]. This lesson puts them side by side.

After this lesson you will be able to:

1. fill in the comparison table of all six methods from memory: complete, optimal, time and space;
2. say which route each method returns on the Lagos-to-Abuja map, and why;
3. choose the right uninformed method for a described problem, and justify it.

## What this lesson does
<!-- bite: 5ab9a86c-5b99-4b1a-907c-104ab5609888 -->

You now have six methods, and each one answered the question "which node next?" differently. That's a lot to keep straight in an exam. This lesson is the summary page: one table of properties, one table of results on our map, and a set of rules for choosing.

There's nothing new to learn here, only things to connect. If any row of the table surprises you, go back to that method's lesson.

## The kid version
<!-- bite: 71c43cda-9132-4481-ad3a-74b3baf73487 -->

Think of six friends looking for the same shop in a market. One checks every stall in the first row, then the second row (BFS). One walks straight down the first aisle to the end before trying another (DFS). One does the same but never goes past the tenth stall (depth-limited). One checks to the first stall, comes back, then to the second, and so on, further each time (iterative deepening). One always walks to whichever stall is cheapest to reach next (uniform-cost). And two start from opposite ends and meet in the middle (bidirectional). They all find the shop eventually, mostly. They differ in how far they walk and how much they have to remember.

**Where the analogy stops working.** A market is small enough that any of them finds the shop. In real search problems, the difference between $O(b^d)$ and $O(bd)$ memory decides whether the method finishes at all.

## The comparison table
<!-- bite: 83dc7d04-9482-49cb-9676-c0d9e5954d37 -->

Here are all six, as in your course slides. $b$ is the branching factor, $d$ the depth of the shallowest goal, $m$ the maximum depth, $\ell$ the depth limit, $C^*$ the optimal cost and $\varepsilon$ the smallest step cost.

| Method | Complete? | Optimal? | Time | Space |
|---|---|---|---|---|
| Breadth-first | Yes, if $b$ finite | If step costs equal | $O(b^d)$ | $O(b^d)$ |
| Uniform-cost | Yes, if costs > 0 | Yes | $O(b^{1+C^*/\varepsilon})$ | $O(b^{1+C^*/\varepsilon})$ |
| Depth-first | No | No | $O(b^m)$ | $O(bm)$ |
| Depth-limited | No, if $\ell < d$ | No | $O(b^\ell)$ | $O(b\ell)$ |
| Iterative deepening | Yes | If step costs equal | $O(b^d)$ | $O(bd)$ |
| Bidirectional | Yes | If step costs equal | $O(b^{d/2})$ | $O(b^{d/2})$ |

## Reading the table
<!-- bite: 6c536380-2892-45b0-aa45-748a01cd7577 -->

Look down the columns and patterns appear:

1. **The space column splits the methods in two.** BFS, UCS and bidirectional search need exponential memory. DFS, DLS and IDS need only linear memory. That's the biggest practical difference.
2. **Only UCS is optimal when costs differ.** BFS, IDS and bidirectional search are optimal only when every step costs the same, because they find the fewest steps.
3. **Only IDS has everything for equal costs:** complete, optimal, and linear memory. That's why it's the default blind search.
4. **DFS and DLS give up guarantees for memory.** Neither is optimal, and both can miss a solution.

## The six methods on our map
<!-- bite: fb58e95d-23a8-43f2-a9b9-a1d29715e99b -->

Here's what each method returned for Lagos to Abuja:

| Method | Route | Roads | km |
|---|---|---|---|
| Breadth-first | Lagos → Benin → Lokoja → Abuja | 3 | 830 |
| Depth-first | Lagos → Benin → Akure → Ibadan → Ilorin → Abuja | 5 | 1,385 |
| Depth-limited ($\ell = 3$) | Lagos → Benin → Lokoja → Abuja | 3 | 830 |
| Iterative deepening | Lagos → Benin → Lokoja → Abuja | 3 | 830 |
| Uniform-cost | Lagos → Ibadan → Akure → Lokoja → Abuja | 4 | 790 |
| Bidirectional | Lagos → Benin → Lokoja → Abuja | 3 | 830 |

The table matches the properties exactly. The four methods that find the fewest steps all return a 3-road route. Only uniform-cost search, the one method that counts kilometres, finds the 790 km route. And DFS returns whatever it stumbled on first.

## Choosing a method
<!-- bite: a2be2e4c-6752-4814-b4b4-1401432a681d -->

Your slides give a "choosing a search method" table. Here it is as rules:

1. **Equal step costs, you need the fewest steps, and memory is available:** breadth-first search. It finds the shallowest solution.
2. **A very large space, tight memory, and any solution will do:** depth-first search, or iterative deepening. Both use little memory.
3. **Step costs differ and there's no good heuristic:** uniform-cost search. It guarantees the cheapest path.
4. **The space is large and the solution's depth is unknown:** iterative deepening. It's the usual blind-search choice.
5. **You know how deep the solution is:** depth-limited search, with the limit set to that depth.
6. **One clear goal state and reversible actions:** bidirectional search, for the $b^{d/2}$ saving.

## Beyond blind search
<!-- bite: 5776c79e-8a02-4dc0-a409-2a2fce250904 -->

The slides' table goes on to "a good admissible heuristic is available: A\*" and "speed matters more than the best answer: greedy best-first search". Those are informed methods, and they're the next section.

## What all six have in common
<!-- bite: 8b85ff7e-6987-483e-9b55-163add858b88 -->

Every method in this section is blind: none of them knows which direction the goal is in. Even UCS, the best of them for our map, spread out from Lagos toward Ilorin and Benin before it settled on the route through Akure, just because those cities were cheap to reach, not because they were heading toward Abuja.

If you looked at the map, you'd never do that. You can *see* Abuja is to the north-east, so you'd favour cities in that direction. Giving the search that kind of hint, an estimate of how far each city is from the goal, is what informed search does. With a good hint, A\* finds the same 790 km route as UCS while expanding fewer cities.

## Terms used in this lesson
<!-- bite: 2ccea99c-07ed-461e-8877-34162c66740e -->

1. **Uninformed search**: This is also known as **blind search**. It's search that uses only the problem definition, with no estimate of how close a state is to the goal. All six methods here are uninformed.
2. **Informed search**: This is also known as **heuristic search**. It's search that uses an estimate of the distance to the goal to decide what to expand. It's the subject of section 03.

## Common pitfalls and traps
<!-- bite: 17f9b283-dddc-4063-a906-0f1d713e951d -->

- **Saying IDS is optimal without the condition.** IDS is optimal only when all step costs are equal. On our map it returns 830 km.
- **Mixing up DFS's time and space.** Time $O(b^m)$, space $O(bm)$.
- **Choosing BFS for a big problem because it's "complete and optimal".** Its $O(b^d)$ memory can make it fail in practice. If memory is tight, IDS gives the same guarantees.

## Check your understanding
<!-- bite: 922e1789-b44a-423d-9d7d-e7d09e0416c6 -->

Try each one before you open the answer.

1. <!-- q: mcq id="f6f0af2b" -->
   Which uninformed methods need only linear memory? (choose all that apply)

   - [ ] Breadth-first search
   - [x] Depth-first search
   - [x] Depth-limited search
   - [x] Iterative deepening search
   - [ ] Uniform-cost search
   - [ ] Bidirectional search

   <details><summary>Answer</summary>

   DFS ($O(bm)$), DLS ($O(b\ell)$) and IDS ($O(bd)$). BFS, UCS and bidirectional search need exponential memory.

   </details>

2. <!-- q: mcq id="8ed77e95" -->
   Road lengths differ, there's no heuristic, and you must find the cheapest route. Which method should you use?

   - [ ] Breadth-first search
   - [ ] Iterative deepening search
   - [x] Uniform-cost search
   - [ ] Depth-first search

   <details><summary>Answer</summary>

   Uniform-cost search: it's the only uninformed method that's optimal when step costs differ.

   </details>

3. <!-- q: mcq id="21838f1b" -->
   A puzzle has a huge state space, every move costs 1, memory is limited, and you have no idea how many moves the solution needs. Which method fits best?

   - [ ] Breadth-first search
   - [ ] Depth-limited search with limit 10
   - [x] Iterative deepening search
   - [ ] Bidirectional search, even though the goal is "any solved arrangement"

   <details><summary>Answer</summary>

   Iterative deepening. It's complete, optimal for equal costs, and uses only linear memory, and it doesn't need the depth in advance. BFS would run out of memory; DLS needs the right limit; bidirectional search needs a single goal state.

   </details>

4. <!-- q: gap id="da4c38e1" answers="b^m|O(b^m);bm|O(bm)" -->
   Depth-first search takes time $O($___$)$ and space $O($___$)$.

   <details><summary>Answer</summary>

   Time $b^m$, space $bm$. The time is exponential in the maximum depth, but the memory is linear.

   </details>

5. <!-- q: open id="2f19ff66" -->
   On the Lagos-to-Abuja map, four methods return the same 830 km route and only uniform-cost search returns 790 km. Explain why, using the methods' properties.

   <details><summary>Answer</summary>

   BFS, depth-limited search with limit 3, iterative deepening and bidirectional search (with BFS halves) all find the solution with the fewest steps, which is optimal only when every step costs the same. The fewest-roads routes have 3 roads, and the one they reach first is 830 km. The roads have different lengths, so the fewest roads isn't the fewest kilometres. Uniform-cost search expands by total cost, so it finds the 790 km route, which has 4 roads.

   </details>

6. <!-- q: mcq id="d20a91ba" -->
   Which method is complete, optimal when step costs are equal, and uses linear memory?

   - [ ] Breadth-first search
   - [ ] Depth-first search
   - [x] Iterative deepening search
   - [ ] Uniform-cost search

   <details><summary>Answer</summary>

   Iterative deepening. BFS has the same guarantees but needs exponential memory; DFS has linear memory but neither guarantee; UCS needs exponential memory.

   </details>

## Before moving on
<!-- bite: da2a35a2-e7d2-4c28-b311-824c6436d10b -->

You're done when you can fill in the comparison table from memory, explain each method's route on the map from its properties, and pick and justify a method for a new problem.

Recap: BFS, IDS and bidirectional search find the fewest steps; UCS finds the lowest cost; DFS and DLS find whatever comes first. BFS, UCS and bidirectional search need exponential memory; DFS, DLS and IDS need linear memory. IDS is the default blind search; UCS is the choice when costs differ. All six are blind to where the goal is.

That's the end of section 02. Section 03 of the [[artificial-intelligence/index|Artificial Intelligence]] subject is heuristic search: giving the search an estimate of the distance to the goal, starting with greedy best-first search and A\*.

## Related
<!-- bite: ab68e39f-d37f-4f03-a5d5-e6bd72ea0b37 -->

- [[artificial-intelligence/02-uninformed-search/02-measuring-a-search-method|Measuring a Search Method]]: what the four columns mean.

## About this lesson
<!-- bite: 89b1b81b-c26d-4b09-8b13-b0f9fe2c6edc -->

**Level:** introductory. Lesson 10 of section 02 (uninformed search). It compares the six uninformed methods on completeness, optimality, time and space, collects their results on the map, and gives rules for choosing one.

**Source:** University of Lagos SSG 518 *Introduction to Search* slides (*Uninformed (Blind) Search Methods* table and *Choosing a Search Method* table). Every route and cost in the map table is computed and asserted by `scripts/diagrams/ai_search.py`.
