# What Software Engineering Is

> **[Beginner]** · The distinction that actually matters, and why most of the job isn't typing.

## Before you start

You can already write a program that runs and does something useful. That's the only prerequisite.

After this lesson you will be able to:

1. Say in one sentence how software engineering differs from programming, and give two concrete things engineering adds.
2. Take a real piece of work and say where the time actually went.
3. Name the three habits — abstraction, decomposition, trade-offs — and point to one of each in code you've written.

**Study route.** Read straight through; it's short. Stop at *Check your understanding*, answer from memory, then do the practice task. The task is the finish line, not the reading.

## The kid version

Building a sandcastle is programming: you make it, it looks right, you're done. Building a real house is engineering. Other people will live in it for fifty years, a plumber who has never met you will have to fix the pipes, and if the roof leaks in winter someone has to know why. **The bricks are the same. What's different is that the house has to keep working for other people, long after you've stopped looking at it.**

**Where the analogy stops working.** A house is mostly finished when the builders leave. Software never is — it gets changed every week for as long as it's used, so the "fixing the pipes" part isn't the end of the job, it *is* the job.

## 1. Why this exists

You built a script that exports orders to CSV. It works. Three months later a teammate adds a "refunded" status, a customer in Lagos sees prices in the wrong currency, the script runs on a server with a different Python version, and nobody remembers why one column is formatted strangely. None of those problems is about the algorithm. **All of them are about the script surviving contact with other people and time** — and that's the gap this lesson names.

## Terms used in this lesson

1. **Programming**: This is getting a computer to do what you want. Its success test is "does it give the right output now, on this machine?"
2. **Software engineering**: This is programming plus everything needed for the program to keep working when there are other people, a deadline, money at stake, and a version of the code that has to work next year.
3. **Abstraction**: This is hiding detail behind a simpler interface so you can use something without holding all of it in your head. A function name is an abstraction; so is an HTTP API.
4. **Decomposition**: This is splitting a problem into pieces small enough to understand one at a time, then checking that the pieces still fit together.
5. **Trade-off**: This is a choice where gaining one property costs you another — faster but more expensive, simpler now but harder to change later. There is no "best" option, only the best option for what you're optimising.
6. **Production**: This is the live environment real users depend on, as opposed to your laptop or a test server.

## 2. Programming vs engineering

Programming is getting a computer to do what you want. Software engineering is getting a computer to do what you want **when there are other people, a deadline, money at stake, and a version of the code that has to keep working next year.**

That sounds like a slogan, so here it is concretely. A program that works on your laptop and a system a company depends on differ in things that have nothing to do with the algorithm:

| A working program has | A software system also needs |
|---|---|
| Correct output today | Correct output after six months of edits by four people |
| Your machine | Someone else's machine, and a server, and CI |
| Your understanding | A README, so the next person has it too |
| Your memory of the tricky bit | A test that fails when the tricky bit breaks |
| Whatever ran last | A record of what's deployed and how to undo it |

**The engineering is in the second column.** It's why two people can both "know how to code" and produce work of completely different value.

## 3. Where the time actually goes

The single most surprising fact for people entering the profession: **writing new code is a minority of the job.** Most hours go to reading existing code, working out what's actually being asked for, deciding between approaches, reviewing other people's work, and finding out why something broke.

This is not a complaint about bureaucracy. It's a consequence of the economics — code is written once and read continuously, so anything that makes reading cheaper pays back repeatedly. That single fact is the root of most practices in [[concepts/04-best-practices/index|best practices]].

**Pause and predict.** Think of the last feature you shipped. Before reading the worked example, guess what fraction of your time was typing new code.

## 4. The three habits

Almost everything in this vault is one of three moves applied to a different subject.

**Abstraction** — hiding detail behind an interface so you can reason about the whole without holding all of it. A function name, an HTTP API, a database index, TCP: all the same move at different scales. The skill is choosing *where* to put the boundary, because a bad abstraction is worse than none — it costs you the detail *and* misleads you about what's underneath.

**Decomposition** — splitting a problem until each piece fits in your head, then checking the pieces still compose. The failure mode is splitting along the wrong seam, so every change touches five modules. That's what [[concepts/04-best-practices/05-solid-principles/index|SOLID]] is mostly about.

**Trade-offs** — recognising there is no best option, only an option that's best given what you're optimising for. Faster or cheaper. Consistent or available. Simple now or flexible later. **Engineers are distinguished less by knowing more options than by being able to say why they chose one.** That's also what a system-design interview is measuring — see [[architecture/interview/01-system-design-round|the round]].

## 5. Worked example — one ticket, honestly timed

The ticket: *"Add a 'refunded' status to orders."* Here is a realistic breakdown for a mid-sized codebase, five and a half hours in total:

| Activity | Time | Which habit, or which column of the table in §2 |
|---|---|---|
| Asking what "refunded" means — full or partial? Does stock go back? | 40 min | Requirements — the cheapest place to find out you're building the wrong thing |
| Reading the order code, the payment webhook, and two reports that filter by status | 90 min | Reading is the job (§3) |
| Deciding: a new status value, or a separate `refunds` table? | 30 min | **Trade-off** — a status is simpler now; a table handles partial refunds later |
| Writing the code and the migration | 60 min | The part people think is the whole job |
| Writing tests, including "a refunded order doesn't appear in revenue" | 50 min | "A test that fails when the tricky bit breaks" |
| Review comments, fixes, and the deploy | 60 min | "A record of what's deployed and how to undo it" |

**Typing new code: one hour of five and a half.** The rest is what made the one hour correct. Notice too that the most valuable 40 minutes came first: had nobody asked "full or partial?", every later step would have been competently done on the wrong thing.

## 6. Engineer, developer, programmer

Practically, these are used interchangeably in job ads and you should not read much into a title. Where the distinction has content:

- **Programmer** — emphasis on writing the code
- **Developer** — writing code within a product and a team
- **Engineer** — the above plus responsibility for how the system behaves in production: whether it stays up, what it costs, what happens when it fails

The useful version isn't a hierarchy of people, it's a question about *scope of responsibility*. "Does it work?" is programming. "Will it still work at 10× traffic, and what happens at 3am when it doesn't?" is engineering.

## Common pitfalls

1. **Measuring yourself by lines written.** Deleting a module, writing a one-paragraph decision record, or asking the question that cancels a feature can be the most valuable thing you do all week.
2. **Treating "engineering" as process for its own sake.** The second column of §2 exists because each item prevented a real failure. If you can't name the failure a practice prevents, question the practice.
3. **Abstracting too early.** An interface with one implementation and a guessed-at future is the "bad abstraction" from §4 — it hides the detail and misleads.

## Check your understanding

1. In one sentence, what does software engineering add to programming?
2. Why does "code is read more than it is written" lead to practices like clear naming and tests?
3. Pick one: a function name, a REST API, TCP. Which of the three habits is it an example of, and what detail does it hide?
4. Your team must choose between storing images in the database or in object storage. Which habit is this, and what's the wrong way to answer it?

<details>
<summary>Answers — after your attempt</summary>

1. It adds everything needed for the program to keep working with other people, over time, in production — tests, documentation, deployment records, reviewable structure.
2. Every minute saved for a reader is saved again for every future reader, while writing happens once. Anything that cheapens reading pays back many times.
3. All three are **abstraction**. A function name hides its body; a REST API hides the server's language and database; TCP hides packet loss, reordering and retransmission.
4. A **trade-off**. The wrong answer is "object storage is best." A right answer names what you're optimising: "object storage, because images are large and served directly to browsers; the cost is a second system to back up and keep in sync."

</details>

## Practice — independent task

**Time one real ticket.** Choose the last feature or bug fix you shipped in any project.

1. Reconstruct a breakdown like §5: activity, rough time, and which habit or column it belongs to.
2. Find one moment where a 10-minute question up front would have saved time later.
3. Find one example each of abstraction, decomposition and a trade-off in that code, and write one sentence on each.

**Done when:** the breakdown adds up to roughly the real time, you can point to the three habits in actual files, and you can say — closed-book — why typing was a minority of the time.

## Before moving on

You can explain the programming/engineering difference to a non-programmer, and you've timed one real ticket.

**Recap.** Programming makes it work; engineering keeps it working with other people and over time. Most of the job is reading, deciding and checking. The three habits — abstraction, decomposition, trade-offs — recur in every subject in this vault.

**Next.** [[software-engineering/02-the-software-development-lifecycle|The software development lifecycle]] gives the time-breakdown above its standard names, which is what lets you say *which phase* a problem belongs to.

## Related
- [[software-engineering/02-the-software-development-lifecycle|the SDLC]] — the shape of the work
- [[software-engineering/03-the-engineering-roles|the roles]] — who does which part
- [[PRIMETECHIE|the Primetechie path]] — the tiered progression through this whole vault

*Source: [reference] — written as the introduction the rest of this vault assumed but never wrote down.*
