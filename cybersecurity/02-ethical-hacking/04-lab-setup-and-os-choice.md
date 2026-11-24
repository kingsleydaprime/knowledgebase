---
id: 7a407425-747f-4f5e-9edf-eb63de1d078d
---

# Lab Setup and OS Choice

**Before you attack anything, you have to decide what to attack *from*: which operating system, on what hardware, kept isolated so your practice can never leak onto a system you don't own.**

## Before you start
<!-- bite: 70bde23d-cc56-4be5-a96a-7fa6d98847d0 -->

You should be able to:

- Run basic Linux commands and install packages → [[languages/index|the languages course]] or any Linux intro.
- Say what a virtual machine and a container are, roughly → [[devops/index|DevOps]] if not.

After this lesson you will be able to:

1. Choose an attacker OS (Kali, Parrot, or your own Linux plus tools) and say why.
2. Choose between a VM, a container, and bare metal for running it, and know the trade-offs.
3. Avoid the single most common wireless-testing mistake before spending any money.
4. Keep your lab isolated from your real network, and test your own phone sensibly.

**Study route.** Kid version and §1–5, then the practice task (decide and write down your own setup). The actual install is lesson 05.

## What a lab setup is

This lesson is the set of choices; [[cybersecurity/02-ethical-hacking/05-home-lab-setup|lesson 05]] is the concrete build.

## The kid version
<!-- bite: 8f8b64e9-1c95-4d45-b6fe-60470f79b974 -->

A mechanic doesn't work on a car in your living room. They have a garage: a space built for messy, risky work, with the right tools on the wall, and a floor you can hose down. If they spill oil or a part catches fire, it's contained — the house is fine.

Your lab is that garage. The attacker OS is the wall of tools. The "isolated network" is the garage being a separate room from the house, so nothing you do leaks into your real life. And a snapshot is being able to magically reset the garage to spotless in one minute.

**Where the analogy stops working.** A garage is one physical room. Your lab is mostly made of *virtual* rooms — VMs and containers — that you can create, clone and delete in seconds. That flexibility is the whole reason we don't just install the tools on your everyday laptop and call it a day.

## 1. The attacker OS — three sensible choices
<!-- bite: c23e49e2-0801-4c6a-bf49-19b0af064074 -->

You run your tools from somewhere. Three reasonable options, from least to most setup:

1. **Kali Linux** — the most-used, best-documented pentest distribution. It ships with essentially every tool in [[cybersecurity/02-ethical-hacking/08-common-tools|common tools]] pre-installed. The default for beginners *specifically because* when something breaks, "Kali + that tool + that error" is the most-searched combination on the internet.
2. **Parrot OS** — very similar tool set, lighter on resources, a slightly friendlier everyday desktop. Preference, not capability, once you're past the start.
3. **Your own Linux plus the tools** — on a Linux host (Fedora, Ubuntu), you can just install `nmap`, `wireshark`, `burpsuite` and the rest yourself. More setup, but it forces you to understand what each tool needs instead of treating a pre-built distro as a black box. A good path once you're comfortable.

For a first lab, Kali or Parrot removes a pile of setup that has nothing to do with learning security. There's no wrong answer here — the tools are the same `nmap` underneath.

## Terms used in this lesson
<!-- bite: 595727cc-84a6-4298-83c2-a761b3237e18 -->

1. **Attacker OS**: This is the machine you run your tools *from* — also called the attack box. Kali is the common one.
2. **Virtual machine (VM)**: This is a whole computer simulated in software, with its own OS, running on your real machine. Heavy, but fully isolated.
3. **Container**: This is a lighter way to run software in isolation, sharing the host's kernel. A Docker container starts in seconds and uses far less memory than a VM.
4. **Bare metal**: This means installing an OS directly on physical hardware, with no VM or container in between.
## Terms used in this lesson: snapshots, networks and Wi-Fi cards

The last four terms are about undoing mistakes, keeping the lab sealed, and Wi-Fi hardware.

5. **Snapshot**: This is a saved frozen state of a VM you can jump back to instantly, undoing anything you did since.
6. **Host-only network**: This is a virtual network that connects your VMs to each other and your host, but **not** to your real router or the internet. The containment the lab depends on.
7. **Monitor mode**: This is a Wi-Fi card setting that lets it capture *all* nearby wireless traffic, not just traffic addressed to it. Needed for [[cybersecurity/02-ethical-hacking/11-wifi-security-testing|Wi-Fi testing]], and many built-in cards can't do it.
8. **Packet injection**: This is a Wi-Fi card's ability to *send* crafted frames, not just receive. Also needed for wireless testing, and also missing from most built-in cards.

## 2. VM, container, or bare metal
<!-- bite: 8aaa3cd0-5a6b-4d36-ac4a-69275990b1e3 -->

Where should the attacker OS and the targets actually run? Three options, and you'll mix them:

- **Container (Docker)** — the lightest. A target like Juice Shop runs in one command and a few hundred megabytes. Perfect for web-app targets and for a memory-limited laptop. Less suited to simulating a whole separate *machine* with many services.
- **Virtual machine** — a whole simulated computer. Heavier (gigabytes of RAM each), but it gives you **snapshots**, full **isolation**, and **disposability** — delete and rebuild in minutes. The right choice for the attacker OS and for multi-service targets.
- **Bare metal** — installing directly on hardware. Only worth it when you need something a VM can't cleanly give you — above all, Wi-Fi monitor mode (§3).

**On a 16 GB laptop**, lean on containers: run your targets as Docker containers and your tools either on the host Linux directly or in one modest Kali VM. Three full VMs at once will fight you for memory; one VM plus containers won't.

## 3. The Wi-Fi adapter gotcha — read before buying anything
<!-- bite: e0c2ea24-229f-470a-a0a4-4e99f7a8efef -->

This is the single most common wall people hit in [[cybersecurity/02-ethical-hacking/11-wifi-security-testing|wireless testing]], and it costs money and hours if you learn it the hard way:

**Most laptops' built-in Wi-Fi chips can't do monitor mode or packet injection at all.** And even the ones that technically can are usually unreliable when passed through into a VM, because USB-wireless passthrough is fiddly.

The fix is a **dedicated external USB Wi-Fi adapter** with a chipset known to support monitor mode and injection. The Atheros AR9271 and Ralink RT3070 chipsets are the classic, well-documented recommendations, precisely because Kali's and Parrot's drivers support them cleanly out of the box. **Check the chipset before you buy** — buying on brand or price and then discovering the hardware simply can't do monitor mode is the frustration this paragraph exists to spare you. (You don't need any of this until lesson 11; just don't buy the wrong thing early.)

## 4. Keeping the lab isolated
<!-- bite: 822955a6-58ed-4c6d-bf4e-9af71959b34f -->

The one rule that makes a lab a lab and not a hazard: **your deliberately-weak targets must not be reachable from your real network or the internet.**

- For **VMs**, that means a **host-only network** (lesson 05 builds one). The targets can talk to your attacker VM and nothing else.
- For **containers**, Juice Shop bound to `localhost:3000` is only reachable from your own machine — already isolated. Don't publish a vulnerable container's port to `0.0.0.0` on a VPS without a firewall in front, or you've put a deliberately-broken app on the public internet.
- Keep your attacker OS and tools **updated**. Running a years-old scanner misses newer checks and, ironically, runs software with its own unpatched holes.

Isolation is why you can run genuinely exploitable software on purpose: it has nowhere to spread. Break that isolation and the same software becomes a liability.

## 5. Testing your own phone
<!-- bite: 26990939-2d30-4db2-9cf0-7cffd15e25a4 -->

Your phone is a fair target — it's yours — and a lot of mobile testing needs no special setup:

- **Routing its traffic through a proxy** (like Burp Suite set as a device-wide proxy) lets you watch and tamper with what an app sends. This works on **both Android and iOS without rooting or jailbreaking**, and covers a lot of ground on its own.
- **Android** has an accessible unlock-and-root path on many devices, which is what you need for anything deeper than traffic inspection. Rooting your own device is unambiguously your call on hardware you own (it does affect warranty).
- **iOS** is far more locked down; deep testing usually needs a jailbreak, which is harder to maintain across versions. But proxy-based traffic inspection often works jailbreak-free and is where most practical mobile app-sec starts.

## Worked example — choosing a setup for a 16 GB laptop
<!-- bite: 4a547e3e-9b6f-462a-b7d8-e5d5bee39c58 -->

Here's a concrete, justified setup for exactly the constraints most learners have — a single laptop with 16 GB of RAM running Linux. This is the setup lesson 05 then builds:

| Decision | Choice | Why |
| --- | --- | --- |
| Attacker OS | Tools on the host Linux, **or** one lightweight Kali VM | Avoids running multiple heavy VMs; the host already is Linux. |
| Tier-1 target | **Juice Shop in Docker** (`localhost:3000`) | A few hundred MB, starts in seconds, isolated to localhost. |
| Multi-service target | Your **VPS** (when you rent one) | A real host with many services for `nmap` practice, without a second heavy local VM. |
| Isolation | localhost binding + the VPS firewall | No deliberately-weak app ever exposed to the public net. |
| Wireless | Nothing yet | Buy an AR9271 adapter only when you reach lesson 11. |

**Why this and not three VMs:** the classic lab (Kali + Metasploitable + DVWA as three VMs) is excellent but wants ~6–8 GB of RAM running at once. On 16 GB that's tight alongside a browser and an IDE. Containers plus one VM get you the same practice ground with room to breathe — and the VPS gives you a *more* realistic multi-service host than Metasploitable anyway. Lesson 05 keeps the three-VM build as an alternative for when you want purely-local network targets.

## Common pitfalls and traps
<!-- bite: dd64d5bc-1c65-4b1c-a38d-74deff797f44 -->

1. **Buying a Wi-Fi adapter before checking the chipset.** The number-one wasted purchase. AR9271 / RT3070, or check compatibility first.
2. **Running three heavy VMs on a small laptop.** They starve each other of memory. Use containers for targets.
3. **Exposing a vulnerable container's port publicly.** `-p 3000:3000` on a VPS with no firewall puts a deliberately-broken app on the internet. Keep it to localhost or behind a firewall.
4. **Letting the attacker OS go stale.** Old tools miss new checks and carry their own vulnerabilities.
5. **Running everything as root by reflex.** Understand *why* a step needs elevated privilege; the habit of not thinking about it is worth breaking early.

## Check your understanding
<!-- bite: e0b0afc3-748d-4f38-8266-ad48a7e4a2d5 -->

Try each one before you open the answer.

1. <!-- q: mcq id="39400d66" -->
   You have a laptop with 16 GB of RAM and want to practise against a vulnerable web app without bogging the machine down. What's the lightest sensible choice?

   - [ ] Run Kali, Metasploitable2 and DVWA as three VMs at once.
   - [x] Run the web app as a Docker container, with your tools on the host or one small VM.
   - [ ] Install the vulnerable app directly on your host OS (bare metal).
   - [ ] Rent three separate VPSes.

   <details><summary>Answer</summary>

   A container is the lightest isolated option — a few hundred MB, seconds to start — and keeps the vulnerable app off your real system. Three VMs would fight for memory on 16 GB; installing the vulnerable app on bare metal destroys the isolation that makes a lab safe.

   </details>

2. <!-- q: mcq id="4ee6e109" -->
   Why is a **host-only network** central to a VM-based lab?

   - [ ] It makes the VMs run faster.
   - [ ] It gives the VMs internet access for updates.
   - [x] It lets the lab VMs talk to each other and the host, but not to your real router or the internet.
   - [ ] It encrypts traffic between the VMs.

   <details><summary>Answer</summary>

   Host-only networking is the containment: deliberately-vulnerable VMs can reach the attacker VM and the host, but not your real LAN or the internet, so the weak software has nowhere to spread. It isn't about speed, updates, or encryption.

   </details>

3. <!-- q: gap id="a386a855" answers="monitor mode" -->
   The Wi-Fi card setting that captures all nearby wireless traffic, not just traffic addressed to your card, is called ___ — and most built-in laptop Wi-Fi chips can't do it.

   <details><summary>Answer</summary>

   Monitor mode. Together with packet injection, it's why wireless testing usually needs a dedicated external adapter (an AR9271 or RT3070 chipset), checked before buying.

   </details>

4. <!-- q: mcq id="643fda8a" -->
   You want to inspect and tamper with the traffic your own phone's app sends, on an ordinary non-jailbroken iPhone. What's true?

   - [x] You can route its traffic through a proxy like Burp without jailbreaking, and inspect it.
   - [ ] You must jailbreak the iPhone before you can see any of its traffic.
   - [ ] iOS traffic can never be inspected on your own device.
   - [ ] Only Android allows any kind of app testing.

   <details><summary>Answer</summary>

   Proxy-based traffic inspection works on a stock iPhone (and Android) without jailbreaking or rooting, and covers a lot of practical mobile app-sec. Jailbreaking/rooting is only needed for deeper testing beyond watching and tampering with traffic.

   </details>

5. <!-- q: open id="874c4472" -->
   A friend says "just install Metasploitable on your laptop normally so it's always ready." Why is this a bad idea, in terms of what makes a lab safe?

   <details><summary>Answer</summary>

   Metasploitable is deliberately full of unpatched, exploitable services. Installed on bare metal on your everyday laptop — reachable on your real network and potentially the internet — it's not a contained target, it's a genuinely vulnerable machine that an attacker (or malware) could use as a foothold, and it can interfere with your real devices. The isolation (a host-only network, or a container bound to localhost) is exactly what lets you run intentionally-weak software safely; removing it turns the lab into a liability.

   </details>

## Practice — write down your own setup
<!-- bite: ec1bce20-3fc5-41e2-9fc0-c2c7447590e0 -->

**Task.** Decide and record the lab setup you'll actually build in lesson 05. One short page.

**Your note must state:**
- Your attacker OS (Kali VM, Parrot, or tools on your host Linux) and one sentence of why.
- Where each target runs (container for the web app; VPS or VM for a multi-service host).
- How each target is isolated (localhost binding; host-only network; VPS firewall).
- Whether you'll need a Wi-Fi adapter yet (you won't, until lesson 11 — note the chipset to buy when you do).

## Practice: when your setup note is done

Here is how you know the note is finished, plus one stretch step.

**Done when:** your note answers "what do I attack from, what do I attack, and how is it contained?" for every piece — and it fits your actual hardware (don't plan three VMs if you have 16 GB).

**Stretch.** Add a line on how you'll keep the attacker OS and tools updated, and why a stale attack box is both less capable and less safe.

## Before moving on
<!-- bite: 211a7888-8115-4db5-8118-1bc04d1dc1ab -->

You can now choose an attacker OS, pick between a container, a VM and bare metal with the trade-offs in mind, dodge the wireless-adapter trap, and keep a lab isolated. You have a setup decided that fits your hardware.

**Recap for later lookup:** attacker OS = Kali/Parrot/your-own-Linux. Containers for web targets (light, localhost), one VM for the attacker or a multi-service target, bare metal only for Wi-Fi monitor mode. Isolate everything (host-only net / localhost / firewall). Buy an AR9271/RT3070 adapter only when you reach wireless.

Next: [[cybersecurity/02-ethical-hacking/05-home-lab-setup|home lab setup]] — building this, with Juice Shop running tonight.

## Related
<!-- bite: 211a7888-8115-4db5-8118-1bc04d1dc1ac -->

- [[cybersecurity/02-ethical-hacking/05-home-lab-setup|Home lab setup]] — the concrete, step-by-step build of everything here.
- [[cybersecurity/02-ethical-hacking/08-common-tools|Common tools]] — what the attacker OS comes loaded with.
- [[cybersecurity/02-ethical-hacking/11-wifi-security-testing|Wi-Fi security testing]] — where the adapter gotcha pays off.

## About this lesson
<!-- bite: fb1422b3-157e-4d31-ac70-2cad6cf25f36 -->

**Level:** Beginner. **Covers:** choosing an attacker OS (Kali/Parrot/own Linux), VM versus container versus bare metal, the Wi-Fi monitor-mode adapter gotcha, lab isolation, and testing your own phone. **Where it sits:** lesson 4 of the [[cybersecurity/02-ethical-hacking/index|Ethical Hacking]] section — the choices behind the build in lesson 5. **Sources:** the original vault note, reframed toward a container-first, VPS-backed lab suited to a 16 GB laptop, with the three-VM classic kept as an alternative. `[reference]` — not drawn from a personal paid engagement.
