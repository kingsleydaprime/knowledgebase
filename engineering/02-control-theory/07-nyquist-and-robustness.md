# Nyquist and Robustness

**[Advanced]** — The stability criterion that handles unstable and delayed plants, why margins can lie, and the fundamental limits nobody can design around.

## Why Nyquist

Bode margins are convenient and they have a blind spot: **they assume the open-loop system is stable and the phase crosses −180° once.**

For an unstable plant, a plant with multiple crossings, or one with significant delay, reading margins off a Bode plot can give you a confidently wrong answer. Nyquist handles all of it, because it's a genuine theorem rather than a rule of thumb.

## The criterion

Plot $L(j\omega)$ in the complex plane as $\omega$ runs from $-\infty$ to $+\infty$. That's the **Nyquist plot** — magnitude and phase on one diagram instead of two.

$$\boxed{N = Z - P}$$

- **$P$** — open-loop poles in the RHP (how many unstable modes the plant already has)
- **$N$** — clockwise encirclements of the point $-1$
- **$Z$** — closed-loop poles in the RHP

**You need $Z = 0$**, so:

> **The closed loop is stable iff the Nyquist plot encircles $-1$ exactly $P$ times counter-clockwise.**

Two cases in practice:

**Stable open loop ($P = 0$):** stable iff the plot **does not encircle $-1$ at all.** This is the case you meet most often, and it reduces to a glance at the picture.

**Unstable open loop ($P > 0$):** you *need* encirclements. And notice what that means — **an unstable plant requires enough gain**. Too little gain and the plot doesn't reach far enough to encircle $-1$. This is the formal version of "you must be fast enough to catch a falling pendulum", and it's why an unstable plant has a *lower* bound on bandwidth.

### Why $-1$

Because closed-loop poles are the roots of $1 + L(s) = 0$, i.e. $L(s) = -1$. The point $-1$ is where the loop gain has magnitude 1 and phase 180° — the signal comes back around, same size, exactly inverted, and the negative feedback subtraction makes it reinforce. **That's the definition of sustained oscillation.**

### Reading the plot

```
              Im
               │
       ────────┼────────  Re
        ●      │    ╱
       −1     ╱│  ╱
            ╱  │╱      ← L(jω) curve
          ╱    │
```

The **distance from the curve to $-1$ is how close you are to instability.** Everything about robustness is that distance, measured in different ways:

- **Gain margin** — where the curve crosses the negative real axis, GM $= 1/|L|$ at that point
- **Phase margin** — where the curve crosses the unit circle, PM is the angle to the negative real axis
- **Vector margin** — the *shortest* distance from the curve to $-1$

**Vector margin is the honest one**, and it's why the next section matters.

## Margins can lie

A design can have GM = 10 dB and PM = 60° — textbook-good numbers — **and still be one small perturbation from instability.**

The failure case: the Nyquist plot loops in *close* to $-1$ without crossing either the unit circle or the negative real axis near it. Both classical margins measure along their own axis and miss the approach entirely.

```
              Im
               │
      ─────────┼──────  Re
        ●   ╱─╮│
       −1  │  ││  ← curve passes very close to −1,
            ╲─╯│     but neither margin registers it
```

**Gain and phase margins measure two specific directions. Uncertainty comes from all directions.**

The fix is the **sensitivity peak**:

$$M_s = \max_\omega |S(j\omega)| = \max_\omega\left|\frac{1}{1 + L(j\omega)}\right| = \frac{1}{\text{min distance from } L \text{ to } -1}$$

**$M_s$ is the reciprocal of the vector margin**, so one number captures the closest approach regardless of direction.

**Target $M_s < 2$ (6 dB).** And it implies the classical margins:

$$GM \geq \frac{M_s}{M_s - 1}, \qquad PM \geq 2\arcsin\frac{1}{2M_s}$$

$M_s = 2$ guarantees GM ≥ 6 dB and PM ≥ 29°. **A good $M_s$ guarantees good classical margins; good classical margins do not guarantee a good $M_s$.** If you check one robustness number, check this one.

## Uncertainty

Robustness only means something relative to a stated set of possible plants. The standard formulations:

**Multiplicative:** $G_{real}(s) = G(s)\big(1 + \Delta(s)\big)$, with $|\Delta(j\omega)| < W(\omega)$

**Additive:** $G_{real}(s) = G(s) + \Delta(s)$

$W(\omega)$ is the **uncertainty weight** — how wrong your model might be at each frequency. It's typically small at low frequency and large at high frequency, because you know the DC gain well and the high-frequency dynamics badly. That shape is the mathematical expression of a real fact about modelling.

**The robust stability condition** for multiplicative uncertainty:

$$|T(j\omega)| < \frac{1}{W(\omega)} \quad \forall\omega$$

$T$ is the complementary sensitivity. **Where uncertainty is large, closed-loop gain must be small.**

> Which is the formal statement of something you'd arrive at by instinct: **don't run high loop gain at frequencies where you don't trust your model.** It's also the theoretical justification for rolling off the loop gain at high frequency — not just to reject noise, but because that's where your model is wrong.

## Fundamental limits

The results that separate control theory from tuning by feel: **constraints no controller can beat.**

### Bode's sensitivity integral — the waterbed

For a stable open-loop system with pole excess ≥ 2:

$$\int_0^\infty \ln|S(j\omega)|\,d\omega = 0$$

**The area under the log-sensitivity curve is conserved.** Push sensitivity down (better disturbance rejection) at one frequency and it *must* rise above 1 somewhere else.

```
 ln|S|
    │        ╱╲  ← amplified here (necessarily)
   0┼───────╯──╲────────
    │  ╲___╱    ╰──
    │  ↑ attenuated here
    └───────────────→ ω
```

You are not removing disturbance rejection difficulty — **you are moving it.** The name "waterbed effect" is exact.

**With unstable poles $p_i$ it's worse:**

$$\int_0^\infty \ln|S(j\omega)|\,d\omega = \pi\sum \text{Re}(p_i)$$

The conserved area is now *positive* — an unstable plant forces net amplification. **Unstable plants are fundamentally harder, and no amount of controller sophistication changes that.**

### RHP zeros and delays

$$\text{RHP zero at } z: \quad \omega_c \lesssim z/2$$

$$\text{Delay } T: \quad \omega_c \lesssim 1/T$$

Not tuning guidance — **hard caps.** Exceed them and the loop is unstable, whatever the controller.

**The impossible case** is worth being able to recognise: a plant with an unstable pole at $p$ and an RHP zero at $z$ where $z < 4p$ or so. The pole demands high bandwidth, the zero forbids it, and **no controller exists that stabilises it with reasonable margins.**

> **This is the most valuable thing in the note.** If you meet a plant like that, the answer is not a better controller — it's to change the plant, move the sensor, or add an actuator. Recognising that early saves months. It's also why some aircraft configurations are simply not flown, and why certain chemical processes are redesigned rather than better controlled.

## Robust control

The field built on taking these limits seriously. Named here so the vocabulary is familiar rather than developed in full.

**$\mathcal{H}_\infty$ control** — minimise the worst-case gain from disturbance to error over all frequencies. **Mixed sensitivity** design shapes $S$, $T$ and $KS$ simultaneously with weighting functions:

$$\min_K \left\|\begin{matrix} W_1 S \\ W_2 KS \\ W_3 T \end{matrix}\right\|_\infty$$

You choose the weights to encode your specification — $W_1$ where you want disturbance rejection, $W_3$ where you don't trust the model — and the synthesis returns a controller or tells you the specification is infeasible. **The infeasibility answer is genuinely useful**, because it tells you the specification is the problem, not your tuning.

**$\mu$-synthesis** handles structured uncertainty — several independently uncertain parameters — and is less conservative than treating everything as one unstructured block.

**The trade-off in practice:** these methods produce controllers of high order (often the plant order plus the weights), which are harder to implement, harder to explain, and harder to tune in the field. They're standard in aerospace and hard-disk servo design, and rare in process control, where a well-tuned PI with good margins is easier to maintain.

## Practical robustness

What to actually check, in order:

1. **$M_s < 2$** — the sensitivity peak. The single most informative number
2. **PM ≥ 45°, GM ≥ 6 dB** — necessary, not sufficient
3. **Delay margin** — $PM_{rad}/\omega_c$ seconds. How much extra delay before instability. **Especially worth computing for anything networked or software-timed**, since delay is the thing most likely to change unexpectedly
4. **Gain variation** — does it survive the plant gain doubling or halving? Real plants change with temperature, load, and wear
5. **Simulate against the extremes** of your parameter ranges, not just the nominal model
6. **Check actuator effort** — $|KS|$ tells you the control signal from noise. A robust design that saturates is not robust

> **A controller tuned perfectly for the nominal plant and marginal everywhere else is a bad design.** Deliberately detune for margin. The best real-world controller is usually noticeably slower than the fastest stable one, and that gap is the price of it still working next year.

---

## Related
- [[engineering/02-control-theory/06-frequency-response|Frequency Response]] — where margins are read
- [[engineering/02-control-theory/05-stability-and-root-locus|Stability and Root Locus]] — the time-domain view
- [[engineering/02-control-theory/11-optimal-control-and-lqr|Optimal Control and LQR]] — optimality vs robustness
- [[engineering/02-control-theory/README|Control theory map]]
