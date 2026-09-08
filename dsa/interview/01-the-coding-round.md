# DSA Interview — The Coding Round

From [[foundations/dsa/README|the DSA course]]. **This note is about method, not problems.** The problems are in [[foundations/dsa/neetcode-150/interview-playbook|the NeetCode playbook]]; what most people are actually missing is the process around them.

---

## The method (use it on every problem, including easy ones)

**1. Restate and clarify — 2 minutes, always.**
Say the problem back in your own words. Then ask about the things that change the answer:
- Input size? (Decides whether O(n²) is acceptable — n ≤ 1000 means it probably is.)
- Sorted? Duplicates? Negatives? Empty? Nulls?
- Can I mutate the input? Is there extra memory available?
- Is there exactly one valid answer, or several?

**Not a formality.** It buys thinking time, prevents solving the wrong problem, and demonstrates the exact behaviour they want on a real team.

**2. Work a small example by hand.** On the whiteboard/screen. Half the time the pattern falls out of doing this, and it gives you test data for step 6 for free.

**3. State the brute force, and its complexity, out loud.** *"The naive approach is check every pair — O(n²). Let me see if I can do better."* This guarantees you have *something*, and it frames the optimisation as deliberate rather than lucky.

**4. Optimise, and say what you're trading.** Almost every optimisation is one of a small set of moves:
- **Hash map** — trade space for time, turning an O(n) scan into O(1) lookup. The single most common move.
- **Sort first** — pay O(n log n) to unlock two pointers or a sweep.
- **Two pointers / sliding window** — exploit sortedness or contiguity to avoid rescanning.
- **Precompute** — prefix sums, suffix maxima.
- **Memoise** — kill overlapping subproblems.
- **The right data structure** — heap for "top K", monotonic stack for "next greater", union-find for connectivity.

**5. Get agreement before you code.** *"So: sort, then two pointers, O(n log n) time, O(1) extra space. Shall I code that?"* If your approach is wrong, this is where a good interviewer redirects you — do not discover that after twenty minutes of typing.

**6. Code, narrating as you go.** Then **trace your own code on the example from step 2, out loud**, before saying you're done. Finding your own bug is a strong positive signal. Being told about it by the interviewer is not.

**7. State the complexity, and check edge cases** unprompted: empty, single element, all identical, overflow, the maximum size.

---

## What actually gets people rejected

Ranked by how often it happens, not by severity:

1. **Silence.** Eight quiet minutes reads as being stuck even if you're thinking productively. Narrate. *"I'm considering whether sorting helps here… it would cost n log n but then I could use two pointers…"*
2. **Coding immediately.** Signals someone who'd start building before understanding a requirement.
3. **Not testing.** Declaring "done" and having the interviewer find the off-by-one.
4. **Optimising the wrong thing.** Micro-optimising an O(n²) solution instead of finding the O(n) one.
5. **Defensiveness on a hint.** Hints are the interviewer trying to *pass* you. Take them visibly and gratefully.
6. **Claiming a complexity you haven't checked.** Especially forgetting that the sort you called is O(n log n), or that string concatenation in a loop is O(n²).

---

## Complexity talk that sounds senior

- **Amortised vs worst case.** `ArrayList.add` is amortised O(1) — most appends are O(1), a resize is O(n), averaged over n appends it's constant. Say "amortised" and mean it.
- **Space includes the call stack.** A recursive solution on a skewed tree is O(n) space, not O(1). This gets missed constantly.
- **Big-O hides constants, and constants can decide the answer.** [[languages/01-java/interview/01-language-and-collections|`ArrayList` beats `LinkedList`]] for middle insertion at realistic sizes because contiguous memory is cache-friendly. Saying this signals mechanical sympathy — it's a genuinely differentiating remark in a coding round.
- **Know the input size that makes each complexity viable:** n ≤ 10 → exponential/backtracking is fine; n ≤ 1000 → O(n²); n ≤ 10⁶ → O(n log n); n ≤ 10⁸ → O(n) only. Reading the constraints tells you the intended complexity, which tells you the intended approach. **This is the closest thing to a cheat code in competitive-style interviews.**

---

## Things worth knowing cold

Not to recite — to *use* without slowing down:

- **Hash map operations are O(1) average, O(n) worst case** (all keys colliding). In Java, treeified buckets make it O(log n) instead. → [[languages/01-java/interview/01-language-and-collections|HashMap internals]]
- **A heap gives you O(log n) insert/extract and O(1) peek.** "Top K" = a heap of size K, giving O(n log K) rather than O(n log n) for a full sort.
- **BFS finds shortest paths in unweighted graphs; DFS doesn't.** A stunning number of people reach for DFS on a shortest-path problem.
- **Dijkstra fails with negative edges** — Bellman-Ford handles them.
- **Binary search's invariant is what you must get right**, not the mid calculation. Decide whether your loop is `while (lo < hi)` or `while (lo <= hi)` and keep the invariant consistent. Use `lo + (hi - lo) / 2` to avoid overflow.
- **Sorting is O(n log n) and you cannot beat it** with comparisons — unless you're not comparing (counting/radix sort, O(n) with bounded integer keys). Knowing when the comparison lower bound doesn't apply is a nice card to have.

---

## The pattern lookup

Kept in [[foundations/dsa/interview/README|the folder README]] — the table mapping "what the problem says" to "what to reach for." If you internalise one thing from this folder, make it that table plus **binary search on the answer**.

---

## Practice that actually works

- **Solve, then re-solve from scratch three days later.** Recognition is not recall. If you can't reproduce it cold, you didn't learn it.
- **Do them out loud, standing up, on a timer.** Interviews are a performance under time pressure; practising silently at your own pace trains the wrong skill.
- **After each problem, write one line: what was the *signal* that pointed at this pattern?** That line is what transfers to a problem you haven't seen. The solution itself doesn't transfer.
- **Prefer breadth of pattern over depth of problem count.** Fifteen patterns well understood beats three hundred problems half-remembered — which is why [[foundations/dsa/06-patterns/README|the patterns folder]] is structured the way it is.
