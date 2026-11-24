---
id: 519f2d5d-2849-48de-8efb-b6897a055e88
---

# Factor of Safety

The factor of safety is how many times stronger a part is than it needs to be for the load it will actually carry.

## Before you start
<!-- bite: 36843b45-d637-436a-9565-22653683b9d0 -->

You should know the screw jack example ([[engineering-design-and-prototyping/17-considerations-of-good-design-1|lesson 17]]) and what yield strength means ([[engineering-design-and-prototyping/18-considerations-of-good-design-2|lesson 18]]). You need simple division; a calculator helps.

After this lesson you will be able to:

1. explain why engineers design parts stronger than they need to be;
2. calculate stress, factor of safety and allowable stress;
3. say why some products need a much higher factor of safety than others.

## What a factor of safety is
<!-- bite: b8d6c9a9-a135-4992-b89b-d1ebe5089ba8 -->

Remember the screw jack designed to lift a car of up to 300 kg? What happens if someone puts it under a car that weighs 320 kg? Or the steel came out a little weaker than the supplier promised? Or the jack has rusted for five years in a car boot?

If the jack was designed to hold *exactly* 300 kg, any one of those breaks it, and the car falls on someone. So engineers design it to hold more: say 600 kg. The factor of safety is that "how many times more".

## Why we need one
<!-- bite: f6e1f77a-9139-47ed-9e7d-7b4ac0bf56d8 -->

We use a factor of safety because we're never sure about everything:

1. **Loads are uncertain.** Users overload things, and real loads include bumps and shocks.
2. **Materials vary.** Two bars of the same steel are never exactly the same strength.
3. **Manufacturing isn't perfect.** A part may come out slightly thinner, or with a tiny crack.
4. **Things get weaker over time.** Fatigue, corrosion and wear (from lesson 18) all eat away at strength.
5. **Our calculations are simplified.** The maths never captures every detail of the real part.

The factor of safety covers all of that uncertainty at once.

## Stress: the load spread over an area
<!-- bite: 232ee5fe-7a92-47fd-9d7f-8772a0301033 -->

To work out a factor of safety, we first need **stress**: how much force each bit of the material is carrying. Stress is the force divided by the area it's spread over.

$$\text{stress} = \frac{\text{force}}{\text{area}}$$

With force in newtons (N) and area in square millimetres (mm²), stress comes out in N/mm², which is the same as megapascals (MPa).

The same force is much worse on a thin rod than a thick one, because the thin rod has less area to share it. That's why stress, not force, is what breaks things.

## Calculating the factor of safety
<!-- bite: 91ebfbe3-9473-4832-9e9f-35c97e07c91f -->

The factor of safety is the stress the material can take before it fails, divided by the stress it will actually carry in use.

$$\text{factor of safety} = \frac{\text{failure stress}}{\text{working stress}}$$

For metals, the failure stress is usually the **yield strength**: the stress at which it starts to bend permanently.

It can also be written with loads: the load that would make it fail, divided by the load it carries. The jack that holds 600 kg but is used for 300 kg has a factor of safety of 600 ÷ 300 = 2.

## Worked example: the screw jack's screw
<!-- bite: 45842c2e-cc09-4ae3-aaf6-80a703948778 -->

The jack's screw carries about 3,000 N (roughly the weight of 300 kg). The thinnest part of the screw has a cross-section area of 50 mm². The steel's yield strength is 240 MPa.

**Step 1, the working stress:**

stress = 3,000 N ÷ 50 mm² = 60 MPa

**Step 2, the factor of safety:**

factor of safety = 240 MPa ÷ 60 MPa = 4

The screw could carry 4 times its working load before it starts to bend permanently. That's comfortably safe for a jack that people lie next to.

## Working backwards: allowable stress
<!-- bite: 4f1cfece-6662-4c29-8183-efbf492dfb45 -->

Often a standard or the company tells you the factor of safety to use, and you work out how much stress the part is allowed to carry. That's the **allowable stress**: the failure stress divided by the required factor of safety.

$$\text{allowable stress} = \frac{\text{failure stress}}{\text{factor of safety}}$$

Example: steel with a yield strength of 250 MPa, and a required factor of safety of 2.5.

allowable stress = 250 ÷ 2.5 = 100 MPa

So the designer must make the part big enough that its stress never goes above 100 MPa.

## How big should it be?
<!-- bite: 088eed89-0dc2-44fd-aef8-1f5ad01182b5 -->

There is no single right number. It depends on how sure you are and how bad a failure would be. Rough typical values (the real ones come from the standards for each industry):

| Situation | Typical factor of safety | Why |
| --- | --- | --- |
| Aircraft structures | About 1.5 | Every extra kilogram costs fuel, and loads and materials are tested very carefully |
| General machinery | About 2 to 3 | Loads and materials are fairly well known |
| Uncertain loads, or brittle materials | 3 to 4 or more | Less certainty, or a material that snaps without warning |
| Lift cables and lifting equipment | Around 10 or more | People's lives depend on it, and wear is hard to see |

## The trade-off
<!-- bite: 71073e00-6f14-4c65-997d-70159318f90a -->

A bigger factor of safety isn't free. It means a thicker, heavier, more expensive part. A bicycle frame with a factor of safety of 10 would be safe but far too heavy to ride (remember the lightweight requirement in lesson 22).

So the factor of safety is a trade-off between safety on one side and weight and cost on the other. The more serious the consequences of failure, and the less certain the loads, the higher it goes. It's also where the code of ethics from lesson 19 shows up in the numbers: protecting public health and safety comes first.

## Common pitfalls
<!-- bite: ecc7c4ee-3dad-4390-a311-6a4895c702e3 -->

1. **Dividing the wrong way.** Factor of safety is failure stress ÷ working stress. It should be bigger than 1; if you get less than 1, the part fails.
2. **Using force instead of stress.** Divide the force by the area first. Strength is given as a stress.
3. **Mixing units.** N ÷ mm² gives MPa. Don't mix metres and millimetres in one calculation.
4. **"Bigger is always better."** A huge factor of safety wastes material, weight and money.

## Check your understanding
<!-- bite: 057128ec-1dab-437c-b62f-a95791a82a3d -->

Try each one before you open the answer.

1. <!-- q: exact id="5c8e2f19" answer="200" accept="200 MPa" -->
   A steel rod carries a force of 20,000 N. Its cross-section area is 100 mm². What is the stress in the rod, in MPa?

   <details><summary>Answer</summary>

   20,000 ÷ 100 = 200 MPa.

   </details>

2. <!-- q: exact id="a3d06b74" answer="1.5" accept="3/2" -->
   A part has a yield strength of 300 MPa and carries a working stress of 200 MPa. What is its factor of safety?

   <details><summary>Answer</summary>

   300 ÷ 200 = 1.5.

   </details>

3. <!-- q: exact id="0f7b4e82" answer="120" accept="120 MPa" -->
   A bracket is made of steel with a yield strength of 360 MPa. The standard requires a factor of safety of 3. What is the allowable stress, in MPa?

   <details><summary>Answer</summary>

   360 ÷ 3 = 120 MPa. The bracket must be sized so its stress stays below this.

   </details>

4. <!-- q: exact id="e2c95a37" answer="1200" accept="1,200|1200 kg|1,200 kg" -->
   A lifting hoist would fail at a load of 6,000 kg. It is designed with a factor of safety of 5. What is the largest load it should be used for, in kg?

   <details><summary>Answer</summary>

   6,000 ÷ 5 = 1,200 kg.

   </details>

5. <!-- q: mcq id="9b1f6d50" -->
   Which of these would need the highest factor of safety?

   - [ ] A plastic toy car
   - [ ] A racing bicycle frame
   - [x] The cable that holds a passenger lift

   <details><summary>Answer</summary>

   The lift cable. People's lives depend on it, and wear inside a cable is hard to see, so it gets around 10 or more.

   </details>

6. <!-- q: open id="6d4a8c21" -->
   Why don't engineers just give every part a factor of safety of 10?

   <details><summary>Answer</summary>

   A higher factor of safety means a thicker, heavier, more expensive part. For many products, like a bicycle or an aircraft, that extra weight and cost would make the product worse or useless. The factor of safety is a trade-off between safety and weight and cost, set by how uncertain the loads are and how bad a failure would be.

   </details>

## Before moving on
<!-- bite: 00fb5041-3eb7-4eb2-860f-dfdfae51a6d6 -->

You can explain why a factor of safety is needed, calculate stress, factor of safety and allowable stress, and say why some products need much more than others. **Next:** [[engineering-design-and-prototyping/24-embedded-electronics-and-mechatronics|24 — Embedded Electronics and Mechatronic Integration]]: sensors, a small computer and motors working together inside one product.

## Related
<!-- bite: 96fed475-898c-4952-86dd-88d802f72a68 -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[continuum-mechanics/index|Continuum Mechanics]]: stress and strain in full.

## About this lesson
<!-- bite: 61bd23fd-b821-4433-a75e-cf0226c81127 -->

**Level:** Intermediate. **Covers:** why a factor of safety is needed, stress, factor of safety, allowable stress, typical values, and the safety versus weight and cost trade-off.

**Where it sits:** lesson 23 of 36, in part 6 (detailed design).

**Source:** written from general engineering knowledge; it is not in the SSG 532 lecture notes. The typical values are rough; real ones come from each industry's standards. The worked numbers are checked by `scripts/diagrams/engineering_design.py`.
