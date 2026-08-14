# Radio Frequency (RF)

**[Intermediate → Advanced]** — The longest note here, and the one with the least intuition available for free: spectrum, modulation, link budgets, antennas, and the IoT radio protocols you'll actually meet.

This is where embedded systems get wild. RF is how your devices talk wirelessly — and understanding it separates people who copy-paste WiFi examples from people who can actually design reliable wireless systems.

## The Electromagnetic Spectrum

Radio waves are electromagnetic radiation, just like visible light — but at much lower frequencies and therefore much longer wavelengths. The relationship:

```
Speed of light = Frequency × Wavelength
c = f × λ
```

At 2.4 GHz (WiFi frequency): λ = 300,000,000 / 2,400,000,000 = **12.5 cm**

At 433 MHz (common IoT band): λ = 300,000,000 / 433,000,000 = **69 cm**

Why does wavelength matter? It determines antenna size, penetration through walls, and range.

| Band | Frequency | Wavelength | Used for |
|---|---|---|---|
| LF/MF | 30kHz–3MHz | 100m–10km | AM radio, RFID |
| HF | 3–30MHz | 10–100m | Shortwave radio |
| VHF | 30–300MHz | 1–10m | FM radio, TV |
| UHF | 300MHz–3GHz | 10cm–1m | WiFi, Bluetooth, LoRa, GSM, GPS |
| SHF | 3–30GHz | 1–10cm | 5G, radar, satellite |

## Modulation — How Data Gets onto a Radio Wave

A raw carrier wave carries no information — it's just a sine wave at a fixed frequency. Modulation is the process of changing some property of the carrier wave to encode data.

**Analog modulation:**
- **AM (Amplitude Modulation)** — vary the wave's height (amplitude) to encode signal. Susceptible to noise. AM radio.
- **FM (Frequency Modulation)** — vary the frequency slightly around the carrier. Much more noise-resistant. FM radio.

**Digital modulation (what IoT uses):**
- **OOK (On-Off Keying)** — simplest: 1 = carrier ON, 0 = carrier OFF. Those cheap 433MHz modules use this.
- **FSK (Frequency Shift Keying)** — 1 = slightly higher frequency, 0 = slightly lower. More robust than OOK. Used by LoRa, Bluetooth Classic.
- **GFSK (Gaussian FSK)** — FSK with a Gaussian filter applied to smooth transitions. Bluetooth Low Energy uses this.
- **BPSK / QPSK (Phase Shift Keying)** — encode data by shifting the phase of the carrier. Efficient, used in GPS signals and some ZigBee implementations.
- **LoRa (Chirp Spread Spectrum)** — not traditional modulation. Uses *chirps* — signals that sweep across a bandwidth. Wildly interference-resistant. The reason LoRa achieves 15km range at milliwatt power levels.

## RF Power and Link Budget

Everything in RF is measured in **dBm** (decibels relative to 1 milliwatt):
- 0 dBm = 1 mW
- 10 dBm = 10 mW
- 20 dBm = 100 mW
- 30 dBm = 1 W
- -40 dBm = 0.0001 mW

Your receiver has a **sensitivity floor** — the minimum signal it can detect. The ESP32's WiFi receiver sensitivity is around **-97 dBm**. Anything weaker than that and the packet is lost.

A link budget is the calculation of whether your signal will make it:

```
Received Power = Tx Power + Tx Antenna Gain - Path Loss + Rx Antenna Gain
```

If received power > receiver sensitivity, your link works. Add a margin (fade margin) for uncertainty.

**Path loss** — radio waves spread out (inverse square law: power drops with distance squared) and get absorbed by objects. 2.4GHz signals are heavily absorbed by water... and the human body is mostly water. This is why your WiFi drops when you stand between the router and the device.

## Antennas

An antenna converts electrical energy into electromagnetic waves (transmitting) and vice versa (receiving). Key specs:

- **Gain (dBi)** — how much the antenna focuses energy in a particular direction compared to a perfect sphere radiator. A dipole antenna has ~2.15 dBi gain. A high-gain directional antenna might have 15 dBi — but only in one direction.
- **Impedance** — antennas have impedance (typically 50Ω). Mismatching impedance between the antenna and the radio causes reflections, reducing efficiency and potentially damaging the transmitter.
- **Polarization** — the orientation of the electric field. A vertical antenna works best with another vertical antenna. Mismatched polarization = up to 20 dB signal loss.

**Quarter-wave antenna:** The simplest usable antenna. Length = λ/4. At 2.4GHz: 31mm. At 433MHz: 173mm. That wire sticking out of your ESP32 dev board IS the antenna.

**PCB trace antenna:** A carefully designed copper trace on the PCB that acts as an antenna. Compact, no extra cost. The ESP32's on-board antenna is this type.

**Chip antenna:** Tiny ceramic component, mounted on the PCB. Even more compact, slightly less efficient.

## The IoT Radio Protocols You'll Actually Use

### WiFi (802.11)
2.4GHz and 5GHz bands. Up to hundreds of Mbps throughput. The infrastructure is already everywhere. Drawbacks: power-hungry (ESP32 WiFi active ~80mA vs deep sleep ~10µA), requires an access point.

Good for: devices that are mains-powered, need internet access, transfer lots of data.

### Bluetooth Classic vs BLE

**Bluetooth Classic** — high throughput (up to 3 Mbps), continuous connection, designed for audio streaming (headphones, speakers). Power hungry, short range (~10m).

**Bluetooth Low Energy (BLE)** — completely different from Classic despite the shared brand name. Optimized for extremely low power. Devices can advertise data without maintaining a connection (beacon mode). A coin cell battery can power a BLE sensor for years. Range: 10-100m. Throughput: up to ~1 Mbps but typically much less.

BLE is the protocol behind AirTags, fitness trackers, smart locks, and beacon advertising. On ESP32 and nRF52840, BLE is first-class.

### WiFi 4 vs WiFi 5 vs WiFi 6

The numbers are marketing names for generations of the 802.11 standard:

| Generation | Standard | Year | Max Speed | Key addition |
|---|---|---|---|---|
| WiFi 4 | 802.11n | 2009 | 600 Mbps | MIMO, 5GHz support |
| WiFi 5 | 802.11ac | 2013 | 3.5 Gbps | MU-MIMO, wider channels |
| WiFi 6 | 802.11ax | 2019 | 9.6 Gbps | OFDMA, TWT, BSS Coloring |

For general internet use, the speed jumps matter. For IoT, two WiFi 6 features matter most:

**OFDMA** — WiFi 4 and 5 serve one device at a time on a channel. WiFi 6 splits the channel into sub-channels and serves multiple devices simultaneously. In a house with 50 smart devices all trying to send data, WiFi 6 handles it far more efficiently.

**TWT (Target Wake Time)** — a device negotiates a schedule with the router: "wake me up every 10 minutes to send my packet, let me sleep otherwise." Between those windows, the WiFi radio is fully off. This dramatically extends battery life for IoT sensors. WiFi 4/5 have no equivalent — devices must stay awake continuously polling for data.

### Zigbee (802.15.4)
Mesh networking protocol in the 2.4GHz band. Devices can relay messages through each other — a Zigbee sensor at the far end of your house routes its packet through intermediate Zigbee devices to reach the hub. Self-healing, low power, up to hundreds of devices per network. Used heavily in smart home (Philips Hue, IKEA Tradfri).

**How Zigbee mesh works:**
```
Sensor (far away)
    │ (too far for direct connection)
    ▼
Smart bulb         ← relays the message
    │
    ▼
Smart plug         ← relays the message
    │
    ▼
Zigbee Hub         ← receives it, sends to cloud
```

Requires a central **coordinator** to manage the network. Not IP-based — devices use Zigbee-specific addressing, not internet addresses.

### Thread — Zigbee's IP-Based Successor

Thread runs on the **same 802.15.4 radio** as Zigbee but is fundamentally different in design. The key difference: Thread is **IP-based**. Every Thread device gets a real IPv6 address, so it can be addressed and reached like any device on the internet — no proprietary addressing scheme.

No single coordinator required — any device can act as a border router. The network is truly decentralised and self-healing.

Thread is the foundation of **Matter** — the universal smart home standard created by Apple, Google, Amazon, and Samsung to make all smart home devices work together regardless of brand. Any device that supports Matter over Thread works with HomeKit, Google Home, Alexa, and SmartThings simultaneously.

**Zigbee vs Thread at a glance:**

| | Zigbee | Thread |
|---|---|---|
| Radio | 802.15.4 | 802.15.4 (same) |
| IP-based | No | Yes (IPv6) |
| Coordinator needed | Yes | No |
| Current install base | Massive | Growing fast |
| Future direction | Mature/stable | Powers Matter standard |
| Real devices using it | Philips Hue, IKEA, SmartThings | Apple HomePod, Nanoleaf, Eve |

In practice: an IoT bridge that speaks both covers the existing market (Zigbee) and the future market (Thread/Matter) from one device.

### LoRa / LoRaWAN
**LoRa** is the physical layer modulation (chirp spread spectrum). **LoRaWAN** is the network protocol on top of it.

The stats are staggering: 15+ km range in rural environments, power consumption low enough that a small battery lasts years, all at the cost of very low data rate (250 bps to 50 kbps).

LoRa is ideal for: agricultural sensors, asset tracking, remote monitoring in places with no WiFi. A LoRaWAN gateway can cover an entire city and serve thousands of end nodes.

The trade-off: you cannot stream data. LoRa is for small, infrequent packets (temperature every 10 minutes, GPS coordinates every hour). Send too frequently and you violate duty cycle regulations (in many countries you're limited to 1% duty cycle in unlicensed bands).

**LoRa modules vs bare chip — the two ways to use LoRa:**

There are two approaches to adding LoRa to a design:

**1. LoRa Module (e.g. REYAX RYLR998)**
A fully integrated module: the SX1262 chip + RF matching circuit + antenna connector + a small MCU for processing — all on a tiny pre-built board. You talk to it over **UART using AT commands** (plain text commands like `AT+SEND=0,5,HELLO`). No SPI, no register configuration, no RF matching to design. Plug it into your breadboard, send text commands, it transmits. Used for: prototyping, quick projects, situations where simplicity matters more than PCB space.

```
Your MCU ──UART──► RYLR998 module ──RF──► (air)
          (AT commands)
```

**2. Bare LoRa Chip (e.g. Semtech SX1262)**
The raw IC soldered directly onto your PCB. You talk to it over **SPI**, sending raw register values and opcodes. You're responsible for the RF matching network, antenna design, and implementing the LoRa protocol stack in firmware. More complex, but: smaller footprint on the PCB, lower cost at volume, full control over every parameter.

```
Your MCU ──SPI──► SX1262 chip ──RF matching──► antenna
          (registers/opcodes)
```

**The connection:** The RYLR998 module is built around the SX1262 chip inside. When you sent AT commands to the RYLR998, the module's internal MCU was translating those commands into SPI register writes to an SX1262 — exactly what we now do directly in firmware on the IoT Bridge PCB.

### NB-IoT and LTE-M
Cellular IoT — runs on 4G/5G infrastructure. NB-IoT is ultra-narrowband, low power, designed for static devices (smart meters, parking sensors). LTE-M supports slightly higher data rates and mobility. Both require a SIM and cellular subscription but give you global coverage without deploying any infrastructure yourself.

### NFC (Near Field Communication)
Operates at 13.56MHz, range: a few centimeters maximum. Standardized protocol stack designed for smartphones. Used for contactless payments, access cards, pairing initiation. The short range is a feature — you have to physically bring devices together, making accidental reads impossible.

### RFID
**Radio Frequency Identification**. A reader emits an RF field that powers a passive tag (no battery in the tag), reads its ID.

- **Low Frequency (125 kHz)** — shorter range, used in older access control cards, animal microchips
- **High Frequency (13.56 MHz)** — NFC lives here. Library cards, contactless payments, RC522 module on your workbench
- **Ultra High Frequency (860-960 MHz)** — longer range (up to meters), used in warehouse inventory, supply chain, retail

### 433 MHz / 315 MHz Modules
The cheapest RF modules on the market. OOK modulation, no addressing, no error correction. A transmitter blasts a signal, every receiver in range picks it up. Used for: garage door openers, remote controls, cheap sensor packages. Fine for simple command-and-control but don't expect reliability — they're brutal to anything that needs guaranteed delivery.

## Interference and Coexistence

The 2.4GHz band is chaos. WiFi (11 channels), Bluetooth (frequency-hops across 79 channels), Zigbee, microwave ovens — all sharing the same spectrum. Bluetooth handles this with adaptive frequency hopping. WiFi uses CSMA/CA (listen before transmitting). But in dense environments, all of these degrade.

Sub-1GHz (433MHz, 868MHz, 915MHz) is much less congested — fewer devices operate there, and the longer wavelengths penetrate walls and ground better. This is why LoRa, Sigfox, and Z-Wave chose this space.

---

## Related
- [[hardware/05-communication-protocols|Communication Protocols]] — the wired equivalents
- [[hardware/07-connectivity|Connectivity]] — choosing between radio and a cable
- [[hardware/08-iot-architecture|IoT Architecture]] — what these radios carry
