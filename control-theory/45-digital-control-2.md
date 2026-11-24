---
id: 6496423e-cfac-459b-913d-9faef2cf17a9
---

# Digital Control 2: Discretising and Implementing a Controller

Discretising turns a continuous controller into a difference equation, and implementing it well is mostly about timing, number formats and limits.

## Before you start
<!-- bite: f5e5f644-2e65-44a3-ae92-8ccabba4e4d7 -->

You should have read [[control-theory/44-digital-control-1|44 — Digital Control 1: Sampling and the z-Transform]], and know the discrete stability test $|z| < 1$.

After this lesson you will be able to:

1. discretise a controller with forward Euler, backward Euler and Tustin, and say which can go unstable;
2. turn a discrete transfer function into a difference equation, and write a PI controller as one;
3. list the fixed-point and timing rules for a real control loop;
4. diagnose the common digital-control failures, and handle networked loops.

## What this lesson covers
<!-- bite: 4ad2c75a-53ac-4000-8472-c7009ceb7d83 -->

You designed $C(s)$ in continuous time. The processor needs $C(z)$, and then a line of code. There are several ways to swap $s$ for something in $z$, and they're not equally safe. After that comes the code itself, and the list of things that go wrong on real hardware, in roughly the order you'll meet them.

## The kid version
<!-- bite: 2fbc2607-8878-49ee-850c-96706c499a54 -->

Translating a recipe from cups to grams: there's more than one way to convert, and a sloppy conversion can ruin the cake. Most conversions are close enough for a cupcake but not for a wedding cake. Discretising is the same: a crude method works at a high sample rate and wrecks things at a low one.

**Where the analogy stops working.** A bad recipe conversion gives a bad cake. A bad discretisation can turn a stable controller into an *unstable* one, which is far worse than slightly off.

## Four ways to swap s for z
<!-- bite: 5b713b98-274c-4bf3-98f5-8e8fabfaca28 -->

1. **Forward Euler**: $s \to \dfrac{z-1}{T}$. Simplest. **It can turn a stable controller unstable**, because it maps part of the stable left half plane outside the unit circle. Only acceptable at very high sample rates.
2. **Backward Euler**: $s \to \dfrac{z-1}{Tz}$. Always maps stable to stable. Slightly distorts the response; a safe default for simple controllers.
3. **Tustin** (bilinear): $s \to \dfrac{2}{T}\cdot\dfrac{z-1}{z+1}$. **The one to use.** It maps the whole left half plane exactly onto the unit disc, so stability is kept both ways, and it's accurate. Its one flaw is **frequency warping** near the Nyquist frequency, fixed at one chosen frequency by **prewarping**: replace $2/T$ with $\omega_0/\tan(\omega_0T/2)$.
4. **Zero-order hold** (`c2d`): the exact conversion for a *plant* driven through a hold (lesson 31). Use ZOH for the plant, Tustin for the controller.

## The methods compared on one pole
<!-- bite: 773d99c1-dc8c-4bc5-a820-4ef21369a699 -->

Take a fast, stable controller pole at $s = -30$, sampled every $T = 0.1$ s. The exact mapping is $z = e^{-3} = 0.050$. Predict before reading on: which method breaks?

1. **Forward Euler**: $z = 1 + sT = 1 - 3 = -2$. Outside the unit circle: **unstable**.
2. **Backward Euler**: $z = 1/(1 - sT) = 1/4 = 0.25$. Stable.
3. **Tustin**: $z = (1 + sT/2)/(1 - sT/2) = -0.5/2.5 = -0.2$. Stable.

The pole was too fast for the sample rate ($|sT| = 3$), and forward Euler couldn't cope. The general advice: **discretise the plant with ZOH and design directly in discrete time** when sampling is slow; designing continuous and converting works when $f_s$ is 30 or more times the bandwidth.

## Difference equations
<!-- bite: 8a828e99-6346-446e-8ff5-1ee39f09b45e -->

A discrete controller becomes code by reading $z^{-1}$ as "the previous sample":

$$C(z) = \frac{b_0 + b_1z^{-1} + b_2z^{-2}}{1 + a_1z^{-1} + a_2z^{-2}}$$

$$u[k] = b_0e[k] + b_1e[k-1] + b_2e[k-2] - a_1u[k-1] - a_2u[k-2]$$

Multiply, add, shift the history along. That's the whole controller.

**Use second-order sections.** A high-order filter written as one big difference equation is numerically fragile, and gets worse with order. Factor it into a chain of second-order pieces ("biquads"), as in [[digital-signal-processing/06-digital-filters|digital filters]].

## The car's PI controller as code
<!-- bite: f55e89ac-3117-431e-b773-5a502ac8ddc9 -->

Lesson 18's car used $C(s) = K_p + K_i/s$ with $K_p = 500$, $K_i = 100$, at $T = 0.1$ s. Apply Tustin to the integral part: $K_i/s \to K_i\tfrac{T}{2}\cdot\tfrac{z+1}{z-1}$. Multiply out and read off the delays:

$$u[k] = u[k-1] + \Big(K_p + \tfrac{K_iT}{2}\Big)e[k] + \Big(-K_p + \tfrac{K_iT}{2}\Big)e[k-1]$$

$$u[k] = u[k-1] + 505\,e[k] - 495\,e[k-1]$$

This is the **velocity form** from lesson 18: it computes the *change* in output, so there is no separate integral state to wind up, and clamping $u[k]$ itself gives anti-windup for free.

## Fixed point
<!-- bite: 174d5996-a930-49db-84f6-9d32407964f0 -->

On a processor with no floating-point unit, numbers are integers with an implied binary point, called **Q-format**; Q15 means 15 bits after the point.

1. **Multiplying doubles the word length.** Multiply two Q15 numbers into a 32-bit accumulator, then shift back.
2. **Watch for overflow, and saturate.** Wrapping round turns a large positive command into a large negative one, which on a motor is spectacular.
3. **Keep the integrator wide.** It adds up tiny numbers for a long time and loses precision first. Give it extra fractional bits.

If you have a floating-point unit, use floats: single precision is plenty for control, and the debugging time saved is worth more than the cycles.

## The control loop
<!-- bite: d48f9a98-c676-44f7-8e3b-c296809764ba -->

```text
timer interrupt at a fixed rate:
    y = read_sensor()          # ADC
    u = controller_update(y)   # the difference equation
    u = clamp(u, u_min, u_max)
    write_actuator(u)          # DAC or PWM
```

1. **Read and write at the same points in every cycle.** Moving them changes the effective delay.
2. **Keep the computation short and predictable**: no memory allocation, no unbounded loops, no blocking input or output. Log to a buffer and let a lower-priority task send it.
3. **Cut the sensor-to-actuator delay.** If the update is long, compute the part that depends on the new reading first, output it at once, then do the rest. That saves nearly a whole sample of delay.

## What actually goes wrong
<!-- bite: 9bcf06c2-aea2-4ced-9fd4-72e2bf110b0d -->

The failures, roughly in the order you'll meet them:

1. **Sampling too slowly.** Fine in simulation, oscillating on hardware. Check the hold's $\omega_cT/2$ (lesson 44).
2. **No anti-aliasing filter.** A mysterious slow oscillation with no source. Look for a real vibration near a multiple of $f_s$.
3. **Timing jitter.** A loop without a real-time schedule, a `delay()` call, an interrupt that sometimes runs long. Symptom: behaviour that changes when unrelated code changes.
4. **Integral windup.** As common as ever in digital form. → [[control-theory/17-pid-control-1|17 — PID Control 1: The Three Terms]]
5. **Derivative of a quantised signal.** A row of spikes. Filter it, or estimate speed with an observer instead of differencing. → [[control-theory/36-observers|36 — Observers]]
6. **Unhandled saturation.** The controller must know the real limits: PWM at 100%, current limits, heat derating.
7. **Numerical drift** in a long-running sum. Use a wider accumulator.

## Networked and distributed control
<!-- bite: 3a774661-e579-4502-a879-2121c45aa7f2 -->

More and more loops close over a network, which breaks assumptions: the delay varies, packets drop, and there's no shared clock. The standard responses:

1. **Timestamp everything**, and use the timestamp, not the arrival order.
2. **Design for the worst-case delay**, not the average.
3. **A Kalman filter handles missing readings naturally**: skip the update, keep predicting (lesson 37).
4. **Event-triggered control**: send only when the error crosses a threshold, not on a fixed schedule. It cuts traffic a lot, with provable stability.
5. **Fail safe on loss of signal.** Decide in advance what the actuator does when the network drops; "hold the last value forever" should be a choice, not an accident.

The parallel with distributed systems is real: a cloud autoscaler is a networked control loop with a slow, noisy plant and minutes of actuator delay. → [[architecture/04-distributed-systems/index|Distributed Systems]]

## Common pitfalls
<!-- bite: 58d7eac7-578a-4fce-b331-73312049d95a -->

1. **Forward Euler at a low sample rate.** It can make a stable controller unstable.
2. **One big high-order difference equation.** Split into second-order sections.
3. **Integer overflow that wraps.** Always saturate.
4. **Discretising the plant with Tustin.** Use ZOH for the plant.

## Check your understanding
<!-- bite: 46ee6cdf-7172-4ea8-86b7-9baaf642b56b -->

Try each one before you open the answer.

1. <!-- q: exact id="2f6b9e40" answer="-0.5" accept="−0.5" -->
   A pole at $s = -15$ is discretised by forward Euler with $T = 0.1$ s, $z = 1 + sT$. Where does it land?

   <details><summary>Answer</summary>

   $z = 1 - 1.5 = -0.5$. Inside the unit circle, so still stable, though far from the exact $e^{-1.5} = 0.22$.

   </details>

2. <!-- q: exact id="c8d1a5e3" answer="0.1429" sigfigs="3" -->
   Same pole, $s = -15$, $T = 0.1$ s, by Tustin: $z = (1 + sT/2)/(1 - sT/2)$. Where does it land?

   <details><summary>Answer</summary>

   $(1 - 0.75)/(1 + 0.75) = 0.25/1.75 = 0.143$.

   </details>

3. <!-- q: gap id="7a4e2b16" answers="202;198" -->
   A PI controller with $K_p = 200$, $K_i = 40$ is discretised by Tustin at $T = 0.1$ s: $u[k] = u[k-1] + $ ___ $e[k] - $ ___ $e[k-1]$.

   <details><summary>Answer</summary>

   $K_p + K_iT/2 = 202$ and $K_p - K_iT/2 = 198$.

   </details>

4. <!-- q: mcq id="e91c4f07" -->
   Which method should you use to discretise a *plant* model driven through a DAC?

   - [ ] Forward Euler
   - [ ] Tustin
   - [x] Zero-order hold
   - [ ] Backward Euler

   <details><summary>Answer</summary>

   Zero-order hold: it's exact for a plant whose input is held constant between samples, which is what a DAC does.

   </details>

5. <!-- q: open id="0d5a3b78" -->
   A motor controller works until someone adds logging code, then starts to buzz. Name the likely cause and the fix.

   <details><summary>Answer</summary>

   Timing jitter: the logging makes some control cycles run late, so the sample time varies and the effective gains change every sample. Run the controller from a fixed-rate timer interrupt and move logging to a lower-priority task that writes from a buffer.

   </details>

## Before moving on
<!-- bite: 1c2fd35c-4964-4878-ae58-87bdc8d504cd -->

You can discretise safely, write the difference equation, and debug a real loop. That completes the linear subject. **Next:** [[control-theory/46-nonlinear-systems|46 — Nonlinear Systems]], about what happens when the plant stops being linear.

## Related
<!-- bite: 9de0779b-1d0f-44dd-8459-929f706abadf -->

- [[control-theory/18-pid-control-2|18 — PID Control 2: Tuning and Implementation]]: the car program this controller runs in.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 438cdd62-b2ad-45d3-9ab3-91e0145c4d6b -->

**Level:** Intermediate to advanced. **Covers:** forward and backward Euler, Tustin and ZOH, difference equations and second-order sections, the car's PI controller in velocity form, fixed point, the control loop, failure modes, and networked control.

**Where it sits:** lesson 45 of 58, part 2 of 2 on digital control.

**Source:** `[reference]`, assembled from standard control texts. Numbers checked in `scripts/diagrams/control_theory.py`.
