# IoT Bridge PCB — Component Selection Document

> **Status:** Draft  
> **Phase:** Component Research & Selection  
> This document justifies every major IC choice before schematic work begins. Lock this down before touching KiCad.

---

## Table of Contents

1. [Main MCU](#1-main-mcu)
2. [LoRa Transceiver](#2-lora-transceiver)
3. [Cellular Module](#3-cellular-module)
4. [Ethernet Controller](#4-ethernet-controller)
5. [PoE Controller](#5-poe-controller)
6. [Power Auto-Switching](#6-power-auto-switching)
7. [Power Regulation](#7-power-regulation)
8. [Storage](#8-storage)
9. [Passives & Connectors](#9-passives--connectors)
10. [Block Diagram](#10-block-diagram)
11. [Open Questions](#11-open-questions)

---

## 1. Main MCU

### Selected: ESP32-C6 (variant: ESP32-C6-1U-N8)

| Spec | Value |
|---|---|
| Core | Single RISC-V @ 160 MHz |
| SRAM | 512 KB (+ 16 KB RTC SRAM) |
| ROM | 320 KB |
| Flash | 8 MB (built-in, N8 variant) |
| Wi-Fi | 802.11 b/g/n/ax (Wi-Fi 6, 2.4 GHz) |
| Bluetooth | BT 5.0 LE |
| 802.15.4 radio | Zigbee 3.0 + Thread 1.3 (same radio, time-shared) |
| GPIO | 23 configurable pins |
| Interfaces | SPI, I2C, UART, I2S, USB Serial/JTAG |
| Operating temp | -40°C to +85°C |
| Package | QFN-40 or as module |

**Why this chip:**  
The ESP32-C6 collapses four radios (Wi-Fi 6, BT5, Zigbee, Thread) into a single $3–5 chip with 8MB flash on-die. No external flash chip needed for the MCU itself. The `-1U` suffix means it exposes a U.FL/IPEX antenna connector instead of a PCB trace antenna — important here because the board will be inside an enclosure. The `N8` suffix confirms 8MB flash built in.

**What it does NOT have (and how we handle it):**
- No built-in Ethernet MAC → handled by W5500 over SPI
- No LoRa radio → handled by SX1262 over SPI
- No cellular → handled by SIM7080G over UART
- No 5G/LTE → out of scope per requirements

**Zigbee + Thread note:** Both protocols share the 802.15.4 radio. They cannot run simultaneously — firmware selects one mode at boot. For this bridge that's fine; the bridge will be pre-configured for whichever mesh protocol the deployment uses.

---

## 2. LoRa Transceiver

### Selected: Semtech SX1262

| Spec | Value |
|---|---|
| Frequency range | 150 – 960 MHz (covers 433, 868, 915 MHz bands) |
| TX power | Up to +22 dBm |
| RX sensitivity | Down to –148 dBm |
| RX current | 4.2 mA |
| Sleep current | < 1.5 µA |
| Interface | SPI + 3× DIO pins |
| Modulation | LoRa (CSS), FSK, GFSK |
| Package | QFN-24 |

**Why SX1262 over SX1276:**  
The SX1262 is the current-generation chip (SX1276 is the older one on the Heltec V2). The SX1262 delivers better sensitivity (–148 vs –137 dBm), lower current consumption, and a cleaner SPI command interface. The Heltec WiFi LoRa 32 V3 (the reference board in the brief) already uses the SX1262 — studying its schematic gives us a validated reference for wiring it to an ESP32.

**Dual-role operation (hub + end-node):**  
Both modes are software-defined using the same chip:
- **Hub mode:** SX1262 listens on a configured frequency/SF, receives packets from sensor nodes, ESP32 processes and forwards upstream via WiFi/Ethernet/cellular
- **LoRaWAN end-node mode:** ESP32 runs a LoRaWAN stack (e.g., RadioLib or LMIC), SX1262 transmits join requests and data frames to a LoRaWAN network server

**Required external components:**
- TCXO or crystal for frequency accuracy (SX1262 supports both; TCXO preferred for LoRaWAN)
- RF switch if sharing the antenna between TX and RX paths (SX1262 has a built-in switch but check application note)
- 50Ω matched trace to U.FL connector or onboard antenna

---

## 3. Cellular Module

### Selected: SIMCom SIM7080G

| Spec | Value |
|---|---|
| Standard | LTE Cat-M1 + NB-IoT + EGPRS (2G fallback) |
| Bands | Global multi-band |
| Data (LTE-M) | 588 kbps DL / 1119 kbps UL |
| Data (NB-IoT) | 589 kbps DL / 1800 kbps UL |
| GNSS | Built-in (GPS, GLONASS, BeiDou) — bonus |
| Interface | UART (AT commands) |
| SIM | Physical nano-SIM slot |
| eSIM | No onboard eSIM (see note) |
| Supply voltage | 3.0 – 4.2 V |
| Package | LCC (surface mount) |

**Why SIM7080G over SIM800L:**  
The brief says "GSM/GPRS" but this is likely loose terminology — the real requirement is cellular connectivity. The SIM800L is 2G only (GPRS), and 2G networks are being shut down globally (many African and European operators have already decommissioned 2G). Designing a bridge around a dead technology is a liability. The SIM7080G gives you:
- LTE Cat-M1 and NB-IoT (the correct cellular standards for IoT in 2025+)
- 2G/EGPRS fallback for areas without LTE-M coverage
- Built-in GNSS for location tracking (free feature, very useful for an IoT bridge)
- Lower power consumption than LTE modules like SIM7600

**Why not SIM7600 / Quectel EC21:**  
Those are LTE Cat 1 modules — appropriate for higher data throughput (video, large files). An IoT bridge sending MQTT payloads doesn't need that. Cat-M1/NB-IoT is the right tier: lower power, lower cost, optimized for exactly this use case.

**eSIM note:**  
The brief requests an eSIM footprint. The SIM7080G doesn't have one, so the design should include:
1. Physical nano-SIM card holder (primary)
2. An eSIM footprint (unpopulated pads for a future discrete eSIM chip like the KIGEN OS from ARM, or a Truphone/Eseye module) — label it DNP (Do Not Populate) on the BOM

**Power supply note:**  
The SIM7080G requires 3.0–4.2V — it cannot be powered directly from a 3.3V rail or 5V rail. A dedicated LDO or small buck converter (e.g., 3.8V) is needed for the cellular module. This is standard for all SIM modules.

---

## 4. Ethernet Controller

### Selected: WIZnet W5500

| Spec | Value |
|---|---|
| Type | Hardwired TCP/IP + MAC + PHY |
| Interface to MCU | SPI (up to 80 MHz) |
| Speed | 10/100 Mbps |
| Supply | 3.3V |
| Protocols | TCP, UDP, IPv4, ICMP, ARP, IGMP, PPPoE |
| Sockets | 8 independent hardware sockets |
| Package | QFN-48 or LQFP-48 |

**Why W5500:**  
The ESP32-C6 has no Ethernet MAC. The W5500 offloads the entire TCP/IP stack to dedicated hardware — the ESP32 just writes data to it over SPI and the W5500 handles framing, checksums, and transmission. This is far more efficient than a software TCP/IP stack running on the MCU. The W5500 is massively documented, has native support in ESP-IDF and Arduino core v3.x, and is proven in thousands of production IoT designs.

**Required external components:**
- Magjack (RJ45 with integrated magnetics and PoE pairs) — e.g., **HanRun HR911105A** or similar
- 25 MHz crystal for W5500's PHY
- Decoupling caps per datasheet

---

## 5. PoE Controller

### Selected: Texas Instruments TPS23730

| Spec | Value |
|---|---|
| Standard | IEEE 802.3bt Type 3 (also compatible with 802.3af/at) |
| Max power | 51W at PD input |
| Internal switch | 0.3Ω (low heat) |
| DC-DC controller | Integrated (current-mode, flyback/active-clamp forward) |
| Classification | Class 1–6 supported |
| Package | HTSSOP-48 |

**Why TPS23730:**  
It's a full PoE PD (Powered Device) controller + DC-DC controller in one chip. It handles the IEEE 802.3bt handshake with the PSE (the PoE switch/injector), draws power from the Ethernet cable, and steps it down to usable DC. The integrated DC-DC controller means fewer external ICs. The 51W ceiling is overkill for this board (we'll draw maybe 5–10W) but gives enormous headroom and ensures compatibility with any 802.3af/at/bt PSE.

**What it outputs:**  
The TPS23730 drives an external transformer for isolation. The secondary side outputs ~12V or ~5V depending on transformer configuration. We'll target 5V output from the PoE stage, which then feeds into the power OR'ing circuit.

**Alternative (simpler):**  
If BOM cost or complexity is a concern, the **TPS2375** (8-pin, 802.3af only, ~15.4W max) + a separate DC-DC converter is a simpler approach. Downside: two chips, less power headroom. Recommend TPS23730 for this exploratory design given the brief asks for maximum features.

---

## 6. Power Auto-Switching

### Selected: Texas Instruments LM66100 × 2 (ORing configuration)

| Spec | Value |
|---|---|
| Input voltage range | 1.5 – 5.5 V |
| Max current | 1.5 A per device |
| Ron | 79 mΩ |
| Quiescent current | Low IQ |
| Package | SOT-23-5 |

**How the power tree works:**

```
PoE Input (48V, from RJ45)
    │
    ▼
TPS23730 (PoE PD Controller + DC-DC)
    │
    ▼
5V regulated (PoE path)
    │
    ├──► LM66100 #1 ──┐
                       ├──► 5V system rail ──► LDO to 3.3V
USB-C Input (5V)       │
    │                  │
    └──► LM66100 #2 ──┘
```

Two LM66100 ideal diodes in an ORing (highest-wins) configuration:
- When PoE is present and USB-C is not: PoE supplies the 5V rail, LM66100 #2 blocks reverse flow into the USB-C port
- When USB-C is present and PoE is not: USB-C supplies the 5V rail, LM66100 #1 blocks reverse flow into the PoE circuit
- When both are present: PoE takes priority (its output is regulated to exactly 5V; USB-C is also 5V — the one with marginally higher voltage wins and the other is blocked automatically)

**USB-C power delivery note:**  
For basic 5V/900mA operation (USB-C default), no PD negotiation chip is needed. If we want to negotiate higher power (9V, 12V, 20V profiles), a USB PD controller like FUSB302 would be needed. For this design, 5V default is fine — USB-C is only a fallback/programming port.

**USB-C port also serves programming/debug:**  
The ESP32-C6 has a built-in USB Serial/JTAG controller. The USB-C connector routes D+ and D- directly to the ESP32-C6's USB pins for flashing and debug — no external USB-to-UART chip (like CP2102) required.

---

## 7. Power Regulation

### 5V → 3.3V: Texas Instruments TLV1117-33 LDO

| Spec | Value |
|---|---|
| Type | LDO linear regulator |
| Output | 3.3V fixed |
| Max current | 800 mA |
| Dropout | ~1.1V at full load |
| Package | SOT-223 |

Supplies: ESP32-C6, SX1262, W5500, SD card, LEDs, button pull-ups.

### 5V → 3.8V: Separate LDO for SIM7080G

The SIM7080G requires 3.0–4.2V. A dedicated **AP2112K-3.8** or **MIC5219** LDO set to 3.8V isolates the noisy cellular module from the main 3.3V rail. This is standard practice — GSM/LTE modules draw large current spikes during transmission and can corrupt the 3.3V rail if not isolated.

---

## 8. Storage

### External Flash: Winbond W25Q64JV (if needed)

The ESP32-C6-1U-N8 already has 8MB flash on-die. This is sufficient for:
- Dual OTA partitions (~3.5MB each)
- NVS (non-volatile storage for config)
- SPIFFS/LittleFS filesystem

No additional flash chip is required. If more storage is needed in a future revision, add a W25Q128 (16MB, SPI) — footprint can be included as DNP.

### MicroSD Card Slot

Standard **push-push MicroSD slot** (e.g., Molex 1040310811 or Amphenol 101-00660-68). Connects to ESP32-C6 over SPI (shares the SPI bus with W5500 and SX1262, using separate CS lines).

**SD card notes:**
- Operates at 3.3V (SD cards are 3.3V native in SPI mode)
- 10kΩ pull-ups on MOSI, CLK, CS lines recommended
- Used for data logging and config files per the brief

---

## 9. Passives & Connectors

| Component | Part | Notes |
|---|---|---|
| RJ45 with magnetics | HanRun HR911105A or Amphenol RJE7318800310 | Integrated Bob Smith termination and PoE pairs |
| USB-C receptacle | USB4105-GF-A (GCT) or XKB U262-161N-4BVC11 | Mid-mount or top-mount, 16-pin |
| SIM card holder | Amphenol 101-00064-68 (nano-SIM, push-pull) | Standard nano-SIM, 6-pin |
| MicroSD slot | Molex 1040310811 (push-push) | SPI mode |
| Tactile button | C&K PTS636 or TE FSM4JSMATR | SMD, 4-pin, 6mm |
| Status LED | Lite-On LTST-C191TBKT (blue) or RGB: Kingbright APFA3010LSEEZGKQBKC | Driven via GPIO through 330Ω resistor |
| U.FL connectors | Hirose U.FL-R-SMT-1(80) | One each for: ESP32-C6 antenna, SX1262, cellular |

---

## 10. Block Diagram

```
                        ┌───────────────────────────────────────────────────┐
                        │                  ESP32-C6-1U-N8                   │
                        │                                                   │
                        │  Wi-Fi 6  │  BT5 LE  │  Zigbee/Thread (802.15.4) │
                        │                                                   │
   SX1262 ◄──── SPI ───►│  SPI bus                                          │
   W5500  ◄──── SPI ───►│  (shared, separate CS lines)                      │
   MicroSD◄──── SPI ───►│                                                   │
                        │  UART ────────────────────────────► SIM7080G      │
                        │                                                   │
                        │  USB D+/D─ ─────────────────────── USB-C port     │
                        └───────────────────────────────────────────────────┘
                                │                        │
                           3.3V rail                3.8V rail
                                │                        │
                         TLV1117-33               AP2112K-3.8
                                │                        │
                            ┌───┴────────────────────────┘
                            │           5V system rail
                            │
               ┌────────────┴────────────┐
               │                         │
          LM66100 #1                LM66100 #2
               │                         │
       TPS23730 (PoE)             USB-C 5V input
               │
       RJ45 + Magnetics
       (PoE 48V from switch)


Antennas (all via U.FL):
  ESP32-C6 ─────── 2.4GHz antenna  (Wi-Fi / BT / Zigbee / Thread)
  SX1262   ─────── Sub-GHz antenna (LoRa 868/915 MHz)
  SIM7080G ─────── LTE antenna
  SIM7080G ─────── GNSS antenna    (separate port on module)
```

---

## 11. Open Questions

- [ ] **Antenna placement:** All four antennas need to be separated on the PCB edge with ground plane cutouts beneath them. Need to decide board size and antenna layout before starting layout.
- [ ] **SPI bus contention:** W5500, SX1262, and MicroSD share SPI. Verify max SPI clock compatibility across all three (W5500 supports 80MHz, SX1262 supports up to 16MHz, SD cards in SPI mode up to 25MHz — run the bus at 16MHz or give each its own SPI peripheral if ESP32-C6 has multiple).
- [ ] **eSIM footprint:** Identify a specific eSIM module footprint to include as DNP pads. Candidates: Truphone TP-000-0001, Sierra Wireless WP7702.
- [ ] **USB-C CC resistors:** For 5V/900mA default draw, two 5.1kΩ pull-down resistors on CC1 and CC2 are required. Confirm no PD controller is needed for the target current budget.
- [ ] **Regulatory bands:** Confirm LoRa frequency band for target deployment region (868 MHz for EU/Africa, 915 MHz for Americas). SX1262 supports both but the BOM antenna and matching network differs.
- [ ] **ESP32-C6 SPI peripheral count:** Verify how many independent SPI peripherals the C6 exposes and whether bus sharing for W5500 + SX1262 + SD is safe given different max clock speeds.

---

## Summary BOM (Major ICs)

| # | Component | Part Number | Function |
|---|---|---|---|
| 1 | MCU | ESP32-C6-1U-N8 | Main processor, Wi-Fi 6, BT5, Zigbee, Thread |
| 2 | LoRa transceiver | Semtech SX1262 | LoRa hub + LoRaWAN end-node |
| 3 | Cellular module | SIMCom SIM7080G | LTE Cat-M1 / NB-IoT / 2G fallback + GNSS |
| 4 | Ethernet controller | WIZnet W5500 | 10/100 Ethernet over SPI |
| 5 | PoE PD controller | TI TPS23730 | 802.3bt PoE powered device + DC-DC |
| 6 | Ideal diode × 2 | TI LM66100 | PoE + USB-C power ORing |
| 7 | 3.3V LDO | TLV1117-33 | Main 3.3V rail |
| 8 | 3.8V LDO | AP2112K-3.8 | Isolated cellular supply |
| 9 | MicroSD slot | Molex 1040310811 | Local storage |
| 10 | USB-C receptacle | USB4105-GF-A | Power + programming |
| 11 | RJ45 w/ magnetics | HR911105A | Ethernet + PoE input |
| 12 | nano-SIM holder | Amphenol 101-00064-68 | Physical SIM |
