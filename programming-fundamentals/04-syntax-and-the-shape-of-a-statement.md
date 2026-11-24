---
id: ff0a39c7-736e-4a62-ae56-4acdbde99465
---

# Syntax and the Shape of a Statement

**Syntax is a language's grammar** — the rules about what arrangements of characters are valid. Break them and the program doesn't run; you get a **syntax error** and a line number.

Beginners experience this as pointless strictness. It isn't. **An unambiguous grammar is the precondition for mechanical translation.** English tolerates ambiguity because a human listener resolves it from context; there's no listener here, so the grammar has to make every valid program mean exactly one thing.

The classic demonstration:

> Let's eat, Grandma.
> Let's eat Grandma.

One comma, two very different meals. English recovers because you know something about the speaker. A parser knows nothing.

## The same idea, three punctuations
<!-- bite: feda2752-06fa-4828-845c-556ec763e41d -->

Watch one statement — *store the number 3 under the name `count`* — across three languages:

```java
int count = 3;        // Java: declare the type, end with a semicolon
```
```python
count = 3             # Python: no type, no semicolon
```
```javascript
let count = 3;        // JavaScript: declare it's a variable, type inferred
```

**Identical meaning. Three sets of rules.** What varies is which decisions the language makes you state explicitly:

- Must you declare the **type**? Java yes, the others no → [[programming-fundamentals/02-languages-and-the-translation-problem|note 02]]
- Must you mark that it's a **new** variable? JavaScript yes (`let`), Python no
- How does a statement **end**? Semicolon, or newline

None of these is better. They're different answers to "how much should the programmer say out loud?"

## Blocks: how a language knows where something ends
<!-- bite: 6239a2cc-1313-40d3-83f2-6a0a95691f90 -->

Every language needs to group statements — *these three lines all belong to the `if`*. Two conventions:

**Braces** — C, Java, JavaScript, C#, Go, Rust:
```javascript
if (score > 10) {
    console.log("well done");
    awardBadge();
}
```

**Indentation** — Python, and it's meaningful rather than cosmetic:
```python
if score > 10:
    print("well done")
    award_badge()
```

In brace languages, indentation is *convention* — the compiler ignores it, humans depend on it, and misleading indentation is a real source of bugs. In Python, indentation **is** the syntax, which is why a stray space can change behaviour and why mixing tabs and spaces causes trouble.

**Whichever you're in, indent consistently.** Use a formatter and stop thinking about it: `black` (Python), `prettier` (JS/TS), `gofmt` (Go), `rustfmt`. This is settled; nobody serious argues about layout any more, they run a tool.

## The shapes that recur everywhere
<!-- bite: 4e9236c8-b048-4427-a6b3-06cacfa91397 -->

Once you've seen these, an unfamiliar language stops looking foreign.

**Assignment** — put a value in a name.
```text
name = "Kingsley"
```
Note `=` means *assign*, not *equals*. Comparison is `==`, and confusing them is one of the two most common beginner errors → [[programming-fundamentals/06-control-flow|note 06]].

**Function call** — a name, then parentheses containing arguments.
```text
print("hello")
max(3, 7)
save()                # parentheses stay, even when empty
```
**The parentheses are what makes it a call.** Writing `max` without them refers to the function itself rather than running it — a distinction that becomes important later and confusing early.

**Member access** — a dot. *The thing on the left, the part of it named on the right.*
```text
name.length
user.email
list.append(4)
```

**Indexing** — square brackets, to get one item out of a collection.
```text
items[0]
scores["maths"]
```

**Comment** — text for humans, ignored entirely by the machine.
```python
# Python, Bash, Ruby
```
```javascript
// most C-family languages
/* ...or a block, across lines */
```

**Operators** — `+ - * /` as expected, plus:
- `%` **modulo** — the remainder. `10 % 3` is `1`. Its most common use is the even/odd test (`n % 2 == 0`) and wrapping a counter round
- `==` equal, `!=` not equal, `<` `>` `<=` `>=`
- `&&`/`and`, `||`/`or`, `!`/`not`

**One trap worth naming now:** `+` means addition for numbers and *joining* for text (**concatenation**). So `"3" + "4"` is `"34"`, not `7`. In some languages `3 + "4"` is an error; in others it quietly produces `"34"`. Neither is what you meant. → [[programming-fundamentals/05-variables-and-types|note 05]].

## Reading an error message
<!-- bite: a03d9140-58b0-4d00-9215-72cd9a2d7f15 -->

Beginners skim errors and start changing things. **The message usually tells you exactly what's wrong**, and reading it properly is the highest-return habit in this note.

```text
  File "app.py", line 12
    if score > 10
                 ^
SyntaxError: expected ':'
```

Four pieces of information: the **file**, the **line**, a **caret at the position**, and the **problem**. That's the fix, stated.

**Two things that trip people up:**

**The reported line can be one after the real mistake.** An unclosed bracket on line 11 is only detected on line 12, when the parser meets something that can't follow. If line 12 looks fine, look up.

**A syntax error means nothing ran.** Not "it ran and failed" — the program was never valid, so no output means no output, not a broken computer.

## Style, and why it isn't taste
<!-- bite: 8e24f237-231d-4356-8fc4-6ed8bba85df5 -->

Syntax is what the machine requires. **Style is what the next reader requires**, and the next reader is usually you in three months.

- **Naming** — `camelCase` (Java, JS), `snake_case` (Python, Rust), `PascalCase` for types nearly everywhere. Follow the language's convention rather than your preference; consistency is the entire point → [[programming-fundamentals/05-variables-and-types|note 05]]
- **Consistent indentation** — via a formatter
- **Comments explaining *why*, not *what*.** `# add 1 to i` is noise. `# skip the header row` is information. If a comment is needed to explain *what*, the code usually wants renaming instead

**Code is read many more times than it is written.** That single economic fact is the root of nearly everything in [[concepts/01-best-practices/01-clean-code/index|clean code]].

## Check your understanding
<!-- bite: 67b8454d-dff5-4797-8708-ec1a222745eb -->

Try each one before you open the answer.

1. <!-- q: exact id="5802bec4" answer="2" -->
   What is `17 % 5`?

   <details><summary>Answer</summary>

   2. `%` is modulo, the remainder: 17 is 3 fives (15) with 2 left over.

   </details>

2. <!-- q: exact id="58361296" answer="12" accept="'12'" -->
   In Python, what does `"1" + "2"` give?

   <details><summary>Answer</summary>

   `"12"`. With text on both sides, `+` joins the strings (concatenation). It does not add the numbers.

   </details>

3. <!-- q: mcq id="b51539dc" -->
   This Python error appears:

   ```text
     File "shop.py", line 20
       total = sum(prices
                         ^
   SyntaxError: '(' was never closed
   ```

   What do you know for certain?

   - [ ] Lines 1 to 19 ran, then the program crashed on line 20
   - [x] Nothing ran at all, because the program was never valid
   - [ ] The `sum` function has a bug
   - [ ] The error is definitely somewhere after line 20

   <details><summary>Answer</summary>

   Nothing ran. A syntax error means the file couldn't be parsed, so no line was executed. Fix the bracket on line 20 and run it again.

   </details>

4. <!-- q: mcq id="ca16d1df" -->
   In Python, indentation decides which lines belong to an `if`. In JavaScript, braces `{ }` do. What does indentation do in JavaScript?

   - [ ] The same as in Python: it is part of the syntax
   - [x] Nothing for the compiler; it is a convention for humans, so misleading indentation can hide a bug
   - [ ] It makes the code run faster
   - [ ] It is an error to indent JavaScript

   <details><summary>Answer</summary>

   The JavaScript compiler ignores indentation; only the braces count. People still rely on it to read the code, so code indented one way but braced another misleads the reader. Run a formatter such as `prettier` and the problem goes away.

   </details>

5. <!-- q: gap id="51d574f8" answers="syntax;style" -->
   ___ is what the machine requires, so breaking it stops the program running. ___ is what the next reader requires, such as good names and consistent layout.

   <details><summary>Answer</summary>

   Syntax, then style. Code is read many more times than it is written, which is why style matters even though the machine ignores it.

   </details>

6. <!-- q: open id="040deed8" -->
   Which of these two comments is worth keeping, and why?

   ```python
   i = i + 1   # add 1 to i
   rows = rows[1:]   # skip the header row
   ```

   <details><summary>Answer</summary>

   The second. It explains why the line is there, which the code alone doesn't tell you. The first repeats what the code already says, so it is noise. If a comment is needed to explain what the code does, a better name is usually the fix.

   </details>

## Related
<!-- bite: 128a1421-87b0-464c-a92a-4da58ac4672e -->
- [[programming-fundamentals/05-variables-and-types|variables and types]] — the first real building block
- [[programming-fundamentals/10-errors-and-debugging|errors and debugging]] — the other two kinds of error
- [[compilers/02-lexical-analysis|lexing and parsing]] — what's actually reading your syntax
- [[concepts/01-best-practices/01-clean-code/index|clean code]] — style, taken seriously

## About this lesson
<!-- bite: 9cee7969-a7e1-415f-9b2a-4b5e61767dd2 -->

**Level:** Beginner. **Covers:** The rules that feel arbitrary, why they exist, and the small set of shapes that recur in every language you'll ever meet.

*Source: [reference] — from the freeCodeCamp Introduction to Programming course.*
