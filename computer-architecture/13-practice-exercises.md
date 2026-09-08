# Practice Exercises

> **[Intermediate → Advanced]** · Twelve experiments on the machine you're reading this on. **Every claim in this course is measurable in minutes, for free.**

This course's own honest note says the gap here is *"less excusable than in `engineering/` or `robotics/`"* — no hardware to buy, no lab, just `perf` and an afternoon. This is that afternoon.

**Setup:** a C compiler (`gcc` or `clang`) and, on Linux, `perf`:
```bash
sudo apt install linux-tools-common linux-tools-$(uname -r)   # Debian/Ubuntu
sudo dnf install perf                                          # Fedora
sudo sysctl kernel.perf_event_paranoid=1                       # allow user counters
```
No `perf`? Most exercises work with wall-clock timing alone; the ones that don't are marked.

**A warning that is itself the lesson: several of these fail to reproduce at `-O2`.** That isn't a broken exercise — modern compilers defeat the classic demonstrations, and finding out *how* teaches more than the original result. Solutions in [[foundations/computer-architecture/14-practice-exercises-solutions|note 14]].

**First, know your machine:**
```bash
lscpu | grep -E "Model name|^CPU\(s\)|cache"
```
Write down your L1d, L2 and L3 sizes. Several exercises need them.

---

## Part A — Representation and instructions (notes 02–04)

**1. Find the floating-point edges.**
In any language, print `0.1 + 0.2`, then find the largest integer `n` where `float(n) != float(n+1)` for a 64-bit double. Then compute `(2**53) + 1` as a float.
**Done when:** you can state how many significant decimal digits a double actually carries, and why the failure begins exactly where it does → [[foundations/computer-architecture/02-data-representation|note 02]].

**2. Overflow deliberately, three ways.**
In C, overflow a signed `int`, an `unsigned int`, and shift a value by more than its width. Compile at `-O0` and `-O2` and compare. Then compile with `-fsanitize=undefined`.
**Done when:** the sanitiser has reported something, and you can say which of the three is defined behaviour and which is UB → [[foundations/computer-architecture/02-data-representation|note 02]] · [[languages/04-c/README|C]].

**3. Read what the compiler actually emits.**
Take a five-line function and compile it at `-O0`, `-O1`, `-O2`, `-O3` (`gcc -S`, or use [godbolt.org](https://godbolt.org)). Diff the assembly. Then write a function whose entire body is optimised away.
**Done when:** you've watched a loop become a constant, and can point at the instruction that replaced it → [[foundations/computer-architecture/04-assembly|note 04]].

---

## Part B — The memory hierarchy (notes 08–09)

**4. Measure your own cache sizes.**
Walk an array of size *N* with a stride of 64 bytes, timing per-access latency, for *N* from 4 KB up to 64 MB. Plot latency against *N* on a log axis.
**Done when:** the plot has visible **steps**, and the positions of those steps match the L1/L2/L3 sizes you wrote down. **This is the single best exercise in this course** — you will have measured the memory hierarchy without being told it exists → [[foundations/computer-architecture/08-the-memory-hierarchy|note 08]].

**5. Make stride cost you.**
Sum every element of a large array. Then sum every 2nd, 4th, 8th, 16th, 32nd element, *normalising per element touched*.
**Done when:** you can explain why per-element cost rises until stride 16 (on 64-byte lines with 4-byte ints) and then stops rising → [[foundations/computer-architecture/09-caches-in-depth|note 09]].

**6. The 5× from reordering identical arithmetic.**
Write a 1024×1024 matrix multiply three ways: naive `ijk`, loop-interchanged `ikj`, and blocked (tile 64). Same arithmetic, same result. Time all three.
**Done when:** you have three timings and can explain the difference **purely in terms of access patterns**, without mentioning instruction count. Try N=512 as well — **the effect changes, and why is the point** → [[foundations/computer-architecture/09-caches-in-depth|note 09]].

---

## Part C — Speculation and parallelism (notes 06–07, 10–11)

**7. Reproduce the sorted-array result — and then fail to.**
The classic: sum only elements `>= 128` in a 32K array of random bytes, sorted vs unsorted. Compile at **`-O0`** and measure. Now compile the same code at **`-O2`** and measure again.
**Done when:** you have a large difference at `-O0` and **almost none at `-O2`**, and you have found the instruction in the `-O2` assembly that explains it. **This is the most instructive exercise here** → [[foundations/computer-architecture/07-branch-prediction-and-speculation|note 07]].

**8. Count the mispredictions.** *(needs `perf`)*
```bash
perf stat -e branches,branch-misses ./your_program
```
Run it on both the sorted and unsorted `-O0` versions.
**Done when:** the miss *rate* — not count — differs by roughly an order of magnitude, and you can relate it to the ~15–20 cycle penalty note 07 describes.

**9. Make a program faster by adding memory.**
Two threads each incrementing their own counter in a shared array: `counter[0]` and `counter[1]`. Time it. Now pad so each counter sits on its own 64-byte cache line. Time again.
**Done when:** the padded version is **substantially faster despite using more memory**, and you can name the phenomenon → [[foundations/computer-architecture/11-multicore-and-memory-models|note 11]].

**10. Break sequential consistency.** *(hard)*
Two threads: thread 1 sets `x=1` then reads `y`; thread 2 sets `y=1` then reads `x`. Run the pair millions of times, counting how often **both** read 0.
**Done when:** you have observed a non-zero count on x86, or explained why you didn't — then inserted a fence and watched it go to zero → [[foundations/computer-architecture/11-multicore-and-memory-models|note 11]].

---

## Part D — Method (note 12)

**11. Get IPC on something you wrote.**
```bash
perf stat ./your_program
```
**Done when:** you can state your IPC, whether it's good for this workload, and **which counter you'd look at next** to find out why. IPC alone is not a verdict → [[foundations/computer-architecture/12-performance|note 12]].

**12. Predict, then measure, then be wrong.**
Before running exercise 6 or 9, **write down your predicted ratio.** Then measure.
**Done when:** you have a written prediction and a measurement side by side. **If you were within 20%, pick a harder experiment.** The habit this builds is the entire content of note 12 — the point is not to be right, it's to notice you weren't.

## Related
- [[foundations/computer-architecture/14-practice-exercises-solutions|Solutions]] — with measured results
- [[foundations/computer-architecture/README|the course]]
- [[foundations/gpu-and-parallel-computing/08-practice-exercises|GPU exercises]] — the same method, other hardware

*Source: [reference] — built from this course's own "what would close the gap" list. Results in note 14 measured Aug 2026.*
