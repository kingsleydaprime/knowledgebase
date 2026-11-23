---
id: 134aefda-ab9a-41aa-8b69-740ebc02ca9f
---

# Module: Loops and What They Cost (Counting Computer Work)

Welcome to the foundation of **Data Structures & Algorithms**. Big-O notation looks like abstract mathematics, but at its heart, it is simply **counting how many times a loop repeats**.

Understanding what loops cost is the single most important skill for predicting whether code will run in milliseconds or take hours to finish.

---

## 1. Why Loop Counting Matters (Real-World Motivation)
<!-- bite: c59b8917-7ca8-412f-a311-8b56515a1d9f -->

Imagine you are tasked with managing an event for $1,000$ guests:

1. **Task A (Single Pass)**: You hand a name badge to each guest as they arrive.
   - You repeat the action $1,000$ times. It takes about **15 minutes**.
2. **Task B (Pairwise Comparison)**: You ask every single guest to introduce themselves to every other guest to make sure no two people have the same full name.
   - Guest 1 speaks to 999 people. Guest 2 speaks to 998 people...
   - Total introductions: $\approx \frac{1000 \times 1000}{2} = 500,000$ handshakes!
   - This takes over **300 hours**!

In programming, **Task A is a single loop ($O(n)$)**, while **Task B is a nested loop ($O(n^2)$)**. Both operate on the exact same 1,000 guests, but the nested loop takes $500\times$ longer.

---

## 2. Plain-English Terminology & Concept Table
<!-- bite: 5b60a149-79fb-4f62-873e-8382a1e658e0 -->

| Term | Plain-English Definition | Real-World Example |
| :--- | :--- | :--- |
| **Input Size ($n$)** | The number of items your code has to process. | 1,000 array elements, 1 million database records. |
| **Iteration** | One single cycle through a loop's body. | Processing item #4 out of 10. |
| **Linear Time ($O(n)$)** | Work increases in direct proportion to input size ($n$). | Doubling input size doubles the running time. |
| **Quadratic Time ($O(n^2)$)** | Work increases with the square of the input size ($n \times n$). | Doubling input size multiplies running time by 4. |
| **Logarithmic Time ($O(\log n)$)** | Work grows incredibly slowly because the remaining items are cut in half each step. | 1,000 items $\rightarrow$ 10 steps; 1,000,000 items $\rightarrow$ 20 steps. |

---

## 3. The Two Fundamental Loop Types
<!-- bite: 366fddaf-934c-4d83-a6f2-f7e805c6a685 -->

Before analyzing performance, let's contrast the two ways loops are written in code:

### 1. The `for` Loop (Known Repetitions)
A `for` loop announces its iteration count upfront in its header:

```python
# Runs exactly 5 times (i = 0, 1, 2, 3, 4)
for i in range(5):
    print("Iteration:", i)
```

### 2. The `while` Loop (Condition-Driven Repetitions)
A `while` loop runs until a condition changes. Its total iterations depend on how variables change **inside** the loop body:

```python
count = 100
while count > 1:
    count = count // 2  # Halves count on every pass!
```

---

## 4. How to Count Loop Iterations (Rules of Complexity)
<!-- bite: cb2d1b2f-2da8-4c87-84e1-b08549c1894f -->

### Rule 1: Sequential Loops ADD ($O(n) + O(n) = O(n)$)
If two loops run one after another, their costs add up:

```python
# First loop: runs n times
for i in range(n):
    do_something()

# Second loop: runs n times
for j in range(n):
    do_something_else()
```
- Total steps: $n + n = 2n$.
- In Big-O, we drop constant multipliers ($2$), so $2n$ is categorized as **$O(n)$ (Linear Time)**.

---

### Rule 2: Nested Loops MULTIPLY ($O(n) \times O(n) = O(n^2)$)
If a loop is placed inside another loop, the inner loop restarts completely for **every single step** of the outer loop:

```python
# Outer loop runs n times
for i in range(n):
    # Inner loop runs n times for EACH outer iteration
    for j in range(n):
        print(i, j)
```

#### Iteration Visual Trace Table (for $n = 3$)

| Outer Loop ($i$) | Inner Loop ($j$) | Execution Count |
| :--- | :--- | :--- |
| `i = 0` | `j = 0, 1, 2` | 3 steps |
| `i = 1` | `j = 0, 1, 2` | 3 steps |
| `i = 2` | `j = 0, 1, 2` | 3 steps |
| **Total Steps** | $3 \times 3 = 9$ steps | **$n^2 = 9$** |

At $n = 1,000$, $n^2$ is **1,000,000 iterations**. This multiplication is why nesting is the #1 source of slow code!

---

### Rule 3: Triangular Loops are Still $O(n^2)$
What if the inner loop starts where the outer loop is currently at?

```python
for i in range(n):
    for j in range(i, n):  # Runs n, then n-1, then n-2...
        do_work()
```
- Total iterations: $n + (n-1) + (n-2) + \dots + 1 = \frac{n(n+1)}{2} = \frac{n^2 + n}{2}$.
- Even though it performs half as many steps as a full square loop, dropping constants leaves us with **$O(n^2)$**.

---

### Rule 4: Loops That Halve are Logarithmic ($O(\log n)$)
When a loop variable is divided by 2 (or multiplied by 2) each step, it cuts the problem size in half:

```python
i = n
while i > 1:
    i = i // 2  # n -> n/2 -> n/4 -> ... -> 1
```

#### Why $O(\log n)$ is a Superpower:
- $n = 1,000 \rightarrow$ runs **10 times**.
- $n = 1,000,000 \rightarrow$ runs **20 times**.
- $n = 1,000,000,000 \rightarrow$ runs **30 times**.

Halving is what makes **Binary Search**, **Balanced Trees**, and **Heaps** lightning fast!

---

## 5. The Hidden Loop Trap
<!-- bite: 99eaf7dd-3694-44de-8f7c-bab21deb0852 -->

> [!WARNING]
> An operation that reads as a single line of code may contain a secret loop under the hood!

Your code might look like one loop, but the computer executes two:

```python
# DANGEROUS: Looks like O(n), but actually O(n²)!
for item in items:           # Outer loop runs n times
    if item in seen_list:    # HIDDEN LOOP: "in list" scans the list lineally -> O(n)!
        print("Duplicate found")
```

### Common Hidden Loops in Python/JavaScript:

1. **`x in python_list`**: Walks the list element-by-element ($O(n)$).
   - *Fix*: Swap `list` for a `set` or `dict` ($O(1)$ address lookup).
2. **`list.insert(0, item)`**: Inserts at index 0, forcing every existing element to shift right by 1 ($O(n)$).
3. **String concatenation inside a loop (`str += char`)**: Rebuilds the entire string in memory each time ($O(n^2)$ total).
   - *Fix*: Append characters to a list and call `''.join(list)` at the end ($O(n)$).

---

## 6. Common Pitfalls & Traps
<!-- bite: 2242a610-44f0-4f6e-91f0-abdddca208b3 -->

- **Infinite `while` Loops**: Forgetting to update the loop condition variable inside the body causes the loop to run forever.
- **Off-By-One Errors**: `range(n)` in Python produces indices from `0` to `n-1`. Accessing `arr[n]` triggers an `IndexError`.
- **Modifying Collections While Iterating**: Adding or removing items from a list while looping over it skips elements or causes unpredictable crashes.

---

## Check your understanding
<!-- bite: c658cd3f-c430-4bf6-a0ef-d482996fbd4d -->

Try each one before you open the answer.

1. <!-- q: mcq id="1d01c1ea" -->
   Loop 1 runs n times. When it finishes, loop 2 runs n times. Neither loop is inside the other. What is the total time complexity?

   - [x] O(n)
   - [ ] O(n²)
   - [ ] O(2n²)
   - [ ] O(log n)

   <details><summary>Answer</summary>

   O(n). Loops one after another add: n + n = 2n, and Big-O drops the constant 2.

   </details>

2. <!-- q: mcq id="28464940" -->
   This code looks like one loop. What is its real time complexity when `items` and `seen_list` both hold about n values, and `seen_list` is a Python list?

   ```python
   for item in items:
       if item in seen_list:
           print("Duplicate found")
   ```

   - [ ] O(n), because there is only one `for`
   - [x] O(n²), because `in` on a list scans it
   - [ ] O(log n), because `in` halves the list
   - [ ] O(1), because `in` is a single line

   <details><summary>Answer</summary>

   O(n²). `item in seen_list` walks the list one element at a time, so it is a hidden O(n) loop inside an O(n) loop. Making `seen_list` a set turns each check into O(1).

   </details>

3. <!-- q: gap id="bd73d8ff" answers="multiply|multiplies;add|adds" -->
   Fill in the gaps. When one loop sits inside another, their costs ___. When one loop runs after another, their costs ___.

   <details><summary>Answer</summary>

   Nested loops multiply, because the inner loop restarts for every step of the outer one. Sequential loops add.

   </details>

4. <!-- q: mcq id="3224fc2b" -->
   Which of these lines hides a loop that costs O(n) on a Python list or string of length n? Choose all that apply.

   - [x] `my_list.insert(0, item)`
   - [x] `if x in my_list:`
   - [x] `text += char` (copying the whole string)
   - [ ] `my_list[5]`

   <details><summary>Answer</summary>

   The first three. Inserting at index 0 shifts every element right, `in` scans the list, and `+=` on an immutable string builds a new copy. Indexing `my_list[5]` is one address calculation, O(1).

   </details>

5. <!-- q: exact id="fb158961" answer="20" accept="about 20|~20" -->
   A loop cuts the remaining work in half on every pass. Roughly how many passes does it take to get from 1,000,000 items down to 1?

   <details><summary>Answer</summary>

   About 20. 2²⁰ is about a million, so halving a million 20 times reaches 1. This is O(log n).

   </details>

6. <!-- q: open id="8a4c1cd7" -->
   A triangular loop does `for i in range(n): for j in range(i, n):`. It does about half the work of a full n × n nested loop. Why is it still called O(n²)?

   <details><summary>Answer</summary>

   It runs n + (n−1) + … + 1 = n(n+1)/2 times, which is n²/2 + n/2. Big-O keeps only the fastest-growing term and drops constant factors, so the ½ disappears and n² is left. Doubling n still multiplies the work by about 4.

   </details>

## Check your understanding: worked problems
<!-- bite: 4b218852-42d4-4705-827c-db6b030340a9 -->

Work each one out on paper first, then type your answer.

1. <!-- q: exact id="27498211" answer="21" -->
   How many times does `work()` run when n = 6?

   ```python
   for i in range(n):
       for j in range(i, n):
           work()
   ```

   <details><summary>Answer</summary>

   21. The inner loop runs 6, 5, 4, 3, 2, 1 times, and 6 + 5 + 4 + 3 + 2 + 1 = 6 × 7 / 2 = 21.

   </details>

2. <!-- q: exact id="67b1bc39" answer="6" -->
   How many times does the loop body run when n = 100? (`//` is whole-number division.)

   ```python
   i = n
   while i > 1:
       i = i // 2
   ```

   <details><summary>Answer</summary>

   6. i goes 100 → 50 → 25 → 12 → 6 → 3 → 1, which is 6 passes. That is about log₂ 100 ≈ 6.6, rounded down.

   </details>

3. <!-- q: exact id="13333ac2" answer="110" -->
   How many times does `step()` run in total when n = 10?

   ```python
   for i in range(n):
       step()
   for i in range(n):
       for j in range(n):
           step()
   ```

   <details><summary>Answer</summary>

   110. The first loop runs 10 times and the nested pair runs 10 × 10 = 100 times. They are one after another, so 10 + 100 = 110. In Big-O that is O(n²).

   </details>

4. <!-- q: exact id="c2a62ddd" answer="5" -->
   How many times does the loop body run when n = 100?

   ```python
   i = 1
   while i < n:
       i = i * 3
   ```

   <details><summary>Answer</summary>

   5. i goes 1 → 3 → 9 → 27 → 81 → 243. After 5 passes i is 243, which is no longer below 100. Multiplying by 3 each step makes it O(log n), base 3.

   </details>

## Related Modules
<!-- bite: c649ba64-7654-49aa-8be1-ee4607e4a307 -->
- [[01-growth-and-asymptotic-notation|Algorithms & Complexity Analysis]] — Formalizing Big-O, $\Omega$, $\Theta$, and space complexity
- [[01-arrays|Arrays]] — Why array indexing is $O(1)$ without loops
- [[03-hash-maps|Hash Maps]] — How hash maps eliminate hidden lookup loops
