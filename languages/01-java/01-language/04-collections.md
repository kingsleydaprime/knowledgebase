# The Collections Framework

**Source:** the projects used `ArrayList`, `HashMap`, `ConcurrentHashMap`, and `Set` heavily (the secondary-index and dedup work in [[languages/01-java/04-persistence/01-jdbc-and-data-modeling|JDBC & Data Modeling]] and [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation]] is real). The systematic framework tour — every interface, the implementation tradeoffs, Big-O — is filled in from [roadmap.sh Java](https://roadmap.sh/java) because it's fundamental and interview-critical, and choosing the right structure is a genuine performance lever.

## The shape of the framework

Two root interfaces, both generic:

- **`Collection<E>`** → `List`, `Set`, `Queue`/`Deque` — a group of elements.
- **`Map<K,V>`** → key→value associations (not technically a `Collection`).

You **program to the interface, hold the implementation**: `List<T> xs = new ArrayList<>()`, not `ArrayList<T> xs = ...`. That way swapping the implementation is a one-line change and method signatures stay general.

## List — ordered, indexed, allows duplicates

| Implementation | Backed by | Random access `get(i)` | Insert/remove at ends | Insert/remove in middle |
|---|---|---|---|---|
| `ArrayList` | resizable array | **O(1)** | O(1) amortized at end | O(n) (shifts elements) |
| `LinkedList` | doubly-linked nodes | O(n) | O(1) | O(1) *if you already hold the node* |

**Default to `ArrayList`.** `LinkedList`'s theoretical O(1) middle-insert requires already having a reference to the node; reaching it is O(n), and its per-node pointer overhead and cache-unfriendly layout make it slower than `ArrayList` in most real workloads. Reach for `LinkedList` essentially only when you need `Deque`/queue semantics — and even then `ArrayDeque` is usually better (below).

`ArrayList` grows by reallocating a larger backing array (typically ~1.5×) and copying — which is why `new ArrayList<>(expectedSize)` matters for large loads: it avoids repeated reallocation, the same reason the bulk-dedup `HashSet<>(8_000_000)` in [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation]] is pre-sized.

The everyday `ArrayList` method surface — a resizable array that (unlike a plain `int[]`) grows on demand and only holds objects (boxed primitives):

```java
List<String> foods = new ArrayList<>();
foods.add("apple");                 // append
foods.add(0, "banana");             // insert at index (shifts the rest)
foods.get(0);                       // "banana" — read by index
foods.set(0, "orange");             // overwrite in place
foods.size();                       // 2 — a method, unlike array.length
foods.contains("apple");            // true — and indexOf("apple") → 1, or -1 if absent
foods.remove("apple");              // remove by value; remove(0) removes by index
for (String f : foods) { ... }      // for-each walk
```

## Set — no duplicates

| Implementation | Ordering | `add`/`contains`/`remove` |
|---|---|---|
| `HashSet` | none (hash order) | O(1) average |
| `LinkedHashSet` | insertion order | O(1) average |
| `TreeSet` | sorted (natural or `Comparator`) | O(log n) |

`Set` membership is why the cross-consumer ID dedup uses `ConcurrentHashMap.newKeySet()` — an O(1) "have I seen this ID?" check. Correct `Set` behavior depends entirely on `equals`/`hashCode` ([[languages/01-java/01-language/02-oop|OOP]]): a broken `hashCode` lets duplicates slip in because they land in different buckets.

## Map — key → value

| Implementation | Ordering | Lookup | Notes |
|---|---|---|---|
| `HashMap` | none | O(1) average | The default; one null key allowed |
| `LinkedHashMap` | insertion (or access) order | O(1) average | Deterministic iteration — why the API response builder uses it ([[languages/01-java/03-tooling/03-lombok-and-builders|Lombok & Builders]]) |
| `TreeMap` | sorted keys | O(log n) | Range queries (`headMap`, `subMap`, `firstKey`) |
| `ConcurrentHashMap` | none | O(1) average | Thread-safe without locking the whole map ([[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]]) |

The everyday `HashMap` method surface — a set of unique **keys**, each mapped to a **value**. Both type parameters must be reference types (`Integer`, not `int`); `put` on an existing key **overwrites** it:

```java
Map<String, Double> prices = new HashMap<>();
prices.put("apple", 0.50);          // add / overwrite
prices.put("banana", 0.25);
prices.get("apple");                // 0.50 — or null if the key is absent
prices.getOrDefault("pear", 0.0);   // 0.0 — null-safe read with a fallback
prices.containsKey("apple");        // true — and containsValue(0.25)
prices.remove("apple");             // delete by key
prices.size();                      // number of entries
for (String key : prices.keySet())          // iterate keys...
    System.out.println(key + ": $" + prices.get(key));
for (var entry : prices.entrySet())          // ...or key+value together (avoids a second lookup)
    System.out.println(entry.getKey() + " -> " + entry.getValue());
```

`HashMap` internals worth knowing: keys are bucketed by `hashCode()`, and within a bucket compared by `equals()`. Collisions chain in a linked list that **converts to a balanced tree once a bucket exceeds 8 entries** (Java 8+), bounding worst-case lookup at O(log n) instead of O(n) under adversarial hashing. `computeIfAbsent(key, k -> ...)` atomically gets-or-creates — the idiom behind one-to-many secondary indexes (`Map<String, Set<String>>`).

A worked example — a **slot machine** payout table keyed by symbol, showing a `Map` as a lookup table plus `getOrDefault` for the "no win" case:

```java
String[] reel = {"🍒", "🍉", "🔔", "⭐", "7️⃣"};
Map<String, Integer> payouts = Map.of("🍒", 10, "🍉", 20, "🔔", 30, "⭐", 40, "7️⃣", 50);

Random random = new Random();
String[] spin = new String[3];
for (int i = 0; i < 3; i++) spin[i] = reel[random.nextInt(reel.length)];
System.out.println(String.join(" | ", spin));

int payout = spin[0].equals(spin[1]) && spin[1].equals(spin[2])   // all three match
        ? payouts.getOrDefault(spin[0], 0)
        : 0;
System.out.println(payout > 0 ? "You win " + payout : "You lose");
```

## Queue and Deque — ends, not indices

- **`Queue<E>`** — FIFO; `offer`/`poll`/`peek`.
- **`Deque<E>`** — double-ended; push/pop/peek at *both* ends. Serves as both a stack and a queue.
- **`PriorityQueue<E>`** — not FIFO; `poll` returns the smallest element by natural order or a `Comparator`, backed by a binary heap (O(log n) insert/poll). This is the structure behind Dijkstra and top-K ([[foundations/dsa/README|DSA]]).

**Use `ArrayDeque`, not `Stack` or `LinkedList`.** The legacy `Stack` class is synchronized and effectively deprecated; `ArrayDeque` is the modern choice for both stack (`push`/`pop`) and queue (`offer`/`poll`) semantics, with better locality than `LinkedList`. (`BlockingQueue`, the concurrent producer/consumer variant, is in [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] — and re-implementing one by hand is one of the [[languages/01-java/02-jvm-and-concurrency/exercises/README|exercises]].)

## Iterator

Every `Collection` is iterable; the enhanced for-loop is `Iterator` sugar. The one rule that bites: **you cannot structurally modify a collection while iterating it** with a for-each, or you get `ConcurrentModificationException`. Remove through the iterator itself, or collect-then-remove:

```java
Iterator<Transaction> it = list.iterator();
while (it.hasNext()) {
    if (it.next().isExpired()) it.remove();   // safe — via the iterator
}
// list.removeIf(Transaction::isExpired);      // cleaner, same effect
```

## Comparable vs Comparator

- **`Comparable<T>`** — a type's *natural* order, via `int compareTo(T other)` on the class itself. Returns negative/zero/positive for less/equal/greater.
- **`Comparator<T>`** — an *external*, swappable ordering, ideal for sorting the same type multiple ways:

```java
list.sort(Comparator.comparing(Transaction::getAmount).reversed()
                     .thenComparing(Transaction::getId));
```

`Collections.sort` / `List.sort` use these; `TreeMap`/`TreeSet`/`PriorityQueue` take a `Comparator` to define their ordering.

## Choosing — the one-line heuristic

- Ordered, indexed, duplicates OK → **`ArrayList`**
- Uniqueness / membership test → **`HashSet`** (insertion order → `LinkedHashSet`; sorted → `TreeSet`)
- Key→value → **`HashMap`** (deterministic iteration → `LinkedHashMap`; sorted/range → `TreeMap`; concurrent → `ConcurrentHashMap`)
- Stack or queue → **`ArrayDeque`**
- "Smallest/largest next" → **`PriorityQueue`**

Getting this choice right is often a bigger performance win than any micro-optimization — an O(n) `list.contains()` in a hot loop that should have been an O(1) `set.contains()` is a classic, and exactly the secondary-index insight in [[languages/01-java/04-persistence/01-jdbc-and-data-modeling|JDBC & Data Modeling]].

## Related
- [[languages/01-java/01-language/03-generics|Generics]] — every collection is generic
- [[languages/01-java/01-language/05-functional-programming|Functional Programming]] — streams operate over collections
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] — the thread-safe collection variants
- [[foundations/dsa/README|DSA]] — the data structures and their Big-O, language-agnostic
