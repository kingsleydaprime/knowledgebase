# Variables and Types

> **[Beginner]** · Named storage, the types that go in it, and the reference-vs-value distinction that causes more confusion than anything else in this course.

A **variable** is a name for a piece of storage holding a value you can look at and change.

The usual metaphor is a labelled box: write a label, put something in, look inside later, swap the contents. It's a good starting model and it breaks in one specific way that matters — covered below.

```python
score = 0          # create it, put 0 in
score = 10         # replace the contents
print(score)       # look inside → 10
```

**Why bother?** Three reasons, and the third is the real one:

1. **Remembering** — anything computed but not stored is gone
2. **Naming** — `taxRate` says what `0.075` means. This is documentation you can't forget to update
3. **Handling the unknown** — you cannot write a user's name into your code, because you don't know it. **Variables are the only way a program can work on data that didn't exist when it was written**, which is most of what programs do

## The types you'll meet everywhere

A **type** is what kind of value it is, which determines what operations make sense. Multiplying two numbers is meaningful; multiplying two names is not.

| Type | Holds | Example |
|---|---|---|
| **Integer** (`int`) | Whole numbers, positive or negative | `42`, `-7`, `0` |
| **Float** / **double** | Numbers with decimals | `3.14`, `-0.5` |
| **Boolean** (`bool`) | Exactly `true` or `false` | `true` |
| **String** (`str`) | Text, in quotes | `"hello"`, `"K"` |
| **Character** (`char`) | Exactly one character | `'A'` |
| **Null** / `None` / `nil` | **The absence of a value** | `null` |

Notes that save real time later:

**Integers have limits.** A 32-bit signed integer stops at 2,147,483,647. Exceed it and it either errors or silently *wraps* to a large negative number. Python grows integers automatically; most languages don't. → [[foundations/computer-architecture/02-data-representation|data representation]].

**Floats are approximations.** `0.1 + 0.2` does not equal `0.3` — it's `0.30000000000000004`. This isn't a bug in your language; it's a consequence of representing decimals in binary, and it's the same in every language. **Never compare floats with `==`, and never use them for money** — use integer minor units (pence, cents) or a decimal type. → [[foundations/numerical-methods/02-floating-point-and-error|floating point]].

**A character is not a one-character string.** `'A'` and `"A"` are different types in languages that distinguish them. Python doesn't; Java and C do.

**Null is its own concept and its own problem.** It means *nothing is here*, and using it as though something were is the classic `NullPointerException` / `undefined is not a function`. Its inventor called it his "billion-dollar mistake". Modern languages fight it with `Option`/`Maybe` types and nullability checks → [[languages/03-rust/README|Rust]].

## Declaring, and where the value lives

Different languages ask for different amounts of ceremony:

```java
int score = 0;          // Java: type stated, then name, then value
```
```python
score = 0               # Python: inferred
```
```javascript
let score = 0;          // JavaScript: mutable
const TAX = 0.075;      // JavaScript: cannot be reassigned
```

`const`/`final`/`val` says **this must not be reassigned**. Use it by default and reach for a mutable variable when you need one — a value that can't change is one fewer thing to track when you're reading code later.

Underneath, the variable is a **name bound to a location in memory**. The name is for you; the machine works in addresses. That's the whole of the model you need for now — [[foundations/os/04-virtual-memory|virtual memory]] and [[foundations/computer-architecture/08-the-memory-hierarchy|the memory hierarchy]] are there when you want the real thing.

## Where the box metaphor breaks

This is the part worth reading twice, because it produces bugs that look like the computer misbehaving.

For simple values (numbers, booleans), assignment **copies**:

```python
a = 5
b = a       # b gets its own copy
b = 10
print(a)    # still 5 — unaffected
```

For compound values (lists, objects, dictionaries), assignment usually copies **the reference, not the contents** — both names now point at the *same* thing:

```python
list1 = [1, 2, 3]
list2 = list1        # NOT a copy — a second label on one box
list2.append(4)
print(list1)         # [1, 2, 3, 4]  ← list1 changed too
```

**`list1` was never touched, and it changed.** There is one list with two names.

The fix is an explicit copy when you want one (`list1.copy()`, `[...list1]`, `list(list1)`) — and note that this copies one level. A "shallow" copy of a list of lists still shares the inner lists; a **deep copy** goes all the way down.

**The rule to carry:** *simple values are copied; everything else is shared unless you say otherwise.* (Why languages do this, and the mutable/immutable axis that decides when you can even notice, is [[foundations/programming-fundamentals/15-how-types-actually-work|note 15]].) This is the root of a large fraction of "why did that change?" bugs, and it's why immutability is treated as a virtue in [[concepts/04-best-practices/README|best practices]].

## Conversion, explicit and otherwise

Converting between types is **casting**:

```python
age_text = "25"
age = int(age_text)      # "25" → 25, now arithmetic works
```

Some languages convert implicitly, and JavaScript is the notorious case:

```javascript
"5" + 3      // "53"   ← + concatenates when either side is a string
"5" - 3      // 2      ← - has no string meaning, so it converts
```

Both are documented, consistent behaviour, and both are ways to ship a bug. **Convert deliberately, at the boundary where data enters** — anything from a user, a file, a form, or a network request arrives as text and should become the type you actually want immediately.

## Scope: where a name is visible

A variable exists within a region. Outside it, the name is unknown:

```python
def calculate():
    result = 42      # local to this function
    return result

print(result)        # NameError — never existed out here
```

- **Local** — inside a function or block. Created on entry, gone on exit
- **Global** — visible everywhere in the file or program

**Prefer local.** A global can be changed from anywhere, which means when it holds the wrong value, the suspect list is the entire program. Scope is a tool for shrinking that list, and functions get their power partly from it → [[foundations/programming-fundamentals/08-functions|note 08]].

## Naming, properly

The convention doesn't matter; consistency and honesty do. **Follow whatever your language uses** — `snake_case` in Python and Rust, `camelCase` in Java and JavaScript, `PascalCase` for types.

What actually matters:

- **Say what it holds.** `userEmail`, not `x`, not `data`, not `temp`
- **Length should track scope.** `i` is fine as a three-line loop counter. A variable used across eighty lines needs a real name
- **Don't encode the type.** `strName` was a workaround for editors that no longer exist
- **Booleans read as questions** — `isValid`, `hasPermission`, `canEdit`
- **Say no to the unit-free number.** `timeout` is ambiguous; `timeoutSeconds` isn't. **A real spacecraft was lost to a units mismatch** — the habit is cheap

**Naming is genuinely hard and genuinely worth the time.** A well-named variable removes the need for a comment, and it removes the need to reread the code that produced it.

## Related
- [[foundations/programming-fundamentals/15-how-types-actually-work|how types actually work]] — **the deeper version of this note**: the bit-level story, and value/reference, mutable/immutable, static/dynamic and strong/weak as four separate questions
- [[foundations/programming-fundamentals/06-control-flow|control flow]] — making decisions with these values
- [[foundations/programming-fundamentals/07-collections|collections]] — many values under one name
- [[foundations/numerical-methods/02-floating-point-and-error|floating point]] — why `0.1 + 0.2` isn't `0.3`
- [[foundations/computer-architecture/02-data-representation|data representation]] — how these are actually stored
- [[concepts/04-best-practices/01-clean-code|clean code]] — naming, at length

*Source: [reference] — from the freeCodeCamp Introduction to Programming course, extended with the reference-vs-value and float-precision material it left out.*
