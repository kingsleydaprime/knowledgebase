# Programming Language Theory

## What this course is about

**Programming language theory studies programming languages with mathematics: what a program means exactly, and what you can prove about it before it ever runs.**

A [[compilers/index|compiler]] is about *how* to make a language work. This subject asks *what* a program means, precisely enough to prove things like "this program can never crash with a type error" or "this loop always finishes". It sounds abstract, and it is the most abstract course in the vault. But most features you use came out of it, often decades before they appeared in everyday languages: generics, automatic type inference, garbage collection, pattern matching, `Option` and `Result`, `async`/`await`, and Rust's borrow checker.

You can be an excellent engineer without this. What it gives you is the ability to understand *why* languages are designed the way they are, and some of the most useful habits in programming, like making invalid data impossible to represent.

## What you'll be able to do

By the end you will be able to:
- read the notation researchers use to describe languages;
- explain lambda calculus, a tiny language of just three parts that can compute anything;
- explain what it means for a type system to be "safe", and why some languages knowingly aren't;
- explain how a language works out types you didn't write;
- explain the surprising link between types and logical proofs;
- explain where Rust's borrow checker and `async` come from, and where languages are heading.

## Where to start

**Before you start:** [[mathematics/02-discrete-math/02-logic|Logic]] and [[mathematics/02-discrete-math/03-proof-techniques|Proof Techniques]] from discrete maths, and confidence in at least one programming language. [[theory-of-computation/index|Theory of Computation]] helps.

Read in order. Notes 02–03 are the foundations; 04–06 are about types, with 06 as the payoff; 07 is where the field is going.

1. [[programming-language-theory/01-what-pl-theory-is|What PL Theory Is]]: why describe languages mathematically, how to read the notation, and how a function's type alone can tell you what it does.
2. [[programming-language-theory/02-lambda-calculus|Lambda Calculus]]: a tiny language made only of functions that can still compute anything, and how adding types made it always finish but less powerful.
3. [[programming-language-theory/03-semantics|Semantics]]: three ways to define exactly what a program means, and how loop invariants become a method of proof.
4. [[programming-language-theory/04-type-systems-formally|Type Systems Formally]]: what makes a type system safe, and why Java's arrays knowingly break the rules.
5. [[programming-language-theory/05-type-inference|Type Inference]]: how languages like OCaml and Haskell work out every type without you writing any, and why Java's `var` can do far less.
6. [[programming-language-theory/06-curry-howard-and-proofs|Curry–Howard and Proofs]]: the discovery that types are statements and programs are proofs of them, and the proof assistants built on it.
7. [[programming-language-theory/07-effects-and-substructural-types|Effects and Substructural Types]]: tracking what code does (like input/output) in its type, the theory behind Rust's borrow checker, and where languages are going.

## Practice

- [[programming-language-theory/08-practice-exercises|Practice Exercises]]: twelve exercises, mostly building things, including a type inference algorithm.
- [[programming-language-theory/09-practice-exercises-solutions|Solutions]]: worked answers. Try first.
- **The single most useful exercise:** add a type checker to [[build-your-own-shit/04-your-own-language|your own language]]. A few hundred lines, and the notation stops being abstract.
- **Free and interactive:** [Software Foundations](https://softwarefoundations.cis.upenn.edu) makes you prove note 04's theorems yourself, and Lean's [Natural Number Game](https://adam.math.hhu.de) teaches proof as a browser game.

## Key ideas to remember

1. **Make illegal states impossible to represent.** Design your types so invalid data can't be built. The most useful idea in this course for everyday code. → [[programming-language-theory/06-curry-howard-and-proofs|06]]
2. **A type checker that's both safe and always finishes must reject some correct programs.** That's a proven limit, not a design flaw. → [[programming-language-theory/04-type-systems-formally|04]]
3. **A safe type system means two things:** a well-typed program never gets stuck, and its types stay true as it runs. → [[programming-language-theory/04-type-systems-formally|04]]
4. **Rust's ownership rules come from 1990s research,** finally made easy enough to use in 2015. → [[programming-language-theory/07-effects-and-substructural-types|07]]
5. **Ideas take decades to go from research to everyday languages,** held back by how easy they are to use, not by what they can do. → [[programming-language-theory/07-effects-and-substructural-types|07]]

## Related

- [[compilers/index|Compilers]]: building languages; this course is the theory behind them.
- [[theory-of-computation/index|Theory of Computation]]: what computers can and can't do.
- [[languages/03-rust/03-ownership|Rust: Ownership]]: where this theory most visibly reached everyday code.

---

## About this course

- **Size:** 9 notes, about 11,500 words, including practice and solutions. Written in August 2026.
- **Further reading:** Pierce, *Types and Programming Languages* (the standard text, and readable: if you read one, read this); Harper, *Practical Foundations for Programming Languages*; Wadler, *Programming Language Foundations in Agda* (free).
- **Not covered yet:** module systems, formal models of objects, analysing programs automatically, generating programs, macros, models of concurrency, and mixing typed and untyped code.
