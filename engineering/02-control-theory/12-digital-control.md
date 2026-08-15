# Digital Control

**[Intermediate → Advanced]** — Everything above assumed continuous time. Your controller runs on a microcontroller at a fixed rate, and that changes things.

## What sampling does

A digital controller doesn't see a signal — it sees samples, and it holds its output constant between them.

```
 continuous ──→[ ADC ]──→[ CONTROLLER ]──→[ ZOH/DAC ]──→ continuous
                sample       compute          hold
```

**Three consequences, and the first is the one that bites:**

**1. The zero-order hold adds delay.** The output is held constant for a whole sample period, so on average it's late by $T/2$:

$$\text{effective delay} \approx T/2 \quad\Longrightarrow\quad \text{phase lag} \approx -\frac{\omega T}{2} \text{ rad}$$

**This eats phase margin**, and it's the single most common reason a controller that simulated beautifully oscillates on hardware. → [[engineering/02-control-theory/06-frequency-response|Frequency Response]]

**2. Aliasing.** Frequencies above $f_s/2$ (the Nyquist frequency) fold back and appear as low-frequency content. A 510 Hz vibration sampled at 1 kHz shows up as a 10 Hz signal your controller will earnestly try to reject.

**Anti-aliasing is an analogue problem.** Once aliased, it's indistinguishable from real signal and no digital filter can recover it — you need a lowpass *before* the ADC. **The commonest omission in a first digital control implementation.**

**3. Quantisation.** Finite ADC resolution puts a floor on your measurement precision, and finite DAC resolution puts a floor on your actuation. A 10-bit ADC over a 10 V range resolves ~10 mV, and **the derivative term amplifies that quantisation noise directly** — a big reason D behaves worse on hardware than in simulation.

## Choosing the sample rate

The engineering decision that matters most.

**Shannon says $f_s > 2f_{max}$.** That's the floor for *reconstruction*, and it is far too slow for *control*.

**For control, the practical rules:**

$$f_s \approx 20 \text{ to } 40 \times f_b \qquad\text{(closed-loop bandwidth)}$$

or equivalently **10–20 samples per rise time**.

| Application | Typical rate |
|---|---|
| Temperature / process | 1 Hz – 1 min |
| Motor speed | 1 kHz |
| Motor current | 10–20 kHz |
| Quadcopter attitude | 500 Hz – 1 kHz |
| Hard disk servo | 20–50 kHz |

**Too slow:** delay destroys phase margin, disturbances between samples go unseen, and the design simply doesn't behave like its continuous model.

**Too fast** is not free either: quantisation noise dominates the derivative, coefficients cluster near $z = 1$ where fixed-point arithmetic loses precision, and you burn CPU you might need elsewhere.

> **Jitter is worse than latency.** A consistent 2 ms delay you can design around. A delay varying between 1 and 3 ms you cannot, because your effective gains change sample to sample. **Use a timer interrupt, not a `sleep()` in a loop.** This matters more than the exact rate you choose.

## The z-transform

The discrete counterpart of Laplace, with the same purpose: turn difference equations into algebra.

$$X(z) = \sum_{k=0}^\infty x[k]z^{-k}$$

**$z^{-1}$ is a one-sample delay.** That's the whole intuition — a unit delay operator, exactly as $s$ is a differentiator.

The mapping between domains:

$$z = e^{sT}$$

And it moves the stability region:

```
   s-plane                    z-plane
      Im                         Im
       │                          │  ╱‾╲
  ─────┼─────  Re      →     ─────┼(  ● )──  Re
   LHP │                          │  ╲_╱
  stable                       inside unit circle
                                  = stable
```

$$\boxed{\text{Discrete stability} \iff |z_i| < 1 \text{ for all poles}}$$

**The left half plane maps to the interior of the unit circle.** The imaginary axis maps to the circle itself. The origin $s=0$ maps to $z=1$ — **which is why a discrete integrator is $\frac{1}{z-1}$ and has a pole at $z=1$**, right on the boundary, exactly as $1/s$ sits on the imaginary axis.

**Poles near $z = 1$ are slow. Poles near $z = 0$ are fast** (deadbeat, settling in a few samples). The correspondence with continuous poles:

$$|z| = e^{-\zeta\omega_n T}, \qquad \angle z = \omega_d T$$

## Discretising a controller

You designed $C(s)$. You need $C(z)$. Four methods, and the choice matters.

**Forward Euler** — $s \to \frac{z-1}{T}$

Simplest. **Can turn a stable controller unstable** — the mapping sends part of the stable $s$-region outside the unit circle. Only acceptable at very high sample rates.

**Backward Euler** — $s \to \frac{z-1}{Tz}$

Always maps stable to stable. Slightly distorts the response but is safe, and it's a reasonable default for simple controllers.

**Tustin / bilinear** — $s \to \frac{2}{T}\cdot\frac{z-1}{z+1}$

**The one to use.** Maps the entire LHP to exactly the unit disc — stability preserved in both directions — and is second-order accurate. Its only flaw is **frequency warping**: the frequency axis compresses as it approaches Nyquist, so a filter corner ends up slightly off.

**Tustin with prewarping** fixes that at one chosen frequency:

$$s \to \frac{\omega_0}{\tan(\omega_0 T/2)}\cdot\frac{z-1}{z+1}$$

Prewarp at the crossover frequency, or at a notch you need placed exactly.

**Zero-order hold (`c2d`)** — exact discretisation of the *plant*, accounting properly for the hold. **The right choice for discretising a plant model**; Tustin is the right choice for discretising a controller.

> **The general advice: discretise the plant with ZOH, then design directly in discrete time.** Designing in continuous time and discretising the controller works when $f_s$ is 30×+ the bandwidth. When sampling is slow relative to the dynamics, direct discrete design is the only thing that delivers the response you specified.

## Implementation

### Difference equations

A discrete controller becomes a difference equation you can execute:

$$C(z) = \frac{b_0 + b_1z^{-1} + b_2z^{-2}}{1 + a_1z^{-1} + a_2z^{-2}}$$

$$u[k] = b_0e[k] + b_1e[k-1] + b_2e[k-2] - a_1u[k-1] - a_2u[k-2]$$

**Multiply, add, shift the history. That's the whole controller.**

**Use second-order sections.** A high-order filter implemented as one big difference equation is numerically fragile — coefficient sensitivity grows badly with order. Factor into cascaded biquads. **Standard practice in DSP, and just as necessary here.**

### Fixed point

On hardware without an FPU:

**Q-format** — an integer with an implied binary point. Q15 means 15 fractional bits.

- **Multiplication doubles the word length.** Multiply two Q15 values into a 32-bit accumulator, then shift back
- **Watch for overflow.** Use saturating arithmetic — wrapping around turns a large positive command into a large negative one, which on a motor is spectacular
- **Keep the integrator wide.** It accumulates small numbers over a long time and is the first thing to lose precision. Use extra fractional bits there specifically

**If you have an FPU, use floats.** Single precision is plenty for control, and the debugging time saved is worth more than the cycles.

### The control loop

```
timer interrupt at fixed rate:
    y = read_sensor()          # ADC
    u = controller_update(y)   # the difference equation
    u = clamp(u, u_min, u_max)
    write_actuator(u)          # DAC / PWM
```

**Read the sensor and write the actuator at consistent points in the cycle.** Moving them around changes your effective delay.

**Keep the computation short and deterministic** — no dynamic allocation, no unbounded loops, no blocking I/O in the control path. Log to a buffer and let a lower-priority task ship it.

**Minimise the sensor-to-actuator delay.** If the computation is long, the classic trick is to split it: compute the part that depends on the new measurement first, output it immediately, then do the rest of the update. Saves nearly a full sample of delay.

## What actually goes wrong

The failure modes, in roughly the order you'll meet them:

**Sampling too slowly.** Works in simulation, oscillates on hardware. Check that phase lag: $\omega_c T/2$ radians of margin gone.

**No anti-aliasing filter.** Mysterious low-frequency oscillation with no obvious source. Look for a real disturbance at $f_s \pm$ your oscillation frequency.

**Timing jitter.** An RTOS-less superloop, a `delay()` call, an interrupt that sometimes runs long. Symptom: inconsistent behaviour that changes when unrelated code changes.

**Integral windup.** Same as ever, and no less common in digital form. → [[engineering/02-control-theory/04-pid-control|PID Control]]

**Derivative on quantised measurements.** The derivative of a staircase is a series of spikes. **Filter it, always** — and consider estimating velocity with an observer instead of differencing. → [[engineering/02-control-theory/10-observers-and-kalman|Observers]]

**Unhandled saturation.** PWM duty capped at 100%, current limits, thermal derating. The controller must know its real limits, not the ones in the model.

**Numerical drift** in a long-running integrator. Single precision loses resolution once the accumulator is large. Use a wider accumulator or periodic reconditioning.

## Networked and distributed control

Increasingly common, and it breaks assumptions worth naming: variable delay, dropped packets, no shared clock.

The standard responses:

- **Timestamp everything**, and use the timestamp rather than arrival order
- **Design for the worst-case delay**, not the average
- **A Kalman filter handles missing measurements naturally** — skip the update, keep predicting. This is a genuine advantage over a fixed filter and the main reason estimator-based designs suit networked systems
- **Event-triggered control** — transmit only when the error exceeds a threshold, rather than on a fixed schedule. Cuts bandwidth substantially with provable stability guarantees
- **Fail safe on loss of signal.** Decide in advance what the actuator does when the network drops, and make it a deliberate choice rather than "hold the last value forever"

The parallels with distributed systems are real, and worth taking seriously — a cloud autoscaler is a networked control loop with a slow, noisy plant and multi-minute actuator delay. → [[architecture/04-distributed-systems/README|Distributed Systems]]

---

## Related
- [[engineering/02-control-theory/04-pid-control|PID Control]] — the controller you're discretising
- [[engineering/02-control-theory/08-state-space|State Space]] — the discrete state-space form
- [[engineering/02-control-theory/06-frequency-response|Frequency Response]] — where the hold delay costs you
- [[engineering/02-control-theory/README|Control theory map]]
