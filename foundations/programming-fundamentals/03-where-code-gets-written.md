# Where Code Gets Written

> **[Beginner]** · Editors, IDEs, the terminal, the REPL — and what each one is actually doing for you.

Code is plain text. You could write it in Notepad and it would run. **Nobody does**, and the reasons are worth understanding rather than just accepting, because each one names a real problem.

## The editor, and what it does for you

An **IDE** (Integrated Development Environment) is a text editor plus the tools that surround writing code. The modern distinction between "editor" and "IDE" has mostly collapsed — VS Code is an editor with extensions that make it an IDE — so the useful question isn't which label applies but **which of these you have**:

**Syntax highlighting.** Colour by role: keywords, strings, numbers, comments. It reads like decoration and works as error detection — an unclosed quote turns half the file into "string", and you see the mistake before you run anything.

**Error detection as you type.** The editor parses continuously and underlines what won't work. **This is the single biggest difference from Notepad**: the feedback loop shrinks from *run it and see* to *see it immediately*.

**Autocomplete.** Suggests names in scope, and what a function expects. Partly speed, mostly **discovery** — it's how you learn what's available on a thing without leaving the file.

**Go-to-definition and find-references.** Jump to where something is defined; find everywhere it's used. Trivial-sounding, and the thing that makes an unfamiliar codebase navigable. You'll use it far more than autocomplete.

**Integrated debugger.** Pause execution and inspect state. → [[foundations/programming-fundamentals/10-errors-and-debugging|note 10]].

**Refactoring.** Rename a variable everywhere it means *this* variable — not everywhere the text appears. The editor knows the difference; find-and-replace doesn't.

**What to actually use:** **VS Code** for almost anything, **PyCharm/IntelliJ** if you want the heavier language-specific tooling, **Neovim** if you want to invest in an editor as a long-term craft (the vault has [[tools/neovim/neovim-setup|notes on it]]). Any of them is fine. **Configuring your editor is not learning to program**, and it's an extremely comfortable way to avoid starting.

## Under the editor: the toolchain

The editor is a window. The actual work is done by programs it calls:

- **A compiler or interpreter** — turns your code into something that runs → [[foundations/programming-fundamentals/02-languages-and-the-translation-problem|note 02]]
- **A package manager** — fetches libraries other people wrote (`pip`, `npm`, `cargo`, `go get`) → [[foundations/programming-fundamentals/08-functions|note 08]]
- **A build tool** — orchestrates the steps for anything non-trivial
- **A debugger**
- **A formatter and a linter** — one fixes layout, one flags suspicious patterns
- **[[git/README|Git]]** — version control, which is not optional and which you should start using on day one, not "once the project is real"

**All of these exist independently of your editor.** That matters, because it's why the same project builds identically in [[devops/06-ci-cd/README|CI]] where there's no editor at all — and it's why "it works on my machine" is a solvable problem rather than a mystery.

## The terminal

A text interface where you type commands. It looks archaic and it is not going away, for one reason: **text commands compose and can be automated, and clicking cannot.**

The handful that get you moving:

```bash
pwd                 # where am I
ls                  # what's here
cd projects         # go into a folder
cd ..               # go up one
mkdir my-project    # make a folder
cat file.txt        # print a file
python3 script.py   # run a program
```

You do not need to memorise more than that to start. Fluency accumulates from use, and it's worth having: everything in [[devops/01-linux/README|devops]] assumes it, servers have no other interface, and [[devops/01-linux/12-bash-scripting|scripting]] turns anything repetitive into something you do once.

**Terminal vs shell vs console**, since the words get used loosely: the **terminal** is the window, the **shell** is the program inside it interpreting what you type (`bash`, `zsh`, `fish`), and the **console** is where a running program prints its output. In practice people say all three interchangeably and it rarely causes confusion.

## Standard output, and print as your first instrument

A program's default way of telling you something is to write text to **standard output**, which lands in your console. Every language has this:

```python
print("hello")            # Python
```
```javascript
console.log("hello");     // JavaScript
```
```java
System.out.println("hello");   // Java
```

**Two roles, and it's worth separating them:**

**Output for a user.** Fine for a command-line tool. Not fine for an app with a real interface — the console is a developer surface, and end users never see it.

**Instrumentation for you.** Printing a value to find out what it actually is at that moment. Crude, universally available, and genuinely one of the most effective debugging tools there is. → [[foundations/programming-fundamentals/10-errors-and-debugging|note 10]].

**In real systems, printing grows up into [[devops/10-observability/README|logging]]** — same idea, with severity levels, timestamps, and somewhere durable to go. When you eventually meet structured logging, it's this.

## The REPL

**Read–Eval–Print Loop.** A prompt where you type one expression and immediately see its result:

```
>>> 2 + 3
5
>>> name = "Kingsley"
>>> len(name)
8
```

Available in Python (`python3`), JavaScript (`node`), Ruby, and increasingly elsewhere.

**Use it constantly.** The REPL collapses the loop between *wondering* and *knowing* to about two seconds. Not sure whether a function includes the last element? Try it. Not sure what happens with an empty list? Try it.

**Guessing is the expensive habit this replaces.** Checking costs seconds; a wrong assumption buried in a function costs an hour of debugging later.

## Notebooks and browser sandboxes

**Notebooks** (Jupyter) interleave code, output and prose in cells you run individually. Excellent for exploration and data work; awkward for anything that needs to run unattended, because the hidden execution order makes them hard to reason about.

**Browser sandboxes** — Replit, CodePen, the Python and JavaScript consoles built into your browser's dev tools. **Nothing to install.** For your first week, that's a real advantage: an afternoon lost to a broken install is an afternoon that teaches you nothing about programming.

Press **F12** in your browser right now and you have a JavaScript REPL. That's a genuinely fine place to work through the next several notes.

## Related
- [[foundations/programming-fundamentals/04-syntax-and-the-shape-of-a-statement|syntax]] — what the editor is checking
- [[foundations/programming-fundamentals/10-errors-and-debugging|errors and debugging]] — the debugger, properly
- [[git/README|git/]] — start using it now, not later
- [[devops/01-linux/README|Linux]] — where the terminal goes next
- [[tools/neovim/neovim-setup|Neovim]] — if the editor itself becomes an interest

*Source: [reference] — from the freeCodeCamp Introduction to Programming course, extended with the terminal/REPL material it skipped as language-specific.*
