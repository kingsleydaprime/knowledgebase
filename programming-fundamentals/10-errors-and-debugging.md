# Errors and Debugging

> **[Beginner]** · The three kinds of thing that go wrong, and a method for finding them that beats changing lines until it works.

Code not working is the normal state of code. **Debugging is not a sign you're bad at this; it's most of the job**, and it's a skill with actual technique rather than a talent you have or don't.

## The three kinds of error

Separating these is the first real diagnostic step, because each is found a different way.

### Syntax errors — it doesn't run

You broke the grammar. A missing bracket, a misspelled keyword, bad indentation.

```
SyntaxError: expected ':' (app.py, line 12)
```

**The easiest kind**, because the program refuses to start and tells you where. Your editor usually catches them before you save. → [[foundations/programming-fundamentals/04-syntax-and-the-shape-of-a-statement|note 04]].

### Runtime errors — it starts, then crashes

The code is valid, but something at execution time is impossible: dividing by zero, indexing past the end of a list, opening a file that isn't there, calling a method on `null`.

```
IndexError: list index out of range
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

**These depend on the data**, which is why they can pass every test you ran and fail on the first real user. That's the whole reason for testing edge cases: empty, zero, one, huge, negative, missing, and unexpected characters.

### Logic errors — it runs, and it's wrong

No crash. No message. The program does something, and it's not what you wanted.

```python
average = total + count      # meant to divide
```

Perfectly legal code, wrong answer.

**These are the expensive ones**, because nothing tells you they exist. They're found by testing, by someone noticing a wrong number, or by a customer. **The reason to check output against a case you worked out by hand is precisely this class of error** — it's the only class where the machine gives you no help at all.

## The method

The instinct when something breaks is to change something and re-run. **Resist it.** It occasionally works, teaches you nothing, and frequently introduces a second bug on top of the first.

### 1. Read the error. All of it.

Beginners skim errors; the message usually contains the answer. Three parts:

- **Type** — `TypeError`, `IndexError`. Tells you the *category*
- **Message** — often the fix, stated in English
- **Stack trace** — the chain of calls that got you there → [[foundations/programming-fundamentals/09-recursion-and-the-call-stack|note 09]]

**Read stack traces from the top for *where*, then downward for *how you got there*.** In a long trace, most frames are library code — find the deepest line that is *yours*. That's nearly always the real location.

### 2. Reproduce it reliably

You cannot fix what you can't trigger. Find the exact input and steps that cause it, every time. **An intermittent bug you can't reproduce is not ready to be fixed** — it's ready to be instrumented.

### 3. Form a hypothesis, then test *that*

The actual discipline: *"I think `total` is zero by the time it reaches line 40."* Then check that specific claim.

This is what separates debugging from thrashing. **One belief, one check, one answer.** Confirmed or eliminated, you've learned something either way — and thrashing produces neither.

### 4. Narrow it down

You know the input and the wrong output. The bug is somewhere between. **Check the middle.** State correct there? The problem is in the second half. Wrong? First half. Repeat.

This is **binary search applied to your own code**, and it finds a bug in a thousand lines in about ten checks. It is by far the highest-leverage habit in this note, and almost nobody does it deliberately at first.

Git makes a version of this automatic: [[git/09-investigating-history|`git bisect`]] binary-searches your commit history to find the one that introduced a bug.

## The tools

### Print statements

Crude, universally available, genuinely effective.

```python
print(f"DEBUG: total={total}, count={count}")
```

**Print the values you *believe* are correct, not the ones you suspect.** The bug is by definition where your model of the program and the program disagree — so the surprising line is the informative one.

Label your prints (`f"here: {x}"`), and **delete them when you're done.** A codebase littered with `print("here 3")` is its own problem.

### The debugger

Set a **breakpoint** and execution pauses there, letting you inspect every variable at that instant. Then:

- **Step over** — run this line, stop at the next
- **Step into** — go inside the function on this line
- **Step out** — finish this function, stop at the caller
- **Continue** — run until the next breakpoint

**A debugger is strictly more powerful than print statements**, and it's worth the hour it takes to learn your editor's. The reason people still use prints is that a debugger is awkward in some environments (production, containers, async code) — but for local work, stepping through a function while watching the values change teaches you more in five minutes than an afternoon of guessing.

### Comment it out

Suspect a section? Comment it out and re-run. Problem gone → it's in there. Still present → look elsewhere. Crude bisection, and it works.

### Rubber duck debugging

Explain the code, line by line, out loud, to something that isn't listening. **This has a real success rate**, because explaining forces you to state what each line *does* rather than what you assumed it did, and the gap usually surfaces mid-sentence.

## Habits that prevent the situation

**Run it constantly.** After every few lines, not after an hour. If it worked five minutes ago and doesn't now, the bug is in five minutes of work. **This single habit does more than every debugging technique combined**, because it collapses the search space before you have to search it.

**Commit often, with [[git/README|git]].** A working state you can return to means a bad experiment costs nothing. `git diff` also answers "what did I change?" — which is the answer, more often than it should be.

**Test the edges.** Empty input, zero, one item, negative numbers, huge values, missing fields, unexpected characters. The middle of the range almost always works.

**Handle the failure paths deliberately.** What happens when the file is missing, the network is down, the input is nonsense? Deciding this while writing is far cheaper than discovering it later.

**Write it down when it's genuinely hard.** What you tried, what you observed, what you ruled out. Half an hour in, you will not remember which of six theories you already eliminated.

**Change one thing at a time.** Change three, and if the behaviour changes you don't know which one did it.

## When you're stuck

**Take a break.** Not procrastination — a real effect. You form a mental model of what the code does, and it's wrong, and *rereading it reinforces the wrong model.* Stepping away is what dislodges it. Solving it in the shower is a cliché because it's true.

**Search the exact error message**, minus the parts specific to you (paths, variable names). Someone has had it.

**Ask well.** What you're trying to do, what you expected, what happened, the exact error, and the *smallest* code that reproduces it. Building that minimal example solves the problem outright often enough that the practice has a name: it forces you to remove everything that isn't the bug.

**AI is genuinely good at this specific task** — pasting an error and the relevant code gets useful answers. Two cautions: it will confidently invent functions that don't exist, and *understanding* the fix is the entire point. A fix you can't explain is a bug you'll have again. → [[using-ai/06-verifying-what-it-tells-you|verifying what it tells you]].

## Related
- [[foundations/programming-fundamentals/11-planning-before-you-type|planning]] — the errors you avoid by thinking first
- [[concepts/04-best-practices/04-testing-fundamentals|testing]] — automating the checks
- [[git/09-investigating-history|investigating history]] — `git bisect` and `git blame`
- [[backend/interview/01-production-debugging|production debugging]] — the same skill, higher stakes
- [[using-ai/06-verifying-what-it-tells-you|verifying AI output]]

*Source: [reference] — from the freeCodeCamp Introduction to Programming course, extended with the hypothesis/bisection method and stack-trace reading.*
