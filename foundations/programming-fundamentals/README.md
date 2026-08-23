# Programming Fundamentals

The on-ramp. **For someone who has never written code** — the concepts that are the same in every language, before any language.

**~19,400 words across 16 notes.** Built August 2026. `[reference]`.

> **The one idea:** a computer has no judgement. Everything in this course is a technique for being completely explicit without the instructions becoming unmanageably long — and every one of them is the same move: **make a thing, name it, then reason with the name instead of the contents.**

## Why this exists

**The vault had no way in.** 900+ notes assuming you can already read code: [[foundations/dsa/README|DSA]] assumes arrays and loops, [[languages/README|languages/]] assumes you know what a variable is, [[foundations/software-engineering/README|software engineering]] explains the *profession* to someone who already programs, and [[backend/README|backend]] starts several floors up.

[[using-ai/README|using-ai/]] was written as the on-ramp for a non-programmer into AI. **This is the equivalent on-ramp into programming itself** — the same gap, noticed the same way, and filled from a source aimed squarely at people with no background.

It is **deliberately language-agnostic**. Examples appear in Python, JavaScript and Java to show the same idea wearing different punctuation, but nothing here requires you to pick one first. That's the point: the second language costs a fraction of the first, and that's only true if you learned the concepts rather than the syntax.

## Reading order

**In order, and slowly.** Unlike most of this vault, each note assumes the previous one.

1. [[foundations/programming-fundamentals/01-what-a-program-actually-is|What a Program Actually Is]] — **[Beginner]** — instructions for something with no judgement, and **why that single fact explains every bug**
2. [[foundations/programming-fundamentals/02-languages-and-the-translation-problem|Languages and the Translation Problem]] — **[Beginner]** — high vs low level, compiled vs interpreted, static vs dynamic, and **how to choose a first language in five minutes rather than three weeks**
3. [[foundations/programming-fundamentals/03-where-code-gets-written|Where Code Gets Written]] — **[Beginner]** — editors, the toolchain, the terminal, standard output, **and the REPL you should be using constantly**
4. [[foundations/programming-fundamentals/04-syntax-and-the-shape-of-a-statement|Syntax and the Shape of a Statement]] — **[Beginner]** — why the rules exist, the shapes that recur in every language, and **how to read an error message**
5. [[foundations/programming-fundamentals/05-variables-and-types|Variables and Types]] — **[Beginner]** — the primitives, floats and money, null, scope, naming — and **the reference-vs-value trap that causes the most confusion in this course**
6. [[foundations/programming-fundamentals/06-control-flow|Control Flow]] — **[Beginner]** — conditionals, switch, the four loops, short-circuiting, and **why nested loops deserve a second look**
7. [[foundations/programming-fundamentals/07-collections|Collections]] — **[Beginner]** — arrays, dynamic arrays, dictionaries, sets, indexing from zero, and **the list-scan-where-a-dictionary-belongs mistake**
8. [[foundations/programming-fundamentals/08-functions|Functions]] — **[Beginner]** — **the most important note here.** Parameters, returns, purity, libraries, and why the point of a function is to let you forget its contents
9. [[foundations/programming-fundamentals/09-recursion-and-the-call-stack|Recursion and the Call Stack]] — **[Beginner → Intermediate]** — base cases, frames, stack overflow, tail calls, **and why stack traces suddenly make sense**
10. [[foundations/programming-fundamentals/10-errors-and-debugging|Errors and Debugging]] — **[Beginner]** — the three kinds of error, and **a method that beats changing lines until it works**
11. [[foundations/programming-fundamentals/11-planning-before-you-type|Planning Before You Type]] — **[Beginner]** — decomposition, pseudocode, flowcharts, and how much planning is actually right
12. [[foundations/programming-fundamentals/12-choosing-what-to-build-next|Choosing What to Build Next]] — **[Beginner]** — tutorial hell, what to build, using AI without letting it do the learning, **and where in this vault to go next**

**Then two more, added after the course was written** — [[foundations/programming-fundamentals/13-objects-and-classes|13]] and [[foundations/programming-fundamentals/14-programming-paradigms|14]] close the gap the "honest note" below originally declared. Read them once 01–12 are comfortable; they're the bridge into [[languages/README|languages/]].

13. [[foundations/programming-fundamentals/13-objects-and-classes|Objects and Classes]] — **[Beginner → Intermediate]** — encapsulation, inheritance, polymorphism, **why "prefer composition over inheritance" is near-unanimous**, and where OOP stops being the answer
14. [[foundations/programming-fundamentals/14-programming-paradigms|Programming Paradigms]] — **[Beginner → Intermediate]** — imperative vs declarative, expressions vs statements, the four styles, and **the one heuristic worth more than the taxonomy**

**Then the reps.** 01–14 are reading; **this is where it becomes a skill.**

15. [[foundations/programming-fundamentals/15-practice-exercises|Practice Exercises]] — **[Beginner]** — sixteen exercises, any language, ~8–12 hours. Each reproduces a real behaviour rather than describing it
16. [[foundations/programming-fundamentals/16-practice-exercises-solutions|Solutions]] — worked answers with the reasoning, **after you've tried**

## The things worth carrying

1. **The computer has no judgement. It did exactly what you wrote.** The question is never *why is it doing this* but *what did I actually tell it to do* → [[foundations/programming-fundamentals/01-what-a-program-actually-is|01]]
2. **Every language is the same bargain**: expressiveness for you, in exchange for a translation step and some control → [[foundations/programming-fundamentals/02-languages-and-the-translation-problem|02]]
3. **The genuine mistake isn't picking the wrong first language — it's not picking.** The concepts transfer → [[foundations/programming-fundamentals/02-languages-and-the-translation-problem|02]]
4. **Check, don't guess.** The REPL turns an hour of debugging into two seconds of trying it → [[foundations/programming-fundamentals/03-where-code-gets-written|03]]
5. **Strict grammar isn't pedantry — it's the precondition for mechanical translation** → [[foundations/programming-fundamentals/04-syntax-and-the-shape-of-a-statement|04]]
6. **Floats are approximations. Never use them for money** → [[foundations/programming-fundamentals/05-variables-and-types|05]]
7. **Simple values are copied; everything else is shared unless you say otherwise.** The root of most "why did that change?" bugs → [[foundations/programming-fundamentals/05-variables-and-types|05]]
8. **`=` assigns, `==` compares** — and short-circuiting is a safety technique, not a footnote → [[foundations/programming-fundamentals/06-control-flow|06]]
9. **Indices start at 0 because an index is an offset**, not because someone was being difficult → [[foundations/programming-fundamentals/07-collections|07]]
10. **Scanning a list where a dictionary belongs is the most common beginner performance bug** — four orders of magnitude, five-line fix → [[foundations/programming-fundamentals/07-collections|07]]
11. **The point of a function is to let you forget its contents.** That forgetting is what allows programs bigger than your head → [[foundations/programming-fundamentals/08-functions|08]]
12. **Adding a dependency is a decision, not a free action** → [[foundations/programming-fundamentals/08-functions|08]]
13. **A missing base case doesn't hang — it crashes**, and the stack explains why → [[foundations/programming-fundamentals/09-recursion-and-the-call-stack|09]]
14. **Debug by hypothesis and bisection**, not by changing things. Ten checks finds a bug in a thousand lines → [[foundations/programming-fundamentals/10-errors-and-debugging|10]]
15. **Running it every few lines does more than every debugging technique combined** → [[foundations/programming-fundamentals/10-errors-and-debugging|10]]
16. **If you can't do it by hand, you cannot write code for it** → [[foundations/programming-fundamentals/11-planning-before-you-type|11]]
17. **You cannot read your way to competence — and finishing things is the habit almost nobody has** → [[foundations/programming-fundamentals/12-choosing-what-to-build-next|12]]
18. **Encapsulation and polymorphism aged well; deep inheritance did not.** Go dropped it, Rust never had it → [[foundations/programming-fundamentals/13-objects-and-classes|13]]
19. **Push the pure logic apart from the effects.** Every paradigm agrees, which is a decent sign it's the real lesson → [[foundations/programming-fundamentals/14-programming-paradigms|14]]

## Where this connects

| | |
|---|---|
| [[foundations/dsa/README\|DSA]] | **The natural next course.** Note 07 ends exactly where it begins |
| [[languages/README\|languages/]] | Where the syntax gets learned properly — Java, Go, Rust, C, C++ |
| [[foundations/software-engineering/README\|software engineering]] | What this becomes when other people, deadlines and next year are involved |
| [[git/README\|git/]] | Start on your first project, not your fifth |
| [[using-ai/README\|using-ai/]] | The parallel on-ramp, and note 12's position on not outsourcing the learning |
| [[foundations/compilers/README\|compilers]] · [[foundations/computer-architecture/README\|architecture]] | What's underneath — **much later** |
| [[project-ideas\|project ideas]] · [[build-your-own-x/README\|build your own X]] | Where reading stops |

## The honest note

**`[reference]`, with an asterisk.** I did not learn to program from this course — it was written *backwards*, by someone who already programs, from a source aimed at people who don't. **That's a real bias and it cuts a specific way:** an experienced person systematically forgets which things were hard, and reliably explains the wrong ones in too much detail.

**What would close the gap:** watching an actual beginner use these notes and marking where they stall. Nothing else substitutes for that, and until it happens the difficulty calibration here is a guess.

**Where I'd bet the guess is wrong:** note 05's reference-vs-value section and note 09 are probably still too fast, and note 07 probably under-explains why hashing gives O(1) — it's stated rather than shown.

**What's missing:** ~~exercises~~ — **closed by notes 15–16 (Aug 2026); the criticism this course made of reading courses no longer applies to it.** ~~objects and classes~~ — **closed by notes 13–14**, after a third source raised it independently and the original judgement ("it belongs in `languages/`") turned out to be wrong: OOP is language-*flavoured*, not language-specific, and leaving it out meant the course stopped one concept short of where every real codebase starts. Still absent: exceptions and error handling as a construct rather than an event, file and network I/O, async and concurrency, generics, and testing as a practice rather than a mention. **Exercises above all** — this is a reading course with no problems in it, which is exactly the criticism note 12 makes of reading courses.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Related
- [[README|Vault README]] — the full map
- [[PRIMETECHIE|The Primetechie Path]] — an order to do all of this in
- [[learning/README|How I Learn]] — the method behind the vault
- [[BUILD-PLAN|Build Plan]]
