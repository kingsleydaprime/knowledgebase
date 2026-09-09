# Module 18: Universal Gates (One Gate Is Enough)

**[Intermediate]** — Part V ends with a result that sounds too strong to be true: **every logic function that exists can be built from NAND gates alone.** Not most. Every one.

## Before you start

- You can build gates from CMOS networks and know their costs — [[how-computers-work/04-logic/01-gates-from-transistors|module 15]].
- You know De Morgan's laws — [[how-computers-work/04-logic/02-boolean-algebra|module 16]].
- You can write any function in canonical SOP form from its truth table — module 16.

**After this lesson you will be able to:**

1. Define functional completeness and prove NAND has it, by construction.
2. Build NOT, AND, OR, NOR and XOR from NAND alone.
3. Explain why {AND, OR} is *not* functionally complete, and what exactly is missing.
4. Weigh the real cost of NAND-only implementations against their manufacturing benefit.

**Study route:** section 4 is the proof, section 5 is the surprising negative result, section 7 is the honest accounting of what universality costs.

---

## 1. Why this exists (real-world motivation)

You now have a small zoo: NOT, AND, OR, NAND, NOR, XOR, each with its own transistor layout and cost.

**A manufacturing engineer would like to know how many of these you actually need.**

The question is not idle. Every distinct cell in a library must be individually designed, laid out, simulated across voltage and temperature corners, characterised for timing and power, and verified. Fewer cell types means less design effort, more predictable yield, and simpler tooling.

**The answer turns out to be one.** A single gate type — NAND — suffices for every digital circuit that can exist. So does NOR. This is not an engineering approximation; it is a theorem, and this module proves it by construction and then tests the construction on all 256 three-input functions.

It also completes Part V's arc. Module 15 built gates from switches. This module shows that **a sufficiently large collection of one kind of switch arrangement can compute anything at all** — which is the claim the whole bottom-up course has been climbing toward.

---

## 2. Terminology

| Term | Plain-English definition |
| :--- | :--- |
| **Functionally complete** | A set of gates from which every Boolean function can be built |
| **Universal gate** | A single gate that is functionally complete on its own |
| **NAND** | NOT-AND: output low only when all inputs are high |
| **NOR** | NOT-OR: output high only when all inputs are low |
| **Constructive proof** | A proof that works by exhibiting the thing, not by contradiction |
| **Monotone function** | One where flipping an input 0→1 never flips the output 1→0 |

---

## 3. What functional completeness means

**A set of gates is functionally complete if every Boolean function can be built from it.**

The bar is high: not "the common ones", but every function of every number of inputs — all $2^{2^n}$ of them for $n$ inputs. For 3 inputs that is 256 functions; for 4 inputs, 65,536.

**{AND, OR, NOT} is functionally complete**, and module 16 showed why: any truth table converts mechanically to canonical SOP, which uses only those three operations. Since the construction always works, the set is complete.

**The interesting question is how much smaller a complete set can be.** And the answer is: one gate, provided you pick the right one.

---

## 4. NAND is universal — the proof

The strategy is to build {AND, OR, NOT} from NAND alone. Once you have those three, canonical SOP gives you everything else, so completeness follows.

### NOT from NAND — 1 gate

Tie both inputs together. $\overline{A \cdot A} = \overline{A}$.

```
        A ──┬──┐
            │  NAND ──── A'
        A ──┴──┘
```

### AND from NAND — 2 gates

NAND is AND followed by an inversion, so invert it back.

```
        A ──┐
            NAND ──┬──┐
        B ──┘      │  NAND ──── A.B
                   └──┘
```

### OR from NAND — 3 gates

By De Morgan: $A + B = \overline{\overline{A} \cdot \overline{B}}$. Invert both inputs, then NAND them.

```
        A ──[NOT]──┐
                   NAND ──── A + B
        B ──[NOT]──┘
```

**That is the proof.** With NOT, AND and OR available, and canonical SOP guaranteed to express any truth table using only those, **every Boolean function is buildable from NAND gates alone.**

The lab does not merely assert this — it **synthesises all 256 three-input Boolean functions from NAND primitives and verifies each against its truth table.** Zero failures.

### XOR from NAND — 4 gates

Worth showing because the construction is not obvious:

```
        c = NAND(A, B)
        OUT = NAND( NAND(A, c), NAND(B, c) )
```

Trace $A{=}1, B{=}1$: $c = 0$, both inner NANDs give 1, output $= \overline{1 \cdot 1} = 0$. Correct — XOR is 0 when inputs match.

### NOR is universal too

The same argument runs with NOR, using the dual De Morgan law. NOT is a NOR with tied inputs; OR is NOR then invert; AND is $\overline{\overline{A} + \overline{B}}$.

**Both NAND and NOR are universal.** In practice NAND dominates, for the reason established in [[how-computers-work/04-logic/01-gates-from-transistors|module 15]]: NOR stacks PMOS transistors in series, and PMOS is the weak type, so NOR is 38–79% more expensive depending on fan-in.

---

## 5. Predict before reading on

{AND, OR, NOT} is functionally complete. NAND alone is functionally complete.

**Is {AND, OR} — without NOT — functionally complete?**

<details><summary>Check your answer</summary>

**No, and the reason is worth understanding.**

AND and OR are both **monotone**: changing an input from 0 to 1 can only ever change the output from 0 to 1, never the reverse. Composing monotone functions always yields another monotone function — there is no arrangement that can break the property.

**NOT is not monotone**, and neither is XOR, nor NAND, nor any function whose output ever *falls* when an input rises.

So {AND, OR} can only build monotone functions. It cannot build NOT. It cannot build XOR. **It cannot build anything that says "no".**

**This is not a minor gap.** Without inversion there is no negation, no comparison for inequality, no conditional branching on a false condition. And note where else it bites: [[how-computers-work/03-transistors/03-cmos|module 13]] showed CMOS gates are *naturally inverting*, which looked like an inconvenience. It is the opposite — **inversion is the property that makes the technology universal at all.**

The thing that seemed like CMOS's awkward quirk is precisely what makes it sufficient.
</details>

---

## 6. Worked example — runnable

Each construction is verified exhaustively against its reference definition, and then the universality claim is tested by synthesising **all 256 three-input Boolean functions** from NAND alone.

Save as `universal_lab.py` and run `python3 universal_lab.py`.

```python
"""Build every logic function from NAND alone, and verify by exhaustion."""
from itertools import product

class Counter:
    """Counts how many NAND gates a construction actually instantiates."""
    def __init__(self): self.n = 0
    def reset(self): self.n = 0

COUNT = Counter()

def NAND(a, b):
    """The one and only primitive."""
    COUNT.n += 1
    return 1 - (a & b)

# --- everything below is built from NAND and nothing else ---

def NOT(a):              return NAND(a, a)
def AND(a, b):           return NOT(NAND(a, b))
def OR(a, b):            return NAND(NOT(a), NOT(b))          # De Morgan
def NOR(a, b):           return NOT(OR(a, b))
def XOR(a, b):
    c = NAND(a, b)
    return NAND(NAND(a, c), NAND(b, c))

def gate_cost(fn, arity):
    """Instantiate the construction once and count NANDs used."""
    COUNT.reset()
    fn(*([0] * arity))
    return COUNT.n

def verify(built, reference, arity):
    """Exhaustively compare a NAND-built gate against its definition."""
    for values in product([0, 1], repeat=arity):
        if built(*values) != reference(*values):
            return False, values
    return True, None

def synthesise(truth_table, n_vars):
    """Build ANY function from its truth table, using only NAND gates.

    Sum of products: each 1-row becomes a minterm (an AND of literals),
    and the minterms are ORed together. AND and OR are themselves built
    from NAND above, so the whole circuit is NAND-only."""
    def circuit(*inputs):
        minterms = []
        for row, output in enumerate(truth_table):
            if not output:
                continue
            bits = [(row >> (n_vars - 1 - i)) & 1 for i in range(n_vars)]
            literals = [inputs[i] if b else NOT(inputs[i])
                        for i, b in enumerate(bits)]
            term = literals[0]
            for lit in literals[1:]:
                term = AND(term, lit)
            minterms.append(term)
        if not minterms:
            return 0                      # constant-false needs no gates
        result = minterms[0]
        for m in minterms[1:]:
            result = OR(result, m)
        return result
    return circuit

if __name__ == "__main__":
    print("Every gate, built from NAND alone, verified over all inputs:")
    print(f"  {'gate':6s} {'NANDs':>6s} {'transistors':>12s}   verified")
    checks = [
        ("NOT",  NOT,  lambda a: 1 - a,                    1),
        ("AND",  AND,  lambda a, b: a & b,                 2),
        ("OR",   OR,   lambda a, b: a | b,                 2),
        ("NOR",  NOR,  lambda a, b: 1 - (a | b),           2),
        ("XOR",  XOR,  lambda a, b: a ^ b,                 2),
    ]
    for name, built, reference, arity in checks:
        ok, bad = verify(built, reference, arity)
        n = gate_cost(built, arity)
        status = "yes" if ok else f"NO at {bad}"
        print(f"  {name:6s} {n:6d} {n*4:12d}   {status}")
        assert ok, name

    print()
    print("cost of universality (dedicated cell vs NAND-only, module 15 costs):")
    for name, dedicated, arity, built in [("AND2", 6, 2, AND), ("OR2", 6, 2, OR),
                                          ("NOR2", 4, 2, NOR), ("XOR2", 12, 2, XOR)]:
        n = gate_cost(built, arity) * 4
        print(f"  {name:5s} dedicated {dedicated:3d}   from NAND {n:3d}"
              f"   penalty x{n/dedicated:.2f}")
    print()

    # The universality claim, tested on EVERY 3-input function
    print("synthesising all 256 three-input Boolean functions from NAND only:")
    n_vars, failures, total_gates = 3, 0, 0
    for f in range(256):
        table = [(f >> i) & 1 for i in range(8)]
        circuit = synthesise(table, n_vars)
        for row, inputs in enumerate(product([0, 1], repeat=n_vars)):
            COUNT.reset()
            if circuit(*inputs) != table[row]:
                failures += 1
                break
    print(f"  functions tested: 256")
    print(f"  failures: {failures}")
    print(f"  every one of them built from NAND gates alone")

    assert failures == 0
    print()
    print("universal_lab: passed")
```

Expected output:

```
Every gate, built from NAND alone, verified over all inputs:
  gate    NANDs  transistors   verified
  NOT         1            4   yes
  AND         2            8   yes
  OR          3           12   yes
  NOR         4           16   yes
  XOR         4           16   yes

cost of universality (dedicated cell vs NAND-only, module 15 costs):
  AND2  dedicated   6   from NAND   8   penalty x1.33
  OR2   dedicated   6   from NAND  12   penalty x2.00
  NOR2  dedicated   4   from NAND  16   penalty x4.00
  XOR2  dedicated  12   from NAND  16   penalty x1.33

synthesising all 256 three-input Boolean functions from NAND only:
  functions tested: 256
  failures: 0
  every one of them built from NAND gates alone

universal_lab: passed
```

---

## 7. What universality costs

Universality is a theorem about what is *possible*, not a claim that it is *optimal*. The lab prices the difference:

| Gate | Dedicated cell | Built from NAND | Penalty |
| :--- | ---: | ---: | ---: |
| AND2 | 6 | 8 | ×1.33 |
| OR2 | 6 | 12 | ×2.00 |
| NOR2 | 4 | 16 | ×4.00 |
| XOR2 | 12 | 16 | ×1.33 |

**NOR is the worst case — four times the transistors when built from NAND.** That makes sense: NOR is NAND's dual, so expressing one in terms of the other requires inverting everything.

So the real engineering position is a compromise:

- **Real cell libraries contain dozens of cell types**, including AND, OR, XOR, AOI/OAI compounds and multiplexers, because dedicated cells are cheaper.
- **But NAND dominates the mix**, and synthesis tools actively rewrite logic toward it using De Morgan.
- **NAND-only implementations appear where uniformity matters more than area** — some FPGA and PLA structures, certain fault-tolerant designs, and teaching hardware.

> [!NOTE]
> **The result's real value is conceptual, not manufacturing advice.**
>
> It means there is **no hierarchy of logical difficulty in hardware**. Addition is not made of fancier stuff than comparison. Encryption is not made of fancier stuff than addition. A neural network's arithmetic is not made of fancier stuff than a pocket calculator's.
>
> **Everything above this line in the course is NAND gates, differing only in quantity and arrangement.** The complexity of a modern processor is entirely a matter of *how many* and *wired how* — never of *what kind*.

---

## 8. The end of Part V — what you have built

Take stock, because a threshold has been crossed.

```
   electrons in a field        (Part II)
        ↓
   doped silicon, junctions    (Part III)
        ↓
   a voltage-controlled switch (Part IV)
        ↓
   a NAND gate                 (Part V)
        ↓
   EVERY POSSIBLE LOGIC FUNCTION
```

**That last arrow is this module.** From here on, the course never needs to go below the gate again — not because the physics stopped mattering, but because **the gate is a complete and sufficient foundation.** Any function you can specify as a truth table, you can now build.

This is the same move as [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]], one level up. Module 5 bought the right to stop thinking about voltage. **Module 18 buys the right to stop thinking about transistors.**

Parts VI and VII spend that credit: assembling gates into adders, ALUs, and memory — never again asking what a gate is made of.

---

## 9. Common pitfalls and traps

1. **Thinking universal means efficient.** NAND-only costs up to 4× more transistors. Universality is about possibility.
2. **Assuming any gate is universal.** AND is not. OR is not. XOR is not. NAND and NOR are the only two-input gates that are.
3. **Forgetting that {AND, OR} lacks inversion.** Monotone gates compose into monotone functions, permanently.
4. **Believing real chips use only NAND.** They use rich libraries. NAND dominates but does not monopolise.
5. **Reading universality as a statement about speed.** A NAND-only XOR has more stages, so it is slower as well as larger. Delay is a separate axis from completeness.

---

## 10. Check your understanding

1. **Build NOT, OR and AND from NOR alone, and count gates.**
   <details><summary>Answer</summary>
   <strong>NOT:</strong> tie inputs together — $\overline{A + A} = \overline{A}$. <strong>1 gate.</strong><br>
   <strong>OR:</strong> NOR then invert. <strong>2 gates.</strong><br>
   <strong>AND:</strong> by De Morgan $A \cdot B = \overline{\overline{A} + \overline{B}}$ — invert both inputs, then NOR. <strong>3 gates.</strong><br>
   Exactly the mirror of the NAND constructions, with AND and OR swapping costs. NOR is equally universal in theory and worse in silicon, for the PMOS-stacking reason from module 15.
   </details>

2. **Is XOR functionally complete on its own?**
   <details><summary>Answer</summary>
   <strong>No.</strong> XOR is <em>linear</em> over GF(2) — every function built from XOR alone is a sum (mod 2) of some subset of the inputs, possibly plus a constant.<br>
   You can get NOT from XOR if a constant 1 is available ($A \oplus 1 = \overline{A}$), but you can never build AND, because AND is nonlinear. XOR gates compose only into other linear functions, exactly as AND and OR compose only into monotone ones.<br>
   {XOR, AND} together <em>is</em> complete — that pair forms the Reed–Muller or algebraic normal form, used in cryptography and in reversible computing.
   </details>

3. **Why does NOR cost 4× to build from NAND, when AND costs only 1.33×?**
   <details><summary>Answer</summary>
   AND is NAND plus one inverter — the structures are nearly the same, so the conversion is cheap.<br>
   NOR is NAND's <em>dual</em>: it needs the opposite series/parallel arrangement in both networks. Building it from NAND means constructing OR first (3 NANDs, since both inputs must be inverted) and then inverting the result (1 more) — 4 NANDs, 16 transistors, against a dedicated NOR2's 4.<br>
   <strong>The general principle: converting between a gate and its dual is the expensive direction.</strong> This is why libraries stock both NAND and NOR rather than deriving one from the other.
   </details>

4. **Someone claims their processor is "more advanced" because it computes neural-network operations. What does this module say about that?**
   <details><summary>Answer</summary>
   Every digital circuit — a calculator, a video decoder, a neural accelerator — is built from the same universal gates. There is no special hardware primitive for "AI"; the arithmetic is multiply-accumulate, built from adders, built from gates.<br>
   What genuinely differs is <strong>quantity, arrangement and data movement</strong>: how many multipliers run in parallel, how they are pipelined, and above all how memory bandwidth feeds them. Those are real and decisive engineering differences.<br>
   But they are differences of <em>organisation</em>, not of <em>kind</em>. Nothing in the accelerator is made of anything the calculator is not.
   </details>

---

## 11. Practice — independent task

**Task:** Design a 2-to-1 multiplexer, $\text{OUT} = (S \cdot B) + (\overline{S} \cdot A)$, using NAND gates only.

- **(a)** Write the truth table for all 8 combinations of $S$, $A$, $B$.
- **(b)** Build it by naive substitution — take the expression and replace each AND, OR and NOT with its NAND construction. Count the NAND gates.
- **(c)** A known optimal NAND-only MUX uses 4 gates. Find it. *Hint: $\overline{S}$ is needed only once, and the two NANDs feeding the output can share structure.*
- **(d)** Add your 4-gate version to `universal_lab.py` and verify it against the reference MUX with `verify()` at arity 3.
- **(e)** Compare transistor counts: your naive version, your 4-gate version, and a dedicated transmission-gate MUX (6 transistors).
- **(f)** Count the maximum number of gates any signal passes through in your 4-gate design. Using a 20 ps per-gate delay from [[how-computers-work/01-electricity/04-signals-and-time|module 4]], what is the propagation delay?
- **(g)** Use `synthesise()` to build the same MUX automatically from its truth table. How many gates does it use compared with your hand design, and why is the automatic version worse?

**Done when:** `verify()` passes for your 4-gate MUX, and you can explain why canonical-SOP synthesis produces a larger circuit than hand design.

<details><summary>Hint for (g), only if stuck</summary>
`synthesise()` builds every 1-row as a full minterm, with no sharing between terms. Hand design spots that $S$ and $\overline{S}$ select between two paths and reuses structure across them.<br>
This gap — mechanical correctness versus structural insight — is exactly the gap that logic optimisation tools exist to close, and it is why synthesis runs minimisation (module 17) before mapping to gates rather than emitting canonical form directly.
</details>

---

## 12. Tradeoffs and limits

- **Universality says nothing about depth.** A NAND-only circuit may need many more stages, and delay grows with depth. Some functions have small NAND-only implementations but unavoidably deep ones.
- **Fan-in is bounded in practice.** The proof assumes 2-input NANDs freely composed; real gates have limited drive and stack height, so large functions need buffering and trees.
- **This is combinational logic only.** Nothing here can *remember*. Every circuit built so far computes a function of its current inputs and forgets everything the instant they change — which is the gap [[how-computers-work/06-memory/01-latches-and-flip-flops|Part VII]] fills.
- **Other complete sets exist.** {XOR, AND} gives algebraic normal form, used in cryptanalysis; the Toffoli gate is universal for *reversible* computing, which matters for quantum and for thermodynamic-limit arguments.

---

## Before moving on

**This is the end of Part V.** You are ready for Part VI when you can, closed-book:

- [ ] Define functional completeness and state why {AND, OR, NOT} has it.
- [ ] Build NOT, AND and OR from NAND, and explain why that proves universality.
- [ ] Explain why {AND, OR} is not complete, using monotonicity.
- [ ] State the cost of NAND-only implementations and why libraries stock many cells anyway.
- [ ] Explain why CMOS being naturally inverting is a feature rather than a quirk.

**Recap:** A gate set is functionally complete if every Boolean function can be built from it. NAND alone is complete — NOT is a NAND with tied inputs, AND is NAND inverted, OR is NAND with inverted inputs by De Morgan — and canonical SOP then covers every truth table, as verified here on all 256 three-input functions. NOR is equally complete but more expensive in CMOS. {AND, OR} is not complete because monotone gates compose only into monotone functions, which makes inversion the property that grants universality.

**Next:** [[how-computers-work/05-combinational/01-multiplexers-and-decoders|Module 20 — Multiplexers and Decoders]] begins Part VI. You will stop building individual gates and start assembling them into blocks that select and address — the two operations every memory and every datapath is made of.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/04-logic/01-gates-from-transistors|Module 15]] — why NAND beats NOR in silicon
- [[how-computers-work/04-logic/02-boolean-algebra|Module 16]] — De Morgan, the tool behind the constructions
- [[how-computers-work/01-electricity/05-the-digital-abstraction|Module 5]] — the previous abstraction boundary
- [[foundations/theory-of-computation/index|theory-of-computation/]] — circuit complexity, where depth and size are studied formally
