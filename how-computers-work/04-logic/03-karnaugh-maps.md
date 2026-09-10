# Module 17: Karnaugh Maps (Seeing the Simplification)

**[Intermediate]** — Algebra in module 16 worked but gave no way to know when you had finished. A Karnaugh map turns simplification into a visual pattern-matching task with a clear stopping rule — and generalises into the algorithm real tools use.

## Before you start

- You can apply the Boolean laws, especially complement ($A + \overline{A} = 1$) and absorption — [[how-computers-work/04-logic/02-boolean-algebra|module 16]].
- You can write canonical SOP from a truth table — module 16.
- You know gate transistor costs — [[how-computers-work/04-logic/01-gates-from-transistors|module 15]].

**After this lesson you will be able to:**

1. Explain why K-map rows and columns use Gray code rather than binary counting order.
2. Group cells correctly, including wrap-around, and read off the simplified expression.
3. Use don't-care conditions to get simplifications that would otherwise be unavailable.
4. Explain what a prime implicant is and why the method has a definite stopping point.

**Study route:** section 3 is why the layout works — the rest follows from it. Section 7 (hazards) is the one that connects back to real timing.

---

## 1. Why this exists (real-world motivation)

Module 16's simplification worked, but look at what it required: noticing that you could *duplicate* a term to enable two different factorisations. That is a genuine insight, not a procedure — and it raises two problems that get worse with every added variable.

**First, it is error-prone.** Each step is a chance to drop a term or mis-apply a law.

**Second — and worse — there is no stopping rule.** When you reach $A + B$, how do you *know* nothing further is possible? With algebra alone, you don't. You stop when you run out of ideas, which is not the same as reaching the minimum.

**A Karnaugh map fixes both.** It arranges the truth table so that terms which can combine are physically adjacent, turning "spot the algebraic opportunity" into "spot the rectangle". And it makes completion visible: when every 1 is covered by a maximal group, you are done.

---

## 2. Terminology

| Term | Plain-English definition | Example |
| :--- | :--- | :--- |
| **Karnaugh map** | A truth table laid out so adjacent cells differ in one variable | — |
| **Gray code** | An ordering where consecutive values differ in exactly one bit | 00, 01, 11, 10 |
| **Implicant** | A product term that is true only where the function is true | $B'C'$ |
| **Prime implicant** | An implicant that cannot be made larger | — |
| **Essential prime implicant** | The only one covering some particular minterm | — |
| **Group** | A rectangle of $2^k$ adjacent 1s | — |
| **Cover** | A set of groups including every 1 | — |
| **Don't care (X)** | An input combination that cannot occur or whose output is irrelevant | — |
| **Hazard / glitch** | A brief wrong output during a transition, caused by unequal delays | — |

---

## 3. Why Gray code is the whole trick

Everything about the K-map follows from one decision: **label the rows and columns in Gray code, not binary counting order.**

```
   Binary order:  00, 01, 10, 11
                        ↑    ↑
                   these differ in TWO bits

   Gray order:    00, 01, 11, 10
                   ↑   ↑   ↑   ↑
                every step changes exactly ONE bit
```

**Why that matters.** The only simplification available is the complement law: $XY + X\overline{Y} = X(Y + \overline{Y}) = X$. Two terms combine **only if they differ in exactly one variable.**

Gray-code ordering guarantees that **physically adjacent cells differ in exactly one variable** — so adjacency on the map *is* combinability. The layout converts an algebraic property into a spatial one, and pattern-matching rectangles is something humans do far better than symbol manipulation.

**Adjacency wraps around.** The left and right edges are adjacent, as are top and bottom, because Gray code is cyclic — 10 and 00 also differ in one bit. The map is really a torus drawn flat, and forgetting the wrap is the most common source of missed simplifications.

### The grouping rules

1. Groups must contain $2^k$ cells: 1, 2, 4, 8, 16.
2. Groups must be rectangular (including wrap-around).
3. **Make each group as large as possible** — every doubling eliminates one literal.
4. Use as few groups as possible, but every 1 must be covered.
5. Groups **may overlap**. Overlap is free and often necessary.

**Rule 3 is where the saving comes from.** A group of 2 removes one variable; a group of 4 removes two; a group of 8 removes three. **Bigger groups mean cheaper gates**, so always extend before you count.

---

## 4. Reading a map

For the function $F(A,B,C,D) = \sum m(0,1,2,5,6,7,8,9,10,14)$:

```
          CD=00   01   11   10
    AB=00    1    1    0    1
    AB=01    0    1    1    1
    AB=11    0    0    0    1
    AB=10    1    1    0    1
```

The minimiser finds six **prime implicants** — every maximal group that exists on this map:

| Pattern | Term | What it is |
| :--- | :--- | :--- |
| `--10` | $CD'$ | a column, wrapping top to bottom |
| `-0-0` | $B'D'$ | four corners, wrapping both ways |
| `-00-` | $B'C'$ | — |
| `0-01` | $A'C'D$ | — |
| `01-1` | $A'BD$ | — |
| `011-` | $A'BC$ | — |

A dash means "this variable is eliminated" — the group spans both its values, so it cannot be deciding anything.

**Only three are needed for a minimal cover:**

$$F = CD' + B'C' + A'BD$$

**Three terms, seven literals** — against the canonical form's ten terms and forty literals. **An 82% reduction in literals**, and the lab verifies the result against all 16 input combinations rather than asking you to trust it.

> [!NOTE]
> **Note `-0-0` — the four-corner group.** Cells 0, 2, 8 and 10 sit at the four corners of the map and are all adjacent because *both* axes wrap. Seeing that requires remembering the map is a torus.
>
> This group is a legitimate prime implicant, though in this case the cover did not need it. Missing wrap-around groups is the classic K-map error, and it is why the algorithmic method in section 6 is more reliable than eyeballing.

---

## 5. Don't cares — free simplification

Sometimes an input combination **cannot occur**, or its output genuinely does not matter. A BCD digit uses only 0–9, so inputs 1010–1111 never arise.

Mark those cells **X**. Then, when grouping:

**Treat each X as whichever value makes your groups bigger — and ignore the ones that don't help.**

This is not a shortcut or an approximation. It is exploiting genuine freedom in the specification: since the output for those inputs is unconstrained, you may choose whatever value yields the cheapest circuit. **Don't-cares often produce dramatic savings**, and a specification that omits them forces the synthesis tool to implement behaviour nobody needs.

In the lab, `minimise()` includes don't-cares when *forming* prime implicants but excludes them from the set that must be *covered* — exactly the right asymmetry, and worth reading the code for.

---

## 6. Predict before reading on

A group of 2 cells eliminates 1 variable. A group of 4 eliminates 2. A group of 8 eliminates 3.

**On a 4-variable map, what does a group of all 16 cells mean?**

<details><summary>Check your answer</summary>

It eliminates **all four variables**, leaving the term **1**.

The function is true for every input — a constant. No gates needed at all; tie the output to $V_{DD}$.

This sounds like a degenerate case, but it happens constantly in real synthesis: after constant propagation, some logic block turns out to be always-true or always-false, and the tool deletes it entirely. **The most valuable optimisation is often discovering that a circuit is unnecessary.**

The same reasoning applies to a group of 8 in a 4-variable map: three variables vanish, leaving a single literal — one wire, no gate.
</details>

---

## 7. Hazards — where the ideal model leaks

Boolean algebra assumes gates are instantaneous. They are not ([[how-computers-work/01-electricity/04-signals-and-time|module 4]]), and that has a consequence K-maps can help with.

Consider two groups covering adjacent 1s but **not overlapping**. As the input moves from one group's territory to the other's, one gate is turning off while another is turning on. If the turn-off happens first, the output **momentarily drops to 0** even though it should stay 1.

That is a **static hazard** — a glitch. It is a real pulse on a real wire, and downstream logic can latch it.

**The fix is visible on the map: add a redundant group that overlaps the boundary.** The extra term is logically unnecessary — it never changes the function's value — but it holds the output high during the handover.

**That redundant term is exactly the consensus term** from [[how-computers-work/04-logic/02-boolean-algebra|module 16]]: $AB + \overline{A}C + BC$, where $BC$ is algebraically redundant but physically essential.

> [!NOTE]
> **Minimal is not always correct.** The minimum-cost circuit can glitch; the glitch-free circuit costs more. Which you want depends on whether the output feeds combinational logic that will settle anyway, or something edge-sensitive that could capture the glitch.
>
> This is the first genuine case in the course where **the mathematical abstraction and the physical reality diverge** — and the resolution is to add something the mathematics says is unnecessary. Keep it in mind for [[how-computers-work/06-memory/01-latches-and-flip-flops|module 22]], where timing stops being a detail and becomes the whole subject.

---

## 8. Worked example — runnable

K-maps are a visual method for humans and do not scale past about six variables. The underlying algorithm — **Quine–McCluskey** — does, and is what real tools use. This lab implements it: it finds every prime implicant by repeated merging, selects a cover, and then **verifies the result against the original specification**.

Save as `kmap_lab.py` and run `python3 kmap_lab.py`.

```python
"""Karnaugh-map minimisation, done algorithmically (Quine-McCluskey)."""
from itertools import product

GRAY2 = [(0, 0), (0, 1), (1, 1), (1, 0)]     # Gray order: one bit changes per step

def gray_code(n_bits):
    """Gray-code sequence: consecutive entries differ in exactly one bit."""
    return [i ^ (i >> 1) for i in range(2 ** n_bits)]

def draw_kmap(minterms, dont_cares, names="ABCD"):
    """Render a 4-variable K-map with rows/cols in Gray-code order."""
    rows, cols = gray_code(2), gray_code(2)
    print(f"        {names[2]}{names[3]}=00   01   11   10")
    for r in rows:
        cells = []
        for c in cols:
            m = (r << 2) | c
            cells.append("X" if m in dont_cares else ("1" if m in minterms else "0"))
        print(f"  {names[0]}{names[1]}={r:02b}    " + "    ".join(cells))

def combine(a, b):
    """Combine two patterns differing in exactly one position -> '-' there."""
    diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    if len(diff) != 1:
        return None
    return a[:diff[0]] + "-" + a[diff[0] + 1:]

def prime_implicants(terms, n_bits):
    """Repeatedly merge adjacent terms; whatever never merges is prime."""
    current = {format(m, f"0{n_bits}b") for m in terms}
    primes = set()
    while current:
        merged, used = set(), set()
        for a in current:
            for b in current:
                if a >= b:
                    continue
                c = combine(a, b)
                if c:
                    merged.add(c)
                    used.add(a); used.add(b)
        primes |= (current - used)
        current = merged
    return primes

def covers(pattern, minterm, n_bits):
    bits = format(minterm, f"0{n_bits}b")
    return all(p == "-" or p == b for p, b in zip(pattern, bits))

def minimise(minterms, dont_cares, n_bits):
    """Select a minimal cover: take essential prime implicants, then greedy."""
    primes = prime_implicants(set(minterms) | set(dont_cares), n_bits)
    required = set(minterms)          # don't-cares need not be covered
    chosen = set()

    # Essential prime implicants: the only one covering some minterm
    for m in required:
        covering = [p for p in primes if covers(p, m, n_bits)]
        if len(covering) == 1:
            chosen.add(covering[0])
    covered = {m for m in required if any(covers(p, m, n_bits) for p in chosen)}

    # Greedy for whatever is left
    while covered != required:
        best = max(primes - chosen,
                   key=lambda p: len({m for m in required - covered
                                      if covers(p, m, n_bits)}))
        chosen.add(best)
        covered |= {m for m in required - covered if covers(best, m, n_bits)}
    return sorted(chosen)

def to_expression(pattern, names="ABCD"):
    parts = [names[i] if b == "1" else names[i] + "'"
             for i, b in enumerate(pattern) if b != "-"]
    return "".join(parts) if parts else "1"

def literal_count(patterns):
    return sum(1 for p in patterns for b in p if b != "-")

if __name__ == "__main__":
    N = 4
    MINTERMS = [0, 1, 2, 5, 6, 7, 8, 9, 10, 14]
    DONT_CARES = []

    print("Gray code is what makes adjacency meaningful:")
    print(f"  2-bit Gray order: {[format(g, '02b') for g in gray_code(2)]}")
    print("  consecutive entries differ in exactly ONE bit, so adjacent")
    print("  cells differ in one variable and can combine via A + A' = 1")
    print()

    print(f"F(A,B,C,D) = sum m{tuple(MINTERMS)}")
    print()
    draw_kmap(set(MINTERMS), set(DONT_CARES))
    print()

    primes = sorted(prime_implicants(set(MINTERMS) | set(DONT_CARES), N))
    print(f"prime implicants found: {len(primes)}")
    print("  " + ", ".join(f"{p} ({to_expression(p)})" for p in primes))
    print()

    result = minimise(MINTERMS, DONT_CARES, N)
    expr = " + ".join(to_expression(p) for p in result)
    print(f"minimal cover: {len(result)} terms, {literal_count(result)} literals")
    print(f"  F = {expr}")
    print()

    # Canonical SOP for comparison
    canonical_literals = len(MINTERMS) * N
    print(f"canonical SOP would be {len(MINTERMS)} terms, {canonical_literals} literals")
    print(f"  reduction: {100*(1 - literal_count(result)/canonical_literals):.0f}% fewer literals")
    print()

    # Verify the minimised form against the original specification
    print("verifying the minimised cover against the specification:")
    mismatches = 0
    for m in range(2 ** N):
        got = any(covers(p, m, N) for p in result)
        want = m in MINTERMS
        if m in DONT_CARES:
            continue
        if got != want:
            mismatches += 1
            print(f"  MISMATCH at minterm {m}")
    print(f"  {2**N - len(DONT_CARES)} inputs checked, {mismatches} mismatches")

    assert mismatches == 0
    assert literal_count(result) < canonical_literals
    print()
    print("kmap_lab: passed")
```

Expected output:

```
Gray code is what makes adjacency meaningful:
  2-bit Gray order: ['00', '01', '11', '10']
  consecutive entries differ in exactly ONE bit, so adjacent
  cells differ in one variable and can combine via A + A' = 1

F(A,B,C,D) = sum m(0, 1, 2, 5, 6, 7, 8, 9, 10, 14)

        CD=00   01   11   10
  AB=00    1    1    0    1
  AB=01    0    1    1    1
  AB=11    0    0    0    1
  AB=10    1    1    0    1

prime implicants found: 6
  --10 (CD'), -0-0 (B'D'), -00- (B'C'), 0-01 (A'C'D), 01-1 (A'BD), 011- (A'BC)

minimal cover: 3 terms, 7 literals
  F = CD' + B'C' + A'BD

canonical SOP would be 10 terms, 40 literals
  reduction: 82% fewer literals

verifying the minimised cover against the specification:
  16 inputs checked, 0 mismatches

kmap_lab: passed
```

**The `combine()` function is the complement law in code.** Two patterns differing in exactly one position merge, with a `-` marking the eliminated variable. That is $XY + X\overline{Y} = X$, expressed as string manipulation — and repeating it until nothing more merges is precisely "make every group as large as possible".

---

## 9. Common pitfalls and traps

1. **Labelling the map in binary order.** Then adjacent cells differ in two variables and cannot combine. The whole method collapses.
2. **Forgetting wrap-around.** Left/right and top/bottom edges are adjacent. The four-corner group is the classic miss.
3. **Making groups too small.** Always extend a group as far as it will go before counting. Each doubling removes a literal.
4. **Refusing to overlap groups.** Overlap costs nothing and is often required for maximal groups.
5. **Using group sizes that are not powers of two.** A group of 3 or 6 does not correspond to any algebraic simplification.
6. **Covering don't-cares.** Include them when *forming* groups; never add a group solely to cover an X.
7. **Assuming minimal means correct.** A minimal cover can glitch. Sometimes you deliberately add a redundant term.

---

## 10. Check your understanding

1. **Why must groups be powers of two?**
   <details><summary>Answer</summary>
   Each merge step combines two terms differing in one variable, eliminating that variable. Starting from single cells, sizes can only double: 1 → 2 → 4 → 8 → 16.<br>
   A group of 3 does not correspond to any sequence of complement-law applications — there is no algebraic simplification it represents. You would have to cover those three cells as a group of 2 plus a group of 1 (possibly overlapping into a larger group).
   </details>

2. **A 4-variable map has a single 1 at $ABCD = 0101$, everything else 0. What is the minimal expression, and what does it cost?**
   <details><summary>Answer</summary>
   A lone 1 with no adjacent 1s forms a group of size 1, so no variables are eliminated: $F = \overline{A}B\overline{C}D$.<br>
   That is a 4-input AND with two inverted inputs — roughly 2 inverters plus a 4-input AND. <strong>Isolated minterms are the worst case for minimisation</strong>: nothing combines, and the canonical form <em>is</em> the minimal form. This is why functions like parity (where 1s are maximally scattered, never adjacent) do not simplify at all — and why XOR, which is 2-input parity, has no cheap SOP implementation.
   </details>

3. **A 4-bit BCD input has six unused codes. Why does marking them as don't-cares often halve the gate count?**
   <details><summary>Answer</summary>
   Six of sixteen cells become flexible — over a third of the map. Each X can be treated as 1 wherever that enlarges a group, and ignored otherwise.<br>
   Since every doubling of a group removes one literal, and the Xs are often positioned to extend groups from 2 to 4 or 4 to 8, the reduction compounds quickly. Concretely: a group of 2 that becomes a group of 8 goes from 3 literals to 1.<br>
   The practical lesson is that <strong>specifying "don't care" rather than arbitrarily picking 0 is a real design decision worth money.</strong> A specification that pins down unreachable cases forces the tool to build logic nobody needs.
   </details>

4. **Why does adding a redundant term fix a hazard, when it cannot change the function's value?**
   <details><summary>Answer</summary>
   The glitch occurs during the <em>transition</em> between two non-overlapping groups: as the input crosses the boundary, one gate turns off before the other turns on, and the output dips.<br>
   A redundant group spanning that boundary is true throughout the handover, so it holds the output high regardless of the order in which the other two switch. It changes nothing about the steady-state function — which is why Boolean algebra calls it redundant — but it changes the <em>dynamic</em> behaviour, which algebra does not model. It is the consensus theorem being physically necessary despite being logically superfluous.
   </details>

---

## 11. Practice — independent task

**Task:** Design a **BCD-to-seven-segment decoder** for segment `a` (the top bar), lit for digits 0, 2, 3, 5, 6, 7, 8, 9.

- **(a)** Build the 4-variable truth table. Inputs are the BCD digit $A$ (MSB) through $D$ (LSB); inputs 10–15 cannot occur.
- **(b)** Draw the K-map, marking the six unused codes as don't-cares.
- **(c)** Find a minimal cover by hand. State each group's size and the term it produces.
- **(d)** Now solve it with `minimise()`, passing the don't-cares. Compare with your hand answer — if they differ in term count, work out which is right and why.
- **(e)** Re-run with the don't-cares treated as 0 instead. How many more literals does that cost?
- **(f)** Price both versions in transistors using module 15's table, assuming an $n$-input AND costs the same as $(n-1)$ AND2 gates.
- **(g)** Check for hazards: are any two groups in your cover adjacent but non-overlapping? If so, name the redundant term that would remove the glitch.

**Done when:** `minimise()` agrees with your hand-derived cover, you can state the cost of ignoring the don't-cares, and you have identified any hazard in your solution.

<details><summary>Hint for (d), only if stuck</summary>
Call it as <code>minimise([0,2,3,5,6,7,8,9], [10,11,12,13,14,15], 4)</code>. The don't-cares go in the second argument, so they help form prime implicants without needing coverage.<br>
If your hand answer has more terms than the tool's, you probably missed a wrap-around group — check the corners and the outer columns first.
</details>

---

## 12. Tradeoffs and limits

- **K-maps stop working past about six variables.** Beyond four they are hard to draw and harder to read. Quine–McCluskey handles more but its runtime grows exponentially; real tools use **Espresso**, a heuristic minimiser that gives near-minimal results quickly.
- **The lab's cover selection is greedy after essentials.** That is optimal for most functions but not guaranteed minimal in general — an exact solution needs **Petrick's method** or an integer-programming formulation. The lab's verification proves the result is *correct*, not that it is *minimal*.
- **Two-level SOP is not always the cheapest form.** Multi-level factored implementations often use fewer gates, at the cost of more delay stages. Real synthesis optimises over multi-level forms.
- **Literal count is a proxy, not the objective.** The real target is area, delay and power in a specific cell library, which is why technology mapping follows minimisation rather than replacing it.

---

## Before moving on

- [ ] Explain why Gray code makes adjacency equal combinability.
- [ ] Group correctly, including wrap-around, and read off terms.
- [ ] Use don't-cares to enlarge groups without covering them.
- [ ] Define prime implicant and essential prime implicant.
- [ ] Explain a static hazard and why a redundant term fixes it.

**Recap:** A Karnaugh map lays out a truth table in Gray-code order so that physically adjacent cells differ in exactly one variable, making the complement law a visual operation. Groups of $2^k$ cells — rectangular, maximal, overlapping, wrapping at the edges — each eliminate $k$ variables. Don't-cares may be included to enlarge groups without needing coverage. The method generalises to Quine–McCluskey, which finds all prime implicants algorithmically; minimal covers can still glitch, and a redundant consensus term is the fix.

**Next:** [[how-computers-work/04-logic/04-universal-gates|Module 18 — Universal Gates]] closes Part V with a result that sounds too strong to be true: **NAND alone is enough to build every logic function that exists.**

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/04-logic/02-boolean-algebra|Module 16]] — the laws this method applies visually
- [[how-computers-work/01-electricity/04-signals-and-time|Module 4]] — the gate delays that cause hazards
- [[foundations/mathematics/02-discrete-math/index|discrete-math/]] — the combinatorial background
