# Control Flow

> **[Beginner]** · Conditionals and loops — the two mechanisms that turn a list of steps into something that can respond and repeat.

Without control flow, a program runs top to bottom, once, doing the same thing regardless of input. Useless for almost everything. **Control flow is how a program branches on what's true and repeats without you writing the steps out.**

Two ideas. That's the whole chapter, and between them they cover everything.

## Conditionals

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

**In C-family languages a missing `break` "falls through" to the next case** — occasionally what you want, usually a bug, and the reason the construct has a bad reputation. Newer designs (Python's `match`, Rust's `match`, modern `switch` expressions) removed the trap and added **pattern matching**, which can destructure values rather than just compare them. If your language has that form, prefer it. → [[foundations/programming-language-theory/README|PL theory]].

`default` / `_` is the `else` of a switch, and the same argument applies: always include it.

## Loops

The second mechanism. Four shapes, and the distinction between them is *what decides when to stop*.

### `for` — a known number of times

```javascript
for (let i = 0; i < 5; i++) {
    console.log(i);        // 0 1 2 3 4
}
```

Three parts: **start** (`i = 0`), **condition to continue** (`i < 5`), **step** (`i++`). It runs 5 times, and `i` ends at 4 — because the check happens *before* each pass, and `5 < 5` is false.

**Starting at 0 and using `<` is deliberate**, not a stylistic quirk: it makes `i` line up with collection indices, which start at 0 → [[foundations/programming-fundamentals/07-collections|note 07]].

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

Loops inside loops, for anything grid-shaped:

```python
for row in grid:
    for cell in row:
        print(cell)
```

**Nesting multiplies the work.** An outer loop of 1,000 with an inner loop of 1,000 is a million iterations. Add a third level and it's a billion — the point where "it works on my test data" and "it works on real data" diverge sharply.

This is where [[foundations/dsa/README|DSA]] starts: not as an interview ritual, but as the answer to *how much work does this actually do as the input grows?* You don't need it yet. **You do need the instinct that nested loops over large inputs deserve a second look.**

## Related
- [[foundations/programming-fundamentals/07-collections|collections]] — what you'll mostly be looping over
- [[foundations/programming-fundamentals/08-functions|functions]] — packaging this up
- [[foundations/programming-fundamentals/09-recursion-and-the-call-stack|recursion]] — the other way to repeat
- [[foundations/dsa/README|DSA]] — when "how many times does this run?" starts to matter
- [[foundations/computer-architecture/07-branch-prediction-and-speculation|branch prediction]] — what an `if` costs the hardware

*Source: [reference] — from the freeCodeCamp Introduction to Programming course.*
