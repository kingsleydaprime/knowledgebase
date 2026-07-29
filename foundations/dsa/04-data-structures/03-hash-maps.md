# Hash Maps

A hash map (dict, hash table, associative array) stores key → value pairs and gets you from a key to its value in average O(1) time, regardless of how many entries it holds. That's the whole pitch — it trades the ordering guarantees of an [[01-arrays|array]] for near-instant lookup by an arbitrary key instead of a numeric index.

## Why it exists

An array gives you O(1) access, but only if you already know the integer index. A hash map answers: "what if my 'index' is a string, a tuple, or any other value?" The trick is to run the key through a **hash function** that converts it into an integer, and use that integer as the index into an underlying array (the "bucket array").

```
key = "apple"
hash("apple") -> 2166136261   (some large integer)
index = hash("apple") % capacity   -> e.g. 5
buckets[5] = ("apple", value)
```

Lookup, insert, and delete all reduce to: hash the key, compute the index, go straight to that bucket — O(1) on average, same reasoning as array indexing, just with an extra hashing step in front.

## Collisions

Two different keys can hash to the same index — that's a **collision**, and it's inevitable once you have more possible keys than buckets. Two common strategies:

- **Chaining**: each bucket holds a small list of (key, value) pairs; on collision, just append to that bucket's list. Lookup becomes "hash to a bucket, then scan the short list."
- **Open addressing**: on collision, probe to a different slot using some rule (linear probing, quadratic probing, double hashing) until an empty one is found.

```
Chaining:
buckets[5] -> [("apple", 1), ("grape", 2)]   <- both hashed to 5, stored together
```

## Load factor and resizing

Load factor = number of entries / number of buckets. As it climbs, collisions get more frequent and average-case O(1) starts to degrade toward O(n) (too many keys crammed into too few buckets). Once load factor crosses a threshold (commonly ~0.7), the table resizes — allocates a bigger bucket array and re-hashes every existing key into it. This is conceptually identical to how [[02-dynamic-arrays|dynamic-arrays]] resize, and it's why hash map operations are described as **amortized** O(1), not strictly O(1).

## Complexity

| Operation | Average | Worst case |
|---|---|---|
| Insert | O(1) | O(n) — everything collides into one bucket |
| Lookup | O(1) | O(n) |
| Delete | O(1) | O(n) |

The worst case is rare in practice with a decent hash function, but it's real — it's the basis of "hash flooding" denial-of-service attacks against naive hash implementations.

## Example

```python
counts = {}
for word in ["a", "b", "a", "c", "a"]:
    counts[word] = counts.get(word, 0) + 1
# {'a': 3, 'b': 1, 'c': 1}

"a" in counts        # O(1) average — membership check
counts.pop("b")      # O(1) average
```

This "count occurrences" pattern is probably the single most common hash map use in interview problems — reach for a dict the moment you catch yourself thinking "how many times have I seen this."

## Gotchas

- **Keys must be hashable, which usually means immutable.** In Python, `list`s can't be dict keys (`TypeError: unhashable type`) but `tuple`s can — because a mutable key could change after being hashed, silently breaking the table's internal structure. See [[03-data-type-classification|data-type-classification]] for why immutability matters here.
- **Python dicts preserve insertion order** (guaranteed since 3.7) — but don't rely on this in languages where it isn't guaranteed (older Python, many other languages' hash map implementations).
- A "hash map is O(1)" is an *average case* claim — don't state it as a worst-case guarantee in an interview without the caveat.
- Iterating a hash map has no defined order tied to hash values — never assume keys come back sorted or in insertion order unless the language specifically promises it.

## Related
- [[03-data-type-classification|data-type-classification]] — hashability and immutability
- [[02-dynamic-arrays|dynamic-arrays]] — resizing follows the same amortized logic
- [[01-arrays|arrays]]
