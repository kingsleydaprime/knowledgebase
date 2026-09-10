# Module: Arrays (Contiguous Memory & Fast Access)

Welcome to the **Arrays** module. An array is the simplest, most fundamental data structure in computer science. Almost every other structure (Dynamic Arrays, Hash Maps, Heaps, Stacks, Queues) is built on top of arrays.

---

## Before you start

- You can read a small Python function.
- You know what a byte is and that memory is addressed numerically.

**What you will be able to do after this lesson:**

1. Compute the memory address of any element from the base address and index.
2. Explain why indexing is O(1) and why searching an unsorted array is not.
3. Explain how a 2-D grid is flattened, and why row-major scanning is faster.
4. Explain why building a string with += in a loop is O(n^2).

**Study route:** read the mechanism, run the lab, then attempt the independent task before opening the hint.

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

## Implementation - complete runnable example

**Runnable example:** save as `arrays_lab.py` and run `python3 arrays_lab.py`. Standard library only; writes no files. Everything is counted rather than timed, so your output will match this exactly.

```python
"""Arrays: address arithmetic, row-major layout, and the concatenation trap.

Everything here is counted rather than timed, so the output is identical
on every machine."""

def address_of(base, index, element_size):
    """The single calculation the CPU performs for arr[i]. No searching."""
    return base + index * element_size

def flat_index(row, col, n_cols):
    """Row-major: a 2-D grid laid out as one 1-D run of memory."""
    return row * n_cols + col

def scan_order(rows, cols, row_major):
    """Return the flat indices a nested loop touches, in order."""
    if row_major:
        return [flat_index(r, c, cols) for r in range(rows) for c in range(cols)]
    return [flat_index(r, c, cols) for c in range(cols) for r in range(rows)]

def cache_lines_touched(indices, element_size=4, line_bytes=64):
    """Count how many times the scan moves to a different 64-byte cache line.

    Sequential access reuses one line for several elements; strided access
    lands on a new line almost every time, and each change is a real fetch."""
    per_line = line_bytes // element_size
    changes, last = 0, None
    for i in indices:
        line = i // per_line
        if line != last:
            changes += 1
            last = line
    return changes

def naive_concat_copies(n):
    """Immutable strings: `result += ch` copies the whole result each time."""
    return sum(range(n))          # 0 + 1 + 2 + ... + (n-1) characters copied

def join_copies(n):
    """"".join(parts) allocates once and copies each character once."""
    return n

if __name__ == "__main__":
    print("ADDRESS ARITHMETIC -- why arr[i] is O(1)")
    base, size = 1000, 4
    for i in (0, 3, 4, 500):
        print(f"  arr[{i:3d}] lives at {base} + {i} x {size} = {address_of(base, i, size)}")
    print("  the same one multiplication and one addition, whatever i is.")
    print()

    print("ROW-MAJOR LAYOUT -- a 2-D grid is a lie told over 1-D memory")
    grid = [[1, 2, 3], [4, 5, 6]]
    flat = [v for row in grid for v in row]
    print(f"  grid  = {grid}")
    print(f"  memory= {flat}")
    for r, c in [(0, 0), (1, 0), (1, 2)]:
        print(f"  grid[{r}][{c}] -> flat index {flat_index(r, c, 3)} -> {flat[flat_index(r,c,3)]}")
    print()

    print("CACHE LOCALITY -- same Big-O, different memory behaviour")
    rows, cols = 64, 64
    for label, rm in (("row-major (rows inner)", True), ("column-major (cols inner)", False)):
        fetches = cache_lines_touched(scan_order(rows, cols, rm))
        print(f"  {label:26s} {fetches:6d} cache-line fetches")
    rm = cache_lines_touched(scan_order(rows, cols, True))
    cm = cache_lines_touched(scan_order(rows, cols, False))
    print(f"  -> column-major fetches {cm/rm:.0f}x more lines for identical work")
    print("     both loops are O(rows x cols). Big-O cannot see this.")
    print()

    print("THE STRING CONCATENATION TRAP -- characters copied")
    print(f"  {'n':>6s} {'result += ch':>14s} {'join':>8s} {'ratio':>8s}")
    for n in (10, 100, 1000):
        a, b = naive_concat_copies(n), join_copies(n)
        print(f"  {n:6d} {a:14,d} {b:8,d} {a/b:7.1f}x")
    print("  += inside a loop is O(n^2) because each += copies everything so far.")

    assert address_of(1000, 3, 4) == 1012
    assert flat_index(1, 2, 3) == 5
    assert cm > rm
    assert naive_concat_copies(1000) > 100 * join_copies(1000)
    print()
    print("arrays_lab: passed")
```

Expected output:

```
ADDRESS ARITHMETIC -- why arr[i] is O(1)
  arr[  0] lives at 1000 + 0 x 4 = 1000
  arr[  3] lives at 1000 + 3 x 4 = 1012
  arr[  4] lives at 1000 + 4 x 4 = 1016
  arr[500] lives at 1000 + 500 x 4 = 3000
  the same one multiplication and one addition, whatever i is.

ROW-MAJOR LAYOUT -- a 2-D grid is a lie told over 1-D memory
  grid  = [[1, 2, 3], [4, 5, 6]]
  memory= [1, 2, 3, 4, 5, 6]
  grid[0][0] -> flat index 0 -> 1
  grid[1][0] -> flat index 3 -> 4
  grid[1][2] -> flat index 5 -> 6

CACHE LOCALITY -- same Big-O, different memory behaviour
  row-major (rows inner)        256 cache-line fetches
  column-major (cols inner)    4096 cache-line fetches
  -> column-major fetches 16x more lines for identical work
     both loops are O(rows x cols). Big-O cannot see this.

THE STRING CONCATENATION TRAP -- characters copied
       n   result += ch     join    ratio
      10             45       10     4.5x
     100          4,950      100    49.5x
    1000        499,500    1,000   499.5x
  += inside a loop is O(n^2) because each += copies everything so far.

arrays_lab: passed
```

## 8. Check Your Understanding (University Self-Assessment)

1. **Question**: An array of 8-byte integers starts at memory address `2000`. What is the exact memory address of `arr[4]`?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>2032</b>. Calculation: <code>2000 + (4 * 8) = 2000 + 32 = 2032</code>.</details>

2. **Question**: Why is inserting an item at the beginning of an array ($O(n)$) much slower than appending an item at the end ($O(1)$)?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Elements in an array live in contiguous memory. Inserting at index 0 requires physically shifting every existing element one slot to the right to make room.</details>

3. **Question**: Why does scanning a 2D matrix row-by-row run faster than scanning column-by-column in C/Python?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Memory is 1D and stores rows back-to-back (Row-Major Order). Scanning row-by-row reads sequential memory addresses, utilizing the CPU cache line efficiently (Cache Locality).</details>

---

## Practice - independent task

Implement `transpose(grid)` returning a new grid with rows and columns swapped, **using only flat 1-D lists and index arithmetic** - no nested lists, no `zip`.

- Represent an `r x c` grid as a flat list of length `r*c` plus the two dimensions.
- Write `get(flat, r, c, n_cols)` and `set(flat, r, c, n_cols, v)` using `row * n_cols + col`.
- Transpose a 2x3 into a 3x2 and verify against a nested-list version.
- **Then answer:** does your transpose read row-major and write column-major, or the reverse? Which of the two loops has poor locality, and could you fix it by swapping the loop order?

**Done when:** your flat transpose matches a nested-list reference on a 3x4 grid, and you can say which access pattern in it is cache-unfriendly.

<details><summary>Hint - open only after an attempt</summary>
The output grid's dimensions are swapped, so <code>out[c][r] = in[r][c]</code> becomes <code>out_flat[c * r_count + r] = in_flat[r * c_count + c]</code>.<br>
One of those walks memory sequentially and the other jumps by a whole row each step. <strong>You cannot make both sequential</strong> - which is exactly why cache-aware transposes process the grid in small blocks rather than row by row.
</details>

## Before moving on

You are done with this module when you can, closed-book:

- [ ] Compute an element's address from base, index and element size.
- [ ] Explain why array indexing is O(1) but front insertion is O(n).
- [ ] Explain row-major layout and why scan order changes speed at identical Big-O.
- [ ] Explain the string concatenation trap and the join fix.

**Recap:** An array is a contiguous block, so any element's address is base + i x size - one multiplication and one addition, regardless of size. That contiguity is also the cost: inserting at the front shifts everything after it. A 2-D grid is flattened row-major, which makes row-wise scanning cache-friendly and column-wise scanning far slower at identical Big-O. Strings are arrays of characters, which is why += in a loop copies everything each time.

**Next:** [[02-dynamic-arrays|Dynamic Arrays]] - arrays cannot grow - this is what happens when you need them to.

## Related Modules
- [[02-dynamic-arrays|Dynamic Arrays]] — How arrays grow automatically when full
- [[04-linked-lists|Linked Lists]] — The non-contiguous alternative using pointers
- [[03-hash-maps|Hash Maps]] — Using array indexing to build $O(1)$ key-value lookups
