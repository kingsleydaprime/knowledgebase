# Arrays

An array is a fixed-size, contiguous block of memory holding elements of the same type. "Contiguous" is the entire point — it's what makes constant-time indexing possible, and it's the property every other structure in this folder gets compared against.

## Why it exists

If elements are all the same size and stored back to back, the address of element `i` is just arithmetic:

```
address(i) = base_address + (i * element_size)
```

No searching, no following pointers — just one multiplication and one addition. That's why `arr[i]` is O(1): the CPU computes the address directly instead of walking anything.

## How it works

```
index:     0     1     2     3     4
         +-----+-----+-----+-----+-----+
value:   | 10  | 22  |  7  | 41  |  3  |
         +-----+-----+-----+-----+-----+
address: 1000  1004  1008  1012  1016   (4-byte ints)
```

Because it's one contiguous block, the array's size has to be known and fixed at allocation time (in low-level languages like C, this is literal — you request N * element_size bytes once). Growing it means allocating a whole new block elsewhere and copying everything over, which is exactly the problem [[02-dynamic-arrays|dynamic-arrays]] solve.

## Kinds of array

Three distinctions that get conflated, and each changes what the code can do:

**Static vs dynamic.** A **static array** has its size fixed at allocation — C's `int arr[100]`, Java's `new int[100]`. A **dynamic array** wraps a static one and reallocates when it fills, which is what Python's `list`, JavaScript's `Array`, C++'s `vector` and Java's `ArrayList` actually are. Most languages hand you the dynamic version by default, so the fixed-size constraint is real but usually hidden — see [[02-dynamic-arrays|dynamic-arrays]].

**Values vs references.** In C or Java, an `int[]` stores the integers themselves, back to back — 4 bytes each, perfectly contiguous. A Python list stores *pointers* to objects scattered on the heap. So `[1, 2, 3]` in Python is contiguous in its *pointers* but not its *values*, which is why the cache-friendliness below applies fully to C arrays and NumPy arrays but only partially to Python lists. It's also why NumPy exists.

**One-dimensional vs multi-dimensional vs jagged.** A **2-D array** is a rectangular grid where every row has the same length. A **jagged array** is an array of arrays whose rows can differ in length — `[[1,2], [3], [4,5,6]]`. Python only really has the jagged kind (a list of lists); C and NumPy have true rectangular arrays. The difference matters because a true 2-D array is **one contiguous block**, while a list of lists is a list of pointers to separately-allocated rows.

## Multi-dimensional arrays and memory layout

Memory is one-dimensional. A 2-D array is therefore a flattening, and which direction it flattens is **row-major order** (rows stored one after another — C, Python, Java) or **column-major order** (columns first — Fortran, MATLAB, R).

```
grid = [[1, 2, 3],
        [4, 5, 6]]

row-major in memory:  1  2  3  4  5  6      <- row 0, then row 1
                      ^-----^  ^-----^

address(r, c) = base + (r * num_cols + c) * element_size
```

That formula is why `grid[r][c]` is still O(1) — one multiply, one add, same as the 1-D case.

**And it has a performance consequence people hit constantly.** Iterating in the same order as the layout walks memory sequentially; iterating across it jumps a whole row on every step:

```python
for r in range(rows):          # fast — follows row-major layout
    for c in range(cols):
        total += grid[r][c]

for c in range(cols):          # slow — jumps rows-worth of memory each step
    for r in range(rows):
        total += grid[r][c]
```

Both are O(rows × cols). The second can be **several times slower in wall-clock time** on a large matrix, purely from cache misses — every access lands on a different cache line, so nothing prefetched ever gets used. Same Big-O, very different program. This is the clearest everyday example of why complexity isn't the whole story, and the same effect drives loop-order choice in matrix multiplication and image processing.

**Flattening is sometimes worth doing yourself.** A grid stored as a single array of length `rows*cols`, indexed `grid[r * cols + c]`, guarantees contiguity even in languages where nested lists wouldn't. Bit-packing a grid of booleans into integers is the same instinct taken further.

## Strings are arrays

In most languages a string is an array of characters (or bytes) with extra methods bolted on, which means **every array insight above applies to strings**: indexing is O(1), scanning is O(n), and inserting into the middle is O(n) because everything shifts.

The wrinkle is immutability. In Python, Java, JavaScript and C#, strings can't be modified in place — every "modification" allocates a whole new string and copies. That makes the innocent-looking loop below O(n²):

```python
result = ""
for ch in chars:
    result += ch          # allocates and copies the whole string, every time
```

The fix is to collect the pieces in a list and join once at the end — O(n). Java's `StringBuilder` and Go's `strings.Builder` exist for exactly this reason, and this is one of the most common accidental-quadratic bugs in real code.

## Complexity

| Operation | Time | Why |
|---|---|---|
| Access by index | O(1) | direct address calculation |
| Search (unsorted) | O(n) | no shortcuts, check every element |
| Search (sorted) | O(log n) | binary search — see [[05-searching|searching]] |
| Insert/delete at end | O(1) | no shifting needed |
| Insert/delete at start/middle | O(n) | every element after the gap has to shift |

## Example

```python
arr = [10, 22, 7, 41, 3]

arr[2]                  # O(1) -> 7
arr.insert(0, 99)       # O(n) -> everything shifts right by one
del arr[0]              # O(n) -> everything shifts left by one
```

## Why arrays are cache-friendly

Contiguous memory means that when the CPU pulls `arr[i]` into cache, it also pulls in `arr[i+1]`, `arr[i+2]`, etc. (a whole cache line, typically 64 bytes). Iterating an array sequentially is fast in practice, not just in Big-O — this is a real, measurable win over structures like [[04-linked-lists|linked-lists]] where each node can be scattered anywhere in memory.

## Gotchas

- Fixed size is a hard constraint in truly static arrays (C-style) — there's no "just add one more" without reallocating. Most languages hide this behind a dynamic array (Python `list`, JS `Array`, C++ `vector`) — see [[02-dynamic-arrays|dynamic-arrays]].
- Insert/delete "at the front" being O(n) is the single most common complexity mistake people make when reasoning about arrays under interview pressure — it's easy to assume every operation is O(1) because access is.
- Out-of-bounds access is undefined behavior in C (reads garbage memory or crashes) but raises a clear `IndexError` in Python — don't assume every language protects you here.

## Related
- [[02-dynamic-arrays|dynamic-arrays]] — the resizable wrapper you actually use
- [[04-linked-lists|linked lists]] — the non-contiguous alternative, and the opposite set of tradeoffs
- [[05-searching|searching]] and [[04-sorting|sorting]]
- [[13-matrix-traversal|matrix traversal]] — 2-D arrays walked as implicit graphs
- [[01-prefix-sum|prefix sum]] — preprocessing an array for O(1) range queries
