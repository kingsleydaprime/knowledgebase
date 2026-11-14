# Concepts

## What this course is about

**These are the habits and ideas that make code easy to read, test and change, whatever you're building and whichever language you use.**

Code that works today isn't the finish line. Someone, often you in six months, will have to read it, fix it and add to it. Code that's hard to understand or tangled together makes every change slow and risky. This course covers the practices experienced developers use to avoid that: writing clear code, testing it, keeping parts of a program from depending too much on each other, and proven designs (called **design patterns**) for problems that come up again and again.

## What you'll be able to do

By the end you will be able to:
- write code other people can read and change easily;
- write automated tests, and know which kind of test to use;
- make changes that are easy for a teammate to review;
- spot code that's too tangled, and untangle it;
- recognise common design patterns and know when one helps and when it's overkill;
- move data from one system to another safely.

## Where to start

You should be able to write small programs first ([[programming-fundamentals/index|Programming Fundamentals]]). Read best practices before design patterns: they're simpler, and the patterns build on them.

### Best practices

1. [[concepts/04-best-practices/01-clean-code/index|Clean Code]]: code is read far more often than it's written, so write it for the reader: clear names, small functions, honest comments.
2. [[concepts/04-best-practices/07-habits-that-make-change-easier|Habits That Make Change Easier]]: seven small habits that separate code that merely works from code that survives fifty more changes.
3. [[concepts/04-best-practices/04-testing-fundamentals/index|Testing Fundamentals]]: the kinds of automated test, fake stand-ins for slow or risky parts, and writing tests first.
4. [[concepts/04-best-practices/02-pr-structure|PR Structure]]: shaping a change (a pull request) so a teammate can review it quickly.
5. [[concepts/04-best-practices/03-documentation-practices|Documentation Practices]]: what to write down, where, and for whom.
6. [[concepts/04-best-practices/08-coupling-and-cohesion/index|Coupling and Cohesion]]: how much parts of a program depend on each other's insides, and how well each part's insides belong together. Most design advice comes back to these two.
7. [[concepts/04-best-practices/05-solid-principles/index|SOLID Principles]]: five rules for keeping code easy to change when requirements change, and when following them goes too far.
8. [[concepts/04-best-practices/06-data-migrations|Data Migrations]]: moving records from one system to another that stores them differently, without losing or mangling any.

### Design patterns

Proven solutions to problems that come up again and again, grouped by the kind of problem they solve.

9. [[concepts/03-design-patterns/01-creational-patterns/index|Creational Patterns]]: ways of creating objects, for when "just call the constructor" isn't enough.
10. [[concepts/03-design-patterns/02-structural-patterns/index|Structural Patterns]]: ways of fitting pieces together, such as wrapping one thing so it looks like another.
11. [[concepts/03-design-patterns/03-behavioral-patterns/index|Behavioral Patterns]]: ways for parts of a program to communicate and share work.

## Practice

- [[concepts/interview/index|Concepts interview prep]]: the questions these ideas come up as in interviews.
- The best practice is your own code: after each lesson, go back to something you've written and apply it.

## Key ideas to remember

1. **Write code for the next person who reads it.** That's usually someone with less context than you had. → [[concepts/04-best-practices/01-clean-code/index|Clean Code]]
2. **A test answers one question fast: "does this still work?"** → [[concepts/04-best-practices/04-testing-fundamentals/index|Testing Fundamentals]]
3. **Parts that know too much about each other's insides make every change ripple.** → [[concepts/04-best-practices/08-coupling-and-cohesion/index|Coupling and Cohesion]]
4. **A design pattern is a tool, not a goal.** Use one when the problem it solves is actually in front of you.

## Related

- [[backend/index|Backend]] and [[frontend/index|Frontend]]: these ideas applied to each side of an app.
- [[architecture/index|Architecture]]: the same thinking at the scale of whole systems.
- [[software-engineering/index|Introduction to Software Engineering]]: what the job involves.

---

## About this course

- **Why the sections start at 03:** sections 01 (backend) and 02 (frontend) moved into their own courses, [[backend/index|Backend]] and [[frontend/index|Frontend]], in August 2026. This folder now holds only ideas that belong to no single area.
- **Why the reading order differs from the file numbers:** best practices were numbered in the order they were written. The order above goes from simplest to most involved.
