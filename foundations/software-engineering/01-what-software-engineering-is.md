# What Software Engineering Is

> **[Beginner]** · The distinction that actually matters, and why most of the job isn't typing.

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

## Where the time actually goes

The single most surprising fact for people entering the profession: **writing new code is a minority of the job.** Most hours go to reading existing code, working out what's actually being asked for, deciding between approaches, reviewing other people's work, and finding out why something broke.

This is not a complaint about bureaucracy. It's a consequence of the economics — code is written once and read continuously, so anything that makes reading cheaper pays back repeatedly. That single fact is the root of most practices in [[concepts/04-best-practices/README|best practices]].

## The three habits

Almost everything in this vault is one of three moves applied to a different subject.

**Abstraction** — hiding detail behind an interface so you can reason about the whole without holding all of it. A function name, an HTTP API, a database index, TCP: all the same move at different scales. The skill is choosing *where* to put the boundary, because a bad abstraction is worse than none — it costs you the detail *and* misleads you about what's underneath.

**Decomposition** — splitting a problem until each piece fits in your head, then checking the pieces still compose. The failure mode is splitting along the wrong seam, so every change touches five modules. That's what [[concepts/04-best-practices/05-solid-principles|SOLID]] is mostly about.

**Trade-offs** — recognising there is no best option, only an option that's best given what you're optimising for. Faster or cheaper. Consistent or available. Simple now or flexible later. **Engineers are distinguished less by knowing more options than by being able to say why they chose one.** That's also what a system-design interview is measuring — see [[architecture/interview/01-system-design-round|the round]].

## Engineer, developer, programmer

Practically, these are used interchangeably in job ads and you should not read much into a title. Where the distinction has content:

- **Programmer** — emphasis on writing the code
- **Developer** — writing code within a product and a team
- **Engineer** — the above plus responsibility for how the system behaves in production: whether it stays up, what it costs, what happens when it fails

The useful version isn't a hierarchy of people, it's a question about *scope of responsibility*. "Does it work?" is programming. "Will it still work at 10× traffic, and what happens at 3am when it doesn't?" is engineering.

## Related
- [[foundations/software-engineering/02-the-software-development-lifecycle|the SDLC]] — the shape of the work
- [[foundations/software-engineering/03-the-engineering-roles|the roles]] — who does which part
- [[PRIMETECHIE|the Primetechie path]] — the tiered progression through this whole vault

*Source: [reference] — written as the orientation the rest of this vault assumed but never wrote down.*
