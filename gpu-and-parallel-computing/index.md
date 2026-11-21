# GPU and Parallel Computing

## What this course is about

**A GPU (graphics processing unit) is a processor built to do thousands of simple calculations at the same time. Parallel computing is splitting work so many processors can do it at once.**

A normal processor (CPU) has a few very clever cores, each good at working through one task quickly. A GPU has thousands of much simpler ones. It was invented to draw graphics, where millions of pixels each need the same small calculation. It turned out that training AI models is the same kind of work, huge amounts of identical arithmetic, which is why GPUs now power almost all of AI.

Getting speed from a GPU isn't automatic. Most of the time the bottleneck isn't the calculating at all but moving data to and from memory. This course explains how GPUs work, how to write code for them, and how to find out what's actually slowing your code down.

## What you'll be able to do

By the end you will be able to:
- explain why processors stopped getting faster and started getting more cores instead;
- explain how a GPU is organised, and when a GPU is the wrong tool;
- write simple GPU programs (kernels) and organise thousands of threads;
- use the standard parallel building blocks: applying, combining, and running totals;
- arrange data so the GPU can read it quickly;
- work out whether your code is limited by calculation or by memory;
- explain how AI models are trained across many GPUs at once.

## Where to start

**Before you start:** solid programming, and [[computer-architecture/index|Computer Architecture]], especially [[computer-architecture/08-the-memory-hierarchy|the memory hierarchy]]. **No GPU?** Google Colab and Kaggle give free ones, and most of the exercises run fine on them.

Read in order. Notes 01–02 are the ideas; 03–05 are writing and tuning code; 06 is how to diagnose speed; 07 is using many GPUs.

1. [[gpu-and-parallel-computing/01-why-parallelism|Why Parallelism]]: why processors stopped getting faster, how much splitting work can really speed it up, and which hardware suits which problem.
2. [[gpu-and-parallel-computing/02-gpu-architecture|GPU Architecture]]: how a GPU is built, why threads run in groups of 32 that must do the same thing, the special units for AI maths, and when a GPU is the wrong answer.
3. [[gpu-and-parallel-computing/03-the-programming-model|The Programming Model]]: writing GPU functions (kernels), organising threads into grids and blocks, and why threads can't all wait for each other mid-task.
4. [[gpu-and-parallel-computing/04-parallel-patterns|Parallel Patterns]]: the standard building blocks, including running totals done in parallel (which looks impossible), and fast matrix multiplication.
5. [[gpu-and-parallel-computing/05-memory-and-data-movement|Memory and Data Movement]]: reading memory in the order the GPU likes, its small fast shared memory, and the slow copy between computer and GPU that ruins most first attempts.
6. [[gpu-and-parallel-computing/06-performance-and-the-roofline|Performance and the Roofline]]: a simple chart that shows whether your code is limited by calculation or by memory, honest timing, and the usual bottlenecks in AI training.
7. [[gpu-and-parallel-computing/07-distributed-and-multi-gpu|Distributed and Multi-GPU]]: the ways of splitting a model's training across many GPUs, and serving models at scale.

## Practice

- [[gpu-and-parallel-computing/08-practice-exercises|Practice Exercises]]: hands-on experiments on a real GPU.
- [[gpu-and-parallel-computing/09-practice-exercises-solutions|Solutions]]: worked answers. Try first.
- **Quick experiments:** add two lists on the GPU and predict its speed from memory bandwidth alone, then check; swap one index to read memory in the wrong order and watch it get 10–30 times slower; profile a real training loop and look for gaps where the GPU sits waiting for data.

## Key ideas to remember

1. **A GPU hides slow memory by having so many threads that another is always ready to work** while one waits. Everything else follows from that design. → [[gpu-and-parallel-computing/02-gpu-architecture|02]]
2. **Threads run in groups of 32 that do the same instruction.** If threads in a group take different branches, they take turns. → [[gpu-and-parallel-computing/02-gpu-architecture|02]]
3. **Reading memory in the right order is the biggest speed lever,** up to 32 times. → [[gpu-and-parallel-computing/05-memory-and-data-movement|05]]
4. **Copying between the computer and the GPU is about 100 times slower than the GPU's own memory.** Keep data on the GPU. → [[gpu-and-parallel-computing/05-memory-and-data-movement|05]]
5. **"GPU at 100%" only means something was running,** not that it was running well. It can be 100% busy at 3% of its real speed. → [[gpu-and-parallel-computing/06-performance-and-the-roofline|06]]

## Related

- [[machine-learning/05-deep-learning/index|Deep Learning]]: the main reason this course exists.
- [[computer-architecture/index|Computer Architecture]]: the CPU that GPUs are compared against.
- [[computer-graphics/index|Computer Graphics]]: what GPUs were first built for.
- [[architecture/04-distributed-systems/index|Distributed Systems]]: large training runs are distributed systems.

---

## About this course

- **Size:** 9 notes, about 12,100 words, including practice and solutions. Written in August 2026, because the vault's large AI section had nothing on the hardware underneath it.
- **Further reading:** *Programming Massively Parallel Processors* (Kirk and Hwu), the standard textbook; NVIDIA's CUDA C++ Programming Guide; the Triton tutorials, the best modern starting point; and the FlashAttention paper, a masterclass in designing around memory.
