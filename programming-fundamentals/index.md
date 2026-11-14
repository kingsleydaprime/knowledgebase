# Programming Fundamentals

## What programming is

**Programming is writing instructions that a computer follows, step by step.**

A computer is very fast and very obedient, but it has no common sense. It can't guess what you meant; it does exactly what you wrote, nothing more. A program is a list of instructions written so precisely that a machine with no judgement can carry them out. Every app on your phone, every website and every game started as instructions like these.

This course is for someone who has **never written code**. It teaches the ideas that are the same in every programming language. Examples are shown in Python, JavaScript and Java, so you can see that the same idea only looks slightly different in each. You don't need to pick a language before you start.

## What you'll be able to do

By the end you will be able to:
- explain what a program is, and why a computer does exactly what you wrote even when that's wrong;
- set up a place to write code and run it;
- store information in variables, make decisions with `if`, and repeat steps with loops;
- keep many values together in lists and dictionaries;
- break a problem into small functions you can reuse;
- read an error message and find a bug methodically instead of guessing;
- plan a small program on paper before typing it;
- choose what to build next, so you keep improving.

## Where to start

Read the notes **in order, and slowly**. Each one builds on the one before.

### The core

1. [[programming-fundamentals/01-what-a-program-actually-is|What a Program Actually Is]]: instructions for something with no judgement, and why that one fact explains every bug.
2. [[programming-fundamentals/02-languages-and-the-translation-problem|Languages and the Translation Problem]]: why there are so many programming languages, how your code gets turned into something the computer runs, and how to pick a first language quickly.
3. [[programming-fundamentals/03-where-code-gets-written|Where Code Gets Written]]: the programs you write code in, the terminal, and how to try a line of code instantly.
4. [[programming-fundamentals/04-syntax-and-the-shape-of-a-statement|Syntax and the Shape of a Statement]]: the grammar rules of code, why they're so strict, and how to read an error message.
5. [[programming-fundamentals/05-variables-and-types|Variables and Types]]: giving names to values, the different kinds of values (numbers, text, true/false), and a common trap with copying.
6. [[programming-fundamentals/06-control-flow|Control Flow]]: making decisions with `if`, and repeating steps with loops.
7. [[programming-fundamentals/07-collections|Collections]]: keeping many values together in lists and dictionaries, and choosing the right one.
8. [[programming-fundamentals/08-functions|Functions]]: the most important note here. Packaging steps under a name so you can reuse them and stop thinking about their insides.
9. [[programming-fundamentals/09-recursion-and-the-call-stack|Recursion and the Call Stack]]: a function that calls itself, and how the computer keeps track of where it is.
10. [[programming-fundamentals/10-errors-and-debugging|Errors and Debugging]]: the three kinds of mistakes, and a method for finding bugs that beats changing lines until it works.
11. [[programming-fundamentals/11-planning-before-you-type|Planning Before You Type]]: breaking a problem into steps on paper before writing code.
12. [[programming-fundamentals/12-choosing-what-to-build-next|Choosing What to Build Next]]: getting out of endless tutorials, what to build, using AI without letting it do your learning, and where to go next in this vault.

### Once the core feels comfortable

These three are the bridge into learning a real language properly.

13. [[programming-fundamentals/13-objects-and-classes|Objects and Classes]]: bundling data with the functions that work on it, the way most real codebases are organised.
14. [[programming-fundamentals/14-programming-paradigms|Programming Paradigms]]: the different styles of writing programs, and the one habit every style agrees on.
15. [[programming-fundamentals/15-how-types-actually-work|How Types Actually Work]]: what's underneath note 05. Why the same bits in memory can be a number, a decimal or some letters, depending on what you tell the computer they are.

## Practice

Notes 01–15 are reading. This is where it becomes a skill.

16. [[programming-fundamentals/16-practice-exercises|Practice Exercises]]: sixteen exercises in any language, about 8–12 hours in total.
17. [[programming-fundamentals/17-practice-exercises-solutions|Solutions]]: worked answers with the reasoning. Try first.

## Key ideas to remember

Once you've read the notes, these are the points worth keeping. Each links to where it's explained.

1. **The computer did exactly what you wrote.** When something goes wrong, don't ask "why is it doing this?". Ask "what did I actually tell it to do?" → [[programming-fundamentals/01-what-a-program-actually-is|01]]
2. **The real mistake isn't picking the wrong first language. It's not picking one.** What you learn carries over to the next. → [[programming-fundamentals/02-languages-and-the-translation-problem|02]]
3. **Try it instead of guessing.** Running one line to see what happens takes seconds; guessing can take an hour. → [[programming-fundamentals/03-where-code-gets-written|03]]
4. **Decimal numbers in a computer are slightly off, so never use them for money.** Store money as whole numbers of the smallest unit, like kobo or cents. → [[programming-fundamentals/05-variables-and-types|05]]
5. **Copying a list doesn't copy it.** Both names point at the same list, so changing one changes "the other". This causes most "why did that change?" bugs. → [[programming-fundamentals/05-variables-and-types|05]]
6. **`=` puts a value in a variable; `==` asks whether two values are equal.** → [[programming-fundamentals/06-control-flow|06]]
7. **Counting starts at 0** because a position in a list is a distance from the start, and the first item is no distance away. → [[programming-fundamentals/07-collections|07]]
8. **If you keep searching a list for something, you probably wanted a dictionary.** The fix is five lines and can make a program thousands of times faster. → [[programming-fundamentals/07-collections|07]]
9. **A function lets you forget how something is done and just use it.** That's what makes programs bigger than your head possible. → [[programming-fundamentals/08-functions|08]]
10. **Find bugs by guessing a cause and testing it,** halving the code each time, not by changing things at random. → [[programming-fundamentals/10-errors-and-debugging|10]]
11. **Run your code every few lines.** It catches more bugs than any debugging technique. → [[programming-fundamentals/10-errors-and-debugging|10]]
12. **If you can't do it by hand, you can't write code for it.** → [[programming-fundamentals/11-planning-before-you-type|11]]
13. **You can't read your way to being good at this.** Build things, and finish them. → [[programming-fundamentals/12-choosing-what-to-build-next|12]]

## Where to go next

- [[dsa/index|Data Structures and Algorithms]]: the natural next course. Note 07 ends where it begins.
- [[languages/index|Languages]]: learning a specific language properly: Java, Go, Rust, C and C++.
- [[git/index|Git]]: saving the history of your code. Start using it on your first project, not your fifth.
- [[software-engineering/index|Software Engineering]]: what programming becomes when there are other people, deadlines and code that has to last.
- [[project-ideas|Project ideas]] and [[build-your-own-shit/index|Build Your Own]]: things to build once you're ready.

## Related

- [[using-ai/index|Using AI]]: a similar starting course, for using AI tools.
- [[PRIMETECHIE|The Primetechie Path]]: an order to do the whole vault in.
- [[learning/index|How I Learn]]: the method behind the vault.

---

## About this course

- **Size:** 17 notes, about 21,000 words. Written in August 2026; notes 13–17 were added afterwards.
- **A known weakness:** it was written by someone who already programs, and experienced people tend to forget which parts were hard. Notes 05 (the copying trap) and 09 (recursion) are probably still too fast. The fix is watching a real beginner use the notes and marking where they get stuck.
- **Not covered yet:** handling errors in code (exceptions), reading and writing files, doing several things at once, generics, and writing tests.
