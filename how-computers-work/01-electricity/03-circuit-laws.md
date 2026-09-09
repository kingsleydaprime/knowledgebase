# Module 3: Circuit Laws (Kirchhoff, Series, Parallel and the Divider)

**[Beginner]** — How to analyse a network rather than a single component. The voltage divider you build here is the literal mechanism behind every logic gate in this course.

## Before you start

- You can apply Ohm's law and the power formulas — [[how-computers-work/01-electricity/02-resistance-and-ohms-law|module 2]].
- You know charge is conserved and that a circuit must form a complete loop — [[how-computers-work/01-electricity/01-charge-current-and-voltage|module 1]].

**After this lesson you will be able to:**

1. State Kirchhoff's two laws and name the conservation principle each one expresses.
2. Reduce a series–parallel resistor network to a single equivalent resistance.
3. Derive the voltage divider formula from Ohm's law rather than recalling it.
4. Explain how a CMOS gate is a voltage divider whose two resistances are switched between "almost zero" and "almost infinite".

**Study route:** work sections 3–5 with a pencil. Section 6 is the payoff — it is where Part II connects to Part IV.

---

## 1. Why this exists (real-world motivation)

Real circuits are not one component. A logic gate has several transistors between the supply and ground; a memory cell has six. To reason about any of them you need to answer two questions about *networks*:

- If several paths meet at a junction, how does current split between them?
- If several components sit in a chain, how does voltage divide across them?

Gustav Kirchhoff answered both in 1845, and the answers are not empirical rules — they follow directly from conservation of charge and conservation of energy. That is why they hold exactly, for every circuit, including ones full of transistors that violate Ohm's law entirely.

---

## 2. Terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **Node** | A junction where two or more components connect; everything electrically joined by wire is one node | A road intersection |
| **Branch** | A single path between two nodes | One road |
| **Loop** | Any closed path you can trace and return to the start | A round trip |
| **Series** | Components in a chain, sharing the same current | Beads on one string |
| **Parallel** | Components across the same two nodes, sharing the same voltage | Lanes of a motorway |
| **Open circuit** | A break — infinite resistance, zero current | A closed valve |
| **Short circuit** | A zero-resistance path — potentially unlimited current | A burst pipe |
| **Equivalent resistance** | The single resistor that would behave identically to a whole network | — |

---

## 3. Kirchhoff's two laws

### Current Law (KCL) — charge is conserved

**The sum of currents entering a node equals the sum of currents leaving it.**

$$\sum I_{\text{in}} = \sum I_{\text{out}}$$

Charge cannot accumulate at a junction — a wire has nowhere to store it. Whatever arrives must depart.

```
              I₁ = 3 A
                 │
                 ▼
        ─────────●─────────>  I₂ = 2 A
                 │
                 ▼
              I₃ = ?

        3 = 2 + I₃   →   I₃ = 1 A
```

### Voltage Law (KVL) — energy is conserved

**The sum of voltage changes around any closed loop is zero.**

$$\sum V_{\text{loop}} = 0$$

A charge carried once around a loop must return to the same potential it started at. Every joule the source gives it is spent somewhere in the loop. If this were not true you could extract free energy by walking a charge in circles.

```
        ┌──── R₁ (drops 4 V) ────┐
        │                        │
      9 V                       R₂ (drops 5 V)
      source                     │
        └────────────────────────┘

        +9 − 4 − 5 = 0  ✓
```

These two laws plus Ohm's law are sufficient to solve any resistive circuit. Everything below is a shortcut derived from them.

---

## 4. Series and parallel

### Series — same current, voltage divides

Components in a chain have **no junction between them**, so by KCL the same current flows through every one.

$$R_{\text{series}} = R_1 + R_2 + \cdots + R_n$$

By KVL the supply voltage is shared out among them, and by Ohm's law each takes a share proportional to its own resistance. **The largest resistor gets the largest share of the voltage.**

### Parallel — same voltage, current divides

Components across the same two nodes all see the **same voltage difference**, since their ends are electrically the same points.

$$\frac{1}{R_{\text{parallel}}} = \frac{1}{R_1} + \frac{1}{R_2} + \cdots$$

For exactly two resistors this reduces to the form worth memorising:

$$R_{\text{parallel}} = \frac{R_1 R_2}{R_1 + R_2}$$

By KCL the total current is the sum of the branch currents, and **the smallest resistor carries the most current.**

> [!NOTE]
> **A parallel combination is always smaller than its smallest member.** Adding another path can only make it easier for current to flow, never harder. If your parallel answer comes out larger than any individual resistor, you have made an arithmetic error — this is a free sanity check, use it every time.

---

## 5. The voltage divider — derive it, don't memorise it

Two resistors in series across a supply. What is the voltage at the point between them?

```
        Vin ──────┐
                  │
                 R₁
                  │
                  ├────── Vout   (the tap)
                  │
                 R₂
                  │
                 GND
```

**The derivation is three lines.** They are in series, so the same current flows through both:

$$I = \frac{V_{in}}{R_1 + R_2}$$

$V_{out}$ is measured across $R_2$, so by Ohm's law:

$$V_{out} = I \times R_2 = \frac{V_{in}}{R_1 + R_2} \times R_2$$

$$\boxed{V_{out} = V_{in} \cdot \frac{R_2}{R_1 + R_2}}$$

**Read the formula as a sentence:** the output is the input, scaled by the fraction of the total resistance that sits below the tap.

### Predict before reading on

$V_{in} = 5$ V, $R_1 = 10$ kΩ, $R_2 = 10$ kΩ. What is $V_{out}$?

Now: $R_1 = 10$ kΩ, $R_2 = 90$ kΩ. And: $R_1 = 90$ kΩ, $R_2 = 10$ kΩ.

<details><summary>Check your answers</summary>

- Equal resistors: $5 \times \frac{10}{20} = \mathbf{2.5}$ V. Equal split, as expected.
- $R_2$ nine times larger: $5 \times \frac{90}{100} = \mathbf{4.5}$ V. Most of the resistance is below the tap, so most of the voltage appears there.
- $R_2$ nine times smaller: $5 \times \frac{10}{100} = \mathbf{0.5}$ V.

**The pattern to carry forward:** make $R_1 \ll R_2$ and the output sits near $V_{in}$; make $R_1 \gg R_2$ and it sits near ground. The ratio is all that matters, not the absolute values.
</details>

---

## 6. Why the divider is the whole point

That last observation is not a curiosity. **It is how every logic gate in this course produces its output.**

Look at what happens as the two resistances become extreme:

| $R_1$ (upper) | $R_2$ (lower) | $V_{out}$ | Interpretation |
| :--- | :--- | :--- | :--- |
| ~0 Ω | ~∞ Ω | ≈ $V_{in}$ | Output pulled **high** — a logic 1 |
| ~∞ Ω | ~0 Ω | ≈ 0 V | Output pulled **low** — a logic 0 |
| ~∞ Ω | ~∞ Ω | undefined | Output floating — **no path either way** |
| ~0 Ω | ~0 Ω | ill-defined | Both paths on — a **short from supply to ground** |

Now suppose you had a component whose resistance you could switch between "essentially zero" and "essentially infinite" using a third, separate terminal.

**That component is a MOSFET.** A CMOS gate is exactly this divider, with a PMOS transistor as $R_1$ and an NMOS transistor as $R_2$, wired so that **exactly one of them conducts at a time**:

- Input low → PMOS conducts, NMOS blocks → output pulled to $V_{in}$ → logic **1**
- Input high → PMOS blocks, NMOS conducts → output pulled to ground → logic **0**

That is an inverter, and rows 1 and 2 of the table are its two states. Row 3 is a **high-impedance output**, used deliberately when several devices share a bus. Row 4 is **short-circuit current** — the momentary path from supply to ground during switching, and one of the reasons a chip consumes power.

You now have the complete mechanism of a logic gate, ten modules before you meet one. Everything between here and [[how-computers-work/04-logic/01-gates-from-transistors|module 14]] exists to explain how a lump of silicon can be persuaded to act as that switchable resistance.

### Loading — the divider's practical trap

Connect something to the tap and you have added a third resistor in parallel with $R_2$, changing the ratio and therefore the output voltage. A divider only reads as calculated when whatever it feeds draws negligible current.

This is why real gates are not built from actual resistors: a resistive divider that is stiff enough to drive a load wastes continuous power, and one that is weak enough to be efficient collapses under load. **CMOS escapes the trap** by making the "on" resistance small only while it is needed and drawing essentially no steady current in either stable state — the subject of [[how-computers-work/03-transistors/03-cmos|module 13]].

---

## 7. Worked example — a complete network

**Setup:** a 12 V supply. $R_1 = 100\ \Omega$ in series with a parallel pair $R_2 = 200\ \Omega$ and $R_3 = 300\ \Omega$.

```
     12 V ──── R₁ (100Ω) ────┬──── R₂ (200Ω) ────┐
                             │                   │
                             └──── R₃ (300Ω) ────┤
                                                GND
```

**Step 1 — collapse the parallel pair.**

$$R_{23} = \frac{200 \times 300}{200 + 300} = \frac{60000}{500} = 120\ \Omega$$

Sanity check: 120 Ω is smaller than both 200 and 300. ✓

**Step 2 — total resistance.** Now it is a simple series chain:

$$R_{total} = 100 + 120 = 220\ \Omega$$

**Step 3 — total current from the supply.**

$$I = \frac{12}{220} = 0.0545 \text{ A} = 54.5 \text{ mA}$$

**Step 4 — voltage across each section.** All 54.5 mA flows through $R_1$:

$$V_{R_1} = 0.0545 \times 100 = 5.45 \text{ V}$$
$$V_{23} = 0.0545 \times 120 = 6.55 \text{ V}$$

KVL check: $5.45 + 6.55 = 12$ V ✓

**Step 5 — split the current between the parallel branches.** Both see 6.55 V:

$$I_{R_2} = \frac{6.55}{200} = 32.7 \text{ mA} \qquad I_{R_3} = \frac{6.55}{300} = 21.8 \text{ mA}$$

KCL check: $32.7 + 21.8 = 54.5$ mA ✓ And the smaller resistor carries more current, as expected.

**Step 6 — power.** Total $P = VI = 12 \times 0.0545 = 0.654$ W. Verify by summing the parts: $I^2R_1 = 0.297$ W, $V^2/R_2 = 0.215$ W, $V^2/R_3 = 0.143$ W. Sum: 0.655 W ✓ (rounding).

### Runnable version

Save as `network_lab.py` and run `python3 network_lab.py`.

```python
def parallel(*resistances):
    """Equivalent resistance of resistors in parallel."""
    return 1.0 / sum(1.0 / r for r in resistances)

def divider(vin, r_upper, r_lower):
    """Voltage at the tap between two series resistors."""
    return vin * r_lower / (r_upper + r_lower)

def solve_network(vin, r1, r2, r3):
    """R1 in series with (R2 parallel R3). Returns a dict of results."""
    r23 = parallel(r2, r3)
    total = r1 + r23
    i_total = vin / total
    v23 = i_total * r23
    return {
        "r_parallel": r23,
        "r_total": total,
        "i_total": i_total,
        "v_r1": i_total * r1,
        "v_parallel": v23,
        "i_r2": v23 / r2,
        "i_r3": v23 / r3,
    }

if __name__ == "__main__":
    n = solve_network(12.0, 100.0, 200.0, 300.0)
    print(f"R2||R3        = {n['r_parallel']:.1f} ohm")
    print(f"R_total       = {n['r_total']:.1f} ohm")
    print(f"I_total       = {n['i_total']*1000:.1f} mA")
    print(f"V across R1   = {n['v_r1']:.2f} V")
    print(f"V across pair = {n['v_parallel']:.2f} V")
    print(f"I through R2  = {n['i_r2']*1000:.1f} mA")
    print(f"I through R3  = {n['i_r3']*1000:.1f} mA")

    # KVL: the two voltage drops must sum to the supply
    assert abs(n["v_r1"] + n["v_parallel"] - 12.0) < 1e-9
    # KCL: the branch currents must sum to the total
    assert abs(n["i_r2"] + n["i_r3"] - n["i_total"]) < 1e-9
    # Parallel combination is smaller than its smallest member
    assert n["r_parallel"] < 200.0

    # The divider extremes that become a logic gate
    print()
    print(f"pull-up   (R1=1, R2=1e9): Vout = {divider(5.0, 1, 1e9):.4f} V  -> logic 1")
    print(f"pull-down (R1=1e9, R2=1): Vout = {divider(5.0, 1e9, 1):.4f} V  -> logic 0")

    print("network_lab: passed")
```

Expected output:

```
R2||R3        = 120.0 ohm
R_total       = 220.0 ohm
I_total       = 54.5 mA
V across R1   = 5.45 V
V across pair = 6.55 V
I through R2  = 32.7 mA
I through R3  = 21.8 mA

pull-up   (R1=1, R2=1e9): Vout = 5.0000 V  -> logic 1
pull-down (R1=1e9, R2=1): Vout = 0.0000 V  -> logic 0
network_lab: passed
```

---

## 8. Common pitfalls and traps

1. **Adding parallel resistors directly.** $R_1 + R_2$ is the series formula. Parallel needs reciprocals, and the answer must come out *smaller* than either.
2. **Forgetting to invert at the end.** $1/R = 1/200 + 1/300$ gives $1/R$, not $R$. Half of all parallel errors stop one step early.
3. **Ignoring loading on a divider.** The formula assumes nothing draws current from the tap. Attach a load and the real output sags.
4. **Assuming components in a picture that *look* adjacent are in series.** Series means no junction between them. If a third wire joins in the middle, they are not in series.
5. **Building a short circuit.** Two "on" paths from supply to ground with nothing between them is not a divider — it is a fault. In CMOS this is a real transient event, not a hypothetical.

---

## 9. Check your understanding

1. **Three 90 Ω resistors in parallel. What is the equivalent resistance?**
   <details><summary>Answer</summary>
   $1/R = 3/90 = 1/30$, so $R = 30\ \Omega$. For $n$ identical resistors in parallel the result is simply $R/n$ — worth recognising on sight.
   </details>

2. **A 9 V supply feeds a divider with $R_1 = 4.7$ kΩ and $R_2 = 2.2$ kΩ. What is $V_{out}$, and how much current does the divider waste continuously?**
   <details><summary>Answer</summary>
   $V_{out} = 9 \times \frac{2200}{6900} = 2.87$ V.<br>
   $I = 9/6900 = 1.30$ mA flowing constantly, dissipating $9 \times 0.0013 = 11.7$ mW — <strong>even when nothing is connected to the tap</strong>. This continuous waste is the reason resistive dividers are unsuitable for logic.
   </details>

3. **Why does KCL hold even for circuits containing transistors, diodes and other components that disobey Ohm's law?**
   <details><summary>Answer</summary>
   Because KCL is a restatement of charge conservation, not a property of resistors. Charge cannot pile up at a node regardless of what the components attached to it do. The same argument makes KVL universal: it restates energy conservation. This is why the two laws are the foundation of <em>all</em> circuit analysis, while Ohm's law is a special case.
   </details>

4. **In the divider table in section 6, why is row 3 (both resistances infinite) described as "undefined" rather than "0 V"?**
   <details><summary>Answer</summary>
   With no conducting path to either the supply or ground, nothing is holding the output node at any particular potential. It retains whatever charge happens to be on it and drifts, and it is highly susceptible to noise coupling from nearby wires. This state is called <strong>high impedance</strong> or <strong>Hi-Z</strong>, and it is genuinely useful: it lets several devices share one bus wire, with all but one holding their outputs at Hi-Z so they do not fight the one that is driving.
   </details>

---

## 10. Practice — independent task

**Task:** Design and analyse a divider that converts a sensor's 0–5 V output down to the 0–3.3 V range a microcontroller ADC can accept safely.

- **(a)** Choose $R_1$ and $R_2$ from E12 standard values (10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82 and decade multiples) so that 5.0 V in gives as close to 3.3 V out as you can manage. State the actual output voltage your pair produces.
- **(b)** Calculate the continuous current the divider draws and the power it wastes.
- **(c)** The ADC input behaves like a 1 MΩ resistance to ground. Recompute the output with that load in parallel with $R_2$. By how many millivolts did your reading shift?
- **(d)** Repeat (a)–(c) with both resistances scaled up by 100×. What improved, and what got worse?
- **(e)** State the tradeoff in one sentence, and say which pair you would actually fit.

**Done when:** you can state the tradeoff between divider stiffness and power consumption in your own words, backed by the two sets of numbers from (b) and (c).

<details><summary>Hint for (c), only if stuck</summary>
The load sits between the tap and ground, which is exactly where $R_2$ is — so they are in parallel. Compute $R_2' = \text{parallel}(R_2, 10^6)$ and rerun the divider formula with $R_2'$. The shift will be tiny for kilohm resistors and obvious for megohm ones, which is the whole point of part (d).
</details>

---

## 11. Tradeoffs and limits

- **This module is purely resistive and purely steady-state.** Add capacitance or inductance and voltages take *time* to settle — [[how-computers-work/01-electricity/04-signals-and-time|module 4]].
- **Series–parallel reduction does not solve every network.** Bridge circuits and other non-reducible topologies need nodal or mesh analysis, applying KCL or KVL systematically. The two laws still suffice; only the shortcut fails.
- **Real components have tolerance.** A 5% resistor pair makes a divider output uncertain by several percent, which matters for measurement and not at all for logic — one more reason digital circuits are easier to build than analogue ones.

---

## Before moving on

- [ ] State KCL and KVL and name the conservation law behind each.
- [ ] Reduce a series–parallel network and check the result with KCL and KVL.
- [ ] Derive the divider formula from Ohm's law without looking it up.
- [ ] Explain, using the four-row table, how switching two resistances between ~0 and ~∞ produces a logic gate.
- [ ] Explain what Hi-Z means and why a shared bus needs it.

**Recap:** KCL (charge conservation) and KVL (energy conservation) hold for all circuits. Series adds resistance and divides voltage; parallel divides current and always reduces resistance. The voltage divider $V_{out} = V_{in} R_2/(R_1+R_2)$ becomes a logic gate the moment the two resistances can be switched between near-zero and near-infinite — which is what a transistor does.

**Next:** [[how-computers-work/01-electricity/04-signals-and-time|Module 4 — Signals and Time]] adds the dimension this module ignored: how long any of this takes to happen.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/03-transistors/03-cmos|Module 13 — CMOS]] — where the divider table becomes a real circuit
- [[how-computers-work/04-logic/01-gates-from-transistors|Module 14 — Gates from Transistors]]
