# The interview playbook — how to run a problem

The [[README|pattern cheat-sheet]] tells you *which tool* a problem shape wants. This note is the layer above it: **how to run the whole interview**, and how to **reverse-engineer the intended approach from the clues** before you've solved anything. In a real interview, *how* you get to the answer is graded as heavily as the answer — a clean process under a hard problem beats a lucky guess.

Two halves: a repeatable **process** (what to do, in order) and a set of **signals** (how to read the problem for hints).

---

## Part 1 — The process (UMPIRE)

A named checklist so you never freeze on "what do I even do first." Say each step *out loud* — the interviewer is scoring your communication, and thinking aloud is how they help you when you're stuck.

### 1. Understand — reword it in your own words
Restate the problem back in plain language: *"So I'm given an array of ints and a target, and I need to return the indices of the two numbers that add up to it — got it."* This catches misunderstandings in the first 30 seconds instead of 20 minutes in, and shows you actually parsed the question rather than pattern-matching a memorized answer.

### 2. Match — ask clarifying questions
Pin down everything the prompt left ambiguous **before** you write anything:
- **Input domain:** can it be empty? negatives? duplicates? is it sorted? how big can `n` get? (the size answer is also your complexity hint — see Part 2).
- **Output:** return the value or the index? all answers or just one? what if there's no valid answer — return `-1`, empty, or throw?
- **Guarantees:** "is there always exactly one solution?" — a *yes* often unlocks a simpler approach.
- **Constraints on the method:** in-place? O(1) extra space? can I mutate the input?

Every answer either removes an edge case you'd have to handle or hands you an assumption you can lean on. Interviewers plant ambiguity on purpose to see if you ask.

### 3. Plan — work through examples, including your own
Take the given example and **trace it by hand**, then invent your **own** — especially edge cases: empty, single element, all-same, already-sorted/reverse-sorted, negatives, the value at the boundary. Your own examples are where the real understanding shows: they force you to define the behavior precisely, and they frequently reveal the pattern (*"oh, once it's sorted, I only ever move inward from both ends"*).

### 4. Plan — brainstorm *multiple* solutions, brute force first
Always start by stating the **brute-force** approach and its complexity, even if it's obviously too slow: *"The naive answer is check every pair, O(n²) time, O(1) space."* This does three things: it guarantees you have *something* correct to fall back on, it gives you a baseline to beat, and the inefficiency usually points at the fix (*"the O(n²) is because I re-search for the complement each time — a hash map makes that lookup O(1), dropping it to O(n)"*). Then propose the optimized approach and **state its complexity before coding**. If you can see two viable approaches, name the trade-off (time vs. space) and let the interviewer weigh in — that's a signal, not indecision.

> Optimize by attacking the bottleneck: **repeated work → memoize/cache** ([[README|DP]]), **repeated search → hash map or sort-then-two-pointers**, **recomputing over a window → sliding window**, **re-scanning for next-greater → monotonic stack**.

### 5. Implement — write the code
Only start coding once you and the interviewer agree on the approach. Narrate as you go (*"this loop walks the right pointer, and I shrink from the left whenever the window's invalid"*). Prefer clear names over clever one-liners; you can micro-optimize after it works. If you blank on a language detail, say so and keep moving — an interviewer will hand you a syntax detail; they won't hand you the algorithm.

### 6. Review — test and trace
Don't announce "done" and stop. **Trace your code line-by-line on a small example**, playing computer with real variable values. Then throw your edge cases at it: empty input, size 1, duplicates, the boundary value, overflow if it's fixed-width arithmetic. Finding and fixing your own bug *before* the interviewer points it out is a strong positive signal; being told your code is broken and shrugging is a red flag.

---

## Part 2 — Reading the signals

Before you brute-force, scan the prompt for tells. Problems are written with a target solution in mind, and the constraints, the stated complexity, and the exact wording all leak it.

### Signal A — the input-size constraint tells you the complexity
Machines do ~10⁸ operations/second and problems allow ~1–10s, so the bound on `n` reveals what complexity is *expected* — often before you've even found the approach. Full table lives in [[foundations/dsa/05-algorithms/01-algorithms|algorithms]]; the reflex version:

| Constraint on `n` | Expected complexity | What that usually means |
|---|---|---|
| `n ≤ ~20` | O(2ⁿ) / O(n!) | try **every** subset/permutation → [[README\|backtracking]] or bitmask DP |
| `n ≤ ~500` | O(n³) | triple loop is fine — often interval / 2-D DP |
| `n ≤ ~5,000` | O(n²) | a nested loop or O(n²) DP is intended |
| `n ≤ 10⁵–10⁶` | O(n) or O(n log n) | one pass, or **sort first**, or a hash map — *not* a nested loop |
| `n ≥ 10⁹`, or a huge value range | O(log n) or O(1) | **binary search**, math/closed-form, or bit tricks — you can't even touch every element |

Seeing `n ≤ 10⁶` and reaching for O(n²) is the constraint *telling you to stop and find the O(n log n)*.

### Signal B — a *stated* target complexity is a dead giveaway
If the problem says "do it in O(...)", work backwards from it:

| They ask for | It almost certainly wants |
|---|---|
| **O(log n)** | **Binary search** (or a balanced-BST / heap operation). Nothing else halves the input like that. |
| **O(n log n)** | A **sort** (then a linear pass / two-pointer sweep), or a **heap**, or divide-and-conquer. The `log n` factor is the sort/heap. |
| **O(n)** on a problem that "feels" like O(n²) | A **hash map** to remove a search, or a **sliding window** / two pointers / prefix sums to remove a rescan. |
| **O(1) space** on an array | **Two pointers**, in-place mutation, or **XOR/bit** tricks (esp. "appears once", "find the missing/duplicate"). |
| **O(1) space** you'd expect to need a set | Often **XOR cancellation** or the **index-as-hash** trick (mark `nums[abs(x)]` negative). |

### Signal C — the wording itself names the pattern
The vocabulary of the prompt maps to tools (this is the [[README|cheat-sheet]] in reverse):
- *"contiguous" subarray/substring* → sliding window or prefix sums.
- *"sorted"* (given, or "you may sort") → two pointers or binary search.
- *"k largest / smallest / most frequent / closest"* → heap of size k.
- *"all combinations / permutations / subsets"* → backtracking.
- *"number of ways" / "min or max cost to..."* with reusable subproblems → DP.
- *"prerequisite / ordering / build order"* → topological sort.
- *"connected / same group / islands"* → union-find or DFS/BFS flood fill.
- *"next greater/smaller"* → monotonic stack.
- *"prefix / starts-with / autocomplete"* → trie.

---

## The 60-second opening, in order

1. **Reword** the problem back. *(Understand)*
2. **Ask** about empties, negatives, duplicates, sortedness, `n`'s max, and the no-answer case. *(Match)*
3. **Trace** the given example, then **invent an edge case** of your own. *(Plan)*
4. **Read the constraints** — let `n`'s size and any stated complexity name the target. *(Signals)*
5. **State the brute force + its complexity**, then the optimized approach + its complexity. *(Plan)*
6. **Code** it, narrating. *(Implement)*
7. **Trace it** on a small input and your edge cases before saying "done." *(Review)*

The single highest-leverage habit: **talk through all of it**. A silent solve of the optimal answer scores worse than a narrated walk from brute force to optimal, because the interview is measuring how you think, not whether you've seen the problem before.

## Related
- [[README|NeetCode 150 index & pattern cheat-sheet]] — signal → tool, once you know *what* you're building
- [[foundations/dsa/05-algorithms/01-algorithms|algorithms]] — the full constraint → complexity table and Big-O reasoning
- [[foundations/dsa/06-patterns/README|patterns]] · [[foundations/dsa/04-data-structures/03-hash-maps|data structures]] — the tools themselves
