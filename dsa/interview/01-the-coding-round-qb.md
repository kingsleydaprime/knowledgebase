# The Coding Round — Question Bank

Micro-questions over [[01-the-coding-round|the coding round module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

This one is about **method**, so answering it out loud is the point twice over.

---

## A. The method

**1. What are the seven steps?**

<details><summary>Answer</summary>

1. Restate and clarify. 2. Work a small example by hand. 3. State the brute force and its complexity out loud. 4. Optimise, saying what you are trading. 5. Get agreement before coding. 6. Code, narrating, then trace your own code. 7. State complexity and check edge cases unprompted.

</details>

**2. How long does step 1 take, and on which problems?**

<details><summary>Answer</summary>

**Two minutes, always** — including easy ones.

</details>

**3. Which clarifying questions actually change the answer?**

<details><summary>Answer</summary>

**Input size** (decides whether $O(n^2)$ is acceptable — $n \le 1000$ means it probably is); sorted? duplicates? negatives? empty? nulls?; can I mutate the input, is there extra memory?; exactly one valid answer or several?

</details>

**4. Why is clarifying not a formality?**

<details><summary>Answer</summary>

**It buys thinking time, prevents solving the wrong problem, and demonstrates the exact behaviour they want on a real team.**

</details>

**5. What does working a small example by hand give you?**

<details><summary>Answer</summary>

**Half the time the pattern falls out of doing it** — and it gives you test data for step 6 for free.

</details>

**6. Why state the brute force out loud?**

<details><summary>Answer</summary>

**It guarantees you have *something*, and it frames the optimisation as deliberate rather than lucky.**

</details>

---

## B. The optimisation moves

**7. Name the six moves.**

<details><summary>Answer</summary>

**Hash map** (space for time); **sort first** (pay $n\log n$ to unlock two pointers or a sweep); **two pointers / sliding window** (exploit sortedness or contiguity); **precompute** (prefix sums, suffix maxima); **memoise** (kill overlapping subproblems); **the right data structure** (heap for top-K, monotonic stack for next-greater, union-find for connectivity).

</details>

**8. Which is the single most common move?**

<details><summary>Answer</summary>

**The hash map** — turning an $O(n)$ scan into an $O(1)$ lookup.

</details>

**9. What should you say at step 5, and why does it matter?**

<details><summary>Answer</summary>

Something like *"So: sort, then two pointers, $O(n\log n)$ time, $O(1)$ extra space. Shall I code that?"* — **because if your approach is wrong, this is where a good interviewer redirects you**, rather than after twenty minutes of typing.

</details>

**10. What must you do before saying you are done?**

<details><summary>Answer</summary>

**Trace your own code on the example from step 2, out loud.** Finding your own bug is a strong positive signal; being told about it is not.

</details>

**11. Which edge cases do you check unprompted?**

<details><summary>Answer</summary>

**Empty, single element, all identical, overflow, the maximum size.**

</details>

---

## C. What gets people rejected

**12. What is the number-one rejection cause?**

<details><summary>Answer</summary>

**Silence.** Eight quiet minutes reads as being stuck even if you are thinking productively.

</details>

**13. What do you do instead?**

<details><summary>Answer</summary>

**Narrate** — *"I'm considering whether sorting helps here… it would cost $n\log n$ but then I could use two pointers…"*

</details>

**14. What does coding immediately signal?**

<details><summary>Answer</summary>

**Someone who would start building before understanding a requirement.**

</details>

**15. What is the right attitude to a hint?**

<details><summary>Answer</summary>

**Hints are the interviewer trying to *pass* you.** Take them visibly and gratefully.

</details>

**16. Name the two complexity claims people most often get wrong.**

<details><summary>Answer</summary>

**Forgetting the sort they called is $O(n\log n)$**, and **forgetting that string concatenation in a loop is $O(n^2)$**.

</details>

**17. What is "optimising the wrong thing"?**

<details><summary>Answer</summary>

**Micro-optimising an $O(n^2)$ solution instead of finding the $O(n)$ one.**

</details>

---

## D. Complexity talk that sounds senior

**18. Explain amortised properly.**

<details><summary>Answer</summary>

`ArrayList.add` is amortised $O(1)$ — **most appends are $O(1)$, a resize is $O(n)$, and averaged over $n$ appends it is constant.** Say "amortised" and mean it.

</details>

**19. What does space include that people forget?**

<details><summary>Answer</summary>

**The call stack.** A recursive solution on a skewed tree is $O(n)$ space, not $O(1)$.

</details>

**20. Give the mechanical-sympathy remark.**

<details><summary>Answer</summary>

**`ArrayList` beats `LinkedList` for middle insertion at realistic sizes, because contiguous memory is cache-friendly** — Big-O hides constants, and constants can decide the answer.

</details>

**21. Give the input-size table.**

<details><summary>Answer</summary>

$n \le 10$ → exponential/backtracking fine; $n \le 1000$ → $O(n^2)$; $n \le 10^6$ → $O(n\log n)$; $n \le 10^8$ → $O(n)$ only.

</details>

**22. Why is that table "the closest thing to a cheat code"?**

<details><summary>Answer</summary>

**Reading the constraints tells you the intended complexity, which tells you the intended approach.**

</details>

---

## E. Things worth knowing cold

**23. Hash map complexity, average and worst?**

<details><summary>Answer</summary>

$O(1)$ average, **$O(n)$ worst case** when all keys collide. In Java, treeified buckets make it $O(\log n)$ instead.

</details>

**24. Heap costs, and the top-K consequence?**

<details><summary>Answer</summary>

$O(\log n)$ insert/extract, $O(1)$ peek. **"Top K" is a heap of size K — $O(n\log K)$ rather than $O(n\log n)$ for a full sort.**

</details>

**25. What mistake do "a stunning number of people" make?**

<details><summary>Answer</summary>

**Reaching for DFS on a shortest-path problem.** BFS finds shortest paths in unweighted graphs; DFS does not.

</details>

**26. Dijkstra and negative edges?**

<details><summary>Answer</summary>

**Dijkstra fails** — Bellman–Ford handles them.

</details>

**27. What must you get right in binary search, and what is secondary?**

<details><summary>Answer</summary>

**The invariant** — not the mid calculation. Decide whether your loop is `while (lo < hi)` or `while (lo <= hi)` and keep the invariant consistent. (Still use `lo + (hi - lo) / 2` to avoid overflow.)

</details>

**28. When does the comparison sorting lower bound not apply?**

<details><summary>Answer</summary>

**When you are not comparing** — counting and radix sort, $O(n)$ with bounded integer keys. **Knowing when the bound does not apply is a nice card to have.**

</details>

---

## F. Practice that works

**29. What is the re-solve rule?**

<details><summary>Answer</summary>

**Solve, then re-solve from scratch three days later.** Recognition is not recall — **if you cannot reproduce it cold, you did not learn it.**

</details>

**30. How should you practise, physically?**

<details><summary>Answer</summary>

**Out loud, standing up, on a timer.** Interviews are a performance under time pressure; practising silently at your own pace trains the wrong skill.

</details>

**31. What one line do you write after each problem?**

<details><summary>Answer</summary>

**What was the *signal* that pointed at this pattern?** That line is what transfers to a problem you have not seen — **the solution itself does not transfer.**

</details>

**32. Breadth or depth?**

<details><summary>Answer</summary>

**Breadth of pattern over depth of problem count.** Fifteen patterns well understood beats three hundred problems half-remembered.

</details>

**33. Summarise the module in one sentence.**

<details><summary>Answer</summary>

Clarify, example, brute force, optimise out loud, agree, code narrating, test yourself — and practise recall standing up on a timer, not recognition at your desk.

</details>

---

## Scorecard

| Pass | Date | Got it | Close | Blank | Questions missed |
| :--- | :--- | :----- | :---- | :---- | :--------------- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Related

- [[01-the-coding-round|The Coding Round]] — the module
- [[dsa/04-patterns/index|The patterns folder]] — the breadth this note argues for
- [[dsa/03-algorithms/01-complexity-analysis/01-growth-and-asymptotic-notation-qb|Growth & Asymptotics — Question Bank]]
