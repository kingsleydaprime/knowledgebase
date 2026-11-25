---
id: d990f73f-ffdf-4124-8010-5fdfad90ff06
---

# Putting It All Together

Here's how all of this connects in a real system. A soil moisture monitoring system for a farm:

**Edge:**
- ESP32 reads soil moisture via ADC (analog signal → digital number)
- Reads temperature via 1-Wire DS18B20
- Every 15 minutes: wakes from deep sleep, takes readings, connects to LoRa module via SPI, transmits a small packet

**Gateway (per farm section):**
- Raspberry Pi with a LoRa receiver listens for packets
- Decodes the sensor data
- Publishes to MQTT broker: `farm/field-a/node-03/moisture` = 42%

**Cloud:**
- MQTT broker receives messages
- InfluxDB logs every reading with timestamp
- Grafana dashboard shows real-time moisture maps
- Automation rule: if moisture < 30%, publish `farm/field-a/valve-03/command` = OPEN
- Valve controller subscribes to that topic, actuates the irrigation valve

The RF link (LoRa) enables the sensor to be kilometers from the gateway with no WiFi infrastructure. The edge MCU spends 99% of its time in deep sleep, lasting a full growing season on a battery pack. The gateway handles protocol translation and cloud connectivity. The cloud provides persistence, visualization, and automation.

---

## Where to Go From Here
<!-- bite: 3c136647-9659-4d2e-b452-ba65bb8485c6 -->

- **Electronics:** Get a breadboard, an ESP32 dev board, some LEDs, resistors, and sensors. Read the datasheet of one sensor end to end.
- **Embedded:** Build something in C with the ESP-IDF (not just Arduino). Deal with FreeRTOS tasks.
- **RF:** Buy an RTL-SDR dongle (~$25) and start receiving signals around you — FM radio, weather satellites, ADS-B aircraft transponders. Seeing the spectrum demystifies RF fast.
- **LoRa:** Get two SX1276 modules, hook them to ESP32s over SPI, get one transmitting and one receiving across your building.
- **BLE:** Build a BLE beacon with an ESP32, scan for it on your phone. Then read the raw advertising packet bytes.

Every expert in this space started by wiring up a blinking LED and wondering why it was brighter than expected. The fundamentals here are the map — the territory is soldering iron burns and `Serial.println()` debugging at 2am.

## Related
<!-- bite: 59c9906d-c99f-4ea6-9d4c-bf21043fd995 -->
- [[hardware/index|Hardware course index]]
- [[hardware/hardware-reference|Hardware Reference]] — units, prefixes and the formulas, for lookup
- IoT Bridge PCB — all of this, done for real
- [[project-ideas|Project Ideas]] — the hardware build tier

## About this lesson
<!-- bite: 99406f4b-f41f-487b-97cf-68aaedd2f57a -->

**Level:** Intermediate. **Covers:** the whole stack in one worked picture, and what to do next.
