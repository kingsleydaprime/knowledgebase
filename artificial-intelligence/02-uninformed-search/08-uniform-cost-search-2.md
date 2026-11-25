---
id: 1ce9d8e7-3cef-4d44-b6ed-d48ccd9f8194
---

# Uniform-Cost Search 2: The Road Trip and When to Stop

On the Lagos-to-Abuja map, uniform-cost search finds the cheapest route, 790 km, and the trace shows why it must wait until the goal comes off the frontier before stopping.

## Before you start
<!-- bite: d3be5029-4514-47c0-8d94-24dd8d6f5e68 -->

Read [[artificial-intelligence/02-uninformed-search/07-uniform-cost-search-1|Uniform-Cost Search 1]] first. You need UCS's rule, the priority queue, and how to update a node's cost.

After this lesson you will be able to:

1. trace uniform-cost search (UCS) on the Lagos-to-Abuja map and get the 790 km route;
2. explain, using the trace, why UCS tests for the goal when a node comes off the frontier;
3. give UCS's properties, including its time and space, and its advantages and disadvantages;
4. write UCS in Python with a heap.

## What this lesson covers
<!-- bite: fde35fd5-daf3-45cf-9134-2142b9829c02 -->

In part 1 you traced UCS on the small graph from your notes. Now it's time for the real test: the road trip, where BFS returned 830 km and DFS returned 1,385 km.

The trace has one moment worth watching closely. Abuja gets onto the frontier early, at a cost that *isn't* the best. What UCS does next is the reason for its "when to stop" rule.

## The kid version
<!-- bite: 225df782-8ebc-424a-b366-b050685ba061 -->

You're comparing bus fares to Abuja. Early on, a friend says "there's a bus via Ilorin for ₦8,100." You could book it on the spot. But you still have cheaper part-routes on your list that haven't reached Abuja yet, like one that's only ₦5,900 so far at Lokoja. If you book now, you might miss a cheaper trip. So you keep extending the cheapest route on your list, and you only book Abuja when the Abuja fare is the cheapest thing left on the list.

**Where the analogy stops working.** Real fares can change while you compare. UCS assumes the costs are fixed while it searches, so once a city's cheapest cost is settled, it stays settled.

## Tracing UCS on the map, steps 1 to 3
<!-- bite: e59c2f83-5189-4139-8c0c-6f1eed5c6122 -->

Here's the map again: Lagos–Ibadan 130, Lagos–Benin 330, Ibadan–Ilorin 160, Ibadan–Akure 210, Benin–Akure 165, Benin–Lokoja 300, Ilorin–Abuja 520, Akure–Lokoja 250, Lokoja–Abuja 200.

**Step 1.** Take Lagos (0) off. Add Ibadan 130 and Benin 330.

Frontier: Ibadan 130, Benin 330.

**Step 2.** Take Ibadan (130) off. Add Ilorin 130 + 160 = 290 and Akure 130 + 210 = 340.

Frontier: Ilorin 290, Benin 330, Akure 340.

**Step 3.** Take Ilorin (290) off. Add Abuja 290 + 520 = **810**.

Frontier: Benin 330, Akure 340, Abuja 810.

Stop and look. Abuja is on the frontier. If UCS stopped here, it would return Lagos → Ibadan → Ilorin → Abuja at 810 km. Predict: is there a cheaper route still to be found?

## Tracing UCS on the map, steps 4 to 7
<!-- bite: 0c84cf0e-943d-4c98-8e0c-3923221f41d5 -->

**Step 4.** Take Benin (330) off. Akure via Benin would be 330 + 165 = 495, but Akure is already at 340, so no change. Add Lokoja 330 + 300 = 630.

Frontier: Akure 340, Lokoja 630, Abuja 810.

**Step 5.** Take Akure (340) off. Lokoja via Akure is 340 + 250 = 590, cheaper than 630, so Lokoja drops to 590 with parent Akure.

Frontier: Lokoja 590, Abuja 810.

**Step 6.** Take Lokoja (590) off. Abuja via Lokoja is 590 + 200 = **790**, cheaper than 810, so Abuja drops to 790 with parent Lokoja.

Frontier: Abuja 790.

**Step 7.** Take Abuja (790) off. It's the goal. Stop.

Follow the parents: Abuja ← Lokoja ← Akure ← Ibadan ← Lagos. The route is **Lagos → Ibadan → Akure → Lokoja → Abuja, 790 km**: the optimal route from section 01, found at last.

## Why UCS waits to stop
<!-- bite: dad4191c-b52a-4ac4-ba90-13489eb6ea0e -->

At step 3, Abuja was added at 810. At step 6, a cheaper way, 790, turned up. If UCS had tested for the goal when Abuja was *added*, it would have stopped at step 3 with the wrong answer.

That's why UCS tests for the goal when a node comes *off* the frontier. By then it's the cheapest thing waiting, and (as part 1 showed) nothing still on the frontier can lead to a cheaper path.

BFS could test early, when a node is generated, because BFS only cares about the number of steps, and a node found later can never have fewer steps. UCS cares about cost, and a node found later *can* be cheaper. Same loop, different test timing, and the timing matters.

## How good is UCS?
<!-- bite: 2e5fcb4e-8c08-4bbc-9535-295e8749fb5c -->

1. **Complete?** Yes, as long as every step costs at least some small positive amount $\varepsilon$ and $b$ is finite.
2. **Optimal?** Yes. The first goal taken off the frontier is the cheapest.
3. **Time:** $O(b^{1 + \lfloor C^*/\varepsilon \rfloor})$.
4. **Space:** the same, $O(b^{1 + \lfloor C^*/\varepsilon \rfloor})$.

Two new symbols: $C^*$ is the cost of the optimal solution (790 km for our trip), and $\varepsilon$ is the smallest step cost (130 km here). $C^*/\varepsilon$ is roughly "how many of the cheapest steps would it take to reach the optimal cost", which plays the role that $d$ played for BFS. If many steps are very cheap, $C^*/\varepsilon$ is large and UCS explores a lot.

When every step costs the same, UCS expands nodes in the same order as BFS: cheapest first and shallowest first become the same thing.

## Advantages and disadvantages
<!-- bite: 9bbc8bd6-5892-4f85-b863-c2a71091c15b -->

From your notes:

**Advantages:**

1. It finds the cheapest path: the optimal, minimum-cost solution.
2. It works even when costs differ. BFS assumes all edges have equal cost.

**Disadvantages:**

1. It can be slow, because it explores many possible paths to make sure of optimality. Your slides add that it can expand many cheap but useless nodes.
2. It needs more memory, because it stores many options in the priority queue. It is not memory efficient.

That first disadvantage is the important one. UCS spreads out evenly by cost in every direction, including directions that lead away from Abuja. It has no idea where Abuja *is*. Section 03 fixes that by giving the search a hint about direction.

## UCS in Python
<!-- bite: b7544203-62a4-4d31-8065-eaea203a35de -->

Python's `heapq` module is a ready-made priority queue. Save this as `ucs.py` and run `python3 ucs.py`.

```python
import heapq

ROADS = {("Lagos", "Ibadan"): 130, ("Lagos", "Benin"): 330, ("Ibadan", "Ilorin"): 160,
         ("Ibadan", "Akure"): 210, ("Benin", "Akure"): 165, ("Benin", "Lokoja"): 300,
         ("Ilorin", "Abuja"): 520, ("Akure", "Lokoja"): 250, ("Lokoja", "Abuja"): 200}

def neighbours(city):
    out = [(b, d) for (a, b), d in ROADS.items() if a == city]
    out += [(a, d) for (a, b), d in ROADS.items() if b == city]
    return sorted(out)

def ucs(start, goal):
    best = {start: 0}                         # cheapest known cost to each city
    parent = {start: None}
    frontier = [(0, start)]                   # a heap of (cost, city): cheapest on top
    while frontier:
        cost, city = heapq.heappop(frontier)
        if cost > best[city]:
            continue                          # a stale, dearer copy: skip it
        print(f"expand {city} at {cost}")
        if city == goal:                      # goal test when taken OFF the frontier
            path = [city]
            while parent[path[-1]]:
                path.append(parent[path[-1]])
            return path[::-1], cost
        for nxt, km in neighbours(city):
            new = cost + km
            if new < best.get(nxt, float("inf")):
                best[nxt], parent[nxt] = new, city
                heapq.heappush(frontier, (new, nxt))
    return None, None

route, km = ucs("Lagos", "Abuja")
print(" -> ".join(route), f"({km} km)")
```

## UCS in Python: what it prints
<!-- bite: 10d9926d-b8ee-49cc-9ba5-be8736bb0f99 -->

Run it, and it prints:

```
expand Lagos at 0
expand Ibadan at 130
expand Ilorin at 290
expand Benin at 330
expand Akure at 340
expand Lokoja at 590
expand Abuja at 790
Lagos -> Ibadan -> Akure -> Lokoja -> Abuja (790 km)
```

Instead of finding and changing a node already in the heap, the code pushes a second, cheaper copy, and skips the dearer copy when it comes off later. That's the usual way to do it with a heap.

## Terms used in this lesson
<!-- bite: 87db5bcb-9e3f-455e-ae04-d561e6f428cd -->

1. **$C^*$**: This is the cost of the optimal solution.
2. **$\varepsilon$ (epsilon)**: This is the smallest step cost in the problem. UCS needs it to be greater than 0.
3. **Heap**: This is a tree-shaped data structure that keeps the smallest item on top, so a priority queue can take it off quickly.
4. **Stale entry**: This is an old, dearer copy of a node left in the heap after a cheaper copy was added. It's skipped when it comes off.

## Common pitfalls and traps
<!-- bite: e79fa531-3b2f-48cc-9686-6e716d6644ab -->

- **Testing for the goal on generation, as in BFS.** On our map, that returns 810 km instead of 790 km.
- **Thinking UCS knows where the goal is.** It doesn't. It spreads out by cost in every direction, which is why it's slow.
- **Forgetting the $\varepsilon > 0$ condition.** With zero-cost steps, UCS can loop forever without its cost ever rising.

## Check your understanding
<!-- bite: c88c5880-0b24-4532-be5c-635442995d72 -->

Try each one before you open the answer.

1. <!-- q: mcq id="eb403c65" -->
   On the Lagos-to-Abuja map, Abuja is first added to the frontier at 810 km, but UCS returns 790 km. Why?

   - [x] UCS tests for the goal when a node comes off the frontier, and a cheaper path to Abuja turned up before then.
   - [ ] UCS runs twice and keeps the better answer.
   - [ ] UCS always returns the route with the most roads.
   - [ ] UCS subtracts the smallest step cost at the end.

   <details><summary>Answer</summary>

   UCS waits until Abuja is the cheapest thing on the frontier. Before that happened, the path through Lokoja lowered Abuja's cost from 810 to 790.

   </details>

2. <!-- q: exact id="7b112b88" answer="12" -->
   A graph has edges with costs S–A 2, S–B 5, A–C 4, B–C 1, C–G 6, A–G 11. Uniform-cost search runs from S to goal G. What is the cost of the path it returns?

   <details><summary>Answer</summary>

   12. Pop S: A 2, B 5. Pop A (2): C 6, G 13. Pop B (5): C via B = 6, not cheaper, no change. Pop C (6): G via C = 12, cheaper than 13. Pop G (12): goal. Route S → A → C → G, cost 2 + 4 + 6 = 12.

   </details>

3. <!-- q: mcq id="8281b12c" -->
   In a problem where every action costs exactly 1, how does UCS compare with BFS?

   - [ ] UCS is never optimal, but BFS is.
   - [x] They expand nodes in the same order, because cheapest and shallowest are then the same.
   - [ ] UCS finds deeper solutions than BFS.
   - [ ] UCS uses a stack, so it behaves like DFS.

   <details><summary>Answer</summary>

   With every step costing 1, a node's cost equals its depth, so cheapest first is the same as shallowest first.

   </details>

4. <!-- q: gap id="f2db5808" answers="optimal|best|cheapest;smallest|minimum|least" -->
   In UCS's complexity $O(b^{1 + \lfloor C^*/\varepsilon \rfloor})$, $C^*$ is the cost of the ___ solution and $\varepsilon$ is the ___ step cost.

   <details><summary>Answer</summary>

   $C^*$ is the cost of the optimal solution; $\varepsilon$ is the smallest step cost.

   </details>

5. <!-- q: open id="7666e51c" -->
   Give UCS's two advantages and two disadvantages from your notes, and say which disadvantage informed search sets out to fix.

   <details><summary>Answer</summary>

   Advantages: it finds the cheapest (optimal) path, and it works when step costs differ, unlike BFS. Disadvantages: it can be slow, because it explores many paths to guarantee optimality, and it needs a lot of memory for the priority queue. Informed search targets the slowness: UCS spreads out by cost in every direction because it doesn't know where the goal is, and a heuristic gives it that sense of direction.

   </details>

## Before moving on
<!-- bite: ed367105-e22c-4211-a4e7-142922ebbbf1 -->

You're done when you can trace UCS on the map to 790 km, point to the step where testing early would have gone wrong, and state UCS's properties and pros and cons.

Recap: on the map, UCS adds Abuja at 810 km at step 3, but keeps going because cheaper paths are still waiting, and lowers it to 790 km via Lokoja at step 6. It stops only when the goal comes off the frontier. UCS is complete and optimal when every step costs more than 0, but it can be slow and memory-hungry because it searches in every direction.

Next, [[artificial-intelligence/02-uninformed-search/09-bidirectional-search|Bidirectional Search]] tries a different trick for speed: search from both ends at once and meet in the middle.

## Related
<!-- bite: 1217a7bd-74ed-4379-b83f-c0de9f1b3f32 -->

- [[dsa/02-data-structures/07-heaps|Heaps]]: how `heapq` keeps the cheapest item on top.
- [[dsa/02-data-structures/09-graphs/index|Graphs]]: Dijkstra's algorithm, UCS's close relative.

## About this lesson
<!-- bite: 6d374d8c-57f4-41c5-b311-6185be406ef9 -->

**Level:** introductory to intermediate. Lesson 8 of section 02 (uninformed search), part 2 of 2 on uniform-cost search. It covers a full UCS trace on the map, the goal test on removal, UCS's properties and complexity, its advantages and disadvantages, and its code.

**Source:** University of Lagos SSG 518 class notes, *Uniform Cost Search* (24/11/25: advantages and disadvantages), and the SSG 518 *Introduction to Search* slides (complexity with $C^*$ and $\varepsilon$, and "can expand many cheap but useless nodes"). The trace is computed and asserted by `scripts/diagrams/ai_search.py`.
