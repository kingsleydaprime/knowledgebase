---
id: 56cd3181-fd4e-46df-9322-ebf5c923d77a
---

# Control Flow

Without control flow, a program runs top to bottom, once, doing the same thing regardless of input. Useless for almost everything. **Control flow is how a program branches on what's true and repeats without you writing the steps out.**

Two ideas. That's the whole chapter, and between them they cover everything.

## Conditionals
<!-- bite: 2686d67a-e643-4a10-a07d-56974125735a -->

`if` runs a block only when a condition is true.

```python
if score > 10:
    print("well done")
```

The condition evaluates to a **boolean** — `true` or `false`. True, the block runs; false, it's skipped entirely.

`else` gives the alternative:
```python
if age >= 18:
    print("welcome")
else:
    print("come back later")
```

`elif` / `else if` chains more cases:
```python
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"
```

**The crucial property: evaluation stops at the first match.** With `score = 95`, the first branch matches, `grade` becomes `"A"`, and nothing else is even tested. This is why order matters — reverse the chain and everything above 70 gets a `"C"`.

**Always have a final `else`.** It catches the case you didn't think of. Without one, an unanticipated input falls through silently, leaving a variable unset — and the failure appears somewhere else entirely, which makes it hard to trace.

## Conditions themselves
<!-- bite: 2693d35b-22c5-4300-8ec8-eabd2ae39a5b -->

**Comparison:** `==` equal, `!=` not equal, `<` `>` `<=` `>=`

**`=` is assignment, `==` is comparison.** This is the most common beginner error in every C-family language. `if (x = 5)` assigns 5 to `x` and is usually *true*, so the branch always runs. Some languages now reject it; many don't.

**Combining:** `and` / `&&`, `or` / `||`, `not` / `!`

```python
if age >= 18 and has_id:
    allow_entry()
```

**Short-circuiting** is worth knowing deliberately: with `and`, if the left side is false the right side is **never evaluated**. With `or`, if the left is true the right is skipped. This is both a performance detail and a safety technique:

```python
if user is not None and user.is_admin:    # safe
```
Reverse those and you crash whenever `user` is `None`, because you check `.is_admin` on nothing.

**Truthiness:** many languages treat non-boolean values as true or false in a condition — `0`, `""`, empty lists and `null` are usually "falsy", most other things "truthy". Convenient, and a source of subtle bugs, because `if items:` and `if items is not None:` differ exactly when `items` is an empty list.

## Switch / match
<!-- bite: ac91091d-2633-45cf-b6d6-ef48e6e01225 -->

When you're comparing one value against many fixed possibilities, a long `elif` chain gets noisy. Most languages offer a dedicated form:

```javascript
switch (day) {
    case "SAT":
    case "SUN":
        rate = weekendRate;
        break;              // ← without this, execution falls into the next case
    case "MON":
        rate = mondayRate;
        break;
    default:
        rate = standardRate;
}
```

**In C-family languages a missing `break` "falls through" to the next case** — occasionally what you want, usually a bug, and the reason the construct has a bad reputation. Newer designs (Python's `match`, Rust's `match`, modern `switch` expressions) removed the trap and added **pattern matching**, which can destructure values rather than just compare them. If your language has that form, prefer it. → [[programming-language-theory/index|PL theory]].

`default` / `_` is the `else` of a switch, and the same argument applies: always include it.

## Loops
<!-- bite: c73cf05a-60f6-480d-b61c-93021da5927a -->

The second mechanism. Four shapes, and the distinction between them is *what decides when to stop*.

### `for` — a known number of times

```javascript
for (let i = 0; i < 5; i++) {
    console.log(i);        // 0 1 2 3 4
}
```

Three parts: **start** (`i = 0`), **condition to continue** (`i < 5`), **step** (`i++`). It runs 5 times, and `i` ends at 4 — because the check happens *before* each pass, and `5 < 5` is false.

**Starting at 0 and using `<` is deliberate**, not a stylistic quirk: it makes `i` line up with collection indices, which start at 0 → [[programming-fundamentals/07-collections|note 07]].

### `for-each` — once per item

```python
for item in shopping_list:
    print(item)
```

**Prefer this whenever you don't need the index.** You cannot go off the end of the collection, you cannot get the bounds wrong, and it states the intent — *do this to every item* — rather than the mechanics.

### `while` — until a condition changes

```python
while not correct_guess:
    guess = get_input()
    correct_guess = check(guess)
```

Use `while` when the number of iterations isn't known up front: reading until end-of-file, retrying until success, running until the user quits.

**Something inside the loop must be able to make the condition false**, or it never ends.

### `do-while` — at least once, then check

```javascript
do {
    input = prompt("enter a number");
} while (isNaN(input));
```

The body runs before the first check. Natural for "ask, then validate, then maybe ask again".

## Infinite loops
<!-- bite: fcf33eb4-0ea9-48b9-993a-ae7b11b05fcd -->

A loop whose condition never becomes false.

```python
i = 0
while i < 10:
    print(i)          # i never changes — this runs forever
```

The program hangs, consumes CPU, and produces nothing. **Ctrl+C in a terminal is how you stop it.**

**Sometimes it's intentional and correct.** `while True:` is the normal shape of a server accepting connections, a game loop rendering frames, or an event loop — anything meant to run until something external stops it. The bug isn't looping forever; it's looping forever *by accident*.

**The two habitual causes:** forgetting to update the variable the condition tests, and updating it in the wrong direction. When something hangs, check those two first.

## `break` and `continue`
<!-- bite: e0e6be19-8929-4a84-b3c8-b4784d79551e -->

```python
for item in items:
    if item is None:
        continue          # skip this one, carry on
    if item == target:
        found = item
        break             # stop the loop entirely
```

`break` exits; `continue` skips to the next iteration. Both are useful and both are easy to overuse — several `break`s scattered through a long loop make it hard to know what's true at the end. Two or three exit points in a short loop is fine; a dozen means the loop wants splitting into a function.

## Nesting, and the cost of it
<!-- bite: 5b5a521a-90e1-4d6a-ab73-436c4b6a8cce -->

Loops inside loops, for anything grid-shaped:

```python
for row in grid:
    for cell in row:
        print(cell)
```

**Nesting multiplies the work.** An outer loop of 1,000 with an inner loop of 1,000 is a million iterations. Add a third level and it's a billion — the point where "it works on my test data" and "it works on real data" diverge sharply.

This is where [[dsa/index|DSA]] starts: not as an interview ritual, but as the answer to *how much work does this actually do as the input grows?* You don't need it yet. **You do need the instinct that nested loops over large inputs deserve a second look.**

## Check your understanding
<!-- bite: f85694b5-6d31-4a4d-a1eb-66d52b128c28 -->

Try each one before you open the answer.

1. <!-- q: exact id="48af20a6" answer="B" -->
   What is `grade` after this runs with `score = 85`?

   ```python
   if score >= 90:
       grade = "A"
   elif score >= 80:
       grade = "B"
   elif score >= 70:
       grade = "C"
   else:
       grade = "F"
   ```

   <details><summary>Answer</summary>

   B. 85 fails the first test, passes `score >= 80`, and the chain stops there. The later branches are never tested.

   </details>

2. <!-- q: exact id="909a3995" answer="C" -->
   The same grades, written in the wrong order. What is `grade` with `score = 95`?

   ```python
   if score >= 70:
       grade = "C"
   elif score >= 80:
       grade = "B"
   elif score >= 90:
       grade = "A"
   ```

   <details><summary>Answer</summary>

   C. 95 passes the first test, `score >= 70`, and evaluation stops at the first match. Every score of 70 or more gets a C, which is why the order of an `elif` chain matters.

   </details>

3. <!-- q: exact id="4d4e5b69" answer="4" -->
   How many times does this loop print?

   ```javascript
   for (let i = 2; i < 6; i++) {
       console.log(i);
   }
   ```

   <details><summary>Answer</summary>

   4 times: it prints 2, 3, 4 and 5. When `i` reaches 6, `6 < 6` is false and the loop stops before the body runs.

   </details>

4. <!-- q: mcq id="4a95b5c1" -->
   `user` might be `None`. Which condition is safe?

   - [x] `if user is not None and user.is_admin:`
   - [ ] `if user.is_admin and user is not None:`
   - [ ] Both are equally safe
   - [ ] Neither, because `and` checks both sides

   <details><summary>Answer</summary>

   The first. `and` short-circuits: if the left side is false, the right side is never evaluated, so `.is_admin` is never read on `None`. In the second, `.is_admin` is read first and crashes when `user` is `None`.

   </details>

5. <!-- q: exact id="ed8552b8" answer="8000000" accept="8,000,000|8 million" -->
   An outer loop runs 200 times, the loop inside it 200 times, and a third loop inside that 200 times. How many times does the innermost body run?

   <details><summary>Answer</summary>

   200 × 200 × 200 = 8,000,000. Nesting multiplies the work, which is why nested loops over big inputs deserve a second look.

   </details>

6. <!-- q: open id="d2968244" -->
   This loop hangs. Name the bug and fix it.

   ```python
   count = 10
   while count > 0:
       print(count)
       count = count + 1
   ```

   <details><summary>Answer</summary>

   The variable moves the wrong way. `count` goes up, so `count > 0` stays true forever. Change the last line to `count = count - 1`. Updating the variable in the wrong direction and forgetting to update it at all are the two usual causes of an accidental infinite loop.

   </details>

## Related
<!-- bite: 20eb8570-8c65-4159-8450-0d52604d131f -->
- [[programming-fundamentals/07-collections|collections]] — what you'll mostly be looping over
- [[programming-fundamentals/08-functions|functions]] — packaging this up
- [[programming-fundamentals/09-recursion-and-the-call-stack|recursion]] — the other way to repeat
- [[dsa/index|DSA]] — when "how many times does this run?" starts to matter
- [[computer-architecture/07-branch-prediction-and-speculation|branch prediction]] — what an `if` costs the hardware

## About this lesson
<!-- bite: 47501b7b-c23c-4b2d-b26c-ead1f341521a -->

**Level:** Beginner. **Covers:** Conditionals and loops — the two mechanisms that turn a list of steps into something that can respond and repeat.

*Source: [reference] — from the freeCodeCamp Introduction to Programming course.*
