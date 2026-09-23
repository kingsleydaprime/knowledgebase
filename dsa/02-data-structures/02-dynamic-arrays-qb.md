# Dynamic Arrays — Question Bank

Micro-questions over [[02-dynamic-arrays|the dynamic arrays module]]. Answer each one out loud in a full sentence **before** opening the toggle; mark yourself got it / close / blank. Format explained in [[01-arrays-qb|the arrays bank]].

---

## A. The object itself

**1. What is a dynamic array?**

<details><summary>Answer</summary>

An array that can grow. Underneath it is still a plain fixed-size array — the growing is a trick played on top of it.

</details>

**2. What is it called in Python, JavaScript, C++ and Java?**

<details><summary>Answer</summary>

Python `list`, JavaScript `Array`, C++ `std::vector`, Java `ArrayList`. Also called a resizable array.

</details>

**3. Why do dynamic arrays exist? What problem do they solve?**

<details><summary>Answer</summary>

You almost never know in advance how many items you will need — records loaded, items in a cart, messages off a socket. A static array demands its size at creation; a dynamic array manages capacity for you.

</details>

**4. Give a real-world illustration.**

<details><summary>Answer</summary>

An expandable accordion suitcase. Compact while it fits; unzip the extension seam to double its capacity when you run out of room.

</details>

**5. What does a dynamic array keep that a plain array does not?**

<details><summary>Answer</summary>

Two numbers instead of one: **length** (how many elements are stored) and **capacity** (how many the block could hold).

</details>

---

## B. The vocabulary

**6. What is length?**

<details><summary>Answer</summary>

How many elements are actually stored right now — the number `len()` returns.

</details>

**7. What is capacity?**

<details><summary>Answer</summary>

How many elements the underlying memory block could hold before running out. Usually larger than the length, and invisible from outside.

</details>

**8. What is headroom?**

<details><summary>Answer</summary>

The spare space, `capacity - length`. It is what lets an append happen with no copying, and the whole reason appends are usually instant.

</details>

**9. What is the growth factor?**

<details><summary>Answer</summary>

The multiplier used when the block runs out of room — commonly $2\times$, sometimes $1.5\times$. That it is a **multiplier and not a fixed amount** is the single most important detail about it.

</details>

**10. What is reallocation?**

<details><summary>Answer</summary>

The expensive step: request a bigger block, copy every existing element into it, release the old block. $O(n)$, and the thing you are trying to do rarely.

</details>

**11. What does amortised $O(1)$ mean?**

<details><summary>Answer</summary>

A single operation can occasionally be slow, but the **average** cost across a long run of operations is constant. It is a statement about the *total*, never a promise about any *one* call.

</details>

---

## C. How resizing actually works

**12. What triggers a resize?**

<details><summary>Answer</summary>

An append when `length == capacity` — there is no headroom left.

</details>

**13. Name the four steps of a resize, in order.**

<details><summary>Answer</summary>

1. Allocate a new block with double the capacity.
2. Copy every existing element into it.
3. Free the old block.
4. Write the new element.

</details>

**14. After appending to a full array of `length = capacity = 4`, what are the new length and capacity?**

<details><summary>Answer</summary>

`length = 5`, `capacity = 8` — three headroom slots left, which is why the next three appends are instant.

</details>

**15. Why can't the array just extend the existing block in place?**

<details><summary>Answer</summary>

The memory immediately after the block is not owned by the array and is very likely already in use by something else. Contiguity can only be guaranteed by finding a fresh block big enough.

</details>

**16. Does resizing change any element's index?**

<details><summary>Answer</summary>

No. Indices are unchanged; only the **addresses** change, because the base address moved. Any raw pointer into the old block is now dangling — which is why C++ says iterators are invalidated by a `push_back` that reallocates.

</details>

---

## D. The amortised argument

**17. A single resize costs $O(n)$. So why is `append` called $O(1)$?**

<details><summary>Answer</summary>

Because capacity **doubles**, resizes get exponentially rarer as the array grows. The rare expensive calls are spread over an ever-larger number of cheap ones.

</details>

**18. Appending 16 elements from capacity 1, how many copies happen in total?**

<details><summary>Answer</summary>

$1 + 2 + 4 + 8 = 15$ copies.

</details>

**19. Write the general sum for $N$ appends and evaluate it.**

<details><summary>Answer</summary>

$$1 + 2 + 4 + \dots + \frac{N}{2} = N - 1 < N$$

A geometric series whose terms double sums to just under twice the last term.

</details>

**20. Total work for $N$ appends, and therefore the average cost per append?**

<details><summary>Answer</summary>

$N$ insertions + fewer than $N$ copies $= 2N$ operations, so $\frac{2N}{N} = 2$ — a constant, i.e. $O(1)$ amortised.

</details>

**21. Why does growing by a fixed amount (say +10 slots) fail?**

<details><summary>Answer</summary>

Resizes then happen every 10 appends no matter how big the array is, and each copies everything. Total copy work becomes $O(n^2)$, so `append` degrades to $O(n)$ on average.

</details>

**22. State the difference between doubling and +10 in one sentence.**

<details><summary>Answer</summary>

Doubling makes the *gap between resizes* grow with the array; adding a constant keeps the gap fixed while the *cost* of each resize grows — so one sums to $O(n)$ and the other to $O(n^2)$.

</details>

**23. Is a growth factor of 1.5 still amortised $O(1)$?**

<details><summary>Answer</summary>

Yes. Any factor strictly greater than 1 gives a geometric series and therefore amortised $O(1)$; 1.5 simply trades a little more copying for less wasted memory. (It also allows freed blocks to be reused, which is why some allocators prefer it.)

</details>

---

## E. Costs

**24. Cost of access by index?**

<details><summary>Answer</summary>

$O(1)$ — the storage is still one contiguous block, so the address arithmetic from [[01-arrays|arrays]] is unchanged.

</details>

**25. Cost of append at the end?**

<details><summary>Answer</summary>

$O(1)$ **amortised**; $O(n)$ worst case on the rare resize.

</details>

**26. Cost of pop from the end?**

<details><summary>Answer</summary>

$O(1)$ — decrement the length counter; nothing shifts.

</details>

**27. Cost of insert or delete at the front?**

<details><summary>Answer</summary>

$O(n)$ — every subsequent element must shift. Dynamic arrays solved the *sizing* problem, not the *shifting* problem.

</details>

**28. Cost of searching an unsorted dynamic array?**

<details><summary>Answer</summary>

$O(n)$ — a linear scan, exactly as for a plain array.

</details>

---

## F. The ADT

**29. What does the dynamic array ADT add to the plain array ADT?**

<details><summary>Answer</summary>

`append`, `pop`, `insert(i, v)` and `delete(i)` — the operations a fixed array cannot have because its length is frozen at creation.

</details>

**30. Which two ADT operations are $O(n)$, and why is that unavoidable?**

<details><summary>Answer</summary>

`insert(i, v)` and `delete(i)`. Contiguous storage means there is no gap to insert into and no way to close a hole, so elements must physically move.

</details>

---

## G. The precise claim, and where it bites

**31. Why is "appending is $O(1)$" a statement about a sequence rather than a call?**

<details><summary>Answer</summary>

Any individual append may be the unlucky one that copies a million elements. The average over the sequence is constant; no single call is guaranteed to be.

</details>

**32. Where does that occasional $O(n)$ spike actually matter?**

<details><summary>Answer</summary>

Latency-sensitive code — an audio callback, a control loop, a game frame. Your average looks perfect and your worst-case timing still blows the budget.

</details>

**33. What is the fix when it matters?**

<details><summary>Answer</summary>

Reserve capacity up front: `reserve()` in C++, `ensureCapacity()` in Java, `[None] * n` in Python. If no resize can happen, no spike can happen.

</details>

**34. Why is pre-allocation an optimisation even when latency doesn't matter?**

<details><summary>Answer</summary>

It removes every resize copy. Building a 100,000-item list by repeated append does roughly 100,000 extra element copies that pre-allocation skips entirely.

</details>

**35. Why does Python not expose `reserve()`?**

<details><summary>Answer</summary>

It deliberately hides capacity as an implementation detail. That is one reason building a list in a hot loop by repeated `append` is sometimes replaced by preallocating a list of the right size and assigning by index.

</details>

---

## H. Boundaries and comparisons

**36. Does a dynamic array ever shrink?**

<details><summary>Answer</summary>

Some implementations do, when length falls well below capacity. The threshold is deliberately *not* half — shrinking at exactly half lets repeated append/pop at the boundary thrash, resizing on every call. Shrinking at a quarter gives hysteresis that prevents it.

</details>

**37. How much memory can a dynamic array waste?**

<details><summary>Answer</summary>

Up to nearly half its block under doubling, just after a resize. That wasted headroom is exactly what is bought with the $O(1)$ append — space traded for time.

</details>

**38. You need fast insertion at the front. What do you use?**

<details><summary>Answer</summary>

A [[04-linked-lists|linked list]], or a deque / [[07-stacks-and-queues|queue]] — a ring buffer gives $O(1)$ at both ends while keeping contiguous storage.

</details>

**39. Is a Python `list` contiguous?**

<details><summary>Answer</summary>

Its **pointer slots** are contiguous; the objects pointed at are scattered. So indexing is $O(1)$ but cache locality is weaker than a true array of values (`array.array`, NumPy).

</details>

**40. In one sentence, what is a dynamic array?**

<details><summary>Answer</summary>

A plain array plus a capacity counter and a doubling rule — which buys `append` at the price of occasional copying and some wasted space.

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

- [[02-dynamic-arrays|Dynamic Arrays]] — the module
- [[01-arrays-qb|Arrays — Question Bank]] — the structure underneath this one
- [[01-growth-and-asymptotic-notation|Complexity analysis]] — where amortised analysis is done properly
