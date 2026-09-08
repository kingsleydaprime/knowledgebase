# Module: Hash Maps & Hash Sets (Instant Key-Value Lookups)

Welcome to the **Hash Maps** module. A Hash Map (also known as a Dictionary, Hash Table, or Associative Array) is a structure that stores **Key $\rightarrow$ Value** pairs and retrieves values in average **$O(1)$ Constant Time**, regardless of whether the table contains 10 entries or 10,000,000 entries.

If Arrays are the workhorse of memory, Hash Maps are the most useful high-level data structure in software development.

---

## 1. Why Do Hash Maps Exist? (Real-World Motivation)

Imagine a physical **Coat Check Room** at a concert hall:

```
  Guest gives Name ("Alice")  --->  Coat Check Attendant (Hash Function)
                                            |
                                            v
                                  Slot Number #4 (Bucket)
                                  [ Alice's Coat ]
```

- In an [[01-arrays|Array]], you can only retrieve data if you already know a numeric index like `arr[4]`.
- But what if your "index" is a person's name (`"Alice"`), a user ID (`"usr_99"`), or an email address?

A Hash Map acts like that coat check attendant: it takes **any arbitrary key**, transforms it into a numeric slot number, and retrieves the value instantly without searching through every item!

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **Key** | The identifier used to store and look up data. | `"user_alice"`, SSN, Product ID. |
| **Value** | The payload data associated with a key. | User profile object, balance. |
| **Hash Function** | A mathematical function that converts a key into a large integer. | `hash("apple") -> 2166136261`. |
| **Bucket Array** | The underlying array where key-value pairs are stored. | Array of size $N$. |
| **Collision** | When two *different* keys produce the exact same bucket index. | Both `"apple"` and `"grape"` map to bucket #5. |
| **Load Factor ($\alpha$)** | The ratio of occupied entries to total bucket slots ($\frac{\text{entries}}{\text{capacity}}$). | 7 entries in 10 slots ($\alpha = 0.7$). |

---

## 3. How a Hash Map Works (The 3-Step Pipeline)

When you write `map["apple"] = 100`, the Hash Map executes three fast steps:

```
1. Pass Key through Hash Function:
   hash("apple") -> 2,166,136,261

2. Map Large Integer to Bucket Array Index (using Modulo %):
   index = 2,166,136,261 % 8 (capacity) -> 5

3. Store Key-Value Pair in Bucket #5:
   bucket[5] = ("apple", 100)
```

```
Bucket Array:
Slot 0: None
Slot 1: None
...
Slot 5: ("apple", 100)  <-- Direct O(1) Access!
```

---

## 4. Handling Collisions (What Happens When Keys Clash?)

Because there are infinitely many possible strings/keys but a finite number of bucket slots, two different keys will eventually hash to the same bucket index. This is called a **Collision**.

Computer scientists use two primary strategies to resolve collisions:

---

### Strategy 1: Separate Chaining (Linked Lists in Buckets)
Each bucket slot holds a small list of pairs. When a collision occurs, the new pair is appended to that bucket's list.

```
Bucket 5:  [ ("apple", 100) ] -> [ ("grape", 250) ] -> None
```
- **Lookup Process**: Hash to bucket #5, then walk the short list to find the matching key.
- *Used by*: Java `HashMap`.

---

### Strategy 2: Open Addressing (Probing for Next Available Slot)
All entries live directly in the flat array. When a slot is occupied, the table **probes** (scans) for the next open slot using a rule (e.g. check slot $i+1, i+2, \dots$).

```
Bucket 5: ("apple", 100)
Bucket 6: ("grape", 250)  <-- Probed to next slot because Slot 5 was full!
```

#### Comparison of Collision Strategies

| Feature | Separate Chaining | Open Addressing |
| :--- | :--- | :--- |
| **Storage Mechanism** | Bucket contains a pointer to a list node. | Everything lives in one flat array. |
| **Cache Behavior** | Poor (list nodes scattered on heap). | **Excellent** (sequential array probing). |
| **Max Load Factor** | Can exceed $1.0$ (lists grow infinitely). | Must stay $< 1.0$ (fails when full). |
| **Deletion Mechanism** | Simple node removal from list. | Requires **Tombstone** markers so probe chains aren't broken. |
| **Modern Adoption** | Textbook classic. | **Python `dict`**, Rust `HashMap`, C++ `flat_map`. |

---

## 5. Load Factor & Dynamic Resizing

As more items are added to a Hash Map, the buckets fill up and collisions become frequent. Left unchecked, $O(1)$ lookups would slow down to $O(n)$ linear scans.

To prevent this, Hash Maps maintain a **Load Factor Threshold** (typically $\approx 0.7$):

$$\text{Load Factor } (\alpha) = \frac{\text{Total Entries}}{\text{Total Capacity}}$$

When $\alpha > 0.7$:
1. Allocate a **new bucket array** with double the capacity ($2\times$).
2. **Re-hash every existing key** into the new bucket array.
3. Free the old array.

Because resizing happens exponentially rarely, Hash Map operations are **Amortized $O(1)$**.

---

## 6. Hash Sets (Instant Membership Checks)

A **Hash Set** is simply a Hash Map that stores only **Keys without Values**. 

It answers one specific question instantly: *"Have I seen this item before?"*

```python
# BAD: O(n) scan inside an O(n) loop = O(n²) total time
seen_list = []
for item in items:
    if item in seen_list:  # Scans entire list element-by-element!
        print("Duplicate")

# GOOD: O(1) membership check inside an O(n) loop = O(n) total time
seen_set = set()
for item in items:
    if item in seen_set:   # Instant O(1) hash lookup!
        print("Duplicate")
```

> [!TIP]
> **The Golden Optimizations Rule**: Replacing a `List` with a `Set` for membership testing is the single most common speedup in software engineering!

---

## 7. Trade-Offs: What Hash Maps Give Up to Buy $O(1)$

Hash Maps are extraordinarily fast, but they come with trade-offs:

1. **Destroys Order**: Hashing scrambles keys across memory. A standard Hash Map cannot tell you the minimum key, maximum key, or display keys in sorted order.
2. **No Range Queries**: You cannot query "all keys between 10 and 50" without scanning every entry in the map ($O(n)$). (For range queries, use a [[01-trees|Binary Search Tree]] or B+ Tree).
3. **Keys Must Be Immutable**: If a key changes its internal data after being inserted into a dict, its hash changes, rendering the item permanently lost inside the table! (In Python, lists cannot be keys, but immutable tuples can).

---

## 8. Summary of Complexity

| Operation | Average Time | Worst-Case Time (Hash Flooding / Collisions) |
| :--- | :--- | :--- |
| **Lookup (`map[key]`)** | **$O(1)$** | $O(n)$ |
| **Insert (`map[key] = val`)** | **$O(1)$ Amortized** | $O(n)$ |
| **Delete (`del map[key]`)** | **$O(1)$** | $O(n)$ |
| **Space Complexity** | $O(n)$ | $O(n)$ |

---

## 9. Check Your Understanding (University Self-Assessment)

1. **Question**: Why are Python `list`s invalid as dictionary keys (`TypeError: unhashable type`), while `tuple`s are valid?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Lists are <b>mutable</b> (their contents can change). If a key's contents change, its hash value changes, breaking the table's ability to locate it. Tuples are <b>immutable</b> and cannot change after creation.</details>

2. **Question**: What is the difference between a Hash Map and a Balanced Binary Search Tree (BST)? When would you prefer a BST?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A Hash Map provides faster average lookups (<b>O(1)</b> vs <b>O(log n)</b>), but destroys order. You prefer a BST when you need keys stored in <b>sorted order</b> or need to perform <b>range queries</b> (e.g. find all keys between X and Y).</details>

3. **Question**: If a Hash Map has 70 entries and 100 bucket slots, what is its Load Factor? What action will the Hash Map take if 10 more entries are added?
   - <details><summary>Click for Answer</summary><b>Answer:</b> The Load Factor is <b>0.7</b> (70/100). Adding 10 more entries brings the load factor to 0.8, crossing the 0.7 threshold and triggering an automatic capacity resize (doubling buckets to 200) and re-hashing.</details>

---

## Related Modules
- [[01-arrays|Arrays]] — The bucket array foundation underneath
- [[02-dynamic-arrays|Dynamic Arrays]] — Amortized resizing principles
- [[01-trees|Trees]] — Binary Search Trees for ordered key-value storage
- [[09-tries|Tries]] — Prefix trees for string key searches
