---
id: 5505aeb2-1dba-49ad-a9bc-483f83dbebe5
---

# Examples of Mechatronic Systems

**A mechatronic system is any product where mechanical parts, electronics, control and software are integrated — and once you know what to look for, they are everywhere.**

Robots, car engines, magnetic bearings and driverless factory vehicles are all mechatronic. This lesson lists the classic examples, then looks closely at the car, because the exam asks you to explain four of its systems.

## Before you start
<!-- bite: 7c0304da-95d8-4b59-8acc-f49a51e418c2 -->

You should know the definition of mechatronics and its five elements ([[mechatronics/02-the-five-elements-of-mechatronics|The Five Elements of Mechatronics]]). No maths.

After this lesson you will be able to:

1. list several standard examples of mechatronic systems;
2. explain four automotive mechatronic systems and the role integration plays in each;
3. say, for any example, what each discipline contributes.

## What counts as an example
<!-- bite: 1f8c1f99-c3bd-47ec-a7db-3b55c12c8baf -->

The standard list of mechatronic systems from the course is: **industrial robots** (such as the FANUC Robot M-20iA), **digitally controlled combustion engines**, **self-adaptive machine tools**, **contact-free magnetic bearings**, **autonomous guided vehicles (AGVs)**, and **automotive assembly welding robots**. What they share is the thing from lesson 1 — the mechanical, electronic, control and computing parts are designed together, and the system does something none of the parts could alone.

## Two examples up close
<!-- bite: 39905e90-0249-4b1f-80f8-314660eb81d1 -->

Two of those are worth a closer look, because they show integration doing something no single discipline could:

- **Contact-free magnetic bearings** hold a spinning shaft on a cushion of magnetic field instead of metal rollers. Mechanically that is impossible to keep stable — a magnet pulling an iron shaft is always unstable. It only works because sensors measure the shaft's position thousands of times a second and electronics adjust the magnet current to hold it centred. The *control and sensing make a mechanically impossible bearing possible.* That is mechatronics.
- **Self-adaptive machine tools** measure cutting force and vibration while cutting and adjust feed and speed on the fly, so the tool lasts longer and the cut stays accurate as the material varies.

## The car as four mechatronic systems
<!-- bite: 95d2a4e7-88c9-4548-a8a8-dc105b20672d -->

A modern car is the example worth knowing in detail, because it bundles several mechatronic systems together. Here are four, each explained with the role of integration — exactly what the automotive exam question wants. They all run the same **sense → decide → act** loop; watch for it in each.

## The car, 1: anti-lock braking (ABS)
<!-- bite: b34520f4-7136-4f51-9fa6-edbd0c1599df -->

**What it does:** stops the wheels from locking and skidding under hard braking, so the car keeps steering.

**The parts:** wheel-speed sensors (sensing), a hydraulic valve block that can release and re-apply brake pressure at each wheel (actuation), and an electronic controller running a control law (computing and control).

**The role of integration:** a purely mechanical brake can only press harder. The mechatronic version *senses* each wheel slowing too fast, *decides* it is about to lock, and *releases* that wheel's pressure for a fraction of a second, many times a second. No single discipline does this — the sensor, the control law and the hydraulic actuator are useless apart and powerful together.

## The car, 2: electronic engine management
<!-- bite: c896aee6-596a-424b-867e-b89e9c139f62 -->

**What it does:** meters exactly the right amount of fuel and the right ignition timing for the current load, temperature and air.

**The parts:** sensors for air flow, throttle position, oxygen in the exhaust and engine temperature; fuel injectors and the ignition coils as actuators; and the engine control unit (ECU) as the embedded computer.

**The role of integration:** a mechanical carburettor sets a fixed fuel mixture. The mechatronic engine *reads* the actual conditions and *computes* the ideal injection and timing every cycle, then *acts* through the injectors — giving more power, less fuel and cleaner exhaust at once. The oxygen sensor even closes the loop: the exhaust is measured and fed back to correct the next injection.

## The car, 3: electronic power steering (EPS)
<!-- bite: c8bbfea4-410f-4395-88e9-60caa0704b45 -->

**What it does:** adds just enough motor assistance to the steering so the wheel is light to turn at low speed and firm at speed.

**The parts:** a torque sensor on the steering column (sensing how hard the driver is turning), an electric motor on the rack (actuation), and a controller that decides how much help to add (control and computing).

**The role of integration:** older hydraulic power steering gives a fixed amount of boost and runs a pump all the time. EPS *senses* the driver's effort and the car's speed, *computes* the right amount of assistance, and *delivers* it with a motor only when needed — lighter, more efficient, and tunable in software. The same hardware can even steer the car itself for lane-keeping.

## The car, 4: electronic stability control (ESC)
<!-- bite: 2825fff6-d7d5-4be7-9bab-a7dce99c0dd8 -->

**What it does (ESC):** keeps the car from spinning out by braking individual wheels when it detects a skid.

**The parts:** accelerometers and a yaw-rate sensor (sensing how the car is actually rotating and sliding), the ABS valve block reused to brake single wheels (actuation), and a controller comparing where the car is going with where the driver is steering (control).

**The role of integration:** the system *senses* that the car's real motion disagrees with the steering, *decides* which wheel to brake to correct the slide, and *acts* through the brakes — all faster than a driver could react. It reuses the ABS hardware, which is itself a sign of good mechatronic integration: one actuator set, several control functions.

The pattern in all four is the same **sense → decide → act** loop, with integration being what makes the whole beat the parts.

## Terms used in this lesson
<!-- bite: 45a7ccf3-6236-489c-9362-187f60e0389e -->

1. **Magnetic bearing**: this is a bearing that holds a shaft with magnetic fields instead of physical contact. It needs active sensing and control to stay stable, which is why it is a mechatronic system and not just a magnet.
2. **Autonomous guided vehicle (AGV)**: this is a driverless vehicle that moves goods around a factory or warehouse by following a planned route and sensing its surroundings.
3. **Engine control unit (ECU)**: this is the embedded computer that runs an engine's management — reading its sensors and commanding fuel and ignition. "ECU" is also used more loosely for any car control module.
4. **Closed loop (in these examples)**: this is when the system measures the result of its own action and uses that measurement to correct the next action — like the oxygen sensor correcting the next fuel injection. Open loop would act without checking the result.

## Common pitfalls and traps
<!-- bite: 16fadbda-2b0f-4e86-99a4-85ad579c2716 -->

- **Naming an example without the integration.** The automotive question explicitly asks for "the role of integration in each case". Saying "ABS stops skidding" is half an answer; you must say how sensing, control and actuation combine to do it.
- **Calling a purely mechanical device mechatronic.** A carburettor, a drum brake or hydraulic power steering are mechanical/hydraulic, not mechatronic — they do not sense and compute. Their electronic replacements are the mechatronic versions.
- **Forgetting that one actuator can serve several functions.** ESC reusing the ABS valves is good integration, not a coincidence — sharing hardware across control functions is a hallmark of mechatronic design.

## Check your understanding
<!-- bite: 92e75208-b601-4b59-840b-54012c3e3709 -->

Try each one before you open the answer.

1. <!-- q: mcq id="ded2d7fe" -->
   Why is a contact-free magnetic bearing a mechatronic system rather than just a clever magnet?

   - [ ] Because magnets are electronic components.
   - [x] Because it is mechanically unstable and only stays centred through continuous sensing and control of the magnet current.
   - [ ] Because it spins very fast.
   - [ ] Because it is made of metal.

   <details><summary>Answer</summary>

   A magnet pulling an iron shaft is inherently unstable, so the bearing only works because sensors measure the shaft position and electronics adjust the current thousands of times a second. Control and sensing make a mechanically impossible bearing possible.

   </details>

2. <!-- q: gap id="ac5b2f90" answers="wheel-speed|wheel speed;hydraulic" -->
   In ABS, ___ sensors detect a wheel about to lock, and the controller commands the ___ valve block to release that wheel's brake pressure briefly.

   <details><summary>Answer</summary>

   Wheel-speed sensors and the hydraulic valve block. Sensing, control and hydraulic actuation together do what pressing the pedal harder cannot.

   </details>

3. <!-- q: mcq id="997facc0" -->
   What does the oxygen sensor add to electronic engine management?

   - [ ] It opens the fuel injectors directly.
   - [x] It closes the loop: the exhaust is measured and fed back to correct the next fuel injection.
   - [ ] It replaces the engine control unit.
   - [ ] It measures engine temperature.

   <details><summary>Answer</summary>

   The oxygen sensor measures the result of combustion and feeds it back, so the ECU corrects the next injection — a closed loop. That is why a modern engine runs cleaner and more efficiently than a fixed carburettor.

   </details>

4. <!-- q: mcq id="603ee23b" -->
   Electronic stability control (ESC) reuses the ABS hydraulic valve block to brake individual wheels. Why is reusing that hardware a sign of good mechatronic design? (choose all that apply)

   - [x] One actuator set serves several control functions, saving cost and weight.
   - [x] It shows the control functions were designed together, not bolted on separately.
   - [ ] It means ESC does not need any sensors.
   - [ ] It removes the need for a controller.

   <details><summary>Answer</summary>

   Sharing actuators across control functions is efficient integration. ESC still needs its own sensors (accelerometers, yaw rate) and a controller — it shares only the actuation with ABS.

   </details>

5. <!-- q: open id="725d4dce" -->
   Choose any two of the four automotive systems. For each, name what it senses, what it decides, and what it acts on — and in one sentence say what the purely mechanical predecessor could not do.

   <details><summary>Answer</summary>

   Example — ABS: senses each wheel's speed, decides a wheel is about to lock, acts by releasing that wheel's brake pressure; a plain mechanical brake can only press harder, so it cannot stop a skid. Electronic power steering: senses the driver's steering torque and car speed, decides how much assistance to add, acts through an electric motor on the rack; hydraulic power steering gives fixed boost and runs its pump constantly, so it cannot vary the help by speed or steer the car itself. (Engine management and ESC are equally acceptable, described the same way.)

   </details>

## Before moving on
<!-- bite: 81ff412c-1d28-477d-ab62-a57264cf6e66 -->

You are done when you can list several mechatronic examples and, for the car, explain four systems as sense–decide–act loops with the role of integration in each.

Recap: classic examples are robots, digitally controlled engines, self-adaptive machine tools, magnetic bearings, AGVs and welding robots; the car bundles ABS, engine management, electronic power steering and stability control, each a sense–decide–act loop where integration beats the mechanical predecessor.

That closes section A. Next, section B begins with [[mechatronics/05-sensors-and-transducers|Sensors and Transducers]] — the devices every one of these examples relies on to feel the world.

## Related
<!-- bite: a88cfdf7-e7f7-4cff-a423-b69fc59b6d45 -->

- [[mechatronics/01-what-mechatronics-is|What Mechatronics Is]]: the synergy these examples demonstrate.
- [[mechatronics/05-sensors-and-transducers|Sensors and Transducers]]: the sensing half of every example here.
- [[robotics/index|Robotics]]: industrial robots and AGVs in depth.

## About this lesson
<!-- bite: 33de1a83-9eaf-4c23-9790-b25ffb3bfd57 -->

**Level:** introductory, no maths. It covers standard examples of mechatronic systems and, in detail, four automotive mechatronic systems with the role of integration in each. It is lesson 4 and the last of section A; read [[mechatronics/03-the-mechatronic-design-process|the design process]] before it.

**Source:** University of Lagos SSG 415 lecture notes (examples of mechatronic systems) and the SSG 415 exam question banks (Question 1d "list four examples"; 2025/26 Question 1a and 1c on automotive mechatronic systems and the role of integration).
