# Hardware Interview — RF & IoT

From [[hardware/06-radio-frequency|06-radio-frequency]], [[hardware/07-connectivity|07-connectivity]], [[hardware/08-iot-architecture|08-iot-architecture]].

The half most candidates are weakest on, because RF resists intuition and most people have only used radios through a library. Being able to reason about a **link budget** and a **power budget** with numbers is disproportionately impressive.

---

### Q1. [Intermediate] 🔥 Pick a radio for a battery sensor reporting once a minute from across a large site.

**They're testing whether you reason from requirements rather than reaching for WiFi.**

**Strong answer covers the axes first** — range, data rate, power, infrastructure, and cost — then applies them:

| | Range | Power | Data rate | Needs |
|---|---|---|---|---|
| **WiFi** | ~50 m | High | High | An access point |
| **BLE** | ~10–100 m | Very low | Low | A phone/gateway nearby |
| **Zigbee/Thread** | ~10–100 m, **meshes** | Low | Low | A coordinator/border router |
| **LoRa** | **km** | Very low | Very low (~0.3–50 kbps) | A gateway |
| **NB-IoT / LTE-M** | Cellular | Low–medium | Low | A subscription, coverage |

**The answer:** LoRa or LoRaWAN. Long range, tiny power, and the payload is a handful of bytes a minute — which is exactly what its very low data rate can carry. WiFi is disqualified on power and range, BLE on range, cellular on cost per node unless you specifically want no gateway infrastructure.

**The detail worth adding:** duty-cycle regulations on sub-GHz ISM bands (e.g. 1 % in EU 868 MHz) cap how often you may transmit — so "once a minute" is a design constraint to check, not a free choice. Mentioning regulatory limits unprompted marks someone who has shipped a radio product.

---

### Q2. [Intermediate] 🔥 What is a link budget, and why is dBm used?

**Strong answer covers:** a link budget is the accounting of gains and losses from transmitter to receiver: `Rx power = Tx power + antenna gains − path loss − cable/connector losses`. If the result is above the receiver's **sensitivity**, the link works — with the difference being your **fade margin**.

**Why dBm:** it's logarithmic, so gains and losses **add instead of multiply**. Doing a link budget in milliwatts means chained multiplication of numbers spanning ten orders of magnitude; in dBm it's mental arithmetic.

**The numbers worth having memorised:** 0 dBm = 1 mW. **+3 dB is double power, −3 dB is half. +10 dB is ten times.** So +20 dBm = 100 mW. Being able to convert instantly, out loud, is a small thing that reads as fluency.

**The detail worth adding:** path loss follows an inverse-square law, so **doubling the range costs 6 dB** — which is why a 3 dB antenna improvement is worth much less than people expect, and why LoRa buys its range through receiver sensitivity (spreading gain) rather than by shouting louder.

---

### Q3. [Intermediate] Why is 2.4 GHz so crowded, and when would you choose sub-GHz?

**Strong answer covers:** 2.4 GHz is a globally licence-free ISM band, so WiFi, Bluetooth, Zigbee, microwave ovens and cordless phones all share it. Its advantages are worldwide legality, small antennas, and cheap silicon.

**Sub-GHz (433/868/915 MHz)** propagates better — longer range at the same power, and materially better penetration through walls and foliage, because lower frequencies diffract more and are absorbed less. The costs: a physically larger antenna (wavelength scales inversely), lower data rates, and **region-specific frequency allocations**, so one hardware SKU may not be sellable worldwide.

**The detail worth adding:** 2.4 GHz is specifically absorbed by water, which includes people and leaves — this is why a link that works in an empty room degrades when the room fills up, and why outdoor 2.4 GHz range collapses in summer when trees are in leaf. That's a concrete, memorable observation rather than a recited fact.

---

### Q4. [Beginner] Why does antenna length matter, and what's the most common antenna mistake?

**Strong answer covers:** an antenna is a resonant structure — it radiates efficiently when its dimensions relate to the wavelength (`λ = c / f`), typically a quarter-wave. At 2.4 GHz, λ ≈ 12.5 cm, so a quarter-wave is about 3 cm. At 868 MHz it's about 8.6 cm — noticeably bigger, which is a real enclosure constraint.

**The most common mistake:** treating the antenna as an afterthought in layout. Ground plane under a chip antenna, metal or a battery next to it, a mismatched feed line, or a wrong-length trace — any of these detune it, and the symptom is "the range is much worse than the datasheet," not an error message.

**The detail worth adding:** the manufacturer publishes a **keep-out area** and a reference layout for exactly this reason, and it's one of the highest-value places to follow the reference design literally. RF is the part of a board where copying is the professional choice.

---

### Q5. [Intermediate] 🔥 Why MQTT rather than HTTP for IoT?

**Strong answer covers:** MQTT is a lightweight **publish/subscribe** protocol over a long-lived TCP connection. Advantages over HTTP request/response for constrained devices:

- **Tiny overhead** — a couple of bytes of header versus hundreds of bytes of HTTP headers per message. On a metered cellular plan that's the actual bill.
- **One persistent connection** — no TCP and TLS handshake per message, which is where most of the *energy* goes on a battery device.
- **Push, not poll** — the broker can reach the device without it polling, which is otherwise the only option behind NAT.
- **Decoupling** — publishers and subscribers don't know about each other, so adding a consumer doesn't touch the device.

**The detail worth adding — QoS levels, because they're where the real thinking is:** QoS 0 is at-most-once, 1 is at-least-once (so **duplicates are possible and consumers must be idempotent**), 2 is exactly-once, which costs a four-message handshake. Most production systems use QoS 1 with idempotent handling, because QoS 2's overhead rarely justifies itself — and this is precisely the [[architecture/04-distributed-systems/10-distributed-transactions|exactly-once is a lie]] conversation from distributed systems, arriving via a different door. Making that connection is the strongest thing you can do with this question.

**Also worth knowing:** the broker is a single point of failure and the thing that actually has to scale, and MQTT's retained messages plus last-will-and-testament are how you get device presence without polling.

---

### Q6. [Intermediate] 🔥 Estimate the battery life of a sensor node.

**They want to see you compute it, not describe it.**

**Strong answer covers the method:** battery life is dominated by the **average** current, which is a duty-cycle weighted sum of the modes — not the peak, and not the sleep figure alone.

Worked example — a node waking once a minute, transmitting for 2 s at 120 mA, sleeping the other 58 s at 10 µA, on a 2000 mAh cell:

```
active:  120 mA × (2/60)   = 4.0   mA average
sleep:   0.01 mA × (58/60) = 0.0097 mA average
total                      ≈ 4.01  mA
life = 2000 mAh / 4.01 mA  ≈ 499 h ≈ 21 days
```

**Then the insight:** sleep current is almost irrelevant here — the transmit window dominates by a factor of 400. Halving the *transmit time* or reporting every 5 minutes buys far more than any sleep-mode optimisation. **Optimise the term that dominates**, and the only way to know which one that is, is to do this arithmetic.

**The detail worth adding:** real cells deliver less than their rating under pulsed high-current loads and in cold temperatures, and self-discharge matters over a multi-year deployment. A serious answer applies a derating factor and says why. Bonus: a big bulk capacitor across the supply lets a coin cell survive a transmit pulse it otherwise couldn't.

---

### Q7. [Intermediate] Describe the layers of an IoT system and where you'd put the intelligence.

**Strong answer covers the three layers:** **device/edge** (sensors, MCU, radio) → **gateway/network** (aggregation, protocol translation, local buffering) → **cloud/application** (storage, analytics, UI).

**Where the intelligence goes is the actual question**, and it's a latency/bandwidth/power tradeoff. Push processing to the edge when: the reaction must be faster than a round trip, bandwidth or cellular cost is the constraint, the link is unreliable, or the raw data is privacy-sensitive. Keep it central when you need cross-device correlation, heavy compute, or the ability to change the logic without touching deployed hardware.

**The detail worth adding:** the strongest version names **updateability** as the deciding factor people forget. Logic in the cloud can be fixed this afternoon; logic in firmware on 500 deployed devices needs an OTA path you must have designed in advance — with a rollback, because a bad update that bricks the fleet is unrecoverable. "How do I fix this when it's wrong?" is a better design question than "where is it fastest?"

---

### Q8. [Advanced] Your devices lose connectivity for six hours. What should happen?

**This is the distributed-systems question wearing a hardware costume**, and it's the [[PRIMETECHIE|Rank IV hardware gate]].

**Strong answer covers:**
- **Buffer locally**, with a bounded ring buffer and an explicit policy for overflow — drop oldest or drop newest, decided by whether you care more about recency or completeness. Unbounded buffering just moves the failure to a crash.
- **Reconnect with exponential backoff and jitter** — 500 devices reconnecting simultaneously when the network returns is a self-inflicted thundering herd on your broker.
- **Timestamp at capture, not at upload**, or every buffered reading arrives with the wrong time. This bites people constantly.
- **Make ingestion idempotent** — retried uploads will duplicate, so a device-side sequence number or event ID lets the server deduplicate.

**The detail worth adding:** the honest position is that **the device's clock is unreliable** — it drifts, and it resets on power loss. So either sync it (NTP on reconnect) and record the sync state, or send a monotonic counter plus an uptime and reconstruct real timestamps server-side at ingest. Recognising that a fleet of devices is a distributed system with unreliable clocks — the same problem as [[architecture/04-distributed-systems/03-time-and-ordering|time and ordering]] — is the answer that separates a firmware engineer from a systems engineer.

---

### Q9. [Beginner] Why Power over Ethernet, and what should you check before using it?

**Strong answer covers:** PoE carries power and data on one cable, which removes a separate power run and a local socket — decisive for cameras, access points and sensors in ceilings and outdoors, where the cable install is most of the cost.

**Check:** the standard and its power budget (802.3af ~15 W at the source, 802.3at ~30 W, 802.3bt up to ~90 W), that the switch actually supplies enough across all ports simultaneously, and the voltage drop over 100 m of cable. Also distinguish real 802.3 PoE, which **negotiates** before applying power, from cheap "passive PoE" that just puts voltage on the pins and will damage a non-PoE device plugged into it.

**The detail worth adding:** the power budget is per-switch, not per-port — a 24-port switch rarely delivers full power on all 24. That's a procurement mistake that only shows up when the last few devices refuse to boot.

---

### Q10. [Advanced] How would you make firmware updates safe on deployed hardware?

**Strong answer covers:** an **A/B (dual-bank) scheme** — write the new image to the inactive bank, verify it, then flip a pointer and boot it. If it fails to check in, the bootloader rolls back to the known-good bank. Never overwrite the running image in place: a power cut mid-write leaves an unbootable device with no recovery path.

**Also:** cryptographically **sign** images and verify in the bootloader, or your update channel is a remote code execution channel. Stage the rollout — a canary group before the fleet. And version the protocol, because you will one day have devices several versions behind.

**The detail worth adding:** the rollback trigger must be **automatic and watchdog-driven** — the new image has to affirmatively prove it works (connect, check in) within a timeout, or the watchdog resets and the bootloader reverts. If rollback requires someone to notice and press a button, it isn't a rollback. This is the same "design for failure" instinct as [[architecture/03-architectural-patterns/02-resilience-patterns|circuit breakers]], with the crucial difference that you can't SSH into a bricked device.

---

## Related
- [[hardware/interview/01-electronics-and-embedded|Electronics & Embedded bank]] — the other half
- [[hardware/06-radio-frequency|Radio Frequency]] · [[hardware/08-iot-architecture|IoT Architecture]]
- [[architecture/interview/02-distributed-systems-depth|Distributed systems bank]] — Q5 and Q8 are the same conversation
- [[projects/iot-bridge-pcb/component-selection|IoT Bridge — component selection]] — radio choice argued for real
