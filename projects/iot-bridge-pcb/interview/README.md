# IoT Bridge PCB — Interview Questions

Questions an interviewer could realistically ask **about this project**, drawn from
[`../component-selection.md`](../component-selection.md),
[`../schematic-notes.md`](../schematic-notes.md),
[`../kicad-walkthrough.md`](../kicad-walkthrough.md) and
[`../documentation.md`](../documentation.md).

A multi-radio IoT gateway board: ESP32-C6 MCU, SX1262 LoRa, SIM7080G cellular, W5500 Ethernet with
PoE, USB-C, microSD — designed in KiCad.

This is the only **hardware** project in the vault, which makes it disproportionately memorable in a
software interview and essential to know cold in a hardware or embedded one.

## How to use this

- **Answer out loud, from memory, before reading the hint.**
- **Strong answer covers** = the checklist a good answer hits, not a script.
- **[Beginner] / [Intermediate] / [Advanced]** = how much project context the question assumes.
- 🔥 = most likely to be asked.

## Files

| File | Covers |
|---|---|
| [01-architecture-and-components.md](01-architecture-and-components.md) | Why each part was chosen, the alternatives rejected, radio/interface trade-offs |
| [02-power-and-rf.md](02-power-and-rf.md) | PoE, ORing auto-switch, regulation, rail separation, the RF switch, antenna/magnetics |
| [03-schematic-workflow-and-story.md](03-schematic-workflow-and-story.md) | KiCad process, ERC, PWR_FLAG, what's left, trade-offs, behavioural |

---

## Before anything else: the 60-second pitch

> It's an IoT bridge board — a gateway that collects from local devices over LoRa, Zigbee or Thread
> and backhauls over whichever link is available: Ethernet with PoE, cellular, or Wi-Fi. ESP32-C6 as
> the MCU because its 802.15.4 radio gives Zigbee and Thread alongside Wi-Fi 6 on one chip, SX1262
> for LoRa at 868 MHz since Nigeria is ITU Region 1, SIM7080G for LTE-M/NB-IoT with 2G fallback, and
> a W5500 for Ethernet because it's a hardwired TCP/IP stack rather than a raw MAC — the ESP32
> doesn't have to run a software stack for it. The decisions I'd defend hardest are on the power
> side: three inputs — PoE, USB-C and a barrel jack — auto-switched with ORing ideal-diode
> controllers, and a **separate 3.8V LDO for the cellular modem** specifically so its transmit
> current spikes can't sag the 3.3V rail everything sensitive runs on.

The cellular rail separation is the line to lead with — it's the decision that shows you understand
what actually kills mixed-signal boards.

---

## Key parts (memorise this table)

| Function | Part | One-line reason |
|---|---|---|
| MCU | ESP32-C6-WROOM-1-N8 (module) | Wi-Fi 6 + BLE + 802.15.4 (Zigbee/Thread) on one RISC-V chip; module = pre-certified RF |
| LoRa | Semtech SX1262 | 150–960 MHz, +22 dBm TX, –148 dBm sensitivity, <1.5 µA sleep |
| RF switch | Skyworks PE4259 | SPDT; SX1262 has separate TX/RX ports, one antenna |
| Cellular | SIMCom SIM7080G | LTE-M + NB-IoT + EGPRS fallback, GNSS bonus, UART/AT |
| Ethernet | WIZnet W5500 | **Hardwired** TCP/IP, 8 sockets, SPI to MCU |
| PoE | TI PPS23730A0RMTT | 802.3af/at with integrated DC-DC controller |
| Power ORing | TI LM66100 ×2 | Ideal-diode auto-switching between sources |
| 3.3V rail | TI TLV1117-33 LDO | 800 mA, SOT-223 |
| 3.8V rail | Separate LDO | Isolates cellular current spikes |
| RJ45 | HR911105A MagJack | Integrated magnetics — no separate transformer |
