---
id: a5fed056-e9d8-4b06-a2b0-0c0f26dea0f0
---

# Nonlinear Design 1: Describing Functions and Gain Scheduling

A describing function predicts limit cycles caused by hard nonlinearities, and gain scheduling handles smooth ones.

## Before you start
<!-- bite: 0aee4055-fd09-45ea-994d-5f0e52c8cef4 -->

You should have read [[control-theory/50-limit-cycles-1|50 — Limit Cycles 1: Stable, Unstable and Semi-Stable]] and [[control-theory/27-nyquist-1|27 — Nyquist 1: The Nyquist Criterion]].

After this lesson you will be able to:

1. say what a describing function is and the assumption it rests on;
2. compute the describing function of an ideal relay and use it to predict a limit cycle's size and frequency;
3. explain relay auto-tuning;
4. describe gain scheduling and its two caveats.

## What this lesson covers
<!-- bite: d61e538c-bae1-4722-b62c-a48750fd2d55 -->

Lessons 46 to 55 *analysed* nonlinear systems. Now we design for them, starting with the two tools engineers reach for most. The first predicts when a loop with a hard nonlinearity, like saturation or a relay, will oscillate on its own. The second is by far the most common way real nonlinear plants are controlled.

## The kid version
<!-- bite: 5d77277b-fe7b-43ce-92d3-15a84ffbb541 -->

A shop's thermostat clicks the heater fully on or fully off, nothing in between. The room temperature ends up swinging gently up and down around the setpoint for ever. A describing function predicts how big that swing is and how fast it goes, by pretending the on-off switch is an amplifier whose gain depends on how big the swing is.

**Where the analogy stops working.** The "gain" trick only works if the room smooths out the heater's sharp on-off pulses into something close to a smooth wave. If the plant doesn't smooth, the prediction is wrong.

## The describing function
<!-- bite: 4672e93c-cd9f-46d0-b255-9f87d464252a -->

Feed a nonlinearity a sine wave of amplitude $A$. The output is periodic but not sinusoidal. Keep only its **fundamental** (the first Fourier term, at the input's frequency), and divide by $A$. That ratio, possibly complex, is the **describing function** $N(A)$: an equivalent gain that depends on amplitude.

The assumption: the rest of the loop is **low-pass**, so the harmonics the nonlinearity creates get filtered out and only the fundamental comes back around. Most plants with enough roll-off satisfy it.

For an **ideal relay** switching between $+M$ and $-M$, the output is a square wave whose fundamental has amplitude $4M/\pi$, so

$$N(A) = \frac{4M}{\pi A}$$

Big inputs see a small gain; small inputs a large one. That's what makes relays oscillate.

## Predicting a limit cycle
<!-- bite: cb438407-6a64-40e4-9e21-ba0ef6d87da2 -->

With the nonlinearity replaced by $N(A)$, the loop's characteristic equation is $1 + N(A)L(j\omega) = 0$, so a limit cycle can exist where

$$L(j\omega) = -\frac{1}{N(A)}$$

Plot $L(j\omega)$ (a Nyquist plot, lesson 27) and the curve $-1/N(A)$ on the same diagram: **each intersection is a predicted limit cycle**, giving its frequency from $L$ and its amplitude from $N$.

Worked: put an ideal relay with $M = 1$ in front of our loop $L = 1/(s(s+1)(s+2))$. For a relay, $-1/N(A) = -\pi A/4$, which runs along the negative real axis. $L(j\omega)$ crosses that axis at $-1/6$ when $\omega = \sqrt2$ (lesson 27). Setting $\pi A/4 = 1/6$:

$$A = \frac{4}{6\pi} = 0.212, \qquad \omega = 1.414 \text{ rad/s}$$

So the loop settles into an oscillation of amplitude 0.21 at 1.41 rad/s, a period of 4.44 s.

## Relay auto-tuning
<!-- bite: 179bf88a-ebe8-4168-9538-af635593380d -->

Look at what just happened. The relay made the loop oscillate at exactly the frequency where $L$'s phase is −180°, and the amplitude told us $|L|$ there: $|L| = 1/N(A) = \pi A/(4M)$. Those are the two numbers Ziegler–Nichols needs (lesson 18): the ultimate gain is $K_u = 1/|L| = 4M/(\pi A)$, and the period is $T_u$.

So instead of turning a P controller up until the loop nearly goes unstable, **swap the controller for a relay for a minute, measure the oscillation, and compute the gains.** That's **relay auto-tuning** (Åström and Hägglund), and it's the "autotune" button on most industrial PID controllers. It's safe because the relay keeps the oscillation small and controlled.

Here: $K_u = 4/(\pi \times 0.212) = 6$ and $T_u = 4.44$ s, matching lesson 19's Routh result exactly.

## Other describing functions
<!-- bite: 98ba5a64-5a74-430d-b598-37a1257dc795 -->

1. **Saturation** with slope $k$ up to $\pm a$: for $A \le a$, $N = k$ (it's linear); for $A > a$, $N(A) = \dfrac{2k}{\pi}\left[\sin^{-1}\dfrac{a}{A} + \dfrac{a}{A}\sqrt{1 - \dfrac{a^2}{A^2}}\right]$, falling towards 0 as $A$ grows. For $k = 1$, $a = 1$, $A = 2$: $N = 0.609$.
2. **Dead zone** and **backlash** have their own formulas; backlash's is complex, because it delays the output, which is why gear play so often causes hunting.

And the crossing geometry also says whether the predicted cycle is stable (the amplitude returns after a nudge) or not. Remember: it's an approximation, good for the practical question "my loop is oscillating; why, how big, and how fast?"

## Gain scheduling
<!-- bite: ff37da1d-3e42-4a17-a6fb-46896579c33c -->

Now the most-used nonlinear technique of all. **Linearise the plant at several operating points, design a linear controller for each, and switch or interpolate between them using a measured variable.** That variable is the **scheduling variable**.

It's standard in aircraft (scheduled on speed and altitude, because a plane handles completely differently at 200 km/h and 900 km/h), in engine control (on speed and load), and in process plants. It's simple, it works, and it reuses everything from the linear lessons.

Back to lesson 07's car with real drag, $2.5v^2$: its linear drag is 50 N per m/s at 10 m/s but 100 at 20 m/s, so its time constant halves. A gain-scheduled cruise control keeps a table of PI gains against speed, so the loop behaves the same in town and on the motorway.

## Gain scheduling: the caveats
<!-- bite: 0a5b175b-181c-421b-a5dd-d1d3199ebaa0 -->

1. **Stability between the design points isn't guaranteed** by the designs at the points. Check in between, by simulation or analysis.
2. **The scheduling variable must change slowly** compared with the loop's dynamics. Schedule too fast and the switching itself can destabilise the loop.

Despite both, gain scheduling handles most real nonlinearity, and it should be the first thing you try. Lesson 57 covers the methods for when it isn't enough.

## Common pitfalls
<!-- bite: afe7f828-c0b3-4063-830a-8661a024d2d5 -->

1. **Using a describing function on a plant with no roll-off.** The harmonics don't get filtered and the prediction fails.
2. **Forgetting the minus sign in $-1/N(A)$.** The intersection is with $-1/N$, not $N$.
3. **Scheduling on a fast-changing variable.** It must vary slowly relative to the loop.
4. **Designing only at the ends of the operating range.** Check the points in between.

## Check your understanding
<!-- bite: 8ca9bb3b-8fac-41b4-9137-57510169b858 -->

Try each one before you open the answer.

1. <!-- q: exact id="4c2e9b71" answer="0.42441" sigfigs="3" -->
   A relay switching between $\pm2$ drives the loop $L = 1/(s(s+1)(s+2))$, whose Nyquist plot crosses the negative real axis at $-1/6$. Using $\pi A/(4M) = 1/6$, what is the oscillation amplitude $A$?

   <details><summary>Answer</summary>

   $A = 4M/(6\pi) = 8/(6\pi) = 0.424$. Doubling the relay output doubles the amplitude.

   </details>

2. <!-- q: exact id="b8f3d016" answer="1.2732" sigfigs="3" -->
   What is the describing function $N(A) = 4M/(\pi A)$ of a relay with $M = 1$ at $A = 1$?

   <details><summary>Answer</summary>

   $4/\pi = 1.27$.

   </details>

3. <!-- q: mcq id="1a5d7c48" -->
   Relay auto-tuning measures a loop's oscillation with a relay in place of the controller. Which two numbers does it give?

   - [x] The ultimate gain $K_u$ and the oscillation period $T_u$
   - [ ] The plant's DC gain and dead time
   - [ ] The phase margin and gain margin
   - [ ] The time constant and damping ratio

   <details><summary>Answer</summary>

   $K_u = 4M/(\pi A)$ and $T_u$, exactly what Ziegler–Nichols tuning needs.

   </details>

4. <!-- q: mcq id="e70c3b92" -->
   A flight controller is gain-scheduled on airspeed. Which is the main risk?

   - [ ] Airspeed is too hard to measure
   - [x] Stability between the design speeds isn't guaranteed, and fast airspeed changes can destabilise the switching
   - [ ] The linear designs can't use PID
   - [ ] Gain scheduling only works for first-order plants

   <details><summary>Answer</summary>

   Those are the two caveats: check between the design points, and schedule on a variable that changes slowly relative to the loop.

   </details>

5. <!-- q: open id="5d91a6e3" -->
   What assumption does the describing-function method make about the rest of the loop, and why is it needed?

   <details><summary>Answer</summary>

   That the linear part is low-pass. The nonlinearity turns a sine into a distorted wave full of harmonics; the method keeps only the fundamental, which is accurate only if the linear part filters the harmonics out before they come back around the loop.

   </details>

## Before moving on
<!-- bite: 117e9ff0-26ab-4954-a37e-af85082f92db -->

You can predict a limit cycle with a describing function and explain gain scheduling. **Next:** [[control-theory/57-nonlinear-design-2|57 — Nonlinear Design 2: Feedback Linearisation, Sliding Mode and Adaptive Control]].

## Related
<!-- bite: c7cfdf6c-9eec-42a9-95e4-e4ba6570c793 -->

- [[control-theory/18-pid-control-2|18 — PID Control 2: Tuning and Implementation]]: Ziegler–Nichols, which relay auto-tuning feeds.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 261216ff-71ca-439d-b405-4f9d2ef77d9d -->

**Level:** Advanced. **Covers:** the describing function, the relay's $N(A)$, predicting a limit cycle on our running loop, relay auto-tuning, saturation's describing function, and gain scheduling with its caveats.

**Where it sits:** lesson 56 of 58, part 1 of 2 on nonlinear design.

**Source:** `[reference]`, assembled from standard control texts. Numbers checked in `scripts/diagrams/control_theory.py`.
