# What Control Theory Is

**[Beginner → Intermediate]** — Why feedback is the single most important idea in engineering, what it costs, and the vocabulary the rest of the track uses.

**Source:** `[reference]` — see [[engineering/README|the domain note]].

## The problem

You want a system to do something. A motor to hold 3000 rpm. A quadcopter to stay level. A furnace at 200 °C. A car at the speed limit.

You can't just command it, because:

- **The model is wrong.** You never know the plant exactly
- **Disturbances happen.** Wind, load changes, friction, someone opening a door
- **Things drift.** Components age, temperature changes, batteries sag
- **Some systems are unstable.** A quadcopter or an inverted pendulum falls over without continuous correction

**Control theory is the mathematics of making a system behave despite all of that.**

## Open loop vs closed loop

**Open loop** — decide the input from a model, apply it, hope.

```
   reference  →  [ CONTROLLER ]  →  [ PLANT ]  →  output
```

A toaster. A washing-machine cycle. A stepper motor commanded to move 200 steps.

Cheap, simple, and it **cannot correct anything it doesn't measure**. If the bread is frozen, the toaster doesn't know. If the stepper stalls, the controller keeps counting.

**Closed loop (feedback)** — measure the output, compare to what you wanted, act on the difference.

```
                   ┌──────────────── disturbance
                   ▼
 r →(+)→ e → [ CONTROLLER ] → u → [ PLANT ] → y →┬→
     ▲−                                          │
     └──────────── [ SENSOR ] ←──────────────────┘
```

The vocabulary, which is used everywhere:

| Symbol | Name | Meaning |
|---|---|---|
| $r$ | reference / setpoint | what you want |
| $y$ | output / process variable | what you got |
| $e = r - y$ | **error** | the difference — the thing the controller acts on |
| $u$ | control input / actuation | what the controller commands |
| $d$ | disturbance | what the world does to you |

**The whole of classical control is: what function should turn $e$ into $u$?**

## What feedback buys you

Four things, and they're the reason feedback is everywhere from cell biology to central banking:

**1. Disturbance rejection.** The controller doesn't need to know a disturbance happened — the error tells it.

**2. Insensitivity to model error.** This is the deep one. With high loop gain $L$, the closed-loop response is

$$\frac{y}{r} = \frac{L}{1 + L} \approx 1 \quad\text{when } L \gg 1$$

**and that's true almost regardless of what $L$ is.** Double the plant gain and the closed-loop response barely moves. You get accuracy from feedback that the components themselves don't have — which is exactly why an op-amp with a wildly variable open-loop gain of $10^5$–$10^6$ produces a precise, predictable amplifier once you close the loop. → [[hardware/01-electricity|Hardware: Electricity]]

**3. Stabilising unstable plants.** A quadcopter is unstable open-loop. So is an inverted pendulum, a modern fighter aircraft, and a Segway. Feedback makes them flyable.

**4. Shaping dynamics.** You can make a sluggish system fast, or an oscillatory one damped, without changing the hardware.

## What feedback costs

The honest side, and it's why control is a *design* discipline rather than a recipe:

**1. It can make a stable system unstable.** The central risk. Feedback plus delay plus gain equals oscillation — the shower where you overcorrect the temperature and oscillate hot/cold forever. → [[engineering/02-control-theory/05-stability-and-root-locus|Stability]]

**2. It amplifies sensor noise.** The controller cannot distinguish a real error from measurement noise, and acts on both. High gain means noisy actuation.

**3. It needs a sensor.** Which costs money, adds delay, and can fail — and a failed sensor in a feedback loop is worse than no feedback, because the controller confidently acts on garbage.

**4. Performance and robustness trade off.** Making a loop fast makes it less tolerant of model error. **This is not an engineering limitation you can design away** — it's a mathematical constraint. → [[engineering/02-control-theory/07-nyquist-and-robustness|Nyquist and Robustness]]

> The **waterbed effect**: push sensitivity down at one frequency and it necessarily rises at another. Bode's integral theorem makes this precise, and it's the most important thing separating control theory from tuning by feel.

## Feedforward

Often forgotten, and often the better half of a solution.

**Feedforward** acts on a *measured disturbance or a known reference* before the error appears:

```
        ┌──→ [ FEEDFORWARD ] ──┐
        │                      ▼
 r ─────┴─(+)→[ FEEDBACK ]→(+)→ [ PLANT ] → y
           ▲−                          │
           └──────────────────────────┘
```

- **Feedback** is reactive: it needs an error to exist before it can correct it
- **Feedforward** is predictive: no error required, but it depends entirely on model accuracy

**Use both.** Feedforward does the bulk of the work using the model; feedback cleans up what the model got wrong. That combination is standard in motion control, where the trajectory is known in advance — a CNC machine or a robot arm computes most of its torque from the planned motion and uses feedback only for the residual.

## Requirements

What "good control" means, concretely — and these become the specification you design against:

**Stability.** Non-negotiable. Bounded input gives bounded output.

**Steady-state accuracy.** Does $y \to r$? The residual is **steady-state error**.

**Speed.** *Rise time* to reach the target, *settling time* to stay within a band of it.

**Overshoot.** How far past the target does it go? Often the binding constraint — an elevator that overshoots by 10% is unacceptable regardless of how fast it is.

**Robustness.** Does it still work when the plant isn't quite what you modelled?

**Actuator limits.** Every real actuator saturates. A design demanding 500 N from a 100 N motor is not a design. → [[engineering/02-control-theory/04-pid-control|PID Control]]

These conflict. **Faster response means more overshoot and less robustness.** Control design is choosing where on that trade to sit, deliberately.

## SISO and MIMO

**SISO** — single input, single output. One actuator, one sensor. Most of classical control, and most of this track.

**MIMO** — multiple inputs and outputs, usually **coupled**: changing one input affects several outputs. A quadcopter (four motors, six degrees of freedom), a distillation column, a chemical reactor.

Coupling is what makes MIMO genuinely harder — you can't tune loops independently, because each one disturbs the others. Classical transfer-function methods struggle; **state-space methods handle MIMO naturally**, which is the main reason they exist. → [[engineering/02-control-theory/08-state-space|State Space]]

## The two traditions

Worth knowing why the field looks like two subjects:

**Classical control (1930s–1950s)** — transfer functions, frequency domain, Bode and Nyquist plots, root locus, PID. Developed for telephone amplifiers and WWII fire control. **Graphical, intuitive, SISO, and enormously practical.** It's what most working engineers use.

**Modern control (1960s–)** — state space, time domain, matrices. Developed for aerospace, where MIMO and optimality mattered. **Handles MIMO, nonlinearity, and optimality; less intuitive.** Kalman filtering and LQR come from here, and the Apollo guidance computer is the canonical application.

**Neither replaced the other.** Classical methods give better insight into robustness and are easier to tune by hand; modern methods handle complexity classical methods can't express. A practising engineer uses both, and this track covers classical first because the intuition transfers.

## Where control shows up

Not just machines:

- **Mechanical** — robots, vehicles, aircraft, machine tools → [[robotics/README|robotics]]
- **Electrical** — power supplies, PLLs, motor drives, op-amp circuits
- **Process** — chemical plants, refineries, HVAC
- **Biology** — homeostasis, glucose regulation, gene expression. Feedback loops evolved long before anyone wrote them down
- **Economics** — central bank interest-rate policy is a feedback controller with a very long delay, which is exactly why it's hard
- **Computing** — TCP congestion control is a distributed feedback loop, and autoscaling is a controller with a slow, noisy plant → [[foundations/networking/08-congestion-control|Congestion Control]]

That last comparison is worth taking seriously. Autoscaling on CPU usage has all the classical problems: sensor delay (metrics lag), actuator delay (instances take minutes to boot), and it oscillates for exactly the reasons this track explains.

## Reading this track

**Notes 02–07 are classical control** and build strictly in order. **08–11 are state space.** 12–13 are implementation and what lies beyond.

**Prerequisites:** complex numbers, differential equations, Laplace transforms (introduced in note 02), and linear algebra for the state-space half. Calculus throughout.

**The most practically valuable note is 04 (PID)** — it's what you'll actually implement, and the tuning material is the part people most often get wrong.

---

## Related
- [[engineering/02-control-theory/02-modelling-and-transfer-functions|Modelling and Transfer Functions]] — how to describe a plant
- [[engineering/02-control-theory/04-pid-control|PID Control]] — the controller you'll actually use
- [[engineering/01-continuum-mechanics/README|Continuum Mechanics]] — the other engineering track
- [[robotics/README|Robotics]] — where this gets applied
- [[engineering/02-control-theory/README|Control theory map]]
