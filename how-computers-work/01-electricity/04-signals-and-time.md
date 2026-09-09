# Module 4: Signals and Time (Why Nothing Happens Instantly)

**[Beginner → Intermediate]** — Everything so far assumed voltages had already settled. They haven't. This module adds time, and time is what sets your processor's clock speed.

## Before you start

- You can analyse a resistive network and use the voltage divider — [[how-computers-work/01-electricity/03-circuit-laws|module 3]].
- You know that the electric field propagates far faster than electrons drift — [[how-computers-work/01-electricity/01-charge-current-and-voltage|module 1]].
- You have met exponentials informally; $e^{-x}$ shrinking towards zero is enough. No calculus is required.

**After this lesson you will be able to:**

1. Describe a periodic signal using amplitude, period, frequency and phase, and convert between period and frequency.
2. Explain why a voltage edge takes time, in terms of charging a capacitance through a resistance.
3. Compute an RC time constant and the time to reach a given fraction of the final voltage.
4. Explain what sets the maximum clock frequency of a synchronous digital system, and calculate it from a gate delay and a path length.

**Study route:** sections 1–5 build the model. Section 6 is the one that connects to processor design — read it slowly.

---

## 1. Why this exists (real-world motivation)

Modules 1–3 quietly assumed a steady state: connect the supply, wait, read the voltages. That assumption is fine for a lamp and useless for a computer, because a computer's entire job is *changing* voltages, billions of times a second.

The moment you ask "how fast can it change?" the answer stops being "instantly". A wire has capacitance. A transistor has an on-resistance. Charging a capacitance through a resistance takes time, and that time — repeated across every gate on a chip — is what stands between you and a faster processor.

**The clock speed printed on a CPU is, at bottom, a statement about how long it takes to charge some very small capacitors.** This module explains why.

---

## 2. Terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **DC** | Direct current — voltage constant over time | A battery |
| **AC** | Alternating current — voltage varying periodically | Mains electricity |
| **Period** ($T$, seconds) | Time for one complete cycle | One swing of a pendulum |
| **Frequency** ($f$, hertz) | Cycles per second, $f = 1/T$ | 50 Hz mains = 50 cycles/second |
| **Amplitude** | The size of the swing | How high the wave goes |
| **Phase** | Where in its cycle a wave is, relative to another | Two runners out of step |
| **Duty cycle** | Fraction of a period spent high | A 50% duty square wave is high half the time |
| **Capacitance** ($C$, farads) | Ability to store charge for a given voltage | A bucket's width |
| **Rise time** | Time to go from 10% to 90% of the final value | How sharp the edge is |
| **Propagation delay** ($t_{pd}$) | Time from an input changing to the output responding | The gate's reaction time |
| **Clock** | A square wave that tells every part of a circuit when to act | A conductor's baton |

---

## 3. Describing a periodic signal

A signal is a voltage that varies with time. The ones that matter here repeat.

```
      Sine wave (analogue, e.g. mains, radio)

   V  ┌╮      ╭─╮      ╭─╮
      │ ╲    ╱   ╲    ╱   ╲
   ───┼──╲──╱─────╲──╱─────╲──> t
      │   ╲╱       ╲╱
      └────────────────────
      |<--- T --->|


      Square wave (digital, e.g. a clock)

   V  ┌────┐    ┌────┐    ┌────
      │    │    │    │    │
   ───┘    └────┘    └────┘   ──> t
      |<-- T -->|
      |<-->| high    |<-->| low
```

**Period and frequency are reciprocals:**

$$f = \frac{1}{T} \qquad\qquad T = \frac{1}{f}$$

A 3 GHz clock has a period of $1/(3 \times 10^9) = 333$ picoseconds. In that time, light travels about 10 centimetres — which is a genuinely useful mental check on whether a signal can physically cross a chip within one cycle.

**Digital systems use square waves** because a square wave spends nearly all its time at one of two well-separated levels, and only a brief moment in between. That is exactly the shape the digital abstraction in [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]] needs.

---

## 4. Why edges are not vertical

Draw a square wave and the transitions look instantaneous. They are not, and the reason is **capacitance**.

**Capacitance is the ability to store charge at a given voltage:**

$$Q = C \times V$$

Every wire has some. Every transistor gate has some — a MOSFET's gate is literally a metal plate separated from the silicon by an insulator, which is the definition of a capacitor ([[how-computers-work/03-transistors/02-mosfet-physics|module 12]]). You do not add capacitance to a digital circuit; you are stuck with it.

To change a node's voltage you must move charge onto or off that capacitance, and that charge has to flow through some resistance — the on-resistance of whatever transistor is driving the node.

```
             R (driver's on-resistance)
   Vsupply ──/\/\/\──┬──── the node we're driving
                     │
                    ═╪═  C (wire + gate capacitance)
                     │
                    GND
```

### The RC time constant

Charging a capacitor through a resistor gives an exponential approach to the final value:

$$V(t) = V_{final}\left(1 - e^{-t/RC}\right)$$

The product $RC$ has units of seconds and is called the **time constant**, written $\tau$ (tau).

| Time elapsed | Fraction of final voltage reached |
| :--- | :--- |
| $1\tau$ | 63.2% |
| $2\tau$ | 86.5% |
| $3\tau$ | 95.0% |
| $5\tau$ | 99.3% — treated as "settled" |

**The shape is always the same** regardless of the actual values; only the horizontal scale changes. Fast charging, then a long tail as the remaining gap shrinks.

```
   V  final ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
              ╭──────────────────
            ╭─╯
          ╭─╯
        ╭─╯
      ╭─╯
    ╭─╯
   ─┴──────┬──────┬──────┬──────┬──────> t
    0      1τ     2τ     3τ     4τ
          63%    86%    95%    98%
```

Two useful landmarks, worth deriving once:

- **Time to reach 50%:** set $1 - e^{-t/\tau} = 0.5$, giving $t = \tau \ln 2 \approx 0.693\tau$.
- **Time to reach 90%:** $t = \tau \ln 10 \approx 2.303\tau$.

**Rise time** is conventionally measured 10% → 90%, which is $\tau(\ln 10 - \ln(10/9)) \approx 2.2\tau$.

> [!NOTE]
> **This is why smaller transistors made chips faster, and it is not the reason most people give.** Shrinking a transistor reduces both its gate capacitance and the length of the wires connecting it. Smaller $C$ means smaller $\tau$ means faster edges. Moore's law delivered speed primarily by shrinking $RC$, not by any change in how the logic worked.

---

## 5. Predict before reading on

A node has 10 fF (femtofarads, $10^{-14}$ F) of capacitance and is driven through a transistor with 5 kΩ of on-resistance.

**What is the time constant, and roughly how long until the node has settled?**

<details><summary>Check your answer</summary>

$$\tau = RC = 5000 \times 10^{-14} = 5 \times 10^{-11} \text{ s} = 50 \text{ ps}$$

Settled (5τ) at about **250 picoseconds**.

If a signal had to cross twenty such stages in series before the next clock edge, that is 5 nanoseconds, capping the clock at 200 MHz. Real high-speed designs keep the number of gate delays per stage small precisely because of this multiplication — which is the entire motivation for **pipelining** in [[foundations/computer-architecture/06-pipelining|computer-architecture/pipelining]].
</details>

---

## 6. Propagation delay and the clock ceiling

**Propagation delay ($t_{pd}$) is the time from an input changing to the output settling to its new valid value.** It bundles together the RC charging above, the time for the transistor to actually switch, and the wire delay.

In a synchronous digital system — which is nearly all of them — a clock signal defines moments at which every storage element captures its input. Between two clock edges, a signal must:

1. Emerge from a register when the clock ticks (**clock-to-Q delay**),
2. Propagate through however many gates lie in its path (**combinational delay**),
3. Arrive and be stable at the next register *before* the following edge (**setup time**).

```
   ┌─────────┐                                   ┌─────────┐
   │ Register│──> [gate] [gate] ... [gate] ────> │ Register│
   │    A    │       combinational logic         │    B    │
   └────▲────┘                                   └────▲────┘
        │                                             │
        └──────────────── clock ──────────────────────┘

   |<--------------- one clock period T -------------->|
   |<-t_cq->|<------ combinational delay ------>|<-t_su>|
```

**The critical path is the slowest such route anywhere in the design.** The clock period must be at least as long as it:

$$T_{min} = t_{cq} + t_{pd,\text{critical}} + t_{setup} \qquad\qquad f_{max} = \frac{1}{T_{min}}$$

### Worked example

A design has clock-to-Q of 30 ps, a setup time of 20 ps, and a critical path of 20 gates each with 20 ps of delay.

$$t_{pd} = 20 \times 20 = 400 \text{ ps}$$
$$T_{min} = 30 + 400 + 20 = 450 \text{ ps}$$
$$f_{max} = \frac{1}{450 \times 10^{-12}} \approx 2.22 \text{ GHz}$$

**Now shorten the critical path to 10 gates** by splitting the logic into two pipeline stages:

$$T_{min} = 30 + 200 + 20 = 250 \text{ ps} \qquad f_{max} = 4.0 \text{ GHz}$$

**Halving the critical path raised the clock by 1.8×, not 2×** — the fixed register overheads ($t_{cq} + t_{setup}$ = 50 ps) do not shrink. Push this far enough and the overheads dominate, which is why pipelines have an optimal depth rather than getting better forever. That result is derived properly in [[foundations/computer-architecture/06-pipelining|computer-architecture/pipelining]]; you now know where the numbers come from.

**This is the single most important practical consequence of Part II.** A processor's clock speed is not chosen. It is *deduced* from the slowest chain of gates on the chip, which is deduced from RC time constants, which are deduced from the physics of Part III.

---

## 7. Worked example — runnable

Save as `timing_lab.py` and run `python3 timing_lab.py`.

```python
import math

def time_constant(resistance_ohms, capacitance_farads):
    """RC, in seconds."""
    return resistance_ohms * capacitance_farads

def time_to_fraction(tau, fraction):
    """Time for an RC charge to reach the given fraction of its final value."""
    if not 0 < fraction < 1:
        raise ValueError("fraction must be strictly between 0 and 1")
    return -tau * math.log(1 - fraction)

def rise_time(tau):
    """Conventional 10%-to-90% rise time."""
    return time_to_fraction(tau, 0.9) - time_to_fraction(tau, 0.1)

def max_clock_hz(t_clk_q, gate_delay, gates_on_critical_path, t_setup):
    """Maximum clock frequency of a synchronous design."""
    period = t_clk_q + gate_delay * gates_on_critical_path + t_setup
    return 1.0 / period, period

if __name__ == "__main__":
    PS = 1e-12

    tau = time_constant(5000, 10e-15)          # 5 kohm driving 10 fF
    print(f"tau = {tau/PS:.0f} ps")
    print(f"  50% at {time_to_fraction(tau, 0.5)/PS:.1f} ps")
    print(f"  90% at {time_to_fraction(tau, 0.9)/PS:.1f} ps")
    print(f"  settled (99.3%) at {5*tau/PS:.0f} ps")
    print(f"  rise time (10-90%) = {rise_time(tau)/PS:.1f} ps")
    assert abs(time_to_fraction(tau, 0.5) - tau * math.log(2)) < 1e-18
    assert abs(rise_time(tau) / tau - 2.197) < 0.01

    print()
    for n_gates in (20, 10):
        f, period = max_clock_hz(30*PS, 20*PS, n_gates, 20*PS)
        print(f"{n_gates:2d}-gate critical path: T = {period/PS:.0f} ps"
              f" -> f_max = {f/1e9:.2f} GHz")

    f20, _ = max_clock_hz(30*PS, 20*PS, 20, 20*PS)
    f10, _ = max_clock_hz(30*PS, 20*PS, 10, 20*PS)
    print(f"halving the path improved the clock by {f10/f20:.2f}x, not 2x"
          f" -- register overhead does not shrink")

    print("timing_lab: passed")
```

Expected output:

```
tau = 50 ps
  50% at 34.7 ps
  90% at 115.1 ps
  settled (99.3%) at 250 ps
  rise time (10-90%) = 109.9 ps

20-gate critical path: T = 450 ps -> f_max = 2.22 GHz
10-gate critical path: T = 250 ps -> f_max = 4.00 GHz
halving the path improved the clock by 1.80x, not 2x -- register overhead does not shrink
timing_lab: passed
```

---

## 8. Common pitfalls and traps

1. **Believing digital signals are square.** They are trapezoids at best, and at multi-gigahertz they look more like sine waves. "Square" is a design intent, not a measurement.
2. **Confusing frequency with speed.** A higher clock does not help if the critical path cannot complete within the period — the circuit simply produces wrong answers. Timing closure, not frequency, is the real target.
3. **Forgetting that $\tau$ never fully completes.** An exponential approaches its final value asymptotically. Engineering practice picks a threshold (usually 5τ) and calls it done.
4. **Treating capacitance as a component you chose to add.** In digital design, virtually all of it is parasitic — wires and gates you needed anyway.
5. **Ignoring clock-to-Q and setup time.** For short critical paths these fixed overheads dominate, and omitting them makes pipelining look better than it is.

---

## 9. Check your understanding

1. **A clock runs at 2.5 GHz. What is its period, and how far does a signal travelling at $2 \times 10^8$ m/s get in one cycle?**
   <details><summary>Answer</summary>
   $T = 1/(2.5 \times 10^9) = 400$ ps. Distance $= 2 \times 10^8 \times 400 \times 10^{-12} = 0.08$ m = <strong>8 cm</strong>.<br>
   A large chip is around 2 cm across, so a signal can just about cross it in a cycle — but not with much margin, which is why clock distribution across a big die is a serious engineering problem in its own right.
   </details>

2. **Two nodes have the same capacitance, but one is driven by a transistor with twice the on-resistance. How do their rise times compare?**
   <details><summary>Answer</summary>
   $\tau = RC$, so double $R$ means double $\tau$ and double the rise time. This is why designers make transistors on critical paths physically wider — a wider transistor has lower on-resistance. The cost is that a wider transistor also presents more gate capacitance to <em>whatever drives it</em>, so the optimisation has a genuine tradeoff rather than a free win.
   </details>

3. **Why does a 50% duty cycle matter for a clock?**
   <details><summary>Answer</summary>
   Many circuits do work on both edges, or use the high and low phases for different operations (as in two-phase latch designs). An asymmetric clock shortens one of those phases and can violate its timing even though the overall frequency is within spec. Clock <em>duty cycle distortion</em> is a specified, budgeted parameter in real designs.
   </details>

4. **If shrinking transistors reduces both $R$ and $C$, why did clock speeds stop rising anyway?**
   <details><summary>Answer</summary>
   Because the limit stopped being $RC$ and became <strong>heat</strong>. From [[how-computers-work/01-electricity/02-resistance-and-ohms-law|module 2]], $P = \alpha C V^2 f$: raising $f$ raises power linearly, and once supply voltage could no longer be scaled down to compensate, the power budget became binding before the timing did. The transistors could switch faster; the package could not shed the heat. Two different physical limits, and the thermal one arrived first.
   </details>

---

## 10. Practice — independent task

**Task:** You are estimating the maximum clock for a small processor design.

Given: clock-to-Q = 25 ps, setup time = 15 ps, and each logic gate has a propagation delay of 18 ps. The four pipeline stages have critical paths of 12, 19, 14 and 8 gates respectively.

- **(a)** Compute the required clock period for each stage individually.
- **(b)** Which stage sets the clock for the whole processor, and what is $f_{max}$?
- **(c)** You may split exactly one stage into two. Which do you split, and what is the new $f_{max}$? Assume the split divides that stage's gates as evenly as possible.
- **(d)** How much did the split gain you as a percentage? Explain why it is less than you might expect from the gate counts alone.
- **(e)** Suppose instead every gate delay improved by 20% through a process shrink, with no pipeline change. Compare that gain to the gain from (c).

**Done when:** you can state which stage is the bottleneck, justify the split, and explain in one sentence why register overhead limits how much pipelining can buy.

<details><summary>Hint for (b), only if stuck</summary>
Every stage shares one clock, so the clock period must accommodate the <em>slowest</em> stage — the maximum of the per-stage periods, not the average or the sum. This is exactly why unbalanced pipelines waste time: the fast stages sit idle waiting for the slow one.
</details>

---

## 11. Tradeoffs and limits

- **The RC model is a simplification.** It treats the driver as a fixed resistor; a real transistor's resistance varies through the transition. SPICE simulation is used for accurate numbers. The RC model gets the *scaling* right, which is what matters for understanding.
- **Wires are not just capacitance.** At high frequency they have inductance and behave as transmission lines with reflections and impedance matching. That is a specialist topic and out of scope here.
- **Asynchronous designs exist.** Circuits without a global clock, using handshaking instead, avoid the critical-path ceiling. They are harder to design and verify, which is why they remain rare.
- **This module ignores noise entirely.** A real signal is never clean. What "clean enough" means is exactly the subject of the next module.

---

## Before moving on

- [ ] Convert between period and frequency and sanity-check a signal against the speed of light.
- [ ] Explain why an edge takes time, naming the resistance and the capacitance involved.
- [ ] Compute $\tau$, the 50% point, and the 10–90% rise time.
- [ ] Compute $f_{max}$ from clock-to-Q, gate delay, path length and setup time.
- [ ] Explain why halving a critical path gives less than double the clock.

**Recap:** Signals vary with time, described by period, frequency, amplitude and phase. Edges take time because charge must move onto a capacitance through a resistance, with time constant $\tau = RC$. Propagation delay accumulates along a path, and the slowest path — the critical path — plus register overheads sets the minimum clock period and therefore the maximum frequency.

**Next:** [[how-computers-work/01-electricity/05-the-digital-abstraction|Module 5 — The Digital Abstraction]] is the capstone of Part II. It explains how noise margins let you throw away everything in this module and think in ones and zeros — and exactly what you are trusting when you do.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[foundations/computer-architecture/06-pipelining|computer-architecture/pipelining]] — where critical-path shortening becomes an architecture
- [[foundations/computer-architecture/12-performance|computer-architecture/performance]] — clock frequency in context
- [[foundations/digital-signal-processing/index|digital-signal-processing/]] — the mathematical treatment of signals
