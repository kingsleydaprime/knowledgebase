# Hardware Interview — Electronics & Embedded

From [[hardware/01-electricity|01-electricity]], [[hardware/02-digital-and-analog|02-digital-and-analog]], [[hardware/03-embedded-systems|03-embedded-systems]], [[hardware/04-microcontrollers|04-microcontrollers]], [[hardware/05-communication-protocols|05-communication-protocols]], [[hardware/10-kicad-basics|10-kicad-basics]].

---

### Q1. [Beginner] 🔥 I want to drive an LED from a 3.3 V GPIO. Size the resistor.

**Strong answer covers:** the LED has a **forward voltage** (~2 V for red, ~3 V for blue/white) that it drops regardless of current, so the resistor only sees the difference. For a red LED at 10 mA: `R = (3.3 − 2.0) / 0.010 = 130 Ω` → pick the next standard value up, 150 Ω.

**Then check the pin can source it.** Most MCU pins are rated ~8–20 mA *per pin* with a lower *total* limit across the port. Exceeding it doesn't always fail immediately — it degrades the die and produces mysterious behaviour later, which is worse than a clean failure.

**The detail worth adding:** blue/white LEDs at ~3.0–3.2 V forward voltage barely work from a 3.3 V rail — the headroom is so small that the current becomes wildly sensitive to supply variation and temperature. That's the point to say "I'd drive it from 5 V, or use a constant-current driver," which shows you've actually built something rather than done the arithmetic.

---

### Q2. [Intermediate] 🔥 What is a decoupling capacitor and where does it go?

**This is the single most-asked hardware question.** If you get one thing right, get this one.

**Strong answer covers:** a chip's current draw isn't constant — it spikes every time internal transistors switch, at nanosecond timescales. The power supply and its traces have **inductance**, so they can't deliver a fast spike; the rail sags, and a sagging rail causes resets, corrupted reads, and faults that look like firmware bugs. The decoupling cap is a **local charge reservoir** sitting right at the chip, supplying that spike from microns away instead of centimetres.

**Placement is the answer, not the value.** 100 nF per power pin, **as close to the pin as physically possible**, with the shortest possible path to the ground plane. A perfect capacitor at the wrong end of a long trace does nothing, because the trace inductance you were trying to avoid is now in series with your fix.

**The detail worth adding:** you pair it with a bulk cap (10 µF+) for lower-frequency demand — small caps handle fast transients, big caps handle sustained draw. And "more capacitance is better" is wrong: large caps have higher ESL and respond too slowly for the fast edges, which is why you see 100 nF *and* 10 µF rather than one 10 µF.

---

### Q3. [Beginner] 🔥 What's a floating pin, and why do we use pull-up/pull-down resistors?

**Strong answer covers:** an input pin not connected to anything is **floating** — its voltage is undefined, drifting with nearby electrical noise and even proximity to your hand. Reading it gives random results. A pull-up (to VCC) or pull-down (to GND) resistor defines a **default state** while still letting an active driver override it.

**The typical wiring:** a button between the pin and ground, with a pull-up — so the pin reads HIGH when unpressed and LOW when pressed. Counterintuitive to beginners, standard in practice, and worth being able to explain (you can sink current reliably; sourcing it is fussier).

**The detail worth adding:** most MCUs have **internal pull-ups** you enable in software, which saves a component — but they're weak (tens of kΩ) and loosely specified, so for anything noise-sensitive or long-wired you fit an external one. Knowing that internals exist *and* when they're not good enough is the distinguishing answer.

---

### Q4. [Intermediate] 🔥 Compare UART, I2C and SPI. When would you pick each?

**Strong answer covers:**

| | Wires | Speed | Devices | Use when |
|---|---|---|---|---|
| **UART** | 2 (TX/RX) | ~115 kbps typical | 1:1 only | Point-to-point, debug console, GPS/modem modules |
| **I2C** | 2 (SDA/SCL) | 100 k–400 kHz | Many, addressed | Lots of slow sensors and you're short on pins |
| **SPI** | 4 (+1 CS each) | 10s of MHz | Many, one CS each | Speed matters — displays, SD cards, radio modules |

**The tradeoff in one line:** I2C buys pin count with speed and complexity; SPI buys speed with pins.

**The detail worth adding:** UART has **no clock line** — both ends agree a baud rate in advance and sample on timing alone, which is exactly why a mismatched baud rate produces garbage rather than an error, and why UART needs a reasonably accurate clock source at both ends. I2C and SPI are **synchronous** — the master supplies a clock, so both ends stay aligned by construction. That's the real axis the three differ on, and saying it shows you understand rather than recall.

---

### Q5. [Intermediate] Why does an I2C bus need pull-up resistors, and what value?

**Strong answer covers:** I2C lines are **open-drain** — devices can only pull the line LOW, never drive it HIGH. That's deliberate: it makes multi-master and clock stretching possible without two devices fighting each other (which would short VCC to ground). Something has to return the line to HIGH, and that's the pull-up.

**Value:** typically 4.7 kΩ, and it's a tradeoff against bus capacitance. Too high and the rise time is too slow for the clock rate — you get corrupted data at 400 kHz that works fine at 100 kHz. Too low and you exceed the sink current devices can handle.

**The detail worth adding:** one pull-up pair **per bus**, not per device. A classic bug is fitting three sensor breakout boards that each carry their own pull-ups, putting them in parallel and dropping the effective resistance to a third — after which the bus stops working and nothing in your firmware is wrong. Being able to name that failure is a strong signal.

---

### Q6. [Intermediate] 🔥 What must you not do inside an interrupt handler?

**Strong answer covers:** an ISR should be **short and non-blocking**. Don't: allocate memory, take a lock that a non-ISR context holds, call printf/serial, busy-wait, or do anything with unbounded runtime. The rest of the system is stalled while you're in there, and interrupts of equal or lower priority are blocked.

**The standard pattern:** set a flag or push to a ring buffer inside the ISR; do the real work in the main loop or a task that polls it.

**The detail worth adding — the `volatile` trap:** a variable written by an ISR and read by the main loop must be declared `volatile`, or the compiler may cache it in a register and your loop never sees the change. This produces a bug that vanishes at `-O0` and appears at `-O2`, which is the exact signature people misdiagnose as a hardware fault.

**And the honest limit:** `volatile` prevents the caching, but it does **not** make access atomic. A 32-bit counter on an 8-bit MCU is read in multiple instructions and can tear mid-update. That needs an interrupt-disable around the read, and knowing the distinction between "visible" and "atomic" is a genuinely senior answer — it's the same distinction as Java's `volatile` in [[languages/01-java/interview/02-jvm-and-concurrency|the JVM bank]].

---

### Q7. [Beginner] Why does a button need debouncing?

**Strong answer covers:** a mechanical switch's contacts physically bounce for ~1–20 ms on actuation, so one press produces a burst of transitions. Any edge-triggered read counts several presses.

**Fixes:** in software, ignore further transitions for ~20–50 ms after the first, or require the level to be stable across several polls. In hardware, an RC filter plus a Schmitt-trigger input.

**The detail worth adding:** prefer the **software** fix in most designs — it's free and tunable. Reach for hardware debouncing when the signal drives an interrupt you can't afford to enter spuriously, or clocks a counter directly. And the naive `delay(50)` inside the ISR is the wrong fix, per Q6.

---

### Q8. [Intermediate] 🔥 LDO vs switching regulator — how do you choose?

**Strong answer covers:** an **LDO** burns the excess voltage as heat: `P = (Vin − Vout) × I`. Simple, cheap, low noise, no switching interference. A **buck converter** switches at high frequency and is 85–95 % efficient regardless of the drop, but adds an inductor, cost, board area, and switching noise.

**The arithmetic that makes the choice:** 12 V → 3.3 V at 500 mA through an LDO dissipates `(12 − 3.3) × 0.5 = 4.35 W` as heat. That's not a regulator, that's a heater — and it'll go into thermal shutdown in a small enclosure. A buck is the only sane option. But 3.7 V Li-ion → 3.3 V at 50 mA is `0.02 W`, and an LDO is obviously right.

**The detail worth adding:** **dropout voltage** — an LDO needs Vin above Vout by a minimum margin (typically 0.2–1.2 V) to regulate at all. A 3.3 V LDO fed from a Li-ion cell falls out of regulation as the battery discharges toward 3.4 V, so the useful battery capacity is smaller than the datasheet curve suggests. Mentioning that shows you've thought about the whole discharge profile, not just the nominal case.

---

### Q9. [Intermediate] How do you interface a 5 V device to a 3.3 V MCU?

**Strong answer covers:** check the direction. **3.3 V → 5 V input** often needs nothing, because most 5 V logic reads anything above ~2.0 V as HIGH. **5 V → 3.3 V input is the dangerous direction** — it can exceed the absolute maximum rating on the pin and damage it.

**Options, roughly in order:** a dedicated level-shifter IC; a MOSFET-based bidirectional shifter (the standard trick for I2C); a resistor divider for slow signals only; or checking whether the MCU pin is **5 V tolerant** — many are, and the datasheet says so per pin.

**The detail worth adding:** a resistor divider is fine for a slow UART line and wrong for SPI at 10 MHz, because the divider's impedance plus the pin capacitance forms a low-pass filter that rounds the edges into unusability. "It depends on the edge rate" is the answer that separates people who've scoped it from people who've read about it.

---

### Q10. [Intermediate] What does ADC resolution mean, and what is aliasing?

**Strong answer covers:** an n-bit ADC divides its reference voltage into `2^n` steps. 12-bit over a 3.3 V reference gives `3.3 / 4096 ≈ 0.8 mV` per step. Resolution is **relative to the reference**, which is why a noisy or drifting reference silently destroys accuracy no matter how many bits you paid for.

**Aliasing:** sampling below twice the highest input frequency (Nyquist) makes high-frequency content appear as a *fake low-frequency signal* — and it's indistinguishable from real data after the fact. The fix is an analog **anti-aliasing low-pass filter before the ADC**, not filtering in software afterwards, because by then the damage is already encoded in your samples.

**The detail worth adding:** resolution ≠ accuracy. A 16-bit ADC on a noisy board with a poor reference may give you 10 usable bits. The useful number is **effective number of bits (ENOB)**, and treating the datasheet's headline bit count as achievable is a beginner tell.

---

### Q11. [Intermediate] How does PWM produce an "analog" output?

**Strong answer covers:** PWM switches fully on and fully off at a fixed frequency, varying the **duty cycle**. The *average* is proportional to duty. For an LED, your eye integrates it and it looks dimmer. For a motor, the winding's inductance integrates it. For an actual analog voltage, you low-pass filter it (RC) or use a real DAC.

**The detail worth adding:** frequency choice matters and is application-specific — above ~100 Hz for LEDs to avoid visible flicker (and much higher if a camera might film it), above ~20 kHz for motors to move the switching whine out of the audible band. Saying *why* each threshold exists is the differentiator.

---

### Q12. [Advanced] A board doesn't power on. Walk me through your diagnosis.

**This is the hardware equivalent of "the service is down."** They're testing method, not knowledge.

**Strong answer covers a bisection, cheapest test first:**
1. **Look and smell** before powering — reversed polarity, a bridged solder joint, a cracked part, the smell of something already dead.
2. **Continuity check with power off** — is VCC shorted to GND? If so, stop; find the short before applying power again.
3. **Current-limited first power-on** — a bench supply set to a sensible current limit turns a destroyed board into a supply that politely goes into constant-current.
4. **Measure each rail in order** — input, then post-regulator, then at the far end of the board. Compare against the schematic. The first rail that's wrong bounds the problem.
5. **Then the passive prerequisites** — reset line held correctly? Crystal oscillating (scope it)? Boot-mode strapping pins in the right state?
6. **Only then suspect firmware.**

**The detail worth adding:** state explicitly that you'd check the **absolute maximum ratings** before applying anything unusual, and that you keep the schematic open the whole time. The generalisable point — the same one as bisecting network layers in [[foundations/networking/interview/04-debugging-and-scenarios|the networking bank]] — is that you're **halving the search space with each measurement**, not poking hopefully. Interviewers care far more about that than about any specific component.

---

### Q13. [Beginner] Absolute maximum ratings vs recommended operating conditions — what's the difference?

**Strong answer covers:** **absolute maximum** is the stress level beyond which you may cause permanent damage — it is *not* a spec you're allowed to operate at. **Recommended operating conditions** are where the datasheet's performance figures are guaranteed. Running between the two is the grey zone where the part works, isn't characterised, and fails unpredictably in the field.

**The detail worth adding:** this is why the [[hardware/README|golden rule]] is to read the datasheet *and* the manufacturer's reference design. The datasheet tells you the limits; the app note tells you how they intended it to be wired. Copying a reference design is not a shortcut — it's using the work of the people who characterised the part.

---

### Q14. [Intermediate] Why do crystals need load capacitors, and what happens if you get them wrong?

**Strong answer covers:** a crystal is specified to resonate at its rated frequency **with a specified load capacitance** across it. The load caps (plus the stray capacitance of pins and traces) form that load. Wrong caps means the oscillator runs slightly off-frequency, or fails to start reliably.

**The detail worth adding:** "slightly off" is fine for blinking an LED and fatal for UART, which needs both ends within a few percent — so a wrong-frequency crystal shows up as serial garbage that people misdiagnose as a baud-rate bug for hours. The standard formula is `C_load = 2 × (C_crystal − C_stray)`, with stray typically a few pF. It's also why "it works on my breadboard but not on the PCB" happens: stray capacitance changed.

---

### Q15. [Advanced] Bare metal vs RTOS — when is an RTOS worth it?

**Strong answer covers:** **bare metal** is a `while(1)` superloop plus interrupts. Total control, minimal overhead, trivially predictable — and it degrades badly once you have several activities with different timing requirements, because everything becomes a hand-rolled state machine sharing one loop.

**An RTOS** gives you tasks, priorities, preemptive scheduling, and blocking primitives (queues, semaphores), so each activity is written as if it owned the CPU. The cost is RAM per task stack, scheduler overhead, and a new class of bugs — priority inversion, stack overflow, races between tasks.

**The heuristic:** reach for an RTOS when you have **multiple independent activities with different deadlines**, especially if any of them blocks. Stay bare metal when the job is one loop plus interrupts, or when the timing is so tight that scheduler jitter is unacceptable.

**The detail worth adding:** "real-time" means **deterministic deadlines**, not "fast." A system that responds in 10 ms *every* time is more real-time than one averaging 1 ms with occasional 50 ms excursions. That distinction — worst case over average — is the same instinct as caring about p99 rather than mean latency in [[languages/01-java/interview/02-jvm-and-concurrency|server work]], and drawing that parallel lands well.

---

## Related
- [[hardware/README|Hardware course]] — the notes these come from
- [[hardware/interview/02-rf-and-iot|RF & IoT bank]] — the wireless and systems half
- [[projects/iot-bridge-pcb/task|IoT Bridge PCB]] — **cite this**; a real board beats any answer here
- [[INTERVIEW|Interview index]]
