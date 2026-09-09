# Module 12: MOSFET Physics (How Voltage Becomes a Channel)

**[Intermediate]** — The device opened up. How a gate voltage conjures a conducting layer out of silicon that was doped the wrong way, what threshold voltage means, and the three regions that define every use of a transistor.

## Before you start

- You know the MOSFET's structure — insulated gate over a channel between two doped regions — [[how-computers-work/03-transistors/01-what-a-transistor-is|module 11]].
- You can explain depletion regions and how applied voltage changes their width — [[how-computers-work/02-semiconductors/05-pn-junctions|module 10]].
- You know majority and minority carriers, and that doping suppresses minorities — [[how-computers-work/02-semiconductors/04-doping|module 9]].
- You remember the 60 mV/decade rule — [[how-computers-work/02-semiconductors/05-pn-junctions|module 10]].

**After this lesson you will be able to:**

1. Explain accumulation, depletion and inversion, and why inversion is the surprising one.
2. Define threshold voltage and explain what physically happens at it.
3. Identify the three operating regions from $V_{gs}$ and $V_{ds}$, and explain pinch-off.
4. Explain why the triode region gives exactly the switchable resistance [[how-computers-work/01-electricity/03-circuit-laws|module 3]] demanded, and why $W/L$ is the designer's main knob.

**Study route:** section 3 is the conceptual leap. Section 5 (pinch-off) is the part most people find genuinely confusing — the diagram is there to help.

---

## 1. Why this exists (real-world motivation)

Module 11 said the gate creates a field that "forms a channel". That sentence was doing a great deal of unexamined work.

**Look at what it is claiming.** The body is P-type — its mobile carriers are holes, and module 9 established that doping *suppresses* the minority electrons to around $10^4$/cm³. To conduct between two N-type regions you need a path made of electrons. There are essentially none available.

**So where does the channel come from?** Not from the gate — it is insulated and cannot inject anything. Not from the source and drain alone. The answer is genuinely surprising: **the gate voltage converts a thin surface layer of P-type silicon into N-type**, without changing a single dopant atom.

That process is called **inversion**, and it is the mechanism at the centre of this course.

---

## 2. Terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **MOS capacitor** | Gate, oxide and semiconductor — a capacitor with silicon as one plate | — |
| **Accumulation** | Gate voltage attracting *majority* carriers to the surface | Crowding the usual residents in |
| **Depletion** | Gate voltage pushing majority carriers away, exposing fixed ions | Clearing the room |
| **Inversion** | Enough gate voltage to attract minority carriers, flipping the surface type | New residents move in |
| **Threshold voltage** ($V_{th}$) | Gate voltage at which strong inversion forms a usable channel | The tipping point |
| **Overdrive** ($V_{ov} = V_{gs} - V_{th}$) | How far past threshold you are | — |
| **Cutoff** | $V_{gs} < V_{th}$ — no channel | Switch off |
| **Triode / linear** | Channel present, small $V_{ds}$ — behaves as a resistor | Switch on |
| **Saturation** | Channel pinched off at the drain — current stops rising with $V_{ds}$ | — |
| **Pinch-off** | The channel vanishing at the drain end | — |
| **$W/L$** | Channel width divided by length — the geometric design knob | — |
| **Subthreshold swing** | Millivolts of gate change per decade of current, below threshold | — |

---

## 3. Inversion — the conceptual leap

Consider just the gate, the oxide and the P-type body. Ignore source and drain for a moment. This stack is a **MOS capacitor**, and its behaviour as gate voltage rises comes in three stages.

### Stage 1 — accumulation ($V_g$ negative)

A negative gate attracts positive charges. The body's majority carriers are holes, so **holes pile up at the surface.**

```
   GATE  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓  (negative)
   OXIDE ░░░░░░░░░░░░░░
   BODY  ○ ○ ○ ○ ○ ○ ○ ○  ← holes accumulate at the surface
     P   ○   ○   ○   ○     surface is MORE p-type than before
```

The surface is more strongly P-type than the bulk. No use for conduction between N-type regions.

### Stage 2 — depletion ($V_g$ slightly positive)

A positive gate **repels** holes, driving them down into the bulk. What is left behind is the fixed negative acceptor ions — immobile, exactly as in [[how-computers-work/02-semiconductors/05-pn-junctions|module 10]].

```
   GATE  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓  (slightly positive)
   OXIDE ░░░░░░░░░░░░░░
   BODY  ⊖ ⊖ ⊖ ⊖ ⊖ ⊖ ⊖ ⊖  ← holes pushed away, fixed ions exposed
     P   ○   ○   ○   ○     a DEPLETION region, no mobile carriers
```

The surface now has no mobile carriers of either type. Still no channel — but notice the gate is building a depletion region purely by field, with no junction involved.

### Stage 3 — inversion ($V_g$ strongly positive) — the surprising part

Push the gate more positive and the field grows strong enough to attract **electrons** to the surface.

Where do they come from? Two sources: thermal generation in the depletion region, and — far more importantly in a real MOSFET — **the N-type source and drain, which are packed with them.**

```
   GATE  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓  (strongly positive)
   OXIDE ░░░░░░░░░░░░░░
   BODY  ● ● ● ● ● ● ● ●  ← ELECTRONS at the surface: an N-type layer
     P   ⊖ ⊖ ⊖ ⊖ ⊖ ⊖ ⊖    inside P-type silicon
         ○   ○   ○
```

**The surface has been inverted.** A layer of P-type silicon a few nanometres thick is now behaving as N-type, and it connects the N-type source to the N-type drain.

> [!NOTE]
> **No dopant atom moved.** The acceptor ions are still there, still negative, still fixed. What changed is which *mobile* carriers occupy the surface — the field pulled in enough electrons to outnumber the holes locally.
>
> **This is the whole transistor.** A voltage on an insulated plate reaches through an insulator and reversibly changes what kind of semiconductor the surface is. Remove the voltage and the electrons disperse; the channel vanishes instantly and completely.
>
> Note also that it is *reversible and fast* — no chemistry, no diffusion, just carriers redistributing under a field. That is why it can happen billions of times per second.

**Threshold voltage $V_{th}$ is the gate voltage at which inversion becomes strong enough to form a usable channel.** It is set at manufacturing time by body doping, oxide thickness, and the gate material's work function — which is why a process is characterised by its $V_{th}$, and why designers treat it as fixed.

---

## 4. Predict before reading on

The channel is formed by electrons attracted from the source and drain into a P-type body.

**What happens to the channel if you raise the source voltage while keeping the gate fixed?**

<details><summary>Check your answer</summary>

**The channel weakens and may vanish.** What matters is $V_{gs}$ — the gate voltage *relative to the source* — not the gate's absolute voltage. Raising the source reduces $V_{gs}$, reducing the overdrive, shrinking the channel.

This has a very practical consequence you will meet in [[how-computers-work/03-transistors/03-cmos|module 13]]: an NMOS transistor is **bad at passing a logic high**. As its source terminal rises toward $V_{DD}$, $V_{gs}$ falls toward $V_{th}$ and the device chokes itself off — it can only pull the output up to $V_{DD} - V_{th}$, not to the rail.

That single fact is why CMOS needs *both* transistor types, and why NMOS-only logic could never deliver module 5's rail-to-rail outputs.
</details>

---

## 5. The three regions

With a channel present, applying $V_{ds}$ drives current through it. How it behaves depends on how $V_{ds}$ compares with the overdrive $V_{ov} = V_{gs} - V_{th}$.

### Cutoff — $V_{gs} < V_{th}$

No inversion layer, no channel. Current is *nearly* zero — see section 7 on why "nearly" matters enormously.

### Triode (linear) — $V_{gs} > V_{th}$ and $V_{ds} < V_{ov}$

The channel exists along its whole length. For small $V_{ds}$ the device behaves as a **resistor whose value is set by $V_{gs}$**:

$$I_d = k'\frac{W}{L}\left[V_{ov}V_{ds} - \frac{V_{ds}^2}{2}\right]$$

**This is precisely what [[how-computers-work/01-electricity/03-circuit-laws|module 3]] asked for**, ten modules ago: a resistance controlled by a third terminal. The shopping list is now filled.

### Saturation — $V_{ds} \geq V_{ov}$

Here is where intuition usually fails, so take it slowly.

The channel's local strength at any point depends on the gate voltage *relative to the channel at that point*. Near the source the channel sits at ~0 V, so the full $V_{gs}$ acts on it. Near the drain the channel has been pulled up toward $V_{ds}$, so the effective gate-to-channel voltage there is only $V_{gs} - V_{ds}$.

**Raise $V_{ds}$ until $V_{gs} - V_{ds} = V_{th}$ and the channel at the drain end is exactly at threshold. Beyond that it vanishes locally — the channel pinches off.**

```
   Triode: channel full length          Saturation: pinched off at drain

   S ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ D              S ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓╲___ D
     ════════════════════                ═══════════════════
     uniform-ish channel                 channel tapers, then ends
                                         short depletion gap here
```

Current does **not** stop. Carriers reaching the pinch-off point are swept across the small depletion gap by the strong field there — exactly the mechanism sweeping minority carriers across a reverse-biased junction in module 10.

**But the current stops increasing.** Raising $V_{ds}$ further just moves the pinch-off point slightly and drops the extra voltage across the gap. The current becomes almost independent of $V_{ds}$:

$$I_d = \frac{1}{2}k'\frac{W}{L}V_{ov}^2$$

**A saturated MOSFET is a voltage-controlled current source** — set by $V_{gs}$, indifferent to $V_{ds}$. That is what makes it a good amplifier, and it is the region analogue designers live in.

---

## 6. $W/L$ — the designer's knob

Both current equations contain $W/L$: channel width over channel length.

- **$L$ is fixed by the process.** "A 7 nm process" refers to a minimum feature size. Designers almost always use minimum $L$, because shorter is faster.
- **$W$ is chosen per transistor.** It is the one geometric parameter a logic designer routinely varies.

**Current scales linearly with $W/L$:**

| $W/L$ | $I_d$ at $V_{gs} = V_{ds} = 1.0$ V |
| ---: | ---: |
| 1.0 | 36.00 μA |
| 2.0 | 72.00 μA |
| 2.8 | 100.80 μA |
| 4.0 | 144.00 μA |

**Now the loose end from [[how-computers-work/02-semiconductors/03-energy-bands|module 8]] ties off.** Hole mobility is 2.8× lower than electron mobility, so a PMOS transistor has 2.8× less $k'$. To make a PMOS drive as hard as an NMOS, you give it 2.8× the width — which is exactly the 2.8 in the table.

**A fact about valence-band structure, established in module 8, has become a number in a layout tool.** That is the course's method working end to end.

The cost is not free: a wider transistor presents proportionally more gate capacitance to whatever drives it. Sizing is therefore a genuine optimisation, not a free win — a theme that recurs throughout digital design.

---

## 7. Cutoff is not actually off

The square-law model says current is zero below threshold. **It is not**, and the discrepancy governs modern chip design.

Below threshold the channel is weakly inverted, and current falls **exponentially** rather than to zero:

$$I_d \propto 10^{(V_{gs} - V_{th})/S}$$

where $S$ is the **subthreshold swing** in volts per decade — typically 70–100 mV/decade.

**$S$ has a hard floor:**

$$S_{min} = \ln(10)\frac{kT}{q} = 59.5 \text{ mV/decade at 300 K}$$

**That is [[how-computers-work/02-semiconductors/05-pn-junctions|module 10]]'s 60 mV rule, returning as promised.** It is the same Boltzmann statistics — the fraction of carriers with enough energy to cross a barrier — and it is not an engineering limitation that better fabrication could remove. It is thermodynamics.

### Why this ended voltage scaling

Follow the chain:

1. To turn a transistor properly off, $V_{th}$ must be comfortably above 0, or leakage is unacceptable.
2. To turn it properly *on*, $V_{DD}$ must be comfortably above $V_{th}$, or drive current collapses.
3. So $V_{DD}$ has a floor set by $V_{th}$, which has a floor set by the 60 mV/decade swing.

**Below about 1 V the arithmetic stops working.** You cannot lower $V_{th}$ without exponentially worse leakage, and you cannot lower $V_{DD}$ without losing the drive to switch.

And from [[how-computers-work/01-electricity/02-resistance-and-ohms-law|module 2]], $P = \alpha C V^2 f$ — with $V$ pinned, the quadratic discount that had paid for every frequency increase since the 1970s was gone.

**Trace the whole chain:** Boltzmann statistics → 60 mV/decade → $V_{th}$ floor → $V_{DD}$ floor → no more $V^2$ savings → clock frequencies plateau → multicore processors.

**The number of cores in your laptop is set by the distribution of thermal energy among electrons.** Modules 2, 10 and 12 have been building to that sentence.

---

## 8. Worked example — runnable

Save as `mosfet_lab.py` and run `python3 mosfet_lab.py`.

```python
import math

# A simplified but self-consistent process
K_PRIME = 200e-6      # mu*Cox, amperes per volt^2 (process transconductance)
V_TH    = 0.4         # threshold voltage, volts
V_DD    = 1.0         # supply, volts
SUBTHRESHOLD_SWING = 0.070   # volts per decade of current

def region(v_gs, v_ds, v_th=V_TH):
    """Which of the three operating regions is the device in?"""
    if v_gs <= v_th:
        return "cutoff"
    return "triode" if v_ds < (v_gs - v_th) else "saturation"

def drain_current(v_gs, v_ds, w_over_l=1.0, v_th=V_TH, k=K_PRIME):
    """Long-channel MOSFET current, all three regions."""
    v_ov = v_gs - v_th                     # overdrive voltage
    if v_ov <= 0:                          # cutoff: exponential subthreshold leak
        return leakage_current(v_gs, w_over_l, v_th, k)
    if v_ds < v_ov:                        # triode / linear
        return k * w_over_l * (v_ov * v_ds - v_ds**2 / 2)
    return 0.5 * k * w_over_l * v_ov**2    # saturation

def leakage_current(v_gs, w_over_l=1.0, v_th=V_TH, k=K_PRIME, swing=SUBTHRESHOLD_SWING):
    """Below threshold, current falls exponentially -- not to zero."""
    i_ref = 0.5 * k * w_over_l * (0.1 ** 2)     # small reference current at v_ov = 0.1
    decades_below = (v_th + 0.1 - v_gs) / swing
    return i_ref * 10 ** (-decades_below)

def on_resistance(v_gs, w_over_l=1.0, v_th=V_TH, k=K_PRIME):
    """Small-signal resistance in the triode region -- the 'switched resistance'."""
    v_ov = v_gs - v_th
    if v_ov <= 0:
        return float("inf")
    return 1.0 / (k * w_over_l * v_ov)

if __name__ == "__main__":
    print(f"process: k' = {K_PRIME*1e6:.0f} uA/V^2, V_th = {V_TH} V, V_DD = {V_DD} V")
    print()

    print("operating region as a function of the two applied voltages:")
    print(f"  {'V_gs':>6s} {'V_ds':>6s}   region")
    for v_gs, v_ds in [(0.2, 0.5), (1.0, 0.1), (1.0, 0.3), (1.0, 0.9), (0.6, 0.5)]:
        print(f"  {v_gs:6.2f} {v_ds:6.2f}   {region(v_gs, v_ds)}")
    print()

    print("drain current vs gate voltage (V_ds = V_DD, W/L = 2):")
    for v_gs in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        i = drain_current(v_gs, V_DD, w_over_l=2.0)
        print(f"  V_gs = {v_gs:.1f} V -> I_d = {i*1e6:10.4f} uA   ({region(v_gs, V_DD)})")
    print()

    # The switchable resistance module 3 asked for
    print("on-resistance in triode (W/L = 2) -- module 3's switched resistor:")
    for v_gs in (0.5, 0.7, 1.0):
        print(f"  V_gs = {v_gs:.1f} V -> R_on = {on_resistance(v_gs, 2.0):9.0f} ohm")
    print(f"  V_gs = 0.0 V -> R_on = infinite (cutoff)")
    print()

    i_on  = drain_current(V_DD, V_DD, w_over_l=2.0)
    i_off = drain_current(0.0,  V_DD, w_over_l=2.0)
    print(f"on current  = {i_on*1e6:.3f} uA")
    print(f"off current = {i_off*1e12:.3f} pA")
    print(f"  on/off ratio = {i_on/i_off:.2e}")
    print()

    # W/L: the designer's only geometric knob
    print("current scales linearly with W/L (V_gs = V_ds = V_DD):")
    for wl in (1.0, 2.0, 2.8, 4.0):
        print(f"  W/L = {wl:4.1f} -> I_d = {drain_current(V_DD, V_DD, wl)*1e6:8.2f} uA")

    print()
    print(f"subthreshold swing = {SUBTHRESHOLD_SWING*1000:.0f} mV/decade")
    print(f"  the room-temperature floor is ln(10)*kT/q = 59.5 mV/decade")
    print(f"  turning off {V_TH} V below threshold buys"
          f" {V_TH/SUBTHRESHOLD_SWING:.1f} decades of current reduction")

    assert region(0.2, 0.5) == "cutoff"
    assert region(1.0, 0.1) == "triode"
    assert region(1.0, 0.9) == "saturation"
    assert i_on / i_off > 1e5
    assert abs(drain_current(V_DD, V_DD, 4.0) / drain_current(V_DD, V_DD, 2.0) - 2.0) < 1e-9
    print()
    print("mosfet_lab: passed")
```

Expected output:

```
process: k' = 200 uA/V^2, V_th = 0.4 V, V_DD = 1.0 V

operating region as a function of the two applied voltages:
    V_gs   V_ds   region
    0.20   0.50   cutoff
    1.00   0.10   triode
    1.00   0.30   triode
    1.00   0.90   saturation
    0.60   0.50   saturation

drain current vs gate voltage (V_ds = V_DD, W/L = 2):
  V_gs = 0.0 V -> I_d =     0.0000 uA   (cutoff)
  V_gs = 0.2 V -> I_d =     0.0001 uA   (cutoff)
  V_gs = 0.4 V -> I_d =     0.0746 uA   (cutoff)
  V_gs = 0.6 V -> I_d =     8.0000 uA   (saturation)
  V_gs = 0.8 V -> I_d =    32.0000 uA   (saturation)
  V_gs = 1.0 V -> I_d =    72.0000 uA   (saturation)

on-resistance in triode (W/L = 2) -- module 3's switched resistor:
  V_gs = 0.5 V -> R_on =     25000 ohm
  V_gs = 0.7 V -> R_on =      8333 ohm
  V_gs = 1.0 V -> R_on =      4167 ohm
  V_gs = 0.0 V -> R_on = infinite (cutoff)

on current  = 72.000 uA
off current = 0.144 pA
  on/off ratio = 5.00e+08

current scales linearly with W/L (V_gs = V_ds = V_DD):
  W/L =  1.0 -> I_d =    36.00 uA
  W/L =  2.0 -> I_d =    72.00 uA
  W/L =  2.8 -> I_d =   100.80 uA
  W/L =  4.0 -> I_d =   144.00 uA

subthreshold swing = 70 mV/decade
  the room-temperature floor is ln(10)*kT/q = 59.5 mV/decade
  turning off 0.4 V below threshold buys 5.7 decades of current reduction

mosfet_lab: passed
```

Note the on-resistance at full drive: **4167 Ω for a $W/L$ of 2**. That is the same order as the 5 kΩ used in [[how-computers-work/01-electricity/04-signals-and-time|module 4]]'s RC timing example — the two modules were describing the same transistor from different ends.

---

## 9. Common pitfalls and traps

1. **Thinking the gate injects carriers.** It is insulated. It attracts carriers that come from the source and drain.
2. **Believing inversion changes the doping.** Dopant ions never move. Only the mobile carrier population at the surface changes.
3. **Using absolute gate voltage instead of $V_{gs}$.** Everything depends on gate voltage *relative to the source*. This is the root of the NMOS-can't-pull-up problem.
4. **Thinking pinch-off stops the current.** Current continues; it merely stops *increasing* with $V_{ds}$.
5. **Treating cutoff as zero current.** Subthreshold leakage is exponential, not zero, and at a billion transistors it dominates idle power.
6. **Forgetting $W/L$ costs capacitance.** Widening a transistor strengthens it and loads its driver. There is an optimum.
7. **Trusting the square-law model at small geometries.** It is a long-channel approximation. Below ~100 nm, velocity saturation makes current closer to linear in $V_{ov}$ than quadratic.

---

## 10. Check your understanding

1. **Why can an NMOS transistor pull an output down to 0 V cleanly, but not up to $V_{DD}$?**
   <details><summary>Answer</summary>
   Pulling <em>down</em>, the source is at ground, so $V_{gs} = V_{DD}$ stays at full overdrive all the way — the device conducts hard right down to 0 V.<br>
   Pulling <em>up</em>, the source terminal is the rising output. As it rises, $V_{gs} = V_{DD} - V_{out}$ shrinks. When $V_{out}$ reaches $V_{DD} - V_{th}$, the overdrive hits zero and the transistor cuts off. It cannot deliver the last $V_{th}$ volts.<br>
   PMOS has the mirror-image problem. This complementary weakness is exactly why CMOS pairs them: NMOS pulls down, PMOS pulls up, each doing the job it is good at.
   </details>

2. **Why does saturation current depend on $V_{gs}$ but barely on $V_{ds}$?**
   <details><summary>Answer</summary>
   $V_{gs}$ sets how strongly the channel is inverted — how much charge is available to carry current. $V_{ds}$ beyond pinch-off does not add charge; it only lengthens the depletion gap at the drain slightly, and the extra voltage is dropped across that gap.<br>
   The current is limited by charge supply, not by the accelerating voltage. That makes a saturated MOSFET a voltage-controlled <em>current source</em>. (In real short-channel devices, channel-length modulation gives a small residual $V_{ds}$ dependence.)
   </details>

3. **A process reduces $V_{th}$ from 0.4 V to 0.2 V, with a 70 mV/decade swing. What happens to leakage, and why might a manufacturer do it anyway?**
   <details><summary>Answer</summary>
   Leakage rises by $10^{0.2/0.07} = 10^{2.86} \approx$ <strong>720×</strong>.<br>
   They do it because drive current depends on $V_{ov} = V_{DD} - V_{th}$. At $V_{DD}$ = 1.0 V, lowering $V_{th}$ from 0.4 to 0.2 raises the overdrive from 0.6 to 0.8 V — and since saturation current goes as $V_{ov}^2$, that is $(0.8/0.6)^2 = 1.78×$ the current, hence a faster circuit.<br>
   This is the fundamental speed-versus-leakage tradeoff. Real chips resolve it by using <strong>multiple threshold voltages</strong> on the same die: low-$V_{th}$ devices on critical paths, high-$V_{th}$ everywhere else.
   </details>

4. **Why is the 59.5 mV/decade subthreshold floor a thermodynamic limit rather than an engineering one?**
   <details><summary>Answer</summary>
   It comes from the Boltzmann distribution of carrier energies. The fraction of carriers with enough energy to surmount a barrier falls as $e^{-E/kT}$, so changing the barrier by $\ln(10)\,kT/q$ changes the current tenfold. That is a property of thermal equilibrium, not of materials or lithography.<br>
   The only escapes are to lower $T$ (impractical for consumer devices) or to use a device that does not rely on thermal injection at all — which is exactly what <strong>tunnel FETs</strong> and negative-capacitance FETs attempt, both still research topics. It is the same physics that fixes the diode's 60 mV/decade in module 10.
   </details>

---

## 11. Practice — independent task

**Task:** You are sizing transistors for a standard cell using the module's process ($k' = 200$ μA/V², $V_{th} = 0.4$ V, $V_{DD} = 1.0$ V, swing 70 mV/decade). PMOS $k'$ is 2.8× lower than NMOS.

- **(a)** Compute the saturation current of an NMOS with $W/L = 2$ at $V_{gs} = V_{DD}$.
- **(b)** What $W/L$ must a PMOS have to deliver the same current? Verify with `drain_current()` using the reduced $k'$.
- **(c)** Compute the triode on-resistance of both at $V_{gs} = V_{DD}$. Are they equal? Should they be?
- **(d)** A designer proposes halving both widths to save area. Compute the new currents and on-resistances. Using $\tau = RC$ from [[how-computers-work/01-electricity/04-signals-and-time|module 4]], and assuming the load capacitance is dominated by *wiring* rather than by the gates, what happens to the delay?
- **(e)** Now assume the load is dominated by the *next stage's gate capacitance*, which also halves. What happens to the delay now? Explain why the two answers differ.
- **(f)** Compute total leakage for 10⁹ transistors at $V_{gs} = 0$, at $V_{th}$ = 0.4 V and again at $V_{th}$ = 0.25 V. Convert both to watts at 1.0 V.
- **(g)** Write `leakage_power(n_transistors, v_th, supply)` and use it to find the $V_{th}$ at which a billion-transistor chip leaks 1 W.

**Done when:** you can state the PMOS width ratio and justify it from mobility, and explain why halving transistor widths helps or hurts depending on what dominates the load capacitance.

<details><summary>Hint for (d) and (e), only if stuck</summary>
Delay goes as $\tau = R_{on}C_{load}$. Halving $W$ doubles $R_{on}$.<br>
If $C_{load}$ is fixed wiring capacitance, delay <strong>doubles</strong> — a clear loss.<br>
If $C_{load}$ is the next gate's input capacitance, it halves too, so $\tau = 2R \times C/2 = RC$ — delay is <strong>unchanged</strong>, and you saved area and switching energy for free.<br>
This is why "make everything minimum size" is often correct in dense logic and badly wrong when driving long wires — and why buffer sizing is a real optimisation problem.
</details>

---

## 12. Tradeoffs and limits of this model

- **The square-law equations are long-channel approximations.** In modern short-channel devices, carriers reach **velocity saturation** and current becomes closer to linear in $V_{ov}$. The qualitative picture — three regions, threshold, pinch-off — survives; the exponents do not.
- **Short-channel effects are omitted.** Drain-induced barrier lowering (DIBL) makes $V_{th}$ depend on $V_{ds}$; the gate loses electrostatic control as $L$ shrinks. Combating this drove the move to **FinFETs** and gate-all-around structures, which wrap the gate around the channel on several sides.
- **The body is assumed grounded.** A non-zero body-source voltage shifts $V_{th}$ — the **body effect** — which matters in stacked transistors like the series NMOS chains you will meet in [[how-computers-work/04-logic/01-gates-from-transistors|module 14]].
- **Temperature dependence is ignored here.** Mobility falls and leakage rises with temperature, so a hot chip is both slower and leakier.

---

## Before moving on

- [ ] Explain accumulation, depletion and inversion, and why inversion is surprising.
- [ ] Explain what threshold voltage is and what physically happens at it.
- [ ] Identify the operating region from $V_{gs}$ and $V_{ds}$, and explain pinch-off without saying current stops.
- [ ] Explain why the triode region is module 3's switchable resistance.
- [ ] Explain the $W/L$ knob and derive the 2.8× PMOS widening from module 8.
- [ ] Trace the chain from Boltzmann statistics to multicore processors.

**Recap:** A gate voltage across an insulator drives the silicon surface through accumulation, depletion and finally inversion, where attracted minority carriers make a P-type surface behave as N-type and connect source to drain. Threshold voltage is where that channel becomes usable. Below it, current falls exponentially at best 59.5 mV/decade; above it, the device is a voltage-controlled resistor at low $V_{ds}$ and a voltage-controlled current source once pinched off. Current scales with $W/L$, which is why PMOS devices are drawn 2.8× wider.

**Next:** [[how-computers-work/03-transistors/03-cmos|Module 13 — CMOS]] puts an NMOS and a PMOS together. Module 3's voltage-divider table becomes a real circuit, the complementary weaknesses cancel, and you get a gate that delivers module 5's rail-to-rail output while burning almost nothing.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/01-electricity/03-circuit-laws|Module 3]] — the switchable resistance, now delivered
- [[how-computers-work/02-semiconductors/03-energy-bands|Module 8]] — the mobility asymmetry behind PMOS sizing
- [[how-computers-work/02-semiconductors/05-pn-junctions|Module 10]] — where 60 mV/decade first appeared
