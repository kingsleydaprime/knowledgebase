# Hardware & Embedded

The layer below all the software. Electricity → signals → microcontrollers → radio → boards that exist physically and can be wrong in ways no compiler catches.

**~31,000 words across notes and one real project.** This domain was filed as "unordered reference material" until August 2026, which badly understated it — it's a course plus a finished build. Split from a single 8,656-word `fundamentals.md` into the numbered notes below in the same pass, so sections are linkable individually.

> **Golden rule of hardware design:** Before wiring any component, read its datasheet and find the manufacturer's own reference design or application note. The datasheet has absolute limits you must not exceed. The application note tells you how to wire it correctly. The reference schematic shows you what that looks like in practice. Every major manufacturer (ST, Espressif, Semtech, WIZnet, TI) publishes all three — use them.

That rule is the closest thing this domain has to a first principle. Software lets you try things and read the error; hardware lets you release the smoke.

## Reading order

The notes build on each other — don't skip, they stack.

1. [[hardware/01-electricity|Electricity]] — **[Beginner]** — voltage/current/resistance, Ohm's law, power, AC vs DC, regulators, power OR'ing, ground, transistors, capacitors, and why decoupling caps are the ones that matter
2. [[hardware/02-digital-and-analog|Digital vs Analog]] — **[Beginner]** — ADC, DAC and PWM: the bridges between a continuous world and a CPU that only has numbers
3. [[hardware/03-embedded-systems|Embedded Systems]] — **[Beginner → Intermediate]** — what "embedded" means, bare metal vs RTOS, memory when you have kilobytes, the firmware loop, GPIO
4. [[hardware/04-microcontrollers|Microcontrollers]] — **[Beginner → Intermediate]** — AVR/Arduino, ESP32, STM32, RP2040, nRF52840; how code gets onto them; clocks and timing
5. [[hardware/05-communication-protocols|Communication Protocols]] — **[Intermediate]** — UART, I2C, SPI, I2S, CAN, 1-Wire, and how to choose
6. [[hardware/06-radio-frequency|Radio Frequency (RF)]] — **[Intermediate → Advanced]** — spectrum, modulation, link budget, antennas, and the radio protocols you'll actually meet (WiFi, BLE, Zigbee, Thread, LoRa, NB-IoT, NFC, RFID). The longest note, and the one with the least free intuition
7. [[hardware/07-connectivity|Connectivity]] — **[Intermediate]** — Ethernet vs WiFi vs cellular, and Power over Ethernet
8. [[hardware/08-iot-architecture|IoT Architecture]] — **[Intermediate]** — the three layers, MQTT, edge computing, and designing to a power budget
9. [[hardware/09-putting-it-all-together|Putting It All Together]] — **[Intermediate]** — the whole stack in one picture, and concrete next steps
10. [[hardware/10-kicad-basics|KiCad Basics]] — **[Intermediate]** — turning a design into a manufacturable board: schematic vs layout, symbols vs footprints, PCB layers, decoupling, crystals, powering from USB

**Also here:** [[hardware/hardware-reference|hardware-reference]] — units, prefixes and key formulas, for lookup rather than reading. And [[hardware/interview/README|interview/]] — 25 questions across electronics/embedded and RF/IoT.

## Practice, not just notes

Unusually for this vault, **the reps already exist here** — [[projects/iot-bridge-pcb/task|the IoT Bridge PCB]] is a real internship project (~19,600 words of working notes): component selection with the reasoning, schematic notes, a KiCad walkthrough, and documentation. It's the largest single applied artefact in the vault.

Read the notes for the concepts, then read the project to see the same concepts argued about under real constraints — cost, availability, board area, and someone else's requirements.

More builds in [[project-ideas|Project Ideas]]'s hardware tier, including **rev 2 of the IoT Bridge**, which is the [[PRIMETECHIE|Rank V hardware gate]].

## Why this sits under the whole stack

Everything else in this vault assumes a working machine. This domain is where "working machine" comes from — and it's the one place where the failure modes are physical: a floating pin, insufficient decoupling, a ground loop, a trace too thin for the current. Debugging here means a multimeter and an oscilloscope rather than a stack trace, which is a genuinely different skill and one reason [[PRIMETECHIE|the path]] treats hardware as its own column rather than a hobby.

## Known gaps

Honest, in the vault's usual style:

- **Nothing on test and bring-up** — how you actually power a new board for the first time without releasing the smoke. There's a project for it in [[project-ideas|project-ideas]] and a debugging walkthrough in [[hardware/interview/01-electronics-and-embedded|the interview bank]]; the note should follow the build, not precede it.
- **No robotics** — motion, control, and autonomy are a separate direction: [[robotics/README|robotics/]], currently scaffold. The *control theory* half now exists as a track: [[engineering/02-control-theory/README|engineering/02-control-theory/]], including the digital-implementation note that covers sampling, discretisation, and fixed-point on a microcontroller.

## Related
- [[robotics/README|Robotics]] — the layer above: actuation, control, autonomy. Planned, not built
- [[engineering/02-control-theory/README|Control Theory]] — why an op-amp's feedback loop and a motor's servo loop are the same subject, and [[engineering/02-control-theory/12-digital-control|how to implement one on an MCU]]
- [[foundations/os/README|Operating Systems]] — what runs once the hardware works
- [[foundations/networking/README|Networking]] — the protocol stack above the physical layer this domain builds
- [[PRIMETECHIE|The Primetechie Path]] — where the hardware gates sit in the progression
