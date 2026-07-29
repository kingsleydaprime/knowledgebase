# Lab Setup & OS Choice

Before running any of the techniques in this folder against your own devices, the practical question is what to actually run them *from* — which OS, on what hardware, and how to keep testing safely contained to things you own.

## Kali Linux vs Parrot OS vs "just install the tools yourself"

- **Kali Linux** — the most widely used, most widely documented penetration-testing distribution; ships with essentially every tool mentioned in [[08-common-tools|common-tools]] preinstalled and configured. The default recommendation for beginners specifically because the documentation and community troubleshooting for "Kali + this tool" is the largest and easiest to find.
- **Parrot OS** — a close alternative with a similar tool set, generally lighter on system resources and with a somewhat more "daily driver friendly" default desktop — a matter of preference more than capability once you're past the beginner stage.
- **Vanilla Debian/Ubuntu + installing tools individually** — more setup work, but forces you to actually understand what each tool needs and how it's configured, rather than treating a pre-built distro as a black box. A reasonable path once you're past the beginner stage and want a deeper understanding of your own environment.

For someone starting out, Kali (or Parrot) removes a large amount of setup friction that has nothing to do with actually learning the security concepts — a completely reasonable trade-off early on.

## Virtual machine vs. bare metal

Running your pentesting OS as a **VM** (VirtualBox, VMware, or UTM on Apple Silicon) rather than installing it directly on your main machine is the standard approach, for good reasons:

- **Snapshots** — take a snapshot before trying something risky, roll back instantly if it breaks.
- **Isolation** — the VM's network can be kept separate from your host machine and your real, everyday-use network segment.
- **Disposability** — a misconfigured or compromised (in a training/CTF context) VM can be deleted and rebuilt in minutes, versus reinstalling an entire physical machine.

Bare metal only becomes worth the setup cost when you need hardware capability a VM can't cleanly provide — most notably, Wi-Fi adapter monitor mode (see below).

## The Wi-Fi adapter gotcha

This is the single most common practical stumbling block for [[11-wifi-security-testing|wifi-security-testing]] specifically: **most laptop built-in Wi-Fi chipsets don't support monitor mode or packet injection at all**, and even when they technically do, USB passthrough into a VM is often unreliable for wireless hardware specifically. The practical fix is a dedicated **external USB Wi-Fi adapter** with a chipset known to support monitor mode and injection (Atheros AR9271 and Ralink RT3070-based adapters are common, well-documented recommendations specifically because Kali/Parrot's drivers support them cleanly). Buying the wrong adapter and spending hours debugging driver issues before realizing the hardware itself doesn't support monitor mode is an extremely common early frustration — checking chipset compatibility before buying anything saves that entirely.

## Building a home lab to practice against

Rather than only ever testing your live home router (which you don't want to leave misconfigured or knocked offline for long), a home lab gives you disposable, resettable targets:

- **Vulnerable-by-design VMs** — Metasploitable, DVWA (Damn Vulnerable Web Application), and similar images are intentionally full of known weaknesses, meant specifically to be attacked and reset.
- **A spare/old router** flashed with test configurations — lets you practice [[11-wifi-security-testing|wifi-security-testing]] techniques against known settings you control completely, without touching your actual daily-use network.
- **HackTheBox / TryHackMe** — hosted, legally sanctioned target machines, covered in [[08-common-tools|common-tools]], that remove the need to build and maintain your own vulnerable infrastructure at all while you're still learning.

## Testing your own phone

- **Android** — has an accessible bootloader-unlock and rooting path on many devices, which is generally what's needed to do anything beyond surface-level testing (inspecting installed app permissions, network traffic via a proxy like Burp Suite configured as a device-wide proxy). Rooting your own device voids warranty considerations but is unambiguously your call to make on hardware you own.
- **iOS** — far more locked down by design; meaningful security testing generally requires a jailbreak, which is harder to maintain across iOS versions and carries more limitations than Android's rooting ecosystem. Testing an iOS app's network traffic (via a proxy) is often possible without a jailbreak at all, and covers a lot of practical ground on its own.

## Gotchas

- Keep your pentesting VM's tools and OS updated — running years-outdated versions of scanners/exploitation frameworks means missing newer checks and, ironically, running software with its own unpatched vulnerabilities.
- Isolate your lab network from your home production network where practical (a separate VLAN or a dedicated router) — this prevents an intentionally-vulnerable practice VM from being reachable by (or interfering with) your actual devices.
- Running tools as root out of habit, without thinking about why a given step needs it, is a common bad habit worth breaking early — understanding *why* a specific action needs elevated privilege is part of actually understanding the tool.

## Related
- [[05-home-lab-setup|home-lab-setup]] — the concrete, step-by-step build of everything described above
- [[08-common-tools|common-tools]]
- [[11-wifi-security-testing|wifi-security-testing]]
- [[14-career-path-and-best-practices|career-path-and-best-practices]]
