# Recursion Fundamentals — Question Bank

Micro-questions over [[01-recursion-fundamentals|the recursion fundamentals module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why recursion

**1. Why can't you count files in a nested directory tree with loops?**

<details><summary>Answer</summary>

A loop needs its nesting **fixed when you write the code**; this problem's nesting is fixed only at runtime, because you do not know how deep the directories go.

</details>

**2. State the recursive insight for that problem.**

<details><summary>Answer</summary>

The number of files in a directory is the number of loose files in it, **plus the number of files in each of its subdirectories** — the second half is the same question, asked about something smaller.

</details>

**3. When is the recursive insight available in general?**

<details><summary>Answer</summary>

Whenever a problem's answer can be phrased in terms of **the same problem on a smaller input**.

</details>

**4. What do the mirror and Russian doll analogies each get right and wrong?**

<details><summary>Answer</summary>

Both capture the **self-similarity**. Mirrors miss the **shrinking** — they recurse forever. A doll does not, because each is strictly smaller and the smallest is solid. **The shrinking is what makes recursion a technique rather than a bug.**

</details>

---

## B. The vocabulary

**5. What is a base case?**

<details><summary>Answer</summary>

An input the function answers immediately without calling itself. **A recursion with no reachable base case never terminates.**

</details>

**6. What is the recursive case?**

<details><summary>Answer</summary>

The branch that reduces the problem and calls itself — e.g. `n * factorial(n-1)`.

</details>

**7. What is progress, and why does it matter?**

<details><summary>Answer</summary>

The requirement that **every recursive call moves strictly closer to a base case**. It separates a recursion from an infinite loop, and it is the property easiest to get subtly wrong.

</details>

**8. What is a stack frame?**

<details><summary>Answer</summary>

Also an activation record — the block of memory holding one call's locals, arguments, and return address. Every call in progress has one; it is released when that call returns.

</details>

**9. What is recursion depth, and why is it a different quantity from call count?**

<details><summary>Answer</summary>

The number of frames at the deepest point — the **memory** cost. Naive Fibonacci makes **millions of calls at a depth of only $n$**.

</details>

**10. What are winding and unwinding?**

<details><summary>Answer</summary>

**Winding** is the descent, where calls are made and frames pile up. **Unwinding** is the return journey, where answers come back and frames are released. Work before the recursive call happens on the way down; work after it happens on the way up.

</details>

**11. What is a tail call?**

<details><summary>Answer</summary>

A recursive call where **nothing happens after it returns** — its result is returned directly. `return helper(n-1, acc+n)` is one; `return n * factorial(n-1)` is not, because the multiplication still has to happen.

</details>

**12. Does Python optimise tail calls?**

<details><summary>Answer</summary>

**No — deliberately.** Some languages reuse the frame and recurse in constant space; Python does not.

</details>

**13. What is memoisation?**

<details><summary>Answer</summary>

Caching the answer to each distinct subproblem the first time it is computed. **The bridge from recursion to dynamic programming.**

</details>

**14. What are overlapping subproblems?**

<details><summary>Answer</summary>

When the recursion tree contains the same subproblem many times. It is **what makes memoisation worth doing**, and its absence is why memoising merge sort achieves nothing.

</details>

---

## C. The three questions

**15. What should you *not* try to do when writing a recursion?**

<details><summary>Answer</summary>

**Picture the whole thing.** Nobody can, and the attempt is what makes recursion feel hard.

</details>

**16. State the three questions.**

<details><summary>Answer</summary>

1. What is the smallest input I can answer without thinking? → base case.
2. **Assuming the function already works for smaller inputs**, how do I build the answer for `n`? → recursive case.
3. Does every recursive call actually move toward the base case? → progress.

</details>

**17. Apply the three questions to summing a list.**

<details><summary>Answer</summary>

1. Empty list → 0.
2. First element plus the sum of the rest.
3. The rest is one shorter, and length cannot go below zero. ✓

</details>

**18. Which question requires a leap, and what is the leap?**

<details><summary>Answer</summary>

Question 2. **You are permitted to assume the recursive call returns the correct answer** — that is exactly what you are in the middle of proving.

</details>

**19. What is the three-question method actually an instance of?**

<details><summary>Answer</summary>

**Induction.** The base case is the base step, the recursive case is the inductive step, and progress guarantees you reach the base.

</details>

**20. What is wrong with `list_sum(values[1:])` as an implementation?**

<details><summary>Answer</summary>

`values[1:]` **copies the rest of the list on every call**, making it $O(n^2)$ in both time and memory. Pass an index instead.

</details>

---

## D. The call stack

**21. Trace `list_sum([3,1,4])` through both phases.**

<details><summary>Answer</summary>

Winding: frames for `[3,1,4]`, `[1,4]`, `[4]`, `[]` pile up. Unwinding: `[]` returns 0, `[4]` returns 4, `[1,4]` returns 5, `[3,1,4]` returns 8.

</details>

**22. What has happened by the end of the winding phase?**

<details><summary>Answer</summary>

**No addition at all.** Every frame is suspended mid-expression, holding its `values[0]`, waiting. The additions all happen on the way back up, in reverse order.

</details>

**23. Where does the $O(n)$ memory go, when the function stores nothing?**

<details><summary>Answer</summary>

**The pending frames *are* the storage.**

</details>

**24. State the single most useful thing to know about recursion's cost.**

<details><summary>Answer</summary>

**Its space complexity is the *depth* of the recursion, not the number of calls.**

</details>

---

## E. The three failures

**25. Failure 1 — what is it, and what happens?**

<details><summary>Answer</summary>

**No base case.** It runs until the stack is exhausted — `RecursionError` in Python.

</details>

**26. Failure 2 — why is `if n == 0` with `n - 2` nastier?**

<details><summary>Answer</summary>

**It works for half the inputs.** `evens_down(10)` is fine; `evens_down(11)` goes $11, 9, \dots, 1, -1, -3, \dots$ and never equals 0.

</details>

**27. State the general rule that fixes it.**

<details><summary>Answer</summary>

**A base case should be a condition the argument cannot jump past, not a value it must land on exactly.** Use `if n <= 0`.

</details>

**28. Failure 3 — what is wrong with `linear(100_000)`?**

<details><summary>Answer</summary>

**Nothing is wrong with the logic.** The machine simply cannot hold 100,000 frames at once.

</details>

**29. Is that a Python quirk?**

<details><summary>Answer</summary>

No — **it is a real limit everywhere.** Python merely reports it politely instead of segfaulting.

</details>

**30. Give the three responses in order of preference.**

<details><summary>Answer</summary>

1. **Rewrite it iteratively** if the recursion is linear.
2. **Restructure so the depth is $O(\log n)$** — what divide and conquer buys you.
3. **Raise the limit** with `sys.setrecursionlimit()`, only when you know the real depth is bounded. Last resort.

</details>

---

## F. The cost of a recursion

**31. How many calls does naive `fib(30)` make?**

<details><summary>Answer</summary>

**2,692,537.**

</details>

**32. Why, structurally?**

<details><summary>Answer</summary>

Branches recompute identical answers. In the `fib(5)` tree, `fib(3)` appears twice, `fib(2)` three times, `fib(1)` five times. The tree roughly doubles per increase in $n$, giving $O(\varphi^n)$ — close enough to $O(2^n)$.

</details>

**33. How many distinct subproblems are there, and what follows?**

<details><summary>Answer</summary>

Only $n+1$ — `fib(0)` through `fib(n)`. **If each is computed once, the total work is $O(n)$.**

</details>

**34. What is the memoised call count?**

<details><summary>Answer</summary>

$2n - 1$ — **59 calls for $n = 30$**, against 2.7 million.

</details>

**35. What does the cache do to the shape?**

<details><summary>Answer</summary>

**It turns the exponential tree into a linear chain.**

</details>

**36. Why would memoising merge sort gain nothing?**

<details><summary>Answer</summary>

Because merge sort **never sorts the same sublist twice** — there are no overlapping subproblems to cache.

</details>

---

## G. Where recursion goes next

**37. Give the routing table.**

<details><summary>Answer</summary>

| If the recursion… | You have | Depth |
| :--- | :--- | :--- |
| shrinks by 1 | linear recursion — a loop in disguise | $O(n)$ |
| splits into halves | **divide and conquer** | $O(\log n)$ |
| revisits subproblems | **dynamic programming** | state count |
| explores and undoes choices | **backtracking** | often exponential |
| walks a structure with children | **traversal** | $O(\text{size})$ |

</details>

**38. What single question routes you between them?**

<details><summary>Answer</summary>

**Do the recursive calls overlap?** If two branches ever solve the identical subproblem, memoise — you are in DP. If they never do, a cache is pure overhead.

</details>

---

## H. Traps

**39. What is wrong with `def fib(n, memo={})`?**

<details><summary>Answer</summary>

The mutable default is **shared across every call to the function for the lifetime of the program**, including calls from unrelated code. Use `memo=None` and create it inside.

</details>

**40. Why is `setrecursionlimit` dangerous rather than merely a last resort?**

<details><summary>Answer</summary>

It converts a clean error into a possible **interpreter crash** — the C stack has its own limit that Python's counter does not track.

</details>

**41. What must you add when recursing on a cyclic structure?**

<details><summary>Answer</summary>

A **visited set**. Directory traversal with symlinks, or a graph, loops forever no matter how correct your base case is.

</details>

**42. Summarise the module in one sentence.**

<details><summary>Answer</summary>

Answer three questions — base case, recursive case assuming it works, and progress — then stop thinking; the cost is calls in time and depth in memory, and they are unrelated.

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

- [[01-recursion-fundamentals|Recursion Fundamentals]] — the module
- [[02-recursion-trees-and-recurrences-qb|Recursion Trees & Recurrences — Question Bank]] — the next bank
- [[../06-dynamic-programming/02-memoisation-and-tabulation|Memoisation and Tabulation]]
