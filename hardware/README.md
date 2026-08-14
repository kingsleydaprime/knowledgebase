# Hardware & Embedded

The layer below all the software. Electricity → signals → microcontrollers → boards that exist physically and can be wrong in ways no compiler catches.

**~31,000 words across notes and one real project** — this domain was filed as "unordered reference material" until August 2026, which badly understated it. It's a course plus a finished build; it just doesn't use the numbered-folder shape the other courses do.

## Reading order

1. [[hardware/fundamentals|Hardware & IoT Fundamentals]] — **[Beginner → Intermediate]** — the whole foundation in one long note, in this order:
   - **Electricity** — Ohm's law, power, AC/DC, regulators, ground, transistors, capacitors (and why decoupling caps are the ones that matter)
   - **Digital vs analog** — ADC, DAC, PWM: the bridges between the real world and a CPU
   - **Embedded systems** — bare metal vs RTOS, memory, the firmware loop, GPIO
   - **Microcontrollers** — AVR/Arduino, ESP32, STM32 and how to choose
   - **Communication protocols** — UART, I2C, SPI: how chips talk on a board
   - **RF and connectivity** — radio basics, Ethernet vs WiFi vs cellular vs PoE
   - **IoT architecture** — putting it together into a system
2. [[hardware/kicad-basics|KiCad Basics]] — **[Intermediate]** — turning a design into a manufacturable board: schematic vs layout, symbols vs footprints, PCB layers, decoupling, crystal oscillators, powering from USB

## Practice, not just notes

Unusually for this vault, **the reps already exist here** — [[projects/iot-bridge-pcb/task|the IoT Bridge PCB]] is a real internship project (~19,600 words of working notes): component selection with the reasoning, schematic notes, a KiCad walkthrough, and documentation. It's the largest single applied artefact in the vault.

Read [[hardware/fundamentals|fundamentals]] for the concepts, then read the project notes to see the concepts being argued about under real constraints.

Also: [[blog-drafts/reading-a-datasheet|reading a datasheet]] — a draft on the skill that separates people who can use a component from people who can only copy a reference design.

## Why this sits under the whole stack

Everything else in this vault assumes a working machine. This domain is where "working machine" comes from — and it's the one place where the failure modes are physical: a floating pin, insufficient decoupling, a ground loop, a trace too thin for the current. Debugging here means a multimeter and an oscilloscope rather than a stack trace, which is a genuinely different skill and one reason [[PRIMETECHIE|the path]] treats it as its own discipline rather than a hobby.

## Known gaps

Honest, in the vault's usual style:

- **`fundamentals.md` is one 8,656-word monolith.** It has a table of contents and reads fine, but it doesn't split into the numbered notes the other courses use. Splitting it would make it linkable at section level.
- **No interview bank** — every other built-out domain has one.
- **Nothing on test and bring-up** — how you actually power a new board for the first time without releasing the smoke.
- **No robotics** — motion, control, and autonomy are a separate direction: [[robotics/README|robotics/]], currently scaffold.

## Related
- [[robotics/README|Robotics]] — the layer above this one: actuation, control, autonomy. Planned, not built
- [[foundations/os/README|Operating Systems]] — what runs once the hardware works
- [[foundations/networking/README|Networking]] — the protocol stack above the physical layer this domain builds
- [[PRIMETECHIE|The Primetechie Path]] — where hardware gates sit in the progression
