# Control Theory

## What control theory is

**Control theory is the maths of making a system do what you want, automatically, by constantly measuring it and correcting it.**

Think of a room thermostat. It measures the temperature, compares it with what you set, and switches the heating on or off to close the gap. That's a **feedback loop**: measure, compare, correct, over and over. The same idea keeps a car's cruise control at a steady speed, a drone level in the wind, a robot arm on its path, and a rocket upright.

The surprise is how easily it goes wrong. Correct too hard and the system overshoots and swings back and forth; correct too slowly and it never quite gets there; and delays in measuring can make a well-meant loop shake itself apart. Control theory gives you the tools to predict that and design loops that are both fast and steady.

Software engineers meet it more than they realise: how the internet slows senders down when it's busy, how cloud services add servers under load (autoscaling), and how rate limiting works are all feedback loops with the same problems.

## What you'll be able to do

By the end you will be able to:
- describe a system with equations, and predict how it will respond;
- tune a PID controller, the most common controller in the world, and implement it so it works on real hardware;
- tell whether a feedback loop will be steady or start swinging, and how much safety margin it has;
- describe systems with several inputs and outputs using matrices;
- estimate things you can't measure directly, by combining a model with noisy sensors (the Kalman filter);
- design controllers by choosing what to optimise;
- turn a design into code that runs on a microcontroller.

## Where to start

**Before you start:** [[mathematics/06-calculus/02-calculus-1/01-preview/01-preview|calculus]], including derivatives. Notes 08–11 also need [[mathematics/04-linear-algebra/index|linear algebra]].

Read in order. Notes 02–07 are the classical methods and build on each other; 08–11 use matrices; 12–13 are about real implementation and more advanced methods.

### Getting oriented

1. [[control-theory/01-what-control-theory-is|What Control Theory Is]]: acting without measuring versus feedback, the standard names for each part of a loop, and what feedback gives you and costs you.

### Classical control

2. [[control-theory/02-modelling-and-transfer-functions|Modelling and Transfer Functions]]: turning physics into equations, and a shorthand (the transfer function) that makes them easy to work with.
3. [[control-theory/03-time-response|Time Response]]: how a system responds to a sudden change: how fast, how much it overshoots, and whether it settles at the right value.
4. [[control-theory/04-pid-control|PID Control]]: the note that matters most. What each part of a PID controller does, how to tune it, and four details that make it work on real hardware.
5. [[control-theory/05-stability-and-root-locus|Stability and Root Locus]]: telling whether a loop will settle or blow up, and how that changes as you turn up the gain.
6. [[control-theory/06-frequency-response|Frequency Response]]: studying a system by how it responds to slow and fast wiggles, and the limits on how fast a loop can be.
7. [[control-theory/07-nyquist-and-robustness|Nyquist and Robustness]]: checking how much a loop can tolerate before it fails, and why the usual safety numbers can look fine on a fragile design.

### Using matrices (state space)

8. [[control-theory/08-state-space|State Space]]: describing a system by a list of numbers that capture its current condition, which handles many inputs and outputs at once.
9. [[control-theory/09-controllability-observability-and-pole-placement|Controllability, Observability and Pole Placement]]: can you steer every part of the system, can you see every part, and if so, how to give it any behaviour you want.
10. [[control-theory/10-observers-and-kalman|Observers and Kalman Filters]]: estimating what you can't measure by combining a model with noisy sensors.
11. [[control-theory/11-optimal-control-and-lqr|Optimal Control and LQR]]: designing a controller by stating what "good" means and letting the maths find the best one.

### Real implementation and beyond

12. [[control-theory/12-digital-control|Digital Control]]: running a controller as code on a microcontroller, and the problems that only show up on real hardware.
13. [[control-theory/13-nonlinear-and-modern-control|Nonlinear and Modern Control]]: systems the simple methods don't cover, and where machine learning fits in.

## Practice

- [[control-theory/projects|Projects]]: hands-on tasks with a clear "done when".
- **The best first experiment:** a motor that follows a knob. Close the loop yourself, turn up the gain, and watch it start to swing. Note 04 becomes concrete in an afternoon.

## Key ideas to remember

1. **Feedback is measure, compare, correct.** It handles disturbances and imperfect models, and it can also cause swinging. → [[control-theory/01-what-control-theory-is|01]]
2. **Every real PID needs three fixes:** stop the I term building up while the output is maxed out, smooth the D term, and take D from the measurement, not the error. → [[control-theory/04-pid-control|04]]
3. **Delay is the enemy.** Even a short delay limits how fast a loop can safely react. → [[control-theory/03-time-response|03]]
4. **Cancelling an unstable part of a system hides it rather than fixing it.** The output looks perfect while the inside runs away. → [[control-theory/09-controllability-observability-and-pole-placement|09]]
5. **Uneven timing is worse than slow timing.** A steady delay you can design around; one that varies changes your loop every step. → [[control-theory/12-digital-control|12]]
6. **A good model beats a clever controller.** Most control failures are really modelling failures. → [[control-theory/13-nonlinear-and-modern-control|13]]

## Related

- [[robotics/index|Robotics]]: the biggest user of this course.
- [[hardware/index|Hardware & Embedded]]: where controllers run.
- [[networking/08-congestion-control|Congestion Control]]: a feedback loop running across the internet.
- [[digital-signal-processing/index|Digital Signal Processing]]: the closely related maths of signals and filters.

---

## About this course

- **Size:** 13 notes, about 21,000 words, written in August 2026.
- **Where it came from:** reference sources, not from tuning real systems. The hardware-specific warnings come from other people's experience.
