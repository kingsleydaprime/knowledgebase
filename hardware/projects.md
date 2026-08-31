# Hardware & Embedded — Projects

*The one domain where you have **more built than written** — [[projects/iot-bridge-pcb/documentation|the IoT bridge]] is a board that physically exists. So this needs the fewest new projects and gives the fastest returns.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## The ladder

- 🟢 **Blink, but properly** — get an LED blinking on a bare microcontroller with **no Arduino framework**: registers directly, your own delay, read the datasheet for the GPIO section. The "hello world" that actually teaches something, because the abstraction you skipped is the whole lesson ([[hardware/03-embedded-systems|GPIO & the firmware loop]]).
- 🟢 **Talk to a sensor over I2C** — wire a temperature/IMU sensor, write the driver yourself from the datasheet rather than importing a library: address it, read its registers, convert the raw value. Then put a scope or logic analyser on the bus and *watch the transaction you wrote* ([[hardware/05-communication-protocols|UART/I2C/SPI]]).
- 🟢 **Instrument your own power** — measure the actual current draw of a board in idle, active, and sleep, and make a number-backed claim about how long it would run on a given battery. Turns "power budget" from a phrase into arithmetic.
- 🟡 **Design a small board and have it fabbed** — something genuinely simple (a breakout, a sensor node, a USB-powered widget): schematic → footprints → layout → gerbers → order it → bring it up. The [[hardware/10-kicad-basics|KiCad]] workflow end to end, at a scale where a mistake costs £15 and a fortnight rather than a project.
- 🟡 ⭐ **Rev 2 of the IoT Bridge** — you have a board and you have notes on what you'd change. Do the revision: fix what rev 1 got wrong, and write up the diff and *why*. **Designing a rev 2 is a different and more valuable skill than designing a rev 1**, and it's the [[PRIMETECHIE|Rank V hardware gate]] almost nobody has.
- 🟡 **Bring-up procedure, written down** — take a new board and document the order you power and verify it: continuity before power, current-limited first power-on, rails measured against the schematic, then clocks, then comms. Then use it on the next board. The checklist that stops you releasing the smoke.
- 🟡 **Firmware you can update over the air** — an ESP32 that fetches and applies its own firmware update, with a rollback path when the new image doesn't boot. Ties [[hardware/03-embedded-systems|embedded]] to [[foundations/networking/README|networking]] and to the "design for failure" instinct from [[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]].
- 🔴 **A device fleet that survives a bad network** — several nodes reporting to a server they can't always reach: local buffering, reconnect with backoff, and a defensible answer for what happens when two nodes resync with conflicting data. This is [[architecture/04-distributed-systems/README|distributed systems]] with a physical body, and it's the [[PRIMETECHIE|Rank IV hardware analogue]].
- 🔴 **Debug something electrical and prove it** — take a fault you'd normally guess at and instrument it instead: scope the rail, find the noise, identify the cause (insufficient decoupling, ground bounce, a trace carrying more current than it should), fix it, and show the before/after trace. The hardware equivalent of a flame graph.


## If you only do one

**Rev 2 of the IoT Bridge.** You already have the hard-won knowledge from rev 1; applying it is cheaper than any new project and produces a visibly better artefact.


## Related

- [[hardware/README|the hardware course]] · [[hardware/interview/README|interview bank]]
- [[projects/iot-bridge-pcb/documentation|the IoT bridge project log]] — the vault's largest applied project
- [[project-ideas|Project Ideas]] — the vault-wide index
