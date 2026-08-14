# Embedded Systems

**[Beginner → Intermediate]** — What makes a system "embedded," bare metal vs an RTOS, how memory differs when there are kilobytes of it, and the firmware loop everything runs inside.

## What Makes a System "Embedded"?

An embedded system is a computer built *into* something else to control it or sense it. It's not a general-purpose computer you use for whatever you want — it has a dedicated job.

- The computer inside your washing machine: embedded system
- The controller inside a smart thermostat: embedded system
- An Arduino reading a soil moisture sensor and opening a valve: embedded system
- Your laptop running VS Code: not embedded

The defining characteristics:
- **Dedicated function** — does one job (or a small set of jobs)
- **Resource constrained** — limited RAM, storage, CPU speed
- **Real-time requirements** — often needs to respond within guaranteed time windows
- **Runs forever** — usually runs in an infinite loop with no "shutdown"

## Bare Metal vs RTOS

**Bare metal** means you write code that runs directly on the hardware with no operating system in between. Your `main()` function typically looks like:

```c
int main() {
    // initialize hardware once
    setup();

    // run forever
    while (1) {
        loop();
    }
}
```

This is what Arduino does. It's simple, fast, and predictable — but it breaks down when you need to do multiple things "at the same time."

**RTOS (Real-Time Operating System)** — FreeRTOS, Zephyr, ThreadX — gives you tasks (like threads) that can run concurrently, plus things like mutexes, queues, and timers. You use an RTOS when:

- You need to handle multiple independent tasks (reading a sensor while also serving a web request while also blinking an LED)
- You have hard timing requirements (this interrupt must be handled within 100 microseconds, no matter what)
- Your system complexity grows beyond what a simple loop can manage cleanly

## Memory in Embedded Systems

Embedded systems have three types of memory and you need to understand all three:

| Memory | What it is | Volatile? | Typical size |
|---|---|---|---|
| **Flash** | Program storage — where your code lives | No (survives power-off) | 256KB – 4MB |
| **SRAM** | Working memory — stack, heap, variables | Yes (gone on power-off) | 2KB – 512KB |
| **EEPROM** | Tiny, byte-addressable persistent store | No | 512B – 4KB |

Flash is where you "flash" your firmware. SRAM is where your variables live at runtime. EEPROM is where you save settings that need to survive a reset (like WiFi credentials, calibration offsets).

The pain: SRAM is tiny. On an ATmega328P (classic Arduino Uno chip), you have **2KB of SRAM**. A single `String` object can eat hundreds of bytes. This is why embedded C developers are fanatical about memory — you can't just malloc your way out of problems.

## The Firmware Loop

Most embedded firmware follows this structure mentally, even if the code looks different:

1. **Initialize** — set up clocks, peripherals, GPIOs, configure UART baud rate, etc.
2. **Main loop** — poll sensors, handle events, update outputs, communicate
3. **Interrupts** — asynchronous handlers that fire when something happens (button pressed, byte received, timer expired) and temporarily preempt the main loop

Interrupts are critical to understand. If you poll a button 1000 times per second in your loop, you waste CPU and might still miss a very fast press. An interrupt fires *immediately* when the pin changes state, regardless of what the CPU is doing, handles it, then returns control to the main loop.

## GPIO — General Purpose Input/Output

GPIO pins are the hands of a microcontroller — they're how it interacts with the physical world.

- **Output mode** — set the pin HIGH or LOW to turn things on/off (LED, relay, transistor)
- **Input mode** — read whether the pin is HIGH or LOW (button, digital sensor)
- **Input with pull-up/pull-down** — a resistor connecting the pin to VCC or GND to give it a defined default state when nothing is connected (floating pins read garbage)

Most MCUs let you configure this in software. On an ESP32 you'd write:

```c
gpio_set_direction(GPIO_NUM_2, GPIO_MODE_OUTPUT);
gpio_set_level(GPIO_NUM_2, 1);  // HIGH
```

---

## Related
- [[hardware/04-microcontrollers|Microcontrollers]] — the chips this runs on
- [[hardware/02-digital-and-analog|Digital vs Analog]] — what GPIO and ADC pins are reading
- [[foundations/os/README|Operating Systems]] — the same scheduling ideas, with megabytes instead of kilobytes
- [[devops/01-linux/19-the-boot-process|The Boot Process]] — the grown-up version of a bootloader handing off
