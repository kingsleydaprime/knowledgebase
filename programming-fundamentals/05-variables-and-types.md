---
id: 2d30340a-f84d-4f71-9cad-aa333fb3ba15
---

# Variables and Types

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
<!-- bite: 10ae0d2a-7d01-40c1-9860-50472fcf6ff0 -->

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

**Integers have limits.** A 32-bit signed integer stops at 2,147,483,647. Exceed it and it either errors or silently *wraps* to a large negative number. Python grows integers automatically; most languages don't. → [[computer-architecture/02-data-representation|data representation]].

**Floats are approximations.** `0.1 + 0.2` does not equal `0.3` — it's `0.30000000000000004`. This isn't a bug in your language; it's a consequence of representing decimals in binary, and it's the same in every language. **Never compare floats with `==`, and never use them for money** — use integer minor units (pence, cents) or a decimal type. → [[mathematics/07-applied-and-computational/01-numerical-methods/02-floating-point-and-error|floating point]].

**A character is not a one-character string.** `'A'` and `"A"` are different types in languages that distinguish them. Python doesn't; Java and C do.

**Null is its own concept and its own problem.** It means *nothing is here*, and using it as though something were is the classic `NullPointerException` / `undefined is not a function`. Its inventor called it his "billion-dollar mistake". Modern languages fight it with `Option`/`Maybe` types and nullability checks → [[languages/03-rust/index|Rust]].

## Declaring, and where the value lives
<!-- bite: 263ce822-a130-4041-95c6-3b98db0999f8 -->

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

Underneath, the variable is a **name bound to a location in memory**. The name is for you; the machine works in addresses. That's the whole of the model you need for now — [[os/04-virtual-memory|virtual memory]] and [[computer-architecture/08-the-memory-hierarchy|the memory hierarchy]] are there when you want the real thing.

## Where the box metaphor breaks
<!-- bite: f2222cd3-5eb8-4d71-82f5-ebc0d2fd4424 -->

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

**The rule to carry:** *simple values are copied; everything else is shared unless you say otherwise.* (Why languages do this, and the mutable/immutable axis that decides when you can even notice, is [[programming-fundamentals/15-how-types-actually-work|note 15]].) This is the root of a large fraction of "why did that change?" bugs, and it's why immutability is treated as a virtue in [[concepts/01-best-practices/index|best practices]].

## Conversion, explicit and otherwise
<!-- bite: 6e0b4046-365d-443c-87a8-141c1378b62d -->

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
<!-- bite: 4d611bb0-6164-418e-8a37-1c2a1cae5c69 -->

A variable exists within a region. Outside it, the name is unknown:

```python
def calculate():
    result = 42      # local to this function
    return result

print(result)        # NameError — never existed out here
```

- **Local** — inside a function or block. Created on entry, gone on exit
- **Global** — visible everywhere in the file or program

**Prefer local.** A global can be changed from anywhere, which means when it holds the wrong value, the suspect list is the entire program. Scope is a tool for shrinking that list, and functions get their power partly from it → [[programming-fundamentals/08-functions|note 08]].

## Naming, properly
<!-- bite: 2efc0609-03e1-4611-8a75-22d4df003a6e -->

The convention doesn't matter; consistency and honesty do. **Follow whatever your language uses** — `snake_case` in Python and Rust, `camelCase` in Java and JavaScript, `PascalCase` for types.

What actually matters:

- **Say what it holds.** `userEmail`, not `x`, not `data`, not `temp`
- **Length should track scope.** `i` is fine as a three-line loop counter. A variable used across eighty lines needs a real name
- **Don't encode the type.** `strName` was a workaround for editors that no longer exist
- **Booleans read as questions** — `isValid`, `hasPermission`, `canEdit`
- **Say no to the unit-free number.** `timeout` is ambiguous; `timeoutSeconds` isn't. **A real spacecraft was lost to a units mismatch** — the habit is cheap

**Naming is genuinely hard and genuinely worth the time.** A well-named variable removes the need for a comment, and it removes the need to reread the code that produced it.

## Check your understanding
<!-- bite: 1dbd87f2-50b2-4b6f-ba93-7470d9958a81 -->

Try each one before you open the answer.

1. <!-- q: exact id="d499dff9" answer="[10, 20, 30]" accept="[10,20,30]" -->
   What does this Python print?

   ```python
   a = [10, 20]
   b = a
   b.append(30)
   print(a)
   ```

   <details><summary>Answer</summary>

   `[10, 20, 30]`. `b = a` doesn't copy the list. It puts a second name on the same list, so appending through `b` changes what `a` sees. Use `b = a.copy()` when you want a separate list.

   </details>

2. <!-- q: exact id="6ead7785" answer="7" -->
   What does this Python print?

   ```python
   x = 7
   y = x
   y = 99
   print(x)
   ```

   <details><summary>Answer</summary>

   7. Simple values like numbers are copied, and `y = 99` points `y` at a new value without touching `x`.

   </details>

3. <!-- q: mcq id="dceee9ba" -->
   A shop stores prices as floats and checks `if 0.1 + 0.2 == 0.3:`. The check is false. What is the right fix for money?

   - [ ] Use a bigger float type
   - [x] Store whole numbers of the smallest unit, such as kobo or cents, or use a decimal type
   - [ ] Round every price to one decimal place before adding
   - [ ] Switch to a language without this bug

   <details><summary>Answer</summary>

   Use integer minor units (₦12.50 becomes 1250 kobo) or a decimal type. `0.1 + 0.2` is `0.30000000000000004` because decimals can't be stored exactly in binary, and that is true in every language.

   </details>

4. <!-- q: exact id="6ca36d7f" answer="53" accept="'53'" -->
   In JavaScript, what does `"5" + 3` give?

   <details><summary>Answer</summary>

   `"53"`. When either side of `+` is a string, JavaScript joins them. (`"5" - 3` gives `2`, because `-` has no string meaning, so it converts.) Convert input to the type you want as soon as it arrives.

   </details>

5. <!-- q: mcq id="901eddf5" -->
   Which variable names follow the lesson's advice? Choose all that apply.

   - [x] `isLoggedIn`
   - [x] `timeoutSeconds`
   - [ ] `strName`
   - [ ] `data2`

   <details><summary>Answer</summary>

   `isLoggedIn` reads as a question, which suits a boolean. `timeoutSeconds` carries its unit. `strName` encodes the type, an old habit with no purpose now, and `data2` says nothing about what it holds.

   </details>

6. <!-- q: open id="1b16a6fc" -->
   Why is a local variable easier to debug than a global one when it ends up holding the wrong value?

   <details><summary>Answer</summary>

   A local variable can only be changed inside its function or block, so that small region is the only place to look. A global can be changed from anywhere, so every line in the program is a suspect. Scope keeps the suspect list short.

   </details>

## Related
<!-- bite: d57f8eed-8575-447d-b3e2-3aaae71275f0 -->
- [[programming-fundamentals/15-how-types-actually-work|how types actually work]] — **the deeper version of this note**: the bit-level story, and value/reference, mutable/immutable, static/dynamic and strong/weak as four separate questions
- [[programming-fundamentals/06-control-flow|control flow]] — making decisions with these values
- [[programming-fundamentals/07-collections|collections]] — many values under one name
- [[mathematics/07-applied-and-computational/01-numerical-methods/02-floating-point-and-error|floating point]] — why `0.1 + 0.2` isn't `0.3`
- [[computer-architecture/02-data-representation|data representation]] — how these are actually stored
- [[concepts/01-best-practices/01-clean-code/index|clean code]] — naming, at length

## About this lesson
<!-- bite: ec3f943c-4443-484e-9914-3a5a3ff5a9ef -->

**Level:** Beginner. **Covers:** Named storage, the types that go in it, and the reference-vs-value distinction that causes more confusion than anything else in this course.

*Source: [reference] — from the freeCodeCamp Introduction to Programming course, extended with the reference-vs-value and float-precision material it left out.*
