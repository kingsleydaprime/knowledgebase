---
id: ff2f90ab-38af-4735-9a95-5e2ecdadde95
---

# Safety and Risk

Safety in design means finding every way a product could hurt someone, rating how risky each one is, and removing or controlling the risk in the right order.

## Before you start
<!-- bite: 9e0312be-2d0a-4549-b695-9090a8f9cf23 -->

You should know FMEA ([[engineering-design-and-prototyping/27-failure-mode-and-effects-analysis|27 — Failure Mode and Effects Analysis]]) and reliability ([[engineering-design-and-prototyping/28-reliability|Reliability]]).

After this lesson you will be able to:

1. tell a hazard from a risk, and safety from reliability;
2. rate risks with a likelihood-severity matrix;
3. reduce risk using the hierarchy of controls and fail-safe design.

## What safety and risk are
<!-- bite: efa2ab58-dfc2-4204-9fdf-36574edff7f6 -->

Lesson 19 listed public health and safety as a duty of every design. This lesson gives the method.

1. A **hazard** is something that could cause harm: the spinning blade of a blender.
2. A **risk** is how likely that harm is, combined with how bad it would be: the chance that someone's fingers meet the blade, and the injury if they do.

You can't remove every hazard (a blender needs a blade), but you can bring the risk down to a level people accept. The running example is a **kitchen blender**.

## Safety is not reliability
<!-- bite: ab54a7bc-b759-46ad-b2d0-cfac1347eb64 -->

The two are easy to confuse:

1. **Reliability** asks whether the product keeps doing its job (lesson 28).
2. **Safety** asks whether it hurts anyone, whether it works or not.

A blender that runs perfectly for ten years while the lid is off is reliable and unsafe. A blender that refuses to start when the lid is loose is less "available", but safe. Good design often deliberately lets a product **fail safe**: when something goes wrong, it stops in a harmless state.

## Finding the hazards
<!-- bite: 3eeb5d29-f662-4177-9859-c75e2a9cfcb4 -->

Hazards are found systematically, not by luck:

1. **Go through the energy sources:** moving parts, electricity, heat, pressure, stored springs, chemicals.
2. **Go through the life cycle** (lesson 18): making it, using it, cleaning it, repairing it, misusing it, throwing it away.
3. **Ask "what if?"** for every user, including children and people who don't read instructions.
4. **Use FMEA** (lesson 27) for failures of the product's own parts, and **HAZOP** (a structured "what if this goes more, less, or the wrong way?") for processes and plants.

For the blender: the blade (cuts), the motor (overheats), mains power (shock), a jar knocked off the base (spills hot liquid), and a child pressing the button.

## Rating risk
<!-- bite: 061e60b2-4bf4-446d-b203-1828ce257fcc -->

Rate each hazard's **likelihood** and **severity**, each from 1 to 5, and multiply them:

$$\text{risk score} = \text{likelihood} \times \text{severity}$$

![A five-by-five risk matrix with likelihood from rare to almost certain on one axis and severity from negligible to catastrophic on the other; each cell shows likelihood times severity, coloured green for low scores, yellow for medium, orange for high and red for very high](images/ed-risk-matrix.svg)

## What the score means
<!-- bite: 2791dcc5-86f3-4899-a14e-fd3d5fd337c9 -->

A typical banding (each organisation sets its own):

| Score | Level | What to do |
| --- | --- | --- |
| 1 to 4 | Low | Accept; keep watching |
| 5 to 9 | Medium | Reduce if reasonably practicable |
| 10 to 16 | High | Must reduce before release |
| 20 to 25 | Very high | Stop; redesign |

Fingers reaching the blade with the lid off: likelihood 3 (possible), severity 4 (serious injury), so 3 × 4 = **12, high**. It must be reduced.

The aim is to bring every risk **as low as reasonably practicable (ALARP)**: keep reducing it until the cost of reducing it further is grossly out of proportion to the benefit.

## The hierarchy of controls
<!-- bite: 89caa7f9-65b2-45bd-9529-e67fb6cb49a8 -->

Controls are tried in a fixed order, from most to least effective:

1. **Eliminate** the hazard: design it out. A hand-held stick blender for some jobs has no open jar to reach into.
2. **Substitute** something less hazardous: a lower-voltage motor, a blunter blade shape for soft foods.
3. **Engineering controls:** guards and **interlocks** that make the hazard unreachable. The blender won't run unless the lid is locked on the jar.
4. **Administrative controls:** warnings, labels, instructions and training. "Keep fingers away from the blade."
5. **Personal protective equipment (PPE):** gloves or goggles. For a consumer product, rarely an option.

A warning label is near the bottom for a reason: it relies on people reading and obeying it. Product safety standards (ISO 12100 for machinery) put it the same way: **inherently safe design first, then safeguards, then information for the user.**

## Fail-safe and the blender's result
<!-- bite: cda815ba-5787-40d3-b6a5-066f6e665851 -->

After applying the hierarchy, rate the risk again: the **residual risk**. With the lid interlock, fingers can't reach a moving blade, so likelihood falls from 3 to 1: 1 × 4 = **4, low**.

The interlock itself must **fail safe**: if its switch breaks, the blender must refuse to run, not run anyway. That is why interlock switches are designed so that a broken spring or a cut wire leaves the circuit open.

## Common pitfalls
<!-- bite: 1b55414d-65cf-4d9c-b3d1-70c824c62d07 -->

1. **Starting with a warning label.** Design the hazard out first; labels are a last resort.
2. **Forgetting misuse.** People will use the product in ways you didn't intend. Design for that.
3. **Rating risk once.** Re-rate after each control to get the residual risk.
4. **Assuming a reliable product is safe.** They are different questions.

The design should now be safe and reliable on paper. Next lesson proves it: verification, validation and testing.

## Check your understanding
<!-- bite: 09acea8e-ca78-4502-b33d-cdc5629c8d39 -->

Try each one before you open the answer.

1. <!-- q: gap id="dcea6231" answers="hazard;risk" -->
   A hot surface on a kettle is a ___. The chance of someone being burned by it, combined with how bad the burn would be, is the ___.

   <details><summary>Answer</summary>

   Hazard, then risk.

   </details>

2. <!-- q: exact id="9ba9d26e" answer="15" -->
   A hazard on a grass cutter is rated likelihood 3 and severity 5. What is its risk score?

   <details><summary>Answer</summary>

   15: 3 × 5. On the lesson's banding that is high, so it must be reduced before release.

   </details>

3. <!-- q: mcq id="83692e50" -->
   Which control is highest in the hierarchy of controls?

   - [ ] A warning sticker on the guard
   - [ ] Gloves supplied with the machine
   - [x] A design with no exposed blade at all
   - [ ] Training for the operator

   <details><summary>Answer</summary>

   Eliminating the hazard by design. Then come substitution, engineering controls such as guards, administrative controls such as stickers and training, and finally PPE.

   </details>

4. <!-- q: open id="127acb27" -->
   A paper shredder's opening lets a child's fingers reach the cutters; the risk is rated likelihood 3, severity 4. Propose an engineering control, and rate the residual risk.

   <details><summary>Answer</summary>

   For example, make the feed slot too narrow for fingers, or add a flap that cuts power when pushed (an interlock). Fingers can then rarely reach the cutters, so likelihood drops to about 1 while severity stays 4, giving a residual risk of 4, low. Any sensible control with a re-rating is fine.

   </details>

5. <!-- q: mcq id="599287b4" -->
   A microwave keeps working perfectly with its door open. What is true?

   - [ ] It is unreliable
   - [x] It is reliable but unsafe
   - [ ] It is safe because it works
   - [ ] It is fail-safe

   <details><summary>Answer</summary>

   Reliable (it keeps doing its job) but unsafe (it can expose people to microwaves). A door interlock that fails safe is the fix.

   </details>

6. <!-- q: open id="389c8771" -->
   What does it mean for an interlock to "fail safe", and why does it matter?

   <details><summary>Answer</summary>

   If the interlock itself fails, for example a broken spring or cut wire, the machine stops or refuses to start, rather than running unguarded. It matters because the interlock is the main protection; if its failure let the machine run, a single broken part would expose the user to the hazard without anyone knowing.

   </details>

## Before moving on
<!-- bite: 59883d3a-886a-4de5-9b5f-5078571b1743 -->

You can tell hazard from risk and safety from reliability, rate risks, apply the hierarchy of controls and design for fail-safe behaviour. **Next:** [[engineering-design-and-prototyping/30-verification-validation-and-testing|30 — Verification, Validation and Testing]]: proving the design meets its requirements and suits its users.

## Related
<!-- bite: 5f4159f4-c2c4-4161-8606-66c622563eba -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[systems-engineering/08-risk-and-failure-analysis|Risk and Failure Analysis]] in systems engineering.

## About this lesson
<!-- bite: 30105f83-4030-4c4a-acbb-b2bc0d3f991b -->

**Level:** Intermediate. **Covers:** hazards and risks, safety versus reliability, finding hazards, the likelihood-severity risk matrix, ALARP, the hierarchy of controls, residual risk and fail-safe design.

**Where it sits:** lesson 29 of 36, in part 8 (making it safe and proving it works).

**Source:** written from general safety engineering knowledge, because the SSG 532 lecture notes only name public health and safety as a design consideration; safety and risk are on the official course outline. The risk banding is a typical one; real organisations set their own. The diagram comes from `scripts/diagrams/engineering_design.py`.
