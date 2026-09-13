# Module: Amortised Analysis (The Cost of a Sequence, Not an Operation)

**[Intermediate → Advanced]** — Some operations are usually cheap and occasionally catastrophic. Asking "what does one call cost?" gives an answer that is technically correct and practically useless. **Amortised analysis asks what $n$ calls cost, and divides.** This lesson gives you the three standard methods for doing that — and, just as importantly, the drill of being handed a table of operation costs and producing an amortised cost from it.

> **Read this one slowly.** It is the part of complexity analysis that interviews reach for when they want to get past "what is $O(n)$?", and it is the part most self-taught engineers have never been shown a *method* for — only the conclusion that "append is amortised $O(1)$".

---

## Before you start

- You can read $O$, $\Omega$ and $\Theta$, and you know that they describe growth rather than time — [[01-growth-and-asymptotic-notation|growth and asymptotic notation]].
- You know how a [[02-dynamic-arrays|dynamic array]] grows, and that it doubles rather than adding one slot.
- You can trace a [[07-stacks-and-queues|stack and a queue]] through a sequence of operations.
- You are comfortable with a geometric series — that $1 + 2 + 4 + \dots + 2^k$ is a little less than $2^{k+1}$.

**After this lesson you will be able to:**

1. State the difference between **worst-case**, **average-case** and **amortised** cost precisely enough to say why amortised is *not* a probabilistic claim.
2. Apply all three methods — **aggregate**, **accounting** and **potential** — to the same structure and get the same answer.
3. Take a **table of operation costs** you have never seen before and produce the amortised cost per operation, with a justification.
4. Recognise when an amortised bound **does not apply**, and name two situations where a real system cares about the worst single operation rather than the average.

**Study route:** read 1–3 in order; the three methods in 4–6 are independent of each other, so if one clicks you can skim the others and come back. Section 7 is the interview drill and section 8 is the lab. Do not skip section 3 — the average-case confusion is the one that gets punished.

---

## 1. Why this exists: a cost that is a lie in both directions

Here is a Python list, and the only operation is `append`:

```python
items = []
for i in range(1_000_000):
    items.append(i)
```

**What does `append` cost?**

Answer it as worst case and you get $O(n)$. That is genuinely true: when the list is full, `append` allocates a bigger block and copies every existing element across. On the append that takes the list from 524,288 to 524,289 elements, the interpreter really does copy half a million pointers.

So the loop above does a million appends, each costing up to $O(n)$, giving $O(n^2)$ — about $10^{12}$ operations, which would take hours.

**It takes about a tenth of a second.** The $O(n^2)$ bound is not wrong, it is *useless*: it is the result of assuming the worst case can happen every time, when in fact the worst case can only happen once every time the array doubles — and each doubling makes the next expensive operation twice as rare.

Now try to fix it by going the other way and calling `append` $O(1)$ "on average". That is *also* misleading, because it invites the reader to think a probability is involved — that you might get unlucky and hit a run of expensive appends. **You cannot.** The structure of the doubling guarantees the expensive ones are spread out. There is no unlucky input.

What is needed is a third kind of statement, and this is it:

> **Amortised cost** is the worst-case average cost per operation, taken over a worst-case *sequence* of operations. It is a guarantee, not an expectation: **any** sequence of $n$ appends costs at most $3n$ writes in total, no matter which sequence.

That sentence is the whole lesson. The three methods below are three ways of proving statements of that shape.

---

## Terms used in amortised analysis

1. **Actual cost**: This is also written $c_i$. This is what operation number $i$ genuinely costs when you run it — the real number of primitive steps. For a dynamic array append this is $1$ most of the time, and $1 + \text{size}$ on the appends that trigger a resize.
2. **Amortised cost**: This is also written $\hat{c}_i$. This is a cost you *assign* to each operation, chosen so that the assigned costs sum to at least the real costs over any sequence. It is an accounting fiction that happens to be a valid upper bound, which is exactly what makes it useful.
3. **Worst-case cost**: This is the most any single operation can cost, considered on its own. For dynamic array append it is $O(n)$, and that number is correct and nearly always the wrong thing to quote.
4. **Average-case cost**: This is the expected cost of one operation, averaged over a **probability distribution of inputs**. It requires you to assume something about how likely each input is. Quicksort's $O(n \log n)$ is average-case: it assumes the pivot is not adversarially chosen.
5. **Amortised versus average-case**: These are different in kind, not in degree. Average-case involves randomness and can be defeated by an unlucky or adversarial input. **Amortised involves no randomness at all** and cannot be defeated, because it is a statement about every possible sequence. Getting these two confused is the single most common error in this topic.
6. **Aggregate method**: This is the first of the three techniques. You compute the total cost $T(n)$ of the whole sequence directly, then declare the amortised cost to be $T(n)/n$. Every operation gets the same amortised cost.
7. **Accounting method**: This is also known as the **banker's method**. You charge each operation a fixed fee, spend part of it on the operation's real cost, and store the rest as **credit** on the data structure. Later expensive operations are paid for out of stored credit. The fee is valid if the credit balance never goes negative.
8. **Credit**: This is stored-up prepayment sitting on the structure, in the accounting method. Credit is not real — nothing in the running program corresponds to it — it is a bookkeeping device for proving the total stays bounded.
9. **Potential method**: This is the third technique, and the most general. You define a **potential function** $\Phi$ mapping the state of the structure to a number, and define the amortised cost of an operation as its actual cost plus the change in potential. Potential is the same idea as credit, expressed as a property of the state rather than as coins on individual elements.
10. **Potential function**: This is written $\Phi(D)$, where $D$ is the state of the data structure. It has to satisfy one condition: $\Phi(D_i) \ge \Phi(D_0)$ for every $i$ — the potential may never drop below where it started. If that holds, the total amortised cost is an upper bound on the total actual cost.
11. **Amortised $O(1)$**: This means that over any sequence of $n$ operations, the total cost is $O(n)$. It emphatically does **not** mean every operation is fast.

---

## 2. The three questions are about three different things

Before any method, get the axes straight. These are not three answers to one question; they are answers to three questions.

| Question | Kind of statement | Defeated by | Example |
| :--- | :--- | :--- | :--- |
| What does the **worst single** operation cost? | A guarantee about one operation | nothing | array append: $O(n)$ |
| What does an operation cost **on a typical input**? | A probabilistic expectation | an adversarial or unlucky input | quicksort: $O(n \log n)$ |
| What do **$n$ operations** cost in total, divided by $n$? | A guarantee about a sequence | nothing | array append: $O(1)$ |

**Both the first and third rows are worst-case guarantees.** They differ in what they are guaranteeing *about*: one operation, or a sequence. That is why "amortised worst-case" is not a contradiction, and why a structure can honestly be described as both $O(n)$ worst case and $O(1)$ amortised at the same time.

---

## 3. The mistake this topic exists to prevent

> **Predict before reading on.** A hash map lookup is usually described as $O(1)$ average and $O(n)$ worst case. Is it also $O(1)$ *amortised*? Answer before continuing.

**No.** And the reason is worth sitting with, because it is the cleanest illustration of the distinction.

A hash map's worst case comes from **collisions**, which depend on the keys you insert. An adversary who knows your hash function can pick $n$ keys that all collide, and then *every single lookup* is $O(n)$ — not one in a thousand, all of them. Averaging over the sequence does not help, because the whole sequence is bad. The $O(1)$ claim for hash maps is genuinely average-case: it rests on an assumption about key distribution, and that assumption is attackable. This is a real attack, not a theoretical one — hash-flooding denial of service is why Python randomises its string hash seed per process.

A dynamic array's expensive appends come from **the structure's own growth schedule**, which the caller does not control and cannot influence. There is no input that makes appends collide. That is why the array gets a true amortised guarantee and the hash map does not.

**The test:** ask whether the expensive operations are *forced to be rare by the mechanism itself*, or merely *unlikely given assumptions about the input*. Only the first gives you an amortised bound.

---

## 4. Method one — aggregate

**The idea in one line:** stop looking at individual operations, add up the whole sequence, and divide.

### Worked derivation: $n$ appends to a doubling array

Start with capacity 1. An append costs 1 write normally; on a resize it costs 1 write plus one copy per existing element.

Resizes happen when the size reaches the capacity, so at sizes $1, 2, 4, 8, \dots$ — and the resize at size $2^k$ copies $2^k$ elements. Over $n$ appends, the total copying is therefore

$$\sum_{k=0}^{\lfloor \log_2 n \rfloor} 2^k = 2^{\lfloor \log_2 n \rfloor + 1} - 1 < 2n$$

**In words: the copying done by all resizes put together is less than twice the number of appends**, because each doubling copies as much as *all previous doublings combined, plus one*. The last resize dominates, and it is bounded by $n$.

Adding the $n$ ordinary writes:

$$T(n) < n + 2n = 3n \qquad\Longrightarrow\qquad \hat{c} = \frac{T(n)}{n} < 3 = O(1)$$

The lab measures exactly this. For $n = 100{,}000$ it reports 231,071 total writes — an amortised 2.31, comfortably under 3.

**One detail worth noticing in the measurements:** the amortised cost is not monotone in $n$. The lab reports 2.023 at $n=1000$ but 2.638 at $n=10{,}000$. That is not noise. It depends on where $n$ falls relative to the last power of two: just after a doubling you have paid for a big copy and not yet amortised it away, and just before one you have not paid yet. The *bound* of 3 holds throughout; the measured ratio oscillates beneath it.

### Why the doubling matters, concretely

Replace doubling with "grow by one slot" and rerun the same argument. Now every append resizes, and the $i$-th copies $i-1$ elements:

$$T(n) = \sum_{i=1}^{n} i = \frac{n(n+1)}{2} \qquad\Longrightarrow\qquad \hat{c} = \frac{n+1}{2} = O(n)$$

The lab confirms it: at $n = 10{,}000$ the doubling array does 26,383 writes and the grow-by-one array does **50,005,000** — an amortised cost of 5,000.5 that grows with $n$ rather than staying flat.

**The geometric growth is not an implementation detail. It is the entire reason the amortised bound exists.** Any constant growth factor $> 1$ works; growth by a constant *amount* does not.

---

## 5. Method two — accounting (the banker's method)

**The idea in one line:** overcharge the cheap operations, bank the surplus, and make the expensive ones spend it.

The aggregate method needs you to sum the whole sequence, which is not always easy. The accounting method replaces that with a local invariant you can check operation by operation.

### The rules

1. Pick an amortised cost $\hat{c}_i$ for each operation — the "fee".
2. When an operation runs, it pays its real cost $c_i$ out of its fee. Any surplus becomes **credit** stored on the structure; any shortfall must be covered by existing credit.
3. **The fee schedule is valid if the credit balance never goes negative.** If it never goes negative, then $\sum \hat{c}_i \ge \sum c_i$, so the fees are a genuine upper bound on the real total.

### Worked derivation: charging 3 per append

Charge every append **3 writes**, and place the surplus as credit on the elements:

- The append does 1 write to store the new element. **2 credits left over.**
- Store those 2 credits on the element just added.

Now consider a resize when the array is full at capacity $m$. It must copy $m$ elements. Where does the money come from?

Since the last resize, the array grew from $m/2$ elements to $m$ — so **$m/2$ new elements were appended, each carrying 2 credits**. That is $m$ credits available, which is exactly the $m$ copies needed. The balance lands on zero and never goes below it.

**Why 2 credits and not 1?** Each element must pay to be copied once for *this* resize, and it must also have already paid for the elements that were sitting there before it. The clean way to see it: each new element pays 1 credit for copying itself at the next resize, and 1 credit for copying one of the older elements that has already spent its own credit. Every old element gets paired with exactly one new one, because the array doubled.

The lab checks the three candidate fees directly and the result is unambiguous:

```
  charge=1 per append -> final bank= -1023  lowest bank=  -1023  TOO LOW
  charge=2 per append -> final bank=   -23  lowest bank=   -510  TOO LOW
  charge=3 per append -> final bank=   977  lowest bank=      0  VALID
```

**A charge of 2 is not enough.** That surprises people, since the copying is "about 2n". The lowest the bank reaches under a fee of 2 is $-510$, and a proof with a negative balance is not a proof. Three is the smallest integer fee that works.

---

## 6. Method three — potential

**The idea in one line:** instead of tracking coins on elements, define a single number that measures how much trouble the current state is storing up.

This is the most powerful of the three, and the one that generalises to structures where "which element holds the credit" is not a sensible question — [[10-union-find|union-find]] and splay trees among them.

### The rules

Define a **potential function** $\Phi$ from a state of the structure to a real number. The amortised cost of the operation taking state $D_{i-1}$ to $D_i$ is

$$\hat{c}_i = c_i + \Phi(D_i) - \Phi(D_{i-1})$$

**In words: the amortised cost is what the operation actually cost, plus however much it increased the stored-up trouble.** An operation that does little work but leaves the structure closer to needing an expensive fix-up is charged for it; an operation that does a lot of work while *relieving* stored trouble gets a rebate.

Summing over the whole sequence, the middle terms telescope:

$$\sum_{i=1}^{n} \hat{c}_i = \sum_{i=1}^{n} c_i + \Phi(D_n) - \Phi(D_0)$$

**So the amortised total is an upper bound on the actual total precisely when $\Phi(D_n) \ge \Phi(D_0)$.** Note carefully what the condition is: the potential must never end below where it *started*. It is not required to be non-negative, and a good deal of confusion comes from textbooks that assume $\Phi(D_0) = 0$ and then state the condition as "$\Phi \ge 0$".

### Worked derivation: the dynamic array

Take

$$\Phi = 2 \cdot \text{size} - \text{capacity}$$

**In words: the potential is how far past the half-full mark the array has got, doubled.** It is $0$ when the array is exactly half full — that is, immediately after a resize — and it climbs to equal the capacity just as the array fills, which is exactly the amount of copying the next resize will cost.

**Case 1 — an append with no resize.** Actual cost 1. Size goes up by one, capacity unchanged, so $\Delta\Phi = 2$.

$$\hat{c} = 1 + 2 = 3$$

**Case 2 — an append that triggers a resize.** The array was full: size $= $ capacity $= m$. Actual cost is $1 + m$. Afterwards size is $m+1$ and capacity is $2m$.

$$\Phi_{\text{before}} = 2m - m = m, \qquad \Phi_{\text{after}} = 2(m+1) - 2m = 2$$
$$\hat{c} = (1 + m) + (2 - m) = 3$$

**Both cases give exactly 3.** That is the signature of a well-chosen potential function: the expensive case's actual cost is cancelled by the collapse in potential, and every operation lands on the same flat number.

The lab prints the first nine appends with both potentials and the amortised cost:

```
   append |  actual | Phi before | Phi after | amortised
        1 |       1 |         -1 |         1 |         3
        2 |       2 |          1 |         2 |         3
        3 |       3 |          2 |         2 |         3
        4 |       1 |          2 |         4 |         3
        5 |       5 |          4 |         2 |         3
```

Read the `actual` column: 1, 2, 3, 1, 5 — wildly uneven. Read the `amortised` column: 3, 3, 3, 3, 3. **Look at append 5, where the actual cost is 5: the potential drops from 4 to 2, and that $-2$ swing is what absorbs the spike.** Note also that $\Phi(D_0) = -1$ here, and the potential never returns below $-1$, so the condition holds even though $\Phi$ starts negative.

### Choosing a potential function

There is no algorithm for it, which is why this method is the hardest. The heuristic that works: **$\Phi$ should be large exactly when an expensive operation is imminent, and it should collapse when that operation happens.** If your candidate does not drop sharply on the expensive case, it will not cancel the spike, and you will not get a flat amortised cost.

---

## 7. The interview drill: from a table of costs to an amortised cost

This is the form the question usually takes, and it is mechanical once you see it. **You are given a rule for what operation $i$ costs. Sum it, divide by $n$, and take the growth rate of the result.**

Four rules, all with $n = 1024$, measured by the lab:

| Rule for the cost of operation $i$ | Total | Amortised | Worst single | Verdict |
| :--- | ---: | ---: | ---: | :--- |
| $i$ if $i$ is a power of 2, else 1 | 3,060 | 2.988 | 1024 | $O(1)$ amortised |
| $n$ on the last operation, else 1 | 2,047 | 1.999 | 1024 | $O(1)$ amortised |
| $i$ on operation $i$ | 524,800 | 512.500 | 1024 | $O(n)$ amortised |
| 100 every 100th operation, else 1 | 2,014 | 1.967 | 100 | $O(1)$ amortised |

Work the first row by hand, because it is the classic and it is the one that looks hardest:

The powers of two up to $n$ are $1, 2, 4, \dots, n$, and there are $\lfloor \log_2 n \rfloor + 1$ of them. They cost $1 + 2 + 4 + \dots + n = 2n - 1$ in total. Everything else costs 1, and there are fewer than $n$ of those. So

$$T(n) < (2n - 1) + n = 3n - 1 \qquad\Longrightarrow\qquad \hat{c} < 3 = O(1)$$

At $n = 1024$: the powers of two sum to $2047$, the remaining $1013$ operations cost $1013$, total $3060$, divided by $1024$ gives $2.988$. **The measured number matches the derivation.**

**The third row is the one to be able to spot.** Its costs also look "mostly small" if you glance at early operations, but $\sum i = n(n+1)/2$, so the amortised cost is $(n+1)/2$ — it *grows with $n$*. An amortised bound is not a magic trick that turns any uneven cost profile into $O(1)$; it turns *rare* spikes into $O(1)$. Spikes that grow steadily are not rare.

**The method, stated once:**

1. Identify which operations are expensive and **how often** they occur as a function of $n$.
2. Sum the expensive ones. Sum the cheap ones (usually just $n$).
3. Divide by $n$ and simplify.
4. If the result is a constant, it is $O(1)$ amortised. If it still contains $n$, it is not — and no averaging will fix it.

---

## 8. Worked example — complete runnable lab

Save as `amortized.py` in an empty directory. Standard library only; nothing is written to disk.

```python
"""Three methods for amortised analysis, each checked against a measured count.

Run:  python3 amortized.py
"""


# ---------------------------------------------------------------- 1. AGGREGATE
class CountingArray:
    """A dynamic array that counts the primitive writes it performs.

    One "write" is one slot assignment: either placing a new element, or
    copying an existing element into a freshly allocated block.
    """

    def __init__(self, growth="double"):
        self.slots = [None]
        self.size = 0
        self.growth = growth
        self.writes = 0          # total slot assignments so far
        self.copies = 0          # the subset of writes caused by resizing

    def append(self, value):
        cost = 1                                     # the write that stores `value`
        if self.size == len(self.slots):
            new_cap = len(self.slots) * 2 if self.growth == "double" else len(self.slots) + 1
            old = self.slots
            self.slots = [None] * new_cap
            for i in range(self.size):               # copy every existing element
                self.slots[i] = old[i]
            self.copies += self.size
            cost += self.size
        self.slots[self.size] = value
        self.size += 1
        self.writes += cost
        return cost


def aggregate_method(n):
    a = CountingArray("double")
    worst_single = 0
    for i in range(n):
        worst_single = max(worst_single, a.append(i))
    return a.writes, a.copies, worst_single


# --------------------------------------------------------------- 2. ACCOUNTING
def accounting_method(n, charge):
    """Charge a flat `charge` per append; pay real costs from the bank.

    If the bank never goes negative, the charge is a valid amortised cost:
    the total charged is an upper bound on the total real cost.
    """
    a = CountingArray("double")
    bank = 0
    min_bank = 0
    for i in range(n):
        bank += charge
        bank -= a.append(i)
        min_bank = min(min_bank, bank)
    return bank, min_bank


# ---------------------------------------------------------------- 3. POTENTIAL
def potential(a):
    """Phi = 2 * size - capacity.

    Zero right after a resize, and it climbs to `capacity` just before the next
    one -- which is exactly the amount of copying that resize will cost.
    """
    return 2 * a.size - len(a.slots)


def potential_method(n):
    a = CountingArray("double")
    worst_amortised = 0
    rows = []
    for i in range(n):
        before = potential(a)
        actual = a.append(i)
        after = potential(a)
        amortised = actual + (after - before)
        worst_amortised = max(worst_amortised, amortised)
        if i < 9:
            rows.append((i + 1, actual, before, after, amortised))
    return rows, worst_amortised


# ------------------------------------------------------------- 4. MULTIPOP
class MultipopStack:
    def __init__(self):
        self.items = []
        self.unit_ops = 0        # every individual push/pop counts as 1

    def push(self, v):
        self.items.append(v)
        self.unit_ops += 1
        return 1

    def pop(self):
        if not self.items:
            return 0
        self.items.pop()
        self.unit_ops += 1
        return 1

    def multipop(self, k):
        popped = 0
        while self.items and popped < k:
            self.items.pop()
            popped += 1
        self.unit_ops += popped
        return popped


# ------------------------------------------------------------ 5. TWO-STACK QUEUE
class TwoStackQueue:
    def __init__(self):
        self.inbox, self.outbox = [], []
        self.moves = 0

    def enqueue(self, v):
        self.inbox.append(v)

    def dequeue(self):
        cost = 0
        if not self.outbox:
            while self.inbox:
                self.outbox.append(self.inbox.pop())
                cost += 1
            self.moves += cost
        return self.outbox.pop(), cost


# ---------------------------------------------------------- 6. BINARY COUNTER
def binary_counter(n, bits=32):
    """n increments of a binary counter; count individual bit flips."""
    c = [0] * bits
    flips = 0
    worst = 0
    for _ in range(n):
        this = 0
        i = 0
        while i < bits and c[i] == 1:
            c[i] = 0
            i += 1
            this += 1
        if i < bits:
            c[i] = 1
            this += 1
        flips += this
        worst = max(worst, this)
    return flips, worst


# ------------------------------------------- 7. THE INTERVIEW DRILL: cost tables
def drill(cost_of, n, name):
    """Given a rule for the cost of operation i, report total and amortised."""
    total = sum(cost_of(i) for i in range(1, n + 1))
    worst = max(cost_of(i) for i in range(1, n + 1))
    return name, total, total / n, worst


def main():
    N = 1000

    print("=== 1. AGGREGATE: total cost of n appends, divided by n ===")
    for n in (10, 100, 1000, 10000, 100000):
        writes, copies, worst = aggregate_method(n)
        print(f"  n={n:>6}  total writes={writes:>7}  copies={copies:>6}"
              f"  worst single={worst:>6}  amortised={writes/n:.4f}")
    print("  -> a single append costs up to n, but the average over the sequence stays under 3")

    print("\n  The same array grown by ONE slot instead of doubling:")
    for n in (10, 100, 1000, 10000):
        a = CountingArray("plus-one")
        for i in range(n):
            a.append(i)
        print(f"  n={n:>6}  total writes={a.writes:>9}  amortised={a.writes/n:>9.1f}")
    print("  -> amortised cost now grows with n: the sequence is O(n^2), not O(n)")

    print("\n=== 2. ACCOUNTING: charge a flat fee, check the bank never goes negative ===")
    for charge in (1, 2, 3):
        bank, min_bank = accounting_method(N, charge)
        verdict = "VALID   " if min_bank >= 0 else "TOO LOW "
        print(f"  charge={charge} per append -> final bank={bank:>6}"
              f"  lowest bank={min_bank:>7}  {verdict}")
    print("  -> 3 is the smallest whole-number charge that never goes into debt")

    print("\n=== 3. POTENTIAL: Phi = 2*size - capacity, amortised = actual + delta-Phi ===")
    rows, worst_amortised = potential_method(N)
    print("   append |  actual | Phi before | Phi after | amortised")
    for i, actual, before, after, amortised in rows:
        print(f"   {i:>6} | {actual:>7} | {before:>10} | {after:>9} | {amortised:>9}")
    print(f"  worst amortised cost over {N} appends: {worst_amortised}")
    print("  -> the expensive appends are exactly the ones where Phi collapses and pays for them")

    print("\n=== 4. MULTIPOP: one operation can cost n, the sequence still costs O(n) ===")
    s = MultipopStack()
    biggest = 0
    for i in range(N):
        s.push(i)
    for k in (10, 100, 500, 1000):
        biggest = max(biggest, s.multipop(k))
        for i in range(k):
            s.push(i)
    print(f"  most expensive single multipop: {biggest}")
    print(f"  total unit operations across the whole sequence: {s.unit_ops}")
    print("  -> nothing can be popped that was not pushed, so total pops <= total pushes")

    print("\n=== 5. TWO-STACK QUEUE: worst dequeue is O(n), amortised is O(1) ===")
    q = TwoStackQueue()
    for i in range(N):
        q.enqueue(i)
    worst_dq = 0
    for i in range(N):
        _, cost = q.dequeue()
        worst_dq = max(worst_dq, cost)
    print(f"  worst single dequeue moved {worst_dq} elements")
    print(f"  total elements moved across all {N} dequeues: {q.moves}")
    print(f"  amortised moves per dequeue: {q.moves / N:.4f}")
    print("  -> each element is moved from inbox to outbox exactly once, ever")

    print("\n=== 6. BINARY COUNTER: n increments, total bit flips < 2n ===")
    for n in (16, 256, 4096, 65536):
        flips, worst = binary_counter(n)
        print(f"  n={n:>6}  total flips={flips:>7}  worst single increment={worst:>3}"
              f"  amortised={flips/n:.4f}")
    print("  -> bit 0 flips every time, bit 1 every second time, bit k every 2^k times")

    print("\n=== 7. THE DRILL: given a cost rule, produce the amortised cost ===")
    n = 1024
    cases = [
        (lambda i: i if (i & (i - 1)) == 0 else 1, "cost i if i is a power of 2, else 1"),
        (lambda i: n if i == n else 1, "cost n on the last operation, else 1"),
        (lambda i: i, "cost i on operation i"),
        (lambda i: 100 if i % 100 == 0 else 1, "cost 100 every 100th operation, else 1"),
    ]
    print(f"  (n = {n} operations)")
    print("   rule                                     |    total | amortised |  worst")
    for cost_of, name in cases:
        _, total, amort, worst = drill(cost_of, n, name)
        print(f"   {name:<40} | {total:>8} | {amort:>9.3f} | {worst:>6}")
    print("  -> rows 1, 2 and 4 are O(1) amortised; row 3 is O(n) amortised and no")
    print("     amount of averaging rescues it")


if __name__ == "__main__":
    main()
```

### Expected output

Generated by running the file above, not reconstructed:

```
=== 1. AGGREGATE: total cost of n appends, divided by n ===
  n=    10  total writes=     25  copies=    15  worst single=     9  amortised=2.5000
  n=   100  total writes=    227  copies=   127  worst single=    65  amortised=2.2700
  n=  1000  total writes=   2023  copies=  1023  worst single=   513  amortised=2.0230
  n= 10000  total writes=  26383  copies= 16383  worst single=  8193  amortised=2.6383
  n=100000  total writes= 231071  copies=131071  worst single= 65537  amortised=2.3107
  -> a single append costs up to n, but the average over the sequence stays under 3

  The same array grown by ONE slot instead of doubling:
  n=    10  total writes=       55  amortised=      5.5
  n=   100  total writes=     5050  amortised=     50.5
  n=  1000  total writes=   500500  amortised=    500.5
  n= 10000  total writes= 50005000  amortised=   5000.5
  -> amortised cost now grows with n: the sequence is O(n^2), not O(n)

=== 2. ACCOUNTING: charge a flat fee, check the bank never goes negative ===
  charge=1 per append -> final bank= -1023  lowest bank=  -1023  TOO LOW 
  charge=2 per append -> final bank=   -23  lowest bank=   -510  TOO LOW 
  charge=3 per append -> final bank=   977  lowest bank=      0  VALID   
  -> 3 is the smallest whole-number charge that never goes into debt

=== 3. POTENTIAL: Phi = 2*size - capacity, amortised = actual + delta-Phi ===
   append |  actual | Phi before | Phi after | amortised
        1 |       1 |         -1 |         1 |         3
        2 |       2 |          1 |         2 |         3
        3 |       3 |          2 |         2 |         3
        4 |       1 |          2 |         4 |         3
        5 |       5 |          4 |         2 |         3
        6 |       1 |          2 |         4 |         3
        7 |       1 |          4 |         6 |         3
        8 |       1 |          6 |         8 |         3
        9 |       9 |          8 |         2 |         3
  worst amortised cost over 1000 appends: 3
  -> the expensive appends are exactly the ones where Phi collapses and pays for them

=== 4. MULTIPOP: one operation can cost n, the sequence still costs O(n) ===
  most expensive single multipop: 1000
  total unit operations across the whole sequence: 4220
  -> nothing can be popped that was not pushed, so total pops <= total pushes

=== 5. TWO-STACK QUEUE: worst dequeue is O(n), amortised is O(1) ===
  worst single dequeue moved 1000 elements
  total elements moved across all 1000 dequeues: 1000
  amortised moves per dequeue: 1.0000
  -> each element is moved from inbox to outbox exactly once, ever

=== 6. BINARY COUNTER: n increments, total bit flips < 2n ===
  n=    16  total flips=     31  worst single increment=  5  amortised=1.9375
  n=   256  total flips=    511  worst single increment=  9  amortised=1.9961
  n=  4096  total flips=   8191  worst single increment= 13  amortised=1.9998
  n= 65536  total flips= 131071  worst single increment= 17  amortised=2.0000
  -> bit 0 flips every time, bit 1 every second time, bit k every 2^k times

=== 7. THE DRILL: given a cost rule, produce the amortised cost ===
  (n = 1024 operations)
   rule                                     |    total | amortised |  worst
   cost i if i is a power of 2, else 1      |     3060 |     2.988 |   1024
   cost n on the last operation, else 1     |     2047 |     1.999 |   1024
   cost i on operation i                    |   524800 |   512.500 |   1024
   cost 100 every 100th operation, else 1   |     2014 |     1.967 |    100
  -> rows 1, 2 and 4 are O(1) amortised; row 3 is O(n) amortised and no
     amount of averaging rescues it
```

---

## 9. The catalogue: the structures you are expected to know

Five results come up repeatedly. For each, the point is not the number but **the argument that produces it**.

### Dynamic array append — amortised $O(1)$

Covered above by all three methods. **The argument:** doubling makes each resize twice as rare as it is expensive.

### Stack with multipop — amortised $O(1)$

A stack supporting `push`, `pop`, and `multipop(k)` which pops the top $k$ items (or everything, if fewer remain). A single `multipop` costs up to $n$.

**The argument is the cleanest in the subject: nothing can be popped that was not first pushed.** Over a sequence of $n$ operations there are at most $n$ pushes, so there are at most $n$ pops in total, however they are grouped. Total cost $\le 2n$, amortised $O(1)$.

In accounting terms: charge 2 per push — one for the push, one prepaid for the eventual pop. `pop` and `multipop` are then free, spending credit the pushes already deposited.

The lab confirms the shape: a single multipop removes 1,000 items, yet the whole sequence of 1,000 pushes plus four multipop-and-refill rounds costs only 4,220 unit operations.

### Queue from two stacks — amortised $O(1)$

`enqueue` pushes onto an inbox stack. `dequeue` pops from an outbox stack; if the outbox is empty, it first moves every element from inbox to outbox, reversing them.

A single `dequeue` can cost $O(n)$. But **each element is moved from inbox to outbox exactly once in its entire lifetime** — once it is in the outbox it is never moved back. So $n$ elements cause at most $n$ moves across the whole sequence.

The lab's numbers say it precisely: worst single dequeue moves 1,000 elements, total moves across all 1,000 dequeues is **1,000**, amortised exactly 1.0.

### Binary counter increment — amortised $O(1)$

Incrementing a binary counter flips a run of trailing 1s to 0 and then one 0 to 1. A single increment on `0111111111` flips ten bits.

**The argument:** bit 0 flips on every increment, bit 1 on every second, bit $k$ on every $2^k$-th. Total flips over $n$ increments:

$$\sum_{k \ge 0} \left\lfloor \frac{n}{2^k} \right\rfloor < n \sum_{k \ge 0} \frac{1}{2^k} = 2n$$

**In words: the total number of bit flips is less than twice the number of increments**, because each higher bit flips half as often as the one below it. The lab shows the ratio converging on 2 from below — 1.9375, 1.9961, 1.9998, 2.0000 — while the worst single increment grows as $\log n$.

### Union-find with path compression and union by rank — amortised $O(\alpha(n))$

The one that genuinely needs the potential method. A single `find` can walk a long chain; path compression then flattens that chain so it is never walked again. The amortised bound is $O(\alpha(n))$, where $\alpha$ is the inverse Ackermann function — below 5 for any $n$ that fits in the observable universe, hence "effectively constant".

**You are not expected to reproduce this proof.** You are expected to say *why it needs amortisation*: the expensive `find` operations are the ones that do the work of making future finds cheap, so their cost is an investment, and only a sequence-level analysis can see that. See [[10-union-find|union-find]].

---

## 10. When the amortised bound is the wrong answer

An amortised guarantee says nothing about *when* the expensive operation lands, and there are systems where that is the only thing that matters.

1. **Real-time and interactive systems.** A game rendering at 60 frames per second has 16 milliseconds per frame. "Amortised $O(1)$" is no comfort if one frame in five hundred triggers a resize that blows the budget and drops a frame visibly. The fix is usually to preallocate — `reserve(n)` — so the resize happens once, at a moment you choose.
2. **Latency percentiles in services.** An amortised bound describes the mean. Your p99 latency is precisely the expensive operations you amortised away. A structure with worst-case $O(\log n)$ can beat one with amortised $O(1)$ on p99 while losing on throughput.
3. **Adversarial settings.** If an attacker can choose *when* to trigger the expensive operation and can force it repeatedly, check whether the bound really is amortised or merely average-case. See section 3 — that difference is the whole of hash-flooding.
4. **A single operation in isolation.** If your program does exactly one `append` to a large array, the amortised bound does not apply to it. Amortisation is a statement about sequences; there is no sequence.

**The honest summary:** amortised $O(1)$ is the right answer for throughput and the wrong answer for latency.

---

## 11. Common pitfalls and traps

1. **Saying "amortised" when you mean "average-case".** These are different claims with different strengths. Amortised holds for every sequence; average-case holds under an assumption about inputs. Quicksort is average-case $O(n\log n)$ and is *not* amortised anything — running it a thousand times does not make a sorted-input run cheaper.
2. **Believing the amortised cost bounds a single operation.** It does not, and this is the whole point of the concept. An append is $O(n)$ worst case whatever its amortised cost is.
3. **Assuming any uneven cost profile amortises to $O(1)$.** Row 3 of the drill table costs $i$ on operation $i$ and amortises to $(n+1)/2$. Check the sum; do not pattern-match on "mostly cheap".
4. **Using a growth factor that is not a factor.** Growing by 1, or by 100, or by any fixed *amount*, gives $O(n)$ amortised. It must be multiplicative. The lab demonstrates the collapse: 50,005,000 writes against 26,383.
5. **Requiring $\Phi \ge 0$ instead of $\Phi(D_i) \ge \Phi(D_0)$.** The actual condition is about the starting value. The lab's potential starts at $-1$ and the analysis is still valid.
6. **Forgetting that credit is fictional.** There is no field in the struct holding credits. If your argument depends on reading the credit balance at runtime, it is not an amortised analysis.
7. **Amortising across operations that a caller can interleave badly.** The dynamic-array bound assumes you only append. Add a `pop` that *shrinks* the array as soon as the size falls **to** half the capacity, and an adversary can sit exactly on that boundary, forcing a resize on every single operation — $O(n)$ per operation forever. The standard fix is to shrink only at one quarter full, leaving a hysteresis gap, which restores the amortised bound.

**Pitfall 7 is worth more than a line.** It is the one that shows you understand the mechanism rather than the conclusion, and "when does the amortised bound break?" is a natural follow-up question after "what is the amortised cost?".

---

## 12. Check your understanding

Attempt each before opening it.

1. **A structure's operation is $O(n)$ worst case and $O(1)$ amortised. Is that a contradiction?**
   <details><summary>Answer</summary>No. They are statements about different things: the first about the most expensive single operation, the second about the total over a sequence divided by its length. Both are worst-case guarantees — neither involves probability. Dynamic array append is exactly this.</details>

2. **You charge 2 credits per append instead of 3. Where does the argument fail?**
   <details><summary>Answer</summary>The bank goes negative. Each new element can then prepay only its own future copy, with nothing left over for the older elements that have already spent their credit — but a resize at capacity $m$ must copy all $m$ elements while only $m/2$ of them were added since the last resize. The lab measures the shortfall: the lowest balance reaches $-510$ over 1,000 appends.</details>

3. **Operation $i$ costs $\sqrt{i}$. What is the amortised cost?**
   <details><summary>Answer</summary>$\sum_{i=1}^{n}\sqrt{i} \approx \frac{2}{3}n^{3/2}$, so the amortised cost is about $\frac{2}{3}\sqrt{n}$ — that is $O(\sqrt{n})$, not $O(1)$. The costs grow steadily rather than spiking rarely, so there is nothing to amortise. Compare row 3 of the drill table.</details>

4. **Why can't the $O(1)$ average-case claim for hash map lookup be upgraded to an amortised claim?**
   <details><summary>Answer</summary>Because its expensive case is caused by the input, not by the structure's own schedule. An adversary choosing colliding keys makes <i>every</i> lookup expensive, so the sequence total is $O(n^2)$ and there is no sequence-level bound to recover. The dynamic array has no such input, because the caller cannot influence when resizes occur.</details>

5. **A dynamic array halves its capacity as soon as its size falls to half the capacity. Give a sequence of $n$ operations costing $\Theta(n)$ each.**
   <details><summary>Answer</summary>Fill it to exactly capacity $m$, then alternate append, pop, append, pop. The append pushes the size to $m+1$ and doubles the capacity to $2m$ — copying $m$ elements. The pop drops the size back to $m$, which is exactly half of $2m$, so the shrink triggers and halves back to $m$ — copying $m$ elements again. Every operation resizes, giving $\Theta(n)$ each and $\Theta(n^2)$ overall; a 12-operation trace costs 108 against 20 for the same sequence without the thrash. Note the boundary matters: shrinking on <i>strictly</i> below half would not thrash here. The robust fix is hysteresis — shrink only at one quarter full, so a resize in either direction leaves the size far from both thresholds.</details>

6. **What condition must a potential function satisfy, exactly?**
   <details><summary>Answer</summary>$\Phi(D_i) \ge \Phi(D_0)$ for every $i$ — the potential may never fall below its starting value. Not "$\Phi \ge 0$": that is only the common special case where $\Phi(D_0)=0$. The condition is what makes $\sum \hat{c}_i \ge \sum c_i$ after the telescoping sum.</details>

---

## 13. Practice — independent task

Implement and analyse a **binary counter with a reset**, then prove your bound three ways.

**The structure.** A counter over `bits` bits supporting:

- `increment()` — the usual binary increment; cost is the number of bits flipped.
- `reset()` — set the counter to zero; cost is the number of bits that were 1 (you clear only those, tracking the highest set bit).

**Part 1 — measure.** Implement it with a cost counter. Run $n = 10^5$ random operations where `reset` occurs with probability $p$, for $p \in \{0, 0.001, 0.01, 0.1\}$. Report total cost and cost per operation for each.

**Part 2 — aggregate.** Derive the total cost of $n$ operations by hand. Your derivation must explain why `reset` does not break the $O(1)$ amortised bound even though a single reset can cost $\log n$.

**Part 3 — accounting.** Find the smallest whole-number charge per `increment` that keeps the bank non-negative for every sequence, with `reset` charged 0. Verify it empirically the way the lab does: track the balance and assert it never goes negative across at least 10,000 random sequences.

**Part 4 — potential.** Define $\Phi$ and show that both operations have $O(1)$ amortised cost. *Hint if you need one, after attempting:* the natural potential is the number of 1 bits currently set.

**Edge cases:** $n = 0$; `reset` on an already-zero counter; two resets in a row; overflow past `bits`, which you should define a behaviour for and state.

**Done when:** your three derivations agree with each other **and** with the measured numbers from part 1; your accounting charge is the smallest that works, demonstrated by showing the next-smallest one going negative; and you can state in one sentence why the answer would change if `reset` cost `bits` rather than the number of set bits.

Then apply it: [[02-dynamic-arrays|dynamic arrays]] and [[10-union-find|union-find]] are the two structures in this course whose headline complexity is amortised, and both notes will read differently now.

---

## Before moving on

You can distinguish worst-case, average-case and amortised precisely; apply the aggregate, accounting and potential methods to the same structure and get the same constant; take an unfamiliar table of operation costs and produce an amortised cost with a derivation; and say when an amortised bound is the wrong thing to care about.

**Recap:** amortised cost is the total over a sequence divided by its length, and it is a **worst-case guarantee with no probability in it** — which is what separates it from average-case. The **aggregate** method sums the sequence and divides. The **accounting** method charges a flat fee and requires the credit balance never to go negative; for a doubling array that fee is 3, and 2 is provably too low. The **potential** method sets $\hat{c}_i = c_i + \Delta\Phi$, needs only $\Phi(D_i) \ge \Phi(D_0)$, and for the doubling array $\Phi = 2\cdot\text{size} - \text{capacity}$ gives a flat 3 in both cases. The results to know: array append, multipop, two-stack queue and binary counter are all amortised $O(1)$; union-find is $O(\alpha(n))$. Geometric growth is what makes the bound exist — growth by a constant amount gives $O(n)$. And an amortised bound describes throughput, not latency.

**Next:** [[01-recursion-fundamentals|Recursion]] — the other half of "how do I cost this?", where the cost of a call depends on the cost of the calls it makes.

---

## Related

- [[01-growth-and-asymptotic-notation|Growth and Asymptotic Notation]] — the $O$, $\Omega$, $\Theta$ vocabulary this is written in
- [[01-complexity-analysis/index|the complexity analysis folder]] — the parent folder and reading route
- [[02-dynamic-arrays|Dynamic Arrays]] — the structure analysed here, from the implementation side
- [[07-stacks-and-queues|Stacks and Queues]] — multipop and the two-stack queue
- [[10-union-find|Union-Find]] — the $O(\alpha(n))$ result that only a potential argument can reach
- [[03-hash-maps|Hash Maps]] — the contrast case: average-case, not amortised
