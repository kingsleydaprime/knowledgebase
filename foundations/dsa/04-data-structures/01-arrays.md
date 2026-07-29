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
- [[02-dynamic-arrays|dynamic-arrays]]
- [[05-searching|searching]]
- [[04-sorting|sorting]]
