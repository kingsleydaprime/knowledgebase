---
id: 0439640d-6d00-4f73-8bcd-202712ace0ad
---

# Collections

A variable holds one value. Real programs handle many: a shopping list, users, scores, rows from a database. **You cannot solve this with more variables** — `item1`, `item2`, `item3` collapses the moment you don't know how many there are, which is nearly always.

Collections hold many values under one name, and give you ways to add, find, remove and iterate.

## Arrays and indexing
<!-- bite: 56adc745-52d0-46fd-a88e-98e36836b5d7 -->

An **array** is an ordered sequence, accessed by position.

```python
scores = [85, 92, 78, 95, 88]
print(scores[0])     # 85  ← the FIRST element
print(scores[2])     # 78
```

**Indexing starts at 0.** The first element is at index 0, the last at `length - 1`. Every mainstream language does this and it is not arbitrary: an index is an *offset* from the start of the block. The first element is zero elements from the start.

The consequence you'll hit within a day:

```python
scores[5]     # IndexError — valid indices are 0..4
```

An **out-of-bounds** error. In Python or Java you get a clean exception. **In C you get whatever memory happened to be next**, no error, and a bug that appears somewhere unrelated — which is the origin of a large fraction of security vulnerabilities → [[cybersecurity/06-attacks-and-threats/index|attacks]].

**Why arrays are fast:** the elements sit contiguously in memory, so `scores[2]` is one multiplication and one addition — *start + 2 × element size*. Getting any element costs the same regardless of the array's size. That's **O(1)** access, and it's the reason arrays underpin nearly every other data structure.

**The price:** a true fixed-size array is fixed at creation. Adding a sixth element to a five-element array means allocating a new, larger block and copying everything across.

## Dynamic arrays
<!-- bite: 3b0f54f1-e045-48ac-871b-a1941dc54795 -->

Which is exactly what a **dynamic array** does for you, automatically: `list` in Python, `ArrayList` in Java, `vector` in C++, `Array` in JavaScript.

```python
items = []
items.append("apple")      # grows as needed
items.append("bread")
```

Internally it keeps a fixed array with spare capacity. When it fills, it allocates a bigger one (typically double) and copies. Because the size doubles, the copies get rarer as it grows, and **the average cost per append stays constant** even though occasional appends are expensive. (This is *amortised* O(1) — the reasoning is worth meeting properly in [[dsa/index|DSA]].)

**Use a dynamic array by default.** In most languages it's what you get from the literal syntax anyway.

## Dictionaries
<!-- bite: ae3819ba-d8a8-40ea-8588-639a8e755880 -->

An array answers *"what's at position 3?"*. That's rarely the question. Usually it's *"what's the price of bread?"* — and searching the whole list for it is both slow and awkward.

A **dictionary** (map, hash map, object, associative array) stores **key–value pairs**:

```python
prices = {"apple": 1.20, "bread": 2.50, "milk": 0.99}
print(prices["bread"])          # 2.50
prices["eggs"] = 3.10           # add
```

**Lookup by key is O(1) on average** — as fast as an array index, but the key can be meaningful. This is done by **hashing**: the key is run through a function producing a number, which becomes a position in an internal array. No searching happens at all.

The rules that follow from that mechanism:

- **Keys are unique.** Assigning to an existing key replaces the value
- **Keys must be hashable** — usually meaning immutable. Strings and numbers yes; a list, generally no
- **Order is not the point.** Historically dictionaries had no order at all. Python 3.7+ preserves insertion order and JavaScript objects mostly do, but **relying on it is a habit that breaks when you move languages**

**Reach for a dictionary whenever you find yourself looping through a list to find one thing by name.** That instinct is worth more than any specific syntax.

## Sets
<!-- bite: 0b03b2aa-9296-4e2d-8013-80ca1ec2736e -->

A **set** holds unique values, unordered, and answers one question fast: *is this in here?*

```python
seen = set()
seen.add("kingsley")
if "kingsley" in seen:      # O(1)
    print("already processed")
```

Two things sets are ideal for and lists are bad at: **deduplication** (`list(set(items))`) and **membership testing**. `if x in my_list` scans the entire list — O(n). The same check on a set is O(1). On a large collection inside a loop, that difference is the whole performance story.

## Choosing
<!-- bite: 92ac0d09-2335-4878-bf67-4b13a7c177e5 -->

| Need | Use | Why |
|---|---|---|
| Ordered, by position | **Array / list** | O(1) index |
| Look up by name/ID | **Dictionary** | O(1) by key |
| "Have I seen this?" | **Set** | O(1) membership |
| Unique, ordered | Dict keys, or ordered set | |
| Fixed group of related values | **Tuple / struct / object** | Immutable, positional |

**The single most common performance mistake in beginner code is scanning a list where a dictionary or set belongs.** A nested loop over two 10,000-item lists is 100 million comparisons; a dictionary turns it into 10,000 lookups. Same result, four orders of magnitude apart, and it's usually a five-line change.

## Iterating
<!-- bite: 358c5a06-fd00-4c4d-9d21-57e2d1006350 -->

Almost always for-each → [[programming-fundamentals/06-control-flow|note 06]]:

```python
for score in scores:
    print(score)

for name, price in prices.items():      # dictionaries give pairs
    print(f"{name}: {price}")

for i, score in enumerate(scores):      # when you genuinely need the index
    print(f"{i}: {score}")
```

**One rule with teeth: do not modify a collection while iterating over it.** Removing items mid-loop shifts the remaining ones and the iteration skips elements — silently, with no error. Build a new collection instead, or iterate over a copy.

## Nesting
<!-- bite: 2f3758e2-0802-4959-8999-079480bfa94b -->

Collections hold collections, which is how you represent anything with structure:

```python
grid = [[1, 2, 3],
        [4, 5, 6]]
print(grid[1][2])           # 6 — row 1, column 2

users = [
    {"name": "Ada",  "roles": ["admin"]},
    {"name": "Alan", "roles": ["user", "beta"]},
]
```

**That second shape is what JSON is**, and therefore what nearly every API response and config file is. Being comfortable reaching into nested lists-of-dictionaries is a genuinely high-return skill → [[backend/02-api-design/index|API design]].

## What's underneath, and where this goes
<!-- bite: e7f85af6-39a5-413d-8878-12658840b1cf -->

Everything above is built from two physical arrangements: **contiguous memory** (arrays — fast to index, expensive to insert in the middle) and **linked nodes** (each element pointing to the next — cheap to insert, no direct indexing).

From those two, everything else: stacks, queues, linked lists, trees, graphs, heaps. Each trades the cost of one operation against another, and choosing well is most of what makes a program fast.

**That's [[dsa/index|DSA]], and it's the natural next thing after this course.** You don't need it to write useful programs. You need it the first time something works on 100 items and takes four minutes on 100,000.

## Check your understanding
<!-- bite: 9de47197-aa26-44a1-beda-30d647321cad -->

Try each one before you open the answer.

1. <!-- q: exact id="6a489791" answer="40" -->
   What does this print?

   ```python
   temps = [31, 28, 40, 35]
   print(temps[2])
   ```

   <details><summary>Answer</summary>

   40. Indexing starts at 0, so index 2 is the third element: 31 is at 0, 28 at 1, 40 at 2.

   </details>

2. <!-- q: exact id="a8b473a2" answer="6" -->
   A list has 7 elements. What is the index of the last one?

   <details><summary>Answer</summary>

   6. Valid indices run from 0 to length − 1, so 0 to 6. Asking for index 7 is out of bounds.

   </details>

3. <!-- q: mcq id="9b8abf26" -->
   A program has a list of 50,000 banned usernames and checks `if name in banned:` for every sign-up. It is slow. What is the best change?

   - [ ] Sort the list first
   - [x] Store the banned names in a set
   - [ ] Use a for loop with `break` instead of `in`
   - [ ] Split the list into two halves

   <details><summary>Answer</summary>

   A set. `in` on a list scans every item, O(n). On a set it is O(1) on average, because the value is hashed straight to its position. "Have I seen this?" is exactly the question a set answers.

   </details>

4. <!-- q: exact id="184de480" answer="8" -->
   What does this print?

   ```python
   grid = [[1, 2, 3],
           [4, 5, 6],
           [7, 8, 9]]
   print(grid[2][1])
   ```

   <details><summary>Answer</summary>

   8. `grid[2]` is the third row, `[7, 8, 9]`, and index 1 of that row is 8.

   </details>

5. <!-- q: mcq id="1a9f9820" -->
   You need to look up a product's price by its name, for example the price of "rice". Which collection fits?

   - [ ] An array of prices
   - [x] A dictionary from name to price
   - [ ] A set of names
   - [ ] A tuple

   <details><summary>Answer</summary>

   A dictionary. `prices["rice"]` goes straight to the value in O(1) on average. With an array you would have to search through it to find the right item.

   </details>

6. <!-- q: open id="e2240b4e" -->
   Why is it dangerous to remove items from a list while a for loop is going through that same list? What should you do instead?

   <details><summary>Answer</summary>

   Removing an item shifts the remaining ones down a place, so the loop skips the element that moved into the removed one's position. There is no error; elements are just quietly missed. Build a new list of the items you want to keep, or loop over a copy.

   </details>

## Related
<!-- bite: 6aaa8143-9bcd-4da4-aae3-a0550f2548b9 -->
- [[programming-fundamentals/06-control-flow|control flow]] — iterating over these
- [[programming-fundamentals/08-functions|functions]] — passing collections around (and note 05's sharing trap applies)
- [[dsa/index|DSA]] — the depth version of this note
- [[programming-fundamentals/05-variables-and-types|variables and types]] — why `list2 = list1` doesn't copy
- [[databases/02-the-relational-model|the relational model]] — collections that outlive the program

## About this lesson
<!-- bite: ea71e23b-3e4f-4dc8-a6cb-2ed25f10f37c -->

**Level:** Beginner. **Covers:** Arrays, lists, dictionaries and sets — holding many values under one name, and why the choice between them decides how fast your program is.

*Source: [reference] — from the freeCodeCamp Introduction to Programming course, extended with sets, hashing and the complexity comparisons it left for later.*
