# Math & Geometry — Question Bank

Micro-questions over [[12-math-and-geometry|the math and geometry module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The vocabulary

**1. What does in-place mean here?**

<details><summary>Answer</summary>

Transforming data directly inside the input structure with **$O(1)$ extra space** — rearranging books on a shelf without a second shelf.

</details>

**2. What is transposition?**

<details><summary>Answer</summary>

Swapping `matrix[i][j]` with `matrix[j][i]` **across the main diagonal** — reflecting a chessboard along its diagonal.

</details>

**3. What is binary exponentiation?**

<details><summary>Answer</summary>

Computing $x^n$ in $O(\log n)$ by **repeatedly squaring** rather than multiplying $n$ times.

</details>

---

## B. Rotate image

**4. What two steps make a 90° clockwise rotation?**

<details><summary>Answer</summary>

**Transpose, then reverse each row.**

</details>

**5. What happens if you do them in the other order?**

<details><summary>Answer</summary>

You get a **90° counter-clockwise** rotation.

</details>

**6. Why does the transpose loop start at `j = i + 1`?**

<details><summary>Answer</summary>

To touch **only above the diagonal** — going over the whole matrix would swap every pair twice and leave it unchanged.

</details>

**7. How would you get 90° counter-clockwise deliberately?**

<details><summary>Answer</summary>

**Reverse each row first, then transpose** — or transpose then reverse the column order.

</details>

---

## C. Set matrix zeroes

**8. State the problem.**

<details><summary>Answer</summary>

If any cell is 0, set its **entire row and column** to zero.

</details>

**9. What is the naive approach and its cost?**

<details><summary>Answer</summary>

Store zero-row and zero-column indices in separate arrays — $O(m+n)$ space.

</details>

**10. What is the $O(1)$-space trick?**

<details><summary>Answer</summary>

**Use the first row and first column of the matrix itself as the marker arrays**, plus two booleans for whether the first row/column themselves contained a zero.

</details>

**11. Why are the two extra booleans necessary?**

<details><summary>Answer</summary>

Because the first row and column are being **overwritten as markers**, so their own original zero status would otherwise be lost.

</details>

**12. Why must the marker pass run before the writing pass?**

<details><summary>Answer</summary>

Writing a zero would otherwise be **read as a marker** by a later cell, cascading zeros across the whole matrix.

</details>

---

## D. Spiral matrix

**13. What is the strategy?**

<details><summary>Answer</summary>

Maintain **four shrinking boundaries** — top, bottom, left, right — peel off one edge per direction in rotation, moving each boundary inward after processing.

</details>

**14. Give the four directions in order.**

<details><summary>Answer</summary>

Right along the top row (`top += 1`), down the right column (`right -= 1`), left along the bottom row (`bottom -= 1`), up the left column (`left += 1`).

</details>

**15. Why are the third and fourth passes guarded by `if`?**

<details><summary>Answer</summary>

**When only a single row or column remains**, the guards prevent double-visiting it.

</details>

---

## E. Fast power

**16. What is the naive cost, and what is the insight?**

<details><summary>Answer</summary>

Naive: $O(n)$ multiplications. Insight: **$x^n = (x^2)^{n/2}$ when $n$ is even** — halving the exponent each step gives $O(\log n)$.

</details>

**17. What happens when $n$ is odd?**

<details><summary>Answer</summary>

Peel off one factor of $x$ and continue with $n-1$, which is even.

</details>

**18. How do you handle a negative exponent?**

<details><summary>Answer</summary>

**Take the reciprocal of $x$ and make $n$ positive before the main loop** — explicitly, not implicitly.

</details>

**19. What is the overflow trap?**

<details><summary>Answer</summary>

In fixed-width languages, **the intermediate `x * x` can overflow 64-bit integers** even when the final answer would fit.

</details>

---

## F. Happy number

**20. How is cycle detection used here?**

<details><summary>Answer</summary>

**Floyd's slow/fast pointers** over the sequence of digit-square sums — two runners on a circular track, the faster lapping the slower.

</details>

**21. Why is a cycle guaranteed to exist for any starting number?**

<details><summary>Answer</summary>

The digit-square sum of any number is bounded, so the sequence must eventually **revisit a value** — either 1 (happy) or a loop (unhappy).

</details>

**22. What is the alternative to Floyd's here, and its cost?**

<details><summary>Answer</summary>

A **hash set of seen values** — same $O(\log n)$-ish time but $O(n)$ space instead of $O(1)$.

</details>

**23. Summarise the module in one sentence.**

<details><summary>Answer</summary>

Matrix problems become $O(1)$ space by reusing the matrix itself as scratch, and number problems become $O(\log n)$ by halving the exponent rather than counting down.

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

- [[12-math-and-geometry|Math & Geometry]] — the module
- [[11-bit-manipulation-qb|Bit Manipulation — Question Bank]]
- [[dsa/04-patterns/13-matrix-traversal|Matrix Traversal]] — the pattern
- [[dsa/04-patterns/04-fast-slow-pointers|Fast & Slow Pointers]] — Floyd's, generally
