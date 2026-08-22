# Syntax and the Shape of a Statement

> **[Beginner]** · The rules that feel arbitrary, why they exist, and the small set of shapes that recur in every language you'll ever meet.

**Syntax is a language's grammar** — the rules about what arrangements of characters are valid. Break them and the program doesn't run; you get a **syntax error** and a line number.

Beginners experience this as pointless strictness. It isn't. **An unambiguous grammar is the precondition for mechanical translation.** English tolerates ambiguity because a human listener resolves it from context; there's no listener here, so the grammar has to make every valid program mean exactly one thing.

The classic demonstration:

> Let's eat, Grandma.
> Let's eat Grandma.

One comma, two very different meals. English recovers because you know something about the speaker. A parser knows nothing.

## The same idea, three punctuations

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

- Must you declare the **type**? Java yes, the others no → [[foundations/programming-fundamentals/02-languages-and-the-translation-problem|note 02]]
- Must you mark that it's a **new** variable? JavaScript yes (`let`), Python no
- How does a statement **end**? Semicolon, or newline

None of these is better. They're different answers to "how much should the programmer say out loud?"

## Blocks: how a language knows where something ends

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

Once you've seen these, an unfamiliar language stops looking foreign.

**Assignment** — put a value in a name.
```
name = "Kingsley"
```
Note `=` means *assign*, not *equals*. Comparison is `==`, and confusing them is one of the two most common beginner errors → [[foundations/programming-fundamentals/06-control-flow|note 06]].

**Function call** — a name, then parentheses containing arguments.
```
print("hello")
max(3, 7)
save()                # parentheses stay, even when empty
```
**The parentheses are what makes it a call.** Writing `max` without them refers to the function itself rather than running it — a distinction that becomes important later and confusing early.

**Member access** — a dot. *The thing on the left, the part of it named on the right.*
```
name.length
user.email
list.append(4)
```

**Indexing** — square brackets, to get one item out of a collection.
```
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

**One trap worth naming now:** `+` means addition for numbers and *joining* for text (**concatenation**). So `"3" + "4"` is `"34"`, not `7`. In some languages `3 + "4"` is an error; in others it quietly produces `"34"`. Neither is what you meant. → [[foundations/programming-fundamentals/05-variables-and-types|note 05]].

## Reading an error message

Beginners skim errors and start changing things. **The message usually tells you exactly what's wrong**, and reading it properly is the highest-return habit in this note.

```
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

Syntax is what the machine requires. **Style is what the next reader requires**, and the next reader is usually you in three months.

- **Naming** — `camelCase` (Java, JS), `snake_case` (Python, Rust), `PascalCase` for types nearly everywhere. Follow the language's convention rather than your preference; consistency is the entire point → [[foundations/programming-fundamentals/05-variables-and-types|note 05]]
- **Consistent indentation** — via a formatter
- **Comments explaining *why*, not *what*.** `# add 1 to i` is noise. `# skip the header row` is information. If a comment is needed to explain *what*, the code usually wants renaming instead

**Code is read many more times than it is written.** That single economic fact is the root of nearly everything in [[concepts/04-best-practices/01-clean-code|clean code]].

## Related
- [[foundations/programming-fundamentals/05-variables-and-types|variables and types]] — the first real building block
- [[foundations/programming-fundamentals/10-errors-and-debugging|errors and debugging]] — the other two kinds of error
- [[foundations/compilers/02-lexical-analysis|lexing and parsing]] — what's actually reading your syntax
- [[concepts/04-best-practices/01-clean-code|clean code]] — style, taken seriously

*Source: [reference] — from the freeCodeCamp Introduction to Programming course.*
