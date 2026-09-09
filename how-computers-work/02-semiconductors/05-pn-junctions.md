# Module 10: PN Junctions and Diodes (The First Asymmetric Device)

**[Intermediate]** — Put N-type against P-type and something new appears: a device that conducts one way and blocks the other. Part III ends here, one step short of a transistor.

## Before you start

- You can explain N-type and P-type silicon, majority and minority carriers, and why ionised dopants are immobile — [[how-computers-work/02-semiconductors/04-doping|module 9]].
- You know $np = n_i^2$ and that doping suppresses minority carriers — module 9.
- You know $kT$ = 25.85 meV at 300 K and what an exponential does to a modest energy difference — [[how-computers-work/02-semiconductors/03-energy-bands|module 8]].

**After this lesson you will be able to:**

1. Explain how a depletion region and built-in potential form, and why the process stops rather than running away.
2. Explain forward and reverse bias in terms of the barrier widening or narrowing.
3. Apply the diode equation and explain the 60 mV-per-decade rule.
4. Explain why a junction rectifies, and identify what a junction still cannot do that a transistor must.

**Study route:** sections 3–4 are the mechanism and the heart of Part III. Section 8 explains why this device, despite being remarkable, is not yet enough.

---

## 1. Why this exists (real-world motivation)

Every component so far has been **symmetric**. A resistor does not care which way current flows. Doped silicon conducts equally in both directions. You can reverse the leads on anything in Part II and nothing changes.

**Symmetric components cannot compute.** Logic requires asymmetry — a device that treats one situation differently from another. Until something breaks the symmetry, you have circuits but no decisions.

The PN junction is the first asymmetric device, and it emerges from doing nothing more than putting the two doped materials from module 9 next to each other. **You do not add a mechanism. The asymmetry assembles itself** out of diffusion, the mass action law, and the fact that ionised dopants cannot move.

---

## 2. Terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **PN junction** | The boundary where P-type meets N-type in one crystal | — |
| **Diffusion** | Carriers spreading from high to low concentration | Perfume filling a room |
| **Drift** | Carriers pushed by an electric field | Wind blowing the perfume back |
| **Depletion region** | The zone near the junction emptied of mobile carriers | A no-man's-land |
| **Space charge** | The exposed fixed dopant ions in that zone | Left-behind litter |
| **Built-in potential** ($V_{bi}$) | The voltage barrier that forms at equilibrium | A hill carriers must climb |
| **Forward bias** | External voltage opposing the barrier (P positive) | Lowering the hill |
| **Reverse bias** | External voltage reinforcing the barrier (N positive) | Raising the hill |
| **Saturation current** ($I_S$) | The tiny reverse leakage, from minority carriers | — |
| **Thermal voltage** ($V_T = kT/q$) | 25.85 mV at 300 K | The natural voltage scale |
| **Breakdown** | Reverse voltage high enough to force conduction | The dam bursting |

---

## 3. How the junction forms

Imagine joining a P-type block to an N-type block. (In reality they are one crystal with different doping, but the reasoning is identical.)

### Step 1 — diffusion

The N side is crowded with electrons; the P side has almost none. That is an enormous concentration gradient, so **electrons diffuse from N to P**. Symmetrically, **holes diffuse from P to N**.

This is not electrical attraction — both materials are neutral. It is pure statistics, the same reason gas spreads out.

### Step 2 — recombination empties the boundary

An electron arriving on the P side finds itself surrounded by holes, and recombines almost immediately. Likewise a hole arriving on the N side.

**The region either side of the boundary is stripped of mobile carriers.** That is the **depletion region**.

### Step 3 — the fixed ions are exposed

Here is where module 9's insistence on immobile dopants pays off.

The carriers that left were balancing the charge of their ionised dopant atoms. **Those dopant ions are locked in the lattice and cannot follow.** With the mobile carriers gone, their charge is uncovered:

- On the **N side**: positive donor ions, no longer balanced by electrons.
- On the **P side**: negative acceptor ions, no longer balanced by holes.

```
        P-TYPE                depletion region              N-TYPE
   (holes, mobile)         (no mobile carriers)       (electrons, mobile)

   ○ ○ ○ ○ ○ ○ │ ⊖ ⊖ ⊖ ⊖ ⊖ │ ⊕ ⊕ ⊕ ⊕ ⊕ │ ● ● ● ● ● ●
   ○ ○ ○ ○ ○ ○ │ ⊖ ⊖ ⊖ ⊖ ⊖ │ ⊕ ⊕ ⊕ ⊕ ⊕ │ ● ● ● ● ● ●
               │           │           │
               │  ←────────E────────   │   E field points N → P
               │                       │
               │<──── W ≈ 0.43 um ────>│

   ○ mobile hole   ● mobile electron
   ⊖ fixed acceptor ion   ⊕ fixed donor ion
```

### Step 4 — the field stops the diffusion

Separated charge means an **electric field**, pointing from the positive N-side ions toward the negative P-side ions.

**That field opposes exactly the motion that created it.** It pushes electrons back toward N and holes back toward P — the reverse of the diffusion that started everything.

**So the process is self-limiting.** Diffusion widens the depletion region, which strengthens the field, which resists further diffusion. Equilibrium arrives when drift exactly cancels diffusion. No external influence is needed; the junction builds its own barrier and then stops.

> [!NOTE]
> **This is a negative feedback loop appearing spontaneously in physics.** Nothing designed it. The junction settles at precisely the width where the two opposing transport mechanisms balance, and it returns to that state if disturbed.
>
> Recognising self-limiting equilibria is worth carrying forward — the same pattern governs the MOSFET channel in [[how-computers-work/03-transistors/02-mosfet-physics|module 12]].

### The built-in potential

The barrier height at equilibrium is:

$$V_{bi} = V_T \ln\!\left(\frac{N_a N_d}{n_i^2}\right) \qquad\text{where } V_T = \frac{kT}{q} = 25.85\text{ mV}$$

For $N_a = N_d = 10^{16}$/cm³:

$$V_{bi} = 0.02585 \times \ln\!\left(\frac{10^{16} \times 10^{16}}{(10^{10})^2}\right) = 0.02585 \times \ln(10^{12}) = 0.02585 \times 27.63 = \mathbf{0.714\ V}$$

**That number should look familiar.** The "0.7 V silicon diode drop" quoted in every electronics text is not a measured curiosity — it falls straight out of the doping levels, the intrinsic carrier concentration, and $kT$. You have just derived it.

| $N_a$, $N_d$ (/cm³) | $V_{bi}$ (V) | Depletion width (μm) |
| :--- | ---: | ---: |
| $10^{15}$, $10^{15}$ | 0.595 | 1.241 |
| $10^{16}$, $10^{16}$ | 0.714 | 0.430 |
| $10^{18}$, $10^{18}$ | 0.952 | 0.050 |
| $10^{19}$, $10^{16}$ | 0.893 | 0.340 |

**Heavier doping means a higher barrier and a narrower depletion region** — more ions per unit volume, so less width is needed to expose the same charge.

> [!NOTE]
> **You cannot measure $V_{bi}$ with a voltmeter.** Probing the junction creates two new metal-semiconductor contacts whose own built-in potentials cancel it exactly. This is required by thermodynamics: a device that produced a usable voltage from nothing at equilibrium would be a perpetual motion machine.

---

## 4. Bias — the barrier is adjustable

### Forward bias — P positive

Connect the positive supply terminal to P and negative to N. The applied voltage **opposes** the built-in field.

The barrier drops from $V_{bi}$ to $V_{bi} - V_{applied}$, and the depletion region **narrows** — 0.430 μm at equilibrium, 0.327 μm at +0.3 V, 0.235 μm at +0.5 V.

With a lower barrier, far more carriers have enough thermal energy to cross. And because the fraction of carriers exceeding an energy barrier follows a **Boltzmann distribution**, lowering the barrier linearly increases the current **exponentially**.

### Reverse bias — N positive

Reverse the connection and the applied voltage **reinforces** the built-in field. The barrier rises, and the depletion region **widens** — 0.666 μm at −1 V, 1.216 μm at −5 V.

Majority carriers now face a taller barrier and essentially none cross. **Current very nearly stops.**

What remains is a tiny leakage: minority carriers — the $10^4$/cm³ holes in N-type material — that wander into the depletion region are swept across by the field. This is the **saturation current** $I_S$, typically around $10^{-12}$ A.

**$I_S$ does not depend on the reverse voltage**, because it is limited by how many minority carriers are *generated*, not by how hard they are pulled. Doubling the reverse voltage does not double the leakage. But $I_S$ **does** depend strongly on temperature, since minority carriers come from thermal generation — which is why leakage roughly doubles every 10 °C.

### The diode equation

$$I = I_S\left(e^{V/(n V_T)} - 1\right)$$

with $n$ the ideality factor (1 for an ideal diode). Reading the two limits:

- **Forward, $V \gg V_T$:** the exponential dominates and current rises steeply.
- **Reverse, $V$ negative:** the exponential vanishes and $I \to -I_S$.

| Voltage | Current |
| ---: | ---: |
| −5.00 V | $-1.000 \times 10^{-12}$ A |
| −0.50 V | $-1.000 \times 10^{-12}$ A |
| 0.00 V | 0 A |
| +0.30 V | $1.096 \times 10^{-7}$ A |
| +0.50 V | $2.510 \times 10^{-4}$ A |
| +0.60 V | $1.201 \times 10^{-2}$ A |
| +0.70 V | $5.748 \times 10^{-1}$ A |

**Between −5 V and −0.5 V the current is identical.** That is rectification: the device genuinely does not care how hard you push backwards.

```
                     I ▲
                       │        ╱  ← exponential rise
                       │       ╱      (~0.7 V "turn-on")
                       │      ╱
                       │    ╱
   ────────────────────┼───╱──────────> V
        ← reverse      │  ╱   forward →
      (flat at -I_S)   │ ╱
                       │
```

### The 60 mV rule

How much extra voltage multiplies the current by ten?

$$\Delta V = V_T \ln(10) = 0.02585 \times 2.303 = \mathbf{59.5\ mV}$$

**About 60 mV per decade of current, at room temperature.** Verified in the lab: 12.01 mA at 0.600 V becomes 120.1 mA at 0.660 V.

This is why a diode appears to have a fixed "0.7 V drop". The current changes by orders of magnitude while the voltage barely moves, so across any normal operating range it looks like a constant.

> [!NOTE]
> **Remember this number — it returns as a fundamental limit.** The same Boltzmann statistics govern a MOSFET turning on, giving a **subthreshold swing** that cannot be better than ~60 mV/decade at room temperature.
>
> That limit is why supply voltages stopped falling below about 1 V, which is why the $V^2$ discount in [[how-computers-work/01-electricity/02-resistance-and-ohms-law|module 2]]'s power equation ran out, which is why clock speeds plateaued and processors went multicore.
>
> **A statistical fact about electron energies sets the number of cores in your laptop.** Four modules apart, the same 60 mV.

---

## 5. Predict before reading on

A silicon diode carries 1 mA at 0.65 V.

**(a)** Roughly what voltage gives 10 mA? **(b)** What about 100 mA? **(c)** What does this say about "the" forward voltage of a diode?

<details><summary>Check your answers</summary>

**(a)** Each decade costs ~59.5 mV, so **≈ 0.71 V**.
**(b)** Another decade: **≈ 0.77 V**.
**(c)** A diode has no single forward voltage. Current changed **100×** while voltage moved 119 mV — under 20%. "0.7 V" is shorthand for "somewhere near 0.7 V across the currents we normally use", not a device constant.

This is why diode circuits are designed with a **series resistor to set the current**, then the diode's voltage is whatever it is. Driving a diode from a fixed voltage source is a good way to destroy it: a 50 mV error changes the current by a factor of ~7.
</details>

---

## 6. Breakdown and the useful variants

Push the reverse voltage high enough and current suddenly flows regardless.

- **Avalanche breakdown** — the field accelerates a stray carrier hard enough to knock others out of bonds by impact; those are accelerated too, and the process cascades. Dominant above ~6 V.
- **Zener breakdown** — in heavily doped junctions the depletion region is so narrow that electrons **quantum-tunnel** straight through. Dominant below ~5 V.

**Breakdown is not inherently destructive.** It destroys the device only if the resulting power exceeds what the package can dissipate. Held within limits, it is sharp and stable — which makes it useful.

Four devices, all one junction:

| Device | What it exploits |
| :--- | :--- |
| **Rectifier diode** | Forward conduction, reverse blocking — AC to DC |
| **Zener diode** | Deliberate, stable breakdown at a chosen voltage — a voltage reference |
| **LED** | Forward recombination releasing energy as photons. Needs a **direct** band gap, so GaAs and GaN, not silicon ([[how-computers-work/02-semiconductors/03-energy-bands|module 8]]) |
| **Photodiode / solar cell** | Reverse mode: incoming photons create electron-hole pairs that the depletion field sweeps out as current |

**The LED and the photodiode are the same device run in opposite directions** — one converts current to light, the other light to current.

---

## 7. Worked example — runnable

Save as `junction_lab.py` and run `python3 junction_lab.py`.

```python
import math

Q = 1.602176634e-19          # coulombs
K_EV = 8.617333e-5           # eV per kelvin
N_I = 1.0e10                 # per cm^3
EPS_SI = 11.7 * 8.854e-14    # farads per cm
T = 300.0

def thermal_voltage(temperature_k=T):
    """kT/q in volts -- 25.85 mV at room temperature."""
    return K_EV * temperature_k

def built_in_potential(n_acceptors, n_donors, temperature_k=T):
    """The barrier that forms at equilibrium, in volts."""
    return thermal_voltage(temperature_k) * math.log(
        n_acceptors * n_donors / N_I**2)

def depletion_width(n_acceptors, n_donors, applied_v=0.0):
    """Total depletion width in cm. Positive applied_v = forward bias."""
    v = built_in_potential(n_acceptors, n_donors) - applied_v
    if v <= 0:
        return 0.0
    return math.sqrt(2 * EPS_SI * v / Q * (1/n_acceptors + 1/n_donors))

def diode_current(voltage, i_sat=1e-12, ideality=1.0, temperature_k=T):
    """Shockley diode equation, amperes."""
    vt = thermal_voltage(temperature_k)
    return i_sat * (math.exp(voltage / (ideality * vt)) - 1)

if __name__ == "__main__":
    vt = thermal_voltage()
    print(f"thermal voltage V_T = kT/q = {vt*1000:.2f} mV at {T:.0f} K")
    print()

    print("built-in potential vs doping:")
    for na, nd in [(1e15, 1e15), (1e16, 1e16), (1e18, 1e18), (1e19, 1e16)]:
        vbi = built_in_potential(na, nd)
        w = depletion_width(na, nd)
        print(f"  Na={na:.0e} Nd={nd:.0e}  V_bi = {vbi:.3f} V"
              f"  depletion width = {w*1e4:.3f} um")

    print()
    print("depletion width vs bias (Na = Nd = 1e16):")
    for v in (-5.0, -1.0, 0.0, 0.3, 0.5):
        w = depletion_width(1e16, 1e16, v)
        label = "reverse" if v < 0 else ("equilibrium" if v == 0 else "forward")
        print(f"  {v:+5.1f} V ({label:11s}) -> {w*1e4:.3f} um")

    print()
    print("diode current vs voltage:")
    for v in (-5.0, -0.5, 0.0, 0.3, 0.5, 0.6, 0.7):
        i = diode_current(v)
        print(f"  {v:+5.2f} V -> {i:12.3e} A")

    # The 60 mV/decade rule -- the same number that limits MOSFET switching
    decade = math.log(10) * vt
    print()
    print(f"one decade of current costs ln(10)*V_T = {decade*1000:.1f} mV")
    i1, i2 = diode_current(0.6), diode_current(0.6 + decade)
    print(f"  check: {i1:.3e} A at 0.600 V, {i2:.3e} A at {0.6+decade:.3f} V"
          f"  (x{i2/i1:.1f})")

    assert 0.6 < built_in_potential(1e16, 1e16) < 0.8
    assert depletion_width(1e16, 1e16, -5.0) > depletion_width(1e16, 1e16, 0.0)
    assert depletion_width(1e16, 1e16, 0.5) < depletion_width(1e16, 1e16, 0.0)
    assert abs(diode_current(-5.0) + 1e-12) < 1e-15   # reverse -> -I_sat
    assert abs(i2 / i1 - 10.0) < 0.1
    print()
    print("junction_lab: passed")
```

Expected output:

```
thermal voltage V_T = kT/q = 25.85 mV at 300 K

built-in potential vs doping:
  Na=1e+15 Nd=1e+15  V_bi = 0.595 V  depletion width = 1.241 um
  Na=1e+16 Nd=1e+16  V_bi = 0.714 V  depletion width = 0.430 um
  Na=1e+18 Nd=1e+18  V_bi = 0.952 V  depletion width = 0.050 um
  Na=1e+19 Nd=1e+16  V_bi = 0.893 V  depletion width = 0.340 um

depletion width vs bias (Na = Nd = 1e16):
   -5.0 V (reverse    ) -> 1.216 um
   -1.0 V (reverse    ) -> 0.666 um
   +0.0 V (equilibrium) -> 0.430 um
   +0.3 V (forward    ) -> 0.327 um
   +0.5 V (forward    ) -> 0.235 um

diode current vs voltage:
  -5.00 V ->   -1.000e-12 A
  -0.50 V ->   -1.000e-12 A
  +0.00 V ->    0.000e+00 A
  +0.30 V ->    1.096e-07 A
  +0.50 V ->    2.510e-04 A
  +0.60 V ->    1.201e-02 A
  +0.70 V ->    5.748e-01 A

one decade of current costs ln(10)*V_T = 59.5 mV
  check: 1.201e-02 A at 0.600 V, 1.201e-01 A at 0.660 V  (x10.0)

junction_lab: passed
```

---

## 8. What a junction still cannot do

The junction is a genuine achievement. It rectifies, it emits light, it detects light, it regulates voltage. It is the foundation of power supplies and of every solar panel.

**And it cannot compute.**

Look at what it offers: **two terminals**. Current between them is a fixed function of the voltage across them. The diode has no say in the matter — its behaviour is entirely determined by its own two connections.

**[[how-computers-work/01-electricity/03-circuit-laws|Module 3]] told you what a switch requires:** a component whose resistance between two terminals is set by a **third, separate** terminal. That is what lets one signal control another, which is what makes a gate, which is what makes logic.

**A two-terminal device can never do that**, no matter how nonlinear it is. Non-linearity is necessary but not sufficient. **You need a third terminal, and you need it to have control without being part of the conducting path.**

So Part III ends one step short — with the barrier being the key realisation. The junction's depletion region is a barrier whose width **responds to voltage**. If you could adjust that barrier with a terminal that is *not* one of the two carrying current, you would have your switch.

**That is precisely what a transistor is**, and it is what Part IV builds.

---

## 9. Common pitfalls and traps

1. **Thinking the depletion region is a physical gap.** The crystal is continuous and unbroken. Only *mobile carriers* are absent; atoms and ionised dopants are all still there.
2. **Believing a diode has a fixed 0.7 V drop.** It is a logarithmic function of current. 0.7 V is shorthand for the range you usually operate in.
3. **Trying to measure $V_{bi}$ directly.** Your probes add their own contact potentials that cancel it exactly. Thermodynamics forbids extracting it.
4. **Assuming reverse current grows with reverse voltage.** $I_S$ is set by minority carrier generation, not by the applied field. It is flat with voltage and steep with temperature.
5. **Thinking breakdown destroys the diode.** Excessive *power* does. Zener diodes operate in breakdown continuously by design.
6. **Expecting silicon LEDs.** Silicon's indirect gap means a recombining electron must also shed momentum, which goes into lattice vibration rather than light. LEDs need direct-gap materials.
7. **Driving a diode from a voltage source.** Because of the exponential, a small voltage error produces a large current error. Always limit current with a series resistor or a current source.

---

## 10. Check your understanding

1. **Why does the depletion region widen under reverse bias and narrow under forward bias?**
   <details><summary>Answer</summary>
   The depletion width is set by how much exposed ion charge is needed to sustain the total barrier voltage. Reverse bias <em>adds</em> to the built-in potential, so more charge must be exposed, so the region widens. Forward bias <em>subtracts</em>, so less charge is needed and it narrows.<br>
   This variable width also makes the junction a voltage-controlled capacitor — two conducting regions separated by a variable insulating gap. That is a <strong>varactor</strong>, used for tuning radio circuits.
   </details>

2. **Why doesn't diffusion continue until the electrons are evenly spread across both sides?**
   <details><summary>Answer</summary>
   Because diffusing carriers leave behind exposed, immobile dopant ions, and that separated charge creates an electric field opposing further diffusion. Equilibrium is reached when the drift current driven by that field exactly cancels the diffusion current.<br>
   The concentrations never equalise. The junction is in a <strong>dynamic</strong> equilibrium — both currents are large and flowing continuously, but they cancel, so no net current flows.
   </details>

3. **A diode's reverse leakage is 1 nA at 25 °C. Estimate it at 85 °C, and say why this matters for a chip.**
   <details><summary>Answer</summary>
   Leakage roughly doubles every 10 °C. From 25 °C to 85 °C is 60 °C — six doublings, so $2^6 = 64$×, giving about <strong>64 nA</strong>.<br>
   In a chip with billions of junctions this is the dominant component of static power. It also creates a positive feedback risk: leakage heats the chip, heat increases leakage. Preventing <strong>thermal runaway</strong> constrains cooling and power delivery design, and is one reason chips throttle when hot.
   </details>

4. **Why is a two-terminal device fundamentally unable to build logic, regardless of how nonlinear it is?**
   <details><summary>Answer</summary>
   Logic requires one signal to control another. With only two terminals, the current is a fixed function of the voltage across those same two terminals — there is no input separate from the output, so no external signal can steer the device's behaviour.<br>
   A gate needs a <strong>control terminal that is not part of the conducting path</strong>, so the controlling signal is not loaded by the controlled current. That third terminal is exactly what a transistor adds, and it is why the transistor, not the diode, is the foundation of computing.
   </details>

---

## 11. Practice — independent task

**Task:** You are characterising a junction with $N_a = 10^{17}$/cm³ and $N_d = 10^{15}$/cm³ — an asymmetric, "one-sided" junction.

- **(a)** Compute $V_{bi}$ and the depletion width at equilibrium.
- **(b)** Compute the depletion width at −10 V and at +0.4 V. By what factor does it change across that range?
- **(c)** The depletion region is asymmetric: it extends further into the *lightly* doped side. Reason out why, then verify with $x_p N_a = x_n N_d$ (charge on each side must balance). What fraction of the width lies in the N side?
- **(d)** Using $I_S = 10^{-14}$ A, compute the voltage needed for 1 mA, 10 mA, and 100 mA. Confirm the spacing matches the 60 mV rule.
- **(e)** Repeat (d) at 100 °C (373 K). Does the diode need more or less voltage for 10 mA? Explain, noting that $I_S$ also rises with temperature — state which effect your calculation captures and which it omits.
- **(f)** Add a `voltage_for_current(target_i, i_sat, temperature_k)` function that inverts the diode equation, and verify it reproduces (d).

**Done when:** your inversion function agrees with the forward calculation, and you can explain why the depletion region sits mostly in the lightly doped side — a fact that matters directly for MOSFET design in Part IV.

<details><summary>Hint for (c), only if stuck</summary>
The total exposed positive charge must equal the total exposed negative charge — the depletion region as a whole is neutral. Charge on a side is (ion concentration) × (width on that side). With $N_a$ 100× larger than $N_d$, the P side needs only 1/100th the width to expose the same charge, so <strong>~99% of the depletion region lies in the lightly doped N side</strong>.
</details>

---

## 12. Tradeoffs and limits of this model

- **The abrupt junction is an idealisation.** Real doping profiles grade smoothly, especially with diffusion. The formulas here are the standard first approximation.
- **The ideal diode equation omits real effects.** Recombination inside the depletion region raises the ideality factor $n$ towards 2 at low current; series resistance flattens the curve at high current; high-level injection changes the physics again. Real diodes have $n$ between 1 and 2.
- **Breakdown voltage is not predicted here.** It depends on doping, geometry and edge effects, and is usually determined empirically.
- **$V_{bi}$ has an upper limit.** As doping approaches degeneracy the formula breaks down, since it assumes non-degenerate Boltzmann statistics.

---

## Before moving on

**This is the end of Part III.** You are ready for Part IV when you can, closed-book:

- [ ] Explain the four steps by which a depletion region forms, and why the process is self-limiting.
- [ ] Explain why the immobility of ionised dopants is essential to the whole mechanism.
- [ ] Derive $V_{bi} \approx 0.7$ V from doping levels, $n_i$ and $kT$.
- [ ] Explain forward and reverse bias in terms of barrier height and depletion width.
- [ ] Explain the 60 mV/decade rule and where else it appears in this course.
- [ ] Explain why a two-terminal device cannot build logic.

**Recap:** Joining P-type and N-type causes carriers to diffuse and recombine, emptying a region near the boundary. The immobile ionised dopants left behind create a space charge and an electric field that opposes further diffusion, so the junction reaches a self-limiting equilibrium with a built-in potential of about 0.7 V. Forward bias lowers the barrier and current rises exponentially at 60 mV per decade; reverse bias raises it and only tiny minority-carrier leakage flows. The junction rectifies, but with only two terminals it cannot let one signal control another, so it cannot compute.

**Next:** [[how-computers-work/03-transistors/01-what-a-transistor-is|Module 11 — What a Transistor Is]] begins Part IV and adds the third terminal. Everything from Part III is now in place: doped regions, junctions, barriers whose width responds to voltage, and an insulator (SiO₂, 9 eV) grown from the silicon itself.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/02-semiconductors/04-doping|Module 9 — Doping]] — the two materials joined here
- [[how-computers-work/03-transistors/02-mosfet-physics|Module 12 — MOSFET Physics]] — where the controllable barrier becomes a switch
- [[how-computers-work/01-electricity/03-circuit-laws|Module 3]] — the third-terminal requirement stated
- [[foundations/hardware/01-electricity|hardware/electricity]] — diodes as practical components
