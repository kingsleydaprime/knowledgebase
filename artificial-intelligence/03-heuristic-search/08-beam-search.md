---
id: fa65f351-e152-4ece-9a40-c5c8735b4e73
---

# Beam Search

Beam search explores level by level like breadth-first search, but at each level it keeps only the $k$ most promising states, judged by a heuristic, and throws the rest away.

## Before you start
<!-- bite: bb45e260-5918-40bf-bcf3-cddaf48bc196 -->

Read [[artificial-intelligence/03-heuristic-search/07-hill-climbing|Hill Climbing]] and [[artificial-intelligence/02-uninformed-search/03-breadth-first-search|Breadth-First Search]] first. Beam search sits between them.

After this lesson you will be able to:

1. explain how beam search works and what the beam width $k$ controls;
2. trace beam search by hand on the map with $k = 1$ and $k = 2$;
3. describe local beam search, the local-search version;
4. explain why beam search is neither complete nor optimal, and when it's still the right tool.

## What beam search is
<!-- bite: 053bcb56-0960-4d03-ad1d-b6b92fe58111 -->

Hill climbing kept just one state. Breadth-first search kept every state on the next level. One uses too little memory to be safe; the other uses too much to be practical.

Beam search picks a number in between. Like BFS, it goes level by level. But when it has generated all the states on the next level, it sorts them by the heuristic and keeps only the best $k$. The rest are dropped for good. The number $k$ is called the **beam width**.

The name comes from a torch beam: you only light up a narrow strip of the search space, the strip that looks most promising.

## The kid version
<!-- bite: 865dd191-01dd-4b71-b737-c65896478042 -->

A football coach has 40 children at trials and room for 2 at each stage. After the first drill, the coach keeps the 2 best and sends the rest home. Those 2 bring friends to the next drill, and again only the best 2 go through. Each stage keeps the field small and focuses on the most promising players.

**Where the analogy stops working.** A child sent home after the first drill might have become the best player of all with a bit more time. Beam search has the same problem: a state that looks weak early might lead to the best solution, and once it's dropped, it's gone.

## Beam search on the map, k = 2
<!-- bite: 322c1c6a-563f-4bd6-b48d-18904c96f10b -->

Use the straight-line distances to Abuja (Lagos 525, Ibadan 450, Benin 370, Akure 360, Ilorin 300, Lokoja 165, Abuja 0) and beam width $k = 2$. At each level, generate every new neighbour of the kept states, sort by $h$, and keep the best two.

**Level 1.** From Lagos: Benin (370) and Ibadan (450). Two states, so keep both.

**Level 2.** From Benin: Akure (360), Lokoja (165). From Ibadan: Akure (already listed), Ilorin (300). Candidates sorted by $h$: Lokoja 165, Ilorin 300, Akure 360. Keep **Lokoja** and **Ilorin**; drop Akure.

**Level 3.** From Lokoja: Abuja (0), Akure (360). From Ilorin: Abuja (already listed). Keep **Abuja** and Akure. Abuja is the goal. Stop.

The route is Lagos → Benin → Lokoja → Abuja, **830 km**.

## What got dropped
<!-- bite: 720b6f89-a23e-4acf-8fa9-270ee46aa382 -->

Look at level 2 again. Akure was dropped because its straight-line distance, 360, was the worst of the three. But the 790 km route goes Lagos → Ibadan → Akure → Lokoja → Abuja. When beam search dropped Akure-via-Ibadan, it threw away the best route.

That's the cost of a narrow beam. Beam search judges states only by the heuristic and only at their own level, and anything outside the beam is gone forever.

## Changing the beam width
<!-- bite: 5223b9ab-4150-436d-b376-bfc17e16dfdd -->

The beam width is a dial between other methods you already know:

1. **$k = 1$:** keep only the single best state at each level. On the map: Lagos → Benin (370 beats 450) → Lokoja (165 beats 360) → Abuja. That's just greedy search with no backing up, the same as hill climbing on $h$.
2. **$k = 2$:** the trace above. A bit more room, same answer here.
3. **$k$ unlimited:** keep everything at each level. That's breadth-first search.

A wider beam is more likely to keep the path to a good solution, but uses more memory and time. A narrower beam is cheaper but riskier.

## Local beam search
<!-- bite: 8c40f62f-2f23-4778-a059-54d3e6cb464f -->

Beam search also has a local-search version, which your slides list with hill climbing: **local beam search**. It keeps $k$ states instead of one, and at each step:

1. Generate all the neighbours of all $k$ states.
2. If any is a goal, stop.
3. Otherwise, keep the best $k$ of all those neighbours, and repeat.

It isn't the same as running $k$ separate hill climbs. Your slides point out that it shares information among the states: if one state has excellent neighbours and the others don't, most of the next $k$ states come from that good region. The search quickly moves its effort to where things look best.

The danger is the same as before: all $k$ states can end up crowded into one small region, around one local maximum. A variant called **stochastic beam search** picks the $k$ states at random, favouring better ones, to keep some variety.

## How good is beam search?
<!-- bite: 30a9fec8-9190-43ed-8bee-9d07b66f3828 -->

1. **Complete?** No. The path to the only solution might be dropped.
2. **Optimal?** No. On our map it drops the 790 km route.
3. **Time:** about $O(kbd)$: $d$ levels, each generating up to $k \times b$ candidates.
4. **Space:** about $O(kb)$ per level, small and fixed, set by the beam width.

Beam search is widely used where search spaces are vast and a good answer is enough, such as speech recognition and machine translation, which keep a beam of the most likely partial sentences at each word.

## Terms used in this lesson
<!-- bite: 9533fc4b-7c4d-4986-9df4-a78c94c472f3 -->

1. **Beam search**: This is a level-by-level search that keeps only the $k$ best states at each level, judged by a heuristic.
2. **Beam width ($k$)**: This is the number of states beam search keeps at each level.
3. **Local beam search**: This is local search that keeps $k$ current states and, at each step, replaces them with the best $k$ of all their neighbours.
4. **Stochastic beam search**: This is local beam search that chooses the $k$ states at random, weighted toward the better ones, to keep variety.

## Common pitfalls and traps
<!-- bite: 7be2fddf-8863-49bb-a5ff-f6fe9db9f100 -->

- **Thinking local beam search is $k$ hill climbs.** The $k$ states share one pool of neighbours, so good regions attract more of the beam.
- **Forgetting that dropped states are gone for good.** Beam search never backs up to a dropped state, which is why it can miss the solution.
- **Mixing up beam width and depth.** $k$ is how many states are kept per level, not how deep the search goes.

## Check your understanding
<!-- bite: fdf29ef4-6741-4a6c-895e-012e979bd13b -->

Try each one before you open the answer.

1. <!-- q: mcq id="f56fe932" -->
   Beam search with an unlimited beam width behaves like which method?

   - [x] Breadth-first search
   - [ ] Depth-first search
   - [ ] A\* search
   - [ ] Hill climbing

   <details><summary>Answer</summary>

   Breadth-first search: it keeps every state at every level. With $k = 1$ it behaves like greedy hill climbing.

   </details>

2. <!-- q: mcq id="3c33fe2d" -->
   Beam search with $k = 2$ has these candidates at one level, with heuristic values (lower is better): P 40, Q 15, R 60, S 22. Which states does it keep?

   - [ ] P and R
   - [x] Q and S
   - [ ] P and Q
   - [ ] All four

   <details><summary>Answer</summary>

   Q (15) and S (22), the two lowest heuristic values. P and R are dropped.

   </details>

3. <!-- q: open id="b34da253" -->
   On the Lagos-to-Abuja map with $k = 2$, beam search returns 830 km, not the best 790 km. At which level, and why, did it lose the best route?

   <details><summary>Answer</summary>

   At level 2. The candidates were Lokoja (165), Ilorin (300) and Akure (360), and only the best two by heuristic were kept, so Akure was dropped. The 790 km route runs Lagos → Ibadan → Akure → Lokoja → Abuja, so dropping Akure-via-Ibadan threw it away, and beam search never comes back to dropped states.

   </details>

4. <!-- q: gap id="3e24dc35" answers="k|beam width" -->
   The number of states beam search keeps at each level is called the beam width, written ___.

   <details><summary>Answer</summary>

   $k$, the beam width.

   </details>

5. <!-- q: open id="34acb184" -->
   How is local beam search with $k$ states different from running $k$ hill climbs separately?

   <details><summary>Answer</summary>

   Separate hill climbs never share anything: each just follows its own best neighbour. Local beam search pools all the neighbours of all $k$ states and keeps the best $k$ overall, so if one state has much better neighbours, most of the next states come from there. Effort moves to the most promising region.

   </details>

## Before moving on
<!-- bite: 73f421b1-db25-4a6f-bc7c-435cbc4d6f53 -->

You're done when you can trace beam search on a map with a given $k$, say what $k = 1$ and an unlimited $k$ turn it into, explain local beam search, and point to where beam search drops a good route.

Recap: beam search goes level by level and keeps only the best $k$ states by heuristic. $k = 1$ is greedy hill climbing; unlimited $k$ is BFS. Its memory is small and fixed, but it's neither complete nor optimal: on our map, $k = 2$ drops Akure at level 2 and returns 830 km. Local beam search keeps $k$ current states and pools their neighbours.

Next, [[artificial-intelligence/03-heuristic-search/09-simulated-annealing|Simulated Annealing]] escapes local maxima a different way: by sometimes taking a step downhill on purpose.

## Related
<!-- bite: f64af2d3-044a-4727-905f-6375d9a925ba -->

- [[artificial-intelligence/03-heuristic-search/03-greedy-best-first-search|Greedy Best-First Search]]: beam search with $k = 1$ follows the same choices.

## About this lesson
<!-- bite: 2e375301-4f4e-4107-b73f-6c28d45ae3ae -->

**Level:** introductory. Lesson 8 of section 03 (heuristic search). It covers beam search, the beam width, traces on the map with $k = 1$ and $k = 2$, local beam search, and its properties.

**Source:** University of Lagos SSG 518 class notes (beam search in the list of informed algorithms, 23/11/25) and the SSG 518 *Introduction to Search* slides (*Local Search and Optimisation*: "local beam search keeps the $k$ best states at each step instead of one, and shares information among them"). Both traces are computed and asserted by `scripts/diagrams/ai_heuristic.py`.
