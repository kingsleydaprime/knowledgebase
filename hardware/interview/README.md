# Hardware — Interview Prep

From the [[hardware/README|Hardware & Embedded course]]. Two files: the electronics/embedded half, and the RF/IoT half.

## Files
1. [[hardware/interview/01-electronics-and-embedded|Electronics & Embedded]] — resistor sizing, decoupling, pull-ups, UART/I2C/SPI, interrupts, regulators, level shifting, ADC, PWM, board bring-up, RTOS
2. [[hardware/interview/02-rf-and-iot|RF & IoT]] — radio selection, link budget, antennas, MQTT, battery-life estimation, edge vs cloud, offline devices, PoE, safe OTA updates

## What these interviews actually test

Three things, in descending order of how much they separate candidates:

**1. Can you do the arithmetic out loud?** Hardware interviews are unusually numerical. Size a resistor, compute a regulator's dissipation, estimate battery life, do a link budget in dBm. These are all one-line calculations, and being fluent at them reads as experience because the people who've built things do them constantly. The people who haven't reach for a definition instead.

**2. Do you know why a component is there?** "A decoupling capacitor smooths the supply" is a definition. "It's a local charge reservoir because trace inductance can't deliver a nanosecond current spike, which is why placement matters more than value" is understanding. Every 🔥 question here has that split.

**3. Do you debug by bisection or by guessing?** [[hardware/interview/01-electronics-and-embedded|Q12]] — "the board doesn't power on" — is the hardware version of "the service is down." Same method, different instrument. Interviewers care far more about the method than about any component.

## The thing that beats every answer here

**Cite your own board.** [[projects/iot-bridge-pcb/task|The IoT Bridge PCB]] is a real design with real component choices and real tradeoffs written down. "Here's why I picked that regulator, and here's what I'd change in rev 2" outperforms any prepared answer in this folder — and it's a story almost no candidate has.

## Related
- [[hardware/README|Hardware course]] · [[INTERVIEW|Interview index]]
- [[architecture/interview/02-distributed-systems-depth|Distributed systems]] — the IoT questions on offline devices and MQTT QoS are the same conversation
- [[languages/01-java/interview/02-jvm-and-concurrency|Java: JVM & concurrency]] — `volatile` and worst-case-vs-average show up in both
