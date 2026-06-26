# IoT Bridge — Schematic Notes

> Running log of decisions, wiring details, and gotchas encountered while drawing the schematic. Update this as you go.

---

## Progress

- [ ] Power Section
- [x] ESP32-C6 — 3V3 supply + decoupling caps (10µF + 100nF)
- [x] ESP32-C6 — EN/CHIP_PU circuit (10kΩ pull-up + 100nF cap)
- [x] ESP32-C6 — BOOT/GPIO9 circuit (10kΩ pull-down + SW_Push button)
- [x] ESP32-C6 — PWR_FLAG on +3V3 and GND nets
- [x] ESP32-C6 — GPIO net labels
- [x] ESP32-C6 — No-connect markers on unused pins
- [x] USB-C Connector
- [ ] SX1262 (LoRa)
- [ ] W5500 (Ethernet)
- [ ] SIM7080G (Cellular)
- [ ] USB-C Connector
- [ ] MicroSD Slot
- [ ] User Interface (Button + LED)
- [ ] SWD Debug Header
- [ ] ERC clean (0 errors)

---

## Section 1 — Power

### What to place in KiCad

**USB-C Connector (USB4105-GF-A)**
- VBUS pin → fuse (500mA polyfuse) → power net labeled `USB_5V`
- D+ and D- → wire to MCU (label them `USB_DP` and `USB_DM`)
- CC1 and CC2 → each gets a **5.1kΩ resistor to GND** (tells the USB host this is a device that wants 5V/900mA)
- SHIELD / GND pins → GND

**LM66100 #1 (PoE 5V side)**
- IN → net labeled `POE_5V` (comes from TPS23730 output)
- OUT → net labeled `+5V` (system rail)
- GND → GND
- CE → GND (CE is active-low — pulling LOW keeps chip always enabled)
- ST → no-connect (status output, not needed)
- Add 100nF decoupling cap from IN to GND and OUT to GND

**LM66100 #2 (USB-C 5V side)**
- IN → `USB_VBUS`
- OUT → `+5V` (same system rail as above — this is the OR'ing)
- GND → GND
- CE → GND (active-low — must be LOW to enable, NOT tied to VOUT)
- ST → no-connect
- Add 100nF decoupling cap from IN to GND and OUT to GND

**TPS23730 (PoE PD Controller)**
- Connects to the RJ45 PoE pairs (pins from the magjack)
- Outputs regulated 5V → label `POE_5V`
- Needs external transformer (add transformer symbol, label primary/secondary)
- Refer to TPS23730 datasheet application circuit — copy it exactly

**TLV1117-33 (3.3V LDO)**
- IN → `+5V`
- OUT → `+3V3` power net
- GND → GND
- Input cap: 10µF electrolytic + 100nF ceramic (IN to GND)
- Output cap: 10µF electrolytic + 100nF ceramic (OUT to GND)

**AP2112K-3.8 (3.8V LDO for cellular)**
- IN → `+5V`
- OUT → `+3V8` power net (only goes to SIM7080G)
- GND → GND
- Input cap: 1µF ceramic (IN to GND)
- Output cap: 1µF ceramic (OUT to GND)

### Power nets (global labels to use consistently)
| Net name | Voltage | Powers |
|---|---|---|
| `USB_5V` | 5V | From USB-C VBUS, before OR'ing |
| `POE_5V` | 5V | From TPS23730 output, before OR'ing |
| `+5V` | 5V | System rail after OR'ing |
| `+3V3` | 3.3V | ESP32, W5500, SX1262, SD card |
| `+3V8` | 3.8V | SIM7080G only |
| `GND` | 0V | Everything |

### Decisions made
- LoRa frequency: **868 MHz** (Nigeria is Region 1 — 868 MHz band)
- USB-C: 5V default only, no PD negotiation chip needed
- CC resistors: 5.1kΩ to GND on both CC1 and CC2

### Gotchas
- **PWR_FLAG rule**: only add it when no component output drives that net. If an LDO VOUT is already on the net, no PWR_FLAG needed — adding one causes "two power outputs" ERC error
- Nets needing PWR_FLAG in this design: `USB_VBUS` (from external cable), `POE_5V` (until PPS23730 is wired), `SIM_VCC` (SIM_VDD pin type is "Output" not "Power output")
- Nets NOT needing PWR_FLAG: `+3V3` (TLV1117 VOUT), `+3V8` (AP2112K VOUT), `+5V` (LM66100 VOUTs), `GND` (power symbol)
- Two LM66100 VOUTs on `+5V` will always give "two power outputs" ERC error — this is intentional OR-ing, exclude it from ERC
- The PPS23730 application circuit is complex — download the datasheet and copy the reference design exactly, don't freehand it
- LM66100 max current is 1.5A — total board current at peak must stay under 1.5A per source or use a higher-rated ORing solution

---

## Section 2 — ESP32-C6 MCU

> Fill in as you work through this section

### What to place
- ESP32-C6-1U-N8 symbol (may need to create custom symbol from datasheet)
- All VDD/VDDIO pins → `+3V3` (100nF decoupling cap per pin, placed right at the pin)
- All GND pins → GND
- EN (enable) pin → 10kΩ pull-up to `+3V3` + 100nF cap to GND
- GPIO0 (boot mode) → 10kΩ pull-down to GND + optional button to `+3V3`

### SPI bus assignments
| Signal | ESP32 GPIO | Device |
|---|---|---|
| MOSI | GPIO6 | W5500, SX1262, SD card (shared) |
| MISO | GPIO7 | W5500, SX1262, SD card (shared) |
| SCK | GPIO8 | W5500, SX1262, SD card (shared) |
| CS_ETH | GPIO2 | W5500 chip select (moved from GPIO9 — see note) |
| CS_LORA | GPIO10 | SX1262 chip select |
| CS_SD | GPIO11 | MicroSD chip select |

> **Note — why not GPIO9 for CS_ETH:** GPIO9 is a strapping pin read at boot (LOW = normal flash boot). We use it for the BOOT button circuit with a 10kΩ pull-down. CS lines must idle HIGH (not selected), which conflicts with a pull-down to GND. GPIO2 has no strapping function and is a clean replacement.

### UART assignment (for SIM7080G)
| Signal | ESP32 GPIO |
|---|---|
| UART_TX | GPIO4 |
| UART_RX | GPIO5 |

### USB
- GPIO13 (USB_DP) → D+ on USB-C connector
- GPIO12 (USB_DM) → D- on USB-C connector

---

## Section 3 — SX1262 (LoRa)

### Key wiring — SPI and control
- NSS (19) → CS_LORA (GPIO10)
- SCK (18) → SPI_SCK (GPIO8)
- MOSI (17) → SPI_MOSI (GPIO6)
- MISO (16) → SPI_MISO (GPIO7)
- RESET (15) → LORA_RESET (GPIO15) — active low
- BUSY (14) → LORA_BUSY (GPIO18)
- DIO1 (13) → LORA_DIO1 (GPIO19) — TX/RX done interrupt
- DIO2 (12) → 100Ω resistor → PE4259 CTRL pin — controls RF switch (TX vs RX path)
- DIO3 (6) → no-connect

### Key wiring — power
- VDD_IN (1) → +3V3, 100nF to GND
- VBAT (10) → +3V3, 100nF + 10µF to GND
- VBAT_IO (11) → +3V3, 100nF to GND
- VR_PA (24) → +3V3, 100nF to GND
- VREG (7) → 100nF cap to GND only (internal regulator output — do not drive)
- DCC_SW (9) → 15µH inductor → +3V3 (DC-DC switch node)
- GND (2) → GND

### Key wiring — crystal
- XTA (3) → 32 MHz crystal pin + 10pF cap to GND
- XTB (4) → 32 MHz crystal pin + 10pF cap to GND
- Crystal case pins → GND
- Use Crystal_GND24 symbol in KiCad

### Key wiring — RF section (copy from SX1262 datasheet section 14.6.2)
- RFO (23) → matching network (L, C per datasheet) → PE4259 RF1 (pin 1)
- RFI_N (22) + RFI_P (21) → their own matching network → PE4259 RF2 (pin 3)
- PE4259 RFC (pin 5) → C8, L5, C9, C10 output matching → Conn_Coaxial pin 1 (ANT_NET)
- PE4259 CTRL (pin 4) → 100Ω resistor → DIO2 (SX1262 pin 12)
- PE4259 CTRL/VDD (pin 6) → +3V3 (no decoupling cap — logic supply only)
- PE4259 GND (pin 2) → GND
- Conn_Coaxial pin 1 (centre/signal) → ANT_NET
- Conn_Coaxial pin 2 (shield) → GND
- Download PE4259 symbol from SnapEDA

### Gotchas
- DIO2 is NOT no-connect — it controls the PE4259 RF switch
- DCC_SW inductor is **15µH** (from datasheet reference design), not 22nH
- Copy the RF matching network component values exactly from datasheet section 14.6.2 — do not guess

---

## Section 4 — W5500 (Ethernet)

### Key wiring
- SCSn → `CS_ETH` (GPIO2)
- SCLK → `SPI_SCK`, MOSI → `SPI_MOSI`, MISO → `SPI_MISO`
- RSTn → `ETH_RESET` (GPIO20) — active low
- INTn → `ETH_INT` (GPIO21) — interrupt
- RSVD → GND (per datasheet)
- EXRES1 → 12.4kΩ resistor → GND (sets internal reference current — value must be exactly 12.4kΩ)
- PMODE0, PMODE1, PMODE2 → all `+3V3` (sets 100Base-T full duplex auto-negotiation)
- VBG, TOCAP, 1V2O → decoupling cap to GND only (internal voltage outputs — never drive them)
- 25 MHz crystal (Crystal_GND24) between XTLIN and XTLOUT, 20pF load caps on each pin, case pins → GND

### RJ45 — use RJ45_Hanrun_HR911105A (MagJack with integrated magnetics)
- W5500 TXOP / TXON → MagJack TX+ / TX-
- W5500 RXIP / RXIN → MagJack RX+ / RX-
- MagJack CT (centre tap) pins → `+3V3` through 49.9Ω resistor (copy from W5500 datasheet)
- MagJack GND / shield → GND
- LED pins → no-connect for prototype

### Gotchas
- EXRES1 must be exactly 12.4kΩ — do not substitute
- VBG/TOCAP/1V2O are outputs — cap to GND only, never connect to a power rail
- Centre tap resistor value comes from the W5500 datasheet application circuit — copy it exactly

---

## Section 5 — SIM7080G (Cellular)

> Fill in as you work through this section

### Key wiring
- UART TX/RX → ESP32 GPIO4/GPIO5
- PWRKEY → GPIO22 — pulse LOW for 1 second to power on/off module
- Power supply → `+3V8` rail (NOT 3.3V)
- SIM card holder → SIM_VCC, SIM_RST, SIM_CLK, SIM_DATA pins on module
- Main antenna → U.FL connector (LTE)
- GNSS antenna → separate U.FL connector

---

## Section 6 — USB-C, MicroSD, Button, LED, SWD

> Fill in as you work through this section
