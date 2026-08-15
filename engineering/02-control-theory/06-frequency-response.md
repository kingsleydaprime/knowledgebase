# Frequency Response

**[Intermediate]** — Bode plots, what "bandwidth" actually means, and why frequency-domain thinking is how working engineers reason about loops.

## The idea

Feed a linear system a sinusoid and, after transients die, **the output is a sinusoid at the same frequency** — only the amplitude and phase differ.

$$u(t) = A\sin\omega t \quad\longrightarrow\quad y(t) = A|G(j\omega)|\sin\big(\omega t + \angle G(j\omega)\big)$$

That's it. **Substitute $s = j\omega$** into the transfer function and you get a complex number whose magnitude is the gain and whose angle is the phase shift, at that frequency.

Sweep $\omega$ across the range of interest and you have a complete description of the system — one that you can **measure directly on real hardware** without knowing the model. That last point is why the frequency domain dominates practical control: the Bode plot of a plant is something you can obtain experimentally on a plant nobody has ever modelled.

## Bode plots

Two plots against $\log\omega$:

- **Magnitude** in decibels: $20\log_{10}|G(j\omega)|$
- **Phase** in degrees: $\angle G(j\omega)$

**Why log scales.** They turn multiplication into addition. Since cascaded systems multiply, on a Bode plot they *add* — so you can sketch the plot of a complicated transfer function by adding the plots of its factors. That's the whole reason for the format.

Decibels worth memorising:

| Gain | dB |
|---|---|
| 0.01 | −40 |
| 0.1 | −20 |
| 0.5 | −6 |
| 1 | **0** |
| 2 | +6 |
| 10 | +20 |
| 100 | +40 |

**0 dB means gain of 1** — the input passes through unchanged. That frequency is where everything interesting happens.

### The building blocks

Every rational transfer function is a product of these, so its Bode plot is their sum:

| Factor | Magnitude | Phase |
|---|---|---|
| Gain $K$ | flat at $20\log K$ | 0° |
| Integrator $1/s$ | **−20 dB/decade**, all $\omega$ | **−90°**, all $\omega$ |
| Differentiator $s$ | +20 dB/decade | +90° |
| Pole $\frac{1}{1 + s/\omega_c}$ | flat, then −20 dB/dec after $\omega_c$ | 0° → **−90°** |
| Zero $1 + s/\omega_c$ | flat, then +20 dB/dec after $\omega_c$ | 0° → +90° |
| Delay $e^{-sT}$ | **flat at 0 dB** | $-\omega T$, **unbounded** |

**Each pole costs you 20 dB/decade of rolloff and 90° of phase lag. Each zero gives them back.**

A first-order pole in detail:

```
 dB
  0 ┼────────────╮
    │             ╲  −20 dB/decade
−20 ┤              ╲
    └──────┬────────╲──────→ log ω
          ωc

 deg
  0 ┼──────╮
    │       ╲
−45 ┤        ●  ← at ωc, phase is exactly −45°
    │         ╲
−90 ┤          ╰────────
```

**At the corner frequency the magnitude is −3 dB and the phase is −45°.** The asymptotes miss by 3 dB there, which is close enough for design work.

**The delay row is the one to stare at.** A pure delay costs you *nothing* in magnitude and *unbounded* phase. It gives you no benefit and takes away the thing keeping you stable. → [[engineering/02-control-theory/03-time-response|Time delay]]

### Sketching by hand

Still worth being able to do, because it builds the intuition that the software plot doesn't:

1. Start at low frequency with the gain and any integrators (slope = −20 dB/dec per integrator)
2. At each pole corner, **subtract** 20 dB/decade from the slope
3. At each zero corner, **add** 20 dB/decade
4. Phase: each pole contributes −90°, spread over roughly a decade either side of its corner; each zero +90°

The final slope is $-20(n - m)$ dB/decade — the pole excess sets the high-frequency rolloff.

## Second-order resonance

$$G(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$

Rolls off at −40 dB/decade past $\omega_n$ with 180° of total phase lag. But for **$\zeta < 0.707$ there's a resonant peak**:

$$M_r = \frac{1}{2\zeta\sqrt{1-\zeta^2}} \qquad \text{at} \qquad \omega_r = \omega_n\sqrt{1 - 2\zeta^2}$$

```
 dB
    │      ╱╲  ← peak grows as ζ → 0
  0 ┼─────╯  ╲
    │         ╲╲  −40 dB/dec
    └──────┬────╲╲──→ log ω
          ωn
```

**Lightly damped modes show up as sharp peaks**, and they're the practical danger in mechanical systems. Structural resonances, drive-belt compliance, unmodelled flexible modes — a peak that crosses 0 dB destabilises the loop even if the rigid-body design was fine. It's why you notch-filter a known resonance, and why a controller tuned on a rigid model can go unstable on the real machine.

## Loop shaping

**The central design idea in the frequency domain**, and the thing most worth taking away from this note.

You don't design the closed-loop response directly. You shape the **open-loop gain $L(j\omega)$**, because it's what you can see and what the controller directly modifies.

Recall from [[engineering/02-control-theory/02-modelling-and-transfer-functions|note 02]]:

$$T = \frac{L}{1+L} \qquad\qquad S = \frac{1}{1+L} \qquad\qquad S + T = 1$$

$T$ is the **complementary sensitivity** (reference to output), $S$ the **sensitivity** (disturbance to output).

- **Where $|L| \gg 1$:** $T \approx 1$, $S \approx 0$ — good tracking, good disturbance rejection
- **Where $|L| \ll 1$:** $T \approx 0$, $S \approx 1$ — no tracking, and **noise is rejected**

So:

> **Want high gain at low frequency and low gain at high frequency.** High gain where the references and disturbances live; low gain where the sensor noise and unmodelled dynamics live.

```
 |L| dB
    │────╲          ← high gain: tracking, disturbance rejection
    │     ╲
  0 ┼──────●──────────  ← crossover ωc: sets bandwidth,
    │       ╲              and phase margin is measured HERE
    │        ╲──────  ← low gain: noise rejection, robustness
    └──────────────→ log ω
```

**The crossover frequency $\omega_c$** — where $|L| = 1$ — is the single most important number in a design:

- **It sets the closed-loop bandwidth**, hence the speed: $\omega_c \approx \omega_b$, and rise time $\approx 1.8/\omega_c$
- **The slope through crossover should be about −20 dB/decade.** Steeper means more phase lag at crossover, hence less margin. This is Bode's gain–phase relationship doing its work
- **Phase margin is measured here**, and it's what determines the damping

And $S + T = 1$ is the algebraic statement of the constraint you can't escape: **you cannot make both small at the same frequency.** Rejecting a disturbance at $\omega$ means tracking noise at $\omega$.

## Bandwidth

$\omega_b$ is the frequency where the **closed-loop** gain drops to −3 dB. The system tracks references below it and ignores those above it.

**Higher bandwidth means faster response.** The connections:

$$t_r \approx \frac{1.8}{\omega_b}, \qquad \omega_b \approx \omega_c$$

**And higher bandwidth costs you:**

- **More noise passes through** — you're tracking at frequencies where the signal is mostly noise
- **More actuator effort**, so saturation becomes likely
- **Less robustness**, because high-frequency model error is exactly where your model is worst

**The hard limits on bandwidth** are worth knowing, because they're the ones you can't tune your way past:

| Limit | Rough cap on $\omega_c$ |
|---|---|
| RHP zero at $z$ | $\omega_c < z/2$ |
| Time delay $T$ | $\omega_c < 1/T$ |
| Unstable pole at $p$ | $\omega_c > 2p$ (a *lower* bound — you must be fast enough) |
| Actuator | can't demand what it can't deliver |
| Sensor noise | can't act on what you can't measure |

Note the third: an unstable plant forces bandwidth *up*, while an RHP zero or delay forces it *down*. **A plant with both an unstable pole and an RHP zero close together may be impossible to control at all** — the required bandwidth exceeds the permitted one. That's a fundamental result, not a design failure, and it's the sort of thing worth checking before spending a month tuning.

## Phase and gain margin

Defined here, used properly in the next note.

**Gain margin** — how much you can multiply the gain before instability. Read at the frequency where phase = −180°.

**Phase margin** — how much extra phase lag you can tolerate. Read at crossover, where $|L| = 1$.

```
 dB
    │────╲
  0 ┼─────╲●──────────
    │      ╲    ↕ gain margin
    └───────╲──┬──→
              ω(−180°)
 deg
    │──╲
    │   ╲  ↕ phase margin
−180┼────╲──●────────
    └────┬────────→
        ωc
```

**Targets: PM ≥ 45°, GM ≥ 6 dB.** Below ~30° phase margin a system is oscillatory and fragile.

**The rule of thumb worth memorising:**

$$\zeta \approx \frac{PM°}{100}$$

So 45° phase margin gives roughly $\zeta = 0.45$ — noticeable overshoot but usable. 70° gives $\zeta \approx 0.7$, the classic target. **This is the bridge between frequency-domain design and time-domain specifications**, and it's why an engineer can tune in the frequency domain while thinking about overshoot.

## Why work here at all

Given root locus exists, the case for the frequency domain:

**You can measure it.** A frequency sweep gives you the plot with no model at all. You cannot measure a root locus.

**Delays are exact.** $e^{-j\omega T}$ is just a phase shift. In root locus, delay requires a rational approximation.

**Uncertainty is naturally expressed here.** "My model is good to 100 rad/s and I don't trust it above that" is a frequency-domain statement, and robust control is built on it. → [[engineering/02-control-theory/07-nyquist-and-robustness|Nyquist and Robustness]]

**Margins are meaningful.** "45° of phase margin" is a real, defensible robustness claim. "Poles at $-2 \pm 3j$" tells you nothing about how much the plant can change.

**It composes.** Cascaded systems add on a Bode plot — which makes it possible to see, at a glance, what a compensator does to a loop.

---

## Related
- [[engineering/02-control-theory/05-stability-and-root-locus|Stability and Root Locus]] — the time-domain view
- [[engineering/02-control-theory/07-nyquist-and-robustness|Nyquist and Robustness]] — margins done properly
- [[engineering/02-control-theory/04-pid-control|PID Control]] — what P, I and D do to these plots
- [[engineering/02-control-theory/README|Control theory map]]
