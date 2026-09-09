# Module 15: Boolean Algebra (Circuit Optimisation as Algebra)

**[Beginner → Intermediate]** — You can build any gate. Now the question is which gates to build. Boolean algebra is how you find a cheaper expression for the same function — and it routinely saves more than transistor sizing ever will.

## Before you start

- You can build a CMOS gate from PDN and PUN networks and know their transistor costs — [[how-computers-work/04-logic/01-gates-from-transistors|module 14]].
- You know NAND is cheaper than NOR, and AND costs more than NAND — module 14.
- You can read a truth table.

**After this lesson you will be able to:**

1. State and apply the Boolean laws, and prove any of them by exhaustive truth table.
2. Use De Morgan's laws to convert between AND-shaped and OR-shaped logic.
3. Write a function in canonical sum-of-products form from its truth table.
4. Simplify an expression and quantify the saving in transistors.

**Study route:** section 4 (De Morgan) is the practically important one. Section 6 shows why this module beats the previous one for cost saving.

---

## 1. Why this exists (real-world motivation)

Module 14 gave you a cost model: NAND2 is 4 transistors, AND2 is 6, XOR2 is 12. You can now price any circuit.

**Which means you can now notice that most circuits are priced badly.**

Take the function $F = A\cdot B + A\cdot\overline{B} + \overline{A}\cdot B$. Built literally, term by term, it needs two inverters, three AND gates and two ORs — **34 transistors**.

That same function is exactly $A + B$. **One OR gate. Six transistors.**

**An 82% saving, and not one transistor was resized.** Module 14 fought for 38% by choosing NAND over NOR; this fight is worth twice as much and is won before any circuit is drawn.

That is what Boolean algebra buys. It is not abstract mathematics that happens to describe circuits — **it is the cost-reduction tool of digital design**, and it is why synthesis software exists.

---

## 2. Terminology

| Term | Plain-English definition | Example |
| :--- | :--- | :--- |
| **Boolean variable** | Takes only 0 or 1 | $A$ |
| **Complement** | NOT — written $\overline{A}$ or $A'$ | $\overline{A}$ |
| **Product** | AND — written $A \cdot B$ or $AB$ | $AB$ |
| **Sum** | OR — written $A + B$ | $A + B$ |
| **Literal** | A variable or its complement | $A$, $\overline{B}$ |
| **Minterm** | A product containing every variable exactly once | $A\overline{B}C$ |
| **Maxterm** | A sum containing every variable exactly once | $A + \overline{B} + C$ |
| **SOP** | Sum of products — ORs of ANDs | $AB + \overline{A}C$ |
| **POS** | Product of sums — ANDs of ORs | $(A+B)(\overline{A}+C)$ |
| **Canonical form** | The SOP or POS using only full minterms/maxterms | — |
| **Duality** | Swap AND↔OR and 0↔1; a valid law stays valid | — |

> [!NOTE]
> **The notation collides with arithmetic, and that is a deliberate historical choice.** $+$ means OR, not addition — $1 + 1 = 1$ in Boolean algebra. $\cdot$ means AND, which *does* coincide with multiplication on {0,1}.
>
> Boole chose these symbols because the algebraic laws are so similar. Most of them transfer; the ones that do not are exactly the interesting ones, like $A + A = A$.

---

## 3. The laws

Each is stated with the intuition that makes it obvious, not just the symbols. All of them are proved exhaustively in the lab.

| Law | AND form | OR form | Why |
| :--- | :--- | :--- | :--- |
| **Identity** | $A \cdot 1 = A$ | $A + 0 = A$ | Combining with the neutral value changes nothing |
| **Null** | $A \cdot 0 = 0$ | $A + 1 = 1$ | The dominant value wins outright |
| **Idempotent** | $A \cdot A = A$ | $A + A = A$ | Repeating yourself adds nothing |
| **Complement** | $A \cdot \overline{A} = 0$ | $A + \overline{A} = 1$ | Something and its opposite |
| **Involution** | $\overline{\overline{A}} = A$ | (self-dual) | Two inversions cancel |
| **Commutative** | $AB = BA$ | $A + B = B + A$ | Order is irrelevant |
| **Associative** | $(AB)C = A(BC)$ | $(A+B)+C = A+(B+C)$ | Grouping is irrelevant |
| **Distributive** | $A(B+C) = AB + AC$ | $A + BC = (A+B)(A+C)$ | Factoring out |
| **Absorption** | $A(A+B) = A$ | $A + AB = A$ | The extra term is redundant |
| **De Morgan** | $\overline{AB} = \overline{A} + \overline{B}$ | $\overline{A+B} = \overline{A}\cdot\overline{B}$ | Inversion swaps AND and OR |

**Two of these differ from ordinary arithmetic, and they are the ones that do the work:**

- **Idempotent** ($A + A = A$): in arithmetic that would be $2A$. Duplicate terms simply vanish.
- **The second distributive law** ($A + BC = (A+B)(A+C)$): this has no arithmetic analogue at all — $a + bc \neq (a+b)(a+c)$. It lets you convert SOP to POS.

**Absorption is the workhorse of simplification.** $A + AB = A$ says that once $A$ is true the whole expression is true, so the $AB$ term never decides anything. Spotting absorption is most of hand-simplification.

### The duality principle

**Swap every AND with OR and every 0 with 1, and a valid law remains valid.** That is why the table has two columns — each row is one law and its dual, and proving one proves the other for free.

This is not a coincidence. It reflects the symmetry between the two stable states of a CMOS gate, and it is the same duality as the PDN/PUN relationship in [[how-computers-work/04-logic/01-gates-from-transistors|module 14]].

---

## 4. De Morgan's laws — the practical tool

$$\overline{A \cdot B} = \overline{A} + \overline{B} \qquad\qquad \overline{A + B} = \overline{A} \cdot \overline{B}$$

**In words: breaking the bar swaps the operator.** "Not (both)" is the same as "either one isn't". "Not (either)" is the same as "neither".

These are the most-used laws in digital design, for a very concrete reason from module 14: **CMOS gates are naturally inverting, and NAND is cheaper than NOR.** De Morgan is the tool that moves inversions around until the logic lands on the cheap primitive.

**A direct example.** Suppose you need $\overline{A} \cdot \overline{B}$:

- **Built literally:** two inverters plus an AND gate = $2 \times 2 + 6 = $ **10 transistors**.
- **Rewritten by De Morgan** as $\overline{A + B}$: a single NOR2 = **4 transistors**.

**Same function, 60% fewer transistors, from applying one identity.**

This is exactly what synthesis tools do at scale — pushing inversions through a whole network to land on NAND-dominated implementations. **[[how-computers-work/04-logic/04-universal-gates|Module 17]] takes this to its conclusion:** if De Morgan lets you rewrite anything in terms of NAND, do you need any other gate at all?

---

## 5. From truth table to expression

Any function can be written down mechanically from its truth table.

**Sum of products:** write one **minterm** for every row where the output is 1, then OR them together. A minterm contains every variable — uncomplemented if it is 1 in that row, complemented if 0.

| $A$ | $B$ | $F$ | Minterm |
| :-: | :-: | :-: | :--- |
| 0 | 0 | 0 | — |
| 0 | 1 | 1 | $\overline{A}B$ |
| 1 | 0 | 1 | $A\overline{B}$ |
| 1 | 1 | 1 | $AB$ |

$$F = \overline{A}B + A\overline{B} + AB$$

**This is guaranteed correct and guaranteed inefficient.** Each minterm handles exactly one row, so nothing is shared and nothing is cancelled. Canonical form is a *starting point*, never an answer.

### Simplifying it

$$F = \overline{A}B + A\overline{B} + AB$$

Apply idempotence to duplicate the $AB$ term — legal, since $AB + AB = AB$:

$$F = \overline{A}B + AB + A\overline{B} + AB$$

Factor each pair:

$$F = B(\overline{A} + A) + A(\overline{B} + B)$$

By complement, each bracket is 1:

$$F = B \cdot 1 + A \cdot 1 = A + B$$

**Three products and two inversions collapse to a single OR.** 34 transistors become 6.

> [!NOTE]
> **The trick of *duplicating* a term to enable two factorisations is the standard move**, and it is the one people find least obvious. Idempotence makes it free — you can always add another copy of a term already present.
>
> Hand-simplification of this kind is error-prone and hard to be sure you have finished, which is exactly why [[how-computers-work/04-logic/03-karnaugh-maps|module 16]] introduces a *visual* method that makes the groupings obvious and tells you when you are done.

---

## 6. Predict before reading on

Module 14 worked hard to save 38% by choosing NAND over NOR. This module's example saved 82% by algebra.

**Does that mean transistor sizing doesn't matter?**

<details><summary>Check your answer</summary>

**No — they compose, and they apply at different stages.**

Algebraic simplification decides **how many gates** you build. Sizing and gate choice decide **how much each gate costs**. The savings multiply: simplify from 34 to 6 transistors, then implement that OR as the cheaper NAND-based form where the surrounding polarity allows, and you have taken both discounts.

**But the order matters.** Simplify first. There is no point carefully sizing a gate that a simplification would have deleted entirely — and this is precisely why an EDA flow runs logic optimisation *before* technology mapping and sizing.

It is the same principle as in software: choose a better algorithm before micro-optimising the loop. A 10× algorithmic win dwarfs a 20% constant-factor win, and doing them in the wrong order wastes the effort.
</details>

---

## 7. Worked example — runnable

Every law below is **proved by exhaustive truth-table comparison**, not asserted. The lab then simplifies a real expression, proves the two forms equivalent, and prices both using module 14's transistor costs.

Save as `boolean_lab.py` and run `python3 boolean_lab.py`.

```python
from itertools import product

# Transistor cost of each gate in static CMOS (module 14)
GATE_COST = {"NOT": 2, "AND2": 6, "OR2": 6, "NAND2": 4, "NOR2": 4, "XOR2": 12}

def verify(name, left, right, n_vars):
    """Prove an identity by exhaustive truth-table comparison."""
    for values in product([0, 1], repeat=n_vars):
        if left(*values) != right(*values):
            return False, values
    return True, None

def check_all(laws):
    width = max(len(n) for n, _, _, _ in laws)
    for name, left, right, n in laws:
        ok, counterexample = verify(name, left, right, n)
        status = "proved" if ok else f"FAILS at {counterexample}"
        print(f"  {name:<{width}s}  {status}")
        if not ok:
            raise AssertionError(name)

def cost(gates):
    """Total transistors for a bag of gates, e.g. {'AND2': 3, 'NOT': 2}."""
    return sum(GATE_COST[g] * n for g, n in gates.items())

if __name__ == "__main__":
    print("Single-variable laws (proved over all inputs):")
    check_all([
        ("identity      A + 0 = A",     lambda a: a | 0,        lambda a: a,     1),
        ("identity      A . 1 = A",     lambda a: a & 1,        lambda a: a,     1),
        ("null          A + 1 = 1",     lambda a: a | 1,        lambda a: 1,     1),
        ("null          A . 0 = 0",     lambda a: a & 0,        lambda a: 0,     1),
        ("idempotent    A + A = A",     lambda a: a | a,        lambda a: a,     1),
        ("idempotent    A . A = A",     lambda a: a & a,        lambda a: a,     1),
        ("complement    A + A' = 1",    lambda a: a | (1-a),    lambda a: 1,     1),
        ("complement    A . A' = 0",    lambda a: a & (1-a),    lambda a: 0,     1),
        ("involution    (A')' = A",     lambda a: 1-(1-a),      lambda a: a,     1),
    ])
    print()

    print("Two- and three-variable laws:")
    check_all([
        ("commutative   A + B = B + A",
         lambda a, b: a | b, lambda a, b: b | a, 2),
        ("absorption    A + A.B = A",
         lambda a, b: a | (a & b), lambda a, b: a, 2),
        ("absorption    A.(A + B) = A",
         lambda a, b: a & (a | b), lambda a, b: a, 2),
        ("De Morgan     (A.B)' = A' + B'",
         lambda a, b: 1-(a & b), lambda a, b: (1-a) | (1-b), 2),
        ("De Morgan     (A+B)' = A'.B'",
         lambda a, b: 1-(a | b), lambda a, b: (1-a) & (1-b), 2),
        ("associative   (A+B)+C = A+(B+C)",
         lambda a, b, c: (a | b) | c, lambda a, b, c: a | (b | c), 3),
        ("distributive  A.(B+C) = A.B + A.C",
         lambda a, b, c: a & (b | c), lambda a, b, c: (a & b) | (a & c), 3),
        ("distributive  A+(B.C) = (A+B).(A+C)",
         lambda a, b, c: a | (b & c), lambda a, b, c: (a | b) & (a | c), 3),
        ("consensus     A.B + A'.C + B.C = A.B + A'.C",
         lambda a, b, c: (a & b) | ((1-a) & c) | (b & c),
         lambda a, b, c: (a & b) | ((1-a) & c), 3),
    ])
    print()

    # A real simplification, proved equivalent then costed
    original  = lambda a, b: (a & b) | (a & (1-b)) | ((1-a) & b)
    simplified = lambda a, b: a | b
    ok, _ = verify("simplification", original, simplified, 2)
    print(f"F = A.B + A.B' + A'.B   simplifies to   F = A + B")
    print(f"  equivalence proved over all inputs: {ok}")
    print()
    print("  truth table (both):")
    for a, b in product([0, 1], repeat=2):
        print(f"    A={a} B={b}  ->  {original(a,b)}   {simplified(a,b)}")
    print()

    before = cost({"NOT": 2, "AND2": 3, "OR2": 2})
    after  = cost({"OR2": 1})
    print(f"  literal implementation: 2 NOT + 3 AND2 + 2 OR2 = {before} transistors")
    print(f"  simplified:             1 OR2                  = {after} transistors")
    print(f"  saving: {before - after} transistors ({100*(before-after)/before:.0f}%)")
    print()

    # De Morgan in its practical role: turning NOR-shaped logic into NAND-shaped
    print("De Morgan as a design tool (module 14: NAND is cheaper than NOR):")
    print(f"  A' . B'  built directly needs 2 NOT + 1 AND2 = {cost({'NOT':2,'AND2':1})} transistors")
    print(f"  rewritten as (A + B)' it is one NOR2         = {cost({'NOR2':1})} transistors")

    assert ok
    assert before > after
    print()
    print("boolean_lab: passed")
```

Expected output:

```
Single-variable laws (proved over all inputs):
  identity      A + 0 = A   proved
  identity      A . 1 = A   proved
  null          A + 1 = 1   proved
  null          A . 0 = 0   proved
  idempotent    A + A = A   proved
  idempotent    A . A = A   proved
  complement    A + A' = 1  proved
  complement    A . A' = 0  proved
  involution    (A')' = A   proved

Two- and three-variable laws:
  commutative   A + B = B + A                  proved
  absorption    A + A.B = A                    proved
  absorption    A.(A + B) = A                  proved
  De Morgan     (A.B)' = A' + B'               proved
  De Morgan     (A+B)' = A'.B'                 proved
  associative   (A+B)+C = A+(B+C)              proved
  distributive  A.(B+C) = A.B + A.C            proved
  distributive  A+(B.C) = (A+B).(A+C)          proved
  consensus     A.B + A'.C + B.C = A.B + A'.C  proved

F = A.B + A.B' + A'.B   simplifies to   F = A + B
  equivalence proved over all inputs: True

  truth table (both):
    A=0 B=0  ->  0   0
    A=0 B=1  ->  1   1
    A=1 B=0  ->  1   1
    A=1 B=1  ->  1   1

  literal implementation: 2 NOT + 3 AND2 + 2 OR2 = 34 transistors
  simplified:             1 OR2                  = 6 transistors
  saving: 28 transistors (82%)

De Morgan as a design tool (module 14: NAND is cheaper than NOR):
  A' . B'  built directly needs 2 NOT + 1 AND2 = 10 transistors
  rewritten as (A + B)' it is one NOR2         = 4 transistors

boolean_lab: passed
```

Note the **consensus theorem** in the output: $AB + \overline{A}C + BC = AB + \overline{A}C$. The $BC$ term is entirely redundant — whenever $BC$ is true, either $A$ is true (so $AB$ covers it) or $A$ is false (so $\overline{A}C$ covers it). It is not obvious by inspection, which is why it is worth knowing by name, and it matters practically for eliminating hazards in [[how-computers-work/04-logic/03-karnaugh-maps|module 16]].

---

## 8. Common pitfalls and traps

1. **Reading $+$ as arithmetic addition.** $1 + 1 = 1$ here. Every Boolean expression is about truth, not quantity.
2. **Misapplying De Morgan by only swapping the operator.** You must complement **each term** *and* swap the operator. $\overline{A + B}$ is $\overline{A}\cdot\overline{B}$, not $\overline{A} + \overline{B}$ and not $\overline{A \cdot B}$.
3. **Stopping at canonical form.** Minterm expansion is a correct starting point and always wasteful.
4. **Forgetting the second distributive law.** $A + BC = (A+B)(A+C)$ has no arithmetic analogue, so it is easy to overlook — and it is the route from SOP to POS.
5. **Not spotting absorption.** $A + AB = A$ is the most common available saving and the easiest to miss in a long expression.
6. **Assuming fewer literals means fewer transistors.** Usually true, but the *shape* matters too: an expression needing a 4-input NOR may cost more than a slightly longer one built from NANDs.

---

## 9. Check your understanding

1. **Simplify $\overline{(\overline{A} + B)} + A\overline{B}$.**
   <details><summary>Answer</summary>
   Apply De Morgan to the first term: $\overline{(\overline{A} + B)} = A \cdot \overline{B}$.<br>
   So the expression is $A\overline{B} + A\overline{B}$, which by <strong>idempotence</strong> is just $A\overline{B}$.<br>
   From roughly three gates plus two inverters down to <strong>one AND and one inverter</strong>. Always look for De Morgan opportunities on any bar covering a compound expression.
   </details>

2. **Why is $A + \overline{A}B = A + B$?**
   <details><summary>Answer</summary>
   Expand $A$ using complement and distribution: $A = A(B + \overline{B}) = AB + A\overline{B}$.<br>
   So $A + \overline{A}B = AB + A\overline{B} + \overline{A}B$ — which is exactly the module's worked example, equal to $A + B$.<br>
   <strong>Intuitively:</strong> if $A$ is true the whole thing is true. If $A$ is false, the expression reduces to $B$. So it is true whenever $A$ or $B$ is — the $\overline{A}$ is doing no work.
   </details>

3. **A function is true only when exactly one of $A$, $B$ is true. Write its canonical SOP, identify it, and price both forms.**
   <details><summary>Answer</summary>
   Rows where output is 1: $(0,1)$ and $(1,0)$. So $F = \overline{A}B + A\overline{B}$ — which is <strong>XOR</strong>.<br>
   Built literally: 2 NOT + 2 AND2 + 1 OR2 = $4 + 12 + 6 = 22$ transistors. As a dedicated XOR2 cell: <strong>12 transistors</strong>.<br>
   XOR does not simplify further — this is a case where algebra cannot help and the answer is a purpose-built cell. It is also why cell libraries include XOR despite its cost, and why adders in [[how-computers-work/05-combinational/02-adders|module 19]] are expensive.
   </details>

4. **Why does an EDA flow simplify logic before choosing gates and sizing them?**
   <details><summary>Answer</summary>
   Because simplification changes <em>how many gates exist</em>, while mapping and sizing change <em>what each costs</em>. Optimising the cost of a gate that simplification would delete is wasted work, and the ordering means the larger saving is taken first and the smaller one applies to what remains.<br>
   The two compose multiplicatively — an 82% algebraic saving followed by a 38% NAND-versus-NOR saving on the remainder is far better than either alone. Reversing the order does not just waste effort; it can also lock in a gate-level structure that hides the algebraic opportunity.
   </details>

---

## 10. Practice — independent task

**Task:** A safety interlock outputs 1 when a machine may run. Inputs: $G$ (guard closed), $P$ (power OK), $E$ (emergency stop pressed), $M$ (maintenance mode).

The rule: run if the guard is closed **and** power is OK **and** emergency stop is *not* pressed. Also run in maintenance mode if power is OK and emergency stop is not pressed, regardless of the guard.

- **(a)** Build the full truth table for all 16 input combinations.
- **(b)** Write the canonical SOP expression, one minterm per 1-row.
- **(c)** Price the canonical form in transistors using module 14's table. State any assumptions about multi-input gate costs.
- **(d)** Simplify algebraically, naming each law as you use it. Aim for a form with three literals.
- **(e)** Price the simplified form. What percentage did you save?
- **(f)** Apply De Morgan to express your answer using only NAND and NOT. Price that version too.
- **(g)** Extend `boolean_lab.py` with both your canonical and simplified functions and use `verify()` to prove they agree on all 16 inputs.

**Done when:** `verify()` confirms equivalence, and you can state the saving as a percentage and name the law that did most of the work.

<details><summary>Hint for (d), only if stuck</summary>
Both clauses share $P \cdot \overline{E}$. Factor it out: $F = P\overline{E}(G + M)$.<br>
That is three literals plus one OR — a dramatic reduction from the canonical form. The law doing the work is <strong>distribution</strong> applied in reverse (factoring), which is the single most productive move in hand simplification after absorption.
</details>

---

## 11. Tradeoffs and limits

- **Hand simplification does not scale and has no stopping rule.** Beyond three or four variables you cannot be confident you have found the minimum. [[how-computers-work/04-logic/03-karnaugh-maps|Module 16]] gives a visual method with a clear termination condition; beyond six variables, algorithmic methods like Quine–McCluskey and Espresso take over.
- **Minimal literal count is not always minimal cost.** The real objective is area, delay and power in a specific cell library — which is why synthesis tools optimise against a technology library rather than against literal count.
- **Boolean algebra assumes ideal, instantaneous gates.** Real gates have delay, and two algebraically identical circuits can behave differently during transitions, producing **glitches**. Module 16 covers hazards and how the consensus theorem fixes them.
- **This is two-valued logic only.** Real designs also carry high-impedance and don't-care states, which extend the algebra.

---

## Before moving on

- [ ] State the ten laws and prove any of them by truth table.
- [ ] Apply De Morgan correctly, complementing terms *and* swapping the operator.
- [ ] Write canonical SOP from a truth table and explain why it is never the final answer.
- [ ] Simplify an expression, using term duplication where it enables factoring.
- [ ] Explain why simplification comes before sizing, and why the savings compose.

**Recap:** Boolean algebra manipulates expressions into cheaper equivalents. Its laws mirror arithmetic except for idempotence and the second distributive law, and every law comes with a dual obtained by swapping AND with OR and 0 with 1. De Morgan's laws move inversions across operators, which is how NOR-shaped logic becomes NAND-shaped and why they are the most used laws in practice. Canonical SOP converts any truth table into a correct, wasteful expression; simplification then removes the waste — 34 transistors to 6 in this module's example.

**Next:** [[how-computers-work/04-logic/03-karnaugh-maps|Module 16 — Karnaugh Maps]] replaces error-prone algebra with a visual method where the simplifications are literally adjacent squares, and where you can tell when you have finished.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/04-logic/01-gates-from-transistors|Module 14]] — the transistor costs used for pricing
- [[how-computers-work/04-logic/04-universal-gates|Module 17]] — where De Morgan leads: NAND alone suffices
- [[foundations/discrete-math/02-logic|discrete-math/logic]] — the same algebra as propositional logic
- [[foundations/theory-of-computation/index|theory-of-computation/]] — Boolean circuits as a model of computation
