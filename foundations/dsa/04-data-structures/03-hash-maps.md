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

| | Chaining | Open addressing |
|---|---|---|
| Collision handling | bucket holds a list | probe for another slot |
| Load factor can exceed 1 | ✓ | ✗ — never more entries than slots |
| Memory | pointer overhead per entry | no pointers, denser |
| Cache behaviour | poor — chains are scattered | **good** — probing stays in nearby memory |
| Deletion | straightforward | needs tombstones, or lookups break |
| Used by | Java `HashMap`, most textbooks | Python `dict`, Rust `HashMap`, most modern implementations |

Open addressing has won in most modern standard libraries for the cache reason: probing a few adjacent slots costs less than one pointer-chase to a scattered list node. Its awkwardness is deletion — you can't just empty a slot, because that would break the probe chain for any key that hashed past it, so deleted slots get a **tombstone** marker instead.

## What makes a good hash function

Three properties, and the first is the one that actually matters:

1. **Uniform distribution** — keys should spread evenly across buckets. A hash that clumps turns O(1) into O(n) by piling everything into a few buckets. This is the whole job.
2. **Deterministic** — the same key must always hash to the same value, within a single run of the program.
3. **Fast** — hashing happens on every single operation, so an expensive hash eats the benefit it's providing.

Note what's *not* on the list: cryptographic security. A hash map wants speed and spread, which is why they use fast non-cryptographic functions (FNV, MurmurHash, SipHash, xxHash) rather than SHA-256. **A hash map's hash function and a cryptographic hash function solve different problems** — conflating them is a common misconception.

**Determinism is per-run, not forever.** Python randomises its string-hash seed at interpreter startup, so `hash("apple")` differs between runs. That's a deliberate defence against the hash-flooding attack below: if an attacker can't predict your hash values, they can't craft keys that all collide. It's also why hash values must never be persisted to disk or used across processes.

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

## Hash sets

A **hash set** is the same structure with the values thrown away — it stores only keys, answering "have I seen this?" in O(1). Python's `set`, Java's `HashSet`, Go's `map[T]struct{}`. Internally it's a hash map whose values are ignored, so every complexity figure above carries over unchanged.

The reason it deserves naming: **swapping a list for a set is the single most common optimisation in practice.**

```python
if x in some_list:     # O(n) — scans the whole list
if x in some_set:      # O(1) — hashes and jumps
```

Inside a loop over n items, that one substitution takes the code from O(n²) to O(n). If you catch yourself scanning a collection to check membership, that's the signal.

## Choosing a hash map vs the alternatives

| Need | Use | Why |
|---|---|---|
| Lookup by arbitrary key | **hash map** | O(1) average |
| Lookup by small integer index | **[[01-arrays|array]]** | O(1) guaranteed, no hashing, far better cache behaviour |
| Membership only, no value | **hash set** | same speed, less memory |
| Keys in **sorted** order | **balanced [[01-trees|BST]]** (`TreeMap`, `std::map`) | O(log n), but ordered iteration and range queries — a hash map cannot do either |
| Smallest/largest repeatedly | **[[08-heaps|heap]]** | O(1) peek, O(log n) pop |
| Prefix queries on string keys | **[[09-tries|trie]]** | hash maps can't answer "all keys starting with…" at all |

**The recurring tradeoff: a hash map buys O(1) by destroying order.** Hashing deliberately scatters keys, so there is no cheap way to ask for the smallest key, keys in a range, or keys with a given prefix. When you need any of those, an ordered structure earns its extra log n.

Also worth remembering the constant factor: if your keys are already small integers, **use an array**. `counts = [0] * 26` for letter frequencies beats a dict — no hashing, no collisions, perfect cache locality. Big-O calls both O(1); the array is several times faster.

## Gotchas

- **Keys must be hashable, which usually means immutable.** In Python, `list`s can't be dict keys (`TypeError: unhashable type`) but `tuple`s can — because a mutable key could change after being hashed, silently breaking the table's internal structure. See [[foundations/programming-fundamentals/15-how-types-actually-work|data-type-classification]] for why immutability matters here.
- **Python dicts preserve insertion order** (guaranteed since 3.7) — but don't rely on this in languages where it isn't guaranteed (older Python, many other languages' hash map implementations).
- A "hash map is O(1)" is an *average case* claim — don't state it as a worst-case guarantee in an interview without the caveat.
- Iterating a hash map has no defined order tied to hash values — never assume keys come back sorted or in insertion order unless the language specifically promises it.

## Related
- [[01-arrays|arrays]] — the bucket array underneath, and the better choice for integer keys
- [[foundations/programming-fundamentals/15-how-types-actually-work|data-type-classification]] — hashability and immutability
- [[02-dynamic-arrays|dynamic-arrays]] — resizing follows the same amortized logic
- [[01-algorithms|algorithms]] — why this is amortized O(1) and not worst-case O(1)
