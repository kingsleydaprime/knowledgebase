# Internship Project: IoT Bridge PCB Design

## Overview

Design a **universal IoT Bridge PCB** — a central hub for onboarding, managing, and facilitating communication between various IoT edge devices.

This is an **exploratory design**. The goal is to test component compatibility, feature integration, and layout strategies. Some elements may or may not make it into the final production version — design for **maximum flexibility and modularity**.

---

## Requirements

### 1. Wireless Communication

| Protocol | Purpose |
|---|---|
| **Wi-Fi & Bluetooth** | Local network access and short-range device pairing |
| **Thread & Zigbee** | Low-power mesh networking with smart devices |
| **LoRa** | Dual role: hub for far-away nodes AND end-node to a LoRaWAN gateway |
| **Cellular (GSM/GPRS)** | Cellular connectivity with physical SIM slot + eSIM footprint |

LoRa is the tricky one — the bridge must operate in **two modes**:
- As a **local LoRa hub**: receives packets from far-away sensor nodes
- As a **LoRaWAN end-node**: forwards data upstream to a LoRaWAN network server

### 2. Wired Connectivity & Power Management

- **Ethernet + PoE** — RJ45 with Power over Ethernet circuitry to power the device from the network cable
- **USB-C** — fallback power source when PoE is unavailable; also used for programming/debugging
- **Power auto-switching** — safe handling of dual inputs (PoE + USB-C) with no component damage

### 3. Memory & Storage

- **Flash Memory** — minimum 8MB to support:
  - Dual firmware partitions (OTA updates)
  - Filesystem storage
- **MicroSD slot** — removable storage for local data logging and config files

### 4. User Interface

- **Utility button** — tactile push-button for reset, pairing mode, etc.
- **Utility LED** — single or RGB indicator for device status

---

## Reference Architectures to Study

| Reference | What to take from it |
|---|---|
| **ESP32-C6-1U-N8** | Strong MCU candidate — native Wi-Fi 6, BT5 LE, Zigbee, Thread, 8MB flash built in |
| **Heltec WiFi LoRa 32 (V3)** | Study the schematic for how ESP32 integrates with an SX1262 LoRa transceiver over SPI |

---

## Tools

- **KiCad** (preferred)
- Altium Designer or Eagle also acceptable

---

## Deliverables

### 1. Component Selection Document (PDF/Word)
- List of all major ICs and modules chosen: MCU, LoRa transceiver, GSM module, PoE controller, etc.
- Brief justification for each choice: cost, availability, footprint, compatibility
- High-level **block diagram** showing how components interface

### 2. PCB Design Files
- [ ] Complete schematic files
- [ ] Complete PCB layout files
- [ ] Generated BOM (Bill of Materials)
- [ ] Gerber files ready for manufacturing

---

## Notes & Blockers

> Document any component availability issues or footprint constraints here. Flag for review session if blocked.

---

## Key Design Decisions to Make

- [ ] Confirm MCU: ESP32-C6 vs alternatives (nRF9160 for cellular? separate cellular module?)
- [ ] LoRa transceiver: SX1262 (likely — matches Heltec V3 reference)
- [ ] GSM module: SIM800L vs SIM7600 vs Quectel EC21 (depends on required data speed)
- [ ] PoE controller IC selection (e.g., AG9800, TPS23730)
- [ ] Power switching circuit: PoE + USB-C priority logic (ideal diode controller like LM66100 or similar)
- [ ] Ethernet PHY: standalone IC (e.g., W5500) vs MCU with built-in MAC + external PHY
