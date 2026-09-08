# Module: Dynamic Arrays (Resizable Contiguous Storage)

Welcome to the **Dynamic Arrays** module. A dynamic array is a static [[01-arrays|array]] with a smart management layer built around it. It provides the lightning-fast $O(1)$ access speed of a static array, while automatically growing in size whenever it fills up.

Dynamic arrays are what high-level languages hand you by default: Python's `list`, JavaScript's `Array`, C++'s `std::vector`, and Java's `ArrayList`.

---

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

## 7. Check Your Understanding (University Self-Assessment)

1. **Question**: If a dynamic array currently has `length = 8` and `capacity = 8`, how many elements will be copied during the next `append()` operation if the growth factor is $2\times$?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>8 elements</b> will be copied to the new block of capacity 16, plus 1 insertion for the new element.</details>

2. **Question**: What is the difference between `Length` and `Capacity` in a dynamic array?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>Length</b> is how many items are actively stored. <b>Capacity</b> is the total allocated memory block size including empty headroom slots.</details>

3. **Question**: Why would changing a dynamic array's growth strategy from "multiply capacity by 2" to "add 100 slots when full" be a terrible performance decision?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Adding fixed slots causes resizes to occur at linear frequency. The total work for N appends becomes quadratic O(n²), turning the average cost of <code>append()</code> from O(1) into O(n).</details>

---

## Related Modules
- [[01-arrays|Arrays]] — The static contiguous foundation
- [[04-linked-lists|Linked Lists]] — The pointer-based alternative with $O(1)$ front insertions
- [[07-stacks-and-queues|Stacks and Queues]] — LIFO/FIFO structures built using dynamic arrays
