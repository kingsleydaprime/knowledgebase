# Communication Protocols

**[Intermediate]** — How chips on a board talk to each other: UART, I2C, SPI, I2S, CAN and 1-Wire — and how to choose between them.

Microcontrollers need to talk to sensors, displays, other MCUs, and the cloud. These are the protocols that make that happen.

## UART — The Simplest

**Universal Asynchronous Receiver-Transmitter**. Two wires: TX (transmit) and RX (receive). Point-to-point, full-duplex (both sides talk simultaneously).

- No clock wire — both sides agree on a **baud rate** (bits per second) in advance. Common: 9600, 115200 bps.
- "Asynchronous" — no shared clock signal, timing is inferred from start/stop bits framing each byte.
- Used for: debug output (Serial Monitor in Arduino), GPS modules, Bluetooth serial modules (HC-05), GSM modems.

```
Device A TX ──────────────► Device B RX
Device A RX ◄────────────── Device B TX
GND ─────────────────────── GND
```

Cross the wires: A's TX goes to B's RX. If you connect TX-to-TX, nothing works (and you might damage things).

## I2C — Many Devices, Two Wires

**Inter-Integrated Circuit** (pronounced "I-squared-C"). Two wires: **SDA** (data) and **SCL** (clock). One master, up to 127 slaves on the same two wires.

Every device on the I2C bus has a unique 7-bit address (e.g., 0x68 for an MPU-6050 IMU). The master initiates all communication by putting the target device's address on the bus. Slaves only respond when addressed.

- Speed: 100kHz (standard mode), 400kHz (fast mode), 1MHz+ (fast-plus/high-speed)
- Needs pull-up resistors on SDA and SCL (typically 4.7kΩ to VCC)
- Perfect for: sensors (temperature, IMU, barometric pressure), small displays (SSD1306 OLED), EEPROMs

The magic: you can chain a temperature sensor, a barometric sensor, an IMU, and a real-time clock all on two wires.

## SPI — Fast and Simple

**Serial Peripheral Interface**. Four wires: **MOSI** (Master Out Slave In), **MISO** (Master In Slave Out), **SCLK** (clock), **CS/SS** (Chip Select, one per device).

SPI is synchronous (clock is explicit) and full-duplex. It's significantly faster than I2C — can run at 10MHz, 50MHz, even 80MHz on some systems. The tradeoff: one CS wire per device, so many devices means many pins.

Used for: SD cards, SPI Flash chips, high-speed ADCs, displays (ILI9341 TFT), Ethernet controllers, RF transceivers (nRF24L01, CC1101).

## I2S — For Audio

**Inter-IC Sound**. Three wires: SCK (clock), WS (word select, left/right channel), SD (serial data). Designed specifically for transmitting digital audio between chips — microphones (INMP441, SPH0645), DACs, codecs. If you're doing speech recognition or audio recording on an ESP32, you'll use I2S.

## CAN Bus — The Automotive Standard

**Controller Area Network**. Two wires: CAN-H and CAN-L (differential pair). Designed for noisy environments — automotive, industrial machinery. Multiple masters, collision-detection built in, messages are identified by ID not by address. Your car uses CAN bus to let the ECU, ABS module, airbag controller, and dashboard all talk to each other. You'll encounter this in automotive IoT and industrial applications.

## 1-Wire

Exactly what it sounds like — one data wire (plus ground). Developed by Dallas/Maxim. The DS18B20 waterproof temperature sensor uses this. Each device has a unique 64-bit ROM code burned in at the factory so you can address multiple sensors on one wire. Slow but brilliantly simple for temperature sensing.

## Choosing the Right Protocol

| Need | Use |
|---|---|
| Debug output / GPS / GSM | UART |
| Multiple sensors, low speed | I2C |
| High speed, displays, SD cards, RF transceivers | SPI |
| Audio | I2S |
| Automotive / industrial | CAN |
| Waterproof temp sensors, daisy-chained | 1-Wire |

---

## Related
- [[hardware/04-microcontrollers|Microcontrollers]] — the peripherals that speak these
- [[hardware/06-radio-frequency|Radio Frequency]] — talking without wires
- [[projects/iot-bridge-pcb/schematic-notes|IoT Bridge — schematic notes]] — these buses on a real board
- [[foundations/networking/README|Networking]] — the same layering idea, several orders of magnitude up
