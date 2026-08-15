# Actuators and Motion

**[Beginner]** — Motors, drivers, gearing, and the current draw that makes power design suddenly matter.

## The choice

**Actuator selection determines what your robot can do more than any software decision.** An undersized motor cannot be fixed in firmware.

| Type | Control | Feedback | Typical use |
|---|---|---|---|
| **Brushed DC** | voltage/PWM → speed | add your own encoder | cheap drive wheels, hobby |
| **Brushless (BLDC)** | commutated phases | Hall sensors or sensorless | drones, e-bikes, modern arms |
| **Stepper** | step pulses → discrete position | usually none (open loop) | 3D printers, CNC, positioning |
| **RC servo** | PWM pulse width → angle | internal, hidden | hobby arms, small joints |
| **Smart servo** (Dynamixel) | packet protocol | position, speed, load, temp | education, research arms |

## Brushed DC

The simplest thing that moves.

**Voltage roughly sets speed; current roughly sets torque.** The two relations worth carrying:

$$\tau = K_t\,i \qquad\qquad V = iR + K_e\omega$$

The second is why a motor draws **stall current** when held still: $\omega = 0$ means no back-EMF, so the only thing limiting current is the winding resistance, which is small. **Stall current is often 10–20× the running current**, and it's what melts drivers and browns out your logic supply.

**Controlled by PWM through an H-bridge** — four switches giving forward, reverse, brake and coast.

**What bites:**

- **Brushes wear out.** Finite life, and they throw electrical noise
- **Inrush and stall current.** Spec the driver for stall, not for nominal. **Current-limit in hardware if you can**
- **Back-EMF spikes.** A motor is an inductor; switching it off produces a voltage spike. Flyback diodes, and keep motor wiring away from signal wiring
- **A motor is a noise source.** Separate power rails, generous decoupling, and a common ground star point. → [[hardware/01-electricity|Electricity]]

**The single commonest beginner failure is powering motors from the microcontroller's supply.** The MCU browns out on the first stall, resets, and the fault looks like a software bug. Separate supplies, common ground.

## Brushless

Better in almost every way, and more complicated to drive.

**No brushes** — the commutation is done electronically, by an ESC energising three phases in sequence. Higher efficiency, higher power density, much longer life.

**Sensored** uses Hall effect sensors for rotor position — smooth from zero speed, needed for anything that must produce torque at standstill (a robot joint, a wheel on a hill).

**Sensorless** infers position from back-EMF, which doesn't exist at zero speed. **Fine for propellers, bad for joints** — a sensorless BLDC has no reliable low-speed torque, which is exactly what a robot arm needs.

**Field-oriented control (FOC)** is the modern way to drive them: transform the three phase currents into torque-producing and flux-producing components and control those directly. **Smooth torque, high efficiency, precise control at all speeds.** Available now on cheap hardware (ODrive, SimpleFOC, VESC), which is why hobby-level robot joints got dramatically better in the last decade.

## Steppers

**Move in discrete steps** — typically 1.8° (200 per revolution), and microstepping subdivides further.

**The appeal: position control with no encoder.** Count the steps you sent and you know where you are — that's why 3D printers and CNC machines use them, and why they're cheap to integrate.

**The catch, and it's a big one: that's open loop.** Push too hard, accelerate too fast, or hit an obstacle, and the motor **skips steps silently**. The controller believes it's at position 100 while the machine is at 94, and nothing reports the discrepancy. → [[engineering/02-control-theory/01-what-control-theory-is|Open loop vs closed loop]]

**Also:**

- **Torque falls off sharply with speed.** Steppers are strong slow and weak fast
- **They draw full current even at standstill**, so they run hot and waste power
- **Microstepping gains smoothness, not accuracy.** 1/16 microstepping does not give you 16× the positional accuracy — friction and detent torque dominate well before that

**Closed-loop steppers** (a stepper plus an encoder plus a servo controller) fix the skipping problem and are worth the small premium on anything that matters.

## Servos

**RC servos** — a DC motor, gearbox, potentiometer and controller in one box. Command an angle with a PWM pulse width (1–2 ms), and the internal loop holds it.

*Trivially easy, and you get no feedback out.* You command 90° and have no idea whether it got there, or whether it's straining. Fine for hobby, unacceptable where it matters.

**Smart servos** (Dynamixel, LX-16A, Feetech) talk a packet protocol over a serial bus and **report position, speed, load, voltage and temperature**. Daisy-chainable, individually addressable. **This is the right choice for a first real arm** — the difference between "I told it to go there" and "it's there, drawing 300 mA, and it's warm" is enormous when debugging.

## Gearing

$$\text{Output torque} = \tau_{motor} \times N \times \eta \qquad \text{Output speed} = \frac{\omega_{motor}}{N}$$

**Motors are fast and weak; robots need slow and strong.** Almost every joint has a gearbox, and the reduction is usually 50:1 to 300:1.

| Type | Backlash | Efficiency | Note |
|---|---|---|---|
| **Spur** | moderate | high | cheap, noisy |
| **Planetary** | low–moderate | high | compact, high torque, common |
| **Harmonic drive** | **near zero** | moderate | precision arms; expensive |
| **Cycloidal** | low | high | high ratio, high shock tolerance |
| **Worm** | low | **low** (~50%) | **self-locking** — holds without power |
| **Belt/cable** | low | high | moves the motor mass off the joint |

**Backlash is the one that ruins control.** Free play between gear teeth means the output doesn't move when you reverse direction — until it does, suddenly. **It's a hard nonlinearity, it cannot be tuned away, and it causes limit cycles in a position loop.** → [[engineering/02-control-theory/13-nonlinear-and-modern-control|Nonlinear Control]]

Which is why precision arms use harmonic drives despite the cost, and why a cheap gearbox caps your achievable accuracy no matter how good your controller is.

**Two more things worth knowing:**

**Reflected inertia scales as $N^2$.** A high reduction makes the load feel enormously heavier to the motor, which is good for holding a load and bad for backdrivability.

**Backdrivability matters for safety.** A worm gear self-locks — it holds position with no power, which is great for a lift and terrible for a collaborative arm, because a human cannot push it out of the way. **Non-backdrivable joints and humans are a bad combination.** → [[robotics/14-safety-and-real-time|Safety]]

## Drivers

The layer between logic and power, and the thing that burns out.

**H-bridge** for brushed DC (L298N is the classic teaching part and is genuinely poor — old bipolar design, ~2 V dropped, gets hot; DRV8833/TB6612 are strictly better for small motors). **ESC** for brushless. **Stepper drivers** (A4988, TMC-series — the Trinamic parts are dramatically quieter).

**What to check before buying:**

- **Continuous *and* peak current rating.** The headline number is usually peak
- **Voltage range**, with margin for back-EMF spikes
- **Current sensing**, if you want torque control or collision detection
- **Thermal protection and overcurrent limiting** — a driver that shuts down beats one that fails short
- **Logic level** — 3.3 V vs 5 V, and whether it's tolerant

## Power

**The part that's easy to underestimate and hard to retrofit.**

Budget for **stall**, not for nominal. Six joints stalling simultaneously is a real scenario — it's what happens when the arm hits something.

**Battery chemistry:**

| | Energy density | Note |
|---|---|---|
| **LiPo** | high | high discharge, needs a balance charger, fire risk if abused |
| **Li-ion (18650)** | high | safer, lower discharge rate, cheap in packs |
| **LiFePO4** | moderate | very safe, long life, heavier |
| **NiMH / SLA** | low | cheap, heavy, mostly obsolete |

**Never charge or discharge lithium cells outside their spec, and use a protection/BMS board.** This is the one place in robotics where a mistake starts a fire.

**Separate the rails.** Motor power and logic power on different regulators, joined at a single ground point. A motor stalling should not reset your controller.

**And check your wire gauge.** 20 A through a thin wire is a heater, and voltage drop over a long run to a distant joint is real.

## From command to motion

Tying it together — the chain from "move there" to actual movement:

```
 trajectory → joint setpoints → [POSITION LOOP] → velocity cmd
                                       ↓
                              [VELOCITY LOOP] → current cmd
                                       ↓
                              [CURRENT LOOP] → PWM → motor
```

**Three nested loops, each faster than the one outside it** — typically 100 Hz / 1 kHz / 10–20 kHz. That's [[engineering/02-control-theory/04-pid-control|cascade control]], and it's how essentially every robot joint is driven. The inner loops absorb disturbances and linearise the actuator before the outer loop ever sees them. → [[robotics/09-robot-control|Robot Control]]

**The physical limits your planner must respect:**

- **Maximum torque** — sets acceleration
- **Maximum speed** — sets traverse time
- **Thermal limits** — you can exceed rated torque briefly, not continuously
- **Joint limits** — mechanical hard stops, and hitting one at speed damages things

**A trajectory that ignores these isn't a trajectory, it's a wish.** → [[robotics/10-motion-planning|Motion Planning]]

---

## Related
- [[robotics/09-robot-control|Robot Control]] — the loops that drive these
- [[hardware/01-electricity|Electricity]] — power, current, and why motors are noisy
- [[hardware/04-microcontrollers|Microcontrollers]] — PWM, timers, and what generates these signals
- [[robotics/README|Robotics map]]
