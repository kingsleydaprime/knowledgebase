# Hardware & Embedded

## What hardware and embedded systems are

**Embedded systems are small computers built into everyday things, such as a microwave, a smartwatch, a car's brakes or a smart meter, running one program that controls that device.**

The computer inside them is usually a **microcontroller**: a tiny, cheap chip that holds a processor, a little memory and pins that connect to the outside world. Through those pins it reads **sensors** (temperature, light, buttons) and controls **actuators** (lights, motors, relays). Many also talk wirelessly, over Wi-Fi, Bluetooth or long-range radio, which is what "Internet of Things" (IoT) devices are.

This course covers the physical layer under all software: electricity, signals, microcontrollers, how chips talk to each other, radio, and designing your own circuit board. It's different from software in one important way: mistakes are physical. Wire something wrongly and a component can burn out. You debug with a multimeter rather than an error message.

## What you'll be able to do

By the end you will be able to:
- work out voltages, currents and power in a simple circuit, and keep components within safe limits;
- explain how a microcontroller reads the real world and controls things;
- choose a microcontroller (Arduino, ESP32, STM32 and others) and load code onto it;
- connect chips together using the standard ways they talk (UART, I2C, SPI and more);
- choose a wireless technology for a device, and estimate how far it will reach;
- design an IoT system, including making a battery last;
- design a simple printed circuit board in KiCad.

## Where to start

**The golden rule:** before wiring any component, read its **datasheet** (its limits, which you must never exceed) and find the maker's **reference design** (an example circuit showing how to wire it correctly). Every major maker publishes both.

Read in order; each note builds on the one before.

1. [[hardware/01-electricity|Electricity]]: voltage, current and resistance, Ohm's law, power, the difference between mains and battery power, and the small capacitors that keep chips stable.
2. [[hardware/02-digital-and-analog|Digital vs Analog]]: how a chip that only knows numbers measures a smooth real-world signal, and produces one.
3. [[hardware/03-embedded-systems|Embedded Systems]]: what "embedded" means, running with or without a small operating system, working with very little memory, and controlling pins.
4. [[hardware/04-microcontrollers|Microcontrollers]]: the popular families (Arduino, ESP32, STM32, Raspberry Pi Pico, nRF52840), how code gets onto them, and timing.
5. [[hardware/05-communication-protocols|Communication Protocols]]: the standard ways chips talk to each other, and how to choose between them.
6. [[hardware/06-radio-frequency|Radio Frequency]]: how wireless works, how far a signal reaches, antennas, and the wireless technologies you'll meet (Wi-Fi, Bluetooth, Zigbee, LoRa, mobile networks, NFC). The longest and hardest note.
7. [[hardware/07-connectivity|Connectivity]]: choosing between Ethernet, Wi-Fi and mobile networks, and powering a device through its network cable.
8. [[hardware/08-iot-architecture|IoT Architecture]]: how connected devices are organised, the messaging system most of them use (MQTT), and designing a device to last on a battery.
9. [[hardware/09-putting-it-all-together|Putting It All Together]]: the whole picture in one place, and what to build next.
10. [[hardware/10-kicad-basics|KiCad Basics]]: turning a circuit into a board you can have manufactured, using the free KiCad software.

## For quick lookup

- [[hardware/hardware-reference|Hardware reference]]: units, prefixes and key formulas.

## Practice

- The IoT Bridge board: a real internship project with about 19,600 words of working notes: choosing components and why, the circuit, a KiCad walkthrough and documentation. Read the course for the ideas, then this to see them argued over under real limits of cost, size and someone else's requirements.
- [[hardware/projects|Projects]]: hands-on tasks, from easy (🟢) to hard (🔴), each with a clear "done when".
- [[hardware/interview/index|Hardware interview prep]]: 25 questions on electronics, embedded systems, radio and IoT.

## Key ideas to remember

1. **Read the datasheet and the reference design before wiring anything.** → [[hardware/01-electricity|Electricity]]
2. **Put a small capacitor next to every chip's power pin.** Missing ones cause strange, intermittent faults. → [[hardware/01-electricity|Electricity]]
3. **A pin connected to nothing reads random values.** Always pull it to a known level. → [[hardware/03-embedded-systems|Embedded Systems]]
4. **Battery life is decided by how long the device sleeps,** not how fast it runs. → [[hardware/08-iot-architecture|IoT Architecture]]

## Related

- [[how-computers-work/index|How Computers Work]]: from electricity to a working processor, in theory.
- [[computer-architecture/index|Computer Architecture]]: how processors are organised.
- [[robotics/index|Robotics]]: adding motion, control and autonomy.
- [[control-theory/index|Control Theory]]: feedback loops, including [[control-theory/44-digital-control-1|running one on a microcontroller]].
- [[networking/index|Networking]]: the protocols above the physical connection.

---

## About this course

- **Size:** about 31,000 words across the notes and the IoT Bridge project. Until August 2026 this was one long file; it was split into the numbered notes so each section can be linked.
- **Where it came from:** written from real use, including a finished circuit board project.
- **Not covered yet:** powering up and testing a brand-new board for the first time (the note should come after a real build), and building a robot; the [[robotics/index|Robotics]] notes are theory, not yet tested on hardware.
