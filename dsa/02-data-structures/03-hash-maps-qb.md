# Hash Maps & Hash Sets — Question Bank

Micro-questions over [[03-hash-maps|the hash maps module]]. Answer in a full sentence before opening the toggle. Format explained in [[01-arrays-qb|the arrays bank]].

---

## A. The object itself

**1. What is a hash map?**

<details><summary>Answer</summary>

A structure that stores pairs of things so you can look one up by the other almost instantly.

</details>

**2. What is it called in Python, C++, Java and JavaScript?**

<details><summary>Answer</summary>

`dict` in Python, `map` in C++ and Java, object (and `Map`) in JavaScript. Also called a hash table or a dictionary generally.

</details>

**3. Why do hash maps exist?**

<details><summary>Answer</summary>

Arrays let you look up by **position**. Hash maps let you look up by **any key you choose** — a username, a product code, a word — at the same $O(1)$ speed.

</details>

**4. What is a key?**

<details><summary>Answer</summary>

The thing you look something up *by*. Keys are unique within the map; storing a pair with an existing key overwrites the old value.

</details>

**5. What is a value?**

<details><summary>Answer</summary>

The thing stored *against* a key. Values have no restrictions at all and can repeat freely.

</details>

**6. What is a hash set, and how does it relate to a hash map?**

<details><summary>Answer</summary>

A hash map that stores keys with no values. It answers exactly one question instantly: *have I seen this before?*

</details>

---

## B. The vocabulary

**7. What is a hash function?**

<details><summary>Answer</summary>

A function taking a key and returning a large integer. The same key always gives the same integer; different keys usually give different ones. It turns "look up this word" into "go to this array position".

</details>

**8. What is a bucket?**

<details><summary>Answer</summary>

One slot in the underlying array where entries are kept. The hash function decides which bucket a key belongs in.

</details>

**9. How is a hash value turned into a bucket index?**

<details><summary>Answer</summary>

Modulo the number of buckets: `index = hash(key) % capacity`.

</details>

**10. What is a collision?**

<details><summary>Answer</summary>

Two **different** keys landing in the same bucket.

</details>

**11. Are collisions a bug?**

<details><summary>Answer</summary>

No, and they cannot be avoided — there are more possible keys than buckets, so some must share. The design question is never how to prevent them, only how to handle them.

</details>

**12. What is chaining?**

<details><summary>Answer</summary>

Each bucket holds a small list of all entries that landed there; a lookup walks that short list.

</details>

**13. What is open addressing?**

<details><summary>Answer</summary>

Every entry lives directly in the flat array. When a bucket is taken, the entry goes into another bucket found by a fixed rule.

</details>

**14. What is linear probing?**

<details><summary>Answer</summary>

The simplest open-addressing rule: if slot $i$ is taken, try $i+1$, then $i+2$, and so on.

</details>

**15. What is the load factor, and what is its symbol?**

<details><summary>Answer</summary>

How full the map is — entries divided by buckets, written $\alpha$.
$$\alpha = \frac{\text{total entries}}{\text{total capacity}}$$

</details>

**16. What is rehashing?**

<details><summary>Answer</summary>

Allocating a larger bucket array and **recomputing the bucket for every existing entry** — necessary because the bucket depends on the array size. It is $O(n)$.

</details>

---

## C. The pipeline

**17. Walk through the three steps of `map["apple"] = 100`.**

<details><summary>Answer</summary>

1. Hash the key: `hash("apple")` → a large integer.
2. Reduce to an index: `integer % capacity` → e.g. bucket 5.
3. Store the pair in bucket 5.

</details>

**18. Why must the hash be *deterministic*?**

<details><summary>Answer</summary>

Because lookup repeats the same computation. If `hash("apple")` returned something different the second time, you would probe the wrong bucket and the entry would be unreachable.

</details>

**19. What property makes a hash function *good*?**

<details><summary>Answer</summary>

It spreads keys uniformly across buckets, so no bucket gets disproportionately many. Uniform spread is what keeps chains short and lookups $O(1)$.

</details>

---

## D. Collision strategies compared

**20. Chaining vs open addressing — where does each store the entries?**

<details><summary>Answer</summary>

Chaining: the bucket holds a pointer to a list node, so entries live scattered on the heap. Open addressing: everything lives in one flat array.

</details>

**21. Which has better cache behaviour, and why?**

<details><summary>Answer</summary>

Open addressing. Probing walks sequential array slots, so the probe sequence is usually already in the cache line you fetched. Chained list nodes are scattered, so each hop is a potential cache miss.

</details>

**22. What load factor can each tolerate?**

<details><summary>Answer</summary>

Chaining can exceed $1.0$ — the lists just grow. Open addressing must stay below $1.0$, because it fails outright when the array is full.

</details>

**23. Why is deletion harder under open addressing?**

<details><summary>Answer</summary>

Emptying a slot breaks the probe chain: a later key that probed past that slot becomes unfindable. The fix is a **tombstone** — a marker meaning "empty, but keep probing past me".

</details>

**24. Which strategy do modern languages use?**

<details><summary>Answer</summary>

Open addressing — Python's `dict`, Rust's `HashMap`, C++ flat maps. Chaining is the textbook classic and what Java's `HashMap` uses.

</details>

---

## E. Load factor and resizing

**25. What happens if the load factor is left to climb?**

<details><summary>Answer</summary>

Collisions become frequent, chains and probe sequences get long, and $O(1)$ lookups degrade toward $O(n)$ scans.

</details>

**26. What is the typical load factor threshold?**

<details><summary>Answer</summary>

Around $0.7$.

</details>

**27. What are the three steps when the threshold is crossed?**

<details><summary>Answer</summary>

1. Allocate a new bucket array with double the capacity.
2. Re-hash every existing key into it.
3. Free the old array.

</details>

**28. Why can't the old bucket assignments simply be copied across?**

<details><summary>Answer</summary>

The bucket index is `hash % capacity`, and the capacity just changed. Every key's index must be recomputed.

</details>

**29. Why does this make hash map operations *amortised* $O(1)$?**

<details><summary>Answer</summary>

Same argument as [[02-dynamic-arrays|dynamic arrays]]: capacity doubles, so rehashes get exponentially rarer and their $O(n)$ cost spreads over an ever-larger number of cheap operations.

</details>

---

## F. Costs

**30. Average and worst-case cost of lookup?**

<details><summary>Answer</summary>

$O(1)$ average, $O(n)$ worst case.

</details>

**31. Average cost of insert and delete?**

<details><summary>Answer</summary>

$O(1)$ amortised for insert (rehashing), $O(1)$ average for delete. Both $O(n)$ worst case.

</details>

**32. Space complexity?**

<details><summary>Answer</summary>

$O(n)$ — plus the deliberately unused buckets that keep the load factor low.

</details>

**33. When does the worst case actually happen?**

<details><summary>Answer</summary>

When every key lands in one bucket — from a bad hash function, or from an attacker choosing colliding keys on purpose.

</details>

**34. What is hash collision denial-of-service?**

<details><summary>Answer</summary>

An attacker submits keys chosen to collide (e.g. as form fields or JSON keys), forcing every lookup to $O(n)$ and collapsing the server under $O(n^2)$ work. It is why languages now **randomise their hash seed at startup**.

</details>

---

## G. The ADT and what is absent

**35. List the hash map ADT.**

<details><summary>Answer</summary>

`put(key, value)`, `get(key)`, `contains(key)`, `delete(key)` — all $O(1)$ average; `size()` — $O(1)$; `keys()`/`values()`/`items()` — $O(n)$, in no guaranteed order.

</details>

**36. Why can a hash map not tell you the smallest key?**

<details><summary>Answer</summary>

The smallest key sits in an arbitrary bucket, so you would have to check all $n$ of them. A [[08-heaps|heap]] does this in $O(1)$; a balanced tree in $O(\log n)$.

</details>

**37. Why can a hash map not answer range queries?**

<details><summary>Answer</summary>

Nearby keys are nowhere near each other in memory — the hash deliberately scattered them. This is exactly why databases index with B-trees rather than hash tables.

</details>

**38. What single cause explains all three missing operations?**

<details><summary>Answer</summary>

**Hashing deliberately destroys order.** Scattering similar keys to unrelated buckets is what avoids collisions, and in scattering it throws away every relationship between keys.

</details>

**39. Python `dict` preserves order since 3.7. Does that contradict the above?**

<details><summary>Answer</summary>

No. It preserves **insertion** order, not sorted order, using an extra list kept alongside the buckets. It gives you none of min-key, range query, or successor.

</details>

**40. Why must keys be immutable?**

<details><summary>Answer</summary>

If a key's internal data changes after insertion, its hash changes, so it now belongs in a different bucket than the one it sits in — and becomes permanently unreachable. In Python, lists cannot be keys; tuples can.

</details>

---

## H. Using them

**41. What is "the single most common speedup in software engineering"?**

<details><summary>Answer</summary>

Replacing a list with a set for membership testing — turning an $O(n)$ scan inside an $O(n)$ loop ($O(n^2)$ total) into an $O(1)$ check inside it ($O(n)$ total).

</details>

**42. Why is `if item in some_list` a trap?**

<details><summary>Answer</summary>

`in` on a list is a full linear scan. It looks identical to `in` on a set, which is a single hash lookup — same syntax, completely different cost.

</details>

**43. When should you *not* reach for a hash map?**

<details><summary>Answer</summary>

When you need ordering, ranges, nearest-neighbour or min/max — use a balanced tree, a B-tree or a heap. Also when keys are few and small, where a plain array indexed directly is simpler and faster.

</details>

**44. State the hash map's trade in one sentence.**

<details><summary>Answer</summary>

It buys $O(1)$ lookup by any key, and pays with the entire notion of order — plus an average-case asterisk that an adversary can exploit.

</details>

---

## Scorecard

| Pass | Date | Got it | Close | Blank | Questions missed |
| :--- | :--- | :----- | :---- | :---- | :--------------- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Related

- [[03-hash-maps|Hash Maps & Hash Sets]] — the module
- [[02-dynamic-arrays-qb|Dynamic Arrays — Question Bank]] — where the same doubling/amortised argument appears
- [[05-trees/03-binary-search-trees|Binary Search Trees]] — the ordered alternative
