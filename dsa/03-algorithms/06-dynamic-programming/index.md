# Dynamic Programming

**Recursion plus a cache — and the judgement to know when that is the right move.**

Four lessons, written to [[COURSE-STANDARD|the course standard]]. The first decides *whether* DP applies, the second is *how to write one*, and the last two work the classic problems in one and two dimensions with every answer checked against brute force.

> **The one idea:** a slow recursion is usually slow because it solves the same subproblem thousands of times. Dynamic programming is noticing that and stopping it. Everything else — tables, loops, rolling arrays — is bookkeeping around that single observation.

## Why this is a folder and not one note

Because "dynamic programming" names four separable skills, and people who struggle with DP have usually mastered the last one and skipped the first two:

1. **Deciding it applies** — overlapping subproblems and optimal substructure, both *testable* rather than intuited.
2. **Designing the state** — the part that is genuinely hard, and where almost all failed attempts go wrong.
3. **Writing it** — memoise or tabulate, in whichever order the transition dictates.
4. **Doing the classics** — the problems everyone recognises.

A note that starts at step 4 teaches you to recognise problems you have already seen. This folder starts at step 1.

## The lessons

1. [[01-what-makes-a-problem-dp|What Makes a Problem DP]] — **[Intermediate]** — the two properties, both measured rather than asserted: overlap by counting distinct subproblems against total calls (Fibonacci scores 86,856×, merge sort scores 1.0×), and optimal substructure by the graph where the longest *simple* path has optimal sub-answers that cannot be combined. Plus why greedy fails on coin change without that being a failure of optimal substructure.
2. [[02-memoisation-and-tabulation|Memoisation and Tabulation]] — **[Intermediate]** — the three declarations every DP is made of — **state, transition, base case** — then top-down versus bottom-up, why the transition dictates the fill order (and what a wrong order silently produces), and how to throw away a whole dimension of memory.
3. [[03-classic-one-dimensional|Classic One-Dimensional DP]] — **[Intermediate]** — house robber, coin change and longest increasing subsequence. **LIS is the one that teaches**: its obvious state cannot produce a transition, and understanding why is the most transferable idea here.
4. [[04-classic-two-dimensional|Classic Two-Dimensional DP]] — **[Intermediate → Advanced]** — LCS, 0/1 knapsack and edit distance, with reconstruction for each — and the loop direction that separates 0/1 knapsack from the unbounded one.

## The thread through all four

**The state is the whole design.** Once you can finish the sentence "`dp[i]` is the ..." correctly, the transition usually writes itself and the code is transcription. Most DP failures are a state that does not carry enough information to compute the next state from — which is precisely why [[03-classic-one-dimensional|LIS]] needs "ending at $i$" rather than "within $0..i$".

**Complexity is states × transition cost.** That product is how you evaluate a candidate state *before* writing code. If it is too large, no implementation trick rescues it; you need a different state.

**Caching removes redundancy; it does not create efficiency.** Memoising an exponential-state recursion gives you an exponential DP. The cache only helps when subproblems actually repeat, which is lesson 01's measurement.

**The fill order is derived, not chosen.** Every cell a transition reads must already be final. Getting this wrong produces silent zeros rather than an error — the most common way a tabulated DP is confidently wrong.

## How this sits against the other techniques

| Overlapping subproblems? | Optimal substructure? | Technique |
| :--- | :--- | :--- |
| no | yes | [[03-divide-and-conquer\|divide and conquer]] |
| **yes** | **yes** | **dynamic programming** |
| yes | no | no efficient method known (longest simple path is NP-hard) |
| no | no | brute force or [[14-backtracking\|backtracking]] |

And inside row two: when a *local* rule provably selects the right subproblem, skip the table and use a [[01-when-greedy-works|greedy algorithm]] — which needs a proof, not a feeling.

## What is verified

Every lab was executed and its expected output generated from that run. **Every DP answer in this folder is asserted against brute force, not merely printed:**

| Lesson | What the lab demonstrates |
| :--- | :--- |
| [[01-what-makes-a-problem-dp\|properties]] | merge sort's redundancy at exactly **1.0×** against Fibonacci's 86,856×; the longest-simple-path sub-answers composing into a walk that repeats a vertex; greedy coin change failing on $\{1,3,4\}$ |
| [[02-memoisation-and-tabulation\|memo/tab]] | a reversed fill order returning **0** instead of 34, with no error; `memoised(50,000)` raising `RecursionError` where the tabulated version is fine |
| [[03-classic-one-dimensional\|1-D]] | house robber, coin change and LIS each agreeing with brute force on 300–400 random inputs; the $O(n\log n)$ LIS `tails` array shown **not** to be a subsequence of the input |
| [[04-classic-two-dimensional\|2-D]] | the rolling knapsack's **upward** loop returning 15 where the answer is 5 — and the first test instance hiding the bug by coincidence |

## Question banks

One bank per lesson: micro-questions with the answers hidden behind toggles, for closed-book recall rather than reading. Method explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

- [[01-what-makes-a-problem-dp-qb|What Makes a Problem DP]]
- [[02-memoisation-and-tabulation-qb|Memoisation & Tabulation]]
- [[03-classic-one-dimensional-qb|Classic One-Dimensional DP]]
- [[04-classic-two-dimensional-qb|Classic Two-Dimensional DP]]

---

## Related

- [[03-algorithms/index|03-algorithms]] — the parent folder
- [[02-recursion/index|Recursion]] — where memoisation first appears, and the recurrences behind the costs
- [[03-divide-and-conquer|Divide and Conquer]] — the technique for when subproblems do *not* overlap
- [[01-when-greedy-works|Greedy Algorithms]] — the special case where a local rule is provably enough
- [[15-dynamic-programming|The DP pattern note]] — the problem-recognition layer above this folder
- [[04-floyd-warshall|Floyd–Warshall]] — a DP over graphs
- [[dsa/neetcode-150/index|NeetCode 150]] — the DP section, for fluency
