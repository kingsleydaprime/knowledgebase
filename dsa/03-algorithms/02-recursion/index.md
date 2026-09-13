# Recursion

**Solving a problem with a smaller copy of itself — and being able to say what that costs.**

Three lessons, written to [[COURSE-STANDARD|the course standard]]. The first teaches the technique, the second teaches how to price it, and the third is the shortcut for when the shape is standard.

> **Why recursion is filed under algorithms rather than under programming fundamentals.** [[09-recursion-and-the-call-stack|Programming fundamentals covers the mechanics]] — what a frame is, how a call returns. This folder is about recursion as a **problem-solving and cost-analysis technique**: how to decompose a problem so a recursive solution exists, and how to get from recursive code to a complexity. Nearly everything later in this course is a recursion with a particular shape, so this is the folder they all point back to.

## The lessons

1. [[01-recursion-fundamentals|Recursion Fundamentals]] — **[Beginner → Intermediate]** — the three questions that produce a recursive function; base case, recursive case and progress; winding and unwinding through the call stack; why space is the *depth* and time is the *call count*; the three ways recursion fails; and memoisation as the fix for repeated subproblems — 2,692,537 calls down to 59.
2. [[02-recursion-trees-and-recurrences|Recursion Trees and Recurrences]] — **[Intermediate]** — turning code into $T(n) = aT(n/b) + f(n)$; drawing the tree; computing nodes, size and work at level $k$; **the three cases — leaves dominate, levels equal, root dominates**; subtractive recurrences; the substitution method; and the doubling test for checking a complexity claim without reading the code.
3. [[03-the-master-theorem|The Master Theorem]] — **[Intermediate → Advanced]** — the same three cases as a theorem with precise conditions; what "polynomially larger" means and why Case 3 needs it; the regularity condition; and **the three situations where the theorem genuinely fails**, including the $n\log n$ trap that produces a confidently wrong answer.

## The thread through all three

**Recursion is induction executed by a machine.** The base case is the base step, the recursive case is the inductive step, and progress is what guarantees the two meet. That is why the method for writing one is three questions rather than a mental trace — you are constructing a proof, and a proof does not require you to picture every case.

**The cost of a recursion is a recurrence, and a recurrence is a tree.** Once you can compute the work at an arbitrary level, every divide-and-conquer complexity in the course falls out of the same three-way comparison. Merge sort's $n\log n$, binary search's $\log n$, tree traversal's $n$ and Strassen's $n^{2.807}$ are four readings of one table.

**Time and space are different questions.** Naive Fibonacci at $n=30$ makes 2.7 million calls at a depth of 30. The call count is the time; the depth is the memory, and the stack is a small fixed resource — about 996 usable frames in CPython by default. This is why [[01-depth-first-search|DFS]] ships in a recursive and an iterative form.

**The routing question for everything downstream is: do the recursive calls overlap?**

1. If two branches ever solve the identical subproblem, cache it — you are in [[15-dynamic-programming|dynamic programming]], and the cache is the whole algorithm.
2. If they never do, a cache is pure overhead, and you are in divide and conquer *(not yet written)* or [[01-depth-first-search|traversal]].
3. If the recursion makes a choice and then *undoes* it, you are in [[14-backtracking|backtracking]].

## What is verified

Every lab was executed and its expected output generated from that run:

| Lesson | What the lab demonstrates |
| :--- | :--- |
| [[01-recursion-fundamentals\|fundamentals]] | `sys.getrecursionlimit()` reports 1,000 but only **996** frames are usable; naive Fibonacci making 242,785 calls for **26** distinct subproblems; a base case the argument steps over, failing on odd input only; and a tail call blowing the stack, because Python does not eliminate them |
| [[02-recursion-trees-and-recurrences\|recursion trees]] | the level-by-level work table for five recurrences, each matching its **exact** closed form; and the doubling test returning 2.00 for linear, 4.00 for quadratic, 3.02 for $n^{\log_2 3}$, and a slowly-falling 2.2 for $n\log n$ |
| [[03-the-master-theorem\|Master Theorem]] | each case's verdict checked against measured work; Strassen's constant ratio to $n^{2.807}$ holding at 2.32; and the $n\log n$ gap case measuring 2.55/2.49/2.44 — **distinguishable from the wrong answer by the numbers alone** |

## Related

- [[03-algorithms/index|03-algorithms]] — the parent folder
- [[01-complexity-analysis/index|Complexity Analysis]] — the measuring system these lessons extend
- Divide and conquer — *not yet written*; [[04-sorting/03-merge-sort|merge sort]] is the worked instance
- [[15-dynamic-programming|Dynamic Programming]] — memoisation, generalised
- [[14-backtracking|Backtracking]] — recursion that undoes its choices
- [[09-recursion-and-the-call-stack|Programming fundamentals: recursion and the call stack]] — the mechanics, if they are still shaky
- [[05-induction-and-recursion|Discrete maths: induction and recursion]] — the proof side
