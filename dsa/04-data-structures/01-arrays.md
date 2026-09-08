# Module: Arrays (Contiguous Memory & Fast Access)

Welcome to the **Arrays** module. An array is the simplest, most fundamental data structure in computer science. Almost every other structure (Dynamic Arrays, Hash Maps, Heaps, Stacks, Queues) is built on top of arrays.

---

## 1. Why Do Arrays Exist? (Real-World Motivation)

Imagine a physical **row of numbered mailboxes** at a post office:

```
  Box 0       Box 1       Box 2       Box 3       Box 4
+-------+   +-------+   +-------+   +-------+   +-------+
| Letter|   | Letter|   | Letter|   | Letter|   | Letter|
+-------+   +-------+   +-------+   +-------+   +-------+
Address 100  Address 104 Address 108 Address 112 Address 116
```

Because the mailboxes are placed **side-by-side in a straight, unbroken line** (contiguous), you don't need to walk past box 0, box 1, and box 2 to open box 3. You can calculate box 3's exact physical location instantly using arithmetic!

That property—storing items back-to-back in memory—is called **contiguity**, and it is the entire reason arrays exist.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **Contiguous Memory** | Data items placed directly next to each other in memory with zero gaps. | Parked cars in adjacent spaces. |
| **Index** | The zero-based position number of an item in the array. | Element 0 is the 1st item. |
| **Base Address** | The memory address where the very first element (`index 0`) lives. | Memory address `1000`. |
| **Element Size** | The amount of bytes a single item consumes (e.g. 4 bytes for an integer). | 4 bytes per integer. |
| **O(1) Access** | Instant lookup time regardless of array size ($n$). | Grabbing item #500 instantly. |

---

## 3. How Array Math Works ($O(1)$ Address Calculation)

When you write `arr[i]` in code, the computer's CPU does not search or loop. It performs a single fast mathematical calculation to find the exact byte location in RAM:

$$\text{Address of element } i = \text{Base Address} + (i \times \text{Element Size})$$

### Concrete Example
Suppose an array of 4-byte integers starts at memory address `1000`:

```
Index:       0       1       2       3       4
           +-------+-------+-------+-------+-------+
Value:     |  10   |  22   |   7   |  41   |   3   |
           +-------+-------+-------+-------+-------+
Address:    1000    1004    1008    1012    1016
```

To access `arr[3]`:
$$\text{Address} = 1000 + (3 \times 4) = 1000 + 12 = 1012$$

The CPU jumps directly to address `1012`. It takes the exact same fraction of a nanosecond whether the array has 5 items or 5,000,000 items!

---

## 4. Multi-Dimensional Arrays & Memory Layout

Memory in a computer chip is strictly 1-dimensional—a long single row of byte addresses. To store a 2D grid (matrix), languages must **flatten** the grid into a single 1D array.

### Row-Major Order (C, C++, Python, Java)
Rows are stored one after another in memory:

```
grid = [[1, 2, 3],
        [4, 5, 6]]

Flattened in RAM:  [ 1, 2, 3,  4, 5, 6 ]
                   ^-------^  ^-------^
                    Row 0      Row 1
```

To access `grid[row][col]` in a grid with `num_cols`:
$$\text{Address}(r, c) = \text{Base} + (r \times \text{num\_cols} + c) \times \text{Element Size}$$

### Performance Consequence: Cache Locality
When your CPU loads `arr[i]` from RAM into its ultra-fast L1 cache, it automatically grabs a **64-byte block (Cache Line)** containing adjacent elements (`arr[i+1]`, `arr[i+2]`, etc.).

```python
# FAST: Iterates sequentially along memory (High Cache Hits)
for r in range(rows):
    for c in range(cols):
        total += grid[r][c]

# SLOW: Jumps across memory rows (Frequent Cache Misses)
for c in range(cols):
    for r in range(rows):
        total += grid[r][c]
```
> [!NOTE]
> Even though both loops have the same Big-O ($O(\text{rows} \times \text{cols})$), the second loop can be **$3\times$ to $5\times$ slower** in actual runtime due to CPU cache misses!

---

## 5. Strings Are Arrays of Characters

In almost every programming language, a String is simply an array of character bytes with text helper methods attached.

### The String Concatenation Trap
In languages like Python, Java, and JavaScript, strings are **immutable** (cannot be changed in place). Appending to a string inside a loop creates a brand new array and copies all characters over each time:

```python
# BAD: O(n²) total time due to repeated array reallocation!
result = ""
for char in char_list:
    result += char  # Secretly O(n) array copy inside an O(n) loop!

# GOOD: O(n) total time using list join
result = "".join(char_list)
```

---

## 6. Time & Space Complexity Summary

| Operation | Time Complexity | Why? |
| :--- | :--- | :--- |
| **Access by Index (`arr[i]`)** | $O(1)$ | Direct formula calculation ($\text{base} + i \times \text{size}$). |
| **Search (Unsorted)** | $O(n)$ | Must check elements one by one. |
| **Search (Sorted)** | $O(\log n)$ | Binary search (halving remaining range). |
| **Insert / Delete at End** | $O(1)$ | No element shifting required. |
| **Insert / Delete at Front/Middle** | $O(n)$ | Must shift all subsequent elements to make/fill a gap. |

---

## 7. Common Pitfalls & Traps

1. **Front Insertion is $O(n)$**: Calling `arr.insert(0, item)` forces every single element in the array to move right by 1 index.
2. **Fixed Size Constraint**: In low-level languages (C/C++), static arrays cannot grow once allocated. Resizing requires allocating a larger block and copying everything over (solved by [[02-dynamic-arrays|Dynamic Arrays]]).
3. **Index Out of Bounds**: Requesting index `n` on an array of length `n` causes a crash because indices run from `0` to `n-1`.

---

## 8. Check Your Understanding (University Self-Assessment)

1. **Question**: An array of 8-byte integers starts at memory address `2000`. What is the exact memory address of `arr[4]`?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>2032</b>. Calculation: <code>2000 + (4 * 8) = 2000 + 32 = 2032</code>.</details>

2. **Question**: Why is inserting an item at the beginning of an array ($O(n)$) much slower than appending an item at the end ($O(1)$)?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Elements in an array live in contiguous memory. Inserting at index 0 requires physically shifting every existing element one slot to the right to make room.</details>

3. **Question**: Why does scanning a 2D matrix row-by-row run faster than scanning column-by-column in C/Python?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Memory is 1D and stores rows back-to-back (Row-Major Order). Scanning row-by-row reads sequential memory addresses, utilizing the CPU cache line efficiently (Cache Locality).</details>

---

## Related Modules
- [[02-dynamic-arrays|Dynamic Arrays]] — How arrays grow automatically when full
- [[04-linked-lists|Linked Lists]] — The non-contiguous alternative using pointers
- [[03-hash-maps|Hash Maps]] — Using array indexing to build $O(1)$ key-value lookups
