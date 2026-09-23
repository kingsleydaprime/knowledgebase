# Arrays — Question Bank

An experiment in a different note format. Instead of prose you read, this is a list of **micro-questions** you answer. One question per idea, down to the smallest term, with the answer hidden until you commit to one.

Companion to [[01-arrays|the arrays module]]. The module explains; this file tests.

---

## How to use this

1. Read only the question. Say or write your answer **out loud or on paper** before opening the toggle.
2. Open the answer. Mark yourself: **got it / close / blank**.
3. Anything not "got it" goes on a second pass the next day.
4. You own this file when you can answer every question cold, in order, without opening a single toggle.

> [!NOTE]
> Answering in your head feels like knowing. It usually isn't. Say the answer in a full sentence before you open the toggle — the gap between "I recognise this" and "I can state this" is the entire point of the format.

---

## A. The object itself

**1. What is an array?**

<details><summary>Answer</summary>

A block of memory holding a fixed number of items of the same type, laid out one after another with no gaps between them.

</details>

**2. Why does an array exist? What problem does it solve?**

<details><summary>Answer</summary>

It solves *"I have many items and I want to reach any one of them instantly."* Because the items are the same size and sit side by side, the machine can calculate where item `i` lives instead of searching for it.

</details>

**3. Draw a diagrammatic representation of an array.**

<details><summary>Answer</summary>

```
Index:       0       1       2       3       4
           +-------+-------+-------+-------+-------+
Value:     |  10   |  22   |   7   |  41   |   3   |
           +-------+-------+-------+-------+-------+
Address:    1000    1004    1008    1012    1016
```

Three rows matter: the **index** you write in code, the **value** stored, and the **address** in memory. The addresses climb by a constant step — that constant step is the whole trick.

</details>

**4. Give a real-world illustration of an array.**

<details><summary>Answer</summary>

A row of numbered mailboxes at a post office. They are the same size and in an unbroken line, so to reach box 3 you don't walk past boxes 0, 1 and 2 — you step straight to it, because you can work out where it stands.

</details>

**5. What single property of an array makes everything else about it true?**

<details><summary>Answer</summary>

**Contiguity** — the items are back-to-back in memory. Fast indexing comes from it, and so does slow insertion, because you cannot make room in the middle of an unbroken line without moving things.

</details>

**6. What does it mean that an array is homogeneous?**

<details><summary>Answer</summary>

Every element is the same type and therefore the same size in bytes. If elements had different sizes, the address of element `i` could not be calculated — you'd have to walk the earlier elements to find out where `i` starts.

</details>

**7. Is an array's length fixed?**

<details><summary>Answer</summary>

For a plain array, yes — fixed when it is created. Growing it means allocating a bigger block elsewhere and copying everything over, which is the subject of [[02-dynamic-arrays|dynamic arrays]].

</details>

---

## B. The vocabulary

**8. What is a memory address?**

<details><summary>Answer</summary>

A number identifying one byte of memory. Memory is one long numbered line of bytes; an address is a position on that line.

</details>

**9. What is contiguous memory?**

<details><summary>Answer</summary>

Storage where items sit directly next to each other with nothing in between — parked cars in adjacent spaces rather than scattered around a city.

</details>

**10. What is an element?**

<details><summary>Answer</summary>

A single item stored in the array.

</details>

**11. What is an index?**

<details><summary>Answer</summary>

The position number of an element, counting from zero.

</details>

**12. Why do indices start at 0 rather than 1?**

<details><summary>Answer</summary>

Because an index is really an **offset from the base address** — how far along you are, not which one you are. The first element is 0 elements along.

</details>

**13. What is the base address?**

<details><summary>Answer</summary>

The memory address of the very first element, index 0. Every other address is worked out relative to it.

</details>

**14. What is element size?**

<details><summary>Answer</summary>

How many bytes one element occupies — e.g. 4 bytes for a 32-bit integer. It must be the same for every element for the address formula to work.

</details>

**15. What is length?**

<details><summary>Answer</summary>

How many elements the array holds. It is stored, not counted, which is why asking for it is $O(1)$.

</details>

**16. What is the index of the last element in an array of length `n`?**

<details><summary>Answer</summary>

`n - 1`. Asking for index `n` runs off the end.

</details>

**17. What is random access?**

<details><summary>Answer</summary>

Reaching any element directly, without passing the ones before it. Getting element 500 costs exactly what getting element 1 costs. This is the array's defining property.

</details>

**18. What is sequential access, and which structure forces it?**

<details><summary>Answer</summary>

Reaching an element only by walking through the ones before it. A [[04-linked-lists|linked list]] forces it: to reach node 500 you follow 500 pointers.

</details>

**19. What is a cache line?**

<details><summary>Answer</summary>

The chunk of memory the processor actually fetches when you ask for a single byte — typically 64 bytes. You never fetch one item; you fetch the block it sits in.

</details>

**20. What is a cache hit and a cache miss?**

<details><summary>Answer</summary>

A **hit** is when the data you asked for is already in cache — nearly free. A **miss** is when it isn't, so the processor waits on a fetch from main memory, which is orders of magnitude slower.

</details>

**21. What is cache locality?**

<details><summary>Answer</summary>

Arranging your reads so the things you use next are in the block you have already fetched. Good locality can make identical work run many times faster without changing the complexity at all.

</details>

**22. Why does an array have good cache locality almost for free?**

<details><summary>Answer</summary>

Because neighbouring elements are neighbouring addresses. Reading `arr[0]` drags `arr[1]`, `arr[2]`, … into cache with it, so a sequential scan pays for one fetch and gets many elements from it.

</details>

---

## C. Address arithmetic

**23. What is the formula for the address of element `i`?**

<details><summary>Answer</summary>

$$\text{Address}(i) = \text{Base Address} + (i \times \text{Element Size})$$

</details>

**24. An array of 4-byte integers starts at address 1000. Where is `arr[3]`?**

<details><summary>Answer</summary>

$1000 + (3 \times 4) = 1012$.

</details>

**25. An array of 8-byte integers starts at address 2000. Where is `arr[4]`?**

<details><summary>Answer</summary>

$2000 + (4 \times 8) = 2032$.

</details>

**26. Where is `arr[0]`, and why does the formula confirm it?**

<details><summary>Answer</summary>

At the base address itself, because $\text{base} + (0 \times \text{size}) = \text{base}$. This is the clean reason indexing starts at zero.

</details>

**27. Why is indexing $O(1)$?**

<details><summary>Answer</summary>

The work is one multiplication and one addition, then one read. It does not depend on `i` or on the array's length, so the cost does not grow with $n$.

</details>

**28. Does the array store a list of its elements' addresses?**

<details><summary>Answer</summary>

No — and that is the point. Storing addresses would cost memory and a lookup. The addresses are *computed* from base and index, so nothing has to be stored or searched.

</details>

**29. Why does the formula break if elements have different sizes?**

<details><summary>Answer</summary>

`i × element_size` assumes every earlier element took up the same space. With variable sizes you would have to add up the actual sizes of all `i` earlier elements — which is walking them, i.e. $O(n)$.

</details>

**30. Does the CPU search, compare, or loop when evaluating `arr[i]`?**

<details><summary>Answer</summary>

None of those. It does the arithmetic and jumps to the address. Whether the array holds 5 items or 5,000,000 is irrelevant.

</details>

---

## D. What an array can and cannot do

**31. What is an ADT?**

<details><summary>Answer</summary>

An **abstract data type** — a description of *what* a structure does (its operations and their costs), stated before you decide *how* it is built.

</details>

**32. What is the complete ADT of a fixed array?**

<details><summary>Answer</summary>

Three operations: `get(i)`, `set(i, value)`, and `length()` — each $O(1)$. That is all of it.

</details>

**33. Name four operations absent from the array ADT, and why each is absent.**

<details><summary>Answer</summary>

1. `insert(i, v)` — needs everything after `i` shifted up, $O(n)$, and there is no spare room anyway.
2. `delete(i)` — leaves a hole, and closing it means shifting everything down, $O(n)$.
3. `append(v)` — the length is fixed at creation.
4. `find(v)` — the array knows *where* things sit, not *what* it contains; you can scan in $O(n)$ but it won't help you.

</details>

**34. Cost of access by index?**

<details><summary>Answer</summary>

$O(1)$ — the address formula.

</details>

**35. Cost of searching an unsorted array?**

<details><summary>Answer</summary>

$O(n)$ — you must check elements one at a time; the layout tells you nothing about the values.

</details>

**36. Cost of searching a sorted array?**

<details><summary>Answer</summary>

$O(\log n)$ with binary search, which halves the remaining range each step. Note that this is only possible *because* random access lets you jump to the midpoint in $O(1)$.

</details>

**37. Cost of inserting or deleting at the end?**

<details><summary>Answer</summary>

$O(1)$ — nothing after it needs to move.

</details>

**38. Cost of inserting or deleting at the front or middle?**

<details><summary>Answer</summary>

$O(n)$ — every subsequent element must shift to open or close the gap.

</details>

**39. Why exactly is front insertion $O(n)$ while appending is $O(1)$?**

<details><summary>Answer</summary>

Contiguity. There is no gap to insert into, so to put something at index 0, all $n$ existing elements must physically move one slot right. At the end, nothing sits after the new item, so nothing moves.

</details>

**40. State the array's trade-off in one sentence.**

<details><summary>Answer</summary>

An array gives you the fastest possible access **by position** and offers nothing else — and every other structure in this folder pays some access-time cost to buy back one of the operations the array lacks.

</details>

---

## E. Multi-dimensional arrays and memory layout

**41. Memory is one-dimensional. So how is a 2-D grid stored?**

<details><summary>Answer</summary>

It is **flattened** into a single 1-D array, and an index formula translates a `(row, col)` pair into one flat position. The 2-D grid is a convenient fiction told over a flat line of bytes.

</details>

**42. What is row-major order?**

<details><summary>Answer</summary>

Whole rows stored one after another: all of row 0, then all of row 1. `[[1,2,3],[4,5,6]]` becomes `[1, 2, 3, 4, 5, 6]`.

</details>

**43. What is column-major order?**

<details><summary>Answer</summary>

Whole columns stored one after another: all of column 0, then all of column 1. The same grid becomes `[1, 4, 2, 5, 3, 6]`.

</details>

**44. Give the row-major address formula for `grid[r][c]`.**

<details><summary>Answer</summary>

$$\text{Address}(r,c) = \text{Base} + (r \times \text{num\_cols} + c) \times \text{Element Size}$$

You skip `r` whole rows, then step `c` elements along.

</details>

**45. Give the column-major formula, and say what changes.**

<details><summary>Answer</summary>

$$\text{Address}(r,c) = \text{Base} + (c \times \text{num\_rows} + r) \times \text{Element Size}$$

The multiplication uses the number of **rows** instead of columns: you skip `c` whole columns, then step `r` down.

</details>

**46. Which languages use which layout?**

<details><summary>Answer</summary>

**Row-major:** C, C++, Java, Python, Rust, Go, NumPy by default.
**Column-major:** Fortran, MATLAB, R, Julia, and the BLAS/LAPACK libraries most scientific computing sits on.

</details>

**47. Is one layout better than the other?**

<details><summary>Answer</summary>

No. What matters is that **your loop order matches your layout** — inner loop over columns in a row-major language, over rows in a column-major one.

</details>

**48. What goes wrong when loop order does not match the layout?**

<details><summary>Answer</summary>

Every read lands in a different 64-byte block, so almost every access is a cache miss. The counted lab in [[01-arrays|the module]] measures **16× more cache-line fetches** for identical work.

</details>

**49. Does the wrong loop order change the Big-O?**

<details><summary>Answer</summary>

No. Both are $O(\text{rows} \times \text{cols})$. This is the clearest example of Big-O being blind to something that badly matters in practice — complexity counts operations, not memory behaviour.

</details>

**50. In NumPy, what do `order='C'` and `order='F'` mean?**

<details><summary>Answer</summary>

`'C'` is row-major (as in C) and `'F'` is column-major (as in Fortran). NumPy makes the choice explicit instead of implicit.

</details>

---

## F. Strings as arrays

**51. What is a string, structurally?**

<details><summary>Answer</summary>

An array of character bytes with text helper methods attached.

</details>

**52. What does it mean that strings are immutable in Python, Java and JavaScript?**

<details><summary>Answer</summary>

They cannot be changed in place. Any "modification" builds a brand-new array and copies the characters over.

</details>

**53. Why is `result += char` inside a loop $O(n^2)$?**

<details><summary>Answer</summary>

Each `+=` allocates a new string and copies everything accumulated so far — an $O(n)$ copy hidden inside an $O(n)$ loop. Total characters copied is $0 + 1 + 2 + \dots + (n-1)$.

</details>

**54. What is the fix, and why is it $O(n)$?**

<details><summary>Answer</summary>

`"".join(parts)`. It looks at the parts first, allocates the final buffer **once**, and copies each character exactly once.

</details>

---

## G. Traps

**55. What is an off-by-one / index-out-of-bounds error?**

<details><summary>Answer</summary>

Asking for index `n` on an array of length `n`. Valid indices run `0` to `n-1`, so index `n` is one past the end.

</details>

**56. Why is `arr.insert(0, item)` a trap inside a loop?**

<details><summary>Answer</summary>

Each call shifts every element right by one, so it is $O(n)$ per call and $O(n^2)$ across the loop. If you need to build from the front, append and reverse at the end, or use a deque.

</details>

**57. Why can you not safely delete from an array while iterating forward over it?**

<details><summary>Answer</summary>

Deleting shifts every later element down one index, so the next element slides into the position you just visited and the loop skips it. Iterate backwards, or build a new list.

</details>

---

## H. Boundaries and comparisons

**58. When should you not use an array?**

<details><summary>Answer</summary>

When the workload is dominated by insertion and deletion in the middle, or when you cannot get one large contiguous block of memory. Then a [[04-linked-lists|linked list]] or another structure fits better.

</details>

**59. Array vs linked list, in one line each.**

<details><summary>Answer</summary>

**Array:** contiguous, $O(1)$ access by index, $O(n)$ middle insertion, excellent cache locality.
**Linked list:** scattered nodes joined by pointers, $O(n)$ access, $O(1)$ splicing *once you hold the node*, poor cache locality.

</details>

**60. Is a Python `list` an array?**

<details><summary>Answer</summary>

It is a **dynamic array** ([[02-dynamic-arrays]]) of pointers. The pointer slots are contiguous, but the objects they point to are scattered — so it has array-like indexing and weaker cache locality than a true contiguous array of values (what `array.array` or a NumPy array gives you).

</details>

**61. Binary search needs $O(\log n)$. Why does it only work on arrays and not on linked lists?**

<details><summary>Answer</summary>

Binary search jumps to the midpoint of a range. That jump is $O(1)$ only with random access. On a linked list, reaching the midpoint is itself $O(n)$, which destroys the saving.

</details>

**62. Finish the sentence: every other data structure in this folder is…**

<details><summary>Answer</summary>

…paying some access-time cost to buy back one of the operations a plain array does not have — growth, insertion, deletion, ordering, or search by value.

</details>

---

## Scorecard

Run the bank three times on different days and record the count. The number should climb; the specific questions you miss are your actual study list.

| Pass | Date | Got it | Close | Blank | Questions missed |
| :--- | :--- | :----- | :---- | :---- | :--------------- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Related

- [[01-arrays|Arrays]] — the full module this bank is drawn from
- [[02-dynamic-arrays|Dynamic Arrays]] — what happens when a fixed array must grow
- [[04-linked-lists|Linked Lists]] — the non-contiguous alternative
