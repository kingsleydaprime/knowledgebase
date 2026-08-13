# IoT Bridge PCB — Architecture & Component Selection

From [`../component-selection.md`](../component-selection.md) and
[`../documentation.md`](../documentation.md) §2–4.

Component-selection questions are really *"can you justify a decision under pressure?"* questions.
Every answer should be **requirement → candidates → chosen → what you gave up.**

---

### Q1. [Intermediate] 🔥 Why the ESP32-C6 specifically? There are cheaper MCUs.

**Strong answer covers:** it's the radio complement that decides it. One chip gives **Wi-Fi 6
(802.11ax, 2.4 GHz), Bluetooth 5.0 LE, and an 802.15.4 radio** — which is what Zigbee 3.0 and Thread
1.3 run on. For a bridge whose entire job is speaking to heterogeneous local devices, getting
Zigbee/Thread without a second radio IC is the whole argument. Plus a single RISC-V core at 160 MHz,
512 KB SRAM, 8 MB on-module flash (N8), 23 GPIO, SPI/I2C/UART/USB-Serial-JTAG, and −40 to +85 °C.

**The constraint to name:** Zigbee and Thread **share the same 802.15.4 radio and are time-shared**,
so only one is active at a time — firmware-selectable per deployment, not simultaneous. Volunteering
that limit is what makes the answer credible.

---

### Q2. [Intermediate] 🔥 Module or bare chip? Defend it.

**Strong answer covers:** the **WROOM-1 module**, for three reasons that all reduce risk rather than
cost: the antenna matching network is already designed and tuned (RF layout is the easiest thing to
get wrong on a first board), decoupling is integrated, and the module carries **FCC/CE
certification** — so the product inherits it instead of paying for full intentional-radiator testing.

**The cost:** higher unit price, a larger footprint, and no freedom to change the RF front end. The
rule to state: a bare chip is the right call at volume, when the RF layout is a solved problem for
you; a module is right for a first spin where certification and RF risk dominate the BOM delta.

---

### Q3. [Advanced] 🔥 Why 868 MHz for LoRa rather than 915 or 433?

**Strong answer covers:** **Nigeria is ITU Region 1**, the same regulatory region as Europe, so
868 MHz is the correct ISM band. 915 MHz is Region 2 (the Americas); using it here would be a
regulatory violation, not just a suboptimal choice. This is a deployment-geography decision, not a
technical preference — and the SX1262 covers 150–960 MHz, so the *chip* isn't the constraint, the
antenna, matching network and filter are.

**Follow-up worth pre-empting:** *"What changes if you sell into the US?"* — a different antenna and
matching network, a re-tune, and different duty-cycle/power rules. The chip stays.

---

### Q4. [Intermediate] Walk me through the SX1262's key specs and why they matter for this application.

**Strong answer covers, with the *why* attached to each number:**
- **+22 dBm TX / −148 dBm RX sensitivity** → the link budget, which is what buys the kilometres.
  LoRa's whole proposition is range, and that pairing is where it comes from.
- **4.2 mA RX current, <1.5 µA sleep** → the node side of the network can run for years on a
  battery; the gateway benefits less, but the same radio is used at both ends.
- **SPI + 3 DIO pins** → simple MCU interface, but the DIOs matter: DIO2 can drive the RF switch
  automatically (see [02-power-and-rf.md](02-power-and-rf.md) Q6).
- **LoRa (CSS) plus FSK/GFSK** → chirp spread spectrum is what gives sub-noise-floor reception; FSK
  is there for compatibility with conventional links.

---

### Q5. [Intermediate] 🔥 Why the W5500 rather than using the ESP32's own MAC with an external PHY?

**Strong answer covers:** the W5500 is a **hardwired TCP/IP stack** — TCP, UDP, IPv4, ICMP, ARP,
IGMP, PPPoE and eight independent hardware sockets, all in silicon. The MCU talks to it over SPI and
never runs a software network stack for Ethernet, which frees both RAM and CPU on a single-core part
that's already juggling three radios.

**The trade-off:** SPI throughput caps you well below wire speed, and you're limited to the protocols
and socket count the chip implements — no custom stack behaviour, no raw-socket tricks. For a
telemetry bridge moving small messages that's irrelevant; for a high-throughput application it would
be the wrong choice. Also worth naming: an EMAC+PHY design is cheaper in parts and more flexible, and
costs you firmware complexity and RAM.

---

### Q6. [Intermediate] Why the SIM7080G, and what did you give up?

**Strong answer covers:** it targets exactly the right tier — **LTE Cat-M1 and NB-IoT**, the
low-power wide-area cellular standards built for telemetry, with **EGPRS/2G fallback** which still
matters in regions where LTE-M coverage is patchy. Bonus GNSS (GPS/GLONASS/BeiDou) at no extra part
cost. Interface is UART with AT commands — simple to drive, no high-speed bus needed at ~600 kbps.

**What you give up:** speed (this is not an LTE modem for bulk data), and **no onboard eSIM** — so
there's a physical nano-SIM slot, with **eSIM pads laid out as DNP** (do-not-populate) reserved for a
future revision. That last detail is a good one to volunteer: it's cheap to reserve a footprint now
and impossible to add later without a respin.

---

### Q7. [Advanced] 🔥 Everything hangs off SPI. How did you decide the bus speed?

**Strong answer covers:** **16 MHz, because the SX1262 is the limiting device**, and the W5500 (which
supports up to 80 MHz) and the SD card are configured down to match. A shared bus runs at the speed
of its slowest participant unless you're willing to reconfigure the controller between transactions.

**Follow-ups worth having ready:** each peripheral needs its own **chip select**, so the GPIO budget
is part of the decision; SPI mode (CPOL/CPHA) must be compatible across devices sharing the bus; and
if one device genuinely needed to run faster, the answer is a second SPI peripheral, not
reconfiguring on every transaction. Also: SD cards can hold the bus during internal operations, which
is an argument for keeping them off a bus shared with a latency-sensitive radio.

---

### Q8. [Intermediate] Why no external flash chip?

**Strong answer covers:** the **ESP32-C6-WROOM-1-N8 has 8 MB on-module** — enough for dual OTA
partitions plus a filesystem, which is the actual requirement (an OTA-capable field device needs room
for two images plus config/logs). A W25Q64JV was evaluated and rejected as unnecessary parts, board
area, and another SPI chip select.

**The reasoning to state:** don't add a part until the memory map says you need it. Adding it "just
in case" costs BOM, area, a CS pin, and another thing to get wrong — and the module already answered
the question.

---

### Q9. [Advanced] 🔥 The board has four connectivity options. How does it decide which to use?

**Strong answer covers:** that's a **firmware policy question, not a hardware one** — the hardware's
job is to make all four simultaneously available and independently power-manageable. The sensible
policy is a preference ladder by cost and power: Ethernet (free, powered, most reliable) → Wi-Fi →
cellular (metered, power-hungry) as the fallback, with failover driven by actual link health rather
than by carrier state, and hysteresis so it doesn't flap between links.

**The hardware consequence worth naming:** because cellular is the *fallback*, it spends most of its
life idle — which is precisely why its power rail is separated (see
[02-power-and-rf.md](02-power-and-rf.md) Q4): the rare, violent transmit spike must not disturb
whatever else is running.

---

### Q10. [Intermediate] Draw me the block diagram.

**Strong answer covers:** power in (PoE / USB-C / barrel) → ORing auto-switch → 5 V rail → 3.3 V LDO
for the digital domain and a separate 3.8 V LDO for the modem. ESP32-C6 at the centre: **SPI** out to
SX1262, W5500 and microSD (each with its own CS); **UART** to SIM7080G; **GPIO** for the RF switch
control, status LED and user button; **USB-C** for power and USB-Serial/JTAG; **SWD/JTAG** header for
debug. RF: SX1262 → PE4259 SPDT → single LoRa antenna; W5500 → MagJack; SIM7080G → cellular antenna;
Wi-Fi/802.15.4 via the module's own antenna.

**The habit this demonstrates:** being able to draw the interfaces from memory is what proves you
designed it rather than assembled a reference design.

---

### Q11. [Beginner] What are the passives actually for?

**Strong answer covers:** three jobs, and being able to name them separately matters —
**decoupling** (a small ceramic at every IC supply pin to serve fast transient current locally, plus
bulk capacitance for slower demand), **pull-ups/pull-downs** (defining the state of resets, chip
selects, and mode pins so nothing floats at power-on), and **termination/matching** (series
resistors on fast lines, RF matching networks, and the RJ45 centre-tap network). The failure mode
worth naming: a floating reset or boot-mode pin gives a board that works on the bench and fails
intermittently in the field.

---

### Q12. [Advanced] 🔥 If you had to cut cost by 30%, what comes off the board?

**Strong answer covers:** the answer should be *feature*-driven, not part-driven. Cellular is by far
the biggest single cost — modem, SIM slot, its own regulator, its own antenna — so the honest first
cut is "does this deployment need a cellular fallback?" Second, PoE: the PPS23730 plus magnetics is
expensive, and a passive-PoE or barrel-jack-only variant is much cheaper. Third, the module-versus-
bare-chip decision flips at volume, once certification is amortised.

**The framing that lands:** on a board like this the cost is in the *radios and the power tree*, not
in the passives — so cost reduction is a product-scope conversation before it's an engineering one.
