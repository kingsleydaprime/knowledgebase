# Module 1: Charge, Current and Voltage (What Is Actually Moving)

**[Beginner]** — The three quantities every other electrical idea is built from. By the end you should be able to say precisely what a wire carries, how fast it moves, and what a battery actually does to it.

## Before you start

- You can rearrange a simple equation — given $a = b \times c$, you can solve for $b$.
- You can read scientific notation: $1.6 \times 10^{-19}$ is a very small number, $8.5 \times 10^{28}$ is a very large one.
- Nothing else. No prior physics or electronics is assumed.

**After this lesson you will be able to:**

1. Define charge, current and voltage in one sentence each, without using the other two words circularly.
2. Calculate the number of electrons per second flowing through a wire carrying a given current.
3. Explain why a signal travels down a wire at nearly the speed of light while the electrons themselves crawl at centimetres per hour.
4. Explain why voltage is always *between two points*, and what "ground" means.

**Study route:** read sections 1–4, then stop and attempt the prediction in section 5 before reading on. The independent task at the end is a calculation, not code.

---

## 1. Why this exists (real-world motivation)

You want to build a machine that computes. Before it can compute anything, it needs some physical quantity it can push around, split into paths, block, and detect — something that moves fast, can be switched quickly, and does not wear out the way a mechanical part does.

Humans tried the alternatives. **Mechanical computers** used rotating gears and sliding rods; the Difference Engine's speed was limited by how fast brass can be moved without shaking itself apart. **Fluidic computers** pushed air or water through valves; they work, they are still used in a few radiation-hard environments, and they are agonisingly slow because fluids have mass and viscosity.

Electrons win for one reason: **they are almost nothing**. An electron's mass is about $9.1 \times 10^{-31}$ kg. You can start and stop a flow of them billions of times per second because there is essentially no inertia to fight. Everything in this course is downstream of that fact.

So the first question is not "how do we compute" but: **what exactly is it that we are pushing around, and what does pushing mean?**

---

## 2. Terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **Charge** ($Q$, coulombs) | A fundamental property of matter. Some particles have it, some don't. Like charges push apart, opposite charges pull together. | The "stuff" that electricity is made of |
| **Electron** | A particle carrying one unit of negative charge, $-1.602 \times 10^{-19}$ C | The thing that actually moves in a wire |
| **Current** ($I$, amperes) | The *rate* at which charge flows past a point. 1 A = 1 coulomb per second | Litres per second past a point in a pipe |
| **Voltage** ($V$, volts) | Energy per unit charge, *between two points*. 1 V = 1 joule per coulomb | Water pressure difference across a pump |
| **Conductor** | A material where electrons move freely | Copper, aluminium |
| **Insulator** | A material where electrons are locked in place | Glass, rubber, silicon dioxide |
| **Ground** | The point you *declare* to be 0 V, so other voltages have a reference | "Sea level" for altitude |

---

## 3. Charge — the underlying quantity

**Charge is not a substance. It is a property**, like mass. A particle does not *contain* charge the way a bucket contains water; it *has* charge the way it has mass.

There are two kinds, and their names are a historical accident. Benjamin Franklin guessed which one flowed in a wire, guessed wrong, and by the time anyone found out, all the textbooks were written. So:

- **Electrons** carry **negative** charge: $-1.602 \times 10^{-19}$ coulombs each.
- **Protons** carry **positive** charge, exactly equal and opposite, locked inside atomic nuclei and effectively immovable in a solid.

The unit, the **coulomb (C)**, is enormous relative to one electron. One coulomb is about $6.24 \times 10^{18}$ electrons — six billion billion. This matters for intuition: currents you meet in real circuits involve staggering numbers of particles, which is exactly why their collective behaviour is smooth and predictable rather than jumpy.

**Charge is conserved.** It is never created or destroyed, only moved. This is not a rule of thumb — it is one of the most precisely tested facts in physics, and it is the reason Kirchhoff's Current Law in [[how-computers-work/01-electricity/03-circuit-laws|module 3]] works exactly rather than approximately.

---

## 4. Current — charge in motion

**Current is the rate of charge flow past a point.**

$$I = \frac{\Delta Q}{\Delta t}$$

where $I$ is current in amperes, $\Delta Q$ is charge in coulombs, and $\Delta t$ is time in seconds. One ampere is one coulomb per second.

### The two conventions, and why they both survive

Franklin's wrong guess left us with **conventional current**, defined as flowing from **positive to negative** — the direction positive charge *would* move. Electrons, being negative, actually drift the opposite way.

```
        CONVENTIONAL CURRENT (what every circuit diagram uses)
        ────────────────────────────>
   ┌────────────────────────────────────────┐
   │                                        │
  +│            copper wire                 │−
   │                                        │
   └────────────────────────────────────────┘
        <────────────────────────────
        ELECTRON DRIFT (what physically happens)
```

Every schematic, datasheet and textbook equation in this course uses **conventional current**. It gives identical answers, because a positive charge moving right is electrically indistinguishable from a negative charge moving left. Use conventional current and forget the electrons — except in [[how-computers-work/02-semiconductors/04-doping|doping]] and [[how-computers-work/03-transistors/02-mosfet-physics|MOSFET physics]], where which carrier is moving genuinely changes the device's behaviour.

### The surprise: drift is glacially slow

Here is the fact that fixes most people's mental model. Electrons in a wire do **not** race along at the speed of light. Their average forward speed — the **drift velocity** — is calculated as:

$$v_d = \frac{I}{n q A}$$

where $n$ is the free-electron density of the material, $q$ is the charge per electron, and $A$ is the wire's cross-sectional area.

For copper ($n \approx 8.5 \times 10^{28}$ electrons per m³), a 1 mm² wire carrying 1 A:

$$v_d = \frac{1}{(8.5 \times 10^{28})(1.602 \times 10^{-19})(1 \times 10^{-6})} \approx 7.3 \times 10^{-5} \text{ m/s}$$

That is **0.073 mm per second** — about **26 centimetres per hour**. An electron leaving your wall socket would take most of a day to reach a lamp across the room.

### So why does the light come on instantly?

**Because the signal is not the electrons.** The wire is already packed full of free electrons everywhere along its length. When you close the switch, you establish an **electric field** through the conductor, and that field propagates at a substantial fraction of the speed of light — typically around $2 \times 10^8$ m/s in a normal wire.

Every electron along the whole wire starts drifting at essentially the same moment.

> [!NOTE]
> **The analogy that actually fits:** a pipe already completely full of water. Push one drop in at your end and a different drop immediately exits the far end. The *push* travels at the speed of sound in water; the individual drops barely move. Electricity works the same way, with the field playing the role of the pressure wave.
>
> This is not a decorative detail. It is why signal timing in a CPU is governed by **propagation delay** — how long the field takes to cross a wire — and not by electron speed. Come back to this in [[how-computers-work/01-electricity/04-signals-and-time|module 4]].

---

## 5. Predict before reading on

A wire carries a steady current of 2 amperes.

**How many electrons pass a given point each second?**

Work it out before continuing. You need only the definition of the ampere and the charge on one electron.

<details><summary>Check your answer</summary>

2 A = 2 coulombs per second. Each electron carries $1.602 \times 10^{-19}$ C.

$$\frac{2}{1.602 \times 10^{-19}} \approx 1.25 \times 10^{19} \text{ electrons per second}$$

**Twelve and a half billion billion electrons every second** — and yet each one is only ambling along at a fraction of a millimetre per second. Both facts are true at once, and holding them together is the point of this section.
</details>

---

## 6. Voltage — the thing that does the pushing

Current is flow. Something has to cause the flow. That something is **voltage**.

**Voltage is energy per unit charge:**

$$V = \frac{\text{Energy}}{\text{Charge}} \qquad 1 \text{ volt} = 1 \text{ joule per coulomb}$$

A 9 V battery gives every coulomb of charge that passes through it 9 joules of energy. That energy is then spent pushing through whatever the circuit contains.

### Voltage is always a difference

This is the single most common beginner error, so it gets its own heading.

**There is no such thing as "the voltage at a point."** Voltage is *always* the difference in electric potential between two points. Asking "what is the voltage here?" is exactly like asking "what is the altitude here?" without saying what you are measuring from — sea level, the ground floor, the centre of the earth?

```
        Point A                         Point B
          ●───────── 5 volts ─────────────●
             (A is 5 V higher than B)

   "The voltage at A" is meaningless on its own.
   "The voltage at A with respect to B is 5 V" is a complete statement.
```

When someone says "this pin is at 3.3 V", they mean **3.3 V relative to ground**, and they are relying on you to fill in the second half.

### Ground is a choice, not a thing

**Ground is whichever point you declare to be 0 V.** It is a convention, chosen for convenience, exactly like choosing sea level as the zero for altitude. Nothing physical distinguishes the ground node; you simply agree to measure everything else from it, and then every other voltage in the circuit has an unambiguous number.

This is why every chip has ground pins, and why two devices that do not share a ground cannot reliably exchange signals — they have no agreed zero, so "3.3 V" means different things to each of them.

### Where the water analogy breaks

The pressure analogy is genuinely useful and it will carry you through the next three modules. But state its limits now, so you are not surprised later:

| Water | Electricity | Where it breaks |
| :--- | :--- | :--- |
| Pressure | Voltage | Fine |
| Flow rate | Current | Fine |
| Pipe friction | Resistance | Fine |
| Water is a substance being consumed | Charge is *not* consumed — it returns to the source | A circuit is a loop; water can spill on the floor, charge cannot |
| Water flows in an open pipe | Current needs a **complete loop** | The single most important difference |
| Pressure propagates at ~1500 m/s | Field propagates at ~$2 \times 10^8$ m/s | Timing intuitions transfer badly |

**The loop requirement is the one to internalise.** Charge is conserved, so every electron leaving a battery's negative terminal must arrive back at its positive terminal. Break the loop anywhere and current everywhere stops instantly. This is why a switch works no matter where you put it in the circuit — and it is the entire basis of how a transistor controls a gate in [[how-computers-work/04-logic/01-gates-from-transistors|module 15]].

---

## 7. Worked example — a complete accounting

**Setup:** a 5 V supply drives a small load. The measured current is 20 mA (0.02 A), and it runs for 1 minute.

**Question 1 — how much charge moved?**

$$Q = I \times t = 0.02 \times 60 = 1.2 \text{ coulombs}$$

**Question 2 — how many electrons is that?**

$$\frac{1.2}{1.602 \times 10^{-19}} \approx 7.5 \times 10^{18} \text{ electrons}$$

**Question 3 — how much energy did the supply deliver?**

Each coulomb receives 5 joules, and 1.2 coulombs passed:

$$E = V \times Q = 5 \times 1.2 = 6 \text{ joules}$$

**Question 4 — what average power is that?**

$$P = \frac{E}{t} = \frac{6}{60} = 0.1 \text{ watts}$$

Notice that $P = E/t = (V \times Q)/t = V \times (Q/t) = V \times I$. We just derived the power equation $P = VI$ from the definitions alone, which is exactly how it will reappear in [[how-computers-work/01-electricity/02-resistance-and-ohms-law|module 2]]. Nothing was assumed.

### Optional check in code

Save as `charge_lab.py` and run `python3 charge_lab.py`. Standard library only; writes no files.

```python
ELECTRON_CHARGE = 1.602176634e-19  # coulombs, exact by SI definition since 2019

def electrons_per_second(current_amps):
    """How many electrons pass a point each second at this current."""
    return current_amps / ELECTRON_CHARGE

def drift_velocity(current_amps, area_m2, carrier_density):
    """Average forward speed of an individual electron, in m/s."""
    return current_amps / (carrier_density * ELECTRON_CHARGE * area_m2)

if __name__ == "__main__":
    COPPER_DENSITY = 8.5e28      # free electrons per cubic metre
    ONE_MM2 = 1e-6               # square metres

    n = electrons_per_second(2.0)
    print(f"2 A carries {n:.3e} electrons/second")
    assert 1.2e19 < n < 1.3e19

    v = drift_velocity(1.0, ONE_MM2, COPPER_DENSITY)
    print(f"1 A in 1 mm^2 copper: drift velocity {v*1000:.4f} mm/s")
    print(f"  = {v*3600*100:.1f} cm per hour")
    assert 0.05e-3 < v < 0.1e-3

    # The contrast that matters
    field_speed = 2e8  # m/s, roughly 2/3 c in a typical wire
    print(f"  field propagates {field_speed/v:.2e} times faster than the electrons")

    print("charge_lab: passed")
```

Expected output:

```
2 A carries 1.248e+19 electrons/second
1 A in 1 mm^2 copper: drift velocity 0.0734 mm/s
  = 26.4 cm per hour
  field propagates 2.72e+12 times faster than the electrons
charge_lab: passed
```

---

## 8. Common pitfalls and traps

1. **Saying "the voltage at pin 3" without a reference.** Always finish the sentence: *with respect to ground*. Two boards that don't share a ground have no common zero and will not communicate.
2. **Believing electrons travel at light speed.** They crawl. The *field* is fast. Getting this wrong makes propagation delay in module 4 incomprehensible.
3. **Thinking current is "used up" going round a circuit.** The current leaving a component equals the current entering it. *Energy* is consumed; *charge* is not. A resistor does not eat electrons.
4. **Confusing conventional current with electron flow in a physics context.** Harmless in circuit analysis, actively misleading once you reach semiconductors, where holes and electrons behave differently.
5. **Treating charge as a substance stored in a wire.** A wire is already electrically neutral and full of electrons. Connecting a battery does not fill it up; it makes what is already there start drifting.

---

## 9. Check your understanding

Attempt each before opening the answer.

1. **A 12 V car battery is rated at 60 amp-hours. How many coulombs of charge can it deliver, and how much energy does it store in joules?**
   <details><summary>Answer</summary>
   An amp-hour is one ampere for one hour. $Q = 60 \times 3600 = 216{,}000$ coulombs.<br>
   $E = V \times Q = 12 \times 216{,}000 = 2.59 \times 10^6$ joules, about 2.6 megajoules (roughly 0.72 kWh).
   </details>

2. **Why does a bird sit safely on a high-voltage power line?**
   <details><summary>Answer</summary>
   Voltage is a <em>difference</em>. Both feet touch the same conductor, so the potential difference across the bird is nearly zero — there is no push to drive current through it. It is also not part of a complete loop to ground. Touch a second wire at a different potential, or ground, and both conditions break at once.
   </details>

3. **Two wires carry the same 1 A current. Wire A is 1 mm² copper; wire B is 4 mm² copper. In which wire do individual electrons move faster, and by how much?**
   <details><summary>Answer</summary>
   In wire A, by a factor of 4. Drift velocity is $v_d = I/(nqA)$ — inversely proportional to cross-sectional area. Same current through a wider pipe means each carrier moves more slowly. Note the current is identical in both; it is the <em>speed of each carrier</em> that differs.
   </details>

4. **A circuit is broken by a switch 10 metres from the battery. When the switch closes, roughly how long before current begins flowing at the far end of the circuit — and how does that compare with the time for an electron to travel that 10 m?**
   <details><summary>Answer</summary>
   The field propagates at roughly $2 \times 10^8$ m/s, so about <strong>50 nanoseconds</strong>.<br>
   An electron drifting at 0.073 mm/s would take $10 / 7.3\times10^{-5} \approx 1.4 \times 10^5$ seconds — about <strong>38 hours</strong>. A factor of roughly $10^{12}$. The current starts everywhere at once; nothing waited for an electron to make the journey.
   </details>

---

## 10. Practice — independent task

**Task:** A USB 2.0 port supplies 5 V and can deliver up to 500 mA. A phone is charging at the full 500 mA for 90 minutes.

Compute, showing your working:

- **(a)** The total charge delivered, in coulombs.
- **(b)** The number of electrons that passed through the cable.
- **(c)** The total energy delivered, in joules and in watt-hours.
- **(d)** The average power in watts.
- **(e)** The cable's conductors are 0.2 mm² copper. What is the electron drift velocity, and how far does an individual electron travel during the whole 90-minute charge?

**Done when:** you have five numbers with correct units, and can state which of them surprised you and why. Part (e) is the one that should feel wrong — the answer is a few centimetres, over an hour and a half of charging.

<details><summary>Hint for (e), only if stuck</summary>
Use $v_d = I/(nqA)$ with $n = 8.5 \times 10^{28}$ m⁻³, $I = 0.5$ A, $A = 0.2 \times 10^{-6}$ m². Then multiply by 5400 seconds. Watch the units on area — square millimetres to square metres is a factor of $10^{-6}$, not $10^{-3}$.
</details>

---

## 11. Tradeoffs and limits of this model

- **This is the steady-state DC picture.** Everything here assumes current has settled to a constant value. Switching behaviour, where a signal is changing, needs the ideas in [[how-computers-work/01-electricity/04-signals-and-time|module 4]].
- **"Free electron density" is a simplification.** The Drude model treats electrons as a classical gas bouncing off atoms. It gives good numbers for metals and is wrong in interesting ways for semiconductors, which is precisely why [[how-computers-work/02-semiconductors/03-energy-bands|module 8]] replaces it with band theory.
- **Wires are treated as perfect here.** Real wires have resistance (module 2), and at high frequency they have inductance and capacitance that make them behave as transmission lines. That matters enormously for CPU design and is out of scope for this course.

---

## Before moving on

You are ready for module 2 when you can, closed-book:

- [ ] Define charge, current and voltage without using the other two words circularly.
- [ ] Calculate electrons per second from a current in amperes.
- [ ] Explain the instant-lamp puzzle: fast field, slow electrons, pre-filled wire.
- [ ] State why voltage needs two points and what ground is.
- [ ] Derive $P = VI$ from the definitions of voltage and current.

**Recap:** Charge is a conserved property of matter. Current is its rate of flow, one ampere being one coulomb per second, and individual carriers drift far more slowly than intuition suggests. Voltage is energy per coulomb, always measured between two points, with ground as the declared zero. A circuit must form a complete loop because charge is conserved.

**Next:** [[how-computers-work/01-electricity/02-resistance-and-ohms-law|Module 2 — Resistance and Ohm's Law]] introduces the third quantity that links voltage and current, and derives the power equation that ultimately limits how fast any chip can run.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[foundations/hardware/01-electricity|hardware/electricity]] — the practical counterpart: picking resistors, driving LEDs, working with real components
- [[how-computers-work/02-semiconductors/01-atoms-and-electrons|Module 6 — Atoms and Electrons]] — why some materials have free electrons at all
