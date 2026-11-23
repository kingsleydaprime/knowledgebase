# Data Structures & Algorithms

## What data structures and algorithms are

**A data structure is a way of organising information in a computer so it's easy to use. An algorithm is a step-by-step method for solving a problem.**

Think of a contacts list. You could write names in the order you met people, which makes adding someone easy, but finding "Tunde" means reading the whole list. Or you could keep them in alphabetical order, which makes finding someone fast, but adding someone means squeezing them into the right place. Neither way is best at everything. **Each data structure is good at some jobs and slow at others**, and choosing well is most of the skill.

The method you use to search the list is an **algorithm**. Reading every name one by one works, but for a million names it's slow. Opening the alphabetical list in the middle and halving the search each time finds anyone in about 20 steps. That difference, between a method that takes days and one that takes a fraction of a second, is what this subject is about.

You'll rarely build these from scratch at work, because languages provide them. But you'll choose between them every day, and the choice decides whether your code is fast or painfully slow. They're also what most coding interviews test.

## What you'll be able to do

By the end you will be able to:
- estimate how a piece of code slows down as its input grows (called **Big-O**);
- pick the right container for a job: list, dictionary, set, queue, heap and more;
- explain how trees and graphs store things like folders, maps and social networks;
- search and sort efficiently, and know why some methods are faster;
- recognise common problem shapes and the standard technique for each;
- solve coding interview problems with a clear, repeatable process.

## Where to start

**Need to learn to code first?** Start with [[programming-fundamentals/index|Programming Fundamentals]]; this course assumes you can read a short program.

Read in the order below. Inside each folder, the file numbers follow this order. The only jumps between folders are Big-O (Step 1) and recursion (Step 3), which live in the algorithms folder but come before the data structures that use them.

### Step 1: Measuring how fast code is

1. [[dsa/01-loops-and-what-they-cost|01 — Loops and What They Cost]]: counting how many times code repeats, and spotting hidden loops that make code slow.
2. [[dsa/03-algorithms/01-complexity-analysis/01-growth-and-asymptotic-notation|01 — Growth and Asymptotic Notation]]: the shorthand everyone uses to describe how code slows down as the input grows. Everything after this uses it.

### Step 2: The basic containers

3. [[dsa/02-data-structures/01-arrays|01 — Arrays]]: items stored side by side, so you can jump straight to any position.
4. [[dsa/02-data-structures/02-dynamic-arrays|02 — Dynamic Arrays]]: arrays that grow when they're full, like Python's list.
5. [[dsa/02-data-structures/03-hash-maps|03 — Hash Maps & Hash Sets]]: finding a value by its name almost instantly, like Python's dictionary.
6. [[dsa/02-data-structures/04-linked-lists|04 — Linked Lists]]: items chained together, each pointing to the next.
7. [[dsa/02-data-structures/05-stacks-and-queues|05 — Stacks and Queues]]: last in, first out (a stack of plates) and first in, first out (a queue at the bank).

### Step 3: Recursion

8. [[dsa/03-algorithms/02-recursion/index|Recursion]]: solving a problem by solving smaller copies of it. Trees and many algorithms depend on it.

### Step 4: Trees

9. [[dsa/02-data-structures/06-trees/index|Trees]]: information arranged in branches, like folders on a computer, including the search trees used for fast lookups.
10. [[dsa/02-data-structures/06-trees/04-traversal/index|Tree Traversal]]: the standard ways to visit every item in a tree.
11. [[dsa/02-data-structures/07-heaps|07 — Heaps & Priority Queues]]: always getting the smallest (or largest) item quickly, as in a priority queue.
12. [[dsa/02-data-structures/08-tries|08 — Tries / Prefix Trees]]: trees for words, used for autocomplete.

### Step 5: Graphs

13. [[dsa/02-data-structures/09-graphs/index|Graphs]]: things connected to other things, like roads between cities or friends on social media.
14. [[dsa/02-data-structures/09-graphs/05-traversal/index|Graph Traversal]]: exploring a graph, going deep first (DFS) or wide first (BFS).
15. [[dsa/02-data-structures/09-graphs/06-algorithms/index|Graph Algorithms]]: shortest routes, putting tasks in a valid order, and connecting everything as cheaply as possible.
16. [[dsa/02-data-structures/10-union-find|10 — Union-Find / Disjoint Set Union]]: quickly tracking which items belong to the same group.

### Step 6: Classic algorithms

17. [[dsa/03-algorithms/03-searching/index|Searching]]: looking through items one by one, and halving the search each time (binary search).
18. [[dsa/03-algorithms/04-divide-and-conquer|04 — Divide and Conquer]]: splitting a problem in half, solving each half, and combining the answers.
19. [[dsa/03-algorithms/05-sorting/index|Sorting]]: putting things in order, and why some methods are much faster than others. The fast ones are divide and conquer.
20. [[dsa/03-algorithms/06-greedy-algorithms/index|Greedy Algorithms]]: taking the best-looking choice at each step, and when that's safe.
21. [[dsa/03-algorithms/07-dynamic-programming/index|Dynamic Programming]]: remembering answers to smaller problems so you never solve the same one twice.

### Step 7: Extra techniques (read as needed)

- [[dsa/03-algorithms/01-complexity-analysis/02-amortized-analysis|02 — Amortised Analysis]]: why an operation that's occasionally slow can still be fast on average.
- [[dsa/03-algorithms/08-number-theory-basics|08 — Number Theory Basics]]: prime numbers, and the greatest common divisor (the largest number that divides two others).
- [[dsa/03-algorithms/09-leader-algorithm|09 — Leader / Majority]]: finding the item that appears more than half the time.
- [[dsa/03-algorithms/10-max-slice-algorithms|10 — Max Slice]]: finding the stretch of numbers with the biggest total.
- [[dsa/03-algorithms/11-bit-manipulation|11 — Bit Manipulation]]: tricks that work directly on the 0s and 1s of a number.
- [[dsa/03-algorithms/12-math-and-geometry|12 — Math and Geometry]]: grid and maths techniques that come up in problems.

## Practice

- **Question banks:** every lesson has a matching `-qb` note: short questions with hidden answers, for testing yourself without looking. Start with [[dsa/01-loops-and-what-they-cost-qb|Loops and What They Cost: question bank]]. The method is explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].
- **Patterns:** [[dsa/04-patterns/index|LeetCode Patterns]] covers 15 techniques that keep coming up in problems, such as two pointers and sliding window. Recognising which one a problem needs is most of the battle. Do these after Step 6.
- **Problems:** [[dsa/neetcode-150/index|NeetCode 150]] has all 150 problems from a well-known practice list, each worked through and linked to the lesson behind it.
- **Interviews:** [[dsa/interview/index|DSA interview prep]], and the [[dsa/neetcode-150/interview-playbook|interview playbook]] for a step-by-step process to use in a coding interview.

## Key ideas to remember

1. **Every data structure makes some jobs fast by making others slow.** There's no structure that's best at everything. → [[dsa/02-data-structures/01-arrays|Arrays]]
2. **Ask which operation your code does most,** then pick the structure that makes that one fast.
3. **Searching a list is slow; looking up a dictionary is fast.** Swapping one for the other is often the biggest speed-up available. → [[dsa/02-data-structures/03-hash-maps|Hash Maps]]
4. **A loop inside a loop usually means trouble at scale.** A million items checked against a million items is a trillion steps. → [[dsa/01-loops-and-what-they-cost|Loops and What They Cost]]
5. **Halving the problem each step is enormously fast.** A million items takes about 20 steps. → [[dsa/03-algorithms/03-searching/index|Searching]]

## Related

- [[programming-fundamentals/index|Programming Fundamentals]]: the course before this one.
- [[databases/index|Databases]]: where trees, hashing and sorting do real work.
- [[theory-of-computation/index|Theory of Computation]]: what computers can't do at all, rather than just slowly.

---

## About this course

- **Size:** about 40,000 words across 30 lesson notes, each with a question bank, plus about 50,000 words working through all 150 NeetCode problems.
- **Where it came from:** written against a Codility course (its material is in `dsa/pdfs/`), then checked against the NeetCode 150 list to fill gaps. Several lessons (amortised analysis, recursion, dynamic programming, A\*, and others) were added after a real interview showed they were missing; see [[disgrace-from-interview|the interview gap list]].
- **How the files are organised:** ways of storing data are in `02-data-structures/`; methods are in `03-algorithms/`, unless a method belongs to one structure, in which case it's filed with that structure (so graph searching lives under `09-graphs/`).
- **Renumbered in November 2026** so the files follow the reading order: stacks and queues now come before trees and graphs, and searching before sorting.
- **Not covered yet:** fast text searching (the KMP algorithm), and segment and Fenwick trees.
