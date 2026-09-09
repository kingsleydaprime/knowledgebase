# Module 11: What a Transistor Is (The Third Terminal)

**[Intermediate]** — Part IV begins. Module 10 ended with a device that rectifies but cannot compute, because two terminals give no way for one signal to control another. This module adds the third terminal.

## Before you start

- You can explain how a depletion region forms and why its width responds to applied voltage — [[how-computers-work/02-semiconductors/05-pn-junctions|module 10]].
- You know N-type and P-type silicon and why ionised dopants are immobile — [[how-computers-work/02-semiconductors/04-doping|module 9]].
- You know SiO₂ has a 9 eV band gap and grows natively on silicon — [[how-computers-work/02-semiconductors/03-energy-bands|module 8]].
- You know what the [[how-computers-work/01-electricity/03-circuit-laws|voltage divider]] needs: a switchable resistance.

**After this lesson you will be able to:**

1. State precisely what a third terminal buys that no two-terminal device can provide.
2. Distinguish amplification from switching, and explain why digital logic only needs the second.
3. Explain the structural and operating difference between a BJT and a MOSFET.
4. Explain, with a calculation, why digital computing is built on MOSFETs rather than BJTs.

**Study route:** section 3 is the conceptual core. Section 6 is the calculation that decided the industry — do not skip it.

---

## 1. Why this exists (real-world motivation)

You have accumulated a precise shopping list across three parts:

- **[[how-computers-work/01-electricity/03-circuit-laws|Module 3]]:** a component whose resistance switches between ~0 and ~∞, controlled by a *third* terminal, gives you a logic gate.
- **[[how-computers-work/01-electricity/05-the-digital-abstraction|Module 5]]:** it must pull hard to the rails, switch sharply (VTC gain steeper than −1), and leak little.
- **[[how-computers-work/02-semiconductors/05-pn-junctions|Module 10]]:** you have a barrier whose width responds to voltage — but only two terminals, so nothing external can steer it.

**Everything is present except a way to reach in and control the barrier from outside the conducting path.**

The transistor is that mechanism, and it is the most consequential invention of the twentieth century. Not because it does anything a vacuum tube could not — it does roughly the same job — but because it does it in a solid piece of silicon that can be manufactured a billion at a time, on a wafer, by a photographic process.

---

## 2. Terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **Transistor** | A three-terminal device where one terminal controls current between the other two | A tap: the handle controls the flow |
| **Amplification** | A small input producing a proportionally larger output | A lever |
| **Switching** | Using the device only fully on or fully off | A light switch |
| **BJT** | Bipolar Junction Transistor — **current**-controlled, three doped regions | — |
| **MOSFET** | Metal-Oxide-Semiconductor Field-Effect Transistor — **voltage**-controlled, insulated gate | — |
| **Base / Emitter / Collector** | The BJT's three terminals | — |
| **Gate / Source / Drain** | The MOSFET's three terminals | Tap handle / inlet / outlet |
| **Body (bulk)** | The MOSFET's substrate — a fourth terminal, usually tied to a rail | — |
| **Gate oxide** | The thin SiO₂ layer insulating the gate from the channel | — |
| **Channel** | The conducting path formed between source and drain | — |
| **Bipolar** | Using *both* electrons and holes | — |
| **Unipolar** | Using only one carrier type | — |

---

## 3. What a third terminal actually buys

This is the conceptual heart of the module.

**A two-terminal device is a fixed function.** Whatever a diode does is determined entirely by the voltage across its own two connections. Current in, current out — and the thing carrying the signal *is* the thing being controlled. There is no separation.

```
   TWO TERMINALS — no control possible

        ──────▷|──────
         A            B
   Current is a fixed f(V_AB). Nothing else has a say.


   THREE TERMINALS — control separated from conduction

                  C  ← control terminal
                  │
        ──────────█──────────
         A                  B
   Current from A to B is a function of the voltage (or current) at C.
   The signal at C steers a current it is not part of.
```

**That separation is everything.** It means:

1. **One circuit can control another.** The output of one gate drives the control terminal of the next. That is what makes gates *composable*, and composition is what turns a switch into a computer.
2. **A weak signal can steer a strong one.** The control terminal need not supply the power that flows between the other two.
3. **Signals can be regenerated.** Recall [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]]: a gate does not amplify its input, it *reads* it and generates a fresh clean output from the supply. Only a three-terminal device can do that, because the output must be sourced from somewhere other than the input.

**Point 3 is worth pausing on.** The digital abstraction's entire promise — that noise never accumulates across a million stages — rests on the output being drawn from the power supply rather than from the input signal. A two-terminal device physically cannot arrange that. **The transistor is what makes the digital abstraction implementable rather than merely desirable.**

---

## 4. Amplifier or switch?

A transistor's control terminal varies the current between the other two *continuously*. That gives two distinct ways to use it.

```
   AMPLIFIER (analogue)              SWITCH (digital)
   operate in the middle             operate at the extremes

   I ▲          ╱                    I ▲ ═══════╗ ← fully ON
     │        ╱                        │        ║   (saturation)
     │      ╱  ← small input change     │        ║
     │    ╱      -> large output        │        ║
     │  ╱        change                 │        ║
     │╱                                 │════════╝ ← fully OFF
     └──────────────> V_control         └──────────────> V_control
        stay in the linear region          pass through the
        deliberately                       middle as fast as possible
```

**Analogue design lives in the middle of that curve.** Radio, audio and sensor circuits all exploit the proportional region.

**Digital design treats the middle as a hazard.** It is the forbidden zone from module 5 — the place where the output is undefined, *and* where both conduction paths are partly on, so current flows straight from supply to ground. A digital transistor should cross that region as fast as possible and spend all its time at one extreme or the other.

> [!NOTE]
> **This reframes what a logic gate is.** A gate is not a small computer. It is a transistor deliberately operated in the two states where it behaves *worst* as an amplifier — hard off and hard on — because those are the states where its behaviour is reliable and reproducible.
>
> Digital design is analogue design that has thrown away the interesting part in exchange for never having to think about it again. That is module 5's bargain, made concrete in silicon.

---

## 5. The two families

### BJT — current-controlled

A BJT is three doped regions in a row: **NPN** or **PNP**. It is two PN junctions sharing a very thin middle layer.

```
        NPN BJT

    emitter    base    collector
      N⁺    │    P    │     N
    ────────┼─────────┼────────
            ↑         ↑
        junction 1  junction 2
              (base is very thin)
```

Forward-bias the emitter-base junction and electrons are injected into the base. **Because the base is extremely thin and lightly doped, most of them shoot straight through** and are collected by the reverse-biased collector junction rather than recombining.

A small base current therefore controls a much larger collector current:

$$I_C = \beta I_B \qquad \beta \approx 50\text{–}200$$

It is **bipolar** because both electrons and holes participate. BJTs are fast, offer high gain, and are excellent analogue amplifiers. They remain the right choice for high-frequency and precision analogue work.

**But the base terminal draws continuous current.** That is the fatal property, and section 6 shows why.

### MOSFET — voltage-controlled

A MOSFET is a completely different idea.

```
        N-channel MOSFET

              GATE (metal or polysilicon)
        ┌───────────────────┐
        │███████████████████│  ← gate
        ├───────────────────┤
        │░░░ gate oxide ░░░░│  ← SiO2 insulator (~1-2 nm modern)
    ────┴───────────────────┴────
     N⁺ │                   │ N⁺
    source                  drain
        └─── channel forms ─┘
              here
     ─────────────────────────────
              P-type body
```

**The gate is separated from the silicon by an insulator.** It does not touch the conducting path at all. Applying a voltage to it creates an **electric field** that reaches through the oxide and pulls carriers into a thin layer beneath — forming or destroying a conducting **channel** between source and drain.

This is why it is a *field-effect* transistor: the field does the work, not a current.

**Consequences:**

- **No steady gate current.** The gate is a capacitor plate. Current flows only while its voltage is *changing*.
- **Unipolar.** An N-channel MOSFET conducts by electrons only; P-channel by holes only.
- **Symmetric structure.** Source and drain are physically identical; which is which is decided by the voltages you apply.

> [!NOTE]
> **"MOS" is a historical name.** The gate was originally metal; it has been polysilicon for decades, and since ~2007 high-k dielectrics have replaced pure SiO₂ in leading-edge processes. The acronym stuck. The **O** — the insulator — is the part that still matters, and it is silicon's native oxide from module 8 doing the job it turned out to be perfect for.

---

## 6. The calculation that decided the industry

BJTs came first, work well, and were used to build real computers. Why did essentially all digital logic move to MOSFETs?

**Because of what it costs to do nothing.**

A BJT holding its "on" state needs continuous base current. With $\beta = 100$, holding 1 mA of collector current requires **10 μA flowing into the base, permanently.** Stop supplying it and the transistor turns off.

A MOSFET holding its "on" state needs **no current at all**. Charge the gate capacitance once and it stays charged; leakage through the oxide is around a picoamp.

**Now scale it.**

| Gate count | Current-controlled | MOSFET | Ratio |
| ---: | ---: | ---: | ---: |
| $10^3$ | 0.01 W | 1 nW | $10^7$ |
| $10^6$ | 10 W | 1 μW | $10^7$ |
| $10^9$ | **10 kW** | 1 mW | $10^7$ |
| $10^{10}$ | 100 kW | 10 mW | $10^7$ |

**A billion current-controlled gates would burn about 10 kilowatts doing nothing** — not computing, not switching, merely holding their state. That is a domestic electric heater's entire output, per chip, at idle.

**The same billion MOSFETs: about a milliwatt.**

This is not a marginal engineering preference. **It is the difference between a technology that scales to a billion devices and one that does not.** Bipolar logic families like ECL were genuinely faster per gate, and they were used where speed justified the power — Cray supercomputers ran on ECL. But they could never have reached a billion transistors on one die, because the power to *hold state* grows linearly with device count and has no upper bound.

MOSFETs decouple the two: **you pay for switching, not for holding.** That is what makes [[how-computers-work/01-electricity/02-resistance-and-ohms-law|module 2]]'s $P = \alpha C V^2 f$ the whole story — the equation has no term for static power precisely because a MOSFET has essentially none. Everything about modern chip design follows from that absence.

---

## 7. Predict before reading on

A modern gate oxide is about 1.2 nm thick. One molecular layer of SiO₂ is about 0.357 nm.

**How many molecules thick is the insulator, and what problem would you expect?**

<details><summary>Check your answer</summary>

$$1.2 / 0.357 \approx 3.4 \text{ molecular layers}$$

**The insulator separating the gate from the channel is between three and four molecules thick.**

The problem is **quantum tunnelling**. At that thickness, electrons have a significant probability of passing straight through the oxide despite lacking the energy to cross its 9 eV barrier — the same tunnelling that produces Zener breakdown in [[how-computers-work/02-semiconductors/05-pn-junctions|module 10]].

Gate leakage stopped being negligible and became a major component of static power. **This is why oxide thinning stopped around 2007**, and why the industry switched to **high-k dielectrics** — materials like hafnium oxide with a higher dielectric constant, which give the same field-coupling strength at a *physically thicker* layer, restoring the tunnelling margin.

You predicted a real historical inflection point from two numbers.
</details>

---

## 8. Worked example — runnable

Save as `transistor_lab.py` and run `python3 transistor_lab.py`.

```python
# How much power does it cost merely to HOLD a logic state?

SIO2_LAYER_NM = 0.357      # thickness of one SiO2 molecular layer, nm

def bjt_base_current(collector_current_a, beta=100):
    """A BJT is current-controlled: holding it on costs continuous base current."""
    return collector_current_a / beta

def static_power_to_hold(n_gates, current_per_gate_a, supply_v):
    """Power burned doing nothing at all -- just maintaining state."""
    return n_gates * current_per_gate_a * supply_v

def oxide_layers(thickness_nm):
    """How many molecular layers of SiO2 is a gate oxide?"""
    return thickness_nm / SIO2_LAYER_NM

if __name__ == "__main__":
    print("A BJT is CURRENT-controlled -- the base draws current continuously:")
    for ic in (1e-3, 10e-3):
        for beta in (50, 100, 200):
            ib = bjt_base_current(ic, beta)
            print(f"  Ic = {ic*1000:5.1f} mA, beta = {beta:3d}"
                  f"  ->  Ib = {ib*1e6:7.2f} uA of continuous base current")
    print()

    print("A MOSFET is VOLTAGE-controlled -- the gate is insulated:")
    print("  gate leakage is roughly 1 pA; there is no steady gate current at all")
    print()

    # The scaling argument that decided the industry
    BJT_HOLD = bjt_base_current(1e-3, 100)   # 10 uA per gate
    FET_HOLD = 1e-12                         # 1 pA of gate leakage
    SUPPLY = 1.0

    print(f"{'gates':>14s} {'BJT-style':>16s} {'MOSFET':>16s} {'ratio':>12s}")
    for n in (1e3, 1e6, 1e9, 1e10):
        p_bjt = static_power_to_hold(n, BJT_HOLD, SUPPLY)
        p_fet = static_power_to_hold(n, FET_HOLD, SUPPLY)
        print(f"{n:14.0e} {p_bjt:13.3e} W {p_fet:13.3e} W {p_bjt/p_fet:12.0e}")

    p_bjt_1e9 = static_power_to_hold(1e9, BJT_HOLD, SUPPLY)
    print()
    print(f"a billion current-controlled gates would burn {p_bjt_1e9/1e3:.0f} kW")
    print(f"  doing nothing -- not switching, just holding their state")
    print(f"the same count of MOSFETs: {static_power_to_hold(1e9, FET_HOLD, SUPPLY)*1e3:.3f} mW")
    print()

    print("gate oxide thickness, in SiO2 molecular layers:")
    for t, era in [(100.0, "1970s"), (10.0, "1990s"), (1.2, "mid-2000s limit")]:
        print(f"  {t:6.1f} nm ({era:15s}) = {oxide_layers(t):6.1f} layers")

    assert bjt_base_current(1e-3, 100) == 1e-5
    assert static_power_to_hold(1e9, BJT_HOLD, 1.0) > 1e3   # kilowatts
    assert static_power_to_hold(1e9, FET_HOLD, 1.0) < 1e-2  # milliwatts
    assert oxide_layers(1.2) < 4
    print()
    print("transistor_lab: passed")
```

Expected output:

```
A BJT is CURRENT-controlled -- the base draws current continuously:
  Ic =   1.0 mA, beta =  50  ->  Ib =   20.00 uA of continuous base current
  Ic =   1.0 mA, beta = 100  ->  Ib =   10.00 uA of continuous base current
  Ic =   1.0 mA, beta = 200  ->  Ib =    5.00 uA of continuous base current
  Ic =  10.0 mA, beta =  50  ->  Ib =  200.00 uA of continuous base current
  Ic =  10.0 mA, beta = 100  ->  Ib =  100.00 uA of continuous base current
  Ic =  10.0 mA, beta = 200  ->  Ib =   50.00 uA of continuous base current

A MOSFET is VOLTAGE-controlled -- the gate is insulated:
  gate leakage is roughly 1 pA; there is no steady gate current at all

         gates        BJT-style           MOSFET        ratio
         1e+03     1.000e-02 W     1.000e-09 W        1e+07
         1e+06     1.000e+01 W     1.000e-06 W        1e+07
         1e+09     1.000e+04 W     1.000e-03 W        1e+07
         1e+10     1.000e+05 W     1.000e-02 W        1e+07

a billion current-controlled gates would burn 10 kW
  doing nothing -- not switching, just holding their state
the same count of MOSFETs: 1.000 mW

gate oxide thickness, in SiO2 molecular layers:
   100.0 nm (1970s          ) =  280.1 layers
    10.0 nm (1990s          ) =   28.0 layers
     1.2 nm (mid-2000s limit) =    3.4 layers

transistor_lab: passed
```

---

## 9. Common pitfalls and traps

1. **Thinking the MOSFET gate "injects" carriers into the channel.** It cannot — it is insulated. It creates a *field* that attracts carriers already present in the body.
2. **Assuming BJTs are obsolete.** They dominate high-frequency analogue, precision amplifiers and power switching. They lost *digital logic*, not electronics.
3. **Confusing the control variables.** BJT: current controls current. MOSFET: voltage controls current. This single difference drives the power argument in section 6.
4. **Forgetting the MOSFET's fourth terminal.** The body affects the threshold voltage. It is usually tied to a supply rail and then ignored, but it is there.
5. **Treating source and drain as fixed.** In a MOSFET they are structurally identical; the labels follow from the applied voltages.
6. **Thinking "no gate current" means "no power".** It means no *static* power. Charging and discharging the gate capacitance every cycle is exactly the $\alpha C V^2 f$ dynamic power of module 2.

---

## 10. Check your understanding

1. **Why can a MOSFET gate be driven by an arbitrarily weak signal, while a BJT base cannot?**
   <details><summary>Answer</summary>
   The MOSFET gate is a capacitor: it needs charge delivered once to change state, and no current to maintain it. A weak driver simply takes longer to charge it — slower, but functional.<br>
   A BJT base needs <em>continuous</em> current proportional to the collector current. A driver too weak to supply it cannot keep the transistor on at all. This is why MOSFET fan-out is limited by <strong>speed</strong> (more gates to charge means longer delay) while BJT fan-out is limited by <strong>current budget</strong> — a much harder wall.
   </details>

2. **A MOSFET's source and drain are structurally identical. What decides which is which?**
   <details><summary>Answer</summary>
   The applied voltages. For an N-channel device, the <strong>source</strong> is whichever terminal is at the lower potential — it is the terminal that <em>sources</em> electrons into the channel. Swap the voltages and the roles swap.<br>
   This is why MOSFETs make excellent bidirectional <strong>transmission gates</strong>, passing signals either way. A BJT is structurally asymmetric (the emitter is far more heavily doped than the collector) and works poorly in reverse.
   </details>

3. **Section 6 compares static power. Why isn't that the whole comparison?**
   <details><summary>Answer</summary>
   It ignores <strong>dynamic</strong> power and speed. BJTs switch faster and drive more current per unit area, which is why ECL was used in supercomputers well into the 1990s.<br>
   The static argument wins because it <em>scales</em>: static power grows linearly with device count and cannot be reduced by slowing down or idling. Dynamic power at least falls when you stop switching. A technology whose idle power is proportional to transistor count has a hard ceiling on integration, whatever its per-gate speed.
   </details>

4. **Why does the gate oxide need to be extremely thin, given that thinness causes tunnelling?**
   <details><summary>Answer</summary>
   The gate controls the channel through <strong>capacitive coupling</strong>, and capacitance is inversely proportional to separation: $C = \varepsilon A / t$. A thinner oxide gives stronger control — more channel charge per volt of gate drive, so more current and a sharper switching transition.<br>
   This is a direct conflict: thinner means better control <em>and</em> more leakage. The resolution was to change $\varepsilon$ instead of $t$ — <strong>high-k dielectrics</strong> raise the permittivity so the same capacitance is achieved at greater physical thickness. Changing the material sidestepped a geometric dead end.
   </details>

---

## 11. Practice — independent task

**Task:** You are comparing two logic families for a design.

Family A (bipolar): 2 mW static power per gate, 0.3 ns propagation delay.
Family B (CMOS): 5 nW static power per gate, 1.2 ns propagation delay, 0.4 pJ switched per transition.

- **(a)** For 10,000 gates, compute the total static power of each family.
- **(b)** Repeat for 1 million and 100 million gates. At what gate count does family A exceed a 150 W package budget?
- **(c)** Family B's dynamic power is (energy per transition) × (transitions per second). At 1 GHz with 10% of gates switching each cycle, compute family B's dynamic power for 100 million gates.
- **(d)** Add family B's static and dynamic power at that scale. Which dominates?
- **(e)** Family A is 4× faster per gate. Construct the argument for why that did not save it, referring to your answer in (b).
- **(f)** Add a `max_gates_within_budget(static_per_gate, budget_w)` function and use it to reproduce (b).

**Done when:** you can state the gate count at which each family hits 150 W, and explain in one sentence why static power — not speed — determined which technology scaled.

<details><summary>Hint for (c), only if stuck</summary>
Transitions per second = (gate count) × (activity factor) × (clock frequency). With 10⁸ gates, α = 0.1 and f = 10⁹ Hz, that is 10¹⁶ transitions per second. Multiply by 0.4 pJ. If the answer looks alarmingly large, that is correct and is exactly why real chips have activity factors well below 0.1 and use clock gating to push them lower still.
</details>

---

## 12. Tradeoffs and limits

- **This module is qualitative about the MOSFET.** *How* the field forms a channel, what threshold voltage means, and how much current flows are all module 12.
- **BJTs are not covered in depth.** Their internals are a course in themselves. What matters here is the contrast: current-controlled versus voltage-controlled, and its consequence for scaling.
- **Modern transistors are no longer flat.** FinFETs (~2011) and gate-all-around nanosheets wrap the gate around the channel on multiple sides for better control. The physics of module 12 still applies; the geometry does not.
- **Static power is not zero in practice.** Subthreshold leakage, gate tunnelling and junction leakage all contribute, and below ~65 nm they became a serious fraction of total chip power — which is why regions are powered *off* rather than merely idled.

---

## Before moving on

- [ ] State what a third terminal provides that two cannot, including why regeneration requires it.
- [ ] Distinguish amplifier operation from switch operation, and say why digital treats the middle as a hazard.
- [ ] Describe the BJT and MOSFET structures and name their control variables.
- [ ] Reproduce the static-power scaling argument and explain why it decided digital logic.
- [ ] Explain why a 1.2 nm oxide is ~3 molecules thick and what that caused historically.

**Recap:** A transistor's third terminal separates control from conduction, letting one signal steer a current it is not part of — which makes gates composable and makes signal regeneration possible. BJTs are current-controlled and need continuous base current to hold a state; MOSFETs are voltage-controlled through an insulated gate and need none. At a billion devices that difference is 10 kW versus 1 mW, which is why all digital logic is MOSFET-based and why the power equation has no static term.

**Next:** [[how-computers-work/03-transistors/02-mosfet-physics|Module 12 — MOSFET Physics]] opens up the device: how gate voltage inverts the surface to form a channel, what threshold voltage is, and the three operating regions.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/01-electricity/03-circuit-laws|Module 3]] — the switchable-resistance requirement
- [[how-computers-work/03-transistors/03-cmos|Module 13 — CMOS]] — where two complementary MOSFETs become a gate
- [[foundations/hardware/03-embedded-systems|hardware/embedded systems]] — transistors as practical components
