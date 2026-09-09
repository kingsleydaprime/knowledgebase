# Module 15: Gates from Transistors (Building the Logic Primitives)

**[Intermediate]** — Part V begins. You have a working CMOS inverter; now build every other gate from the same two-network recipe — and find out why real chips are made overwhelmingly of NAND.

## Before you start

- You can draw a CMOS inverter and explain its pull-up / pull-down structure — [[how-computers-work/03-transistors/03-cmos|module 13]].
- You know PMOS devices are ~2.8× weaker per unit width — [[how-computers-work/02-semiconductors/03-energy-bands|module 8]].
- You know an "on" transistor is a resistor whose value depends on $W/L$ — [[how-computers-work/03-transistors/02-mosfet-physics|module 12]].

**After this lesson you will be able to:**

1. Build the pull-down and pull-up networks for any logic function, and explain why they must be duals.
2. Derive a gate's truth table from its transistor arrangement rather than memorising it.
3. Explain why CMOS gates are naturally inverting, and what AND and OR really cost.
4. Quantify why NAND is preferred over NOR, and show the penalty grows with fan-in.

**Study route:** section 3 is the construction recipe. Section 6 is the design conclusion that shapes every standard cell library in existence.

---

## 1. Why this exists (real-world motivation)

Module 13 gave you one gate: the inverter. It is a genuine logic gate — NOT is a real operation — but you cannot build a computer from inverters alone. An inverter has one input, and every interesting operation combines *several* things.

Addition needs to know whether two bits are both 1. A memory needs to know whether this address *and* that enable line are asserted. Any decision at all requires combining inputs.

**The good news is that the recipe barely changes.** The inverter's structure — a pull-up network of PMOS, a pull-down network of NMOS, arranged so exactly one conducts — generalises directly to any number of inputs and any logic function.

**The interesting news is that the cost is not symmetric.** Two gates that look equally simple on paper — NAND and NOR — differ by nearly 40% in area, and the gap widens as inputs are added. That asymmetry traces straight back to hole mobility in module 8, and it has shaped how digital logic is actually built.

---

## 2. Terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **Pull-down network (PDN)** | NMOS transistors between output and ground | The drain path |
| **Pull-up network (PUN)** | PMOS transistors between output and $V_{DD}$ | The supply path |
| **Dual networks** | Structured so exactly one conducts for every input | — |
| **Series connection** | Transistors in a chain — *all* must conduct | Doors in a corridor |
| **Parallel connection** | Transistors side by side — *any* one suffices | Doors side by side |
| **Fan-in** | Number of inputs to a gate | — |
| **Fan-out** | Number of gate inputs one output drives | — |
| **Standard cell** | A pre-designed, pre-characterised gate layout in a library | — |
| **Naturally inverting** | CMOS produces NAND/NOR directly; AND/OR need an extra stage | — |
| **Stack height** | How many transistors are in series in a network | — |

---

## 3. The construction recipe

Two rules, and they are the whole method.

### Rule 1 — the pull-down network (NMOS)

**NMOS conducts when its gate is HIGH.**

- **Series** = AND. Current flows only if *every* transistor in the chain is on, so only if every input is high.
- **Parallel** = OR. Current flows if *any* transistor is on, so if any input is high.

### Rule 2 — the pull-up network (PMOS) is the dual

**PMOS conducts when its gate is LOW.** The PUN must conduct exactly when the PDN does not, so its structure is inverted:

- Where the PDN has **series**, the PUN has **parallel**.
- Where the PDN has **parallel**, the PUN has **series**.

```
   NAND: output is LOW only when BOTH inputs are HIGH

                       V_DD
                    ┌───┴───┐
                    │       │
                 ┌──┴──┐ ┌──┴──┐
            A ───┤PMOS │ │PMOS ├─── B      PMOS in PARALLEL
                 └──┬──┘ └──┬──┘
                    └───┬───┘
                        ├──────── OUT
                     ┌──┴──┐
            A ───────┤NMOS │                NMOS in SERIES
                     └──┬──┘                (both must be on
                     ┌──┴──┐                 to pull down)
            B ───────┤NMOS │
                     └──┬──┘
                       GND
```

**Trace it.** Both inputs high: both NMOS conduct, the series chain completes, output pulled to ground → **0**. Any input low: that NMOS breaks the chain, *and* the corresponding PMOS turns on, pulling the output up → **1**.

That is NAND, derived from the arrangement rather than looked up.

```
   NOR: output is HIGH only when BOTH inputs are LOW

                       V_DD
                     ┌──┴──┐
            A ───────┤PMOS │                PMOS in SERIES
                     └──┬──┘                (both must be on
                     ┌──┴──┐                 to pull up)
            B ───────┤PMOS │
                     └──┬──┘
                        ├──────── OUT
                    ┌───┴───┐
                 ┌──┴──┐ ┌──┴──┐
            A ───┤NMOS │ │NMOS ├─── B      NMOS in PARALLEL
                 └──┬──┘ └──┬──┘
                    └───┬───┘
                       GND
```

> [!NOTE]
> **The duality is not a convention — it is forced.** If both networks conducted at once you would have module 3's row 4: a direct short from supply to ground. If neither conducted you would have row 3: a floating output.
>
> **Constructing the PUN as the PDN's dual is what makes both failure states structurally unreachable.** This is why CMOS is robust: the correctness is in the topology, not in careful timing.

---

## 4. Why CMOS is naturally inverting

Notice something about both gates above: **they invert.** Series NMOS gives AND, but the output goes *low* when the AND condition is met — so the gate computes NAND, not AND.

This is unavoidable. The PDN pulls the output **down** when its condition is satisfied, so a satisfied condition always produces a 0.

**To get AND, you build NAND and add an inverter.** That is two more transistors, one more stage of delay, and more area.

| Gate | Transistors | Note |
| :--- | ---: | :--- |
| NOT | 2 | |
| NAND2 | 4 | |
| NOR2 | 4 | |
| AND2 | 6 | = NAND2 + inverter |
| OR2 | 6 | = NOR2 + inverter |
| XOR2 | 12 | no simple dual network |

**AND is 50% more expensive than NAND, and slower.** This inverts the intuition most people bring from Boolean algebra, where AND and OR feel primitive and NAND feels like a compound. **In silicon it is the other way round.** NAND and NOR are the primitives; AND and OR are derived.

**XOR is the expensive one.** Its function — true when inputs differ — has no compact series/parallel representation, so a static CMOS XOR needs around 12 transistors. This is worth remembering: XOR appears in the heart of every adder in [[how-computers-work/05-combinational/02-adders|module 20]], and its cost is a real factor in arithmetic circuit design.

---

## 5. Predict before reading on

Module 13 ended with a claim: NAND is cheaper and faster than NOR, because PMOS transistors are the weak ones and you want fewer of them in series.

**Work out why series stacking is the problem.** If one "on" transistor is a resistor of value $R$, what is the resistance of two in series? What does that mean for a network that must be as strong as a reference inverter?

<details><summary>Check your answer</summary>

**Two "on" transistors in series have resistance $2R$** — resistances in series add ([[how-computers-work/01-electricity/03-circuit-laws|module 3]]).

To drive as hard as a single reference transistor, each device in a series stack of $n$ must be **$n$ times wider**, since $R_{on} \propto 1/W$ ([[how-computers-work/03-transistors/02-mosfet-physics|module 12]]).

Transistors in **parallel** need no widening at all — the worst case is a single device conducting alone, which is already the reference case.

**Now apply it to each gate:**

- **NAND:** NMOS in series (widen by 2, and NMOS is the *strong* type), PMOS in parallel (no widening, so just the 2.8× mobility compensation).
- **NOR:** NMOS in parallel (no widening), PMOS in series — **so the already-2.8×-weak PMOS must also be doubled, to 5.6×.**

**NOR stacks the weak transistor.** That is the entire argument, and section 6 puts numbers on it.
</details>

---

## 6. The numbers — why chips are made of NAND

Sizing both gates so they drive as hard as a reference inverter:

| Gate | $W_{nmos}$ | $W_{pmos}$ | Total width | Input cap |
| :--- | ---: | ---: | ---: | ---: |
| NAND2 | 2.0 | 2.8 | 9.6 | 4.8 |
| NOR2 | 1.0 | 5.6 | 13.2 | 6.6 |
| NAND3 | 3.0 | 2.8 | 17.4 | 5.8 |
| NOR3 | 1.0 | 8.4 | 28.2 | 9.4 |
| NAND4 | 4.0 | 2.8 | 27.2 | 6.8 |
| NOR4 | 1.0 | 11.2 | 48.8 | 12.2 |

**The NOR penalty, and how it grows:**

| Fan-in | Area | Input capacitance |
| ---: | ---: | ---: |
| 2 | ×1.38 | ×1.38 |
| 3 | ×1.62 | ×1.62 |
| 4 | ×1.79 | ×1.79 |

**A 4-input NOR is nearly 1.8× the area of a 4-input NAND, and presents 1.8× the load to whatever drives it.**

That second column is the one that hurts. Larger input capacitance means the *previous* gate must charge more, so it is slower too — the penalty propagates backwards through the circuit. And from [[how-computers-work/03-transistors/03-cmos|module 13]], dynamic power is $\alpha CV^2f$: more capacitance is more power on every transition.

**Hence the design rules that govern real chip libraries:**

1. **Prefer NAND over NOR** wherever the logic allows.
2. **Keep stack heights low** — 4-input gates are usually the practical limit; beyond that, cascade smaller gates instead.
3. **Push inversions around** using De Morgan's laws ([[how-computers-work/04-logic/02-boolean-algebra|module 16]]) to convert NOR-shaped logic into NAND-shaped logic.

> [!NOTE]
> **Follow this chain all the way down.** Holes move by a relay of valence electrons through a nearly full band (module 8) → hole mobility is 2.81× lower → PMOS delivers less current per unit width (module 12) → series PMOS stacks must be widened proportionally → NOR costs 38–79% more than NAND → **standard cell libraries are built predominantly from NAND, and synthesis tools actively rewrite logic to use it.**
>
> A fact about band structure determines the shape of the logic in every chip you own.

---

## 7. Worked example — runnable

This derives each gate's truth table *from its transistor networks* — checking for shorts and floating outputs — then computes the sizing comparison.

Save as `gates_lab.py` and run `python3 gates_lab.py`.

```python
from itertools import product

MOBILITY_RATIO = 2.8    # electrons vs holes (module 8) -> PMOS is 2.8x weaker

# A CMOS gate is two networks. Each is described by when it CONDUCTS.
# NMOS conducts on a HIGH input; PMOS conducts on a LOW input.
GATES = {
    "NOT":  dict(n_inputs=1,
                 pdn=lambda i: i[0],                    # one NMOS
                 pun=lambda i: not i[0]),               # one PMOS
    "NAND": dict(n_inputs=2,
                 pdn=lambda i: i[0] and i[1],           # NMOS in SERIES
                 pun=lambda i: (not i[0]) or (not i[1])),  # PMOS in PARALLEL
    "NOR":  dict(n_inputs=2,
                 pdn=lambda i: i[0] or i[1],            # NMOS in PARALLEL
                 pun=lambda i: (not i[0]) and (not i[1])), # PMOS in SERIES
}

def evaluate(gate):
    """Derive the truth table from the transistor networks, checking complementarity."""
    rows = []
    for inputs in product([0, 1], repeat=gate["n_inputs"]):
        bits = [bool(b) for b in inputs]
        pulls_down = gate["pdn"](bits)
        pulls_up = gate["pun"](bits)
        if pulls_down and pulls_up:
            raise AssertionError(f"short circuit at {inputs}")
        if not pulls_down and not pulls_up:
            raise AssertionError(f"floating output at {inputs}")
        rows.append((inputs, 0 if pulls_down else 1))
    return rows

def sizing(gate_kind, fan_in, ratio=MOBILITY_RATIO):
    """Widths needed so the gate drives as hard as a reference inverter.

    Series transistors must each be `fan_in` times wider to compensate for
    their resistances adding; parallel ones need no widening (worst case is
    a single device conducting alone)."""
    if gate_kind == "NAND":      # NMOS series, PMOS parallel
        w_n, w_p = fan_in * 1.0, ratio
    elif gate_kind == "NOR":     # NMOS parallel, PMOS series
        w_n, w_p = 1.0, fan_in * ratio
    else:
        raise ValueError(gate_kind)
    total_width = fan_in * (w_n + w_p)
    input_cap = w_n + w_p        # one NMOS + one PMOS gate per input
    return w_n, w_p, total_width, input_cap

if __name__ == "__main__":
    print("truth tables derived from the transistor networks:")
    for name, gate in GATES.items():
        rows = evaluate(gate)
        table = "  ".join(f"{''.join(map(str, i))}->{o}" for i, o in rows)
        print(f"  {name:5s} {table}")
    print("  (no shorts, no floating outputs -- the networks are true duals)")
    print()

    print(f"sizing for equal drive strength (PMOS is {MOBILITY_RATIO}x weaker):")
    print(f"  {'gate':>7s} {'W_nmos':>8s} {'W_pmos':>8s} {'total W':>9s} {'in cap':>8s}")
    for fan_in in (2, 3, 4):
        for kind in ("NAND", "NOR"):
            w_n, w_p, total, cap = sizing(kind, fan_in)
            print(f"  {kind+str(fan_in):>7s} {w_n:8.1f} {w_p:8.1f} {total:9.1f} {cap:8.1f}")
    print()

    print("NOR penalty relative to NAND at the same fan-in:")
    for fan_in in (2, 3, 4):
        _, _, t_nand, c_nand = sizing("NAND", fan_in)
        _, _, t_nor, c_nor = sizing("NOR", fan_in)
        print(f"  fan-in {fan_in}: area x{t_nor/t_nand:.2f}, input capacitance x{c_nor/c_nand:.2f}")
    print()

    print("transistor counts (static CMOS):")
    for name, count, note in [
        ("NOT", 2, ""), ("NAND2", 4, ""), ("NOR2", 4, ""),
        ("AND2", 6, "= NAND2 + inverter"), ("OR2", 6, "= NOR2 + inverter"),
        ("XOR2", 12, "no simple dual network"),
    ]:
        print(f"  {name:6s} {count:3d} transistors  {note}")
    print()
    print("  CMOS is naturally INVERTING: AND and OR cost an extra stage.")

    _, _, t_nand2, _ = sizing("NAND", 2)
    _, _, t_nor2, _ = sizing("NOR", 2)
    assert t_nor2 > t_nand2, "NOR must be more expensive than NAND"
    assert evaluate(GATES["NAND"])[-1] == ((1, 1), 0)
    assert evaluate(GATES["NOR"])[0] == ((0, 0), 1)
    print()
    print("gates_lab: passed")
```

Expected output:

```
truth tables derived from the transistor networks:
  NOT   0->1  1->0
  NAND  00->1  01->1  10->1  11->0
  NOR   00->1  01->0  10->0  11->0
  (no shorts, no floating outputs -- the networks are true duals)

sizing for equal drive strength (PMOS is 2.8x weaker):
     gate   W_nmos   W_pmos   total W   in cap
    NAND2      2.0      2.8       9.6      4.8
     NOR2      1.0      5.6      13.2      6.6
    NAND3      3.0      2.8      17.4      5.8
     NOR3      1.0      8.4      28.2      9.4
    NAND4      4.0      2.8      27.2      6.8
     NOR4      1.0     11.2      48.8     12.2

NOR penalty relative to NAND at the same fan-in:
  fan-in 2: area x1.38, input capacitance x1.38
  fan-in 3: area x1.62, input capacitance x1.62
  fan-in 4: area x1.79, input capacitance x1.79

transistor counts (static CMOS):
  NOT      2 transistors  
  NAND2    4 transistors  
  NOR2     4 transistors  
  AND2     6 transistors  = NAND2 + inverter
  OR2      6 transistors  = NOR2 + inverter
  XOR2    12 transistors  no simple dual network

  CMOS is naturally INVERTING: AND and OR cost an extra stage.

gates_lab: passed
```

The `evaluate()` function is worth dwelling on: it does not contain a truth table. It **derives** each one by asking, for every input combination, which network conducts — and raises an error if both or neither do. **The truth tables are a consequence of the transistor topology, not an input to it.** That is the bottom-up method made executable.

---

## 8. Common pitfalls and traps

1. **Building the PUN as a copy of the PDN.** It must be the **dual** — series becomes parallel. Copying it gives you a short circuit on some inputs.
2. **Expecting AND to be cheaper than NAND.** In CMOS, AND *is* NAND plus an inverter. Boolean-algebra intuition inverts the real cost.
3. **Ignoring stack height.** Each series transistor adds resistance and must be widened. A 6-input NOR is a genuinely bad circuit.
4. **Sizing parallel transistors as if they were series.** Parallel devices need no widening — the worst case is one conducting alone.
5. **Forgetting that input capacitance is a cost.** A physically larger gate loads its driver, slowing the *previous* stage and burning more dynamic power.
6. **Assuming XOR is as cheap as its symbol suggests.** It is the most expensive common gate, and it sits in the critical path of every adder.

---

## 9. Check your understanding

1. **Build the PDN and PUN for $\overline{A \cdot (B + C)}$. How many transistors, and what is the maximum stack height?**
   <details><summary>Answer</summary>
   <strong>PDN (NMOS):</strong> the function inside the bar is $A$ AND ($B$ OR $C$), so: transistor A in <em>series</em> with a <em>parallel</em> pair B and C. Three NMOS.<br>
   <strong>PUN (PMOS):</strong> the dual — A in <em>parallel</em> with a <em>series</em> pair B and C. Three PMOS.<br>
   <strong>Six transistors</strong>, maximum stack height 2 in each network. This is an <strong>AND-OR-Invert (AOI)</strong> gate, and it is much cheaper than building it from separate AND, OR and NOT cells (which would take 6 + 6 + 2 = 14). Real cell libraries include AOI and OAI cells precisely for this reason.
   </details>

2. **Why do parallel transistors need no widening, while series ones do?**
   <details><summary>Answer</summary>
   Sizing must handle the <em>worst case</em>. For a parallel network the worst case is exactly one transistor conducting while the others are off — which is the same as the single reference transistor, so no widening is needed. When more conduct, the network is only stronger.<br>
   For a series network, <em>all</em> transistors are always in the path when it conducts, so their resistances always add. With $n$ in series each must be $n$ times wider to keep the total at the reference value.
   </details>

3. **A synthesis tool converts $\overline{A} \cdot \overline{B}$ into a NOR gate. Using De Morgan, what is the alternative, and which would you prefer?**
   <details><summary>Answer</summary>
   $\overline{A} \cdot \overline{B} = \overline{A + B}$ — a NOR gate, 13.2 units of width.<br>
   The alternative is to keep it as two inverters feeding an AND, but AND is itself NAND + inverter, so that is worse still.<br>
   The real move is to change the <em>surrounding</em> logic so the required polarity comes out NAND-shaped. This is what synthesis tools do constantly — pushing inversions through a network with De Morgan's laws to land on NAND-dominated implementations. It is a major reason [[how-computers-work/04-logic/02-boolean-algebra|module 16]] matters practically and not just theoretically.
   </details>

4. **Why does the NOR penalty grow with fan-in while NAND's does not?**
   <details><summary>Answer</summary>
   In NAND, only the <em>NMOS</em> stack grows with fan-in. NMOS is the strong type (baseline width 1.0), so widening it to $n$ is relatively cheap, and the PMOS side stays at 2.8 regardless.<br>
   In NOR, the <em>PMOS</em> stack grows. PMOS already starts at 2.8× for mobility, so a stack of $n$ needs $2.8n$ — the two penalties <strong>multiply</strong>. At fan-in 4 that is 11.2 versus NAND's 2.8, and the gap widens with every extra input.
   </details>

---

## 10. Practice — independent task

**Task:** Design and cost a 2-to-1 multiplexer: $\text{OUT} = (S \cdot B) + (\overline{S} \cdot A)$.

- **(a)** Build it from library cells (NOT, AND2, OR2) and count the transistors using the table in section 4.
- **(b)** Now build the *inverting* version, $\overline{\text{OUT}}$, as a single AOI-style gate with one PDN and one PUN. Draw both networks and count transistors.
- **(c)** Compare the two counts. How much did the single-gate version save?
- **(d)** What is the maximum stack height in your part (b) design? Size every transistor for equal drive against a reference inverter, and compute the total width.
- **(e)** Part (b) produces the inverted output. Give two ways to deal with that, and say which is free.
- **(f)** Extend `gates_lab.py` with your multiplexer's PDN and PUN as lambdas, and use `evaluate()` to confirm the truth table is correct — including that no input combination causes a short or a float.

**Done when:** `evaluate()` accepts your networks without raising, the truth table matches a multiplexer, and you can state the transistor saving from building it as one gate rather than from library cells.

<details><summary>Hint for (e), only if stuck</summary>
Option 1: add an output inverter — costs 2 transistors and a stage of delay.<br>
Option 2: <strong>absorb the inversion into the next stage.</strong> If whatever consumes this signal can be re-expressed to accept the inverted polarity (via De Morgan), the inversion is <em>free</em>. This is exactly what synthesis tools do, and it is why inverting gates being the natural primitive is far less of a problem than it first appears.
</details>

---

## 11. Tradeoffs and limits

- **Static CMOS is not the only style.** Pass-transistor and transmission-gate logic can build XOR and multiplexers far more cheaply — a transmission-gate MUX needs about 6 transistors rather than 12. The cost is degraded output levels and no signal regeneration, so such gates cannot be cascaded freely.
- **The sizing model here is first-order.** It ignores the body effect (which raises $V_{th}$ for transistors higher in a stack, making them weaker still — so real series stacks are *worse* than this model says), internal node capacitances, and velocity saturation.
- **Fan-in limits are practical, not absolute.** Beyond about 4 inputs, a tree of smaller gates beats one large gate on both delay and area.
- **This module says nothing about simplifying the logic itself.** Choosing between equivalent Boolean expressions before you build anything is the subject of the next two modules, and it usually saves more than transistor sizing does.

---

## Before moving on

- [ ] State the two construction rules and explain why the PUN must be the PDN's dual.
- [ ] Derive NAND and NOR truth tables from their transistor arrangements.
- [ ] Explain why CMOS is naturally inverting and what AND really costs.
- [ ] Explain why series stacks need widening and parallel ones do not.
- [ ] Quantify the NOR penalty and trace it back to hole mobility.

**Recap:** Every CMOS gate is a PDN of NMOS and a PUN of PMOS built as duals, so exactly one conducts for any input — making shorts and floating outputs structurally impossible. Series means AND, parallel means OR, and the PUN inverts that structure. CMOS gates are therefore naturally inverting: NAND and NOR are the primitives, AND and OR cost an extra stage. Because series transistors must be widened and PMOS is already 2.8× weak, NOR stacks the weak device and costs 38–79% more than NAND, which is why real libraries and synthesis tools are NAND-dominated.

**Next:** [[how-computers-work/04-logic/02-boolean-algebra|Module 16 — Boolean Algebra]] moves up a level. You can now build any gate; the question becomes which gates to build. Boolean algebra is how you find a cheaper expression for the same function — and De Morgan's laws are the tool that turns NOR-shaped logic into NAND-shaped logic.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/03-transistors/03-cmos|Module 13 — CMOS]] — the inverter this generalises
- [[how-computers-work/02-semiconductors/03-energy-bands|Module 8]] — where the 2.8× originates
- [[how-computers-work/05-combinational/02-adders|Module 20 — Adders]] — where XOR's cost starts to matter
