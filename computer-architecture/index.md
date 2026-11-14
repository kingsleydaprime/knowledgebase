# Computer Architecture

## What computer architecture is

**Computer architecture is how a processor is designed: how it reads and runs your program's instructions, and how it gets data from memory fast enough to keep busy.**

Your code is translated into very simple instructions, such as "add these two numbers" or "copy this value from memory". The processor (CPU) runs billions of them a second. To manage that, it uses tricks: it works on several instructions at once, guesses which way your `if` statements will go before it knows, and keeps recently used data in small, very fast memories called **caches**.

Those tricks are why two pieces of code that look equally fast can differ by ten or thirty times. Big-O tells you how code slows down as the input grows; this course explains why one loop is so much faster than another loop of the same Big-O. Mostly, the answer is memory.

## What you'll be able to do

By the end you will be able to:
- explain how numbers, decimals and text are stored as bits, and why `0.1 + 0.2` isn't exactly `0.3`;
- read simple assembly code, the processor's own instructions;
- explain how a processor works on several instructions at once, and what slows it down;
- explain why memory is usually the bottleneck, and lay out data so it's fast to read;
- avoid the hidden slowdowns when several processor cores share data;
- measure your program's speed and find where the time actually goes.

## Where to start

**Before you start:** basic programming, and [[dsa/03-algorithms/01-complexity-analysis/01-growth-and-asymptotic-notation|Big-O notation]]. Reading [[how-computers-work/index|How Computers Work]] first helps a lot but isn't required.

Read in order. Notes 02–05 are the foundations; 06, 07 and 10 are how a processor goes fast; 08 and 09 are memory, the most useful part in practice; 11 and 12 are multiple cores and measuring speed.

1. [[computer-architecture/01-what-architecture-is|What Computer Architecture Is]]: the agreement between software and processor, the two main families of processor design, and how long different operations take, scaled to human time so you can feel the difference.
2. [[computer-architecture/02-data-representation|Data Representation]]: how negative numbers, decimals and text are stored as bits, and why the order of fields in your data can matter.
3. [[computer-architecture/03-instruction-sets|Instruction Sets]]: the instructions a processor understands, how functions pass values to each other, and doing one operation on many values at once.
4. [[computer-architecture/04-assembly|Assembly]]: reading the processor's instructions, which is the skill that matters, rather than writing them.
5. [[computer-architecture/05-the-datapath|The Datapath]]: the five steps a processor takes to run each instruction.
6. [[computer-architecture/06-pipelining|Pipelining]]: working on several instructions at once, like an assembly line, and why sorting an array can make the same loop several times faster.
7. [[computer-architecture/07-branch-prediction-and-speculation|Branch Prediction and Speculation]]: how the processor guesses which way an `if` will go, and how those guesses led to the Spectre security flaw.
8. [[computer-architecture/08-the-memory-hierarchy|The Memory Hierarchy]]: the most important note here. Caches, why reading memory in order is fast, and why arrays beat linked lists in practice.
9. [[computer-architecture/09-caches-in-depth|Caches in Depth]]: how caches are organised, how cores keep their caches in agreement, and how two threads can slow each other down without sharing any data.
10. [[computer-architecture/10-out-of-order-and-superscalar|Out-of-Order and Superscalar]]: how the processor runs instructions out of order when it's safe, and how to write loops that let it.
11. [[computer-architecture/11-multicore-and-memory-models|Multicore and Memory Models]]: what happens when several cores read and write the same memory, and why some threading code works on one kind of processor and breaks on another.
12. [[computer-architecture/12-performance|Performance]]: a method for making code faster: measure, understand, fix the biggest thing, measure again.

## Practice

Everything in this course can be measured on the computer you're reading it on, for free.

- [[computer-architecture/13-practice-exercises|Practice Exercises]]: twelve experiments on your own machine, such as working out your cache sizes from timing alone.
- [[computer-architecture/14-practice-exercises-solutions|Solutions]]: worked answers. Try first.
- **Quick experiments:** time the same loop on sorted and unsorted data; multiply two matrices with the loops in different orders; look at the assembly your compiler produces on [Godbolt](https://godbolt.org) at different optimisation levels.

## Key ideas to remember

1. **Main memory is around 50–75 times slower than the processor's fastest cache.** Most programs wait on memory, not on calculation. → [[computer-architecture/08-the-memory-hierarchy|08]]
2. **To predict speed, count how much memory you touch, not how many operations you do.** → [[computer-architecture/08-the-memory-hierarchy|08]]
3. **An array and a linked list are both O(n) to walk through, yet the array can be ten times faster,** because its items sit next to each other in memory. → [[computer-architecture/08-the-memory-hierarchy|08]]
4. **Two threads updating different variables can still slow each other down** if those variables sit next to each other in memory. → [[computer-architecture/09-caches-in-depth|09]]
5. **An `if` that's easy to predict costs almost nothing; one that's random is expensive.** → [[computer-architecture/06-pipelining|06]]
6. **Never use decimal numbers for money, or compare them with `==`.** → [[computer-architecture/02-data-representation|02]]
7. **Speeding up a part that takes 10% of the time can save at most 10%.** Measure before optimising. → [[computer-architecture/12-performance|12]]

## Related

- [[how-computers-work/index|How Computers Work]]: the layer below, from electricity up to the processor.
- [[os/index|Operating Systems]]: the layer above.
- [[gpu-and-parallel-computing/index|GPU and Parallel Computing]]: processors built for thousands of tasks at once.
- [[compilers/index|Compilers]]: how your code becomes these instructions.
- [[languages/04-c/index|C]], [[languages/05-cpp/index|C++]] and [[languages/03-rust/index|Rust]]: languages where you control memory layout and can see these effects.

---

## About this course

- **Size:** 14 notes, about 18,900 words, including practice and solutions. Written in August 2026 after comparing the vault against a standard computer science syllabus.
- **Further reading:** Patterson and Hennessy, *Computer Organization and Design* (the basics); Hennessy and Patterson, *Computer Architecture: A Quantitative Approach* (depth); Drepper, *What Every Programmer Should Know About Memory* (free, and the best thing written on note 08's topic); Agner Fog's optimisation manuals.
- **Not covered yet:** input/output and DMA (devices writing to memory directly), power and heat, chip layout, verifying hardware designs, and FPGAs.
