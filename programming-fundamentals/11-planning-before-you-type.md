# Planning Before You Type

> **[Beginner]** · Pseudocode, flowcharts, decomposition — the part that feels like not-programming and is where most of the quality comes from.

The instinct when given a problem is to open an editor and start typing. For anything past twenty lines, this reliably produces code you rewrite three times, discover a missing case halfway through, and then bolt something on at the end.

**Most professional programming time goes to thinking, reading and deciding rather than typing** — see [[foundations/software-engineering/01-what-software-engineering-is|what software engineering is]]. This note is the beginner-scale version of that.

## Understand the problem first

Sounds trivial. It's the step most often skipped, and skipping it means building the wrong thing correctly — the most expensive failure available.

Before anything else, answer:

- **What are the inputs?** What types, what ranges, where do they come from?
- **What are the outputs?** Exactly what shape?
- **What are the rules?** How does one become the other?
- **What are the edge cases?** Empty, zero, one, huge, negative, missing, malformed
- **What should happen when it goes wrong?**

**Then do one example by hand.** Take a real input, work out the correct output on paper, and keep it — it's your first test case, and it will catch more than you expect.

**If you can't do it by hand, you cannot write code for it.** That's not an insult; it's a useful signal. It means the problem isn't understood yet, and no amount of typing will fix that.

## Decomposition

Break the problem into pieces small enough to hold in your head, then check the pieces still compose.

*"Build a program that reads a CSV of student marks and prints a report"* is not one problem:

1. Read the file
2. Parse each line into fields
3. Convert marks from text to numbers
4. Handle rows that are malformed
5. Calculate the average per student
6. Assign a grade from the average
7. Format the output
8. Print it

**Each of those is a [[foundations/programming-fundamentals/08-functions|function]], and now each is small enough to be obviously right.** You can also write and test them one at a time, in any order, rather than having a program that either works completely or not at all.

**The failure mode is splitting along the wrong seam** — pieces that need to know too much about each other. If step 5 needs to understand the file format, the split was wrong.

## Pseudocode

**Pseudocode is your solution written in structured English**, ignoring syntax entirely. No semicolons, no exact function names, nothing that runs.

```
FUNCTION calculate_grade(marks):
    IF the list is empty:
        RETURN "No marks"

    total = 0
    FOR each mark in marks:
        add mark to total

    average = total / number of marks

    IF average >= 90: RETURN "A"
    ELSE IF average >= 80: RETURN "B"
    ELSE IF average >= 70: RETURN "C"
    ELSE: RETURN "F"
```

**Why bother when you could write the real thing?**

**It separates two hard problems.** *What should happen* and *how do I say it in this language* are both difficult. Doing them simultaneously is why beginners get stuck — the logic evaporates while you're looking up how to write a loop.

**It's fast to change.** Spotting a missing case in pseudocode costs a crossed-out line. Spotting it in written code costs a refactor.

**It exposes the gaps.** Writing the above, you're forced to decide about the empty list — a decision the English description let you skip, and one that would have crashed later.

**It survives a language change.** The pseudocode is the same for Python, Java or Go.

**It's language-independent, so it's how you talk to other people about code** — which is most of what a technical discussion is.

## Flowcharts

For anything with branching that's hard to follow in prose, a diagram is better than words:

```
      ┌──────────┐
      │  start   │
      └────┬─────┘
           ▼
    ┌──────────────┐
    │ read number  │
    └──────┬───────┘
           ▼
      ╱──────────╲
     ╱  n > 100?  ╲──── no ──┐
     ╲            ╱          │
      ╲──────────╱           ▼
           │ yes      ┌─────────────┐
           ▼          │ print "low" │
    ┌─────────────┐   └──────┬──────┘
    │ print "high"│          │
    └──────┬──────┘          │
           └────────┬────────┘
                    ▼
                 ┌──────┐
                 │ end  │
                 └──────┘
```

Rectangles for actions, diamonds for decisions, arrows for flow.

**What flowcharts are uniquely good at is showing you a path you forgot.** Every diamond has two arrows out. If one leads nowhere, you've found a missing case *before* writing it — and missing branches are exactly the class of bug that produces silent wrong answers.

Don't diagram everything. Diagram the part where the branching is genuinely confusing.

## Working top-down

Write the shape first, in terms of functions that don't exist yet:

```python
def main():
    data = read_file("marks.csv")
    students = parse_students(data)
    report = build_report(students)
    print(report)
```

That's the whole program, and it's readable before any of it works. Then implement each function — and each is small, isolated, and testable on its own.

**This is the same abstraction move as everything else in the course**: decide what the pieces *are* before deciding how they work. Its practical benefit is that you can stop at any point with something coherent, rather than a half-written monolith.

## How much planning is right

**Judgement, not rule.** Planning a ten-line script is waste. Not planning a five-hundred-line program is worse waste.

A workable calibration:

| Size | Planning |
|---|---|
| Under ~20 lines | Just write it |
| A function with real branching | A few lines of pseudocode |
| A program with several parts | Decompose into functions, sketch the main flow |
| Anything with tricky logic | Pseudocode it, plus a flowchart for the tricky part |
| Anything you'll maintain | The above, plus write down *why* you chose this shape |

**The signal that you under-planned is rewriting.** If you're restructuring a third time, stop typing and go back to paper.

**The signal that you over-planned is a perfect design for a problem you don't understand yet.** For anything genuinely unfamiliar, writing a rough version to *learn the problem* and then throwing it away is legitimate and often faster. The mistake is keeping it.

## Write it down for later

A note about *why* — why this structure, what else you considered, what constraint forced it — costs two minutes and saves an hour when you or someone else comes back in three months. The code shows *what*; only you know *why*, and you will not remember.

At professional scale this becomes an architecture decision record → [[concepts/04-best-practices/03-documentation-practices|documentation practices]].

## Related
- [[foundations/programming-fundamentals/08-functions|functions]] — what decomposition produces
- [[foundations/programming-fundamentals/12-choosing-what-to-build-next|what to build next]] — where to apply this
- [[foundations/software-engineering/02-the-software-development-lifecycle|the SDLC]] — this, at professional scale
- [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|how to approach system design]] — this, at system scale
- [[learning/README|how I learn]] — the board-and-notebook version of the same instinct

*Source: [reference] — from the freeCodeCamp Introduction to Programming course.*
