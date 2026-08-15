# Modelling and Transfer Functions

**[Intermediate]** — Turning physics into a transfer function, why the Laplace transform is worth the trouble, and where poles and zeros come from.

## From physics to a differential equation

Every plant model starts with a balance law. Three examples that cover most of what you'll meet:

**Mass–spring–damper:**

$$m\ddot{x} + c\dot{x} + kx = F(t)$$

**RLC circuit** (voltage across the capacitor):

$$LC\ddot{v}_C + RC\dot{v}_C + v_C = v_{in}(t)$$

**DC motor** (speed from voltage, neglecting inductance):

$$J\dot{\omega} + b\omega = K_t i, \qquad V = Ri + K_e\omega$$

**Notice the first two are the same equation.** Mass ↔ inductance, damping ↔ resistance, spring ↔ 1/capacitance. That analogy is why control theory transfers across domains — the mathematics doesn't know whether it's describing a car suspension or a filter. → [[hardware/01-electricity|Hardware: Electricity]]

## Why Laplace

Differential equations are awkward to compose. If you have a controller feeding a plant feeding a sensor, combining three ODEs means substitution and a mess.

The **Laplace transform** converts differentiation into multiplication:

$$\mathcal{L}\{f(t)\} = F(s) = \int_0^\infty f(t)e^{-st}\,dt$$

$$\mathcal{L}\{\dot{f}\} = sF(s) - f(0) \qquad \mathcal{L}\{\ddot{f}\} = s^2F(s) - sf(0) - \dot{f}(0)$$

**With zero initial conditions, $d/dt$ becomes $\times s$.**

So an ODE becomes an algebraic equation, and cascading systems becomes **multiplying** their transfer functions. That's the entire payoff: composition becomes arithmetic.

The transforms worth knowing:

| $f(t)$ | $F(s)$ |
|---|---|
| $\delta(t)$ | $1$ |
| $1$ (step) | $1/s$ |
| $t$ (ramp) | $1/s^2$ |
| $e^{-at}$ | $1/(s+a)$ |
| $\sin\omega t$ | $\omega/(s^2+\omega^2)$ |
| $f(t-T)$ (delay) | $e^{-sT}F(s)$ |

That last one matters — **a pure time delay is $e^{-sT}$**, which is not a rational function, and it's why delay is so destructive to stability. → [[engineering/02-control-theory/06-frequency-response|Frequency Response]]

## The transfer function

$$G(s) = \frac{Y(s)}{U(s)} = \frac{\text{output}}{\text{input}}\Bigg|_{\text{zero initial conditions}}$$

For the mass–spring–damper:

$$G(s) = \frac{X(s)}{F(s)} = \frac{1}{ms^2 + cs + k}$$

**A transfer function is a complete description of a linear time-invariant system's input–output behaviour.** Everything about how it responds — speed, damping, oscillation, stability — is encoded in that ratio of polynomials.

Written generally:

$$G(s) = \frac{N(s)}{D(s)} = K\frac{(s - z_1)(s - z_2)\cdots}{(s - p_1)(s - p_2)\cdots}$$

**Poles** ($p_i$) — roots of the denominator. **Zeros** ($z_i$) — roots of the numerator.

## What poles mean

**The single most important idea in classical control:**

> **Poles determine the shape of the response. Their locations *are* the system's natural modes.**

Each pole contributes a term $e^{p_i t}$ to the response:

| Pole location | Contributes | Behaviour |
|---|---|---|
| Real, negative ($-a$) | $e^{-at}$ | decaying exponential — **stable** |
| Real, positive ($+a$) | $e^{at}$ | growing — **unstable** |
| Complex pair ($-\sigma \pm j\omega$) | $e^{-\sigma t}\sin(\omega t)$ | **damped oscillation** |
| Pure imaginary ($\pm j\omega$) | $\sin\omega t$ | sustained oscillation — marginally stable |
| At origin | constant | integrator |

```
              Im
               │      × ← unstable (right half plane)
     stable    │
        ×      │
   ────────────┼────────────  Re
        ×      │      ×
               │
    LEFT half plane = STABLE
```

$$\boxed{\text{Stable} \iff \text{all poles have negative real part}}$$

That's the criterion the entire field rests on. → [[engineering/02-control-theory/05-stability-and-root-locus|Stability]]

**Distance from the imaginary axis sets speed** — a pole at $-10$ decays ten times faster than one at $-1$. **The pole closest to the axis dominates**, which is what makes second-order approximation of high-order systems work in practice.

## What zeros mean

Less intuitive, and they matter more than people expect.

Zeros **don't affect stability** — they don't appear in the characteristic equation. They shape the *transient*: they can add overshoot, speed up the initial response, or cancel a pole.

**Right-half-plane zeros are the ones to watch.** A system with an RHP zero is **non-minimum phase**, and it exhibits **initial undershoot** — it goes the *wrong way first*.

Real examples:

- **Backing a car with a trailer** — to move the trailer left, you must first steer right
- **A bicycle** — countersteering: to turn left at speed, push the bars right first
- **Boiler drum level** — adding cold feedwater makes the level *drop* momentarily as steam bubbles collapse, before rising
- **Aircraft altitude via elevator** — pitching up initially loses altitude

> **RHP zeros impose a hard limit on achievable bandwidth.** You cannot control faster than an RHP zero allows, no matter how clever the controller — pushing gain up makes the loop unstable. That's a fundamental constraint, not a tuning problem, and recognising a non-minimum-phase plant early saves a lot of wasted effort.

## Block diagram algebra

The reason transfer functions are worth it — composition becomes arithmetic.

**Series:** $G_1G_2$
**Parallel:** $G_1 + G_2$

**Negative feedback** — the one to memorise:

$$T(s) = \frac{G(s)}{1 + G(s)H(s)}$$

with $G$ forward path and $H$ the feedback path. For unity feedback ($H=1$):

$$T(s) = \frac{G}{1+G}$$

**$L = GH$ is the loop gain**, and it's the central object of classical design. Note the closed-loop poles are the roots of $1 + L(s) = 0$ — **the characteristic equation.** Everything in [[engineering/02-control-theory/05-stability-and-root-locus|root locus]] and [[engineering/02-control-theory/07-nyquist-and-robustness|Nyquist]] is about the roots of that one equation.

And the insensitivity result from [[engineering/02-control-theory/01-what-control-theory-is|note 01]] falls straight out: when $|L| \gg 1$, $T \approx 1$ regardless of $G$.

## Linearisation

Transfer functions require **linearity**, and real systems aren't. The standard move is to linearise about an operating point.

For $\dot{x} = f(x, u)$, expand in a Taylor series about $(x_0, u_0)$ and keep the first-order terms:

$$\delta\dot{x} \approx \left.\frac{\partial f}{\partial x}\right|_0 \delta x + \left.\frac{\partial f}{\partial u}\right|_0 \delta u$$

**The pendulum is the standard example:**

$$\ddot\theta + \frac{g}{L}\sin\theta = 0 \quad\xrightarrow{\ \sin\theta \approx \theta\ }\quad \ddot\theta + \frac{g}{L}\theta = 0$$

Valid to about 20°, and the linear model is where the whole classical toolkit applies.

**Three things to keep in mind:**

**A linearised model is local.** Valid near the operating point and nowhere else. A model linearised at hover doesn't describe aggressive flight.

**Gain scheduling** is the practical response: linearise at several operating points, design a controller for each, and interpolate. Standard in aerospace and engine control.

**Some nonlinearities cannot be linearised away** — saturation, backlash, friction, hysteresis. Those need [[engineering/02-control-theory/13-nonlinear-and-modern-control|nonlinear methods]].

## System identification

Often you can't derive a model — the plant is too complex or poorly characterised. So you measure one.

**Step response** — apply a step, record the output, fit a model. The workhorse for process control, and the basis of Ziegler–Nichols tuning. A first-order-plus-dead-time fit

$$G(s) = \frac{Ke^{-\theta s}}{\tau s + 1}$$

describes a surprising number of industrial processes with three parameters.

**Frequency sweep** — inject sinusoids across a range and measure gain and phase. Gives the Bode plot directly and is the most informative method, at the cost of time. → [[engineering/02-control-theory/06-frequency-response|Frequency Response]]

**Least-squares / ARX fitting** — apply a rich excitation (PRBS is standard) and fit a discrete model numerically. What `System Identification Toolbox` and its open-source equivalents do.

**Practical warnings:**

- **Excite the frequencies you care about.** A slow ramp tells you nothing about high-frequency behaviour
- **Stay in the linear region.** Large inputs hit saturation and you'll fit a model of the saturation
- **Validate on different data** than you fitted to — the same discipline as [[ai-ml/02-ml-engineer/04-model-evaluation/README|any model fitting]]
- **An identified model is only valid over the range you excited.** Extrapolation is guessing

## Standard forms

Two you should recognise instantly, because most plants approximate one of them.

**First order:**

$$G(s) = \frac{K}{\tau s + 1}$$

$K$ is the DC gain, $\tau$ the **time constant** — the response reaches 63% in $\tau$, and 98% in $4\tau$. Thermal systems, simple RC circuits, motor speed.

**Second order:**

$$G(s) = \frac{K\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$

$\omega_n$ is the **natural frequency**, $\zeta$ the **damping ratio**. Everything mechanical with mass and compliance. These two parameters determine the entire character of the response — the subject of the next note.

---

## Related
- [[engineering/02-control-theory/03-time-response|Time Response]] — what these poles produce
- [[engineering/02-control-theory/05-stability-and-root-locus|Stability and Root Locus]] — the characteristic equation
- [[engineering/02-control-theory/08-state-space|State Space]] — the alternative representation
- [[engineering/02-control-theory/README|Control theory map]]
