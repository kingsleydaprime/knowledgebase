# Module 24: Latches and Flip-Flops (Feedback Becomes Memory)

**[Intermediate → Advanced]** — Part VII begins with the conceptual leap of the whole course. **Every circuit built so far forgets everything the instant its inputs change.** One wire changes that.

## Before you start

- You can build gates from CMOS networks — [[how-computers-work/04-logic/01-gates-from-transistors|module 15]].
- You know gates have propagation delay and signals take time to settle — [[how-computers-work/01-electricity/04-signals-and-time|module 4]].
- You remember the forbidden zone and what happens to a gate held inside it — [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]].

**After this lesson you will be able to:**

1. Explain how cross-coupled gates create two stable states, and why that is memory.
2. Trace an SR latch settling, and explain the forbidden state and the race it causes.
3. Distinguish a level-sensitive latch from an edge-triggered flip-flop, and say why synchronous design needs the second.
4. Explain setup and hold times, metastability, and why it can only be made improbable — never eliminated.

**Study route:** section 3 is the leap. Section 7 (metastability) cashes a promise made back in module 5 and is the most important practical content in Part VII.

---

## 1. Why this exists (real-world motivation)

Stop and notice something about everything built in Parts V and VI.

An adder given `5` and `3` outputs `8`. Change the inputs to `2` and `2`, and the output becomes `4` — **and the 8 is gone.** Not stored anywhere, not recoverable. The circuit has no past.

**This is what "combinational" means: output is a pure function of the current inputs.** The ALU, the multiplexers, the decoders, the multiplier — every one of them is a function evaluated continuously, with no history.

**A computer cannot work this way.** A program is a *sequence*. It needs to hold a value from one step to the next, remember where it is in the instruction stream, accumulate a running total. Without memory there is arithmetic but no computation in any useful sense.

So the question is stark: **you have only gates, and gates have no memory. How do you build memory out of components that have none?**

The answer is one wire, connected in a way that has been quietly forbidden until now.

---

## 2. Terminology

| Term | Plain-English definition |
| :--- | :--- |
| **Combinational** | Output depends only on current inputs |
| **Sequential** | Output depends on inputs *and* stored state |
| **Feedback** | An output routed back to become an input |
| **Bistable** | Having exactly two stable states |
| **Latch** | Level-sensitive storage — transparent while enabled |
| **Flip-flop** | Edge-triggered storage — samples only at a clock edge |
| **Transparent** | Output following input directly, right now |
| **Setup time** | How long data must be steady *before* the clock edge |
| **Hold time** | How long data must stay steady *after* the clock edge |
| **Metastability** | A storage element stuck between 0 and 1 |
| **Synchroniser** | Two flip-flops in series, used to accept asynchronous inputs |
| **MTBF** | Mean time between failures |

---

## 3. The leap: cross-coupled gates

Take two NOR gates. **Connect each one's output to the other's input.**

```
        S ─────┐
               │  ┌──────┐
               └──┤ NOR  ├──┬──── Q_bar
            ┌─────┤      │  │
            │     └──────┘  │
            │               │
            │     ┌──────┐  │
            └─────┤ NOR  ├──┴──── Q
        R ────────┤      │
                  └──────┘

        Q     = NOR(R, Q_bar)
        Q_bar = NOR(S, Q)
```

**Look at what is strange here.** Each gate's output is the other's input, so neither can be evaluated first. There is no "the input" and "the output" — the circuit's state is whatever the pair settles into.

**And it settles into one of exactly two configurations:**

| State | Q | Q_bar | Check |
| :--- | :-: | :-: | :--- |
| A | 1 | 0 | $Q = \text{NOR}(0,0) = 1$ ✓, $\overline{Q} = \text{NOR}(0,1) = 0$ ✓ |
| B | 0 | 1 | $Q = \text{NOR}(0,1) = 0$ ✓, $\overline{Q} = \text{NOR}(0,0) = 1$ ✓ |

**Both are self-consistent.** In state A, the 1 on Q holds Q_bar at 0, and the 0 on Q_bar holds Q at 1. **Each output is the reason the other stays where it is.** Remove all external input and the pair sits there indefinitely.

> [!NOTE]
> **That is memory, and it deserves a moment.**
>
> Nothing is "stored" in the sense of being written down. There is no substance holding a value. **The state persists because it is self-reinforcing** — a loop of causation with two solutions, and the circuit is sitting in one of them.
>
> The bit is not *in* a gate. It is in the **relationship** between two gates. Cut the feedback wire and the bit does not leak out; it simply stops existing.
>
> This is why memory needs power. The state is a continuously maintained equilibrium, not a stored object. Remove the supply and there is nothing to maintain it — which is exactly why SRAM is volatile in [[how-computers-work/06-memory/03-memory-technology|module 26]].

### Writing to it

$S$ (set) and $R$ (reset) let you force a state:

- **$S=1, R=0$** → forces Q to 1. Trace: `(0,1) → (0,0) → (1,0)`, settling in **2 gate delays**.
- **$S=0, R=0$** → **hold.** Neither gate is forced, so the loop keeps whatever it had. **This is the memory state.**
- **$S=0, R=1$** → forces Q to 0.

The settling traces in the lab are worth reading: the circuit visibly passes through an intermediate configuration before locking into the new stable state.

---

## 4. The forbidden state

**$S = 1, R = 1$ breaks it.** Both gates are forced low, so $Q = 0$ *and* $\overline{Q} = 0$ — which contradicts the whole point of naming the second output "Q-bar".

That alone is merely useless. **The real danger is what happens when you release it.**

From $(0,0)$, dropping both inputs to 0 leaves both gates seeing the same inputs and trying to drive each other high simultaneously. The lab shows this **oscillating** — never settling within 20 iterations.

**In real hardware it does settle, and which state it lands in depends on which gate happens to be a few picoseconds faster.** That is a **race condition**: the outcome is decided by manufacturing variation and temperature, not by the design. Two identical chips can differ; the same chip can differ between runs.

**This is why SR latches are almost never used directly.** The fix is to make the forbidden input unreachable by construction — which is the D latch.

---

## 5. The D latch — one input, no forbidden state

Feed a single input $D$ to $S$, and $\overline{D}$ to $R$, gated by an **enable**:

```
        D ──┬──[AND]──── S
            │     ▲
            │   enable
            │     ▼
            └─[NOT]─[AND]──── R
```

Now $S$ and $R$ can never both be 1 — they are complements. **The forbidden state is structurally impossible.**

- **Enable = 1:** the latch is **transparent** — Q follows D continuously.
- **Enable = 0:** the latch **holds** its last value.

**But transparency is itself a problem.** While enabled, changes at D flow straight through to Q. If Q feeds back into logic that eventually reaches D, the value can race around the loop several times within one enable pulse. You cannot reason about "one step" of a computation.

---

## 6. The flip-flop — sampling an instant

**What you want is storage that captures its input at a single moment**, not over an interval.

The standard construction is **master–slave**: two latches in series, driven by *opposite* clock phases.

```
          ┌─────────┐        ┌─────────┐
   D ────►│ MASTER  │───────►│  SLAVE  │────► Q
          │ latch   │        │ latch   │
          └────▲────┘        └────▲────┘
               │                  │
            clock'              clock
        (open when LOW)     (open when HIGH)
```

**At no point are both open.** While the clock is low the master tracks D and the slave holds; on the rising edge the master freezes and the slave takes its value. **Data advances exactly one stage per clock edge**, and the value that lands is whatever D was at the instant of the edge.

The lab's trace makes the difference visible:

| Time | Clock | D | Latch Q | Flip-flop Q |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 1 | 1 | 1 | 1 ← rising edge |
| 3 | 1 | 0 | **0** | **1** |
| 4 | 0 | 0 | 0 | 1 |

**At time 3 the latch follows D down to 0; the flip-flop holds the 1 it captured at the edge.** That difference is what makes synchronous design tractable: between edges, every flip-flop's output is stable, so combinational logic has a whole clock period to settle before anything is captured.

> [!NOTE]
> **This is why a computer needs a clock**, and the answer is not "to make it go fast".
>
> Signals travel different paths with different delays ([[how-computers-work/01-electricity/04-signals-and-time|module 4]]). Without a shared reference there is no moment at which you can say "all values are now valid".
>
> **The clock defines that moment.** Its period is chosen so the slowest path — the critical path — has definitely settled. At each edge, every flip-flop captures simultaneously, and the whole machine advances one well-defined step.
>
> **A clock does not make a computer fast. It makes it *correct*** by turning a mess of continuously varying voltages into a sequence of discrete, agreed-upon states — the same kind of bargain as module 5, this time in the time dimension rather than the voltage dimension.

---

## 7. Setup, hold, and metastability

Here is where module 5's forbidden zone returns to collect.

A flip-flop needs D **stable for a window around the clock edge**:

```
                     clock edge
                          │
        ──────────────────┼──────────────────
              setup       │      hold
            ◄─────────────┼─────────►
                          │
        D must not change anywhere in this window
```

- **Setup time** — D steady *before* the edge, so the master has settled.
- **Hold time** — D steady *after* the edge, so the capture completes.

**Violate the window and the flip-flop may enter a metastable state**: its internal feedback loop balanced between the two stable states, output sitting somewhere in the forbidden zone, neither 0 nor 1.

**It is a ball balanced exactly on a ridge.** It will fall — but *when* is unbounded.

### You cannot design this away

**MTBF for a metastable failure:**

$$\text{MTBF} = \frac{e^{t/\tau}}{T_0 \cdot f_{clock} \cdot f_{data}}$$

With $\tau = 20$ ps, $T_0 = 10$ ps, a 100 MHz clock and 1 MHz data:

| Settling time allowed | MTBF |
| ---: | ---: |
| 100 ps | 0.15 seconds |
| 200 ps | 22 seconds |
| 300 ps | ~55 minutes |
| 500 ps | 2.3 years |
| 1000 ps | $1.6 \times 10^{11}$ years |

**Read the first row. A design allowing only 100 ps of settling fails, on average, every 150 milliseconds.**

But look at the trend: **every extra 20 ps multiplies MTBF by $e$.** Going from 100 ps to 1 ns takes you from "several times a second" to "far longer than the age of the universe."

> [!NOTE]
> **Metastability is never eliminated. It is made improbable.**
>
> That is an uncomfortable but genuine engineering position, and it is the honest answer to "is digital logic reliable?" The MTBF is never infinite — there is always a nonzero probability that a flip-flop stays balanced past the deadline.
>
> **The standard defence is a synchroniser: two flip-flops in series.** If the first goes metastable, it has a full clock period to resolve before the second samples it. That single change moves $t$ from a fraction of a cycle to a whole cycle, which — because the relationship is exponential — buys many orders of magnitude.
>
> This applies whenever a signal crosses from one clock domain to another, or comes from outside the chip entirely: a button press, a network packet, another chip's clock. **Anything asynchronous must be synchronised**, and forgetting to do so produces the worst class of bug there is — rare, non-reproducible, and temperature-dependent.

---

## 8. Predict before reading on

A synchroniser uses two flip-flops in series. Someone proposes three, "to be safer".

**How much does the third one buy, and what does it cost?**

<details><summary>Check your answer</summary>

**It buys another full clock period of settling time — which multiplies MTBF by $e^{T/\tau}$.** At a 100 MHz clock (10 ns period) and $\tau = 20$ ps, that is $e^{500}$: a number so large the improvement is meaningless. Two flip-flops already give MTBF far beyond any product's lifetime.

**It costs one more cycle of latency** on every signal crossing the boundary.

**So the third flip-flop is usually pointless** — at low clock speeds. It becomes genuinely useful when the clock period is short relative to $\tau$: at multi-GHz, one period may not provide enough settling time, and three-stage synchronisers appear in real high-speed designs.

**The general lesson is worth keeping:** when a relationship is exponential, the first fix buys nearly everything and further fixes buy nearly nothing. Knowing where you are on that curve is the difference between engineering and superstition.
</details>

---

## 9. Worked example — runnable

The SR latch here is simulated by **iterating the feedback until it stops changing** — which is exactly what the physical gates do, at the speed of their propagation delay.

Save as `latch_lab.py` and run `python3 latch_lab.py`.

```python
"""Feedback turns combinational logic into memory -- and never quite safely."""
import math

def NOR(a, b):
    return 1 - (a | b)

def sr_latch_settle(s, r, q=0, q_bar=1, max_iterations=20):
    """Simulate cross-coupled NOR gates by iterating until nothing changes.

    Q     = NOR(R, Q_bar)
    Q_bar = NOR(S, Q)

    The feedback means the outputs are inputs. We iterate to find where
    the circuit settles -- which is exactly what the real gates do, at
    the speed of their propagation delay."""
    history = [(q, q_bar)]
    for i in range(max_iterations):
        new_q = NOR(r, q_bar)
        new_q_bar = NOR(s, q)
        if (new_q, new_q_bar) == (q, q_bar):
            return q, q_bar, history, True        # settled
        q, q_bar = new_q, new_q_bar
        history.append((q, q_bar))
    return q, q_bar, history, False               # never settled: oscillating

class DFlipFlop:
    """Edge-triggered, built as master-slave: two level-sensitive latches
    driven by opposite clock phases. Only the CLOCK EDGE moves data through."""
    def __init__(self):
        self.master = 0
        self.slave = 0
        self.prev_clock = 0

    def step(self, d, clock):
        if clock == 0:
            self.master = d                    # master follows D while clock low
        if self.prev_clock == 0 and clock == 1:
            self.slave = self.master           # rising edge: master -> slave
        self.prev_clock = clock
        return self.slave

class DLatch:
    """Level-sensitive: TRANSPARENT whenever the enable is high."""
    def __init__(self):
        self.q = 0

    def step(self, d, enable):
        if enable:
            self.q = d                          # follows input continuously
        return self.q

def metastability_mtbf(settling_time_s, tau_s, t0_s, clock_hz, data_hz):
    """Mean time between metastability failures.

    MTBF = exp(t/tau) / (T0 * f_clock * f_data)

    Note what this says: MTBF is never infinite. Metastability is not
    prevented, only made improbable."""
    return math.exp(settling_time_s / tau_s) / (t0_s * clock_hz * data_hz)

def human_time(seconds):
    for unit, size in [("years", 3.156e7), ("days", 86400),
                       ("hours", 3600), ("seconds", 1)]:
        if seconds >= size:
            return f"{seconds/size:.3g} {unit}"
    return f"{seconds:.3g} seconds"

if __name__ == "__main__":
    print("SR LATCH -- watch the feedback settle")
    print("  Q = NOR(R, Q_bar),  Q_bar = NOR(S, Q)")
    print()
    q, qb = 0, 1                      # start reset; the sequence carries state forward
    for s, r, label in [(1, 0, "SET"), (0, 0, "HOLD (from set)"),
                        (0, 1, "RESET"), (0, 0, "HOLD (from reset)")]:
        q, qb, hist, ok = sr_latch_settle(s, r, q, qb)
        path = " -> ".join(f"({a},{b})" for a, b in hist)
        print(f"  S={s} R={r}  {label:18s} {path}")
        print(f"      settled at Q={q}, Q_bar={qb}  after {len(hist)-1} gate delays")
    print()

    print("  THE HOLD STATE IS THE MEMORY: with S=R=0 the latch keeps whatever")
    print("  it had. Each gate's output is the other's input, so the pair")
    print("  reinforces itself with no external help.")
    print()

    print("THE FORBIDDEN STATE -- S=R=1:")
    q, qb, hist, ok = sr_latch_settle(1, 1, 0, 1)
    print(f"  settles to Q={q}, Q_bar={qb}  -- both LOW, so Q_bar is not NOT-Q")
    print(f"  the invariant Q = NOT(Q_bar) is broken")
    q, qb, hist, ok = sr_latch_settle(0, 0, 0, 0)
    print(f"  releasing both inputs from (0,0): settled={ok}, path length {len(hist)}")
    if not ok:
        print(f"  -> OSCILLATES. Which state it lands in depends on which gate")
        print(f"     is a fraction of a picosecond faster. This is a RACE.")
    print()

    print("LEVEL-SENSITIVE LATCH vs EDGE-TRIGGERED FLIP-FLOP")
    latch, ff = DLatch(), DFlipFlop()
    print(f"  {'time':>5s} {'clock':>6s} {'D':>3s} | {'latch Q':>8s} {'flip-flop Q':>12s}")
    signals = [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0), (0, 1), (1, 1)]
    for t, (clock, d) in enumerate(signals):
        lq = latch.step(d, clock)
        fq = ff.step(d, clock)
        note = ""
        if t > 0 and signals[t-1][0] == 0 and clock == 1:
            note = "  <- rising edge"
        print(f"  {t:5d} {clock:6d} {d:3d} | {lq:8d} {fq:12d}{note}")
    print()
    print("  the LATCH follows D whenever the clock is high (transparent).")
    print("  the FLIP-FLOP samples D only at the rising edge -- which is what")
    print("  makes a synchronous system predictable.")
    print()

    print("METASTABILITY -- the failure mode you cannot design away")
    print("  (asynchronous input sampled too close to the clock edge)")
    TAU, T0 = 20e-12, 10e-12
    CLK, DATA = 100e6, 1e6
    print(f"  tau={TAU*1e12:.0f}ps  T0={T0*1e12:.0f}ps  clock={CLK/1e6:.0f}MHz"
          f"  data={DATA/1e6:.0f}MHz")
    print(f"  {'settling time':>14s} {'MTBF':>18s}")
    for t_ps in (100, 200, 300, 500, 1000):
        mtbf = metastability_mtbf(t_ps * 1e-12, TAU, T0, CLK, DATA)
        print(f"  {t_ps:11d} ps {human_time(mtbf):>18s}")
    print()
    print("  every extra 20 ps of settling time multiplies MTBF by e (2.72x).")
    print("  this is why a SYNCHRONISER is two flip-flops in series: the first")
    print("  may go metastable, the second gets a whole clock period to settle.")

    assert sr_latch_settle(1, 0, 0, 1)[0] == 1
    assert sr_latch_settle(0, 1, 1, 0)[0] == 0
    assert sr_latch_settle(0, 0, 1, 0)[0] == 1        # holds a 1
    assert sr_latch_settle(0, 0, 0, 1)[0] == 0        # holds a 0
    assert not sr_latch_settle(0, 0, 0, 0)[3]         # (0,0) start oscillates
    assert metastability_mtbf(1e-9, TAU, T0, CLK, DATA) > \
           metastability_mtbf(1e-10, TAU, T0, CLK, DATA)
    print()
    print("latch_lab: passed")
```

Expected output:

```
SR LATCH -- watch the feedback settle
  Q = NOR(R, Q_bar),  Q_bar = NOR(S, Q)

  S=1 R=0  SET                (0,1) -> (0,0) -> (1,0)
      settled at Q=1, Q_bar=0  after 2 gate delays
  S=0 R=0  HOLD (from set)    (1,0)
      settled at Q=1, Q_bar=0  after 0 gate delays
  S=0 R=1  RESET              (1,0) -> (0,0) -> (0,1)
      settled at Q=0, Q_bar=1  after 2 gate delays
  S=0 R=0  HOLD (from reset)  (0,1)
      settled at Q=0, Q_bar=1  after 0 gate delays

  THE HOLD STATE IS THE MEMORY: with S=R=0 the latch keeps whatever
  it had. Each gate's output is the other's input, so the pair
  reinforces itself with no external help.

THE FORBIDDEN STATE -- S=R=1:
  settles to Q=0, Q_bar=0  -- both LOW, so Q_bar is not NOT-Q
  the invariant Q = NOT(Q_bar) is broken
  releasing both inputs from (0,0): settled=False, path length 21
  -> OSCILLATES. Which state it lands in depends on which gate
     is a fraction of a picosecond faster. This is a RACE.

LEVEL-SENSITIVE LATCH vs EDGE-TRIGGERED FLIP-FLOP
   time  clock   D |  latch Q  flip-flop Q
      0      0   0 |        0            0
      1      0   1 |        0            0
      2      1   1 |        1            1  <- rising edge
      3      1   0 |        0            1
      4      0   0 |        0            1
      5      0   1 |        0            1
      6      1   1 |        1            1  <- rising edge

  the LATCH follows D whenever the clock is high (transparent).
  the FLIP-FLOP samples D only at the rising edge -- which is what
  makes a synchronous system predictable.

METASTABILITY -- the failure mode you cannot design away
  (asynchronous input sampled too close to the clock edge)
  tau=20ps  T0=10ps  clock=100MHz  data=1MHz
   settling time               MTBF
          100 ps      0.148 seconds
          200 ps         22 seconds
          300 ps   3.27e+03 seconds
          500 ps         2.28 years
         1000 ps     1.64e+11 years

  every extra 20 ps of settling time multiplies MTBF by e (2.72x).
  this is why a SYNCHRONISER is two flip-flops in series: the first
  may go metastable, the second gets a whole clock period to settle.

latch_lab: passed
```

Note that `sr_latch_settle` contains **no stored variable representing the bit**. It iterates two NOR functions until they stop changing, and the bit is whatever fixed point they land on. That is not a simulation convenience — it is what the hardware literally does.

---

## 10. Common pitfalls and traps

1. **Thinking a latch "contains" a bit.** The bit is the equilibrium of a feedback loop. Cut the loop and it does not leak out — it ceases to exist.
2. **Confusing latches with flip-flops.** A latch is transparent while enabled; a flip-flop samples at an edge. Using a latch where a flip-flop belongs produces races that simulate fine and fail in silicon.
3. **Using an SR latch directly.** The $S=R=1$ state and its release race make it unsafe. Use a D latch or flip-flop.
4. **Ignoring setup and hold.** They are as much a specification as the logic function. A design that meets logic but violates timing is broken.
5. **Assuming metastability is a theoretical worry.** At 100 ps of margin it happens several times a second.
6. **Forgetting to synchronise asynchronous inputs.** Every button, external clock and cross-domain signal needs a synchroniser. Omitting one produces rare, unreproducible failures.

---

## 11. Check your understanding

1. **Why does the SR latch take two gate delays to change state, but zero to hold?**
   <details><summary>Answer</summary>
   Holding requires no change: the outputs already satisfy both gate equations, so the first iteration finds nothing to update.<br>
   Changing state means the new input must propagate through one gate, and <em>that</em> gate's new output must propagate through the second before the pair is consistent again — two gate delays. The lab's traces show exactly this: <code>(0,1) → (0,0) → (1,0)</code>.
   </details>

2. **A D latch is used where a flip-flop was needed, in a circuit whose output feeds back into its own input. What goes wrong?**
   <details><summary>Answer</summary>
   While the enable is high the latch is <strong>transparent</strong>, so the output can travel round the feedback path and back to the input <em>within the same enable pulse</em> — possibly several times.<br>
   Instead of advancing one step per clock, the circuit iterates an unpredictable number of times depending on gate delays. A counter might increment two or three times per tick, and the count would vary with temperature. A flip-flop makes exactly one advance per edge because master and slave are never open together.
   </details>

3. **Why does a synchroniser use two flip-flops rather than a slower clock?**
   <details><summary>Answer</summary>
   Both increase settling time, but a slower clock penalises the <em>entire design</em> while a synchroniser costs one cycle of latency on one signal.<br>
   Since MTBF grows exponentially with settling time, the second flip-flop's extra clock period buys an enormous improvement for a negligible price. Slowing the whole chip to fix one asynchronous input would be a catastrophic trade.
   </details>

4. **Metastability's MTBF is never infinite. How is it acceptable to ship products on that basis?**
   <details><summary>Answer</summary>
   Because "never fails" is not achievable for <em>any</em> physical system — cosmic-ray bit flips, electromigration and dielectric breakdown are all probabilistic too. Engineering targets a failure rate far below other causes and below the product's useful life.<br>
   A two-flip-flop synchroniser typically gives MTBF in the millions of years, so metastability is not remotely the limiting factor. <strong>The discipline is to compute the number rather than assume it</strong> — and the frightening part of the table is that a careless design gives 0.15 seconds, which is also a computed number.
   </details>

---

## 12. Practice — independent task

**Task:** Design and analyse a synchroniser for a button input on a 50 MHz system.

- **(a)** The button is a mechanical switch, asynchronous to your clock. Explain why sampling it directly with one flip-flop is unsafe, referring to setup/hold.
- **(b)** With $\tau = 25$ ps, $T_0 = 15$ ps, $f_{clock} = 50$ MHz and button events at 10 Hz, compute MTBF for a single flip-flop allowing 2 ns of settling.
- **(c)** Add a second flip-flop. The first now has a full clock period (20 ns) to settle. Recompute MTBF. Express both in human-readable units.
- **(d)** Mechanical switches also **bounce** — making and breaking contact many times over ~10 ms. A synchroniser does not fix this. Design a debouncer: describe the counter and threshold you would use, and state how many clock cycles 10 ms is.
- **(e)** Implement `debounce(samples, stable_cycles)` that returns the cleaned signal, and test it against a bouncy input sequence you construct.
- **(f)** Combine synchroniser and debouncer in the right order. Which comes first, and why does the other order fail?
- **(g)** Compute the total latency from physical press to a clean, synchronous signal, in cycles and in milliseconds. Is it noticeable to a human?

**Done when:** you have both MTBF figures, a working debouncer, and can justify the ordering of the two stages in one sentence.

<details><summary>Hint for (f), only if stuck</summary>
<strong>Synchroniser first.</strong> The debouncer is ordinary synchronous logic — counters and comparators built from flip-flops — and every one of those flip-flops has setup/hold requirements.<br>
Feeding a raw asynchronous signal into the debouncer means <em>each</em> of its flip-flops can go metastable independently, and they may disagree about what they saw. Synchronise first so the debouncer only ever sees a clean, clock-aligned signal. <strong>The rule is general: synchronise at the boundary, immediately, before any logic touches the signal.</strong>
</details>

---

## 13. Tradeoffs and limits

- **Real latches are not two NOR gates.** A CMOS D latch is usually transmission gates plus inverters — fewer transistors and faster. The bistable-feedback principle is identical.
- **Flip-flops are expensive.** A master–slave D flip-flop is roughly 20–24 transistors versus a NAND's 4. This is why designs minimise state, and why register files are a significant fraction of a core's area.
- **The MTBF model is a first-order approximation.** $\tau$ and $T_0$ are measured per process and vary with voltage and temperature. Vendors publish them; do not guess.
- **Clock distribution is its own discipline.** Getting the edge to millions of flip-flops simultaneously requires balanced clock trees, and residual **clock skew** eats into the timing budget.

---

## Before moving on

- [ ] Explain how cross-coupled gates produce two stable states, and why that is memory.
- [ ] Trace an SR latch settling, and explain the forbidden state and its release race.
- [ ] Distinguish transparent from edge-triggered, and say why feedback circuits need the latter.
- [ ] Explain setup and hold, and what metastability is physically.
- [ ] Compute MTBF and explain why a two-stage synchroniser is sufficient.

**Recap:** Cross-coupling two NOR gates creates a loop with two self-consistent solutions — the bit is the equilibrium, not a stored object, which is why memory needs power. S and R force a state; $S=R=1$ is forbidden because releasing it causes a race decided by gate delays. A D latch removes that state but is transparent while enabled, so synchronous designs use edge-triggered flip-flops built master–slave. Data near the clock edge can leave a flip-flop metastable; MTBF grows exponentially with settling time, so a two-flip-flop synchroniser makes the failure vanishingly improbable without ever making it impossible.

**Next:** [[how-computers-work/06-memory/02-registers-and-counters|Module 25 — Registers and Counters]] scales one bit to a word, and builds the program counter — the register that makes a machine step through instructions rather than compute one value.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/01-electricity/05-the-digital-abstraction|Module 5]] — the forbidden zone metastability lives in
- [[how-computers-work/01-electricity/04-signals-and-time|Module 4]] — propagation delay and the clock period
- [[how-computers-work/06-memory/03-memory-technology|Module 26]] — why this feedback pair makes SRAM volatile
- [[foundations/computer-architecture/05-the-datapath|computer-architecture/the datapath]] — flip-flops as pipeline registers
