---
id: 1346f3bd-67f7-4c52-8cbf-58c08feb9a7c
---

# Embedded Electronics and Mechatronic Integration

A mechatronic product combines mechanical parts, electronics and software, with a small computer that senses the world, decides, and moves something in response.

## Before you start
<!-- bite: 759f8e88-787f-4981-bc44-ba0a46c8043c -->

You should know system architecture and interfaces ([[engineering-design-and-prototyping/16-system-architecture-and-mbse|System Architecture and MBSE]]).

After this lesson you will be able to:

1. describe the sense-think-act loop and name common sensors and actuators;
2. work out an ADC reading, a PWM average voltage and a battery life;
3. explain why a motor needs a driver, and list the problems that appear when electronics meet mechanics.

## What mechatronics is
<!-- bite: b4ce739d-4980-4b6f-804f-04024dd78ef0 -->

**Mechatronics** is the joining of **mechanical engineering, electronics, control and software** in one product. A washing machine, a car's anti-lock brakes, a drone, a 3D printer and an automatic gate are all mechatronic. The electronics inside, built around a small dedicated computer, are called **embedded electronics**, because they are embedded in the product rather than being a general-purpose computer.

The running example in this lesson is an **automatic plant waterer**: it measures how dry the soil is, and when it's too dry it runs a small pump for a few seconds.

## Sense, think, act
<!-- bite: cb53fe93-c44f-4e46-9cbd-5b2c667963e1 -->

Every mechatronic system runs the same loop:

1. **Sense:** sensors measure the world and turn it into electrical signals. A soil moisture probe.
2. **Think:** a **microcontroller** reads the signals, runs the program, and decides. "Moisture below 30%? Water."
3. **Act:** **actuators** turn electrical signals back into movement, heat, light or sound. The pump.

![A block diagram of the sense-think-act loop for an automatic plant waterer: a soil moisture sensor feeds the microcontroller, which drives a pump through a motor driver; the pump wets the soil, which changes what the sensor reads, closing the loop; a battery and regulator power the electronics](images/ed-sense-think-act.svg)

## Open and closed loop
<!-- bite: 8243202e-0934-4264-93d6-240f613f58eb -->

Because watering changes the moisture the sensor reads, the loop is **closed**: this is **closed-loop control**. A timer that waters every morning whatever the soil is doing would be **open-loop**: simpler, but it can't react.

## Sensors and actuators
<!-- bite: 4bb0c6a9-ff3a-4201-8542-a6129b3cd525 -->

Common **sensors**:

1. **Temperature:** thermistor or digital temperature sensor.
2. **Distance:** ultrasonic or infrared.
3. **Position and angle:** potentiometer, rotary encoder, limit switch.
4. **Force and weight:** load cell.
5. **Motion and orientation:** accelerometer and gyroscope (an IMU).
6. **Light:** photoresistor or photodiode.

Common **actuators**:

1. **DC motor:** spins continuously; speed set by voltage.
2. **Servo motor:** turns to a set angle and holds it.
3. **Stepper motor:** turns in exact steps, for precise positioning, as in 3D printers.
4. **Solenoid:** a straight push or pull, as in a door lock or a valve.
5. **Relay:** a switch the microcontroller can flip to control a bigger circuit.

## The microcontroller
<!-- bite: 3bc64b56-6d8c-49db-b5a5-da400588bf48 -->

A **microcontroller** is a whole small computer on one chip: processor, memory and input/output pins. Arduino boards (ATmega), ESP32 and STM32 are common. The features you use most:

1. **Digital input/output (GPIO):** pins that read or set on/off, such as a button or an LED.
2. **Analogue-to-digital converter (ADC):** reads a voltage as a number. A **10-bit** ADC splits its range into 2¹⁰ = 1,024 steps. With a 5 V range, one step is 5 ÷ 1,024 ≈ **4.9 mV**.
3. **Pulse-width modulation (PWM):** switches a pin on and off very fast. The fraction of time it is on, the **duty cycle**, sets the average voltage: 40% duty on a 12 V supply averages 0.4 × 12 = **4.8 V**. That is how a microcontroller controls motor speed or LED brightness.
4. **Communication:** **I2C**, **SPI** and **UART** connect it to sensors, displays and other chips.

## Power and driving loads
<!-- bite: abc080da-15ef-4329-8215-98e73c424005 -->

A microcontroller pin can supply only a few milliamps. A pump or motor needs hundreds. Connect a motor straight to a pin and you destroy the pin, so you use a **driver**: a transistor, a MOSFET, a relay or a motor driver chip (an **H-bridge** if the motor must run both ways). The pin sends the signal; the driver switches the big current from the supply. Motors also need a **flyback diode** to absorb the voltage spike when they switch off.

**Battery life** comes from a power budget: capacity ÷ average current. A 2,000 mAh battery supplying an average of 250 mA lasts about 2,000 ÷ 250 = **8 hours**. Sleeping the microcontroller between readings and running the pump only briefly cuts the average current, so the same battery lasts weeks.

## Integration: where it goes wrong
<!-- bite: adb3d000-d2df-43c3-9251-d3a192c74d3f -->

The hard part of mechatronics is making the three worlds work together:

1. **Electrical noise:** a motor starting can reset the microcontroller. Separate the motor's power, add capacitors, and keep sensor wires away from motor wires.
2. **Grounding:** every part must share a common ground, or signals are meaningless.
3. **Mounting and wiring:** cables chafe, connectors shake loose, boards need mounting points designed into the housing. Agree them in the interface control document.
4. **Heat:** drivers and regulators get hot inside a sealed case.
5. **Water and dust:** the plant waterer lives next to water; seal the electronics.
6. **Software:** the program must handle a sensor that fails, so the pump doesn't run forever.

## From breadboard to product
<!-- bite: 073df363-3e37-4364-ba2d-e6f8329883de -->

Electronics are prototyped in stages, like the mechanical parts in lesson 25:

1. **Breadboard:** plug components together with jumper wires, no soldering. Quick to change.
2. **Stripboard or perfboard:** soldered, more robust, for a working prototype.
3. **Printed circuit board (PCB):** a custom board designed in a tool such as KiCad, small and reliable, for the final product.

## Common pitfalls
<!-- bite: c6ce82c4-d59a-4f85-9381-382e90b102bc -->

1. **Driving a motor straight from a pin.** Always use a driver.
2. **Forgetting the common ground** between boards and supplies.
3. **No power budget.** The product runs flat in an hour instead of a month.
4. **Designing the housing before the electronics.** There is then no room for the board, the cables or the heat to escape.

Now the design has its mechanical, electronic and software parts. Next lesson builds it and tests it as a prototype.

## Check your understanding
<!-- bite: 88737d3d-1fa2-47bb-bb66-11944611b377 -->

Try each one before you open the answer.

1. <!-- q: exact id="7a9076bd" answer="0.805664" sigfigs="2" -->
   A 12-bit ADC (4,096 steps) measures a range of 0 to 3.3 V. What voltage does one step represent, in millivolts?

   <details><summary>Answer</summary>

   About 0.81 mV: 3,300 mV ÷ 4,096. More bits give finer steps.

   </details>

2. <!-- q: exact id="698bb92c" answer="3.75" -->
   A microcontroller drives a fan with PWM at a 75% duty cycle from a 5 V supply. What is the average voltage, in volts?

   <details><summary>Answer</summary>

   3.75 V: 0.75 × 5.

   </details>

3. <!-- q: exact id="9b9806d0" answer="12" -->
   A data logger's 1,800 mAh battery supplies an average current of 120 mA, and only 80% of its capacity is usable. How many hours does it last?

   <details><summary>Answer</summary>

   12 hours: 1,800 × 0.8 = 1,440 mAh usable, and 1,440 ÷ 120 = 12.

   </details>

4. <!-- q: mcq id="63669493" -->
   A 3D printer must move its print head to exact positions without a position sensor. Which actuator suits it?

   - [ ] A plain DC motor
   - [x] A stepper motor
   - [ ] A solenoid
   - [ ] A relay

   <details><summary>Answer</summary>

   A stepper motor turns in exact steps, so counting steps gives the position.

   </details>

5. <!-- q: open id="5f466476" -->
   A student connects a small water pump straight to an Arduino output pin. The pin stops working. Explain why, and how it should be done.

   <details><summary>Answer</summary>

   A pin can only supply a few milliamps, and the pump needs hundreds, so the pin was overloaded. Use a driver: the pin switches a transistor, MOSFET or relay, which switches the pump's current from its own supply, with a flyback diode across the pump and a common ground between the two supplies.

   </details>

6. <!-- q: mcq id="729f5d33" -->
   A garden sprinkler waters for 10 minutes every morning, rain or shine. What kind of control is this?

   - [x] Open-loop
   - [ ] Closed-loop
   - [ ] Sense-think-act with feedback
   - [ ] PWM

   <details><summary>Answer</summary>

   Open-loop: it doesn't measure the result. Adding a soil moisture sensor that the controller checks would make it closed-loop.

   </details>

## Before moving on
<!-- bite: a933f587-562a-4ffe-b9ca-33723a7e079b -->

You can describe a mechatronic system, choose sensors and actuators, work out ADC, PWM and battery figures, and avoid the common integration problems. **Next:** [[engineering-design-and-prototyping/25-prototyping-and-testing-protocols|25 — Prototyping and Testing Protocols]]: rough models, real models, and the tests that decide pass or fail.

## Related
<!-- bite: 6077a058-cc5f-4c04-bfea-154084d2a8fa -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[hardware/03-embedded-systems|Embedded Systems]] and [[hardware/04-microcontrollers|Microcontrollers]]: the electronics in depth.
- [[hardware/10-kicad-basics|KiCad Basics]]: designing a PCB.
- [[robotics/index|Robotics]]: mechatronics at its most complete.

## About this lesson
<!-- bite: f5655c46-9f6b-4e17-9aa0-32021d6fa147 -->

**Level:** Intermediate. **Covers:** what mechatronics is, the sense-think-act loop, open and closed loop, sensors and actuators, the microcontroller's GPIO, ADC, PWM and buses, drivers and power budgets, integration problems, and prototyping electronics.

**Where it sits:** lesson 24 of 36, in part 6 (detailed design).

**Source:** written from general engineering knowledge, because the SSG 532 lecture notes don't cover embedded electronics; it is on the official course outline. The worked numbers are checked by `scripts/diagrams/engineering_design.py`; the diagram comes from the same script.
