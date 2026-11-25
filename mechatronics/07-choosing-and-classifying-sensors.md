---
id: 89c7433c-1bd2-4fd9-8351-452879bc1774
---

# Choosing and Classifying Sensors

**Sensors are classified by four criteria — the character of their signal, their power supply, their mode of operation and the subject they measure — and chosen against six selection criteria, using the datasheet to check each one.**

When you buy a phone charger you check the plug, the voltage and the price before you pay. Choosing a sensor is the same habit, done carefully, with the datasheet as the label on the box.

## Before you start
<!-- bite: 8c823d1b-3113-4ccb-a5cc-d950a949a62d -->

You should know the performance characteristics ([[mechatronics/06-sensor-performance-characteristics|Sensor Performance Characteristics]]), because selection is mostly checking them. No maths.

After this lesson you will be able to:

1. outline the four criteria used to classify sensors, with an example each;
2. list the six criteria for selecting a sensor;
3. explain the role of the sensor datasheet, for example when choosing sensors for a drone.

## What classifying and choosing mean
<!-- bite: ba373939-193c-451e-8c43-7d22aa167f29 -->

There are thousands of sensors. **Classifying** them puts them into groups so you can talk about them sensibly — "it's an active, analogue, deflection-type thermal sensor" tells an engineer a lot in one breath. **Choosing** one is matching a sensor to a job. The two go together: the class tells you how a sensor will fit into your system, and the selection criteria tell you whether it is good enough.

We keep the **drone** from lesson 5 as the running example, and add the exam's other case, a **wearable health monitor** (a smartwatch reading heart rate and temperature).

## The kid version
<!-- bite: 8cb31ed0-f163-4c05-b596-011d85fcf6de -->

Think of sorting a big box of toys. You can sort them by colour, by size, by whether they need batteries, or by what they are for. A single toy fits into one group in *each* sorting — a red, small, battery-powered car. Sensors are sorted the same way, four different ways at once. Then, when you need one toy for a particular game, you read the label on its box to check it will do the job.

**Where the analogy stops working.** A toy's label is a few words; a sensor's datasheet is pages of tested numbers, and those numbers only hold under the conditions the datasheet states.

## 1. By signal character: analogue or digital
<!-- bite: f5cd8c1f-469a-4dff-9a33-5d82141e3078 -->

The first classification is about **what kind of output** the sensor gives.

An **analogue** sensor gives a continuous, uninterrupted output — a voltage that can take any value in its range, like a thermistor's. A **digital** sensor gives discrete steps or events — counts or a binary number, like an encoder's pulses.

The notes point out the advantage of digital sensors: high accuracy and precision, and **no analogue-to-digital converter is needed** to connect them to a computer, because the signal is already digital.

*Wearable:* the heart-rate sensor's light signal is analogue; a step counter's output is digital.

## 2. By power supply: active or passive
<!-- bite: af5a888c-2d06-4c60-83bc-3e46bee4c401 -->

The second classification is about **where the energy for the output comes from**. The notes define it this way:

An **active** sensor needs an external power supply — an auxiliary energy source — to work. A **strain gauge** and a **resistance thermometer** are active: their resistance changes, but you must drive a current through them to get a voltage out.

A **passive** sensor produces its output directly from the stimulus, with no external supply. A **piezoelectric** crystal makes a voltage when squeezed; a **thermocouple** (thermoelectric) makes a voltage from a temperature difference; radioactive detectors also count here.

Be careful: some textbooks use the two words the other way round. In this course, use the notes' definitions, and say which convention you are using if in doubt.

## 3. By mode of operation: deflection or null
<!-- bite: 007e77a5-e41f-4ff8-87ab-1aaf4825da89 -->

The third classification is about **how the reading is taken**.

A **deflection-type** sensor gives an output that is directly proportional to the measured quantity, and you read that deflection. A pressure gauge where a piston pushes against a spring and moves a dial needle is deflection-type.

A **null-type** sensor works by a **balance act**: you adjust a known opposing effect until it exactly cancels the measured one, and the reading is how much you had to apply. A beam balance and a Wheatstone bridge are null-type. Null methods are usually more accurate, because at balance the sensor carries no load, but they are slower.

## 4. By subject of measurement
<!-- bite: ad26acec-8719-4fab-952a-cb30817d6eee -->

The fourth classification is simply **what the sensor measures**: acoustic, biological, chemical, electric, mechanical, optical, radiation, thermal, and so on.

*Wearable:* the heart-rate sensor is optical (it shines light into the skin), the skin-temperature sensor is thermal, and a sweat sensor would be chemical.

So one sensor sits in all four groups at once. A smartwatch heart-rate sensor is analogue, active (its LED needs power), deflection-type and optical.

## How each classification affects performance
<!-- bite: ef30802e-e2cf-4f1f-b72c-0d45531fe416 -->

The 2025/26 exam asks how each criterion **influences performance**. One line each:

1. **Signal character**: digital output avoids conversion error and noise on the wire, so it is easier to keep accurate; analogue needs conditioning and an ADC, which add error.
2. **Power supply**: an active sensor drains the battery — important in a wearable — while a passive sensor needs no supply but often gives a tiny signal that needs amplifying.
3. **Mode of operation**: null-type is more accurate but slower; deflection-type is quick enough to follow a fast-changing heartbeat.
4. **Subject of measurement**: decides what physics the sensor relies on, and so what disturbs it — an optical sensor is fooled by sunlight and movement.

## The six selection criteria
<!-- bite: 4179ae67-d86c-42db-beaa-42814b3824ed -->

Classifying tells you what kind of sensor something is. Choosing one for a job, the notes give six criteria:

1. **The variable to be measured and the application** — what exactly, and where.
2. **The nature of precision and sensitivity required** — how good the reading must be.
3. **The dynamic range** — the smallest to the largest value it must handle.
4. **The level and type of primary transducers required** — what the front-end element must be.
5. **The complexity of the control system** — how the signal must fit the controller.
6. **Cost, size, and ease of maintenance** — what you can afford, fit and look after.

## The role of the datasheet
<!-- bite: 930f2507-650b-4067-b720-bf868d23d3b6 -->

A **datasheet** is the document from the manufacturer that states a sensor's tested characteristics: range, sensitivity, resolution, accuracy, linearity, repeatability, response time, supply voltage, output type, operating temperature, size and interface.

Its role in a mechatronic system is to let you **check, before you buy or build, that the sensor meets the system's requirements**. You write down what the system needs (from the functional specification in the design process), then read each number off the datasheet and compare. It also tells you how to connect, power and calibrate the sensor correctly.

## Worked example: a drone's position and speed sensors
<!-- bite: 22476363-683a-4eac-8a70-bad4569baade -->

The exam asks how you would use datasheets to choose a drone's position and speed sensors. Go requirement by requirement:

1. **Range.** The drone flies up to 100 m, so a rangefinder with a 0.2–8 m range is only good for landing; height above that needs a barometer or GPS.
2. **Accuracy and resolution.** To land within 10 cm, the rangefinder's datasheet accuracy must be well under 10 cm.
3. **Response time / update rate.** The flight controller updates 400 times a second, so the motion sensor must deliver at least that fast.
4. **Environment.** Check the operating temperature and vibration ratings — a drone shakes.
5. **Power, size, weight and interface.** Every gram costs flight time; the output must match the flight controller's bus.

If any number fails, that sensor is out. The datasheet is how you *know* the system will meet its requirements, rather than hoping.

## Terms used in choosing sensors
<!-- bite: f2d2e0a3-4a35-40ca-851c-249d224e8c28 -->

1. **Analogue sensor**: this is a sensor whose output is continuous, able to take any value in its range.
2. **Digital sensor**: this is a sensor whose output is in discrete steps or counts, ready for a computer without conversion.
3. **Active sensor (as in the notes)**: this is a sensor that needs an external, auxiliary power supply to produce its output.
4. **Passive sensor (as in the notes)**: this is a sensor that produces its output directly from the stimulus, with no external supply.
5. **Null-type sensor**: this is a sensor that measures by balancing the quantity against a known opposing effect until the result is zero.
6. **Datasheet**: this is the manufacturer's document listing a sensor's tested characteristics and how to connect and use it.

## Common pitfalls and traps
<!-- bite: d501fe52-755f-4057-a94a-07b8c042f0b1 -->

- **Mixing up classification and selection.** The four classification criteria (signal, power, mode, subject) say what a sensor *is*; the six selection criteria say whether it *suits the job*. Exams ask for them separately.
- **Using the opposite active/passive convention.** Follow the notes: active needs external power (strain gauge), passive generates its own output (thermocouple, piezoelectric).
- **Reading a datasheet number without its conditions.** "±0.5 °C" may only hold from 0 to 50 °C.
- **Choosing on one number.** A sensor with superb accuracy that is too slow, too heavy or too power-hungry still fails.

## Check your understanding
<!-- bite: ae15854f-8d68-4870-91c4-672da0c992f0 -->

Try each one before you open the answer.

1. <!-- q: mcq id="51843892" -->
   Which four criteria are used to classify sensors? (choose all that apply)

   - [x] Character of the signal (analogue or digital)
   - [x] Power supply (active or passive)
   - [x] Mode of operation (deflection or null)
   - [x] Subject of measurement (thermal, optical, …)
   - [ ] Price

   <details><summary>Answer</summary>

   Signal character, power supply, mode of operation and subject of measurement. Price is a selection criterion, not a classification.

   </details>

2. <!-- q: mcq id="8182ef3b" -->
   Using the course's definitions, which of these is a **passive** sensor?

   - [ ] A strain gauge
   - [ ] A resistance thermometer
   - [x] A thermocouple
   - [ ] A potentiometer

   <details><summary>Answer</summary>

   The thermocouple produces a voltage directly from a temperature difference, with no external supply. The strain gauge, resistance thermometer and potentiometer all need a supply to give an output, so they are active.

   </details>

3. <!-- q: gap id="d9fdb231" answers="null;deflection" -->
   A Wheatstone bridge adjusted until its meter reads zero is a ___-type measurement, while a spring-loaded pressure gauge whose needle moves in proportion to the pressure is a ___-type measurement.

   <details><summary>Answer</summary>

   Null-type (balance), then deflection-type.

   </details>

4. <!-- q: open id="f3cb119e" -->
   Describe the role of the sensor datasheet in a mechatronic system.

   <details><summary>Answer</summary>

   The datasheet is the manufacturer's statement of the sensor's tested characteristics — range, sensitivity, resolution, accuracy, linearity, response time, supply, output type, operating conditions, size. Its role is to let the designer check, before selecting the sensor, that each of those meets the system's requirements, and to show how to connect, power and calibrate it correctly. It turns sensor selection from guessing into checking.

   </details>

5. <!-- q: open id="a83145fb" -->
   A wearable health monitor must measure heart rate and skin temperature for a week on a small battery. Pick two of the four classification criteria and explain how each would influence which sensors you choose.

   <details><summary>Answer</summary>

   Power supply: active sensors drain the battery, so you would prefer low-power active sensors or passive ones (a thermocouple-type temperature sensor) and duty-cycle the optical heart-rate LED. Signal character: a digital-output sensor plugs straight into the microcontroller with no ADC, saving power and avoiding conversion noise. (Mode of operation — fast deflection-type to follow a heartbeat — and subject of measurement — optical heart-rate sensors being disturbed by movement and sunlight — are equally good answers.)

   </details>

6. <!-- q: mcq id="18b8469e" -->
   A drone's flight controller needs height readings from ground level to 120 m. The candidate rangefinder's datasheet says range 0.2–8 m, accuracy ±1 cm, update rate 500 Hz. What is the right conclusion?

   - [ ] Use it: the accuracy and update rate are excellent.
   - [x] It cannot cover the required range on its own; pair it with a barometer or GPS for height above 8 m.
   - [ ] Reject it because ±1 cm is not accurate enough.
   - [ ] The datasheet does not matter if the sensor is cheap.

   <details><summary>Answer</summary>

   The dynamic range fails: 8 m is far below 120 m. It is still excellent for landing, so pair it with a sensor that covers the rest of the range. One failed requirement rules out using it alone.

   </details>

## Before moving on
<!-- bite: 215ecfbd-8787-4b51-b5c7-4f6251de4856 -->

You are done when you can classify any sensor four ways, list the six selection criteria, and explain how a datasheet is used to check a sensor against requirements.

Recap: classify by signal (analogue/digital), power (active/passive), mode (deflection/null) and subject; select on variable and application, precision and sensitivity, dynamic range, primary transducer, control complexity, and cost/size/maintenance; the datasheet is where you check every one.

Next, [[mechatronics/15-measurement-uncertainty|Measurement Uncertainty and Error Propagation]] asks what happens when you calculate a result from several imperfect sensor readings: how big is the uncertainty in the answer?

## Related
<!-- bite: 488b2d4f-9bd5-44c6-8511-3d375a81a1fa -->

- [[mechatronics/03-the-mechatronic-design-process|The Mechatronic Design Process]]: where sensor selection sits in the design.
- [[mechatronics/06-sensor-performance-characteristics|Sensor Performance Characteristics]]: the numbers you check on the datasheet.

## About this lesson
<!-- bite: 2da7ad56-d16d-4131-b3c1-15ba3be9d099 -->

**Level:** introductory, no maths. It covers the four classification criteria, how each affects performance, the six selection criteria and the role of the datasheet, with a drone and a wearable monitor as running examples. It is lesson 7, in section B.

**Source:** University of Lagos SSG 415 "Sensors and Transducers" notes (sensor selection criteria and classification) and the SSG 415 exam question banks (Question 1f "role of sensor data sheet", 1h "four criteria used to classify sensors"; 2025/26 Question 1d on drone sensor datasheets and 1f on wearable health monitoring).
