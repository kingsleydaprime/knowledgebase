# Module: Loops and What They Cost (Counting Computer Work)

Welcome to the foundation of **Data Structures & Algorithms**. Big-O notation looks like abstract mathematics, but at its heart, it is simply **counting how many times a loop repeats**.

Understanding what loops cost is the single most important skill for predicting whether code will run in milliseconds or take hours to finish.

---

## 1. Why Loop Counting Matters (Real-World Motivation)

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

| Term | Plain-English Definition | Real-World Example |
| :--- | :--- | :--- |
| **Input Size ($n$)** | The number of items your code has to process. | 1,000 array elements, 1 million database records. |
| **Iteration** | One single cycle through a loop's body. | Processing item #4 out of 10. |
| **Linear Time ($O(n)$)** | Work increases in direct proportion to input size ($n$). | Doubling input size doubles the running time. |
| **Quadratic Time ($O(n^2)$)** | Work increases with the square of the input size ($n \times n$). | Doubling input size multiplies running time by 4. |
| **Logarithmic Time ($O(\log n)$)** | Work grows incredibly slowly because the remaining items are cut in half each step. | 1,000 items $\rightarrow$ 10 steps; 1,000,000 items $\rightarrow$ 20 steps. |

---

## 3. The Two Fundamental Loop Types

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

- **Infinite `while` Loops**: Forgetting to update the loop condition variable inside the body causes the loop to run forever.
- **Off-By-One Errors**: `range(n)` in Python produces indices from `0` to `n-1`. Accessing `arr[n]` triggers an `IndexError`.
- **Modifying Collections While Iterating**: Adding or removing items from a list while looping over it skips elements or causes unpredictable crashes.

---

## 7. Check Your Understanding (University Self-Assessment)

1. **Question**: You have two loops. Loop 1 runs $n$ times. Loop 2 runs $n$ times right after Loop 1 finishes. What is the total time complexity?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>O(n)</b> (Linear Time). Sequential loops add: n + n = 2n, and constant factors are dropped in Big-O notation.</details>

2. **Question**: What is the hidden time complexity trap of writing `if item in my_list:` inside a `for item in items:` loop?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <code>item in my_list</code> has to scan the list from start to finish, taking O(n) time. Nested inside a for loop of size n, the total time complexity degrades to <b>O(n²)</b>.</details>

3. **Question**: If a loop cuts the remaining input size in half on every step (e.g. 100 -> 50 -> 25 -> 12...), how many steps will it take to process 1,000,000 items?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Approximately <b>20 steps</b> (O(log₂ 1,000,000) ≈ 20).</details>

---

## Related Modules
- [[foundations/dsa/05-algorithms/01-algorithms|Algorithms & Complexity Analysis]] — Formalizing Big-O, $\Omega$, $\Theta$, and space complexity
- [[01-arrays|Arrays]] — Why array indexing is $O(1)$ without loops
- [[03-hash-maps|Hash Maps]] — How hash maps eliminate hidden lookup loops
