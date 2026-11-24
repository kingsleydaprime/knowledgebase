---
id: 126ae950-2150-427e-be0f-b8415c8ae56d
---

# Modelling 2: Transfer Functions of Electrical Circuits

Electrical circuits get their transfer functions straight from impedances: each component becomes an expression in $s$, and circuit rules you already know do the rest.

## Before you start
<!-- bite: 82b492bf-20df-473a-84ed-01a7810da005 -->

You should have read [[control-theory/03-modelling-1|03 — Modelling 1: From Physics to Transfer Functions]], and know Ohm's law and Kirchhoff's voltage law (the voltages around a loop add to zero).

After this lesson you will be able to:

1. write the impedance of a resistor, inductor and capacitor in $s$;
2. find a circuit's transfer function with a voltage divider or mesh analysis and Cramer's rule;
3. find the transfer function of inverting and non-inverting op-amp circuits;
4. explain loading, and why two cascaded RC stages aren't two RC transfer functions multiplied.

## What this lesson covers
<!-- bite: c9e10d86-c978-43af-abd1-932a81e5f416 -->

Lesson 03 built the car's transfer function from a differential equation. For circuits there's a quicker road: write each component as an **impedance** in $s$, and treat it like a resistor. Then voltage dividers, loop equations and op-amp formulas give the transfer function directly, with no differential equation in sight.

## The kid version
<!-- bite: 1fc4b386-1400-4d6d-a77c-e24efc67e36d -->

A water pipe resists flow the same whether the water is steady or sloshing. A narrow pipe with a heavy flywheel pump resists sloshing more than steady flow; a stretchy balloon in the line passes sloshing easily but blocks steady flow. Impedance is a component's resistance that depends on how fast the signal wiggles, and $s$ stands for that wiggle speed.

**Where the analogy stops working.** Pipes don't shift the timing of the flow. Impedances do: an inductor or capacitor delays the current relative to the voltage, which is why impedances are complex numbers, not just bigger or smaller resistances.

## Impedances
<!-- bite: 3cc02f80-2f27-4415-b4bd-f26b581762eb -->

Starting from rest, Laplace turns each component's law into "voltage = impedance × current":

| Component | Law in time | Impedance $Z(s) = V(s)/I(s)$ |
| --- | --- | --- |
| Resistor $R$ | $v = Ri$ | $R$ |
| Inductor $L$ | $v = L\,di/dt$ | $Ls$ |
| Capacitor $C$ | $i = C\,dv/dt$ | $1/(Cs)$ |

Impedances in **series add**; in **parallel**, their reciprocals add. From here, every rule for resistors works.

## The RLC circuit
<!-- bite: 7c8028eb-5863-4d0b-ba65-e08406a19f3a -->

A source $V$ drives $R$, $L$ and $C$ in series; the output is the capacitor voltage $V_C$. The current is $I = V/(Ls + R + 1/(Cs))$, and $V_C = I/(Cs)$. Divide:

$$\frac{V_C(s)}{V(s)} = \frac{1/(Cs)}{Ls + R + 1/(Cs)} = \frac{1}{LCs^2 + RCs + 1}$$

That's the voltage divider rule, $V_{out}/V_{in} = Z_{out}/Z_{total}$, and it matches lesson 03's differential equation.

With $L = 1$ H, $C = 0.25$ F and $R = 1$ Ω: $\dfrac{1}{0.25s^2 + 0.25s + 1} = \dfrac{4}{s^2 + s + 4}$. So $\omega_n = 2$ rad/s and $\zeta = 1/(2 \times 2) = 0.25$: a wobbly circuit, 44% overshoot (lesson 13).

## Mesh analysis: two loops
<!-- bite: c4620982-786a-433b-8287-ad4aaf6e13d1 -->

When the circuit has more than one loop, write Kirchhoff's voltage law for each **mesh current**, and solve the equations with **Cramer's rule**. Take the circuit from the textbook's example 2 (Nise's example 2.10): a source $V$, resistor $R_1$ and inductor $L$ in loop 1; the inductor shared with loop 2, which also has $R_2$ and $C$.

1. Loop 1: $(R_1 + Ls)I_1 - LsI_2 = V$.
2. Loop 2: $-LsI_1 + \left(Ls + R_2 + \dfrac{1}{Cs}\right)I_2 = 0$.

The shared inductor appears in both, with a minus sign off the diagonal. In matrix form, $\begin{bmatrix}R_1 + Ls & -Ls \\ -Ls & Ls + R_2 + 1/(Cs)\end{bmatrix}\begin{bmatrix}I_1 \\ I_2\end{bmatrix} = \begin{bmatrix}V \\ 0\end{bmatrix}$.

## Mesh analysis: Cramer's rule
<!-- bite: 6132cf59-5944-47ba-82b7-ee9ddac4b54c -->

Cramer's rule: replace column 2 of the matrix by the right-hand side, take the determinant, and divide by the matrix's own determinant $\Delta$:

$$I_2 = \frac{\begin{vmatrix}R_1 + Ls & V \\ -Ls & 0\end{vmatrix}}{\Delta} = \frac{LsV}{\Delta}$$

With every component equal to 1 ($R_1 = R_2 = 1$ Ω, $L = 1$ H, $C = 1$ F), $\Delta = (1 + s)(s + 1 + 1/s) - s^2 = (2s^2 + 2s + 1)/s$. Predict before reading on: what's $I_2/V$?

$$\frac{I_2(s)}{V(s)} = \frac{s}{\Delta} = \frac{s^2}{2s^2 + 2s + 1}$$

Two zeros at the origin: the capacitor blocks steady current, so $I_2$ settles to zero after a step.

## Op-amps
<!-- bite: bd51adc9-ad0f-4a36-b0b5-4baf096d0fbb -->

An **operational amplifier** has huge gain, draws almost no input current, and in negative feedback keeps its two inputs at the same voltage. Those facts give two formulas, with input impedance $Z_1$ and feedback impedance $Z_2$:

1. **Inverting**: $\dfrac{V_o}{V_i} = -\dfrac{Z_2}{Z_1}$.
2. **Non-inverting**: $\dfrac{V_o}{V_i} = 1 + \dfrac{Z_2}{Z_1}$.

Op-amps are how analogue controllers are built. Put a resistor $R_2$ in series with a capacitor $C$ as the feedback impedance of an inverting amplifier with input resistor $R_1$: $Z_2 = R_2 + 1/(Cs)$, so

$$\frac{V_o}{V_i} = -\frac{R_2 + 1/(Cs)}{R_1} = -\left(\frac{R_2}{R_1} + \frac{1}{R_1Cs}\right)$$

A **PI controller** (lesson 17), with $K_p = R_2/R_1$ and $K_i = 1/(R_1C)$, and a sign flip a second inverter removes.

## Loading: why stages don't just multiply
<!-- bite: 87395b41-25f8-41c1-a2f0-5ddd6800af85 -->

Two identical RC low-pass stages in a row, each $1/(RCs + 1)$. Is the whole thing $1/(RCs + 1)^2$? Predict, then check.

No. The second stage draws current from the first, changing the first stage's output: the stages **load** each other. Writing the two mesh equations properly, with $R = C = 1$:

$$\frac{V_o}{V_i} = \frac{1}{s^2 + 3s + 1}, \qquad \text{not} \quad \frac{1}{(s+1)^2} = \frac{1}{s^2 + 2s + 1}$$

The poles move from $-1, -1$ to $-0.38$ and $-2.62$. Remember this one: **block diagrams multiply blocks in series only when each block's output isn't affected by what it feeds.** Put a buffer (a non-inverting op-amp with gain 1) between the stages and the product becomes exact.

## Common pitfalls
<!-- bite: 80a6e726-7fe8-4789-ab71-eb298c94c25f -->

1. **Forgetting impedance of a capacitor is $1/(Cs)$.** Not $Cs$.
2. **Dropping the minus sign on shared components** in mesh equations.
3. **Multiplying loaded stages.** Write the full circuit equations or add a buffer.
4. **Forgetting the inverting amplifier's minus sign.**

## Check your understanding
<!-- bite: 758697f4-53f3-49f5-ac6b-e2d2bd9e4b0c -->

Try each one before you open the answer.

1. <!-- q: mcq id="5f3b9c20" -->
   A resistor $R$ and capacitor $C$ are in series, and the output is taken across the resistor. What is $V_R/V_i$?

   - [ ] $1/(RCs + 1)$
   - [x] $RCs/(RCs + 1)$
   - [ ] $RCs$
   - [ ] $1/(RCs)$

   <details><summary>Answer</summary>

   Voltage divider: $R/(R + 1/(Cs)) = RCs/(RCs + 1)$, a high-pass filter.

   </details>

2. <!-- q: exact id="a9d27e41" answer="0.5" accept="1/2" -->
   A series RLC circuit has $L = 1$ H, $C = 1$ F and $R = 1$ Ω, with the output across $C$: $1/(s^2 + s + 1)$. What is its damping ratio?

   <details><summary>Answer</summary>

   $\omega_n = 1$ and $2\zeta\omega_n = 1$, so $\zeta = 0.5$.

   </details>

3. <!-- q: exact id="0c6e8b13" answer="-5" accept="−5" -->
   An inverting op-amp has a 10 kΩ input resistor and a 50 kΩ feedback resistor. What is its gain?

   <details><summary>Answer</summary>

   $-Z_2/Z_1 = -50/10 = -5$.

   </details>

4. <!-- q: gap id="e1b47d96" answers="4;10" -->
   A PI controller is built as an inverting op-amp with input resistor $R_1 = 25$ kΩ and feedback $R_2 = 100$ kΩ in series with $C = 4$ μF. Its gains are $K_p = $ ___ and $K_i = 1/(R_1C) = $ ___ per second.

   <details><summary>Answer</summary>

   $K_p = 100/25 = 4$; $K_i = 1/(25000 \times 4 \times 10^{-6}) = 10$.

   </details>

5. <!-- q: open id="7d20c3a5" -->
   Why isn't the transfer function of two cascaded RC stages equal to the product of the two single-stage transfer functions?

   <details><summary>Answer</summary>

   The second stage draws current from the first, so the first stage's output voltage is lower than it would be unloaded. Its single-stage transfer function assumed nothing was connected. Multiplying blocks is only valid when each output is unaffected by what it drives, for example with a buffer amplifier between them.

   </details>

## Before moving on
<!-- bite: 8b350e63-7c4e-4333-8b7f-af7d590a2cc0 -->

You can find any linear circuit's transfer function from impedances. **Next:** [[control-theory/05-modelling-3|05 — Modelling 3: Translational Mechanical Systems]], the same idea for masses, springs and dampers.

## Related
<!-- bite: faebc59a-c3a9-4e8f-909b-f73f194b7e87 -->

- [[hardware/01-electricity|Hardware: Electricity]]
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 027f0ba7-bea3-44aa-8fe0-749906c0569e -->

**Level:** Intermediate. **Covers:** impedances, the voltage divider and the RLC circuit, mesh analysis with Cramer's rule, inverting and non-inverting op-amps, an op-amp PI controller, and loading.

**Where it sits:** lesson 4 of 58, part 2 of the modelling lessons.

**Source:** the author's course notes, A. M. Hussein, *Control Engineering*, Benha University: chapter 3 (sections 2 and 3, examples 1 to 4) and chapter 6 (section 6); worked circuits after N. S. Nise, *Control Systems Engineering*. Numbers checked in `scripts/diagrams/control_theory.py`.
