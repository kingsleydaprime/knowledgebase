# Compilers

## What a compiler is

**A compiler is a program that translates code you write into instructions a computer can actually run.**

A processor only understands very simple instructions in binary, like "add these two numbers" or "jump to this instruction". You write something much easier to read, like `total = price * quantity`. A compiler bridges the gap. It reads your text, checks it makes sense, and works out the processor instructions that do the same thing, often making them faster along the way.

It works in a series of steps, like a factory line: split the text into words, work out the grammar, check that the types fit, turn it into a simpler in-between form, improve that, and finally produce the processor's instructions. Some languages (like Python) are **interpreted** instead: a program reads and runs your code directly, without producing a separate file first. This course covers both, and the mix of the two that most real languages use.

## What you'll be able to do

By the end you will be able to:
- explain each step a compiler takes, from text to running program;
- write the code that splits text into words and builds a tree from its grammar;
- explain how a compiler catches type errors before your program runs;
- explain how compilers make code faster, and the limits of what they can do;
- explain how programs are linked together and loaded into memory;
- build a small programming language of your own that runs on a simple virtual machine;
- explain how garbage collectors free memory automatically, and how JIT compilers speed programs up while they run.

## Where to start

**Before you start:** solid programming, and some [[dsa/index|data structures]] (trees especially). [[theory-of-computation/index|Theory of Computation]] explains why compilers are built in these steps, but isn't required.

Read in order.

### The front end: understanding your code

1. [[compilers/01-what-a-compiler-is|What a Compiler Is]]: the steps, why they're split into a front half and a back half, and the range from interpreters to compilers that most languages sit on.
2. [[compilers/02-lexical-analysis|Lexical Analysis]]: splitting text into words (tokens), such as names, numbers and symbols.
3. [[compilers/03-parsing|Parsing]]: building a tree from the grammar, with a simple method for working out which operations come first, like `*` before `+`.
4. [[compilers/04-asts-and-semantic-analysis|ASTs and Semantic Analysis]]: the code's tree, and working out what each name refers to.
5. [[compilers/05-type-systems-and-checking|Type Systems and Checking]]: checking that values are used correctly, and how some languages work out types without you writing them.

### The back end: producing instructions

6. [[compilers/06-intermediate-representations|Intermediate Representations]]: the simpler in-between form compilers work on, including LLVM's, which Rust, Swift and Clang all share.
7. [[compilers/07-optimisation|Optimisation]]: making code faster without changing what it does, and why copying small functions into their callers matters most.
8. [[compilers/08-code-generation|Code Generation]]: choosing processor instructions, deciding which values live in the processor's few fast registers, and how functions call each other.
9. [[compilers/09-linking-and-loading|Linking and Loading]]: joining compiled pieces into one program, and how the operating system loads it to run.

### Runtimes: running your code

10. [[compilers/10-bytecode-and-virtual-machines|Bytecode and Virtual Machines]]: compiling to instructions for a simple imaginary machine and writing a program that runs them. The realistic target for a language you build yourself.
11. [[compilers/11-garbage-collection|Garbage Collection]]: freeing memory automatically once nothing uses it, and the trade-offs between methods.
12. [[compilers/12-jit-compilation|JIT Compilation]]: compiling code while the program runs, the way Java and JavaScript engines get fast.

## If you're building your own language

The realistic path:

1. **Split text into tokens:** a few hundred lines. → note 02
2. **Build a tree** with a hand-written parser. → notes 03 and 04
3. **Run the tree directly** with a simple interpreter. → note 04
4. **You now have a working language.** That's a weekend or two; everything after is speed or rigour.
5. Then either a **virtual machine** (note 10) or a **type checker** (note 05), whichever interests you.
6. A **garbage collector** once you have functions and objects. → note 11
7. A **JIT** only if you have a specific reason. → note 12

Don't start by producing real processor instructions. It's a whole project in itself; target a virtual machine instead.

**The best guide:** [Crafting Interpreters](https://craftinginterpreters.com) by Robert Nystrom, free online. You build a complete language twice, and most of the practical advice here comes from it.

## Key ideas to remember

1. **A compiler is a chain of simple steps.** Each is manageable alone; the split also lets one compiler back end serve many languages. → [[compilers/01-what-a-compiler-is|01]]
2. **Record where every token came from (line and column) from the very start.** Without it you can't give good error messages, and adding it later is painful.
3. **Error messages are the product.** People see them far more often than successful output.
4. **Write the lexer and parser by hand.** Every major compiler does, because it gives better error messages. → [[compilers/03-parsing|03]]
5. **Look up variables by position, not by name, when you can.** It's the biggest easy speed-up for an interpreter. → [[compilers/04-asts-and-semantic-analysis|04]]

## Related

- [[theory-of-computation/index|Theory of Computation]]: why compilers are shaped this way.
- [[computer-architecture/index|Computer Architecture]]: the processor the instructions run on.
- [[languages/04-c/01-why-c-and-the-compilation-model|C: the compilation model]]: the steps, seen from a real language.
- [[programming-language-theory/index|Programming Language Theory]]: what languages mean, formally.
- [[how-computers-work/index|How Computers Work]]: its final project builds a small language and compiler.

---

## About this course

- **Size:** 12 notes, about 16,500 words, written in August 2026 to support building a language of your own.
- **Where it came from:** reference sources, mainly *Crafting Interpreters*, *Engineering a Compiler* (Cooper and Torczon) and the "Dragon Book". There's no compiler project in this vault yet.
- **Not covered yet:** recompiling only what changed (how IDEs stay fast), and language design itself; this course is about building languages, not what makes a good one.
