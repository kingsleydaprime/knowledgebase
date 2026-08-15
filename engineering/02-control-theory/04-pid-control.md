# PID Control

**[Intermediate]** — The controller you will actually implement. What each term does, how to tune one, and the four implementation details that separate working code from a controller that fights you.

**The most practically important note in this track.** Something like 95% of industrial control loops are PID, and most of them are badly tuned.

## The controller

$$u(t) = K_p e(t) + K_i \int_0^t e(\tau)\,d\tau + K_d \frac{de(t)}{dt}$$

In the Laplace domain:

$$C(s) = K_p + \frac{K_i}{s} + K_d s = \frac{K_d s^2 + K_p s + K_i}{s}$$

Three terms, each responding to a different aspect of the error:

| Term | Responds to | Effect |
|---|---|---|
| **P** — proportional | error **now** | the main driving effort |
| **I** — integral | **accumulated** past error | eliminates steady-state offset |
| **D** — derivative | **rate of change** of error | damping, anticipation |

> A useful framing: **P is the present, I is the past, D is the future.**

## Proportional

$$u = K_p e$$

The obvious controller: bigger error, harder push.

**What it does:** raises loop gain, so faster response and smaller steady-state error.

**Its two failures:**

**Steady-state offset.** On a type-0 plant, P control *always* leaves an error. If $e = 0$ then $u = 0$, and if the plant needs a nonzero input to hold the setpoint (holding a heater against ambient losses, holding an arm against gravity), then the error can never reach zero. The error settles wherever $K_p e$ equals the required input.

$$e_{ss} = \frac{1}{1 + K_p K_{plant}}$$

Raising $K_p$ shrinks it but never removes it. → [[engineering/02-control-theory/03-time-response|Steady-state error]]

**Instability at high gain.** Push $K_p$ up and the system oscillates, then diverges. The gain at which it starts is the **ultimate gain** $K_u$ — and it's the basis of Ziegler–Nichols tuning.

**Proportional band** is the process-control way of expressing the same thing: $PB = 100/K_p$ percent — the error span over which the output moves through its full range. Same knob, inverted.

## Integral

$$u = K_i \int e\,dt$$

**It accumulates.** As long as any error persists, the integral keeps growing, so the output keeps rising until the error is gone.

**This is what kills steady-state error**, and the mechanism is exactly what note 03 describes: the $1/s$ adds an integrator, taking the loop from type 0 to type 1.

The reason it's not free: **an integrator adds 90° of phase lag** across all frequencies. Phase lag eats phase margin, so **integral action always makes a loop less stable**. Too much $K_i$ gives sluggish oscillation — a slow hunting around the setpoint.

It also **responds to history, not the present**, so it lags. After a disturbance, the integral has to unwind, which is why an I-heavy loop overshoots on the way back.

### Integral windup — the classic bug

**If you implement one thing correctly, make it this.**

The actuator saturates. The valve is fully open, the motor is at max torque, the heater is at 100%. But the error is still nonzero, so the integrator keeps accumulating — into a number that means nothing, because the output can't go any higher.

Then the process finally reaches the setpoint. The error flips sign. But the integral is now enormous, so the controller **holds the actuator saturated well past the setpoint** while the integral slowly unwinds.

```
setpoint ─────────────────────────────
                    ╭──────╮  ← huge overshoot,
                   ╱        ╲    controller "stuck"
                  ╱          ╲___
        ________╱
  integral ────────▲ accumulating while saturated
```

Symptom: massive overshoot and a long, unexplained delay before the controller responds to anything.

**Three fixes, all standard:**

**Conditional integration (clamping)** — stop integrating whenever the output is saturated. Simplest and usually sufficient:

```
if not saturated:
    integral += error * dt
```

**Back-calculation** — feed the difference between commanded and actual output back into the integrator, unwinding it proportionally:

```
integral += (error + (u_actual - u_commanded) / Kb) * dt
```

**Integral limits** — clamp the integral term to a fixed range. Crude, but effective and easy to reason about.

> **Every real PID implementation needs anti-windup.** A textbook PID with no windup protection will misbehave the first time it hits a limit, and it will hit a limit.

## Derivative

$$u = K_d \frac{de}{dt}$$

Responds to *how fast* the error is changing — it acts before the error is large, which is why it reads as anticipation.

**What it does:** adds damping. Reduces overshoot and settling time, and **adds phase lead**, which improves stability margin. It's the term that lets you run higher $K_p$ than you otherwise could.

**Its three problems, and they're why D is often left at zero:**

**Noise amplification.** Differentiation multiplies high-frequency content by $\omega$. Sensor noise at 1 kHz gets amplified enormously. This is the main reason D is disabled in practice — **on a noisy sensor, D is worse than useless.**

The fix is a **filtered derivative**:

$$D(s) = \frac{K_d s}{1 + s/N}$$

with $N$ typically 8–20. Above the corner frequency it stops differentiating and behaves like a gain, bounding the noise amplification at $K_d N$. **Every practical PID uses a filtered derivative** — a pure $K_d s$ is not implementable and not desirable.

**Derivative kick.** A step change in setpoint makes $de/dt$ momentarily infinite, producing a spike in the output.

The fix is **derivative on measurement** — since $e = r - y$ and $r$ is piecewise constant, $\dot{e} = -\dot{y}$ almost always:

$$u = K_p e + K_i \int e\,dt - K_d \frac{dy}{dt}$$

Note the sign. **This is what you should write by default**; it behaves identically for disturbance rejection and eliminates the kick entirely.

**It's not useful on a delay-dominated process.** If the process has significant dead time, the derivative is reacting to old information. Most process-control loops run PI for exactly this reason.

## Setpoint weighting

The generalisation of the two fixes above, and worth knowing because it decouples two requirements:

$$u = K_p(\beta r - y) + K_i\int(r - y)\,dt - K_d\frac{dy}{dt}$$

$\beta \in [0,1]$ weights the setpoint in the proportional term. $\beta = 1$ is standard PID; $\beta = 0$ is proportional-on-measurement.

**Why it matters:** setpoint tracking and disturbance rejection have different optimal tunings. Setpoint weighting lets you tune for disturbance rejection (usually what matters) and then use $\beta$ to soften the setpoint response without retuning anything.

## Tuning

### What each knob does

The table everyone wants, with the honest caveat that these are trends, not guarantees — the terms interact:

| Increase | Rise time | Overshoot | Settling | Steady-state error | Stability |
|---|---|---|---|---|---|
| **$K_p$** | ↓ faster | ↑ worse | small change | ↓ smaller | ↓ worse |
| **$K_i$** | ↓ faster | ↑ worse | ↑ worse | **eliminated** | ↓ worse |
| **$K_d$** | small change | ↓ better | ↓ better | no effect | ↑ better |

### Manual tuning — the method that works

The one to use when you can experiment on the plant:

1. **Set $K_i = 0$, $K_d = 0$.**
2. **Raise $K_p$ until the loop oscillates steadily.** Note that gain — it's $K_u$.
3. **Halve it.** You now have a stable P controller with offset.
4. **Add $K_i$**, increasing until the offset is removed in acceptable time. Too much and it oscillates slowly.
5. **Add $K_d$ only if you need it** and the sensor is clean enough. Increase until overshoot is acceptable; back off when the output gets jittery.
6. **Test against a disturbance, not just a setpoint change.** These are different problems and a loop tuned for one can be poor at the other.

### Ziegler–Nichols

The classic recipes. Two forms.

**Closed loop (ultimate gain).** Find $K_u$ and the oscillation period $T_u$ as above:

| Controller | $K_p$ | $T_i$ | $T_d$ |
|---|---|---|---|
| P | $0.5K_u$ | — | — |
| PI | $0.45K_u$ | $T_u/1.2$ | — |
| PID | $0.6K_u$ | $T_u/2$ | $T_u/8$ |

(with $K_i = K_p/T_i$ and $K_d = K_p T_d$)

**Open loop (step test).** From a step response, read dead time $\theta$, time constant $\tau$, and gain $K$:

| Controller | $K_p$ | $T_i$ | $T_d$ |
|---|---|---|---|
| P | $\tau/(K\theta)$ | — | — |
| PI | $0.9\tau/(K\theta)$ | $3.3\theta$ | — |
| PID | $1.2\tau/(K\theta)$ | $2\theta$ | $0.5\theta$ |

> **Ziegler–Nichols is aggressive.** It targets quarter-amplitude damping — each oscillation peak a quarter of the last — which gives roughly 25% overshoot and thin stability margins. It was designed for 1940s process control where a fast response mattered more than a smooth one.
>
> **Treat Z-N as a starting point, not an answer.** In practice halve the gain from what it gives you, then tune from there. And don't run the closed-loop test on anything where sustained oscillation is dangerous.

**Cohen–Coon** is the alternative for delay-dominated processes ($\theta/\tau > 0.3$), where Z-N does badly.

**Lambda tuning (IMC)** is what modern process control actually uses: you specify a desired closed-loop time constant $\lambda$ and compute the gains from the model. For a first-order-plus-dead-time plant:

$$K_p = \frac{\tau}{K(\lambda + \theta)}, \qquad T_i = \tau$$

**The appeal is that $\lambda$ is a physically meaningful knob** — "I want this loop to settle in 30 seconds" — instead of a dimensionless gain. Larger $\lambda$ is slower and more robust. It's far more predictable than Z-N and is the recommended default when you have a model.

## Implementation

A correct discrete PID, with every fix above applied:

```
# state
integral = 0
prev_measurement = 0

# each sample, at fixed dt
error = setpoint - measurement

# P — with setpoint weighting
P = Kp * (beta * setpoint - measurement)

# I — with clamping anti-windup
integral += Ki * error * dt

# D — on measurement, filtered, note the sign
d_meas = (measurement - prev_measurement) / dt
d_filt = alpha * d_filt + (1 - alpha) * d_meas
D = -Kd * d_filt

u = P + integral + D

# saturate, and stop integrating if we're against a limit
u_sat = clamp(u, u_min, u_max)
if u != u_sat:
    integral -= Ki * error * dt      # undo this sample's accumulation

prev_measurement = measurement
```

**The details that matter, in order of how often they're got wrong:**

**Fixed sample time.** The $dt$ in the integral and derivative must be consistent. Jitter changes your effective gains sample to sample. Use a timer interrupt or a real-time loop, not `sleep()` in a while loop. If $dt$ genuinely varies, measure it and use the actual value.

**Sample fast enough.** Rule of thumb: **10–20 samples per rise time**, or $\omega_s > 20\omega_b$. Too slow adds delay and destabilises; too fast wastes cycles and amplifies quantisation noise in the derivative. → [[engineering/02-control-theory/12-digital-control|Digital Control]]

**Bumpless transfer.** Switching between manual and automatic, or changing gains on the fly, must not step the output. Initialise the integral so the new output matches the current one.

**Units and scaling.** Keep gains in physical units where you can. It makes them portable and it makes wrong values obvious.

**Velocity form** — an alternative worth knowing:

$$\Delta u_k = K_p(e_k - e_{k-1}) + K_i e_k \Delta t + K_d(\ldots)$$

You compute the *change* in output and accumulate it in the actuator. **Windup protection is inherent** (there's no explicit integral state to wind up) and bumpless transfer is automatic. Common in PLCs, and a good default when driving a valve or a stepper that holds its own position.

## Cascade control

When one loop isn't enough, and the most useful structure beyond plain PID.

```
r →[ OUTER PID ]→ setpoint →[ INNER PID ]→[ ACTUATOR ]→[ PLANT ]
        ▲                          ▲                        │
        │                          └─── fast sensor ────────┤
        └────────── slow sensor ─────────────────────────────┘
```

The outer (primary) loop controls what you care about; its output is the **setpoint for the inner loop**, which controls something faster and closer to the actuator.

**Standard example:** a robot joint. The outer loop controls position, and commands a velocity; the inner loop controls velocity, and commands current; an innermost loop controls current. Each is faster than the one outside it. → [[robotics/README|Robotics]]

**Rules:**

- **The inner loop must be significantly faster** — 5–10× is the usual guidance. Otherwise the loops interact and both become hard to tune
- **Tune inner first**, with the outer loop in manual, then close the outer around it
- The payoff: **the inner loop absorbs disturbances before they reach the outer loop**, and it linearises the actuator as far as the outer loop is concerned

## When PID isn't enough

PID is remarkable value for three parameters, and it does have limits:

- **Significant dead time** — use a Smith predictor or model predictive control
- **MIMO with strong coupling** — loops fight each other → [[engineering/02-control-theory/08-state-space|State Space]], LQR
- **Hard constraints** you must respect (limits on states, not just inputs) → **model predictive control**
- **Strong nonlinearity** across the operating range → gain scheduling, or [[engineering/02-control-theory/13-nonlinear-and-modern-control|nonlinear control]]
- **Non-minimum-phase plants** — an RHP zero caps bandwidth no matter the tuning → [[engineering/02-control-theory/02-modelling-and-transfer-functions|RHP zeros]]

But start with PID. **The commonest failure mode in practice isn't that PID was inadequate — it's that it was tuned badly, implemented without anti-windup, or differentiating a noisy signal.**

---

## Related
- [[engineering/02-control-theory/03-time-response|Time Response]] — the step test tuning depends on
- [[engineering/02-control-theory/05-stability-and-root-locus|Stability and Root Locus]] — why high gain destabilises
- [[engineering/02-control-theory/06-frequency-response|Frequency Response]] — what the D term does to phase
- [[engineering/02-control-theory/12-digital-control|Digital Control]] — implementing this on a microcontroller
- [[engineering/02-control-theory/README|Control theory map]]
