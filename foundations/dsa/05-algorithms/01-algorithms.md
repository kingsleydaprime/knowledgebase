# Module: Algorithms & Complexity Analysis (Big-O, Bounds & Space)

Welcome to the **Algorithms & Complexity Analysis** module. An **Algorithm** is a finite, well-defined sequence of instructions designed to transform an input into a desired output.

This module introduces the mathematical vocabulary—**Big-O**, **Big-$\Omega$**, and **Big-$\Theta$**—used by computer scientists to evaluate, compare, and optimize software performance across all engineering disciplines.

---

## 1. Why Growth Rate Matters (Real-World Motivation)

Suppose you need to compare two sorting programs:

- **Method A**: Tested on your high-end gaming laptop $\rightarrow$ finishes in **2.5 seconds**.
- **Method B**: Tested on a cheap server $\rightarrow$ finishes in **5.0 seconds**.

Does this mean Method A is a better algorithm? **Not necessarily!** If you run Method A on a slow phone, it might take 20 seconds. 

Measuring runtime in seconds is unreliable because it depends on hardware speed, programming language overhead, and CPU load.

### Measuring Growth Rate instead of Time
Instead of measuring seconds, computer science measures **how the workload grows as input size ($n$) scales to infinity**:

```
Input Size (n)   | O(1) Constant | O(n) Linear | O(n log n)    | O(n²) Quadratic
---------------------------------------------------------------------------------
n = 10           | < 1 µs        | < 1 µs      | < 1 µs        | < 1 µs
n = 1,000        | < 1 µs        | < 1 µs      | 10 µs         | 1 millisecond
n = 1,000,000    | < 1 µs        | 10 ms       | 0.2 seconds   | 11 DAYS!
```

> [!KEY-INSIGHT]
> At $n = 1,000,000$, an $O(n^2)$ algorithm takes **11 days**, while an $O(n \log n)$ algorithm finishes in **0.2 seconds** on the exact same computer!

---

## 2. The Three Asymptotics: $O$, $\Omega$, and $\Theta$

In computer science, we use three mathematical notations to bound an algorithm's growth function $T(n)$:

```
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

The mathematical bounds ($O, \Omega, \Theta$) are independent of the input scenarios (Best, Average, Worst):

- **Best-Case**: The input configuration that requires the absolute minimum operations (e.g. searching for an item that happens to be at index 0 $\rightarrow \Theta(1)$).
- **Average-Case**: Expected work averaged over all probable inputs.
- **Worst-Case**: The input configuration that causes maximum possible work (e.g. searching for an item that is missing $\rightarrow \Theta(n)$).

### Security Aspect: Why Worst-Case is the Production Standard
A [[03-hash-maps|Hash Map]] operates in average **$\Theta(1)$ time**, but degrades to **$\Theta(n)$ worst-case** when all keys collide into a single bucket. 

Attackers can intentionally exploit this gap by sending malicious input data designed to trigger worst-case performance (**Hash-Flooding Denial of Service Attack**). Software engineers design systems against the **Worst-Case**!

---

## 4. Derived Recursive Complexity (Recurrence Trees)

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

**Amortized Analysis** measures the average cost per operation across a **guaranteed sequence of operations**, where rare expensive steps are paid for by many cheap steps.

### Dynamic Array Append Example
- **Normal Push**: $O(1)$ constant time (adding item to open slot).
- **Resize Push (when full)**: $O(n)$ time (allocating $2\times$ array and copying $N$ items).

Because capacity **doubles**, appending $N$ items produces total copy work of $1 + 2 + 4 + \dots + N/2 = N - 1$ copies.

$$\text{Amortized Cost per Append} = \frac{\text{Total Work}}{\text{Total Appends}} = \frac{O(N)}{N} = \mathbf{O(1)}$$

---

## 6. Reading Constraints to Guess the Intended Big-O

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

- **Total Space**: Total memory required, including input arrays.
- **Auxiliary Space**: Extra temporary memory allocated by the algorithm *excluding* the input.
- **In-Place Algorithm**: An algorithm with **$O(1)$ Auxiliary Space** (modifies data directly inside input array).

> [!CAUTION]
> **The Hidden Call Stack**: Recursive functions consume auxiliary memory on the CPU call stack proportional to maximum recursion depth $h$! A recursive function with no variable allocations still takes **$O(h)$ space**.

---

## 8. Common Pitfalls & Traps

1. **Dropping Lower-Order Terms**: $O(n^2 + n)$ simplifies strictly to **$O(n^2)$**, as $n^2$ completely dominates $n$ for large inputs.
2. **Confusing Variables**: If an algorithm processes an array of length $N$ and a string of length $M$, the complexity is **$O(N \cdot M)$**, NOT $O(N^2)$!
3. **Ignoring Constants at Small Scale**: For small inputs ($N < 20$), an $O(n^2)$ Insertion Sort runs faster than an $O(n \log n)$ Quick Sort due to lower constant overhead.

---

## 9. Check Your Understanding (University Self-Assessment)

1. **Question**: What is the difference between Big-O ($O$), Big-Omega ($\Omega$), and Big-Theta ($\Theta$)?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>Big-O</b> represents the mathematical upper bound (worst-case curve). <b>Big-Omega</b> represents the lower bound (at-least curve). <b>Big-Theta</b> represents a tight bound where an algorithm's growth is sandwiched precisely between upper and lower bounds.</details>

2. **Question**: If a problem states that input array size $N \le 1,000,000$, will a double nested loop ($O(N^2)$) pass within a 1-second execution time limit?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>No!</b> An $O(N²)$ algorithm on $N = 1,000,000$ requires $10^{12}$ operations (taking ~11 days at $10^8$ ops/sec). You must use an <b>O(N log N)</b> or <b>O(N)</b> solution.</details>

3. **Question**: Why is recursive Depth-First Search (DFS) on a binary tree of height $H$ described as taking $O(H)$ space, even if the function creates no local variables?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Each active recursive call pushes a stack frame onto the system call stack. At maximum depth, the call stack contains $H$ stack frames, using <b>O(H) auxiliary space</b>.</details>

---

## Related Modules
- [[foundations/dsa/01-loops-and-what-they-cost|Loops and What They Cost]] — Practical loop counting rules
- [[02-dynamic-arrays|Dynamic Arrays]] — Amortized analysis application
- [[04-sorting|Sorting Algorithms]] — Comparison sort lower bounds ($O(n \log n)$)
