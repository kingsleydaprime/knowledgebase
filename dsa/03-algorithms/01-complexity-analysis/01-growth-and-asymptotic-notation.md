---
id: 0aa8cd36-1459-4b70-a4b8-9e79a44a109f
---

# Module: Algorithms & Complexity Analysis (Big-O, Bounds & Space)

Welcome to the **Algorithms & Complexity Analysis** module. An **Algorithm** is a finite, well-defined sequence of instructions designed to transform an input into a desired output.

This module introduces the mathematical vocabulary—**Big-O**, **Big-$\Omega$**, and **Big-$\Theta$**—used by computer scientists to evaluate, compare, and optimize software performance across all engineering disciplines.

---

## Before you start
<!-- bite: b6397289-751e-4296-be18-cb69c1e590f0 -->

- You can read a `for` loop and count how many times it runs — [[01-loops-and-what-they-cost|loops and what they cost]].
- You know what an array is and that indexing it is cheap — [[01-arrays|arrays]].

**After this lesson you will be able to:**

1. Distinguish $O$, $\Omega$ and $\Theta$, and use each one correctly rather than saying "big-O" for all three.
2. Separate best, average and worst case, and say why production reasoning uses the worst.
3. Derive the complexity of a recursive algorithm from its recurrence.
4. Explain **amortised** analysis, and why a dynamic array's `append` is $O(1)$ despite occasionally copying everything.
5. Read a problem's constraints and infer the intended complexity before writing any code.

**Study route:** read 1–7, attempt the prediction in section 6, then run the lab — it measures the growth rates rather than asserting them.

---

## 1. Why Growth Rate Matters (Real-World Motivation)
<!-- bite: 02c706df-4128-4213-a430-daec8b4f1dfb -->

Suppose you need to compare two sorting programs:

- **Method A**: Tested on your high-end gaming laptop $\rightarrow$ finishes in **2.5 seconds**.
- **Method B**: Tested on a cheap server $\rightarrow$ finishes in **5.0 seconds**.

Does this mean Method A is a better algorithm? **Not necessarily!** If you run Method A on a slow phone, it might take 20 seconds. 

Measuring runtime in seconds is unreliable because it depends on hardware speed, programming language overhead, and CPU load.

### Measuring Growth Rate instead of Time
Instead of measuring seconds, computer science measures **how the workload grows as input size ($n$) scales to infinity**:

```text
Input Size (n)   | O(1) Constant | O(n) Linear | O(n log n)    | O(n²) Quadratic
---------------------------------------------------------------------------------
n = 10           | < 1 µs        | < 1 µs      | < 1 µs        | 1 µs
n = 1,000        | < 1 µs        | 10 µs       | 0.1 ms        | 10 ms
n = 1,000,000    | < 1 µs        | 10 ms       | 0.2 seconds   | ABOUT 3 HOURS!
```

> [!KEY-INSIGHT]
> At $n = 1,000,000$ and about $10^8$ simple steps a second, an $O(n^2)$ algorithm takes **about 3 hours** ($10^{12}$ steps), while an $O(n \log n)$ algorithm finishes in **0.2 seconds** on the exact same computer!

---

## 2. The Three Asymptotics: $O$, $\Omega$, and $\Theta$
<!-- bite: ef56dc2d-8df4-4398-9990-3525d4466277 -->

In computer science, we use three mathematical notations to bound an algorithm's growth function $T(n)$:

```text
           Upper Bound: O(f(n))  --->  Work is at most f(n)
T(n) ====> Tight Bound: Θ(f(n))  --->  Work is PRECISELY f(n)
           Lower Bound: Ω(f(n))  --->  Work is at least f(n)
```

| Notation | Name | Formal Meaning | Plain-English Definition |
| :--- | :--- | :--- | :--- |
| **$O(f(n))$** | **Big-O** | $T(n) \le c \cdot f(n)$ | **Upper Bound**: "At worst, work grows no faster than $f(n)$." |
| **$\Omega(f(n))$**| **Big-Omega**| $T(n) \ge c \cdot f(n)$ | **Lower Bound**: "At best, work grows no slower than $f(n)$." |
| **$\Theta(f(n))$**| **Big-Theta**| $c_1 f(n) \le T(n) \le c_2 f(n)$ | **Tight Bound**: "Work grows **exactly** like $f(n)$." |

> [!IMPORTANT]
> **The Tight Bound Rule**: $\Theta(f(n))$ holds **if and only if** both $O(f(n))$ and $\Omega(f(n))$ hold simultaneously!

---

## 3. Best, Average, and Worst-Case Scenarios
<!-- bite: 11eb2c21-209a-4254-afc8-011a48554099 -->

The mathematical bounds ($O, \Omega, \Theta$) are independent of the input scenarios (Best, Average, Worst):

- **Best-Case**: The input configuration that requires the absolute minimum operations (e.g. searching for an item that happens to be at index 0 $\rightarrow \Theta(1)$).
- **Average-Case**: Expected work averaged over all probable inputs.
- **Worst-Case**: The input configuration that causes maximum possible work (e.g. searching for an item that is missing $\rightarrow \Theta(n)$).

### Security Aspect: Why Worst-Case is the Production Standard
A [[03-hash-maps|Hash Map]] operates in average **$\Theta(1)$ time**, but degrades to **$\Theta(n)$ worst-case** when all keys collide into a single bucket. 

Attackers can intentionally exploit this gap by sending malicious input data designed to trigger worst-case performance (**Hash-Flooding Denial of Service Attack**). Software engineers design systems against the **Worst-Case**!

---

## 4. Derived Recursive Complexity (Recurrence Trees)
<!-- bite: aff2e564-4f94-412d-aeae-6921def40d15 -->

For recursive algorithms, complexity is derived by building a **Recurrence Tree**:

```python
# 1. Merge Sort: Recurrence T(n) = 2T(n/2) + O(n)
#    - Splits problem into 2 halves, recurses, and merges in O(n) time.
#    - Tree Height: log₂ n levels
#    - Work per Level: O(n)
#    - Total Work: O(n log n)

# 2. Binary Search: Recurrence T(n) = T(n/2) + O(1)
#    - Recurses into 1 half, discards the other half.
#    - Tree Height: log₂ n levels
#    - Work per Level: O(1)
#    - Total Work: O(log n)
```

---

## 5. Amortized Analysis vs. Average Case
<!-- bite: 3d1f2e1b-bcb6-4af8-96b8-e5b85fc836d3 -->

**Amortized Analysis** measures the average cost per operation across a **guaranteed sequence of operations**, where rare expensive steps are paid for by many cheap steps.

### Dynamic Array Append Example
- **Normal Push**: $O(1)$ constant time (adding item to open slot).
- **Resize Push (when full)**: $O(n)$ time (allocating $2\times$ array and copying $N$ items).

Because capacity **doubles**, appending $N$ items produces total copy work of $1 + 2 + 4 + \dots + N/2 = N - 1$ copies.

$$\text{Amortized Cost per Append} = \frac{\text{Total Work}}{\text{Total Appends}} = \frac{O(N)}{N} = \mathbf{O(1)}$$

---

## 6. Reading Constraints to Guess the Intended Big-O
<!-- bite: c64eb672-0d9c-451e-8ca2-9e6468c4ef15 -->

In competitive programming and technical interviews, the problem's **input size ($N$) constraint** directly tells you which Big-O complexity is expected:

| Input Constraint ($N$) | Maximum Allowed Time Complexity | Expected Algorithm Family |
| :--- | :--- | :--- |
| $N \le 12$ | **$O(N!)$** | Brute-force permutations, Backtracking. |
| $N \le 25$ | **$O(2^N)$** | Subset generation, Recursive Bitmask DP. |
| $N \le 500$ | **$O(N^3)$** | Floyd-Warshall shortest path, Triple nested loops. |
| $N \le 10,000$ | **$O(N^2)$** | Quadratic sorts (Selection, Insertion), Double nested loops. |
| $N \le 1,000,000$ | **$O(N \log N)$ or $O(N)$** | Merge Sort, Quickselect, Hash Maps, Two Pointers, Monotonic Stack. |
| $N > 10,000,000$ | **$O(\log N)$ or $O(1)$** | Binary Search, Math formulas, Bitwise operations. |

---

## 7. Space Complexity: Auxiliary vs. Total
<!-- bite: dbab4fee-de6f-4f4d-8df2-ec30a86b8f2c -->

- **Total Space**: Total memory required, including input arrays.
- **Auxiliary Space**: Extra temporary memory allocated by the algorithm *excluding* the input.
- **In-Place Algorithm**: An algorithm with **$O(1)$ Auxiliary Space** (modifies data directly inside input array).

> [!CAUTION]
> **The Hidden Call Stack**: Recursive functions consume auxiliary memory on the CPU call stack proportional to maximum recursion depth $h$! A recursive function with no variable allocations still takes **$O(h)$ space**.

---

## Implementation — complete runnable example
<!-- bite: 99857968-3bde-49e6-b155-5e36faf08c3a -->

**Runnable example:** save as `complexity.py` in any empty directory and run `python3 complexity.py`. Standard library only; writes no files.

The lab counts **operations**, not seconds. Wall-clock time varies with machine, load and interpreter; operation counts are the thing the notation actually describes, and they are reproducible.

```python
"""Growth rates, recurrences and amortised cost - counted, not timed."""
import math


class Counter:
    def __init__(self):
        self.ops = 0


def constant(xs, c):
    c.ops += 1
    return xs[0] if xs else None


def logarithmic(xs, c):
    """Binary search for a value that is not present: the full log2(n) descent."""
    lo, hi = 0, len(xs) - 1
    while lo <= hi:
        c.ops += 1
        mid = (lo + hi) // 2
        if xs[mid] < -1:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def linear(xs, c):
    total = 0
    for v in xs:
        c.ops += 1
        total += v
    return total


def linearithmic(xs, c):
    """Merge sort's shape: log2(n) levels, n work per level."""
    if len(xs) <= 1:
        return xs
    mid = len(xs) // 2
    left = linearithmic(xs[:mid], c)
    right = linearithmic(xs[mid:], c)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        c.ops += 1
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    c.ops += len(left) - i + len(right) - j
    out.extend(left[i:]); out.extend(right[j:])
    return out


def quadratic(xs, c):
    best = 0
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            c.ops += 1
            best = max(best, xs[j] - xs[i])
    return best


class DynamicArray:
    """A resizable array that doubles, so the copying cost can be counted."""

    def __init__(self):
        self.capacity = 1
        self.size = 0
        self.copies = 0
        self.resizes = 0

    def append(self, _value):
        if self.size == self.capacity:
            self.copies += self.size          # every existing element is moved
            self.resizes += 1
            self.capacity *= 2
        self.size += 1


if __name__ == "__main__":
    print("Block 1 - growth rates, measured by doubling n")
    funcs = [("O(1)      ", constant), ("O(log n)  ", logarithmic),
             ("O(n)      ", linear), ("O(n log n)", linearithmic),
             ("O(n^2)    ", quadratic)]
    sizes = [100, 200, 400, 800]
    print("   complexity   " + "".join(f"{n:>10}" for n in sizes) + "     ratio per doubling")
    for label, fn in funcs:
        counts = []
        for n in sizes:
            c = Counter()
            fn(list(range(n)), c)
            counts.append(c.ops)
        ratios = [counts[i + 1] / counts[i] for i in range(len(counts) - 1)]
        avg = sum(ratios) / len(ratios)
        print(f"   {label}   " + "".join(f"{v:>10,}" for v in counts) + f"       {avg:.2f}x")
    # the ratio per doubling IS the complexity, read off directly
    c1, c2 = Counter(), Counter()
    linear(list(range(400)), c1); linear(list(range(800)), c2)
    assert abs(c2.ops / c1.ops - 2.0) < 0.01, "linear doubles"
    q1, q2 = Counter(), Counter()
    quadratic(list(range(400)), q1); quadratic(list(range(800)), q2)
    assert 3.9 < q2.ops / q1.ops < 4.1, "quadratic quadruples"
    print("  double n: O(n) doubles, O(n^2) QUADRUPLES, O(log n) adds one step")
    print("  that ratio column is the complexity, read straight off the measurements")

    print()
    print("Block 2 - the recurrence, checked against the measurement")
    print("        n   measured merge ops   n*log2(n)   ratio")
    for n in (64, 256, 1024, 4096):
        c = Counter()
        linearithmic(list(range(n, 0, -1)), c)
        pred = n * math.log2(n)
        print(f"   {n:6}   {c.ops:18,}   {pred:9,.0f}   {c.ops/pred:.2f}")
    print("  T(n) = 2T(n/2) + O(n): log2(n) levels, O(n) per level -> O(n log n)")

    print()
    print("Block 3 - amortised: why append is O(1) despite copying")
    print("        n   resizes   total elements copied   copies per append")
    for n in (10, 100, 1000, 10000, 100000):
        arr = DynamicArray()
        for i in range(n):
            arr.append(i)
        print(f"   {n:6}   {arr.resizes:7}   {arr.copies:21,}   {arr.copies/n:17.3f}")
    arr = DynamicArray()
    for i in range(100000):
        arr.append(i)
    assert arr.copies < 2 * 100000, "total copying is bounded by 2n"
    assert arr.resizes == math.ceil(math.log2(100000)) + 1 or arr.resizes <= 18
    print("  total copying stays under 2n, so the AVERAGE append is O(1)")
    print("  a single append can still be O(n) - amortised is about the total,")
    print("  not about any one operation. That distinction matters for latency.")

    print()
    print("  and this is why DOUBLING matters - growing by a fixed 1 instead:")

    class GrowByOne(DynamicArray):
        def append(self, _value):
            if self.size == self.capacity:
                self.copies += self.size
                self.resizes += 1
                self.capacity += 1
            self.size += 1

    for n in (100, 1000, 10000):
        a = GrowByOne()
        for i in range(n):
            a.append(i)
        print(f"    n={n:6}: copies {a.copies:12,}   ({a.copies/n:8.1f} per append)")
    a = GrowByOne()
    for i in range(1000):
        a.append(i)
    assert a.copies > 400000, "growing by one is quadratic overall"
    print("    growing by one copies ~n^2/2 in total: each append becomes O(n)")

    print()
    print("Block 4 - reading constraints to guess the intended complexity")
    print("       n         feasible complexity        rough operations")
    budget = 10 ** 8
    for n, label in ((10, "O(n!)"), (25, "O(2^n)"), (500, "O(n^3)"),
                     (5000, "O(n^2)"), (10 ** 6, "O(n log n)"), (10 ** 9, "O(n) or O(log n)")):
        est = {"O(n!)": math.factorial(min(n, 12)), "O(2^n)": 2 ** min(n, 40),
               "O(n^3)": n ** 3, "O(n^2)": n ** 2,
               "O(n log n)": n * math.log2(n), "O(n) or O(log n)": n}[label]
        print(f"  {n:>10,}   {label:>24}   {est:>20,.0f}")
    print(f"  the working rule: about {budget:,} simple operations per second")
    print("  so n <= 10^4 admits O(n^2); n = 10^6 demands O(n log n) or better")

    print()
    print("complexity: passed")
```

Expected output:

```text
Block 1 - growth rates, measured by doubling n
   complexity          100       200       400       800     ratio per doubling
   O(1)                  1         1         1         1       1.00x
   O(log n)              6         7         8         9       1.14x
   O(n)                100       200       400       800       2.00x
   O(n log n)          672     1,544     3,488     7,776       2.26x
   O(n^2)            4,950    19,900    79,800   319,600       4.01x
  double n: O(n) doubles, O(n^2) QUADRUPLES, O(log n) adds one step
  that ratio column is the complexity, read straight off the measurements

Block 2 - the recurrence, checked against the measurement
        n   measured merge ops   n*log2(n)   ratio
       64                  384         384   1.00
      256                2,048       2,048   1.00
     1024               10,240      10,240   1.00
     4096               49,152      49,152   1.00
  T(n) = 2T(n/2) + O(n): log2(n) levels, O(n) per level -> O(n log n)

Block 3 - amortised: why append is O(1) despite copying
        n   resizes   total elements copied   copies per append
       10         4                      15               1.500
      100         7                     127               1.270
     1000        10                   1,023               1.023
    10000        14                  16,383               1.638
   100000        17                 131,071               1.311
  total copying stays under 2n, so the AVERAGE append is O(1)
  a single append can still be O(n) - amortised is about the total,
  not about any one operation. That distinction matters for latency.

  and this is why DOUBLING matters - growing by a fixed 1 instead:
    n=   100: copies        4,950   (    49.5 per append)
    n=  1000: copies      499,500   (   499.5 per append)
    n= 10000: copies   49,995,000   (  4999.5 per append)
    growing by one copies ~n^2/2 in total: each append becomes O(n)

Block 4 - reading constraints to guess the intended complexity
       n         feasible complexity        rough operations
          10                      O(n!)              3,628,800
          25                     O(2^n)             33,554,432
         500                     O(n^3)            125,000,000
       5,000                     O(n^2)             25,000,000
   1,000,000                 O(n log n)             19,931,569
  1,000,000,000           O(n) or O(log n)          1,000,000,000
  the working rule: about 100,000,000 simple operations per second
  so n <= 10^4 admits O(n^2); n = 10^6 demands O(n log n) or better

complexity: passed
```

Block 1 is the lesson in one table: the **ratio per doubling** *is* the complexity. Linear doubles, quadratic quadruples, logarithmic barely moves — measured, not recited.

## 8. Common Pitfalls & Traps
<!-- bite: 8c6d2498-dd8f-464f-bab5-0c49f7e86f96 -->

1. **Dropping Lower-Order Terms**: $O(n^2 + n)$ simplifies strictly to **$O(n^2)$**, as $n^2$ completely dominates $n$ for large inputs.
2. **Confusing Variables**: If an algorithm processes an array of length $N$ and a string of length $M$, the complexity is **$O(N \cdot M)$**, NOT $O(N^2)$!
3. **Ignoring Constants at Small Scale**: For small inputs ($N < 20$), an $O(n^2)$ Insertion Sort runs faster than an $O(n \log n)$ Quick Sort due to lower constant overhead.

---

## Check your understanding
<!-- bite: 91ddc1aa-ba6f-49dd-b313-c0efde9c31b8 -->

Try each one before you open the answer.

1. <!-- q: mcq id="bb1092c4" -->
   Big-Θ is a tight bound. When does T(n) = Θ(f(n)) hold?

   - [ ] When T(n) = O(f(n)) holds, whatever the lower bound
   - [ ] When T(n) = Ω(f(n)) holds, whatever the upper bound
   - [x] When both T(n) = O(f(n)) and T(n) = Ω(f(n)) hold
   - [ ] Only in the worst case

   <details><summary>Answer</summary>

   Θ means the growth is sandwiched: at most c₂·f(n) (the O part) and at least c₁·f(n) (the Ω part). You need both.

   </details>

2. <!-- q: gap id="672eb141" answers="Θ(1)|O(1)|1|constant;Θ(n)|O(n)|n|linear" -->
   Fill in the gaps. Linear search looks through an unsorted array of n items for a target. If the target is at index 0, the cost is ___. If the target is missing, the cost is ___.

   <details><summary>Answer</summary>

   Θ(1) in the best case, because the first check finds it. Θ(n) in the worst case, because every item is checked before giving up.

   </details>

3. <!-- q: mcq id="7e5e0704" -->
   A problem says the input array has N ≤ 1,000,000 items and the time limit is 1 second. Which complexity should your solution aim for?

   - [ ] O(N³)
   - [ ] O(N²)
   - [x] O(N log N) or O(N)
   - [ ] O(2^N)

   <details><summary>Answer</summary>

   O(N²) would be about 10¹² steps, far too many. At around 10⁸ simple steps per second, only O(N log N) or O(N) fits.

   </details>

4. <!-- q: mcq id="2d0e5169" -->
   A recursive depth-first search on a binary tree of height H declares no local variables. How much auxiliary space does it use?

   - [ ] O(1), because it creates no variables
   - [x] O(H), because each active call keeps a stack frame
   - [ ] O(2^H), one frame per node
   - [ ] O(n²)

   <details><summary>Answer</summary>

   Every call that has not returned yet holds a frame on the call stack. At the deepest point there are H of them, so the hidden cost is O(H).

   </details>

5. <!-- q: open id="245bcd1f" -->
   A hash map lookup is Θ(1) on average but Θ(n) in the worst case. Why do engineers design production systems around the worst case?

   <details><summary>Answer</summary>

   Because an attacker can choose the input. By sending keys that all collide into one bucket (hash flooding), they turn every lookup into the Θ(n) case and slow or crash the service. The average case only holds when the input is not hostile, so a safe system must survive the worst case.

   </details>

## Check your understanding: worked problems
<!-- bite: 6fc12de7-acff-4bbe-b03a-d2c8c27c9151 -->

Work each one out on paper first, then type your answer.

1. <!-- q: exact id="0b0ceb87" answer="55" -->
   How many times does `count += 1` run when n = 10?

   ```python
   count = 0
   for i in range(n):
       for j in range(i, n):
           count += 1
   ```

   <details><summary>Answer</summary>

   55. The inner loop runs 10, 9, 8, … 1 times, and 10 + 9 + … + 1 = 10 × 11 / 2 = 55. That is about n²/2, so the loop is O(n²).

   </details>

2. <!-- q: exact id="6c761f2f" answer="24" -->
   How many times does `count += 1` run when n = 8?

   ```python
   count = 0
   for i in range(n):
       j = 1
       while j < n:
           count += 1
           j *= 2
   ```

   <details><summary>Answer</summary>

   24. The inner loop doubles j from 1 while j < 8, so it runs for j = 1, 2, 4: three times, which is log₂ 8. The outer loop repeats that 8 times: 8 × 3 = 24. This is the n log n shape.

   </details>

3. <!-- q: exact id="46dd92e0" answer="10000" accept="10,000|1e4" -->
   An O(n²) algorithm does n² simple steps. n = 1,000,000 and the machine does 10⁸ steps per second. How many seconds does it take?

   <details><summary>Answer</summary>

   10,000 seconds, almost 3 hours. n² = 10¹², and 10¹² / 10⁸ = 10⁴. An O(n log n) algorithm on the same input would take about 0.2 seconds.

   </details>

4. <!-- q: exact id="26bfedca" answer="9" -->
   Binary search runs on a sorted array of 1,000 items (indexes 0 to 999), looking for a value smaller than every item. It uses `while lo <= hi`, `mid = (lo + hi) // 2` and sets `hi = mid - 1` each time. How many times does the loop body run?

   <details><summary>Answer</summary>

   9. hi falls 999 → 498 → 248 → 123 → 60 → 29 → 13 → 5 → 1 → −1, one loop each time. That is about log₂ 1000 ≈ 10, so the search is O(log n).

   </details>

## Practice — independent task
<!-- bite: 33554fa1-63ec-4c19-a750-ec0f748191c9 -->

Implement `classify_growth(fn, sizes)` — infer an algorithm's complexity from measurements alone, without reading its source.

1. Run `fn` at each size, counting operations (pass in a counter, as the lab does).
2. Compute the ratio between consecutive counts when $n$ doubles. Map the ratio to a class: $\approx 1$ is $O(1)$, slightly above 1 is $O(\log n)$, $\approx 2$ is $O(n)$, a little above 2 is $O(n\log n)$, $\approx 4$ is $O(n^2)$, $\approx 8$ is $O(n^3)$.
3. Report a **confidence**: how consistent the ratios are across sizes. A single ratio proves nothing; three that agree is evidence.
4. Test it on functions whose complexity you know, including at least one $O(n\log n)$ — the case hardest to distinguish from $O(n)$ at small $n$. Report the smallest $n$ at which your classifier separates them reliably.
5. **Then find its limits.** Write a function that is $O(n)$ but with a huge constant, and one that is $O(n^2)$ only for $n > 1000$ (linear below that). Show what your classifier says about each, and explain why asymptotic classification from small samples is unreliable in exactly those two ways.

**Edge cases:** a function whose count is zero at small $n$ (division by zero in the ratio); a function with randomised behaviour (average over several runs, with a fixed seed); sizes too small to be in the asymptotic regime at all.

**Done when:** your classifier gets the known cases right, you can state the $n$ at which it separates $O(n)$ from $O(n\log n)$, and you can explain both failure modes from step 5 with numbers you produced.

## Before moving on
<!-- bite: 56d17e0c-6300-476f-90d1-85b7e3de717a -->

You are done with this lesson when you can:

- Use $O$, $\Omega$ and $\Theta$ correctly, and say what is wrong with "the best case is $O(n)$" as a phrasing habit.
- Derive $O(n\log n)$ for merge sort from its recurrence, without looking it up.
- Explain amortised $O(1)$ append, and why a single append can still be slow.
- Look at $n \le 10^5$ in a problem statement and name the complexities that will pass.

**Recap for later lookup:** $O$ is an upper bound, $\Omega$ a lower bound, $\Theta$ both; worst case is the production standard because it is the only guarantee; a recurrence $T(n) = aT(n/b) + f(n)$ is read off the recursion tree — levels times work per level; amortised cost averages over a sequence, and doubling makes total copying $< 2n$; roughly $10^8$ simple operations per second is the rule for reading constraints.

**Next:** [[01-depth-first-search|Depth-First Search]] — the first algorithm whose cost you will analyse with this vocabulary.

## Related Modules
<!-- bite: c36a37ab-833f-452b-bce3-049feb5d56ff -->
- [[dsa/01-loops-and-what-they-cost|Loops and What They Cost]] — Practical loop counting rules
- [[02-dynamic-arrays|Dynamic Arrays]] — Amortized analysis application
- [[05-sorting/index|Sorting Algorithms]] — Comparison sort lower bounds ($O(n \log n)$)
