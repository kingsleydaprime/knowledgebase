# Non-Comparison Sorts — Question Bank

Micro-questions over [[05-non-comparison-sorts|the non-comparison sorts module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Escaping the bound

**1. These sort in $O(n)$ despite the $\Omega(n\log n)$ lower bound. Why is there no contradiction?**

<details><summary>Answer</summary>

**They never compare two elements.**

</details>

**2. What do they use instead?**

<details><summary>Answer</summary>

**The key itself as information** — as an array index, or as a sequence of digits.

</details>

**3. State the difference in terms of the question asked.**

<details><summary>Answer</summary>

The decision-tree model assumes the only question you may ask is **"is $a < b$?"**. These ask **"what is the value of $a$?"**

</details>

**4. What is the cost of that extra power?**

<details><summary>Answer</summary>

**A loss of generality.** A comparison sort works on anything with an ordering — strings, tuples, custom objects, user comparators. These need small non-negative integer keys, or keys decomposable into digits.

</details>

---

## B. Counting sort

**5. Give the three steps.**

<details><summary>Answer</summary>

1. Count occurrences of each key.
2. Turn the counts into a **prefix sum**, so `count[v]` is the number of elements $\le v$ — the position just past where the $v$s end.
3. Walk the input **backwards**, placing each element at `count[key]-1` and decrementing.

</details>

**6. What is the cost?**

<details><summary>Answer</summary>

$O(n + k)$ time and $O(n + k)$ space, for keys in $0..k$.

</details>

**7. When is it worth it?**

<details><summary>Answer</summary>

**When $k$ is $O(n)$.** A million ages ($k = 120$) is superb; a thousand 64-bit integers means $k = 2^{64}$ and an impossible array.

</details>

**8. Why walk backwards?**

<details><summary>Answer</summary>

**That is what makes it stable.** Going backwards places later-occurring equal elements at higher positions, preserving their original order. Forwards, they come out reversed.

</details>

**9. Why does that stability matter far more than it looks?**

<details><summary>Answer</summary>

**Because radix sort depends on it.**

</details>

---

## C. Radix sort

**10. What problem does radix sort fix?**

<details><summary>Answer</summary>

Counting sort is useless for large key ranges. Radix sorts **one digit at a time**, so $k$ is only the digit base (10, or 256), never the full key range.

</details>

**11. What is the cost?**

<details><summary>Answer</summary>

$O(d(n + b))$ for $d$ digits in base $b$ — **linear in $n$ when $d$ is fixed**.

</details>

**12. What does the whole thing rest on?**

<details><summary>Answer</summary>

**Stability.** When sorting by the tens digit, two numbers with the same tens digit must stay in the order the units pass left them.

</details>

**13. What happens with an unstable inner sort?**

<details><summary>Answer</summary>

It **destroys the previous pass's work and the final result is simply wrong** — silently. **This is the single most important dependency in the algorithm.**

</details>

**14. Would most-significant-digit-first work just as well?**

<details><summary>Answer</summary>

Not in the same way. MSD splits into buckets by the top digit, and **those buckets must then be sorted independently and recursively**. That works — it is what you use for variable-length strings — but it is a different, more complex algorithm.

</details>

**15. Why does LSD work as a flat sequence of passes?**

<details><summary>Answer</summary>

**Because each pass builds on the last** — stability carries the previous passes' ordering forward as a tiebreak.

</details>

---

## D. Bucket sort

**16. Describe it.**

<details><summary>Answer</summary>

Distribute into buckets by value range, sort each bucket (usually with insertion sort), concatenate.

</details>

**17. What is its cost, and under what assumption?**

<details><summary>Answer</summary>

Average $O(n)$ **when the input is uniformly distributed** over the range.

</details>

**18. How load-bearing is that assumption?**

<details><summary>Answer</summary>

Completely. **If everything lands in one bucket you have done a distribution pass and then an $O(n^2)$ insertion sort.** Bucket sort is the least robust of the three and the most dependent on knowing your data.

</details>

---

## E. Traps

**19. How do you handle negative numbers?**

<details><summary>Answer</summary>

Counting sort indexes an array by key, so negatives need an **offset**. Radix needs explicit sign handling too.

</details>

**20. Can you use a custom comparator with these?**

<details><summary>Answer</summary>

**No.** They need integer keys or digit decompositions — there is no comparison for a comparator to define.

</details>

**21. When does walking forwards in counting sort actually break something?**

<details><summary>Answer</summary>

Usually it does not matter — **until you use it inside radix sort, where it breaks correctness.**

</details>

**22. Summarise the three in one sentence.**

<details><summary>Answer</summary>

Read the key instead of comparing it — counting sort when the range is small, radix sort when it is not (on a stable inner sort), and bucket sort only when you know the distribution is uniform.

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

- [[05-non-comparison-sorts|Non-Comparison Sorts]] — the module
- [[01-the-lower-bound-qb|The Lower Bound — Question Bank]] — the theorem these sidestep
