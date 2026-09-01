# Dynamic Arrays

A dynamic array is a static [[01-arrays|array]] wearing a trench coat — underneath, it's still a fixed-size contiguous block, but it manages that block for you: when it fills up, it silently allocates a bigger block, copies everything over, and keeps going. Python's `list`, JavaScript's `Array`, C++'s `vector`, Java's `ArrayList` are all this.

## Why it exists

Plain arrays can't grow — the size is fixed at allocation. But "I don't know how many elements I'll need ahead of time" is the normal case, not the exception. Dynamic arrays give you array-speed indexing *and* the ability to grow, at the cost of occasional, amortized-cheap resize operations.

## How it works

Internally it tracks two numbers: **length** (how many elements are actually in use) and **capacity** (how big the underlying block actually is). Capacity is usually bigger than length, as headroom.

```
length = 3, capacity = 4
+-----+-----+-----+-----+
|  10 |  22 |  7  |  _  |   <- one empty slot left
+-----+-----+-----+-----+
```

When you append and there's no room left (`length == capacity`):

1. Allocate a new, bigger block — typically **double** the capacity.
2. Copy all existing elements into the new block.
3. Free the old block.
4. Append the new element.

```
append(41) when full:
old: [10, 22, 7]         capacity 3
new: [10, 22, 7, 41, _, _]   capacity 6 (doubled)
```

## Why doubling makes append "amortized O(1)"

A single resize costs O(n) — you copy every element. But because capacity doubles each time, resizes become exponentially rarer as the array grows. If you append n elements one at a time starting from empty, the total cost of all the resizing (1 + 2 + 4 + 8 + ... + n ≈ 2n) is O(n) — spread across n appends, that's O(1) **on average**, even though any single append might occasionally cost O(n).

This "average cost over a sequence of operations" is what *amortized* means — it's not that every append is cheap, it's that expensive ones are rare enough to not matter over time. Growing by a fixed amount (e.g. +1 each time) instead of doubling would make every append O(n) amortized — this is why the growth factor matters and isn't just an implementation detail.

## Complexity

| Operation | Time | Note |
|---|---|---|
| Access by index | O(1) | same as static array |
| Append at end | O(1) amortized | O(n) worst case, on a resize |
| Insert/delete at start/middle | O(n) | shifting, same as static array |
| Search | O(n) unsorted / O(log n) sorted | see [[05-searching\|searching]] |

## Example

```python
arr = []
for i in range(5):
    arr.append(i)   # each append is O(1) amortized;
                     # CPython grows the underlying array in chunks, not one at a time
```

## Gotchas

- `len(arr)` is the **length**, not the capacity — the extra headroom is invisible from the outside in most languages, which is exactly why occasional resizes are surprising if you don't know they're happening.
- Inserting at index 0 (`arr.insert(0, x)`) is still O(n) even on a dynamic array — resizing solved the growth problem, not the shifting problem.
- If you know the final size ahead of time, pre-allocating (e.g. `[None] * n` in Python) avoids repeated resizing entirely — worth doing in performance-sensitive code.

## Related
- [[01-arrays|arrays]]
- [[01-algorithms|algorithms]] — amortized analysis
