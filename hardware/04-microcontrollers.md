# Microcontrollers

**[Beginner → Intermediate]** — The chips themselves — AVR, ESP32, STM32, RP2040, nRF52840 — how you get code onto them, and why clocks matter more than beginners expect.

A microcontroller (MCU) is a complete computer on a single chip — CPU, memory (Flash + SRAM), and peripherals (GPIO, ADC, UART, SPI, I2C, timers) all in one package. Compare this to a microprocessor (like the Intel chip in your laptop) which is just the CPU — it needs external RAM, storage, and peripherals.

## The Big Players

### AVR / Arduino (ATmega328P)
The classic entry point. The Arduino Uno's ATmega328P runs at 16 MHz, has 32KB flash, 2KB SRAM. Painfully limited by modern standards but: the ecosystem is enormous, the learning curve is gentle, and the simplicity forces you to understand what's actually happening.

Use it for: learning, simple sensors/actuators, projects that don't need WiFi or a lot of processing.

### ESP32 (Espressif)
The microcontroller that changed IoT. Dual-core 240MHz processor, 520KB SRAM, built-in WiFi AND Bluetooth/BLE, dozens of GPIO pins, ADC, DAC, hall sensor, touch sensing. And it costs about $3.

The ESP32 is where most hobbyist and professional IoT projects live. You can program it with Arduino IDE (same familiar syntax), ESP-IDF (Espressif's native C framework), MicroPython, or Rust.

The ESP8266 was the predecessor — WiFi only, single core, less RAM — but you'll still see it everywhere because it's even cheaper.

### STM32 (STMicroelectronics)
The professional's MCU. ARM Cortex-M core, available in variants from tiny M0 (like an AVR but more capable) up to M7 running at 480MHz. Used in industrial equipment, medical devices, automotive. STM32 is what you learn when you want to take embedded seriously.

Key concepts STM32 forces you to learn: clock trees, DMA (Direct Memory Access), HAL vs LL drivers, STM32CubeIDE. It's more complex but the ceiling is very high.

### RP2040 (Raspberry Pi Pico)
Raspberry Pi's own silicon. Dual-core ARM Cortex-M0+, 264KB SRAM, 2MB flash, runs at 133MHz. The party trick: **PIO (Programmable I/O)** — dedicated state machines that can bit-bang arbitrary protocols in hardware without using CPU cycles. Brilliant for high-speed communication, LED strips (WS2812), custom protocols. MicroPython support is first-class.

### nRF52840 (Nordic Semiconductor)
The gold standard for Bluetooth Low Energy (BLE) and Thread/Zigbee applications. ARM Cortex-M4 with FPU, 1MB flash, 256KB SRAM, and an ultra-low-power radio. If you're building a wearable, a BLE sensor, or a mesh network node, this chip shows up constantly.

## How You Program a Microcontroller

Your code is compiled on your computer into machine code (a `.bin` or `.hex` file), then flashed to the MCU's Flash memory over a programming interface:

- **USB-to-Serial / Bootloader** — easiest. The MCU has a built-in bootloader that accepts firmware over UART. Arduino works this way.
- **SWD (Serial Wire Debug)** — ARM standard. Two wires (SWDIO + SWDCLK), requires an ST-Link, J-Link, or similar probe. Gives you real-time debugging (breakpoints, variable inspection) — invaluable.
- **JTAG** — older, more pins (4-5), full debug capability. Still common on older chips.

## Clocks and Timing

Every MCU has a clock — a crystal or internal oscillator that pulses at a fixed frequency. Every instruction takes a certain number of clock cycles to execute. At 16 MHz, you get 16 million cycles per second. At 240 MHz (ESP32), 240 million.

`delay(1000)` in Arduino burns 1 second doing literally nothing — the CPU is stuck in a counting loop. In real embedded code you avoid busy-waiting and instead use timers and interrupts to do things at specific intervals without blocking.

---

## Related
- [[hardware/03-embedded-systems|Embedded Systems]] — what you're programming them to do
- [[hardware/05-communication-protocols|Communication Protocols]] — how they talk to everything else
- [[hardware/10-kicad-basics|KiCad Basics]] — power pins, crystals, and wiring one onto a board
