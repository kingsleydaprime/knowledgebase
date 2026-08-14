# IoT Architecture

**[Intermediate]** — The three layers of an IoT system, MQTT, edge computing, and designing for a power budget rather than a CPU budget.

An IoT system isn't just a sensor — it's the full chain from physical measurement to cloud storage to user interface.

## The Three Layers

```
┌─────────────────────────────────┐
│          Cloud / Backend        │  ← Storage, processing, APIs, dashboards
├─────────────────────────────────┤
│             Gateway             │  ← Protocol translation, local processing
├─────────────────────────────────┤
│        Edge / End Devices       │  ← Sensors, actuators, MCUs
└─────────────────────────────────┘
```

**Edge devices** — your microcontrollers, sensors, actuators. These live in the physical world, are often battery-powered, and must be power-efficient. They measure things (temperature, movement, soil moisture) and control things (valves, motors, lights).

**Gateway** — bridges the edge-to-cloud gap. Often a Raspberry Pi, industrial PC, or dedicated hardware. Speaks LoRa/Zigbee/BLE to edge devices, and WiFi/Ethernet/Cellular to the internet. Can do local processing (edge computing) — running ML inference, filtering data, making autonomous decisions without cloud round-trips.

**Cloud / Backend** — time-series databases (InfluxDB, TimescaleDB), message brokers (MQTT broker, AWS IoT Core), dashboards (Grafana, Node-RED), APIs.

## MQTT — The IoT Messaging Protocol

**MQTT (Message Queuing Telemetry Transport)** is the dominant protocol for IoT messaging. It's a publish/subscribe model over TCP/IP, designed for constrained devices.

- Devices **publish** messages to **topics**: `home/livingroom/temperature`
- Other devices or servers **subscribe** to topics they care about
- A central **broker** (Mosquitto, AWS IoT Core, HiveMQ) handles routing
- **QoS levels**: 0 (fire-and-forget), 1 (at least once), 2 (exactly once)
- Tiny overhead — a minimal MQTT packet is 2 bytes fixed header

```
Sensor ──publish──► Broker ──deliver──► Dashboard
                      │
                      └──deliver──► Automation rules
                      │
                      └──deliver──► Database writer
```

One sensor publishes temperature, and simultaneously: a dashboard updates, a database logs it, and an automation rule checks if it exceeded a threshold. The sensor doesn't know or care about any of the subscribers.

## Edge Computing

Not everything should go to the cloud. Running inference on an MCU or gateway:

- Faster response (no round-trip latency)
- Works offline
- Cheaper (no cloud compute costs)
- More private (raw data never leaves the device)

TensorFlow Lite for Microcontrollers runs on Cortex-M devices with as little as 16KB SRAM. You can do keyword spotting, anomaly detection, gesture recognition — all on-device.

## Power Design for IoT

Battery life is everything for field-deployed IoT. The math:

```
Battery life (hours) = Battery capacity (mAh) / Average current draw (mA)
```

A 2000mAh cell at 10mA average = 200 hours (8 days). Terrible.

The key insight: **active time is the enemy**. An ESP32 draws ~80mA when WiFi is active. But in deep sleep, it draws ~10µA. If you wake up every 10 minutes, take a reading, send an MQTT packet, and go back to sleep — the average current drops to well under 1mA. Now that 2000mAh battery lasts months.

Design pattern for battery IoT:
1. Wake from deep sleep (RTC timer or external interrupt)
2. Initialize peripherals
3. Take reading
4. Connect to WiFi / radio
5. Publish data
6. Disconnect
7. Enter deep sleep for N minutes

The entire active window should be under 2 seconds. Every millisecond of WiFi active time costs you battery life.

---

## Related
- [[hardware/07-connectivity|Connectivity]] — how devices reach the layer above
- [[hardware/09-putting-it-all-together|Putting It All Together]] — the whole picture
- [[architecture/04-distributed-systems/README|Distributed Systems]] — a device fleet is a distributed system with a physical body
- [[robotics/README|Robotics]] — the direction this leads if the devices move
