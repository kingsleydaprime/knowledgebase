# Recursion and the Call Stack

> **[Beginner → Intermediate]** · A function that calls itself, why it doesn't run forever, and the piece of machinery that makes it work — which also explains a lot of error messages.

**Recursion is a function calling itself.** It sounds circular and useless. It's one of the most powerful ideas in programming, and it's the natural way to handle anything with a nested or self-similar shape.

```python
def countdown(n):
    if n <= 0:              # base case — stop
        print("Liftoff!")
        return
    print(n)
    countdown(n - 1)        # recursive case — call itself, smaller
```

`countdown(3)` prints 3, 2, 1, Liftoff.

## The two parts, and both are mandatory

**The base case** — the condition where it stops calling itself and just returns.
**The recursive case** — where it calls itself with an input that has moved *closer to the base case*.

**Omit the base case and it never stops.** But unlike an infinite loop, which merely hangs, this one crashes — and understanding why requires the call stack.

## The call stack

When any function is called, the machine has to remember where to come back to. It does this on **the stack**: a region of memory where each active call gets a **stack frame** holding its arguments, its local variables, and the return address.

Call a function → a frame is **pushed**. It returns → the frame is **popped**. **Last in, first out**, always.

```
main()
  └─ processOrder()
       └─ calculateTax()      ← currently running, on top

stack:  [ main | processOrder | calculateTax ]
                                    ↑ pops first
```

This is not an abstraction invented for teaching — it's how the CPU actually works, with a register pointing at the top of the stack. → [[foundations/computer-architecture/04-assembly|assembly]] and [[foundations/os/02-processes-and-threads|processes and threads]].

Now recursion is unmysterious. `countdown(3)` produces:

```
countdown(3)  → prints 3, calls
  countdown(2)  → prints 2, calls
    countdown(1)  → prints 1, calls
      countdown(0)  → base case, prints Liftoff, returns
    returns
  returns
returns
```

Four frames at the deepest point, then they unwind.

**And the missing base case becomes obvious: frames are pushed and never popped until the stack runs out of memory.** That's a **stack overflow** — an actual, physical limit, typically a few thousand frames deep. The error is telling you precisely what happened.

## Working through one that returns a value

```python
def factorial(n):
    if n <= 1:
        return 1              # base case
    return n * factorial(n - 1)
```

`factorial(4)`:

```
factorial(4) → 4 * factorial(3)      ← waits
factorial(3) → 3 * factorial(2)      ← waits
factorial(2) → 2 * factorial(1)      ← waits
factorial(1) → 1                     ← base case, returns
```
then unwinding: `2 * 1 = 2` → `3 * 2 = 6` → `4 * 6 = 24`.

**The thing to notice: each call is suspended mid-expression, waiting for the one below it.** That's the frame doing its job — holding `n` and the fact that a multiplication is still pending.

**Trace one on paper.** This is genuinely the moment recursion stops being confusing, and it doesn't happen from reading.

## When recursion is the right tool

Not for counting down — a loop is clearer. Recursion earns its place when **the problem contains smaller versions of itself.**

**Trees and hierarchies.** A folder contains files and folders; each of those contains files and folders. Iterating that is fiddly; recursing it is four lines. The same applies to a DOM tree, a JSON document, an org chart, a comment thread.

```python
def total_size(folder):
    total = 0
    for item in folder:
        if is_file(item):
            total += size(item)
        else:
            total += total_size(item)      # a folder is just a smaller problem
    return total
```

**Divide and conquer.** Split in half, solve each half, combine. [[foundations/dsa/05-algorithms/04-sorting|Binary search, merge sort, quicksort]] are all this shape — and the reason binary search is O(log n) is that each call discards half the remaining data.

**Anything defined recursively.** Parsing nested expressions, walking a graph, generating permutations.

**The rule of thumb:** if you're reaching for a stack, or nesting loops to an unknown depth, recursion is probably the honest shape. If a `for` loop expresses it clearly, use the loop.

## The costs

**Every call has overhead** — pushing a frame, jumping, returning. A recursive solution is usually slower than the equivalent loop.

**Depth is bounded.** Python defaults to about 1,000 frames. Recursing over a million-item list will crash where a loop wouldn't.

**Naive recursion can be catastrophically wasteful.** The famous case:

```python
def fib(n):
    if n <= 1: return n
    return fib(n - 1) + fib(n - 2)
```

`fib(5)` computes `fib(3)` twice, `fib(2)` three times. The work grows **exponentially** — `fib(50)` is billions of calls and will not finish. The fix is **memoisation**: cache each result the first time, and the same function runs in linear time. That single change is the entry point to [[foundations/dsa/README|dynamic programming]].

**Some languages optimise a special case.** If the recursive call is the *last* thing a function does (**tail recursion**), the current frame isn't needed any more and can be reused, making it as cheap as a loop. Scheme, Haskell and Scala guarantee this; **Python and Java deliberately don't**, so don't rely on it unless you know your language does it.

## The other things the stack explains

Understanding the stack pays off well beyond recursion:

**Stack traces.** The list of frames printed when something crashes, innermost first. It's a literal snapshot of the stack at the moment of failure — read from the top for *where*, and downward for *how you got there*. Learning to read these properly is one of the highest-return debugging skills → [[foundations/programming-fundamentals/10-errors-and-debugging|note 10]].

**Stack vs heap.** Local variables and frames live on the **stack** — fast, automatically freed on return, limited in size. Larger and longer-lived data lives on the **heap** — flexible, and either garbage-collected or freed by you. This is why returning a pointer to a local variable is a classic C bug: the frame is gone → [[languages/04-c/README|C]] and [[foundations/os/05-memory-allocation|memory allocation]].

**Each thread gets its own stack**, which is part of why threads are cheaper than processes and why deep recursion in many threads exhausts memory quickly → [[foundations/os/02-processes-and-threads|threads]].

## Related
- [[foundations/programming-fundamentals/08-functions|functions]] — the prerequisite
- [[foundations/dsa/05-algorithms/01-algorithms|algorithms]] — where recursion becomes the default tool
- [[foundations/os/05-memory-allocation|memory allocation]] — stack and heap properly
- [[foundations/computer-architecture/04-assembly|assembly]] — the stack as the hardware sees it
- [[foundations/discrete-math/05-induction-and-recursion|induction and recursion]] — the maths of why base cases work

*Source: [reference] — from the freeCodeCamp Introduction to Programming course, extended with the frame-level model, tail calls and the memoisation case.*
