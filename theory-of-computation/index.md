# Theory of Computation

## What this course is about

**Theory of computation asks two questions: what can a computer solve at all, and what can it solve quickly?**

Some problems turn out to be impossible for any computer, however powerful, and this can be proven. The most famous: no program can look at every other program and correctly say whether it will run forever or eventually stop. Other problems are possible but so slow that the best known method would take longer than the age of the universe for big inputs. Many everyday problems, like finding the best delivery route through many cities, are in this second group.

Knowing this saves you from spending months looking for a solution that can't exist. It also explains everyday things: why you can't reliably check HTML with a regular expression, why every code checker sometimes complains about correct code, and why some encryption is safe and some isn't.

The course does this with simple imaginary machines. A machine with no memory can recognise some patterns. Give it a stack of memory and it can match brackets. Give it unlimited memory and it can do anything a real computer can. **The amount of memory a problem needs tells you which tool it needs.**

## What you'll be able to do

By the end you will be able to:
- explain what regular expressions can and can't match, and why;
- explain why programming languages need parsers, not just regular expressions;
- describe the Turing machine, the simple model of every computer;
- prove that some problems can't be solved by any program;
- recognise problems that have no fast exact solution, and choose a practical way around them;
- explain what quantum computers could and couldn't break.

## Where to start

**Before you start:** [[mathematics/02-discrete-math/index|Discrete Mathematics]], especially logic, proof and sets. This course is mostly proofs.

Read strictly in order. Notes 02–04 climb from simple machines to more powerful ones; 05–06 are the most powerful machine and its limits; 07–08 are about speed.

1. [[theory-of-computation/01-what-computation-is|What Computation Is]]: treating problems as sets of strings, the ladder of machine types, and why every programming language can compute the same things.
2. [[theory-of-computation/02-finite-automata|Finite Automata]]: machines with no memory beyond their current state, which is what regular expressions really are, and how a badly written one can freeze a server.
3. [[theory-of-computation/03-regular-languages|Regular Languages]]: what those machines can and can't recognise, and a proof that HTML can't be fully parsed with a regular expression.
4. [[theory-of-computation/04-context-free-languages|Context-Free Languages]]: grammars, and machines with a stack, which can match nested brackets. How programming languages are parsed.
5. [[theory-of-computation/05-turing-machines|Turing Machines]]: the simplest model that can do anything a computer can, and how one machine can run any other, the idea behind every computer.
6. [[theory-of-computation/06-decidability|Decidability]]: the problems no program can solve, starting with "will this program stop?", and why every code checker must sometimes be wrong.
7. [[theory-of-computation/07-complexity-classes|Complexity Classes]]: P, NP and what "NP-complete" means, and what to do in practice when your problem is one. The most useful note here.
8. [[theory-of-computation/08-beyond-p-vs-np|Beyond P vs NP]]: algorithms that use randomness, what quantum computers mean for encryption, and proofs that reveal nothing but their truth.

## Practice

- [[theory-of-computation/09-practice-exercises|Practice Exercises]]: fourteen problems, including three proofs from scratch, a regular-expression engine and a solver for logic puzzles to build.
- [[theory-of-computation/10-practice-exercises-solutions|Solutions]]: worked answers. Try first.
- **The proofs are the content.** Reading a proof isn't the same as producing one, so do at least: prove that strings like `aaabbb` (equal numbers of `a`s then `b`s) can't be matched by a regular expression, prove that the halting problem can't be solved, and do one NP-completeness proof.

## Key ideas to remember

1. **The ladder of machines is a ladder of memory.** If something can nest to any depth, like brackets, you need at least a stack: a parser, not a regular expression. → [[theory-of-computation/03-regular-languages|03]]
2. **Every general-purpose language can compute the same things.** The language only changes what's convenient. → [[theory-of-computation/01-what-computation-is|01]]
3. **No program can answer any interesting question about what every program does,** such as "does it stop?" or "is it malicious?". So code checkers must either miss problems or flag correct code. → [[theory-of-computation/06-decidability|06]]
4. **"Impossible" and "too slow" are different.** For impossible, change the problem; for too slow, settle for a good-enough answer. → [[theory-of-computation/05-turing-machines|05]]
5. **For an NP-complete problem, you can't have exact, fast and general all at once.** Pick two. Spotting this in the first five minutes, not the sixth month, is the practical payoff. → [[theory-of-computation/07-complexity-classes|07]]
6. **Quantum computers aren't just faster searchers.** They break today's public-key encryption, but ordinary encryption survives with longer keys. → [[theory-of-computation/08-beyond-p-vs-np|08]]

## Related

- [[compilers/index|Compilers]]: the practical use of notes 02–04. Lexers are finite automata and parsers use a stack.
- [[dsa/03-algorithms/01-complexity-analysis/01-growth-and-asymptotic-notation|Big-O]]: measuring speed, which notes 07–08 build on.
- [[cybersecurity/05-cryptography/index|Cryptography]]: built on problems believed to be too slow to solve.
- [[computer-architecture/index|Computer Architecture]]: the universal machine, built in hardware.

---

## About this course

- **Size:** 10 notes, about 13,300 words, including practice and solutions. Written in August 2026 after comparing the vault against a standard computer science syllabus.
- **Further reading:** Sipser, *Introduction to the Theory of Computation* (the standard text, and very readable); Papadimitriou, and Arora and Barak, for complexity.
- **Not covered yet:** formal proofs that the machine types are equivalent (they're described, not derived), and the more specialised branches of complexity theory.
