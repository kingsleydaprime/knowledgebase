---
id: 9c9446b0-595b-40ba-ad06-422d8007489e
---

# Modelling 2: Mathematical Models From First Principles

A mathematical model can be built from physical laws, written as balance equations plus the relations that link their variables.

## Before you start
<!-- bite: 6da6ffd2-90d2-4aff-8fe5-fdab290bf97e -->

You should have read [[systems-simulation/04-modelling-1|04 — Modelling 1]].

After this lesson you will be able to:

1. state the fundamental axiom of mathematical modelling;
2. tell first-principles modelling from system identification, and explain a model's validity range;
3. build a simple model from a balance equation and a constitutive relation, and say what linearisation does.

## What a mathematical model is
<!-- bite: a149cfad-4bdc-46d4-9de9-6f8dbdcd4467 -->

Lesson 04 chose a model to fit a purpose. This lesson writes one down as equations. A **mathematical model** describes the properties of a system's parts and how they interact, using mathematical language. Most of this lesson comes from a process control chapter, so treat it as supporting material: learn the ideas, and don't expect heavy equations in a simulation exam.

## The fundamental axiom
<!-- bite: 4d67cc9a-2696-4d34-9d77-8c9fee131028 -->

The **fundamental axiom** of mathematical modelling, also called the modelling hypothesis, says: the model of a component describes its behaviour as an independent entity, plus how it is connected to the other components.

In plain words: you can take one component out, literally or in your head, study it on its own, and then plug it back in through its connections. That is what makes large models buildable piece by piece.

## Across and through variables
<!-- bite: 83a8361d-bb89-462d-a157-950063359697 -->

Many kinds of system share the same structure, with two kinds of variable.

| System | Across variable | Through variable |
| --- | --- | --- |
| Mechanical | Velocity | Force |
| Fluid | Pressure | Flow rate |
| Electrical | Voltage | Current |

An **across** variable is measured between two points (the voltage across a resistor). A **through** variable passes through a component (the current through it).

Two-terminal components then fall into three kinds:

1. **Dissipaters:** power is lost in them, such as a resistor turning current into heat.
2. **Delay types and accumulators:** they store energy and give it back, so over a long time no net power is lost, such as a capacitor or a spring.
3. **Sources or drivers:** their variable is fixed whatever else happens, such as a battery holding its voltage.

## First principles or system identification
<!-- bite: 48ee12ca-8df1-46b4-ba42-01b45f065787 -->

There are two ways to get a model:

1. **First principles:** derive it from physical laws, such as conservation of mass or Newton's laws.
2. **System identification:** measure the real system and fit a model to the data.

Often both are combined: the structure of the model comes from physics, and the uncertain numbers in it come from measurements.

**Every model has a limited validity range,** even one built on physical laws. A model from system identification is especially risky outside the range of the experiment that produced it. Lesson 33 calls this the model's bounds of validity.

## The two kinds of relationship
<!-- bite: 860c3694-8b87-4df8-afd0-675d388b0c7d -->

First-principles models use two kinds of relationship.

1. **Conservation laws.** A **flow balance** says: accumulation per unit time = inflow − outflow + production. An **effort balance** says: change per unit time = forcing − loading. Newton's laws and Kirchhoff's voltage law are effort balances.
2. **Constitutive relationships.** These are static relations between variables, true at every instant: Ohm's law, a valve's characteristic, Bernoulli's law, the ideal gas law.

## The procedure
<!-- bite: 85910fac-e3c4-42bb-8d09-2978161da19b -->

1. Write the balance equations.
2. Add constitutive relationships to link the variables.
3. Check the units: every added term must have the same unit, and both sides of each equation must match.

## Example: an RC low-pass filter
<!-- bite: de7c04d0-8a7a-4198-b32b-d2514b555460 -->

A resistor R feeds a capacitor C. The input voltage is $u_{\text{in}}$ and the output, across the capacitor, is $u_{\text{out}}$.

1. **Balance:** the current into the capacitor charges it, so $C\,\dfrac{du_{out}}{dt} = i$.
2. **Constitutive:** Ohm's law across the resistor gives $i = \dfrac{u_{in} - u_{out}}{R}$.
3. **Combine:** $RC\,\dfrac{du_{out}}{dt} + u_{out} = u_{in}$.

That is a first-order linear differential equation. The product RC has the unit of time (seconds), so both sides are in volts, and the units check out.

## Linearisation
<!-- bite: 1763883b-d6a3-4059-94c8-6aac6ed37de0 -->

Real models are often nonlinear, which makes them hard to solve. If the system works near a known operating point, you can replace the nonlinear equation with a linear one using a **first-order Taylor series** about that point: keep the value and the slope, and drop the curvature.

If the system moves over a wide range, use several linear models, one for each part of the range. This is the validity range idea again: a linear model is only trusted near the point it was built around.

## Common pitfalls
<!-- bite: 00f42e81-b79c-4ae4-aedf-b3155f79e42c -->

1. **Skipping the unit check.** A term with the wrong unit is the fastest sign of a mistake.
2. **Using a fitted model outside its data.** A system-identification model knows nothing beyond the range it was measured on.
3. **Trusting a linear model far from its operating point.** Linearisation is local.

We now have models. Next lesson turns to *simulation* models specifically: the five types, and the components every simulation model is built from.

## Check your understanding
<!-- bite: bb8b030c-b864-4ee1-9de8-bb1e135e4a7f -->

Try each one before you open the answer.

1. <!-- q: mcq id="89b32498" -->
   A tank gains 12 litres per minute from a pipe, loses 7 litres per minute through a drain, and produces nothing. By the flow balance, how fast does the water in it change?

   - [ ] It falls by 5 litres per minute
   - [x] It rises by 5 litres per minute
   - [ ] It rises by 19 litres per minute
   - [ ] It doesn't change

   <details><summary>Answer</summary>

   It rises by 5 litres per minute: accumulation = inflow − outflow + production = 12 − 7 + 0.

   </details>

2. <!-- q: exact id="be8743c3" answer="2" -->
   In an RC filter, R = 2,000 Ω and C = 1,000 µF (0.001 F). What is the time constant RC, in seconds?

   <details><summary>Answer</summary>

   2 seconds: 2,000 × 0.001. RC has the unit of time, which is what makes the equation $RC\,du_{out}/dt + u_{out} = u_{in}$ balance in volts.

   </details>

3. <!-- q: gap id="88abae73" answers="first principles|first-principles;system identification" -->
   A model derived from physical laws is built from ___. A model fitted to measurements of the real system comes from ___.

   <details><summary>Answer</summary>

   First principles, then system identification. Often both are combined: structure from physics, numbers from data.

   </details>

4. <!-- q: mcq id="f8c34d57" -->
   Which of these is a constitutive relationship rather than a conservation law?

   - [ ] Inflow − outflow = accumulation
   - [ ] Newton's second law as a force balance
   - [x] Ohm's law, $V = IR$
   - [ ] Kirchhoff's voltage law

   <details><summary>Answer</summary>

   Ohm's law, a static relation between voltage and current. The others are balances.

   </details>

5. <!-- q: open id="b18f6d83" -->
   A pump model was fitted to data measured between 20% and 60% of full speed. An engineer uses it to predict behaviour at 95%. What is wrong?

   <details><summary>Answer</summary>

   The model is being used outside its validity range. A system-identification model only describes the range it was measured on, and the pump may behave quite differently near full speed. Measure in that range, or build that part of the model from first principles.

   </details>

6. <!-- q: open id="013e9d0c" -->
   What does linearisation do, and when is it safe?

   <details><summary>Answer</summary>

   It replaces a nonlinear equation with a linear one using a first-order Taylor series about an operating point, keeping the value and slope and dropping the curvature. It is safe only near that point; over a wide range, use several linear models.

   </details>

## Before moving on
<!-- bite: 08bcb8b1-8783-4866-9555-39a2c7947e2e -->

You can state the fundamental axiom, build a small model from a balance and a constitutive relation, and say where a model can be trusted. **Next:** [[systems-simulation/06-types-and-components-of-simulation-models|06 — Types and Components of Simulation Models]].

## Related
<!-- bite: 72edd460-76d8-4c7e-a32e-a7e24dfbc8e7 -->

- [[systems-simulation/index|Systems simulation map]]
- [[control-theory/index|Control Theory]]: where models like the RC filter are used to design controllers.

## About this lesson
<!-- bite: 8df019d9-94ed-4a3b-bf29-432cd58d611e -->

**Level:** Beginner to intermediate. **Covers:** the fundamental axiom, across and through variables, the three kinds of two-terminal component, first principles versus system identification, conservation and constitutive relations, the procedure, the RC filter and linearisation.

**Where it sits:** lesson 05 of 38, part 2 of 2 on modelling.

**Source:** the author's own SSG 418 and SSG 517 study notes, section C (from the process control chapter). The tank and pump examples are added for this lesson.
