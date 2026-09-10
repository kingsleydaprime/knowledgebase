# Module 13: CMOS (Why Your Laptop Doesn't Melt)

**[Intermediate]** — The end of Part IV. Two transistors with opposite, complementary weaknesses combine into a gate that has neither. Module 3's divider table becomes a real circuit, and module 5's demands are all met at once.

## Before you start

- You can explain inversion, threshold voltage and the three operating regions — [[how-computers-work/03-transistors/02-mosfet-physics|module 12]].
- You know an NMOS cannot pull an output all the way up — module 12, section 4.
- You remember [[how-computers-work/01-electricity/03-circuit-laws|module 3]]'s four-row divider table and [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]]'s requirement of VTC gain steeper than −1.
- You know $P = \alpha C V^2 f$ was asserted in [[how-computers-work/01-electricity/02-resistance-and-ohms-law|module 2]] but never derived.

**After this lesson you will be able to:**

1. Explain the complementary pull-up / pull-down structure and why exactly one network conducts.
2. Explain why CMOS produces rail-to-rail outputs where a single transistor type cannot.
3. **Derive** $P = \alpha C V^2 f$ from the energy needed to charge a capacitor.
4. Account for all three components of CMOS power and say which dominates when.

**Study route:** section 3 is the circuit, section 5 is the derivation module 2 owed you, section 6 is where every earlier thread ties off.

---

## 1. Why this exists (real-world motivation)

Module 12 ended with a problem. An NMOS transistor pulls *down* beautifully — its source sits at ground, $V_{gs}$ stays at full overdrive, it conducts hard all the way to 0 V. But pulling *up* it starves itself: as the output rises, $V_{gs}$ shrinks, and the device cuts off at $V_{DD} - V_{th}$.

**With this module's numbers, an NMOS-only pull-up reaches 0.6 V out of 1.0 V.** Compare that with [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]]'s requirement: a gate must output *at least* $V_{OH}$, comfortably above the receiver's $V_{IH}$, to leave a usable noise margin. A 0.4 V shortfall destroys it.

Early logic families tried to work around this. **NMOS logic** used a resistor as the pull-up — which works, but a resistor pulling up while an NMOS pulls down means a permanent path from supply to ground whenever the output is low. That is module 3's row 4: a short circuit, burning static power on every gate holding a zero.

**The solution is almost embarrassingly elegant.** PMOS has the exact mirror-image weakness — it pulls up perfectly and pulls down badly. Use each for the job it is good at, and arrange that only one is ever on.

---

## 2. Terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **CMOS** | Complementary MOS — NMOS and PMOS used together | — |
| **Pull-up network (PUN)** | PMOS transistors connecting output to $V_{DD}$ | The tap to the supply |
| **Pull-down network (PDN)** | NMOS transistors connecting output to ground | The drain |
| **Complementary** | Structured so exactly one network conducts at a time | — |
| **Rail-to-rail** | Output reaching fully to $V_{DD}$ and to 0 V | — |
| **Static power** | Consumed while holding a steady state | — |
| **Dynamic power** | Consumed by switching | — |
| **Short-circuit current** | Brief supply-to-ground current while both networks partly conduct | — |
| **Activity factor** ($\alpha$) | Fraction of gates switching per clock cycle | — |
| **Noise margin** | From module 5 — the corruption budget | — |

---

## 3. The CMOS inverter

The simplest CMOS gate is one PMOS above one NMOS, gates tied together as the input, drains tied together as the output.

```
                    V_DD
                     │
                 ┌───┴───┐
        IN ──────┤ PMOS  │   pull-up network
                 └───┬───┘   (conducts when IN is LOW)
                     │
                     ├────────── OUT
                     │
                 ┌───┴───┐
        IN ──────┤ NMOS  │   pull-down network
                 └───┬───┘   (conducts when IN is HIGH)
                     │
                    GND
```

**PMOS conducts when its gate is low; NMOS conducts when its gate is high.** Tie both gates to the same input and they are guaranteed to be in opposite states.

| Input | PMOS | NMOS | Output | Module 3's divider row |
| :--- | :--- | :--- | :--- | :--- |
| LOW (0 V) | **on** (~4 kΩ) | off (~∞) | pulled to $V_{DD}$ → **1** | row 1: $R_1 \approx 0$, $R_2 \approx \infty$ |
| HIGH (1 V) | off (~∞) | **on** (~4 kΩ) | pulled to GND → **0** | row 2: $R_1 \approx \infty$, $R_2 \approx 0$ |

**That is module 3's voltage divider, ten modules later, with the resistances now switchable by a third terminal.** The table you read as an abstract exercise in Part II is the actual operating table of the actual circuit.

And notice what is *absent*: rows 3 and 4 of that table. There is never a moment in the steady state when both are off (floating output) or both are on (short circuit). **The complementary structure makes those states unreachable by construction.**

### Why the output reaches the rails

Each transistor is used only in the direction where it does not starve itself:

- **Pulling low:** the NMOS source is at ground. $V_{gs} = V_{DD}$ throughout, full overdrive all the way down to 0 V.
- **Pulling high:** the PMOS source is at $V_{DD}$. $V_{sg} = V_{DD}$ throughout, full overdrive all the way up to $V_{DD}$.

**Each device is a source-follower in the bad direction and a proper switch in the good one.** By using each only in its good direction, CMOS delivers a genuine 0 V and a genuine $V_{DD}$ — the rail-to-rail behaviour module 5 required, with the full supply available as noise margin.

---

## 4. Meeting module 5's other demand

Module 5 said regeneration needs a voltage transfer characteristic with slope steeper than −1 somewhere, or noise would grow rather than shrink across a chain of gates.

Solving the inverter numerically — finding, for each input, the output where pull-up and pull-down currents balance — gives:

| $V_{in}$ | $V_{out}$ |
| ---: | ---: |
| 0.00 | 1.0000 |
| 0.40 | 1.0000 |
| 0.45 | 0.9914 |
| 0.50 | 0.9000 |
| 0.55 | 0.0086 |
| 0.60 | 0.0000 |
| 1.00 | 0.0000 |

**The measured slope through the transition is −23.5.** Module 5 needed steeper than −1; CMOS delivers more than twenty times that.

**Read what the shape means.** Inputs anywhere from 0 to 0.4 V all produce exactly 1.0 V out. Inputs from 0.6 to 1.0 V all produce exactly 0 V. A 400 mV spread of dirty inputs collapses to a *zero* millivolt spread of outputs. That is noise being squeezed out entirely — the mechanism behind module 5's hundred-stage digital chain arriving uncorrupted.

The flat regions do the restoring; the steep middle makes the boundary between them sharp.

---

## 5. Deriving $P = \alpha C V^2 f$

[[how-computers-work/01-electricity/02-resistance-and-ohms-law|Module 2]] used this equation to explain the end of the megahertz race, and promised a derivation. Here it is.

### Step 1 — charging a capacitor costs $CV^2$, always

The gate's load is a capacitance $C$ — the next gate's input plus wiring. To output a 1, the PMOS charges it from 0 to $V_{DD}$.

Charge delivered: $Q = CV_{DD}$. Every coulomb falls through the full supply voltage, so **energy drawn from the supply is $E = QV_{DD} = CV_{DD}^2$.**

But the energy *stored* on a capacitor is only $\frac{1}{2}CV_{DD}^2$.

**The other half is dissipated as heat in the PMOS channel resistance** — and remarkably, this is true *regardless of the resistance value*. A lower on-resistance charges faster but dissipates exactly the same energy. You cannot optimise it away.

### Step 2 — discharging dissipates the stored half

To output a 0, the NMOS connects the capacitor to ground. The stored $\frac{1}{2}CV_{DD}^2$ is dissipated in the NMOS channel. None returns to the supply.

### Step 3 — one full cycle costs $CV^2$

$$E_{cycle} = \underbrace{\tfrac{1}{2}CV_{DD}^2}_{\text{charging loss}} + \underbrace{\tfrac{1}{2}CV_{DD}^2}_{\text{discharging loss}} = CV_{DD}^2$$

### Step 4 — scale to a chip

With $N$ gates, clock frequency $f$, and activity factor $\alpha$ (the fraction completing a full cycle each clock):

$$\boxed{P_{dynamic} = \alpha\, N\, C\, V_{DD}^2\, f}$$

**The equation module 2 asserted is now derived.** And its two crucial features are visible in the derivation: $V$ appears **squared** because charge scales with voltage *and* each charge falls through that voltage; $f$ appears **linearly** because it simply counts how often you pay.

> [!NOTE]
> **Why CMOS burns nothing when idle.** Stop the clock and $f = 0$, so dynamic power goes to zero. In the steady state one network is fully off, so there is no path from supply to ground — no static current beyond leakage.
>
> **This is the property that made billion-transistor chips possible**, and it is exactly what [[how-computers-work/03-transistors/01-what-a-transistor-is|module 11]]'s 10 kW-versus-1 mW calculation was pointing at. It is also why **clock gating** — switching off the clock to idle blocks — is one of the most effective power optimisations available.

---

## 6. Where the power actually goes

Three components, for a billion gates at 3 GHz, 1 fF load, $\alpha = 0.05$:

| Component | Magnitude | When it dominates |
| :--- | ---: | :--- |
| **Dynamic** ($\alpha CV^2f$) | 150 W | Any active chip |
| **Static leakage** | 1.0 mW | Idle chips, small geometries |
| **Short-circuit** | few % of dynamic | Slow input edges |

**Short-circuit current** deserves a note. During a transition the input passes through the region where *both* transistors are partly on — module 3's row 4, briefly reachable after all. A pulse of current flows straight from supply to ground.

It is small when edges are fast and grows when they are slow, which is a concrete reason to keep edges sharp: a slowly changing input spends longer in the forbidden zone, burning more power and — as module 5 noted — producing an undefined output while it does.

The leakage figure above uses an idealised 1 pA per device. **In real deep-submicron processes leakage is a far larger fraction** — at 65 nm and below it became a serious share of total power, which is why modern chips **power-gate** entire regions rather than merely idling them.

---

## 7. Predict before reading on

A designer builds a CMOS inverter with NMOS and PMOS at the *same* $W/L$.

**What goes wrong?**

<details><summary>Check your answer</summary>

**The gate becomes asymmetric.** From [[how-computers-work/02-semiconductors/03-energy-bands|module 8]], hole mobility is 2.8× lower than electron mobility, so an equally sized PMOS drives 2.8× less current.

Consequences:

- **Rise time is ~2.8× slower than fall time.** The gate pulls down briskly and up sluggishly.
- **The switching threshold shifts below $V_{DD}/2$**, because the stronger NMOS wins the current balance at a lower input voltage.
- **Noise margins become unequal** — the shifted threshold eats into one side's margin.

**The fix is to make the PMOS ~2.8× wider**, which is exactly the sizing used in this module's lab and visible as the taller P-row in every standard cell layout.

**Trace where that number came from:** valence-band structure gives holes a larger effective mass (module 8) → lower mobility → less current per unit width (module 12) → wider PMOS transistors → an asymmetric layout you can see in a die photograph. Five modules, one number.
</details>

---

## 8. Worked example — runnable

Save as `cmos_lab.py` and run `python3 cmos_lab.py`.

```python
V_DD   = 1.0        # supply, volts
V_TH_N = 0.4        # NMOS threshold
V_TH_P = 0.4        # PMOS threshold magnitude
K_N    = 200e-6     # NMOS process transconductance, A/V^2
K_P    = K_N / 2.8  # PMOS is weaker -- hole mobility (module 8)

def fet_current(v_gs, v_ds, k, v_th, w_over_l):
    """Long-channel current magnitude for one transistor."""
    v_ov = v_gs - v_th
    if v_ov <= 0:
        return 0.0
    if v_ds < v_ov:
        return k * w_over_l * (v_ov * v_ds - v_ds**2 / 2)
    return 0.5 * k * w_over_l * v_ov**2

def inverter_output(v_in, wl_n=1.0, wl_p=2.8, v_dd=V_DD):
    """Solve for the output voltage where pull-up and pull-down currents balance."""
    lo, hi = 0.0, v_dd
    for _ in range(200):
        mid = (lo + hi) / 2
        i_down = fet_current(v_in, mid, K_N, V_TH_N, wl_n)          # NMOS to ground
        i_up   = fet_current(v_dd - v_in, v_dd - mid, K_P, V_TH_P, wl_p)  # PMOS to VDD
        if i_down > i_up:
            hi = mid      # pull-down winning, output must be lower
        else:
            lo = mid
    return (lo + hi) / 2

def nmos_only_pullup(v_dd=V_DD, v_th=V_TH_N):
    """The best an NMOS pass transistor can do pulling UP: it starves itself."""
    return v_dd - v_th

def switching_energy(capacitance_f, supply_v):
    """Energy drawn from the supply for one full 0->1->0 cycle: C*V^2."""
    return capacitance_f * supply_v**2

def dynamic_power(n_gates, capacitance_f, supply_v, frequency_hz, activity):
    return activity * n_gates * capacitance_f * supply_v**2 * frequency_hz

if __name__ == "__main__":
    print(f"V_DD = {V_DD} V, V_th = {V_TH_N} V, PMOS is {K_N/K_P:.1f}x weaker per unit width")
    print()

    print("inverter transfer characteristic (W/L: NMOS 1.0, PMOS 2.8):")
    for v_in in [0.0, 0.2, 0.4, 0.45, 0.5, 0.55, 0.6, 0.8, 1.0]:
        print(f"  V_in = {v_in:.2f} -> V_out = {inverter_output(v_in):.4f}")
    print()

    # Module 5 required |slope| > 1 somewhere. Measure it across the transition.
    v1, v2 = 0.48, 0.52
    slope = (inverter_output(v2) - inverter_output(v1)) / (v2 - v1)
    print(f"slope through the transition ({v1} -> {v2} V) = {slope:+.2f}")
    print(f"  module 5 needs |slope| > 1 for noise to be squeezed: {abs(slope) > 1}")
    print()

    print("rail-to-rail output -- the reason CMOS needs BOTH types:")
    print(f"  CMOS inverter, input low  -> output = {inverter_output(0.0):.4f} V")
    print(f"  CMOS inverter, input high -> output = {inverter_output(1.0):.4f} V")
    print(f"  NMOS-only pull-up would reach only {nmos_only_pullup():.4f} V"
          f" (loses V_th = {V_TH_N} V)")
    print()

    print("where the power goes:")
    C_GATE = 1e-15          # 1 fF per gate load
    N_GATES = 1e9
    FREQ = 3e9
    ALPHA = 0.05
    e = switching_energy(C_GATE, V_DD)
    print(f"  energy per full 0->1->0 cycle = C*V^2 = {e*1e15:.2f} fJ")
    print(f"    of which C*V^2/2 = {e/2*1e15:.2f} fJ is stored, then dissipated on discharge")
    p_dyn = dynamic_power(N_GATES, C_GATE, V_DD, FREQ, ALPHA)
    print(f"  {N_GATES:.0e} gates at {FREQ/1e9:.0f} GHz, activity {ALPHA}:")
    print(f"    dynamic power = {p_dyn:.1f} W")
    p_static = N_GATES * 1e-12 * V_DD
    print(f"    static leakage = {p_static*1e3:.1f} mW  ({100*p_static/p_dyn:.3f}% of dynamic)")

    assert inverter_output(0.0) > 0.99 * V_DD      # full rail high
    assert inverter_output(1.0) < 0.01 * V_DD      # full rail low
    assert abs(slope) > 1                          # module 5's gain requirement
    assert nmos_only_pullup() < inverter_output(0.0)
    print()
    print("cmos_lab: passed")
```

Expected output:

```
V_DD = 1.0 V, V_th = 0.4 V, PMOS is 2.8x weaker per unit width

inverter transfer characteristic (W/L: NMOS 1.0, PMOS 2.8):
  V_in = 0.00 -> V_out = 1.0000
  V_in = 0.20 -> V_out = 1.0000
  V_in = 0.40 -> V_out = 1.0000
  V_in = 0.45 -> V_out = 0.9914
  V_in = 0.50 -> V_out = 0.9000
  V_in = 0.55 -> V_out = 0.0086
  V_in = 0.60 -> V_out = 0.0000
  V_in = 0.80 -> V_out = 0.0000
  V_in = 1.00 -> V_out = 0.0000

slope through the transition (0.48 -> 0.52 V) = -23.47
  module 5 needs |slope| > 1 for noise to be squeezed: True

rail-to-rail output -- the reason CMOS needs BOTH types:
  CMOS inverter, input low  -> output = 1.0000 V
  CMOS inverter, input high -> output = 0.0000 V
  NMOS-only pull-up would reach only 0.6000 V (loses V_th = 0.4 V)

where the power goes:
  energy per full 0->1->0 cycle = C*V^2 = 1.00 fJ
    of which C*V^2/2 = 0.50 fJ is stored, then dissipated on discharge
  1e+09 gates at 3 GHz, activity 0.05:
    dynamic power = 150.0 W
    static leakage = 1.0 mW  (0.001% of dynamic)

cmos_lab: passed
```

---

## 9. Beyond the inverter — a preview

The inverter generalises directly. **Any logic function** is built by arranging the two networks as duals of each other:

- **Pull-down network (NMOS):** transistors in **series** implement AND; in **parallel** implement OR.
- **Pull-up network (PMOS):** the exact opposite — series for OR, parallel for AND.

Because PMOS conducts on a low input, the pull-up network automatically computes the complement, which is why **CMOS gates are naturally inverting**. NAND and NOR are the primitives; AND and OR cost an extra inverter stage.

That is [[how-computers-work/04-logic/01-gates-from-transistors|module 15]]'s subject, along with a consequence you can already predict: since PMOS devices are the weak ones, you want as few of them in *series* as possible — which makes **NAND cheaper and faster than NOR**, and is why real chip libraries are built predominantly from NAND.

---

## 10. Common pitfalls and traps

1. **Thinking CMOS uses no power.** It uses no *static* power. Dynamic power at 150 W is the entire thermal design problem.
2. **Forgetting the PMOS width factor.** Equal sizing gives an asymmetric, slower gate with unequal noise margins.
3. **Believing the charging loss depends on the on-resistance.** It is $\frac{1}{2}CV^2$ regardless. Lower resistance buys speed, not efficiency.
4. **Assuming both networks are never on together.** They are, briefly, during every transition — that is short-circuit current, and slow edges make it worse.
5. **Thinking leakage is negligible.** It was, above 90 nm. It is not now, which is why power gating exists.
6. **Expecting non-inverting gates to be cheap.** CMOS is naturally inverting; AND is a NAND plus an inverter, so it is bigger and slower than NAND.

---

## 11. Check your understanding

1. **Why is the energy dissipated when charging a capacitor independent of the resistance doing the charging?**
   <details><summary>Answer</summary>
   The supply delivers charge $Q = CV$ with every coulomb falling through the full voltage $V$, so it always provides $CV^2$. The capacitor always ends up storing $\frac{1}{2}CV^2$. The difference, $\frac{1}{2}CV^2$, must have gone to heat — and that argument never mentions resistance.<br>
   A smaller resistance means a larger current for a shorter time; the $I^2R$ integral comes out identical. The only way to reduce the loss is to lower $C$ or $V$ — which is precisely why the industry pursued smaller geometries and lower supply voltages, and why hitting the $V$ floor in module 12 was so consequential.
   </details>

2. **Why does CMOS have essentially no static power, when an NMOS-with-resistor-pull-up gate does?**
   <details><summary>Answer</summary>
   In a resistive-pull-up gate, whenever the output is low the NMOS conducts and the resistor is still connected to $V_{DD}$ — a permanent path from supply to ground. Every gate holding a zero burns power continuously.<br>
   In CMOS the pull-up is a PMOS that is <em>fully off</em> in that state. Both stable states have exactly one network conducting and the other blocking, so no path exists. Static current is limited to leakage.
   </details>

3. **A chip runs at 150 W dynamic power. The designers halve the activity factor with clock gating. What happens, and what does it not fix?**
   <details><summary>Answer</summary>
   Dynamic power halves to 75 W, since $P \propto \alpha$ linearly.<br>
   It does <strong>not</strong> reduce leakage — those gates are still powered, and their transistors still leak whether clocked or not. As geometries shrink and leakage grows as a fraction of total power, clock gating alone becomes insufficient, which is why <strong>power gating</strong> (cutting the supply to idle blocks entirely) was introduced. Clock gating attacks $\alpha$; only power gating attacks leakage.
   </details>

4. **The lab's transfer characteristic shows inputs from 0 to 0.4 V all producing exactly 1.0 V out. Why is that flatness as important as the steep middle?**
   <details><summary>Answer</summary>
   The steep region makes the <em>boundary</em> between 0 and 1 sharp, but the flat regions are what actually perform the restoration. A 400 mV spread of dirty inputs maps to a single output value — noise removed entirely, not merely reduced.<br>
   A gate with a steep transition but sloped "flat" regions would pass some input variation through to its output, and that residue would accumulate along a chain. Module 5's promise that a million-gate chain is as reliable as a one-gate chain depends on the flat regions being genuinely flat.
   </details>

---

## 12. Practice — independent task

**Task:** You are budgeting power for a processor design at $V_{DD} = 1.0$ V.

- **(a)** 500 million gates, 1.5 fF average load, 2.5 GHz, activity 0.08. Compute dynamic power.
- **(b)** The thermal budget is 95 W. Does the design fit? If not, by how much must $\alpha$ fall?
- **(c)** Instead of reducing $\alpha$, the team considers dropping $V_{DD}$ to 0.9 V. Compute the new dynamic power. Why is this more effective per unit of change than reducing $\alpha$?
- **(d)** Lowering $V_{DD}$ reduces overdrive $V_{ov} = V_{DD} - V_{th}$. With $V_{th} = 0.4$ V, compute the change in saturation current (which goes as $V_{ov}^2$) and hence the approximate change in gate delay. What must happen to the clock?
- **(e)** Recompute dynamic power at 0.9 V *and* the reduced clock from (d). Is the design now within budget, and what did it cost in performance?
- **(f)** Leakage is 40 nA per gate at $V_{th} = 0.4$ V, and rises 10× per 70 mV of $V_{th}$ reduction. Compute total leakage power at $V_{th}$ = 0.4 V and 0.3 V. At which threshold does leakage exceed 10% of your answer to (e)?
- **(g)** Write `power_budget(n_gates, c_load, v_dd, freq, alpha, v_th)` returning dynamic, leakage and total power, and use it to find a $(V_{DD}, V_{th})$ pair meeting 95 W with the highest clock you can.

**Done when:** you have a defensible $(V_{DD}, V_{th}, f)$ operating point within 95 W, and can explain the two competing pressures on $V_{th}$ — drive current pulling it down, leakage pushing it up.

<details><summary>Hint for (d), only if stuck</summary>
At $V_{DD}$ = 1.0 V, $V_{ov} = 0.6$ V. At 0.9 V, $V_{ov} = 0.5$ V. Saturation current scales as $V_{ov}^2$, so current falls by $(0.5/0.6)^2 = 0.69$ — a 31% reduction.<br>
Delay is roughly inversely proportional to drive current, so delay rises by $1/0.69 = 1.44×$ and the clock must fall by about the same factor. Then recompute: you saved 19% on $V^2$ but gave up 31% of your clock. Whether that is a good trade is exactly the judgement part (e) asks for.
</details>

---

## 13. Tradeoffs and limits

- **The lab's inverter model is long-channel.** Real short-channel devices have velocity saturation, and the transfer curve is less abrupt than the numerical solve suggests. The qualitative conclusion — high gain, rail-to-rail, flat regions — holds.
- **Leakage here is idealised.** At 1 pA per device it looks negligible. Real deep-submicron leakage is orders of magnitude higher and is a first-order design concern.
- **Wire capacitance increasingly dominates.** As transistors shrank, interconnect stopped being free. In modern chips a large share of dynamic power is spent driving wires, not gates.
- **CMOS is not the only logic style.** Pass-transistor logic, dynamic (precharged) logic and current-mode logic all trade robustness for speed or area. CMOS won on robustness and static power, not on every metric.

---

## Before moving on

**This is the end of Part IV.** You are ready for Part V when you can, closed-book:

- [ ] Draw a CMOS inverter and give its truth table with the state of both transistors.
- [ ] Explain why the output reaches both rails, and why a single transistor type cannot manage it.
- [ ] Map the inverter's two states onto module 3's divider table, and say why rows 3 and 4 are unreachable in the steady state.
- [ ] Derive $P = \alpha CV^2f$ from the energy to charge a capacitor.
- [ ] Name the three power components and say when each dominates.
- [ ] Explain the 2.8× PMOS sizing and trace the number back to module 8.

**Recap:** CMOS pairs a PMOS pull-up network with an NMOS pull-down network so exactly one conducts in each stable state. Each transistor is used only in the direction where it does not starve itself, giving genuine rail-to-rail outputs and a transfer characteristic with a slope around −23 — far exceeding module 5's requirement. Because no path from supply to ground exists in either stable state, static power is limited to leakage, and all real power is dynamic: $\alpha CV^2f$, derived from the $CV^2$ cost of one charge-discharge cycle.

**Next:** [[how-computers-work/04-logic/01-gates-from-transistors|Module 15 — Gates from Transistors]] begins Part V. You have a working switch and a working inverter; now build NAND, NOR and the rest, and find out why NAND is the gate real chips are made of.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/01-electricity/03-circuit-laws|Module 3]] — the divider table this circuit implements
- [[how-computers-work/01-electricity/05-the-digital-abstraction|Module 5]] — the gain and rail-to-rail requirements now met
- [[how-computers-work/01-electricity/02-resistance-and-ohms-law|Module 2]] — where the power equation was first used
- [[computer-architecture/12-performance|computer-architecture/performance]] — the architectural consequences of the power wall
