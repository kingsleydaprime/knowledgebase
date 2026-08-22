# Choosing What to Build Next

> **[Beginner]** · The gap between "I know the concepts" and "I can build things", and the honest way across it.

You've reached the end of the concepts. Variables, control flow, collections, functions, recursion, debugging, planning. **Every mainstream language is now a matter of syntax and libraries rather than new ideas.**

And you will still, most likely, feel unable to build anything. That feeling is accurate, and it's not a knowledge problem.

## Why finishing a course doesn't make you a programmer

**Reading about programming and doing it exercise different skills entirely.** Following a tutorial, every decision has been made for you — what to build, how to structure it, which library, what to do when it breaks. Take those away and there's nothing to fall back on, because none of them were practised.

This produces **tutorial hell**: completing course after course, understanding every line, and freezing in front of an empty file. The exit is not another course. **It is building something nobody told you how to build**, which will be uncomfortable, and the discomfort is the mechanism.

The vault has a name for this: [[PRIMETECHIE|reading is not a rank]].

## Pick a language and commit for a while

You've probably already chosen → [[foundations/programming-fundamentals/02-languages-and-the-translation-problem|note 02]]. If not: **Python** unless you have a specific reason otherwise.

**Then stay there for a few months.** Switching languages at every friction point feels like progress and is avoidance — the difficulty is almost never the language. The concepts transfer; the fluency doesn't, and fluency is what you're building.

## Build something small and finish it

**Finished is the operative word.** Ten abandoned half-projects teach less than one complete small one, because everything hard about software lives in the last 20%: the edge cases, the errors, the awkward inputs, making it usable by someone who isn't you.

Good first projects share three properties: **you can describe them in one sentence**, **you'd actually use them**, and **you can finish in a few days.**

- A command-line to-do list that saves to a file
- A script that renames or organises files in a folder by rule
- A number-guessing game with input validation and a score
- A tool that reads a CSV and prints a summary
- A password generator with configurable rules
- A script that fetches something from an API and formats it

**Then extend the one you built.** Add persistence. Add error handling for every bad input you can think of. Add tests. Give it a config file. **Extending an existing project teaches you more than starting a new one**, because you're forced to read and modify code — which is the actual job → [[foundations/software-engineering/01-what-software-engineering-is|where the time goes]].

When you want bigger, the vault has two lists: [[project-ideas|project ideas]] across every domain, and [[build-your-own-x/README|build your own X]] for when you want to build the tools themselves.

## Practise deliberately, but don't mistake it for building

Sites with small, self-contained problems — Exercism, Codewars, LeetCode, Advent of Code — are genuinely useful for fluency: loops, string handling, collections, thinking in code without looking things up.

**Two honest limits.** They're all *given a specification, produce an answer* — no design decisions, no structure, no naming, no maintenance, which is most of real work. And **LeetCode specifically is interview preparation**, a distinct skill from building software, and starting it now is premature. The vault's position on this is in [[foundations/dsa/README|DSA]] and [[INTERVIEW|the interview index]].

**Roughly 20% exercises, 80% projects** is a reasonable split at this stage. The reverse is a way of feeling productive while avoiding the hard thing.

## Learn the surrounding tools now, not later

Concepts aren't the whole of programming. Three things are worth starting immediately, while your projects are small enough that mistakes are cheap:

**[[git/README|Git]].** Start on your first project, not your fifth. Learning version control on a codebase you care about is significantly worse.

**The [[devops/01-linux/README|command line]].** Every tool, server and CI system assumes it → [[foundations/programming-fundamentals/03-where-code-gets-written|note 03]].

**Reading other people's code.** Deeply uncomfortable and enormously effective. Pick a small library you use, open the source, and work out how one function does its job. You will be surprised how ordinary it is — and that demystification is itself the lesson.

## Use AI without letting it do the learning

You'll be using an LLM. Two ways to do it, and they lead to different places.

**Corrosive:** *"write me a program that does X"*, paste, move on. It works, you learned nothing, and you cannot debug or extend it — because you never built the model of *why* it's shaped that way.

**Useful:** write it yourself, get stuck, then ask *"why is this returning None?"*, *"what's the idiomatic way to do this in Python?"*, *"review this function — what have I missed?"* Ask it to explain, to quiz you, to critique your attempt.

**The test is simple: can you explain every line you're about to keep?** If not, you have a dependency rather than a skill. → [[using-ai/README|using AI]], especially [[using-ai/06-verifying-what-it-tells-you|verifying what it tells you]].

This vault's own position is that AI is best used as a [[learning/06-ai-as-sparring-partner|sparring partner]] — hints and questions rather than answers.

## Where to go from here

Once you can build small things unaided, the vault opens up:

| Interest | Start at |
|---|---|
| **Any direction at all** | [[PRIMETECHIE|the Primetechie path]] — a tiered progression through everything |
| A specific language, properly | [[languages/README|languages/]] |
| Web servers, APIs, databases | [[backend/README|backend]] |
| Browsers, interfaces | [[frontend/README|frontend]] · [[concepts/02-frontend/README|frontend concepts]] |
| Efficiency, interviews | [[foundations/dsa/README|DSA]] |
| Data, models | [[ai-ml/README|AI & ML]] |
| Servers, deployment, cloud | [[devops/README|devops]] |
| How the machine works | [[foundations/os/README|OS]] · [[foundations/computer-architecture/README|architecture]] |
| Breaking things, defensively | [[cybersecurity/README|cybersecurity]] |

**And [[learning/README|how I learn]]** for the method behind all of it — the reading list is not the point; the reps are.

## The three things worth carrying

**Confusion is the normal working state.** Everyone doing this is confused most of the time; experienced programmers are just used to it and have better tactics for getting unstuck. It never becomes "obvious" — you just get faster at the loop.

**You cannot read your way to competence.** Reading gives you vocabulary and the ability to recognise things. Building gives you the judgement. Both are needed; only one is comfortable, which is why most people do only one.

**Finish things.** It's the single highest-return habit at this stage, and it's the one almost nobody does.

## Related
- [[project-ideas|project ideas]] — the vault's build list, tiered
- [[build-your-own-x/README|build your own X]] — where reading stops
- [[PRIMETECHIE|the Primetechie path]] — an order to do all of this in
- [[learning/README|how I learn]] — the method
- [[foundations/software-engineering/README|software engineering]] — what this becomes professionally

*Source: [reference] — from the freeCodeCamp Introduction to Programming course (closing segments), extended with this vault's own position on tutorial hell and AI-assisted learning.*
