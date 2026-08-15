# Proof Techniques

**[Beginner → Intermediate]** — How to establish that something is true for every case, and the handful of patterns that cover almost everything.

## What a proof is

**A proof is an argument that convinces a sceptical reader that a statement is true — for all cases, not just the ones you tried.**

It's not a formal derivation in symbolic logic (that's a *formal* proof, and almost nobody writes them by hand). **It's prose with rigorous reasoning**, written for a human.

> **The relationship to testing is exact and worth stating.** A test checks one input. A property test checks many. **A proof checks all of them, including the ones you'd never think of.** That's why proofs are worth the effort for a consensus algorithm and not worth it for a CRUD endpoint — the cost is high and the value scales with how catastrophic an uncovered case would be.

## Direct proof

Assume $p$, derive $q$, conclude $p \to q$. **The default; try it first.**

> **Claim:** If $n$ is even, then $n^2$ is even.
>
> **Proof.** Suppose $n$ is even. Then $n = 2k$ for some integer $k$. So $n^2 = 4k^2 = 2(2k^2)$. Since $2k^2$ is an integer, $n^2$ is even. $\blacksquare$

**The structure to notice:** unpack the definition ("even" → $n = 2k$), do algebra, repack into the definition. **Most direct proofs are exactly that**, and getting stuck usually means you haven't unpacked a definition yet.

## Proof by contraposition

To prove $p \to q$, prove $\neg q \to \neg p$ instead. **Same statement** — see [[foundations/discrete-math/02-logic|note 02]] — and often far easier.

> **Claim:** If $n^2$ is even, then $n$ is even.
>
> **Direct attempt:** $n^2 = 2k$, so $n = \sqrt{2k}$… and you're stuck. Square roots aren't algebraically pleasant.
>
> **Contrapositive:** if $n$ is odd, then $n^2$ is odd. Suppose $n = 2k+1$. Then $n^2 = 4k^2+4k+1 = 2(2k^2+2k)+1$, which is odd. $\blacksquare$

**The tell:** when the hypothesis is awkward to work with and the *negation of the conclusion* is concrete, flip it. Here "n is odd" gives you $2k+1$ to manipulate; "$n^2$ is even" gives you a square root.

## Proof by contradiction

Assume the statement is **false**, derive something impossible, conclude it must be true.

> **Claim:** $\sqrt{2}$ is irrational.
>
> **Proof.** Suppose not — suppose $\sqrt{2} = a/b$ in lowest terms. Then $2b^2 = a^2$, so $a^2$ is even, so $a$ is even (by the previous result). Write $a = 2c$: then $2b^2 = 4c^2$, so $b^2 = 2c^2$, so $b$ is even too. **But then $a$ and $b$ share a factor of 2**, contradicting "lowest terms". $\blacksquare$

**Powerful, and worth two warnings:**

**It can obscure.** A direct proof usually *explains why*; a proof by contradiction often just shows the alternative is impossible. Prefer direct when you have the choice.

**It's non-constructive.** Proving "a solution exists" by contradiction doesn't tell you what the solution is. (Constructive mathematics rejects this move entirely, which matters for [[foundations/compilers/05-type-systems-and-checking|type theory]] and proof assistants — a constructive proof *is* a program that produces the object.)

**Where it's the natural tool:** proving something *doesn't* exist, or that a set is infinite. **Euclid's proof that there are infinitely many primes** is the classic — assume finitely many, multiply them all and add 1, and you've produced a number that's either prime or has a prime factor not in your list.

## Proof by cases

Split into exhaustive cases and prove each.

> **Claim:** For any integer $n$, $n^2 + n$ is even.
>
> **Proof.** *Case 1: $n$ even.* $n = 2k$, so $n^2+n = 2k(2k+1)$, even. *Case 2: $n$ odd.* $n=2k+1$, so $n^2+n = (2k+1)(2k+2) = 2(2k+1)(k+1)$, even. Every integer is even or odd, so the cases are exhaustive. $\blacksquare$

**The only thing that can go wrong is missing a case**, so state explicitly why yours are exhaustive. This is precisely the discipline a compiler enforces with exhaustiveness checking on a `match` — and the reason [[languages/03-rust/06-structs-enums-and-pattern-matching|Rust's]] insistence on it catches real bugs.

## Counterexample

**To disprove a universal claim, produce one instance where it fails.** That's the whole method.

> **Claim:** Every odd number is prime.
> **Disproof:** 9. $\blacksquare$

**Asymmetry worth remembering:** disproving $\forall$ takes one example; proving it takes a general argument. **This is why finding a bug is easy and proving there are none is hard**, and it's the same asymmetry as [[research/04-research-questions-and-hypotheses|falsifiability]] in science.

**And it's why $n = 1, 2, 3$ working proves nothing.** A famous case: $n^2 + n + 41$ is prime for every $n$ from 0 to 39, and composite at 40.

## Proof by induction

**The most important technique in computer science**, and it gets its own note because recursion is the same idea.

**Structure:**
1. **Base case** — prove $P(0)$
2. **Inductive step** — prove $P(k) \to P(k+1)$ for arbitrary $k$
3. **Conclude** $P(n)$ for all $n \geq 0$

**The domino intuition:** the base case knocks the first one over; the inductive step guarantees each knocks over the next.

Fully developed in [[foundations/discrete-math/05-induction-and-recursion|note 05]], including strong induction and structural induction.

## Existence and uniqueness

**Existence** — show something exists. **Constructive** proofs exhibit one; **non-constructive** proofs show one must exist without producing it.

The pigeonhole principle gives beautifully non-constructive proofs: *some* two people in London have the same number of hairs on their heads, and you'll never learn who. → [[foundations/discrete-math/06-combinatorics-and-counting|Combinatorics]]

**Uniqueness** — the standard move: assume two objects $a$ and $b$ both satisfy the property, then prove $a = b$.

## Proving programs correct

Where this becomes concrete, and the reason CS students learn it.

**Loop invariants** are induction, exactly. A property that:
1. Holds before the loop starts (**base case**)
2. Is preserved by each iteration (**inductive step**)
3. Combined with the exit condition, gives what you wanted (**conclusion**)

> **Binary search.** Invariant: *if the target is in the array, it's within `[lo, hi]`.*
>
> **Initially** `lo=0, hi=n-1` — trivially true. **Each iteration** discards a half that provably can't contain the target, so the invariant survives. **On exit**, the range is empty or has been found — so if it wasn't found, it wasn't there.
>
> **Termination:** `hi - lo` strictly decreases and is bounded below, so the loop ends.

**Correctness needs both parts:**

**Partial correctness** — *if* it terminates, the answer is right. **Termination** — it does terminate.

**They're separate obligations**, and proving termination generally is impossible — that's the halting problem. → [[foundations/theory-of-computation/06-decidability|Decidability]]

**The practical technique** is a *variant*: a quantity that strictly decreases each iteration and cannot go below a bound. `hi - lo` above; the remaining list length in a recursion. **If you can't name the variant, you may not have termination** — and that's a genuinely useful review question to ask about any loop that isn't obviously bounded.

## Writing a proof

**State what you're proving.** Precisely, with all quantifiers.

**Say which technique you're using.** "We proceed by induction on $n$." The reader shouldn't have to reverse-engineer your structure.

**Define your notation** before using it.

**Justify each step**, or make it obviously mechanical. "Therefore" needs to be earned.

**Say where each hypothesis is used.** A proof that never uses a hypothesis is proving something stronger — or is wrong.

**End it.** $\blacksquare$ or QED.

> **A proof is writing, and the same rules apply as anywhere else: clarity over cleverness, point first, and a reader who doesn't have your context.** → [[research/09-scientific-writing-craft|Scientific Writing Craft]]

## Common errors

**Proving the converse.** You set out to prove $p \to q$ and prove $q \to p$. **The commonest error there is**, and easy to miss in your own work.

**Circular reasoning.** Using the conclusion, usually disguised.

**Assuming what's to be proven in the inductive step.** You may assume $P(k)$ — that's the hypothesis. You may not assume $P(k+1)$, which is what you're proving.

**Examples as proof.** Any number of cases is not all cases.

**Losing generality.** "Let $n$ be an even integer" when the claim was about all integers.

**Division by a possibly-zero quantity**, and taking square roots without both signs. Both quietly discard cases.

**A missing case**, which is the failure mode of proof by cases and of pattern matching alike.

---

## Related
- [[foundations/discrete-math/02-logic|Logic]] — the reasoning these formalise
- [[foundations/discrete-math/05-induction-and-recursion|Induction and Recursion]] — the technique that matters most
- [[foundations/theory-of-computation/06-decidability|Decidability]] — where proofs establish impossibility
- [[foundations/discrete-math/README|Discrete maths map]]
