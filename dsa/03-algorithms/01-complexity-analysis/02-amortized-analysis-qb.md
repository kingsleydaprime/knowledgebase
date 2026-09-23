# Amortized Analysis — Question Bank

Micro-questions over [[02-amortized-analysis|the amortised analysis module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The lie in both directions

**1. A million `append`s, each $O(n)$ worst case. What does that predict, and what actually happens?**

<details><summary>Answer</summary>

It predicts $O(n^2)$ — about $10^{12}$ operations, hours of work. **It takes about a tenth of a second.**

</details>

**2. Is the $O(n^2)$ bound wrong?**

<details><summary>Answer</summary>

No — it is **useless**. It assumes the worst case can happen every time, when it can only happen once per doubling, and each doubling makes the next expensive operation twice as rare.

</details>

**3. Why is "$O(1)$ on average" also misleading here?**

<details><summary>Answer</summary>

It invites the reader to think a probability is involved — that you might get unlucky. **You cannot.** The doubling structure guarantees the expensive ones are spread out. There is no unlucky input.

</details>

**4. Define amortised cost.**

<details><summary>Answer</summary>

**The worst-case average cost per operation, taken over a worst-case *sequence* of operations.** It is a guarantee, not an expectation: any sequence of $n$ appends costs at most $3n$ writes in total, no matter which sequence.

</details>

---

## B. The vocabulary

**5. What is actual cost $c_i$?**

<details><summary>Answer</summary>

What operation $i$ genuinely costs when you run it — the real number of primitive steps. For an append: 1 usually, $1 + \text{size}$ on a resize.

</details>

**6. What is amortised cost $\hat{c}_i$?**

<details><summary>Answer</summary>

A cost you **assign** to each operation, chosen so the assigned costs sum to at least the real costs over any sequence. **An accounting fiction that happens to be a valid upper bound.**

</details>

**7. What is average-case cost, and what does it require?**

<details><summary>Answer</summary>

The expected cost of one operation over a **probability distribution of inputs**. It requires an assumption about how likely each input is — quicksort's $O(n\log n)$ assumes the pivot is not adversarially chosen.

</details>

**8. How do amortised and average-case differ?**

<details><summary>Answer</summary>

**In kind, not degree.** Average-case involves randomness and can be defeated by an adversarial input. **Amortised involves no randomness at all** and cannot be defeated, because it is a statement about every possible sequence.

</details>

**9. What does amortised $O(1)$ emphatically not mean?**

<details><summary>Answer</summary>

**That every operation is fast.** It means only that over any sequence of $n$ operations, the total is $O(n)$.

</details>

---

## C. The three questions

**10. Lay out the three questions as a table.**

<details><summary>Answer</summary>

| Question | Kind | Defeated by | Example |
| :--- | :--- | :--- | :--- |
| Worst **single** operation? | guarantee about one op | nothing | append $O(n)$ |
| Cost on a **typical input**? | probabilistic expectation | adversarial input | quicksort $O(n\log n)$ |
| $n$ operations total ÷ $n$? | guarantee about a sequence | nothing | append $O(1)$ |

</details>

**11. Why is "amortised worst-case" not a contradiction?**

<details><summary>Answer</summary>

Both the first and third rows are **worst-case guarantees**. They differ in what they guarantee *about*: one operation, or a sequence. So a structure can honestly be $O(n)$ worst case and $O(1)$ amortised at once.

</details>

---

## D. The mistake this prevents

**12. A hash map is $O(1)$ average and $O(n)$ worst case. Is it $O(1)$ amortised?**

<details><summary>Answer</summary>

**No.**

</details>

**13. Why not?**

<details><summary>Answer</summary>

Its worst case comes from **collisions, which depend on the keys you insert**. An adversary can pick $n$ colliding keys, and then *every single lookup* is $O(n)$ — not one in a thousand, all of them. Averaging over the sequence does not help because the whole sequence is bad.

</details>

**14. Why does the dynamic array get a genuine amortised bound?**

<details><summary>Answer</summary>

Its expensive appends come from **the structure's own growth schedule**, which the caller cannot influence. There is no input that makes appends collide.

</details>

**15. State the test.**

<details><summary>Answer</summary>

Ask whether the expensive operations are **forced to be rare by the mechanism itself**, or merely **unlikely given assumptions about the input**. Only the first gives an amortised bound.

</details>

---

## E. The aggregate method

**16. State the idea in one line.**

<details><summary>Answer</summary>

Stop looking at individual operations, add up the whole sequence, and divide.

</details>

**17. Derive the total copying for $n$ appends to a doubling array.**

<details><summary>Answer</summary>

Resizes happen at sizes $1, 2, 4, \dots$, and the resize at $2^k$ copies $2^k$:
$$\sum_{k=0}^{\lfloor\log_2 n\rfloor} 2^k = 2^{\lfloor\log_2 n\rfloor+1} - 1 < 2n$$

</details>

**18. Say that in words.**

<details><summary>Answer</summary>

**All the resizes put together copy less than twice the number of appends**, because each doubling copies as much as all previous doublings combined plus one. The last resize dominates, and it is bounded by $n$.

</details>

**19. Finish the derivation.**

<details><summary>Answer</summary>

$T(n) < n + 2n = 3n$, so $\hat{c} = T(n)/n < 3 = O(1)$.

</details>

**20. Why is the measured amortised cost not monotone in $n$?**

<details><summary>Answer</summary>

It depends where $n$ falls relative to the last power of two — just after a doubling you have paid for a big copy and not yet amortised it away; just before one you have not paid yet. **The bound of 3 holds throughout; the measured ratio oscillates beneath it.**

</details>

**21. Redo the argument for "grow by one slot".**

<details><summary>Answer</summary>

Every append resizes, and the $i$-th copies $i-1$:
$$T(n) = \sum_{i=1}^{n} i = \frac{n(n+1)}{2}, \qquad \hat{c} = \frac{n+1}{2} = O(n)$$
Measured: 50,005,000 writes versus 26,383 for doubling at $n = 10{,}000$.

</details>

**22. State the conclusion about growth.**

<details><summary>Answer</summary>

**Geometric growth is not an implementation detail — it is the entire reason the amortised bound exists.** Any constant *factor* $> 1$ works; growth by a constant *amount* does not.

</details>

---

## F. The accounting (banker's) method

**23. State the idea in one line.**

<details><summary>Answer</summary>

Overcharge the cheap operations, bank the surplus, and make the expensive ones spend it.

</details>

**24. Give the three rules.**

<details><summary>Answer</summary>

1. Pick an amortised cost (fee) per operation.
2. Each operation pays its real cost from its fee; surplus becomes **credit**, shortfall must come from existing credit.
3. **The schedule is valid iff the credit balance never goes negative** — then $\sum\hat c_i \ge \sum c_i$.

</details>

**25. Work the "charge 3 per append" argument.**

<details><summary>Answer</summary>

1 write stores the element, leaving **2 credits** on it. At a resize with capacity $m$, the array grew from $m/2$ to $m$ — so $m/2$ new elements each carry 2 credits, giving exactly $m$ credits for the $m$ copies. The balance lands on zero and never goes below.

</details>

**26. Why 2 credits and not 1?**

<details><summary>Answer</summary>

Each new element pays **1 credit to copy itself** at the next resize, and **1 credit to copy an older element** that has already spent its own. Every old element pairs with exactly one new one, because the array doubled.

</details>

**27. Why is a fee of 2 not enough?**

<details><summary>Answer</summary>

The bank reaches $-510$ in the lab, and **a proof with a negative balance is not a proof**. Three is the smallest integer fee that works — which surprises people, since the copying is "about $2n$".

</details>

---

## G. The potential method

**28. State the idea in one line.**

<details><summary>Answer</summary>

Instead of tracking coins on elements, define a single number measuring **how much trouble the current state is storing up**.

</details>

**29. Give the definition of amortised cost in this method.**

<details><summary>Answer</summary>

$$\hat c_i = c_i + \Phi(D_i) - \Phi(D_{i-1})$$

The actual cost plus however much the operation increased the stored-up trouble.

</details>

**30. Why does the sum telescope, and what does that give?**

<details><summary>Answer</summary>

$$\sum \hat c_i = \sum c_i + \Phi(D_n) - \Phi(D_0)$$

So the amortised total bounds the actual total **precisely when $\Phi(D_n) \ge \Phi(D_0)$**.

</details>

**31. What is the condition on $\Phi$, and what do textbooks get wrong?**

<details><summary>Answer</summary>

The potential must never end below **where it started** — not "$\Phi \ge 0$". That confusion comes from textbooks assuming $\Phi(D_0) = 0$.

</details>

**32. Give the dynamic array potential function and say what it means.**

<details><summary>Answer</summary>

$$\Phi = 2 \cdot \text{size} - \text{capacity}$$

**How far past the half-full mark the array has got, doubled.** It is 0 immediately after a resize and climbs to equal the capacity just as the array fills — exactly what the next resize will cost.

</details>

**33. Work case 1: an append with no resize.**

<details><summary>Answer</summary>

Actual cost 1; size $+1$, capacity unchanged, so $\Delta\Phi = 2$. $\hat c = 1 + 2 = 3$.

</details>

**34. Work case 2: an append that triggers a resize.**

<details><summary>Answer</summary>

Size = capacity = $m$, actual cost $1+m$. $\Phi_{\text{before}} = m$, $\Phi_{\text{after}} = 2(m+1) - 2m = 2$.
$$\hat c = (1+m) + (2-m) = 3$$

</details>

**35. What is the signature of a well-chosen potential?**

<details><summary>Answer</summary>

**Both cases give exactly the same flat number.** The expensive case's actual cost is cancelled by the collapse in potential.

</details>

**36. Give the heuristic for choosing $\Phi$.**

<details><summary>Answer</summary>

**$\Phi$ should be large exactly when an expensive operation is imminent, and collapse when it happens.** If it does not drop sharply on the expensive case, it will not cancel the spike.

</details>

---

## H. The interview drill

**37. State the four-step method.**

<details><summary>Answer</summary>

1. Identify which operations are expensive and **how often** they occur as a function of $n$.
2. Sum the expensive ones; sum the cheap ones (usually just $n$).
3. Divide by $n$ and simplify.
4. Constant → $O(1)$ amortised. Still contains $n$ → it is not, and no averaging will fix it.

</details>

**38. Cost is $i$ if $i$ is a power of 2, else 1. Derive the amortised cost.**

<details><summary>Answer</summary>

Powers of two up to $n$ sum to $2n - 1$; the rest cost fewer than $n$. So $T(n) < 3n - 1$ and $\hat c < 3 = O(1)$. At $n = 1024$: $2047 + 1013 = 3060$, $/1024 = 2.988$.

</details>

**39. Cost is $i$ on operation $i$. What is the amortised cost, and what is the lesson?**

<details><summary>Answer</summary>

$\sum i = n(n+1)/2$, so $\hat c = (n+1)/2$ — **it grows with $n$**. The lesson: an amortised bound turns *rare* spikes into $O(1)$; **spikes that grow steadily are not rare.**

</details>

---

## I. The catalogue

**40. Stack with multipop — what is the argument?**

<details><summary>Answer</summary>

**Nothing can be popped that was not first pushed.** At most $n$ pushes means at most $n$ pops however they are grouped. Total $\le 2n$, amortised $O(1)$. In accounting terms: charge 2 per push, and pops are free.

</details>

**41. Queue from two stacks — what is the argument?**

<details><summary>Answer</summary>

**Each element moves from inbox to outbox exactly once in its lifetime** — once in the outbox it is never moved back. So $n$ elements cause at most $n$ moves. The lab measures amortised exactly 1.0.

</details>

**42. Binary counter increment — derive the bound.**

<details><summary>Answer</summary>

Bit 0 flips every increment, bit 1 every second, bit $k$ every $2^k$-th:
$$\sum_{k\ge0}\left\lfloor \frac{n}{2^k}\right\rfloor < n\sum_{k\ge0}\frac{1}{2^k} = 2n$$
**Total flips are less than twice the number of increments**, because each higher bit flips half as often as the one below.

</details>

**43. Why does union-find genuinely need the potential method?**

<details><summary>Answer</summary>

Because the **expensive `find` operations are the ones doing the work of making future finds cheap** — their cost is an investment, and only a sequence-level analysis can see that.

</details>

---

## J. When it is the wrong answer

**44. Why is amortised $O(1)$ no comfort at 60fps?**

<details><summary>Answer</summary>

A frame has 16ms. One frame in five hundred triggering a resize **drops a frame visibly**. The fix is to preallocate — `reserve(n)` — so the resize happens once, at a moment you choose.

</details>

**45. What does an amortised bound do to your p99?**

<details><summary>Answer</summary>

**Your p99 latency is precisely the expensive operations you amortised away.** A structure with worst-case $O(\log n)$ can beat one with amortised $O(1)$ on p99 while losing on throughput.

</details>

**46. Does the amortised bound apply to a single operation in isolation?**

<details><summary>Answer</summary>

No. **Amortisation is a statement about sequences; with one operation there is no sequence.**

</details>

**47. Give the honest summary.**

<details><summary>Answer</summary>

**Amortised $O(1)$ is the right answer for throughput and the wrong answer for latency.**

</details>

---

## K. Traps

**48. Is quicksort amortised $O(n\log n)$?**

<details><summary>Answer</summary>

No — it is **average-case** $O(n\log n)$ and is *not* amortised anything. Running it a thousand times does not make a sorted-input run cheaper.

</details>

**49. What is the shrink-at-half trap?**

<details><summary>Answer</summary>

Add a `pop` that shrinks as soon as size falls **to** half the capacity, and an adversary can sit exactly on the boundary, forcing a resize every operation — $O(n)$ per operation forever. **The fix is to shrink only at one quarter full**, leaving a hysteresis gap.

</details>

**50. Why can your argument never read the credit balance at runtime?**

<details><summary>Answer</summary>

**Credit is fictional.** There is no field in the struct holding credits — it is a bookkeeping device for proving the total stays bounded.

</details>

---

## Scorecard

| Pass | Date | Got it | Close | Blank | Questions missed |
| :--- | :--- | :----- | :---- | :---- | :--------------- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Related

- [[02-amortized-analysis|Amortized Analysis]] — the module
- [[01-growth-and-asymptotic-notation-qb|Growth & Asymptotics — Question Bank]]
- [[dsa/02-data-structures/02-dynamic-arrays-qb|Dynamic Arrays — Question Bank]] — the running example
- [[dsa/02-data-structures/10-union-find-qb|Union-Find — Question Bank]] — the case needing the potential method
