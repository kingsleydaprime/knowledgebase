# Monotonic Stack — Question Bank

Micro-questions over [[06-monotonic-stack|the monotonic stack pattern]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why it exists

**1. What problem does it solve, and what does the naive version cost?**

<details><summary>Answer</summary>

**"For each element, find the next greater (or smaller) element."** Naively you scan forward from each position — $O(n^2)$, so 500,000 comparisons for 1,000 prices.

</details>

**2. Define a monotonic stack.**

<details><summary>Answer</summary>

**A stack kept strictly increasing or strictly decreasing from bottom to top**, by popping anything that would break that order before pushing.

</details>

**3. What is the stack invariant?**

<details><summary>Answer</summary>

**The order rule the stack maintains** — in a monotonic increasing stack, each new element must be larger than the top.

</details>

---

## B. The mechanism

**4. Describe the loop in one sentence.**

<details><summary>Answer</summary>

Walk the array once; **for each new element, pop everything smaller than it — those elements have just found their next greater element — then push the current index.**

</details>

**5. Why store indices rather than values?**

<details><summary>Answer</summary>

**Because you need to know *where* to write the answer** when you pop, and the index also lets you compute distances (as in Daily Temperatures) and widths (as in Largest Rectangle).

</details>

**6. Write the next-greater loop.**

<details><summary>Answer</summary>

```python
result = [-1] * len(nums)
stack = []
for i, num in enumerate(nums):
    while stack and nums[stack[-1]] < num:
        result[stack.pop()] = num
    stack.append(i)
```

</details>

**7. Trace `[2,1,2,4,3]`.**

<details><summary>Answer</summary>

`i=0` push → `[0]`. `i=1` push → `[0,1]`. `i=2` pop 1 (`result[1]=2`), push → `[0,2]`. `i=3` pop 2 (`result[2]=4`), pop 0 (`result[0]=4`), push → `[3]`. `i=4` push → `[3,4]`.
**result = `[4, 2, 4, -1, -1]`.**

</details>

**8. What do the remaining stack entries mean at the end?**

<details><summary>Answer</summary>

**They have no next greater element** — which is why the result array is initialised to $-1$.

</details>

---

## C. Why it is O(n)

**9. Give the argument.**

<details><summary>Answer</summary>

**Every index is pushed exactly once and popped at most once across the entire run**, so the total push/pop count is bounded by $2n$, not $n^2$.

</details>

**10. What familiar analysis is that?**

<details><summary>Answer</summary>

**The same amortised argument as dynamic array resizing** — the loop looks nested, but total work across the run is linear.

</details>

---

## D. Variants

**11. How do you find the *previous smaller* element instead?**

<details><summary>Answer</summary>

Keep the stack in **increasing** value order; pop while the top is $\ge$ the current value, **then read the answer off the top before pushing**:

```python
while stack and nums[stack[-1]] >= num:
    stack.pop()
result[i] = stack[-1] if stack else -1
stack.append(i)
```

</details>

**12. What is the structural difference between the two variants?**

<details><summary>Answer</summary>

**Next-greater writes the answer when it pops; previous-smaller reads the answer when it pushes.** One looks forward, the other looks backward.

</details>

**13. What is a monotonic *queue*, and what is it for?**

<details><summary>Answer</summary>

A deque holding indices in decreasing value order — **for sliding window maximum**, where the aggregate is not invertible.

</details>

**14. What are its two `while` loops?**

<details><summary>Answer</summary>

**Pop the front** when an index falls out of the window; **pop the back** while the incoming value is $\ge$ the back's value — those can never be the maximum again.

</details>

---

## E. Trade-offs

**15. What kinds of problems does it fit?**

<details><summary>Answer</summary>

**"Next/previous greater/smaller" problems specifically** — those with a monotonic condition. Daily Temperatures and Largest Rectangle in Histogram are the classics.

</details>

**16. How large can the stack get?**

<details><summary>Answer</summary>

$O(n)$ — in the worst case (a strictly increasing array) **nothing is ever popped and it contains all indices**.

</details>

**17. What is the key to getting it right?**

<details><summary>Answer</summary>

**Understanding the invariant** — which direction the stack is ordered decides both the comparison operator and whether you write on pop or read on push.

</details>

**18. Summarise the pattern in one sentence.**

<details><summary>Answer</summary>

Keep a stack in sorted order and let each arriving element evict everything it dominates — each eviction is an answer, and every index is pushed and popped once.

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

- [[06-monotonic-stack|Monotonic Stack]] — the pattern
- [[dsa/02-data-structures/07-stacks-and-queues-qb|Stacks and Queues — Question Bank]]
- [[03-sliding-window-qb|Sliding Window — Question Bank]] — where the monotonic deque appears
