# Module: Dynamic Arrays (Resizable Contiguous Storage)

Welcome to the **Dynamic Arrays** module. A dynamic array is a static [[01-arrays|array]] with a smart management layer built around it. It provides the lightning-fast $O(1)$ access speed of a static array, while automatically growing in size whenever it fills up.

Dynamic arrays are what high-level languages hand you by default: Python's `list`, JavaScript's `Array`, C++'s `std::vector`, and Java's `ArrayList`.

---

## Before you start

- You understand contiguous memory and O(1) indexing. See [[01-arrays|arrays]].
- You can read Big-O notation and know what 'amortised' means informally.

**What you will be able to do after this lesson:**

1. Explain why a fixed-size array must be reallocated to grow.
2. Compute the total copies for n appends under doubling, and show it is under 2n.
3. Explain why doubling gives amortised O(1) and fixed-chunk growth does not.
4. Explain why append is cheap and insert-at-front is not.

**Study route:** read the mechanism, run the lab, then attempt the independent task before opening the hint.

## 1. Why Do Dynamic Arrays Exist? (Real-World Motivation)

Imagine buying an expandable **accordion suitcase** for travel:
- When you start packing, it takes up a compact space.
- If you run out of room, you un-zipper the extension seam to **double its capacity**.

In real-world software, you almost never know in advance how many records a user will load, how many items will be added to a shopping cart, or how many messages will arrive over a network connection.

Static arrays demand a fixed size at creation time. Dynamic arrays eliminate that restriction by automatically managing capacity behind the scenes.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **Length (Size)** | The number of elements currently stored in the array. | 3 active items. |
| **Capacity** | The actual maximum size of the allocated memory block. | 4 available slots. |
| **Headroom** | The empty slots remaining (`capacity - length`). | 1 empty slot remaining. |
| **Growth Factor** | The multiplier used to expand capacity when full (usually $2\times$ or $1.5\times$). | Doubling 4 slots to 8 slots. |
| **Amortized $O(1)$** | The average time per operation across a long sequence of calls. | Expensive resizes are rare enough that the average cost stays $O(1)$. |

---

## 3. How Dynamic Resizing Works

Internally, a dynamic array tracks both its current **length** and underlying **capacity**.

### State 1: Headroom Available
```
length = 3, capacity = 4
+-------+-------+-------+-------+
|  10   |  22   |   7   |   _   |  <-- 1 empty slot left
+-------+-------+-------+-------+
```
Appending `41` fills the empty slot. Now `length = 4, capacity = 4`.

---

### State 2: Array Full (`length == capacity`) — The Resize Trigger
When you call `append(99)` and `length == capacity`, the dynamic array executes a 4-step resize algorithm:

```
Step 1: Allocate a new block with DOUBLE the capacity (capacity = 8)
+---+---+---+---+---+---+---+---+
| _ | _ | _ | _ | _ | _ | _ | _ |
+---+---+---+---+---+---+---+---+

Step 2: Copy existing elements from old block to new block
+---+---+---+---+---+---+---+---+
| 10| 22| 7 | 41| _ | _ | _ | _ |
+---+---+---+---+---+---+---+---+

Step 3: Free the old memory block.

Step 4: Append the new element 99
+---+---+---+---+---+---+---+---+
| 10| 22| 7 | 41| 99| _ | _ | _ |
+---+---+---+---+---+---+---+---+
Now length = 5, capacity = 8 (3 empty headroom slots remaining!)
```

---

## 4. Mathematical Proof: Why Doubling Makes Append "Amortized $O(1)$"

A single resize operation costs $O(n)$ because every single element must be copied to the new memory location. Why, then, do computer scientists claim that `append()` is $O(1)$?

Because capacity **doubles**, resizes become exponentially rarer as the array grows!

### Counting the Total Copies
Suppose you append $N = 16$ elements starting from a capacity of 1:

```
Appends 1-2:   Resize to 2   (Cost: 1 copy)
Appends 3-4:   Resize to 4   (Cost: 2 copies)
Appends 5-8:   Resize to 8   (Cost: 4 copies)
Appends 9-16:  Resize to 16  (Cost: 8 copies)

Total Copies across ALL 16 appends = 1 + 2 + 4 + 8 = 15 copies!
```

Mathematically, for $N$ appends:
$$\text{Total Copy Cost} = 1 + 2 + 4 + 8 + \dots + \frac{N}{2} = N - 1 < N$$

- **Total work for $N$ appends**: $N$ insertions + $N$ copies = $2N$ operations.
- **Average (Amortized) cost per append**: $\frac{2N}{N} = 2 = O(1)$!

> [!IMPORTANT]
> **Why Fixed Additive Growth Fails**: If you increased capacity by a fixed amount (e.g. $+10$ slots each time instead of multiplying by $2\times$), the total copy work would be $O(n^2)$, causing `append()` to degrade to a slow $O(n)$ average cost!

---

## 5. Time & Space Complexity Summary

| Operation | Time Complexity | Notes |
| :--- | :--- | :--- |
| **Access by Index (`arr[i]`)** | $O(1)$ | Direct formula calculation ($\text{base} + i \times \text{size}$). |
| **Append at End** | **$O(1)$ Amortized** | $O(n)$ worst-case only on the rare resize step. |
| **Pop from End** | $O(1)$ | Shrinks length counter; no shifting needed. |
| **Insert / Delete at Front** | $O(n)$ | Must shift all subsequent elements right/left. |
| **Search (Unsorted)** | $O(n)$ | Linear scan. |

---

## 6. Practical Optimizations & Gotchas

1. **Pre-Allocation Optimization**: If you know you will store 100,000 items, pre-allocate the capacity upfront (`[None] * 100000` in Python or `vector.reserve(100000)` in C++) to prevent all resize copies!
2. **Front Operations Are Still $O(n)$**: Dynamic arrays solve the dynamic sizing problem, but inserting at index 0 still requires shifting every item. If you need fast front insertions, use [[07-stacks-and-queues|Queues]] or [[04-linked-lists|Linked Lists]].

---

## Implementation - complete runnable example

**Runnable example:** save as `dynamic_arrays_lab.py` and run `python3 dynamic_arrays_lab.py`. Standard library only; writes no files. Everything is counted rather than timed, so your output will match this exactly.

```python
"""Dynamic arrays: why doubling gives amortised O(1) append.

Counts element copies exactly, so the amortisation is arithmetic rather
than a claim."""

class GrowableArray:
    """A dynamic array built on a fixed-capacity store, like a real one."""
    def __init__(self, growth=2):
        self.data, self.size, self.capacity = [None], 0, 1
        self.growth, self.copies, self.resizes = growth, 0, 0

    def append(self, value):
        if self.size == self.capacity:
            self._resize(max(1, int(self.capacity * self.growth)))
        self.data[self.size] = value
        self.size += 1

    def _resize(self, new_capacity):
        """The expensive step: allocate bigger, copy everything across."""
        bigger = [None] * new_capacity
        for i in range(self.size):
            bigger[i] = self.data[i]
        self.copies += self.size
        self.resizes += 1
        self.data, self.capacity = bigger, new_capacity

    def __getitem__(self, i):
        if not 0 <= i < self.size:
            raise IndexError(i)
        return self.data[i]

    def insert_front(self, value):
        """O(n): everything must shift right to make room."""
        if self.size == self.capacity:
            self._resize(max(1, int(self.capacity * self.growth)))
        for i in range(self.size, 0, -1):
            self.data[i] = self.data[i - 1]
        self.copies += self.size
        self.data[0] = value
        self.size += 1

def append_cost(n, growth):
    a = GrowableArray(growth)
    for i in range(n):
        a.append(i)
    return a.copies, a.resizes

if __name__ == "__main__":
    print("GROWTH BY DOUBLING -- copies during n appends")
    print(f"  {'n':>7s} {'copies':>10s} {'resizes':>9s} {'copies/append':>14s}")
    for n in (10, 100, 1000, 10000):
        copies, resizes = append_cost(n, 2)
        print(f"  {n:7d} {copies:10,d} {resizes:9d} {copies/n:14.2f}")
    print("  -> copies per append approaches 1 and never exceeds 2.")
    print("     THAT is what 'amortised O(1)' means: some appends are")
    print("     expensive, but the average over any run is constant.")
    print()

    print("WHY DOUBLING, NOT ADDING A FIXED AMOUNT")
    print(f"  {'strategy':>22s} {'copies for n=10000':>20s}")
    a = GrowableArray(2)
    for i in range(10000): a.append(i)
    print(f"  {'double (x2)':>22s} {a.copies:20,d}")
    # grow by a constant chunk instead
    size = cap = copies = 0
    for i in range(10000):
        if size == cap:
            copies += size
            cap += 100
        size += 1
    print(f"  {'grow by 100 each time':>22s} {copies:20,d}")
    print(f"  -> fixed-chunk growth is O(n^2) overall; doubling is O(n).")
    print()

    print("APPEND vs INSERT AT FRONT")
    back = GrowableArray()
    for i in range(1000): back.append(i)
    front = GrowableArray()
    for i in range(1000): front.insert_front(i)
    print(f"  1000 appends        : {back.copies:8,d} copies")
    print(f"  1000 front inserts  : {front.copies:8,d} copies")
    print(f"  -> front insertion is O(n) per operation, O(n^2) overall.")

    copies_2x, _ = append_cost(10000, 2)
    assert copies_2x < 2 * 10000, "doubling must stay under 2 copies per append"
    assert copies_2x < copies, "doubling must beat fixed-chunk growth"
    assert front.copies > 100 * back.copies
    a = GrowableArray()
    for i in range(5): a.append(i * i)
    assert [a[i] for i in range(5)] == [0, 1, 4, 9, 16]
    print()
    print("dynamic_arrays_lab: passed")
```

Expected output:

```
GROWTH BY DOUBLING -- copies during n appends
        n     copies   resizes  copies/append
       10         15         4           1.50
      100        127         7           1.27
     1000      1,023        10           1.02
    10000     16,383        14           1.64
  -> copies per append approaches 1 and never exceeds 2.
     THAT is what 'amortised O(1)' means: some appends are
     expensive, but the average over any run is constant.

WHY DOUBLING, NOT ADDING A FIXED AMOUNT
                strategy   copies for n=10000
             double (x2)               16,383
   grow by 100 each time              495,000
  -> fixed-chunk growth is O(n^2) overall; doubling is O(n).

APPEND vs INSERT AT FRONT
  1000 appends        :    1,023 copies
  1000 front inserts  :  500,523 copies
  -> front insertion is O(n) per operation, O(n^2) overall.

dynamic_arrays_lab: passed
```

## 7. Check Your Understanding (University Self-Assessment)

1. **Question**: If a dynamic array currently has `length = 8` and `capacity = 8`, how many elements will be copied during the next `append()` operation if the growth factor is $2\times$?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>8 elements</b> will be copied to the new block of capacity 16, plus 1 insertion for the new element.</details>

2. **Question**: What is the difference between `Length` and `Capacity` in a dynamic array?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>Length</b> is how many items are actively stored. <b>Capacity</b> is the total allocated memory block size including empty headroom slots.</details>

3. **Question**: Why would changing a dynamic array's growth strategy from "multiply capacity by 2" to "add 100 slots when full" be a terrible performance decision?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Adding fixed slots causes resizes to occur at linear frequency. The total work for N appends becomes quadratic O(n²), turning the average cost of <code>append()</code> from O(1) into O(n).</details>

---

## Practice - independent task

Implement `pop()` and automatic shrinking, then measure the hazard it creates.

- Add `pop()` removing the last element in O(1).
- Add shrinking: when size drops below **half** capacity, halve the capacity.
- Now write a loop that repeatedly appends one element and pops it, at exactly the boundary where capacity flips. Count the copies.
- **You should see thrashing** - every single operation triggers a resize.
- Fix it by shrinking only when size drops below **a quarter** of capacity. Re-measure.

**Done when:** you can state how many copies the naive shrink rule costs for 1000 alternating operations versus the quarter rule, and explain why hysteresis fixes it.

<details><summary>Hint - open only after an attempt</summary>
With shrink-at-half, an array sitting at exactly half capacity that gains one element grows (copying everything), and losing it again shrinks (copying everything). Each operation is O(n), so the sequence is O(n^2).<br>
Shrinking at a <em>quarter</em> leaves a gap between the grow threshold and the shrink threshold, so a single element cannot cross both. That gap is <strong>hysteresis</strong>, and every real implementation has some form of it.
</details>

## Before moving on

You are done with this module when you can, closed-book:

- [ ] Explain why growing requires allocate-and-copy rather than extending in place.
- [ ] Compute total copies for n appends under doubling and show it is bounded by 2n.
- [ ] Explain why growing by a fixed chunk is O(n^2) overall.
- [ ] State why amortised O(1) is not the same as O(1).

**Recap:** A dynamic array wraps a fixed-capacity block, reallocating when full. Doubling means the copies form a geometric series summing to under 2n, so n appends cost O(n) in total and each append is amortised O(1) - some are expensive, the average is constant. Growing by a fixed amount instead makes the total O(n^2). Front insertion remains O(n) because contiguity must be preserved.

**Next:** [[03-hash-maps|Hash Maps]] - the structure that gives up ordering entirely to buy O(1) lookup by key.

## Related Modules
- [[01-arrays|Arrays]] — The static contiguous foundation
- [[04-linked-lists|Linked Lists]] — The pointer-based alternative with $O(1)$ front insertions
- [[07-stacks-and-queues|Stacks and Queues]] — LIFO/FIFO structures built using dynamic arrays
