# Module 19: Buffers, Fan-out and Driving Real Wires

**[Intermediate]** — Part V ends with the layer between logic and physics. A gate's output is not an idea — it is a transistor that must physically charge every wire and input it connects to, and there is a limit.

## Before you start

- You can build gates from CMOS networks — [[how-computers-work/04-logic/01-gates-from-transistors|module 15]].
- You know $\tau = RC$ and that edges take time — [[how-computers-work/01-electricity/04-signals-and-time|module 4]].
- You know noise margins and what the forbidden zone costs — [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]].
- You know an "on" transistor is a resistor set by $W/L$ — [[how-computers-work/03-transistors/02-mosfet-physics|module 12]].

**After this lesson you will be able to:**

1. Explain what a buffer is and why a gate that computes nothing is worth building.
2. Calculate fan-out delay and design a buffer tree.
3. Explain tri-state outputs, and why a bus needs exactly one driver.
4. Explain floating inputs, bus contention and decoupling — the three faults that make real boards fail.

**Study route:** section 3 is fan-out, section 5 is tri-state, section 6 is the practical electrical layer you need before building anything physical.

---

## 1. Why this exists (real-world motivation)

Every diagram so far has drawn a gate's output as a line going wherever it is needed. **Lines are free in diagrams. They are not free in silicon or on a breadboard.**

A gate's output is the drain of a transistor. To make that node high, the transistor must **physically move charge onto every input it drives and every millimetre of wire connecting them**. From [[how-computers-work/01-electricity/04-signals-and-time|module 4]], that takes time proportional to the capacitance being charged.

So a question the course has dodged: **how many inputs can one output drive?**

The answer is "as many as you like, but it gets slower with every one" — and past a point, unusably slow. **The fix is a component that computes nothing at all**, which sounds absurd until you see the numbers.

**This module also covers the three faults that kill real hardware** — floating inputs, bus contention and supply droop. Every one of them was named in the [[build-your-own-shit/17-your-own-cpu/04-breadboard|breadboard build track]] without explanation. Here is the explanation.

---

## 2. Terminology

| Term | Plain-English definition |
| :--- | :--- |
| **Buffer** | A gate whose output equals its input — it amplifies drive, not logic |
| **Fan-out** | How many gate inputs one output drives |
| **Fan-in** | How many inputs one gate has |
| **Drive strength** | How much current a gate output can source or sink |
| **Load capacitance** | Total capacitance an output must charge |
| **Tri-state** | An output that can be high, low, or **disconnected** |
| **Hi-Z** | High impedance — the disconnected state |
| **Bus** | A shared wire with several possible drivers |
| **Bus contention** | Two drivers enabled at once — a short circuit |
| **Floating input** | An input connected to nothing — picks up noise |
| **Pull-up / pull-down** | A resistor holding an otherwise-floating line at a defined level |
| **Open-drain** | An output that can pull low but never high |
| **Decoupling capacitor** | A local charge reservoir beside a chip's power pins |

---

## 3. Fan-out — the cost of every connection

Each gate input presents a small capacitance (its gate oxide, from [[how-computers-work/03-transistors/02-mosfet-physics|module 12]] — a MOSFET gate is literally a capacitor plate). Drive $n$ inputs and you must charge $n$ times that.

| Fan-out | Load | Delay |
| ---: | ---: | ---: |
| 1 | 2.0 fF | 5.6 ps |
| 2 | 4.0 fF | 11.2 ps |
| 4 | 8.0 fF | 22.4 ps |
| 8 | 16.0 fF | 44.8 ps |
| 16 | 32.0 fF | 89.6 ps |
| 32 | 64.0 fF | 179.2 ps |

**Delay grows linearly with fan-out**, because $\tau = RC$ and $C$ is proportional to the number of loads.

> [!NOTE]
> **Exceeding fan-out does not break a circuit — it slows it.** That is what makes it dangerous.
>
> A logic error announces itself. A fan-out violation produces a design that is *correct* and misses timing, and the symptom appears somewhere else entirely — a path that fails only at high temperature, or only on some chips. **Silent, distributed, load-dependent failure** is the worst kind to debug.
>
> This is why datasheets specify maximum fan-out, and why synthesis tools check it automatically.

---

## 4. The buffer — a gate that does nothing, usefully

**A buffer's output equals its input.** Logically it is the identity function: pointless.

**Electrically it is the whole point.** Recall from [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]] that a gate does not pass its input through — it *reads* which band the input is in and **generates a fresh output from the power supply.**

So a buffer:

- presents **one** input load to whatever drives it,
- and drives its own output with **full strength**, from the supply.

**It resets the load.** A weak signal driving one buffer, which drives sixteen inputs, is far faster than that signal driving sixteen inputs directly.

In CMOS a buffer is **two inverters in series** — the cheapest way to get non-inverting drive, since a single inverter would flip the logic.

### Buffer trees

For large fan-outs, chain them:

```
                    ┌─[BUF]─► 4 loads
                    │
   source ─[BUF]────┼─[BUF]─► 4 loads
                    │
                    ├─[BUF]─► 4 loads
                    │
                    └─[BUF]─► 4 loads
```

| Loads | Flat fan-out | Buffer tree | Buffers used | Speedup |
| ---: | ---: | ---: | ---: | ---: |
| 16 | 90 ps | 85 ps | 5 | 1.1× |
| 64 | 358 ps | 127 ps | 21 | 2.8× |
| 256 | 1434 ps | 170 ps | 85 | 8.5× |
| 1024 | 5734 ps | 212 ps | 341 | **27×** |

**Each buffer costs a gate delay but resets the load to one.** Trees turn $O(n)$ fan-out delay into $O(\log n)$ — **the same "sequential dependency into a logarithmic tree" move** as carry-lookahead ([[how-computers-work/05-combinational/02-adders|module 21]]) and carry-save multiplication ([[how-computers-work/05-combinational/03-multipliers-and-comparators|module 22]]). Fourth appearance; it really is the reusable idea in digital design.

**The clock is the extreme case.** A clock signal must reach every flip-flop on a chip — millions of them. That is a buffer tree with many levels, carefully balanced so every leaf arrives at nearly the same instant. Residual differences are **clock skew**, and it eats directly into the timing budget of [[how-computers-work/06-memory/01-latches-and-flip-flops|module 24]]'s setup/hold window.

---

## 5. Tri-state — the third output state

So far outputs have been 0 or 1. **A tri-state buffer adds a third: disconnected.**

```
              enable
                │
   in ──────[▷]─┴──── out
                
   enable = 1  ->  out = in        (drives normally)
   enable = 0  ->  out = Hi-Z      (electrically absent)
```

**Hi-Z is not a voltage.** It means the output transistors are *both off*, so the pin neither sources nor sinks current — module 3's divider row 3, where both resistances are infinite. The output is not 0, not 1, and not "in between": it has simply let go of the wire.

### Why this exists: shared buses

Many devices need to put data on **one** shared wire — a memory bus, a register file's read port, a backplane.

```
   ┌────────┐   ┌────────┐   ┌────────┐
   │ device │   │ device │   │ device │
   │   A    │   │   B    │   │   C    │
   └───┬────┘   └───┬────┘   └───┬────┘
      [▷]         [▷]         [▷]      <- tri-state buffers
       │           │           │
   ────┴───────────┴───────────┴────   the shared BUS
```

**Exactly one enable may be asserted:**

| Enabled drivers | Result |
| :--- | :--- |
| One | Bus carries that value ✓ |
| **Zero** | **Floating** — undefined, noise-sensitive |
| **Two or more** | **CONTENTION** — a short from supply to ground |

**Contention is a genuine short circuit.** One driver pulls high while another pulls low, and the only thing limiting current is the transistors' own resistance. They get hot. Sustained, they fail permanently.

> [!NOTE]
> **This is why a bus is driven by a decoder** ([[how-computers-work/05-combinational/01-multiplexers-and-decoders|module 20]]).
>
> A decoder's output is **one-hot by construction** — exactly one line high, always. Wire the enables from a decoder and contention becomes structurally impossible, in the same way the PDN/PUN duality made shorts impossible inside a gate ([[how-computers-work/04-logic/01-gates-from-transistors|module 15]]).
>
> **Correctness by topology rather than by discipline** — the recurring good idea in this course.

### Multiplexer or bus?

Both let many sources feed one destination, and they trade off cleanly:

| | Multiplexer | Tri-state bus |
| :--- | :--- | :--- |
| Wiring | Every source runs to the MUX | One shared wire |
| Sources | Fixed at design time | Devices can be added |
| Failure mode | None — it always outputs something | Contention, floating |
| Used in | On-chip datapaths | Board-level and legacy buses |

**Modern chips overwhelmingly prefer multiplexers**, because on-chip wires are cheap and contention bugs are expensive. Tri-state buses persist off-chip, where running a separate wire per device is not an option.

---

## 6. The three faults that kill real hardware

Everything above is on-chip theory. **These three are why breadboards fail**, and they are the practical electrical layer the build tracks assumed.

### Floating inputs

**A CMOS input connected to nothing is not 0.** It is a capacitor with no driver, picking up charge from nearby signals and from the air. It drifts into the forbidden zone of [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]], where the gate's behaviour is undefined — and often oscillates, since it sits in its high-gain transition region.

**Worse, it burns power.** In the transition region *both* the pull-up and pull-down networks partly conduct, so the gate draws continuous current — the short-circuit current of [[how-computers-work/03-transistors/03-cmos|module 13]], now permanent rather than momentary.

**The fix: tie every unused input to VCC or GND.** Never leave one floating. This includes unused gates in a package you are only half using.

**A pull-up or pull-down resistor** does the same job for a line that is sometimes driven and sometimes not — a bus, or a button. It weakly holds a defined level, and any real driver easily overrides it.

**Open-drain** outputs rely on this: they can pull low but never high, so a shared pull-up resistor provides the high level. Several devices can share the line and any one can pull it low without contention — which is exactly how I²C works, and why it needs pull-up resistors on the board.

### Bus contention

Covered above. **Check enable logic before powering on**, and prefer a decoder over hand-wired enables.

### Supply droop, and why decoupling capacitors exist

When a chip switches, it draws a current spike. That current flows through the **inductance** of the package pins and PCB traces, and inductance opposes current change:

$$V = L\frac{di}{dt}$$

| Switching current | Inductance | Rise time | Droop |
| ---: | ---: | ---: | ---: |
| 50 mA | 5 nH | 1.0 ns | 250 mV |
| 500 mA | 5 nH | 1.0 ns | 2500 mV |
| 500 mA | 5 nH | 0.1 ns | 25000 mV |
| 2000 mA | 1 nH | 0.1 ns | 20000 mV |

**Compare with module 5's 400 mV noise margin.** Even the first row eats most of it. The others are catastrophic.

**A chip with a poor supply corrupts itself** — its own switching drags $V_{DD}$ down until its outputs no longer meet $V_{OH}$, and the digital abstraction fails from the inside.

**A decoupling capacitor is a local charge reservoir**, placed as close to the power pins as physically possible. It supplies the fast current spike without that current having to travel through the inductance of the supply path. The capacitor recharges slowly between spikes.

**0.1 µF ceramic across every chip's power pins, right at the chip.** This is not a superstition, and it is the single most common reason a breadboard circuit "works sometimes".

---

## 7. Predict before reading on

A signal must reach 256 gate inputs. A colleague suggests using one very large transistor — 256× the normal width — instead of a buffer tree.

**Does that work?**

<details><summary>Check your answer</summary>

**It moves the problem rather than solving it.**

A 256× wider transistor does have $1/256$ the on-resistance, so it charges the load fast. But from [[how-computers-work/03-transistors/02-mosfet-physics|module 12]], **a wider transistor also has proportionally more gate capacitance** — so it presents a 256× load to whatever drives *it*.

You have moved the fan-out problem one stage back, and made it worse: the previous gate now drives one enormous load instead of the original signal driving 256 small ones.

**The buffer tree wins because each stage only has to be moderately stronger than the last.** The optimal ratio between successive stages is about $e \approx 2.7$ (in practice 3–4 is used), which is why the lab's tree branches by 4.

This is the classic **logical effort** result in VLSI design, and it is the reason chips are full of graduated buffer chains rather than single huge drivers.
</details>

---

## 8. Worked example — runnable

Save as `buffer_lab.py` and run `python3 buffer_lab.py`.

```python
"""Driving real wires: fan-out, buffer trees, tri-state buses, decoupling."""
import math

GATE_DELAY_PS = 20
C_INPUT_FF    = 2.0      # one gate input presents ~2 fF of load
C_WIRE_FF_MM  = 200.0    # a 1 mm on-chip wire is ~200 fF
R_DRIVE_OHM   = 4000.0   # a minimum-size gate's on-resistance (module 12)

def load_capacitance_ff(fan_out, wire_mm=0.0):
    """Total capacitance a gate must charge: every input it drives, plus wire."""
    return fan_out * C_INPUT_FF + wire_mm * C_WIRE_FF_MM

def delay_ps(fan_out, wire_mm=0.0, drive_strength=1.0):
    """tau = R*C. A wider transistor lowers R proportionally (module 12)."""
    c = load_capacitance_ff(fan_out, wire_mm) * 1e-15
    r = R_DRIVE_OHM / drive_strength
    return r * c * 1e12 * 0.7        # 0.7*RC ~ the 50% propagation point

def buffer_tree(total_loads, branching=4):
    """Drive N loads through a tree of buffers instead of one huge fan-out.

    Returns (levels, total_buffers, delay_ps)."""
    if total_loads <= branching:
        return 0, 0, delay_ps(total_loads)
    levels = math.ceil(math.log(total_loads, branching))
    buffers, remaining = 0, total_loads
    for _ in range(levels):
        remaining = math.ceil(remaining / branching)
        buffers += remaining
    # each level drives `branching` loads, plus one gate delay per level
    d = levels * (delay_ps(branching) + GATE_DELAY_PS)
    return levels, buffers, d

def bus_state(drivers):
    """A shared bus. `drivers` is a list of (enabled, value).

    Exactly one driver may be enabled. Zero = floating (undefined),
    two or more = CONTENTION, a short from supply to ground."""
    active = [(en, v) for en, v in drivers if en]
    if len(active) == 0:
        return None, "FLOATING (Hi-Z) -- no driver, value undefined"
    if len(active) > 1:
        return None, f"CONTENTION -- {len(active)} drivers fighting, SHORT CIRCUIT"
    return active[0][1], "ok"

def decoupling_droop_mv(switching_current_a, inductance_nh, rise_time_ns):
    """Supply droop from switching current through package inductance: V = L di/dt.

    This is why every chip needs a decoupling capacitor."""
    di_dt = switching_current_a / (rise_time_ns * 1e-9)
    return inductance_nh * 1e-9 * di_dt * 1000

if __name__ == "__main__":
    print("FAN-OUT -- every input you drive is capacitance you must charge")
    print(f"  {'fan-out':>8s} {'load (fF)':>11s} {'delay (ps)':>12s}")
    for fo in (1, 2, 4, 8, 16, 32):
        print(f"  {fo:8d} {load_capacitance_ff(fo):11.1f} {delay_ps(fo):12.1f}")
    print("  -> delay grows LINEARLY with fan-out. This is why a gate has a")
    print("     specified maximum fan-out, and why exceeding it silently")
    print("     slows a circuit rather than breaking it.")
    print()

    print("A BUFFER fixes it by re-driving the signal from the supply")
    print(f"  {'loads':>7s} {'flat fan-out':>14s} {'buffer tree':>14s} {'buffers':>9s}"
          f" {'speedup':>9s}")
    for loads in (16, 64, 256, 1024):
        flat = delay_ps(loads)
        levels, bufs, tree = buffer_tree(loads)
        print(f"  {loads:7d} {flat:11.0f} ps {tree:11.0f} ps {bufs:9d}"
              f" {flat/tree:8.1f}x")
    print("  -> a buffer adds a gate delay but resets the load to 1.")
    print("     Trees turn O(n) fan-out delay into O(log n).")
    print()

    print("TRI-STATE BUSES -- the third output state")
    scenarios = [
        ([(1, 0xAA), (0, 0x55), (0, 0xFF)], "one driver enabled"),
        ([(0, 0xAA), (0, 0x55), (0, 0xFF)], "no driver enabled"),
        ([(1, 0xAA), (1, 0x55), (0, 0xFF)], "TWO drivers enabled"),
    ]
    for drivers, label in scenarios:
        value, status = bus_state(drivers)
        shown = f"{value:#04x}" if value is not None else "----"
        print(f"  {label:22s} -> bus = {shown}   {status}")
    print("  -> this is why a bus needs a DECODER on its enables (module 20):")
    print("     one-hot guarantees exactly one driver, by construction.")
    print()

    print("DECOUPLING -- why every chip needs a capacitor beside it")
    print("  supply droop from V = L(di/dt) through package inductance:")
    print(f"  {'current':>9s} {'L (nH)':>8s} {'rise (ns)':>11s} {'droop (mV)':>12s}")
    for i, l, t in [(0.05, 5.0, 1.0), (0.5, 5.0, 1.0), (0.5, 5.0, 0.1), (2.0, 1.0, 0.1)]:
        print(f"  {i*1000:7.0f}mA {l:8.1f} {t:11.2f} {decoupling_droop_mv(i,l,t):12.0f}")
    print("  compare with the 400 mV noise margin of module 5:")
    print("  -> without decoupling, a chip's own switching current can drag")
    print("     its supply below the level its inputs need. It corrupts ITSELF.")

    assert delay_ps(16) > delay_ps(1)
    assert buffer_tree(1024)[2] < delay_ps(1024)
    assert bus_state([(1, 5), (1, 9)])[0] is None
    assert bus_state([(0, 5)])[0] is None
    assert bus_state([(1, 7), (0, 9)])[0] == 7
    assert decoupling_droop_mv(0.5, 5.0, 0.1) > 400     # exceeds the noise margin
    print()
    print("buffer_lab: passed")
```

Expected output:

```
FAN-OUT -- every input you drive is capacitance you must charge
   fan-out   load (fF)   delay (ps)
         1         2.0          5.6
         2         4.0         11.2
         4         8.0         22.4
         8        16.0         44.8
        16        32.0         89.6
        32        64.0        179.2
  -> delay grows LINEARLY with fan-out. This is why a gate has a
     specified maximum fan-out, and why exceeding it silently
     slows a circuit rather than breaking it.

A BUFFER fixes it by re-driving the signal from the supply
    loads   flat fan-out    buffer tree   buffers   speedup
       16          90 ps          85 ps         5      1.1x
       64         358 ps         127 ps        21      2.8x
      256        1434 ps         170 ps        85      8.5x
     1024        5734 ps         212 ps       341     27.0x
  -> a buffer adds a gate delay but resets the load to 1.
     Trees turn O(n) fan-out delay into O(log n).

TRI-STATE BUSES -- the third output state
  one driver enabled     -> bus = 0xaa   ok
  no driver enabled      -> bus = ----   FLOATING (Hi-Z) -- no driver, value undefined
  TWO drivers enabled    -> bus = ----   CONTENTION -- 2 drivers fighting, SHORT CIRCUIT
  -> this is why a bus needs a DECODER on its enables (module 20):
     one-hot guarantees exactly one driver, by construction.

DECOUPLING -- why every chip needs a capacitor beside it
  supply droop from V = L(di/dt) through package inductance:
    current   L (nH)   rise (ns)   droop (mV)
       50mA      5.0        1.00          250
      500mA      5.0        1.00         2500
      500mA      5.0        0.10        25000
     2000mA      1.0        0.10        20000
  compare with the 400 mV noise margin of module 5:
  -> without decoupling, a chip's own switching current can drag
     its supply below the level its inputs need. It corrupts ITSELF.

buffer_lab: passed
```

---

## 9. Common pitfalls and traps

1. **Thinking a buffer is useless because it computes the identity.** Its job is electrical, not logical: it re-drives the signal from the supply.
2. **Leaving inputs floating.** Not 0, not 1 — undefined, noisy, and it burns power continuously.
3. **Enabling two bus drivers.** A real short. Use a decoder so it cannot happen.
4. **Assuming Hi-Z is a logic level.** It is the *absence* of a level. Something else must define the line, or nothing does.
5. **Omitting decoupling capacitors.** The commonest cause of "works sometimes" hardware.
6. **Fixing fan-out with one huge transistor.** It relocates the load to the previous stage.
7. **Forgetting the clock is a signal too.** It has the largest fan-out on the chip and needs the most careful buffering.

---

## 10. Check your understanding

1. **Why does exceeding fan-out cause harder bugs than a logic error?**
   <details><summary>Answer</summary>
   A logic error is deterministic and reproducible — the circuit does the wrong thing, always. A fan-out violation leaves the circuit <em>logically correct</em> and merely slow, so it only fails when that path's delay exceeds the clock period.<br>
   That depends on temperature, supply voltage and manufacturing variation, so it may fail on one chip and not another, or only when warm. <strong>Silent, intermittent and load-dependent</strong> is the worst combination to debug, which is why tools check fan-out automatically rather than leaving it to review.
   </details>

2. **An I²C bus has two pull-up resistors and no tri-state drivers. How does it avoid contention?**
   <details><summary>Answer</summary>
   I²C devices use <strong>open-drain</strong> outputs: they can pull the line low but can never drive it high. The pull-up resistor provides the high level whenever nobody is pulling down.<br>
   If two devices pull low simultaneously, nothing bad happens — they agree. If one pulls low while another does not, the line goes low, which is the wired-AND behaviour the protocol's arbitration depends on. <strong>Contention is impossible by construction</strong> because no device can ever drive high. The cost is speed: the pull-up resistor charges the line slowly, which is why I²C is far slower than a push-pull bus.
   </details>

3. **Why does a 0.1 µF capacitor beside a chip help, when the power supply already has a much larger capacitor?**
   <details><summary>Answer</summary>
   Because of <strong>inductance and distance</strong>. The bulk capacitor is centimetres away, and the current spike would have to travel through the inductance of that path — which is exactly what causes the droop ($V = L\,di/dt$).<br>
   A local ceramic capacitor sits millimetres from the pins, so its path has very little inductance and it can supply the fast transient. The bulk capacitor then recharges it slowly. <strong>They serve different frequencies</strong>: bulk for slow average demand, local ceramic for nanosecond spikes. This is why real boards have both, and why decoupling capacitors must be placed <em>at</em> the chip rather than "somewhere on the rail".
   </details>

4. **Why do on-chip designs prefer multiplexers while board-level designs still use tri-state buses?**
   <details><summary>Answer</summary>
   On-chip, wires are cheap and plentiful — running a separate wire from every source to a MUX costs little, and a MUX has no failure mode: it always outputs exactly one selected value, with no contention or floating states possible.<br>
   At board level, every wire is a physical trace and a connector pin. Running $n$ separate buses to accommodate $n$ devices is impractical, and you may not know at design time how many devices will be attached. <strong>A shared bus trades safety for wiring economy</strong>, and that trade only makes sense when wires are expensive.
   </details>

---

## 11. Practice — independent task

**Task:** You are designing the clock distribution and a shared bus for a small board.

- **(a)** A clock must reach 64 flip-flops. Compute the delay with a flat fan-out, then design a buffer tree with branching factor 4. How many buffers, how many levels, and what is the delay?
- **(b)** Repeat with branching factors 2, 3, 4 and 8. Which minimises delay? Explain why very small and very large branching factors are both bad.
- **(c)** Clock skew is the *difference* in arrival time between leaves. If one branch has 3 buffers and another has 4, what is the skew? How does that eat into the setup/hold budget of [[how-computers-work/06-memory/01-latches-and-flip-flops|module 24]]?
- **(d)** Four devices share an 8-bit bus. Design the enable logic using a decoder so contention is impossible. What happens when the "select" input is a value with no device attached?
- **(e)** Add a pull-down resistor network so the bus reads as 0x00 rather than floating when no device is enabled. What does that cost in power and speed?
- **(f)** Each device draws 200 mA when switching, with a 2 ns rise time, through 4 nH of package inductance. Compute the supply droop. Does it exceed a 400 mV noise margin?
- **(g)** Extend `buffer_lab.py` with `clock_tree_skew(leaves, branching)` returning delay and worst-case skew, and verify your answers to (a)–(c).

**Done when:** you have an optimal branching factor with a reason, a contention-proof enable scheme, and a droop figure you can compare against the noise margin.

<details><summary>Hint for (b), only if stuck</summary>
Small branching (2) means many levels, and each level costs a full gate delay — so total delay grows with $\log_2 n$ levels. Large branching (8) means few levels but each buffer drives a heavy load, so each level is slow.<br>
The optimum balances the two, and lands near a branching factor of <strong>3 to 4</strong> — the same $e \approx 2.7$ result as the logical-effort answer in section 7. Deriving that ratio yourself is the point of the exercise.
</details>

---

## 12. Tradeoffs and limits

- **The delay model is first-order.** Real timing depends on input slew, wire RC and the specific cell library. The scaling is right; the absolute picoseconds are not.
- **Logical effort is the proper theory.** This module's rule of thumb ("branch by ~4") comes from Sutherland and Sproull's logical-effort method, which gives the optimal sizing analytically.
- **Tri-state is increasingly rare on-chip.** Modern designs avoid it because contention is hard to verify and Hi-Z is hard to simulate reliably. Multiplexers dominate.
- **Signal integrity is a discipline of its own.** At high frequency, wires behave as transmission lines with reflections, crosstalk and ground bounce. Everything here assumes signals are slow enough to ignore that — true on a breadboard at 1 MHz, false on a motherboard at 1 GHz.

---

## Before moving on

**This is the end of Part V.** You are ready for Part VI when you can, closed-book:

- [ ] Explain why a buffer is worth building despite computing the identity.
- [ ] Calculate fan-out delay and design a buffer tree.
- [ ] Explain Hi-Z, and why exactly one bus driver may be enabled.
- [ ] Explain floating inputs and why they burn power.
- [ ] Explain supply droop and why decoupling capacitors go *at* the chip.

**Recap:** A gate output must physically charge every input and wire it drives, so delay grows linearly with fan-out. A buffer computes nothing but re-drives the signal from the supply, resetting the load — and buffer trees turn $O(n)$ fan-out delay into $O(\log n)$, with an optimal branching factor near 4. Tri-state outputs add a disconnected state so several devices can share a bus, with a decoder guaranteeing exactly one driver. Floating inputs are undefined and burn power; bus contention is a short; and switching current through package inductance causes supply droop that a local decoupling capacitor exists to absorb.

**Next:** [[how-computers-work/05-combinational/01-multiplexers-and-decoders|Module 20 — Multiplexers and Decoders]] begins Part VI, and its decoder is what makes bus enables safe.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/01-electricity/05-the-digital-abstraction|Module 5]] — the noise margin droop threatens
- [[how-computers-work/05-combinational/01-multiplexers-and-decoders|Module 20]] — decoders as contention-proof enables
- [[build-your-own-shit/17-your-own-cpu/04-breadboard|PRIME-1 breadboard track]] — where these three faults actually bite
- [[hardware/index|hardware/]] — practical electronics and components
