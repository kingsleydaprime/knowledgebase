# Module 2: Resistance and Ohm's Law (The Cost of Moving Charge)

**[Beginner]** — The third quantity, the one equation that links all three, and the power relationship that has dictated the shape of every processor built since 2005.

## Before you start

- You can define charge, current and voltage — [[how-computers-work/01-electricity/01-charge-current-and-voltage|module 1]].
- You can rearrange $V = I \times R$ into its other two forms.
- You know that $P = VI$, derived at the end of module 1.

**After this lesson you will be able to:**

1. Explain physically why resistance exists, in terms of what electrons collide with.
2. Apply Ohm's law and the three power formulas, and choose the right one for the quantities you have.
3. Calculate a current-limiting resistor and the power it must dissipate.
4. Explain why processor clock speeds stopped increasing around 2005, using the power equation.

**Study route:** sections 1–5 are the core. Section 6 is where the whole course starts pointing forwards — do not skip it, it is the reason CMOS exists.

---

## 1. Why this exists (real-world motivation)

Module 1 gave you a push (voltage) and a flow (current). It did not say how much flow a given push produces. That depends entirely on what you are pushing through, and the answer matters enormously in practice.

Connect a 9 V battery across a copper wire and you get a short circuit — hundreds of amperes, a very hot wire, and possibly a fire. Connect the same battery across a piece of glass and you get essentially nothing. Same push, wildly different flow.

**Resistance is the quantity that captures this difference**, and understanding it turns out to be far more than bookkeeping. Resistance is where electrical energy becomes heat, and heat is the hard ceiling on computation. Every design decision from transistor sizing to datacentre architecture is ultimately a negotiation with the equations in this module.

---

## 2. Terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **Resistance** ($R$, ohms Ω) | How much a component opposes current for a given voltage | Pipe narrowness |
| **Resistivity** ($\rho$, Ω·m) | Resistance of the *material itself*, independent of shape | How rough the pipe's inner surface is |
| **Conductance** ($G$, siemens) | The reciprocal of resistance, $G = 1/R$ | How easily current flows |
| **Ohmic device** | One where $R$ is constant — doubling $V$ doubles $I$ | A resistor |
| **Non-ohmic device** | One where $R$ changes with conditions | A diode, a transistor, a lightbulb filament |
| **Power** ($P$, watts) | Energy converted per second, $1 \text{ W} = 1 \text{ J/s}$ | How fast the component heats up |
| **Dissipation** | Electrical energy irreversibly becoming heat | Why a laptop has a fan |

---

## 3. Where resistance comes from

A conductor is a crystal lattice of atoms with electrons drifting between them. That lattice is not still — every atom vibrates about its position, more violently the hotter the material is.

**Resistance is electrons scattering off those vibrations and off lattice imperfections.** An electron accelerates under the field, travels a short distance, collides, loses its accumulated momentum as heat, and starts again. The drift velocity from module 1 is precisely the average of this stop-start motion.

```
   Ideal (no resistance):        Real conductor:

   e⁻ ──────────────────>        e⁻ ─╮ ╭─╮ ╭──╮ ╭─>
      accelerates freely             ╰─╯ ╰─╯  ╰─╯
                                   collide, lose energy as heat
                                   ●    ●    ●    ●
                                   vibrating lattice atoms
```

Three consequences fall directly out of this picture, and each one will matter later:

- **Longer conductor → more resistance.** More distance means more collisions.
- **Wider conductor → less resistance.** More parallel paths for carriers to take.
- **Hotter conductor → more resistance** (for metals). More violent vibration means more scattering. This is why an incandescent bulb's resistance rises sharply once it lights up.

Combining the first two gives the geometric form:

$$R = \rho \frac{L}{A}$$

where $\rho$ is the material's resistivity, $L$ its length and $A$ its cross-sectional area. Copper's resistivity is about $1.68 \times 10^{-8}$ Ω·m; glass is around $10^{12}$ Ω·m — **twenty orders of magnitude apart.** That colossal gap is what makes conductors and insulators feel like different kinds of thing rather than two ends of a scale.

> [!NOTE]
> **Silicon sits between them**, around $10^{3}$ Ω·m pure — hence *semi*conductor. And unlike copper or glass, that value can be tuned across many orders of magnitude by adding trace impurities. That tunability is the entire reason computers are made of silicon, and it is the subject of [[how-computers-work/02-semiconductors/04-doping|module 9]].

---

## 4. Ohm's Law

$$V = I \times R$$

Voltage across a component equals the current through it times its resistance. Rearranged:

$$I = \frac{V}{R} \qquad\qquad R = \frac{V}{I}$$

**Ohm's law is not a law of nature.** It is a *description of a class of materials* — those whose resistance stays constant as voltage varies. Metals at constant temperature obey it well. Many of the most important devices in this course do not obey it at all: a diode's resistance collapses above its forward voltage ([[how-computers-work/02-semiconductors/05-pn-junctions|module 10]]), and a MOSFET's resistance is *controlled by a third terminal*, which is exactly what makes it useful ([[how-computers-work/03-transistors/02-mosfet-physics|module 12]]).

Keep the distinction sharp: Ohm's law is a tool for the ohmic parts of a circuit, not a universal truth.

---

## 5. Power — three forms of one equation

From module 1 we derived $P = VI$ from definitions alone. Substituting Ohm's law gives two more forms:

$$P = VI \qquad P = I^2 R \qquad P = \frac{V^2}{R}$$

All three are the same statement. **Pick whichever uses the two quantities you actually know:**

| You know | Use |
| :--- | :--- |
| Voltage across it and current through it | $P = VI$ |
| Current through it and its resistance | $P = I^2R$ |
| Voltage across it and its resistance | $P = V^2/R$ |

The $I^2$ and $V^2$ terms are the ones with teeth. **Double the current, quadruple the heat.** This is why transmission lines run at hundreds of kilovolts: for the same delivered power, higher voltage means proportionally lower current, and losses fall with the *square* of that reduction.

### Worked example — driving an LED

**Setup:** a 5 V supply, an LED that drops 2.0 V across itself and needs 20 mA to light properly.

**Step 1 — how much voltage is left for the resistor?** The LED takes 2.0 V of the available 5 V, so the resistor must absorb the remaining:

$$V_R = 5.0 - 2.0 = 3.0 \text{ V}$$

**Step 2 — what resistance gives 20 mA at 3 V?**

$$R = \frac{V_R}{I} = \frac{3.0}{0.02} = 150 \ \Omega$$

**Step 3 — how much power must that resistor survive?**

$$P = I^2 R = (0.02)^2 \times 150 = 0.0004 \times 150 = 0.06 \text{ W} = 60 \text{ mW}$$

A standard 1/4-watt (250 mW) resistor handles this with a wide margin. Had the answer come out near 250 mW you would need a physically larger part — power rating is about the component's ability to shed heat, not its resistance.

**Step 4 — sanity check the whole circuit.** Total power from the supply is $P = VI = 5 \times 0.02 = 0.1$ W. Of that, 60 mW is wasted as heat in the resistor and 40 mW goes into the LED. **The circuit is 40% efficient**, which is why current-limiting resistors are replaced by switching drivers in anything battery-powered.

---

## 6. Why this equation ended the megahertz race

This section is the reason module 2 exists in a computing course.

In a CMOS chip — the technology all of Part IV builds toward — most power is consumed *while switching*, charging and discharging the tiny capacitances of the circuit. The governing relationship is:

$$P_{\text{dynamic}} = \alpha \, C \, V^2 \, f$$

where $\alpha$ is the fraction of transistors switching, $C$ the switched capacitance, $V$ the supply voltage and $f$ the clock frequency.

Read what that says:

- **Power scales linearly with frequency.** Double the clock, double the power.
- **Power scales with the *square* of voltage.** Halve the voltage, quarter the power.

For decades this was a free lunch. Each process generation made transistors smaller, which let $V$ come down, which paid for a higher $f$ — a bargain known as **Dennard scaling**. Chips got faster *and* stayed within their power budget.

**Then it stopped.** Below roughly 1 volt, supply voltage cannot fall much further: transistors need enough gate voltage to switch reliably, and leakage current rises sharply as you approach the threshold. With $V$ pinned, the $V^2$ discount was gone, and raising $f$ meant paying full price in watts and heat.

### The calculation that shows it

Compare an early-1990s CPU (5 V, 33 MHz) with a modern one (1 V, 3 GHz), holding $\alpha C$ fixed:

$$\frac{P_{\text{modern}}}{P_{\text{old}}} = \frac{V_m^2 f_m}{V_o^2 f_o} = \frac{1^2 \times 3000}{5^2 \times 33} = \frac{3000}{825} \approx 3.6$$

**Voltage scaling bought a 25× reduction, and frequency spent 91× of it.** Net result: about 3.6 times the power, which is precisely the story of how CPU heatsinks went from a bare chip to a copper tower with a fan.

**This is why processors went multicore.** With single-core frequency capped by heat, the only way to spend more transistors usefully was to run several cores at a *lower* clock — trading the linear-in-$f$ power cost for parallelism. Every "why do I have 8 cores instead of one 30 GHz core" question terminates in the $V^2 f$ term above.

You will meet the consequences again in [[how-computers-work/03-transistors/03-cmos|module 13]] (why CMOS burns almost nothing when idle) and throughout [[foundations/computer-architecture/12-performance|computer-architecture/performance]].

---

## 7. Predict before reading on

You have a 100 Ω resistor rated at 1/4 watt. You connect it across a 12 V supply.

**Does it survive?**

<details><summary>Check your answer</summary>

$$P = \frac{V^2}{R} = \frac{144}{100} = 1.44 \text{ W}$$

**No.** It needs to dissipate 1.44 W and is rated for 0.25 W — nearly **six times** over. It will discolour, smell, and fail, possibly open-circuit and possibly on fire.

The safe voltage for a 1/4 W, 100 Ω resistor is $V = \sqrt{PR} = \sqrt{0.25 \times 100} = 5$ V. Note how the square relationship punishes you: going from 5 V to 12 V is only 2.4× the voltage but 5.8× the power.
</details>

---

## 8. Worked example — runnable

Save as `ohms_lab.py` and run `python3 ohms_lab.py`. Standard library only; writes no files.

```python
def resistor_for_led(supply_v, led_forward_v, target_current_a):
    """Series resistor value and the power it must dissipate."""
    v_across_resistor = supply_v - led_forward_v
    if v_across_resistor <= 0:
        raise ValueError("supply must exceed the LED forward voltage")
    r = v_across_resistor / target_current_a
    p = target_current_a ** 2 * r          # P = I^2 R
    return r, p

def dynamic_power_ratio(v_old, f_old, v_new, f_new):
    """Relative CMOS dynamic power, holding activity and capacitance fixed."""
    return (v_new ** 2 * f_new) / (v_old ** 2 * f_old)

if __name__ == "__main__":
    r, p = resistor_for_led(supply_v=5.0, led_forward_v=2.0, target_current_a=0.020)
    print(f"LED resistor: {r:.0f} ohm, dissipating {p*1000:.0f} mW")
    assert abs(r - 150.0) < 1e-9
    assert abs(p - 0.06) < 1e-9

    # Circuit efficiency: how much of the supply power reaches the LED?
    total = 5.0 * 0.020
    print(f"  supply delivers {total*1000:.0f} mW, LED gets {(total-p)*1000:.0f} mW"
          f" -> {100*(total-p)/total:.0f}% efficient")

    # The end of the megahertz race, in one line
    ratio = dynamic_power_ratio(v_old=5.0, f_old=33e6, v_new=1.0, f_new=3.0e9)
    print(f"5V/33MHz -> 1V/3GHz: dynamic power x{ratio:.1f}")
    assert 3.5 < ratio < 3.7

    # Boundary case: the resistor that cannot survive
    v, r_test = 12.0, 100.0
    print(f"12 V across 100 ohm: {v**2/r_test:.2f} W (a 1/4 W part fails)")

    print("ohms_lab: passed")
```

Expected output:

```
LED resistor: 150 ohm, dissipating 60 mW
  supply delivers 100 mW, LED gets 40 mW -> 40% efficient
5V/33MHz -> 1V/3GHz: dynamic power x3.6
12 V across 100 ohm: 1.44 W (a 1/4 W part fails)
ohms_lab: passed
```

---

## 9. Common pitfalls and traps

1. **Applying Ohm's law to non-ohmic devices.** An LED does not have "a resistance" you can look up — its current rises exponentially with voltage past the forward drop. You calculate the *resistor*, never the LED.
2. **Ignoring the power rating.** Resistance tells you the current; power tells you whether the part survives. Beginners size resistance correctly and let the component burn.
3. **Forgetting the square.** "I only doubled the voltage" quadruples the heat. This catches people repeatedly.
4. **Assuming resistance is constant with temperature.** For precision work and for anything that gets hot, it is not. A bulb filament's cold resistance can be a tenth of its hot resistance, which is why bulbs fail at switch-on.
5. **Treating $P = VI$ as applying to the whole supply when computing one component's heat.** Each component dissipates according to *its own* voltage and current.

---

## 10. Check your understanding

1. **A 3.3 V microcontroller pin sources 8 mA into a load. What is the load's effective resistance, and what power does it dissipate?**
   <details><summary>Answer</summary>
   $R = V/I = 3.3/0.008 = 412.5\ \Omega$. $P = VI = 3.3 \times 0.008 = 26.4$ mW.
   </details>

2. **Two identical resistors are available. You need to dissipate 0.5 W but each is rated 1/4 W. Does putting them in series across the same supply help?**
   <details><summary>Answer</summary>
   Yes. In series the total resistance doubles, so for a fixed supply voltage the current halves. Each resistor now sees half the voltage and half the current, dissipating $P/4$ each — total dissipation is halved, and it is split across two parts, so each handles a quarter of the original. The tradeoff is that you have also changed the circuit's current, which may not be acceptable.
   </details>

3. **Why do power companies transmit at 400 kV rather than at household voltage?**
   <details><summary>Answer</summary>
   Losses in the transmission line are $P_{loss} = I^2 R_{line}$. For a fixed delivered power $P = VI$, raising $V$ by a factor of $k$ lowers $I$ by $k$, which cuts line losses by $k^2$. Transmitting at 400 kV instead of 400 V reduces current 1000× and losses one million times.
   </details>

4. **A chip runs at 1.0 V and 2 GHz, dissipating 40 W. Its designers want 3 GHz. If voltage must rise to 1.1 V for the higher clock to be stable, what is the new dynamic power?**
   <details><summary>Answer</summary>
   $P_{new} = 40 \times \frac{1.1^2 \times 3}{1.0^2 \times 2} = 40 \times \frac{1.21 \times 3}{2} = 40 \times 1.815 = 72.6$ W.<br>
   A 50% frequency increase costs an <strong>81% power increase</strong>, because voltage had to rise too and it enters squared. This coupling is exactly why the industry stopped chasing clock speed.
   </details>

---

## 11. Practice — independent task

**Task:** You are designing the power budget for a small board.

- A 3.3 V rail supplies four LEDs, each with a 2.1 V forward drop, each needing 15 mA, each with its own series resistor.
- A microcontroller on the same rail draws 25 mA.

Compute:

- **(a)** The resistor value for one LED, and the nearest standard value at or above it (standard E12 values: 10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82 and their decade multiples).
- **(b)** The actual current through each LED once you use the standard value instead of the exact one.
- **(c)** The power dissipated in each resistor, and whether 1/8 W (125 mW) parts suffice.
- **(d)** Total current drawn from the 3.3 V rail with all four LEDs lit.
- **(e)** Total power drawn from the rail, and what fraction of it is wasted in the four resistors.

**Done when:** you have chosen a real, orderable resistor value, justified it, and can state the board's total current draw — the number you would need to select a regulator.

<details><summary>Hint for (a) and (b), only if stuck</summary>
Exact value is $(3.3 - 2.1)/0.015$. Round <em>up</em> to the next standard value — rounding down raises the current above your target and risks the LED. Then recompute the current with the standard value: $I = 1.2 / R_{standard}$.
</details>

---

## 12. Tradeoffs and limits

- **Resistors waste energy by design.** They are the simplest way to limit current and the least efficient. Anything battery-powered uses switching regulators instead, which are far more efficient and far more complex.
- **The dynamic power equation omits leakage.** Modern chips also burn **static power** — current leaking through transistors that are nominally off. Below about 65 nm this became a significant fraction of the total, and it is why chips power down whole regions rather than merely idling them. See [[how-computers-work/03-transistors/03-cmos|module 13]].
- **This is all steady-state.** Nothing here says how *fast* a voltage can change, which is the subject of [[how-computers-work/01-electricity/04-signals-and-time|module 4]] and the real limit on clock frequency.

---

## Before moving on

- [ ] Explain physically what electrons collide with, and why that produces heat.
- [ ] State all three power formulas and choose correctly between them.
- [ ] Size a current-limiting resistor and verify its power rating.
- [ ] Explain, using $P = \alpha C V^2 f$, why clock speeds plateaued and cores multiplied.
- [ ] Explain why silicon's resistivity sitting between copper's and glass's is the interesting fact.

**Recap:** Resistance is carrier scattering, geometrically $R = \rho L/A$. Ohm's law $V = IR$ describes ohmic materials, not all devices. Power has three interchangeable forms, and the squared terms mean small increases in voltage or current cause large increases in heat. In CMOS, $P = \alpha C V^2 f$ — the equation that ended the frequency race and produced multicore processors.

**Next:** [[how-computers-work/01-electricity/03-circuit-laws|Module 3 — Circuit Laws]] extends this from single components to networks, and builds the voltage divider, which is the mechanism behind every logic level in the rest of the course.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/01-electricity/01-charge-current-and-voltage|Module 1 — Charge, Current and Voltage]]
- [[foundations/computer-architecture/12-performance|computer-architecture/performance]] — where the power wall's architectural consequences are worked out
- [[foundations/hardware/01-electricity|hardware/electricity]] — practical component selection
