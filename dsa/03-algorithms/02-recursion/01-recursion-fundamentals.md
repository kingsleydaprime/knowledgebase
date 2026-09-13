# Module: Recursion Fundamentals (Solving a Problem With a Smaller Copy of Itself)

**[Beginner → Intermediate]** — A recursive function calls itself. That is the mechanical description and it is nearly useless as an explanation, because it tells you what recursion *looks like* rather than what it *is for*. This lesson is about the thing it is for: **turning a problem you cannot solve into a smaller instance of the same problem, plus a small amount of work.**

Everything downstream depends on this — [[02-recursion-trees-and-recurrences|recursion trees]], [[03-the-master-theorem|the Master Theorem]], [[03-divide-and-conquer|divide and conquer]], [[01-depth-first-search|DFS]], [[04-sorting/03-merge-sort|merge sort]], [[14-backtracking|backtracking]], and all of dynamic programming.

---

## Before you start

- You can write and call a function, and you know that a function's local variables belong to that call — [[08-functions|functions]].
- You have seen a recursive function at least once, even if it did not click — [[09-recursion-and-the-call-stack|recursion and the call stack]].
- You can read $O(n)$ and $O(2^n)$ as statements about growth — [[01-growth-and-asymptotic-notation|growth and asymptotic notation]].

**After this lesson you will be able to:**

1. Write a recursive function by answering **three specific questions**, rather than by intuition.
2. Trace the **call stack** for a recursive call, and predict the depth it will reach before running it.
3. Explain why naive Fibonacci is $O(2^n)$ and the memoised version is $O(n)$, **in terms of subproblems rather than lines of code**.
4. Name the three ways a recursion fails — no base case, a base case the argument steps over, and a depth the stack cannot hold — and demonstrate each.

**Study route:** read 1–4, answer the prediction in section 5 before reading past it, then run the lab. Section 7 is where recursion connects to the rest of the course.

---

## 1. Why this exists: the problem you cannot see the end of

Count the files in a directory.

You could write a loop. But a directory contains directories, which contain directories, and you do not know how deep it goes — so how many nested loops do you write? **You cannot answer that, because the answer depends on data you have not seen yet.** A loop needs its nesting fixed when you write the code; this problem's nesting is fixed only at runtime.

Now notice something about the problem's shape:

> The number of files in a directory is the number of loose files in it, **plus the number of files in each of its subdirectories.**

The second half of that sentence is the same question again, asked about something smaller. That is the entire recursive insight, and it is available whenever a problem's answer can be phrased in terms of the same problem on a smaller input.

```
photos/                      files(photos/)
├── cat.jpg                    = 2 loose files
├── dog.jpg                      + files(2023/)
├── 2023/                        + files(2024/)
│   ├── jan.jpg
│   └── feb.jpg               files(2023/) = 2 + nothing
└── 2024/
    └── trips/                files(2024/) = 0 + files(trips/)
        └── rome.jpg          files(trips/) = 1
                              -------------------------
                              total = 2 + 2 + (0 + 1) = 5
```

**The analogy that is usually offered — mirrors facing each other, or Russian dolls — captures the self-similarity and misses the part that matters: the shrinking.** Mirrors recurse forever. A doll does not, because each one is strictly smaller and the smallest is solid. The second property is the one that makes recursion a technique rather than a bug.

---

## Terms used in recursion

1. **Recursive function**: This is a function whose body contains a call to itself. The call may be direct, or it may go through another function and come back.
2. **Base case**: This is also known as the **terminating case** or **stopping condition**. This is an input the function answers immediately, without calling itself. `factorial(0) = 1` is a base case. **A recursion with no reachable base case never terminates.**
3. **Recursive case**: This is the branch that reduces the problem and calls itself. For factorial it is `n * factorial(n - 1)` — one multiplication, plus the same problem on `n - 1`.
4. **Progress**: This is the requirement that every recursive call moves strictly closer to a base case. It is what separates a recursion from an infinite loop, and it is the property that is easiest to get subtly wrong.
5. **Stack frame**: This is also known as an **activation record**. This is the block of memory holding one call's local variables, its arguments, and the address to return to. Every call in progress has one, and it is released when that call returns.
6. **Call stack**: This is the stack of frames for all calls that have started and not yet finished. If `a` calls `b` and `b` calls `c`, there are three frames, and they unwind in reverse — [[07-stacks-and-queues|LIFO]].
7. **Recursion depth**: This is the number of frames on the stack at the deepest point. It is the *memory* cost of a recursion, and it is a different quantity from the number of calls: naive Fibonacci makes millions of calls at a depth of only $n$.
8. **Stack overflow**: This is running out of room for frames. Python raises `RecursionError` at a configurable limit — 1,000 by default — rather than crashing, which is a courtesy most languages do not extend.
9. **Winding and unwinding**: This is the two-phase shape of every recursion. **Winding** is the descent, where calls are made and frames pile up; **unwinding** is the return journey, where answers come back and frames are released. Work placed before the recursive call happens on the way down; work placed after it happens on the way back up.
10. **Tail call**: This is a recursive call in which *nothing happens after it returns* — its result is returned directly. `return helper(n - 1, acc + n)` is a tail call; `return n * factorial(n - 1)` is not, because the multiplication still has to happen. Some languages reuse the frame for a tail call and so recurse in constant space. **Python does not**, deliberately.
11. **Memoisation**: This is caching the answer to each distinct subproblem the first time it is computed, and returning the cached value on every later request. It is the bridge from recursion to [[15-dynamic-programming|dynamic programming]].
12. **Overlapping subproblems**: This is the situation where the recursion tree contains the same subproblem many times. It is what makes memoisation worth doing, and its absence is why memoising merge sort achieves nothing.

---

## 2. The three questions

Do not try to picture the whole recursion. **Nobody can, and the attempt is what makes recursion feel hard.** Answer three questions instead, and trust the result.

1. **What is the smallest input I can answer without thinking?** That is your base case.
2. **Assuming the function already works for smaller inputs, how do I build the answer for `n` from them?** That is your recursive case. **Assume it works.** Do not trace down into it — that is the whole point of the technique.
3. **Does every recursive call actually move toward the base case?** That is progress, and it is the check people skip.

### Applied: sum a list

1. **Smallest input:** the empty list. Its sum is 0.
2. **Assuming it works for smaller lists:** the sum of a list is its first element plus the sum of the rest.
3. **Progress:** the rest is one shorter than the list, and length cannot go below zero. ✓

```python
def list_sum(values):
    if not values:              # 1. base case
        return 0
    return values[0] + list_sum(values[1:])   # 2. recursive case
```

**Question 2 is the one that requires a leap, and the leap is the method.** You are permitted to assume `list_sum(values[1:])` returns the correct sum, because that is exactly what you are in the middle of proving. This is induction: the base case is the base step, the recursive case is the inductive step, and progress is what guarantees you reach the base.

> **A note on this particular implementation.** `values[1:]` copies the rest of the list on every call, which makes this $O(n^2)$ in time and $O(n^2)$ in memory — a bad way to sum a list. It is written this way because it is the clearest illustration of the three questions. Passing an index instead of slicing fixes it, and the lab's `linear` function does exactly that.

---

## 3. The call stack: where the "extra" memory goes

A loop uses one set of variables. A recursion uses one set **per call in progress**, and they all exist at the same time.

Trace `list_sum([3, 1, 4])`:

```
WINDING  (frames pile up, nothing has been computed yet)

  list_sum([3,1,4])  -> 3 + ?          frame 1
    list_sum([1,4])  -> 1 + ?          frame 2
      list_sum([4])  -> 4 + ?          frame 3
        list_sum([]) -> 0              frame 4  <- base case, first real answer

UNWINDING  (answers travel back up, frames released)

        list_sum([])  returns 0
      list_sum([4])   returns 4 + 0 = 4
    list_sum([1,4])   returns 1 + 4 = 5
  list_sum([3,1,4])   returns 3 + 5 = 8
```

**Read the winding phase and notice that no addition has happened yet.** Every frame is suspended mid-expression, holding its `values[0]`, waiting. The additions all happen on the way back up, in reverse order. That is why the memory cost of this function is $O(n)$ even though it stores nothing explicitly — the pending frames *are* the storage.

**This is the single most useful thing to know about recursion's cost.** Its space complexity is the *depth* of the recursion, not the number of calls. The lab makes it concrete: a call chain of depth 100 has 100 frames, and the interpreter's default ceiling is 996 usable frames.

---

## 4. The three ways recursion fails

### Failure 1: no base case

```python
def countdown(n):
    print(n)
    countdown(n - 1)      # nothing stops this
```

Runs until the stack is exhausted. In Python, `RecursionError`.

### Failure 2: a base case the argument steps over

This one is nastier because it works for half the inputs.

```python
def evens_down(n):
    if n == 0:            # only ever true for even n
        return 0
    return evens_down(n - 2)
```

`evens_down(10)` is fine. `evens_down(11)` goes $11, 9, 7, \dots, 1, -1, -3, \dots$ and never equals 0. **The fix is to make the base case a boundary rather than a point:** `if n <= 0`. The lab runs both and shows 10 returning normally while 11 raises.

**The general rule: a base case should be a condition the argument cannot jump past, not a value it must land on exactly.**

### Failure 3: correct, but too deep

```python
def linear(n):
    if n <= 0:
        return 0
    return 1 + linear(n - 1)
```

Perfectly correct, and `linear(100_000)` raises `RecursionError` regardless. There is nothing wrong with the logic — the machine simply cannot hold 100,000 frames at once.

**This is not a Python quirk, it is a real limit everywhere**; Python merely reports it politely instead of segfaulting. The three responses, in order of preference:

1. **Rewrite it iteratively** if the recursion is linear. A recursion of depth $n$ that could be a loop should usually be a loop.
2. **Restructure so the depth is $O(\log n)$** rather than $O(n)$ — this is what divide and conquer buys you, and why merge sort recurses to depth 20 on a million elements rather than a million.
3. **Raise the limit** with `sys.setrecursionlimit()` only when you know the real depth is bounded and merely larger than 1,000. It is the last resort, not the first: the limit exists to catch runaway recursion before it takes the process down.

This is exactly why [[01-depth-first-search|DFS]] ships in both recursive and iterative forms, and why the DFS lab kills the recursive one on a 5,000-vertex path.

---

## 5. The cost of a recursion: calls, not lines

> **Predict before reading on.** `fib(n) = fib(n-1) + fib(n-2)` with base cases `fib(0)=0, fib(1)=1`. The function has one line of real work. How many calls does `fib(30)` make — roughly 30, roughly 900, or roughly 2.7 million? Commit to an answer.

The answer is **2,692,537**, and the lab measures it.

Here is why, and the reason is entirely about the *shape* of the recursion rather than the code:

```
                      fib(5)
              ┌─────────┴─────────┐
           fib(4)               fib(3)
        ┌────┴────┐          ┌────┴────┐
     fib(3)     fib(2)    fib(2)     fib(1)
    ┌──┴──┐    ┌──┴──┐   ┌──┴──┐
 fib(2) fib(1) fib(1) fib(0) fib(1) fib(0)
 ┌──┴──┐
fib(1) fib(0)
```

**Count `fib(3)`: it appears twice. `fib(2)` appears three times. `fib(1)` appears five times.** Each of those recomputes an identical answer from scratch. The tree roughly doubles in size for each increase in $n$, giving $O(\varphi^n)$ — close enough to $O(2^n)$ for every practical purpose.

The measured numbers make the shape unmistakable:

| $n$ | naive calls | memoised calls | iterative steps |
| ---: | ---: | ---: | ---: |
| 10 | 177 | 19 | 10 |
| 20 | 21,891 | 39 | 20 |
| 25 | 242,785 | 49 | 25 |
| 30 | 2,692,537 | 59 | 30 |

**Look at the naive column going down: 177 → 21,891 → 2,692,537. Multiplying by roughly 123 for each +10 in $n$.** That is exponential growth, from a function whose body is one addition.

And the diagnosis in a single line: `fib_naive(25)` makes **242,785 calls to solve 26 distinct subproblems** — a redundancy factor of about 9,338.

### Memoisation: the fix, and why it works

```python
def fib_memo(n, memo=None):
    if memo is None:
        memo = {}
    if n < 2:
        return n
    if n in memo:
        return memo[n]
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]
```

**There are only $n+1$ distinct subproblems — `fib(0)` through `fib(n)` — so if each is computed once, the total work is $O(n)$.** The cache turns the exponential tree into a linear chain. The measured call count is $2n - 1$: 59 calls for $n = 30$, against 2.7 million.

**This is the whole idea of dynamic programming**, arrived at from the recursion side. It works here because the subproblems *overlap*. Memoising merge sort would gain nothing, because merge sort never sorts the same sublist twice.

---

## 6. Worked example — complete runnable lab

Save as `recursion.py` in an empty directory. Standard library only. **It deliberately raises `RecursionError` several times and catches them** — that is the demonstration, not a failure.

```python
"""What recursion costs, and where it breaks.

Run:  python3 recursion.py
"""

import sys


# ------------------------------------------------------- 1. THE CALL STACK
def depth_probe(n, _depth=0):
    """Return the deepest frame depth reached. One frame per pending call."""
    if n == 0:
        return _depth
    return depth_probe(n - 1, _depth + 1)


def stack_limit():
    """Find the actual recursion depth this interpreter allows, at the current limit."""
    lo, hi = 1, 20_000
    while lo < hi:
        mid = (lo + hi + 1) // 2
        try:
            depth_probe(mid)
            lo = mid
        except RecursionError:
            hi = mid - 1
    return lo


# ------------------------------------------ 2. THE SAME FUNCTION, THREE COSTS
calls = {"naive": 0, "memo": 0, "iter": 0}


def fib_naive(n):
    calls["naive"] += 1
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_memo(n, memo=None):
    if memo is None:
        memo = {}
    calls["memo"] += 1
    if n < 2:
        return n
    if n in memo:
        return memo[n]
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]


def fib_iter(n):
    a, b = 0, 1
    for _ in range(n):
        calls["iter"] += 1
        a, b = b, a + b
    return a


# ------------------------------------------------- 3. THE THREE COMMON SHAPES
shape_calls = {"linear": 0, "halving": 0, "binary": 0, "divide": 0}


def linear(n):
    """T(n) = T(n-1) + O(1)  ->  O(n)"""
    shape_calls["linear"] += 1
    if n <= 0:
        return 0
    return 1 + linear(n - 1)


def halving(n):
    """T(n) = T(n/2) + O(1)  ->  O(log n)"""
    shape_calls["halving"] += 1
    if n <= 1:
        return 0
    return 1 + halving(n // 2)


def binary_branch(n):
    """T(n) = 2T(n-1) + O(1)  ->  O(2^n)"""
    shape_calls["binary"] += 1
    if n <= 0:
        return 1
    return binary_branch(n - 1) + binary_branch(n - 1)


def divide(n):
    """T(n) = 2T(n/2) + O(n)  ->  O(n log n).  Returns work done, not call count."""
    shape_calls["divide"] += 1
    if n <= 1:
        return n
    left = divide(n // 2)
    right = divide(n - n // 2)
    return left + right + n          # the + n is the 'combine' step


# --------------------------------------------------- 4. BASE CASE MISTAKES
def missing_base(n, budget):
    """A 'base case' that the argument can step over."""
    if budget <= 0:
        raise RecursionError("would not terminate")
    if n == 0:                        # even n only ever hits this...
        return 0
    return missing_base(n - 2, budget - 1)


# ------------------------------------------------- 5. TAIL CALLS IN PYTHON
def tail_sum(n, acc=0):
    """Tail-recursive: nothing happens after the recursive call returns."""
    if n == 0:
        return acc
    return tail_sum(n - 1, acc + n)


def main():
    print("=== 1. One frame per pending call ===")
    for n in (1, 10, 100):
        print(f"  depth_probe({n}) reached frame depth {depth_probe(n)}")
    print(f"  sys.getrecursionlimit() default here: {sys.getrecursionlimit()}")
    print(f"  deepest call chain actually achievable at that limit: {stack_limit()}")
    sys.setrecursionlimit(20_000)
    print(f"  after sys.setrecursionlimit(20000): {stack_limit()}")
    print("  -> recursion depth is bounded by a real, small, adjustable resource; a loop is not")

    print("\n=== 2. Fibonacci: same definition, three costs ===")
    print("    n |   naive calls | memo calls | iter steps |  naive/n")
    for n in (5, 10, 20, 25, 30):
        for k in calls:
            calls[k] = 0
        fib_naive(n)
        fib_memo(n)
        fib_iter(n)
        print(f"  {n:>3} | {calls['naive']:>13,} | {calls['memo']:>10} "
              f"| {calls['iter']:>10} | {calls['naive']/max(n,1):>8.1f}")
    print("  -> naive calls roughly double for every +1 in n: that is 2^n, not n")

    print("\n  How much of the naive work is repeated?")
    for k in calls:
        calls[k] = 0
    fib_naive(25)
    distinct = 26
    print(f"  fib_naive(25) made {calls['naive']:,} calls for only {distinct} distinct subproblems")
    print(f"  -> {calls['naive']/distinct:.0f}x redundancy; memoisation removes all of it")

    print("\n=== 3. The three shapes, counted ===")
    print("   recurrence                     |   n |    calls | closed form")
    for n in (8, 64, 1024):
        shape_calls["linear"] = 0
        linear(n)
        print(f"   T(n) = T(n-1) + O(1)           | {n:>3} | {shape_calls['linear']:>8} | n+1 = {n+1}")
    for n in (8, 64, 1024):
        shape_calls["halving"] = 0
        halving(n)
        import math
        print(f"   T(n) = T(n/2) + O(1)           | {n:>3} | {shape_calls['halving']:>8} "
              f"| log2(n)+1 = {int(math.log2(n))+1}")
    for n in (4, 8, 16):
        shape_calls["binary"] = 0
        binary_branch(n)
        print(f"   T(n) = 2T(n-1) + O(1)          | {n:>3} | {shape_calls['binary']:>8} "
              f"| 2^(n+1)-1 = {2**(n+1)-1}")

    print("\n  The divide-and-conquer shape, measuring WORK rather than calls:")
    print("     n |  work done | n*log2(n) | ratio")
    import math
    for n in (16, 256, 4096, 65536):
        w = divide(n)
        nlogn = n * math.log2(n)
        print(f"  {n:>6} | {w:>10,} | {nlogn:>9,.0f} | {w/nlogn:>5.2f}")
    print("  -> work/(n log n) stays flat, which is what O(n log n) means")

    print("\n=== 4. A base case the argument steps over ===")
    for start in (10, 11):
        try:
            missing_base(start, budget=50)
            print(f"  missing_base({start}) returned fine")
        except RecursionError as e:
            print(f"  missing_base({start}) -> RecursionError: {e}")
    print("  -> 'n == 0' is not a base case for odd n; it needs 'n <= 0'")

    print("\n=== 5. Python does NOT optimise tail calls ===")
    sys.setrecursionlimit(1000)
    for n in (100, 999):
        try:
            print(f"  tail_sum({n}) = {tail_sum(n)}")
        except RecursionError:
            print(f"  tail_sum({n}) -> RecursionError")
    try:
        tail_sum(10_000)
    except RecursionError:
        print("  tail_sum(10,000) -> RecursionError, even though nothing happens after the call")
    print("  -> in a language with tail-call elimination this would run in constant stack space")


if __name__ == "__main__":
    main()
```

### Expected output

Generated by running the file above:

```
=== 1. One frame per pending call ===
  depth_probe(1) reached frame depth 1
  depth_probe(10) reached frame depth 10
  depth_probe(100) reached frame depth 100
  sys.getrecursionlimit() default here: 1000
  deepest call chain actually achievable at that limit: 996
  after sys.setrecursionlimit(20000): 19996
  -> recursion depth is bounded by a real, small, adjustable resource; a loop is not

=== 2. Fibonacci: same definition, three costs ===
    n |   naive calls | memo calls | iter steps |  naive/n
    5 |            15 |          9 |          5 |      3.0
   10 |           177 |         19 |         10 |     17.7
   20 |        21,891 |         39 |         20 |   1094.5
   25 |       242,785 |         49 |         25 |   9711.4
   30 |     2,692,537 |         59 |         30 |  89751.2
  -> naive calls roughly double for every +1 in n: that is 2^n, not n

  How much of the naive work is repeated?
  fib_naive(25) made 242,785 calls for only 26 distinct subproblems
  -> 9338x redundancy; memoisation removes all of it

=== 3. The three shapes, counted ===
   recurrence                     |   n |    calls | closed form
   T(n) = T(n-1) + O(1)           |   8 |        9 | n+1 = 9
   T(n) = T(n-1) + O(1)           |  64 |       65 | n+1 = 65
   T(n) = T(n-1) + O(1)           | 1024 |     1025 | n+1 = 1025
   T(n) = T(n/2) + O(1)           |   8 |        4 | log2(n)+1 = 4
   T(n) = T(n/2) + O(1)           |  64 |        7 | log2(n)+1 = 7
   T(n) = T(n/2) + O(1)           | 1024 |       11 | log2(n)+1 = 11
   T(n) = 2T(n-1) + O(1)          |   4 |       31 | 2^(n+1)-1 = 31
   T(n) = 2T(n-1) + O(1)          |   8 |      511 | 2^(n+1)-1 = 511
   T(n) = 2T(n-1) + O(1)          |  16 |   131071 | 2^(n+1)-1 = 131071

  The divide-and-conquer shape, measuring WORK rather than calls:
     n |  work done | n*log2(n) | ratio
      16 |         80 |        64 |  1.25
     256 |      2,304 |     2,048 |  1.12
    4096 |     53,248 |    49,152 |  1.08
   65536 |  1,114,112 | 1,048,576 |  1.06
  -> work/(n log n) stays flat, which is what O(n log n) means

=== 4. A base case the argument steps over ===
  missing_base(10) returned fine
  missing_base(11) -> RecursionError: would not terminate
  -> 'n == 0' is not a base case for odd n; it needs 'n <= 0'

=== 5. Python does NOT optimise tail calls ===
  tail_sum(100) = 5050
  tail_sum(999) -> RecursionError
  tail_sum(10,000) -> RecursionError, even though nothing happens after the call
  -> in a language with tail-call elimination this would run in constant stack space
```

### What the blocks are showing

- **Block 1** separates two things that get conflated: `sys.getrecursionlimit()` reports 1,000, but the deepest chain actually achievable is **996**, because `main` and its callers already occupy frames. The limit is on the whole stack, not on your function.
- **Block 3** counts calls against the closed form for each recurrence shape, and they match exactly — $n+1$, $\log_2 n + 1$, $2^{n+1} - 1$. The last section measures **work** rather than calls for the divide-and-conquer shape, and the ratio to $n\log_2 n$ settles at 1.06. It does not converge to exactly 1 because the true count is $n(\log_2 n + 1)$; the $+1$ fades as $n$ grows, which is precisely what "ignore lower-order terms" means in practice.
- **Block 5** shows `tail_sum(999)` failing at a limit of 1,000 — the missing frames are the ones `main` is already using.

---

## 7. Where recursion goes next

Recursion is not one technique; it is the substrate for four, and telling them apart is what the rest of this course is about.

| If the recursion... | You have | Cost shape | Covered in |
| :--- | :--- | :--- | :--- |
| shrinks by 1 each time | linear recursion — usually a loop in disguise | $O(n)$ depth | this lesson |
| splits into halves and combines | **divide and conquer** | $O(\log n)$ depth | [[03-divide-and-conquer|divide and conquer]] |
| revisits the same subproblems | **dynamic programming** (memoise it) | depends on state count | [[15-dynamic-programming\|dynamic programming]] |
| explores choices and undoes them | **backtracking** | often exponential | [[14-backtracking\|backtracking]] |
| walks a structure with children | **traversal** | $O(\text{size})$ | [[01-depth-first-search\|DFS]], [[01-depth-first-traversals\|tree traversals]] |

**The question that routes you between them:** *do the recursive calls overlap?* If two branches ever solve the identical subproblem, memoise — you are in dynamic programming. If they never do, you are in divide and conquer or traversal, and a cache would be pure overhead.

---

## 8. Common pitfalls and traps

1. **Trying to trace the whole thing in your head.** Recursion is designed so you do not have to. Verify the base case, verify the recursive case *assuming the call works*, verify progress, and stop.
2. **A base case that is a point rather than a boundary.** `if n == 0` fails for any argument that can step over zero. Use `if n <= 0` unless you have a reason not to.
3. **Confusing call count with depth.** Naive `fib(30)` makes 2.7 million calls at a depth of 30. The first number is the time cost, the second is the memory cost, and they are unrelated.
4. **Mutable default arguments as a cache.** `def fib(n, memo={})` shares one dictionary across every call to the function for the lifetime of the program, including calls from unrelated code. Use `memo=None` and create it inside, as the lab does.
5. **Slicing to shrink the input.** `values[1:]` looks harmless and copies the list every call, silently turning $O(n)$ into $O(n^2)$. Pass an index instead.
6. **Assuming tail recursion is free.** It is in Scheme, Haskell and (with effort) Rust. It is **not** in Python, Java or JavaScript engines in the general case. The lab shows a tail call blowing the stack at 999.
7. **Reaching for `setrecursionlimit` first.** It converts a clean error into a possible interpreter crash, because the C stack has its own limit that Python's counter does not track. Fix the depth, or go iterative.
8. **Recursing on a cyclic structure without a visited set.** Directory traversal with symlinks, or a graph, will loop forever no matter how correct your base case is. See [[01-depth-first-search|DFS]].

---

## 9. Check your understanding

1. **Why is the space complexity of naive `fib(n)` only $O(n)$, when it makes $O(2^n)$ calls?**
   <details><summary>Answer</summary>Because calls are not simultaneous. The tree is explored depth-first: <code>fib(n-1)</code> is fully evaluated and its frames released before <code>fib(n-2)</code> is called. The most frames alive at once is the height of the tree, which is $n$. Time counts every node in the tree; space counts only the longest root-to-leaf path.</details>

2. **`def f(n): return f(n-1) + f(n-2)` with `if n <= 1: return n` removed entirely. What happens, and why is the error message misleading?**
   <details><summary>Answer</summary>It recurses forever and raises <code>RecursionError: maximum recursion depth exceeded</code>. The message is misleading because it suggests the depth limit is the problem — raising the limit would only delay the failure. The real fault is a missing base case, which is a logic error, not a resource one.</details>

3. **Would memoising merge sort speed it up?**
   <details><summary>Answer</summary>No. Merge sort partitions its input, so no two recursive calls ever receive the same sublist — there are no overlapping subproblems to cache. You would pay for hashing and storage and get nothing back. Memoisation helps exactly when the recursion tree repeats subproblems, which is the property that defines dynamic programming.</details>

4. **Rewrite `list_sum` so it uses $O(1)$ extra space beyond the call stack, and say what the call stack still costs.**
   <details><summary>Answer</summary><code>def list_sum(values, i=0): return 0 if i == len(values) else values[i] + list_sum(values, i+1)</code>. This removes the $O(n)$ copy per call, so extra space per frame is constant — but the stack is still $O(n)$ deep, so total space is still $O(n)$. Only an iterative version, or a language with tail-call elimination, gets you to $O(1)$ overall.</details>

5. **A colleague says "recursion is always slower than iteration". Give the strongest version of their argument and then the case against.**
   <details><summary>Answer</summary><b>For:</b> each call costs a frame — allocation, argument copying, return-address bookkeeping — which a loop does not pay; and the depth is bounded by a resource a loop does not consume. For a linear recursion that maps onto a loop, iteration wins on both counts. <b>Against:</b> for problems whose structure is itself recursive — trees, nested directories, backtracking — the iterative version must build and manage an explicit stack, which does the same allocations with worse readability and more bugs. The cost is inherent in the problem, not in the recursion. The honest rule is: linear recursion should usually be a loop; branching recursion usually should not.</details>

---

## 10. Practice — independent task

Implement `count_paths(grid)`: the number of distinct paths from the top-left to the bottom-right of an `R × C` grid, moving only **right** or **down**, where some cells are blocked.

**Input:** a list of strings, `.` for open and `#` for blocked. **Output:** an integer count.

**Part 1 — pure recursion.** Answer the three questions explicitly in comments before writing code. Then implement it with no cache.

**Part 2 — measure the damage.** Instrument it with a call counter. Report calls for a fully-open grid at sizes $2\times2$ through $8\times8$ — and state, from the numbers alone, what growth you are looking at.

**Part 3 — memoise.** Add a cache keyed on position. Report the call count for the same sizes and explain, in terms of *distinct subproblems*, why the new number is what it is. You should be able to predict it before running.

**Part 4 — break it.** Find the grid size at which the un-memoised version becomes unusable on your machine, and the size at which the memoised version hits `RecursionError`. They will be very different numbers, and the difference is the point.

**Edge cases:** a $1\times1$ grid; the start or the end blocked; a fully blocked row cutting the grid in two; a grid with one row; an empty input.

**Done when:** both versions agree on every test grid; your predicted memoised call count matches the measured one; and you can state in one sentence why this problem memoises well while merge sort does not.

Then compare with the course's worked version: [[111-unique-paths|Unique Paths]] is this problem, and [[15-dynamic-programming|the dynamic programming pattern]] is where the cache becomes a table.

---

## Before moving on

You can write a recursive function by answering the three questions; trace winding and unwinding and predict the depth; explain naive Fibonacci's cost in terms of repeated subproblems rather than lines of code; and name and demonstrate the three failure modes.

**Recap:** recursion expresses a problem as a smaller instance of itself plus a little work. A base case stops it, a recursive case shrinks it, and progress guarantees the two meet — make the base case a boundary (`n <= 0`), never a point (`n == 0`). Every pending call holds a frame, so **space is the depth, time is the call count**, and they are unrelated. The default Python ceiling is 1,000 frames and about 996 are usable. When the recursion tree repeats subproblems, memoisation collapses it — naive Fibonacci at $n=30$ makes 2,692,537 calls and the memoised version makes 59. Python does not eliminate tail calls.

**Next:** [[02-recursion-trees-and-recurrences|Recursion Trees and Recurrences]] — how to get from recursive code to a complexity, by drawing the tree and adding up the levels.

---

## Related

- [[02-recursion-trees-and-recurrences|Recursion Trees and Recurrences]] — the next lesson: costing a recursion properly
- [[03-the-master-theorem|The Master Theorem]] — the shortcut, once you can draw the tree
- [[09-recursion-and-the-call-stack|Recursion and the call stack]] — the programming-fundamentals treatment, if the mechanics are still shaky
- [[01-growth-and-asymptotic-notation|Growth and Asymptotic Notation]] — what $O(2^n)$ is claiming
- [[15-dynamic-programming|Dynamic Programming]] — memoisation, generalised
- [[14-backtracking|Backtracking]] — recursion that undoes its choices
- [[01-depth-first-search|Depth-First Search]] — recursion over a graph, and why it ships in two forms
- [[02-recursion/index|the recursion folder]]
