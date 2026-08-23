# Practice Exercises

> **[Beginner]** · Sixteen exercises over the whole course. **This is the note that turns the previous fourteen into a skill.**

The course's own honest note says it plainly: *"this is a reading course with no problems in it, which is exactly the criticism note 12 makes of reading courses."* This is that fixed.

**Use any language.** Examples are in Python because it has the least syntax between you and the idea, but every exercise works in JavaScript, Java, Go or C — and doing a few in a second language is itself exercise 2.

**Work in order.** Several build on earlier output. Solutions in [[foundations/programming-fundamentals/16-practice-exercises-solutions|note 16]] — **genuinely try each one first.** The failures are the lesson; a solution you read is a solution you don't own.

**Time budget:** the whole set is roughly 8–12 hours. None of it needs anything installed beyond a language and an editor — several work in a browser console.

---

## Part A — The model (notes 01–04)

**1. Be the compiler for a person.**
Write instructions for "find the largest number in a list" precise enough for someone with no judgement to follow. No code — English, numbered steps. Then hand them to an actual person and have them follow it *literally* on `[3, 9, 2]`, then on `[]`, then on `[-5, -2]`.
**Done when:** all three produce a correct result, or you can name exactly which step was ambiguous. **Most people's first attempt fails on the empty list and on all-negatives** — the second because they started with "assume the largest is 0" → [[foundations/programming-fundamentals/01-what-a-program-actually-is|note 01]].

**2. One program, three languages.**
Write a program that reads a number and prints whether it's even or odd, in **three** languages you don't already know well. Don't learn the languages — copy syntax from their docs.
**Done when:** you can list what genuinely differed (type declarations, statement terminators, block delimiters, printing) and what didn't (the *idea*). This is the claim in [[foundations/programming-fundamentals/02-languages-and-the-translation-problem|note 02]] that the second language costs a fraction of the first — verify it rather than believe it.

**3. Break it four ways, on purpose.**
Take a working ten-line program and introduce, one at a time: a missing closing bracket, a misspelled variable name, a missing quote, and a colon/semicolon removed. Record the **exact** error message and the line number it reports each time.
**Done when:** you have four messages written down, and for at least one of them **the reported line is not the line you broke.** Understanding why is the point → [[foundations/programming-fundamentals/04-syntax-and-the-shape-of-a-statement|note 04]].

**4. Check five things instead of guessing.**
Open a REPL. Answer these by *trying*, not reasoning: does string slicing include the end index? What does dividing two integers give you? What happens when you index one past the end? What does an empty list evaluate to in an `if`? What is `0.1 + 0.2`?
**Done when:** you were wrong about at least one, and the whole exercise took under five minutes → [[foundations/programming-fundamentals/03-where-code-gets-written|note 03]].

---

## Part B — The building blocks (notes 05–08)

**5. Make a variable change without touching it.**
Create a list, assign it to a second name, modify through the second name, print the first. Then do the same with an integer. Then fix the list case so the original is untouched — and then break your fix with a *nested* list.
**Done when:** you can state the one rule that explains all four results, and you've seen a shallow copy fail on nested data → [[foundations/programming-fundamentals/05-variables-and-types|note 05]].

**6. Lose money to a float.**
Add `0.10 + 0.20` and compare it to `0.30` with `==`. Then write a till that adds 100 items at £0.10 and compare the total to £10.00. Then rewrite it correctly.
**Done when:** the naive version is provably wrong, and your fix uses integer pence or a decimal type — not rounding at the end, which hides the bug rather than removing it → [[foundations/programming-fundamentals/05-variables-and-types|note 05]].

**7. FizzBuzz, then FizzBuzz differently.**
Write it: 1–100, multiples of 3 → `Fizz`, of 5 → `Buzz`, of both → `FizzBuzz`. Then write it **again** with the rules in a data structure rather than in `if` statements, so adding "multiples of 7 → Bazz" is a one-line change.
**Done when:** the second version handles a new rule without touching any conditional logic. **This is the single most useful small exercise in the set** — it's the difference between code that works and code that absorbs change → [[foundations/programming-fundamentals/06-control-flow|note 06]] · [[foundations/programming-fundamentals/07-collections|note 07]].

**8. Earn the four orders of magnitude.**
Build a list of 20,000 random usernames. Then, for 5,000 lookups, check membership with `in` against the **list**, and time it. Now put them in a set or dictionary and time the same 5,000 lookups.
**Done when:** you have two timings and their ratio, and you can explain the difference from how each structure finds things. [[foundations/programming-fundamentals/07-collections|Note 07]] claims this is the most common beginner performance bug — **confirm the number yourself.**

**9. Refactor until each function does one thing.**
Take this and split it: a single 40-line function that reads a file of `name,score` lines, skips malformed rows, computes each person's average, assigns a grade, and prints a report.
**Done when:** every resulting function can be described **without using the word "and"**, and you can test the grade-assignment logic without a file existing → [[foundations/programming-fundamentals/08-functions|note 08]] · [[foundations/programming-fundamentals/11-planning-before-you-type|note 11]].

**10. Hunt the off-by-one.**
Write a function returning the last `n` items of a list. Test it with `n = 0`, `n = 1`, `n = len(list)`, `n = len(list) + 1`, and an empty list.
**Done when:** all five behave sensibly *and you decided deliberately* what `n = 0` and `n > len` should do, rather than accepting whatever fell out → [[foundations/programming-fundamentals/07-collections|note 07]].

---

## Part C — Depth (notes 09–14)

**11. Overflow the stack, then remove the recursion.**
Write recursive factorial. Call it with 5, then 100, then 100,000. Then rewrite it as a loop and call it with 100,000 again.
**Done when:** you've seen the actual error, can say what ran out, and can state why the loop version doesn't hit it → [[foundations/programming-fundamentals/09-recursion-and-the-call-stack|note 09]].

**12. Make exponential linear with one line.**
Write naive recursive Fibonacci. Time `fib(30)`. Add a cache. Time `fib(30)` again, then `fib(100)`.
**Done when:** you have three timings, and you can state roughly how many times `fib(25)` was computed in the naive version → [[foundations/programming-fundamentals/09-recursion-and-the-call-stack|note 09]].

**13. Find a bug by bisection, not by staring.**
Have someone plant one bug in a 60–100 line program of yours — or write one, leave it a week, and plant one yourself in a copy. Find it by **stating a hypothesis and testing the midpoint**, not by reading top to bottom. Log every check and its result.
**Done when:** your log has fewer than ~8 entries. If you found it by reading, do it again with a different bug — **the discipline is the exercise**, not the finding → [[foundations/programming-fundamentals/10-errors-and-debugging|note 10]].

**14. Plan first, and prove it was worth it.**
Pick something with real branching — a text-based ATM: balance, deposit, withdraw with insufficient-funds handling, PIN with three attempts, quit. **Write pseudocode and a flowchart before any code.** Note the time. Then implement it, and count how many times you had to restructure.
**Done when:** you have the pseudocode, the program, and an honest count. Then do exercise 15 *without* planning and compare the counts → [[foundations/programming-fundamentals/11-planning-before-you-type|note 11]].

**15. Model something with invariants.**
Build a `BankAccount` that **cannot** be put into an invalid state: no negative balance, no zero-or-negative deposits, no withdrawing more than the balance. Then try to break it from outside the class.
**Done when:** every attempt to corrupt it from outside fails, or you can name exactly which language feature would prevent it → [[foundations/programming-fundamentals/13-objects-and-classes|note 13]].

**16. The same problem, two paradigms.**
Take a list of order records and compute the total value per customer, twice: once **imperatively** (a loop, a mutable accumulator) and once **declaratively** (map/filter/reduce or comprehensions, no mutation).
**Done when:** both produce identical output, and you can say which you'd rather debug at 3 a.m. and why. There is no correct answer — **having a reason is the exercise** → [[foundations/programming-fundamentals/14-programming-paradigms|note 14]].

---

## When you're done

**You are not finished with this course until you've built something nobody told you to build** → [[foundations/programming-fundamentals/12-choosing-what-to-build-next|note 12]]. These exercises are reps; a project is the game.

Then: [[foundations/dsa/README|DSA]] for efficiency, or [[languages/06-python/README|Python]] to go deep in one language.

## Related
- [[foundations/programming-fundamentals/16-practice-exercises-solutions|Solutions]] — after you've tried
- [[foundations/programming-fundamentals/README|the course]]
- [[learning/06-ai-as-sparring-partner|AI as sparring partner]] — **how to use an LLM on these without wasting them**

*Source: [reference] — written Aug 2026 to close the gap this course's own README named.*
