# Time Response

**[Intermediate]** — Reading a step response, the two numbers that determine everything, and the specifications you design against.

## First-order systems

$$G(s) = \frac{K}{\tau s + 1}$$

Step response:

$$y(t) = K\left(1 - e^{-t/\tau}\right)$$

```
y
K ┤        ╭────────────────────
  │      ╭─╯
  │    ╭─╯
  │  ╭─╯
  │ ╱
0 ┼╯────┬────┬────┬────┬──────→ t
  0     τ   2τ   3τ   4τ
       63%  86%  95%  98%
```

**One parameter, $\tau$, determines everything.** Reach 63% in one time constant, 98% in four. **Settling time ≈ $4\tau$** is the rule of thumb worth memorising.

No overshoot, no oscillation, ever. A first-order system cannot overshoot — which is why thermal processes and simple RC filters are so well-behaved and so slow.

## Second-order systems

$$G(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$

Two parameters, and they do completely different jobs:

- **$\omega_n$ — natural frequency.** How *fast*. Scales the time axis
- **$\zeta$ — damping ratio.** *Shape*. Determines overshoot and oscillation

The poles:

$$s = -\zeta\omega_n \pm j\omega_n\sqrt{1-\zeta^2}$$

| $\zeta$ | Poles | Response |
|---|---|---|
| $0$ | imaginary | **undamped** — oscillates forever |
| $0 < \zeta < 1$ | complex pair | **underdamped** — overshoots, then settles |
| $1$ | repeated real | **critically damped** — fastest with no overshoot |
| $> 1$ | two distinct real | **overdamped** — slow, no overshoot |

```
y
  │      ╭╮      ζ = 0.2  (oscillatory)
  │     ╱  ╲╭─╮
1 ┼────╱────╰─╰──────────
  │   ╱ ╭───────────      ζ = 0.7  (good compromise)
  │  ╱ ╱  ╭──────────     ζ = 1.0  (critical)
  │ ╱ ╱ ╱ ╱               ζ = 2.0  (sluggish)
0 ┼╯─┴─┴─┴────────────→ t
```

> **$\zeta \approx 0.7$ is the classic design target.** About 5% overshoot, fast settling, and reasonable robustness. $\zeta = 1$ has no overshoot but is *slower to settle* than $\zeta = 0.7$ — which surprises people. Critically damped is fastest to *reach* the target monotonically, not fastest to *settle within a band*.

**The geometric reading of pole location** is worth internalising, because it's what makes [[engineering/02-control-theory/05-stability-and-root-locus|root locus]] design intuitive:

```
            Im
             │    ×
             │   ╱│
             │  ╱ │ ωd = ωn√(1−ζ²)
          ωn│ ╱   │
             │╱ θ │
   ──────────┼────┼─────  Re
          −ζωn
```

- **Distance from origin** = $\omega_n$ (speed)
- **Angle from the negative real axis** = $\cos^{-1}\zeta$ (damping)
- **Horizontal distance** = $\zeta\omega_n$ (decay rate — this sets settling time)
- **Vertical distance** = $\omega_d$ (oscillation frequency)

Move a pole left → faster settling. Move it toward the real axis → less overshoot. **That's the entire vocabulary of pole placement.**

## Step response specifications

The numbers you actually design against:

$$\text{Overshoot: } M_p = e^{-\pi\zeta/\sqrt{1-\zeta^2}} \times 100\%$$

$$\text{Settling time (2\%): } t_s \approx \frac{4}{\zeta\omega_n}$$

$$\text{Rise time (10–90\%): } t_r \approx \frac{1.8}{\omega_n}$$

$$\text{Peak time: } t_p = \frac{\pi}{\omega_d}$$

The overshoot table is worth carrying:

| $\zeta$ | Overshoot |
|---|---|
| 0.3 | 37% |
| 0.5 | 16% |
| **0.7** | **4.6%** |
| 0.8 | 1.5% |
| 1.0 | 0% |

**Two things fall out of these formulas that shape how you design:**

**Overshoot depends only on $\zeta$.** Not on $\omega_n$. So you set damping to meet the overshoot spec, then set $\omega_n$ to meet the speed spec — the two requirements decouple, which is unusually convenient.

**Settling time depends on $\zeta\omega_n$**, the real part of the pole. That's why "move the poles left" means "settle faster".

## Dominant poles

Real systems are higher than second order. **The approximation that makes classical design work:**

> **Poles far to the left decay fast and contribute little. The behaviour is dominated by the poles closest to the imaginary axis.**

Rule of thumb: if other poles are **5× further left**, treat the system as second-order using the dominant pair.

```
     Im
      │  ×  ← dominant pair
  ×   │            (these determine the response)
──────┼──────  Re
  ×   │  ×
   ↑
  fast poles — negligible
```

This is why every textbook formula above, derived for a pure second-order system, applies usefully to a sixth-order plant. **It's also the first thing to check when a system doesn't behave as designed** — a neglected pole or an unmodelled delay has crept close enough to matter.

## Steady-state error

Does the output actually reach the reference? For unity feedback with loop gain $L(s)$:

$$e_{ss} = \lim_{s\to 0} \frac{s\,R(s)}{1 + L(s)}$$

The answer depends on the **system type** — the number of integrators ($1/s$ terms) in $L(s)$:

| Type | Step input | Ramp input | Parabola |
|---|---|---|---|
| **0** (no integrator) | $\dfrac{1}{1+K_p}$ | ∞ | ∞ |
| **1** (one integrator) | **0** | $\dfrac{1}{K_v}$ | ∞ |
| **2** (two integrators) | **0** | **0** | $\dfrac{1}{K_a}$ |

> **Each integrator in the loop eliminates the steady-state error to one higher order of input.** That is precisely why the **I** term in a PID controller kills steady-state error — it adds an integrator, taking the system from type 0 to type 1. → [[engineering/02-control-theory/04-pid-control|PID Control]]

And it explains a common frustration: a proportional-only controller on a plant with no natural integrator will *always* have a steady-state offset. Raising the gain shrinks it but never removes it — you need the integrator.

**Where the integrator comes from doesn't matter.** A motor position loop is naturally type 1 (velocity integrates to position), so P control alone gives zero steady-state position error. A motor *speed* loop is type 0, and needs the I term.

## Time delay

The most destructive thing you can have in a loop.

$$G_{delay}(s) = e^{-sT}$$

**Unity magnitude at every frequency, and phase lag growing without bound**: $\angle = -\omega T$ radians.

So delay costs you phase margin — the thing keeping you stable — while giving nothing back. → [[engineering/02-control-theory/06-frequency-response|Frequency Response]]

Because $e^{-sT}$ isn't rational, it's often approximated for analysis by a **Padé approximation**:

$$e^{-sT} \approx \frac{1 - sT/2}{1 + sT/2}$$

Note the numerator — that's a **right-half-plane zero**. Delay behaves like a non-minimum-phase element, with all the bandwidth limitations that implies. → [[engineering/02-control-theory/02-modelling-and-transfer-functions|RHP zeros]]

**Sources of delay in real systems**, all of which count:

- Transport lag (fluid down a pipe, material on a conveyor)
- Sensor processing and filtering
- Computation time
- **Sampling** — a zero-order hold adds an average delay of half a sample period → [[engineering/02-control-theory/12-digital-control|Digital Control]]
- Network latency, in distributed control

> **Delay is why the shower oscillates.** You adjust the tap, wait, feel no change, adjust more, and then both adjustments arrive at once. It's also why cloud autoscaling oscillates — instances take minutes to boot, so the controller keeps scaling while the previous action is still in flight.

**Smith predictor** is the classical remedy: use a model to predict what the delayed output *will* be and control against the prediction. Works well when the delay is known and constant, and badly when it isn't.

## Reading a real step response

The practical skill — extracting a model from data:

```
y │        ╭─╮___________
  │      ╭─╯ ╰
  │     ╱
  │    ╱
  │   ╱
  │__╱
  └──┬─────────────────→ t
     └─ dead time θ
```

1. **Dead time $\theta$** — the flat bit before anything happens. Pure delay
2. **Slope and time constant** — draw the maximum-slope tangent; where it crosses the final value gives $\tau$
3. **Final value ÷ step size** = DC gain $K$
4. **Overshoot** → $\zeta$ from the table above
5. **Oscillation period** → $\omega_d$, hence $\omega_n$

That gives you $G(s) = Ke^{-\theta s}/(\tau s + 1)$ or a second-order fit — enough to design a controller. **This is what Ziegler–Nichols open-loop tuning is doing**, and it's why a step test is the first thing you do to an unfamiliar plant. → [[engineering/02-control-theory/04-pid-control|PID Control]]

**The ratio $\theta/\tau$ is the single most useful number** from that test: below ~0.2 the loop is easy to control, above ~1 it's genuinely difficult and no amount of PID tuning will make it fast.

---

## Related
- [[engineering/02-control-theory/02-modelling-and-transfer-functions|Modelling and Transfer Functions]] — where poles come from
- [[engineering/02-control-theory/04-pid-control|PID Control]] — using this to tune
- [[engineering/02-control-theory/05-stability-and-root-locus|Stability and Root Locus]] — moving poles deliberately
- [[engineering/02-control-theory/README|Control theory map]]
