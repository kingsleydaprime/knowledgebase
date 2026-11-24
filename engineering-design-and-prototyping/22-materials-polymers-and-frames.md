---
id: 3b43c723-0b97-453b-86eb-25aa8ab5c7bd
---

# Materials: Polymers and Frames

Material choice is the part of detailed design where you decide what each part is made of, matching the material's properties to the job, the production volume and the cost.

## Before you start
<!-- bite: 70c4be2b-089b-4bbe-b864-ef89fb7a785c -->

You should know the material properties from [[engineering-design-and-prototyping/18-considerations-of-good-design-2|Considerations of Good Design 2]] (strength, fatigue, toughness, corrosion resistance) and the DFMA principles ([[engineering-design-and-prototyping/21-engineering-drawings-and-dfma|lesson 21]]).

After this lesson you will be able to:

1. compare thermoplastics and thermosetting polymers, with two products for each;
2. recommend a material and a manufacturing process for a lightweight, high-strength bicycle frame, and justify it.

## What material choice is
<!-- bite: b93558d7-f4d7-4229-92c2-0583e4cc2e2e -->

Remember from lesson 18: material selection starts with the service conditions, then depends on the material's properties, the manufacturing process, and how it must perform over its service time.

This lesson does that twice:

1. For plastics, which are everywhere in product design and come in two very different families.
2. For a bicycle frame, a classic "pick the material and the process" problem.

## Thermoplastics and thermosets: what they are
<!-- bite: 244eb393-9e49-47aa-a9a0-c43ec08a85e5 -->

Plastics are polymers: very long chain-like molecules. How those chains are held together splits them into two families:

- **Thermoplastics** soften when heated and harden when cooled, and can be reheated and reshaped many times. Like chocolate: melt it, set it, melt it again.
- **Thermosetting polymers (thermosets)** cure once (set) permanently and cannot be remelted; they char or burn if overheated. Like an egg: once it's cooked, heating it again won't make it raw.

## Comparing the two
<!-- bite: 154e27aa-1fb5-40ca-8a3f-603f8f85e7f9 -->

| Property | Thermoplastics | Thermosets |
| --- | --- | --- |
| What happens with heat | Soften when heated and harden when cooled; can be reshaped many times | Cure once permanently; cannot be remelted, char if overheated |
| Structure | Long chains held by weak forces | Chains linked by strong cross-links, forming a rigid network |
| Typical properties | Flexible to tough, easier to process, recyclable | Hard, rigid, good heat and chemical resistance, dimensionally stable, harder to recycle |
| Typical applications | Packaging, pipes, casings, consumer goods, 3D printing filament | Electrical parts, circuit boards, adhesives, heat-resistant handles, composites |
| Examples | Water bottles (PET); PVC pipes | Circuit boards (epoxy resin); pot handles or electrical sockets (phenolic, also called Bakelite) |

The structure row explains everything else. Weak forces between chains let go when heated, so thermoplastics melt and can be recycled. Cross-links don't let go, so thermosets stay rigid when hot, which is exactly what a pot handle needs.

## The bicycle frame problem
<!-- bite: f80733b4-96ff-45e8-b35a-33f2f0f79d85 -->

Now the bigger problem: designing a lightweight, high-strength bicycle frame. What should it be made of, and how should it be made?

First, what the frame needs:

- **Low mass for its strength and stiffness**, so the rider isn't pushing extra weight.
- **Resistance to fatigue**, because the load repeats with every pedal stroke (remember the paper clip bent back and forth).
- **Corrosion resistance**, because bikes live in rain.
- A **cost** that suits the market.

## The four candidate materials
<!-- bite: 947cd68f-aebe-43ad-8bb1-ad8caf65da91 -->

| Option | Properties | Process | Fit |
| --- | --- | --- | --- |
| Aluminium alloy (for example 6061-T6) | Roughly one third the density of steel, good strength after heat treatment, corrosion resistant, easy to work | Extruded or hydroformed tubes, TIG welded, then heat treated | Best balance for medium to high volume and moderate cost |
| Carbon fibre composite | Very high strength and stiffness for its weight, can be shaped and tuned | Layup of prepreg sheets in a mould, then cured | Best performance, but high cost and labour, so for low volume or premium bikes |
| Chromoly steel | Tough and fatigue resistant, but heavier | Tube cutting and welding or brazing | Good for repair and low-cost tooling |
| Titanium | Light, strong and corrosion resistant | Welded in inert gas | Very expensive, so a niche market |

Notice carbon fibre is a composite whose resin is a thermoset: that's why it's cured once in a mould and can't be melted down and reshaped.

## The recommendation
<!-- bite: da0953d2-30ce-47a4-9560-b0dd75eb551c -->

For a lightweight, high-strength frame produced in medium to high volume at a reasonable cost, choose **aluminium alloy** with hydroformed tubes and welding, followed by heat treatment.

If the target is a premium, low-volume racing frame and cost is less important, choose **carbon fibre**.

Justify it with the three factors the question names:

1. **Material properties**: strength-to-weight, fatigue, corrosion.
2. **Production volume**: welding suits volume; hand layup does not.
3. **Cost**: raw material plus labour.

The design is now fully detailed. Time to build it and see if it works: prototyping and testing, next.

## Common pitfalls
<!-- bite: 0748924a-8cf0-4226-8672-17b18cbf2161 -->

1. **"Thermosets are just harder thermoplastics."** The difference is the cross-links: thermosets can never be remelted.
2. **Picking the best-performing material without asking about volume and cost.** Carbon fibre is the best frame material on paper, but wrong for a cheap bike made in large numbers.
3. **Naming a material without a process.** The question asks for both, and the process must suit the volume.

## Check your understanding
<!-- bite: 6b65c1c0-8f39-42fa-bc35-5b854b3e4ce4 -->

Try each one before you open the answer.

1. <!-- q: mcq id="3a9f2d61" -->
   A broken plastic garden chair can be shredded, melted and moulded into a new one. Which family of polymer is it made of?

   - [x] Thermoplastic
   - [ ] Thermoset

   <details><summary>Answer</summary>

   Thermoplastic: it softens when heated and can be reshaped many times, so it is recyclable.

   </details>

2. <!-- q: mcq id="d84e0b17" -->
   Why are pot handles often made from a thermoset like phenolic (Bakelite)?

   - [ ] Because thermosets are cheaper and easier to recycle
   - [x] Because thermosets don't soften when hot, thanks to their cross-links
   - [ ] Because thermosets are more flexible

   <details><summary>Answer</summary>

   Cross-links keep a thermoset rigid when hot, giving it good heat resistance. A thermoplastic handle would soften near the flame.

   </details>

3. <!-- q: mcq id="1e7c5a93" -->
   Which of these products are usually made of thermoplastics? Choose all that apply.

   - [x] PET drink bottles
   - [x] PVC water pipes
   - [ ] Epoxy circuit boards
   - [x] 3D printing filament

   <details><summary>Answer</summary>

   PET bottles, PVC pipes and 3D printing filament. Epoxy circuit boards are thermosets.

   </details>

4. <!-- q: mcq id="6b2f8e40" -->
   A company wants to make 50,000 affordable city bikes a year. Which frame material and process fit best?

   - [ ] Carbon fibre, hand layup in a mould
   - [x] Aluminium alloy, hydroformed tubes, welded and heat treated
   - [ ] Titanium, welded in inert gas

   <details><summary>Answer</summary>

   Aluminium alloy. It has a good strength-to-weight ratio and corrosion resistance, welding suits high volume, and the cost is moderate. Carbon fibre's hand layup doesn't suit volume, and titanium is too expensive.

   </details>

5. <!-- q: open id="c50a7d2e" -->
   A small workshop makes 20 hand-built racing bikes a year for professional riders, and price is not a concern. Recommend a frame material and process, and justify it using material properties, production volume and cost.

   <details><summary>Answer</summary>

   Carbon fibre composite, laid up as prepreg sheets in a mould and cured. Properties: very high strength and stiffness for its weight, and it can be shaped and tuned for racing. Volume: 20 a year is low, so the labour-heavy layup process is fine. Cost: high material and labour cost doesn't matter, because price is not a concern for this market.

   </details>

## Before moving on
<!-- bite: b59e6384-e31c-4c5d-a42f-7faf51552f08 -->

You can compare thermoplastics and thermosets with examples, and recommend and justify a material and process for a bicycle frame. **Next:** [[engineering-design-and-prototyping/23-factor-of-safety|23 — Factor of Safety]]: making parts stronger than they need to be, and by how much.

## Related
<!-- bite: b1415061-df23-47dc-b110-e4687e76f434 -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[engineering-design-and-prototyping/31-manufacturing-processes|Manufacturing Processes]]: the processes and volumes behind a choice like the bicycle frame.

## About this lesson
<!-- bite: 334e871f-f2c0-4226-af41-e9346f6ae1da -->

**Level:** Intermediate. **Covers:** thermoplastics versus thermosetting polymers, and choosing a material and process for a lightweight, high-strength bicycle frame.

**Where it sits:** lesson 22 of 36, in part 6 (detailed design).

**Source:** written for the SSG 532 exam from general engineering knowledge. It is not in the lecture notes, so check it against any slides the lecturer gave.
