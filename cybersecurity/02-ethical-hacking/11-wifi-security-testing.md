# Wi-Fi Security Testing

Testing your own wireless network's security — checking whether your passphrase would hold up, whether WPS is exposing a shortcut around it — is one of the most common legitimate, no-authorization-paperwork-needed exercises in this whole field, precisely because you already own the network. The moment a network isn't yours, this becomes [[01-rules-of-engagement-and-legal|exactly the authorization question]] covered in that note — everything below assumes you're testing your own router and your own devices, on your own network, the way the built-in tools' own documentation frames their primary legitimate use.

## How WPA2 authentication actually works

WPA2-Personal (the common home Wi-Fi security standard) authenticates devices via a **4-way handshake**: when a device joins the network, the router and the device exchange four messages that let both sides independently derive a shared session key from the network passphrase, without ever sending the passphrase itself over the air. Critically, that handshake is visible to anyone listening on the same channel — capturing it doesn't hand you the passphrase, but it hands you enough information to test password guesses against, **offline**, without touching the network again.

## The general methodology

1. **Monitor mode** — put a Wi-Fi adapter into a mode where it captures all traffic on a channel, not just traffic addressed to it (`airmon-ng start wlan0`).
2. **Capture the handshake** — listen for a device's 4-way handshake with the target router (`airodump-ng`). If nothing is joining naturally, a **deauthentication frame** can be sent to a connected device, forcing it to disconnect and automatically reconnect, producing a fresh handshake to capture (`aireplay-ng --deauth`).
3. **Crack it offline** — run a dictionary or mask (pattern-based) attack against the captured handshake, using **aircrack-ng** or, far faster on a GPU, **hashcat** (mode 22000 for the current handshake format).

```
# illustrative shape of the workflow, not a copy-paste attack script:
airmon-ng start wlan0
airodump-ng wlan0mon
aireplay-ng --deauth 5 -a <router_bssid> wlan0mon
aircrack-ng -w rockyou.txt capture.cap
```

`wifite` automates this whole sequence (monitor mode, handshake capture, deauth, cracking attempt) into one guided tool, and is the common starting point for testing your own network end to end rather than driving each step by hand.

## Why this only threatens weak passphrases

A dictionary/mask attack tries candidate passphrases and checks each one against the captured handshake — it succeeds only if the real passphrase is in the wordlist or matches the pattern being tried. A long, random, high-entropy passphrase (16+ characters, not a dictionary word or a name-plus-year pattern) is not practically crackable this way with current hardware — this is the direct, actionable takeaway: **passphrase strength is what this entire attack class actually tests**, and it's the first thing worth fixing on your own network if a crack succeeds quickly.

## WPS — a common shortcut around a strong passphrase

WPS (Wi-Fi Protected Setup) lets a device join a network using an 8-digit PIN instead of the full passphrase, meant for easy setup. Its PIN structure has a well-known design flaw (the PIN is effectively validated in two much shorter halves), making it crackable via an online brute-force attempt (**reaver**, **bully**) or, on some routers, an offline "Pixie Dust" attack against a weak PIN-generation implementation — often far faster than cracking the passphrase directly, and completely bypasses passphrase strength entirely. **Disabling WPS is one of the single highest-value fixes** on almost any home router, regardless of how strong the actual passphrase is.

## WPA3 — why it resists this attack class structurally

WPA3 replaces the 4-way handshake with **SAE (Simultaneous Authentication of Equals)**, which provides forward secrecy and is specifically designed to resist exactly this offline-dictionary-attack pattern — capturing a WPA3 SAE exchange doesn't hand an attacker something they can crack offline the way a WPA2 handshake does. If your own router supports WPA3, enabling it is a more structural fix than passphrase strength alone.

## Defensive checklist for your own network

- Use WPA3 if the router and all devices support it; otherwise WPA2 with a long, random passphrase.
- Disable WPS entirely.
- MAC address filtering and hiding your SSID are not real security controls — both are trivially bypassed by anyone actively monitoring traffic, and add inconvenience without meaningfully raising attacker cost.
- Keep router firmware updated — router-specific vulnerabilities (not just protocol-level weaknesses) are a common real-world entry point.

## Gotchas

- **Only test networks and devices you own or have explicit permission to test** — capturing handshakes or sending deauth frames against a neighbor's network, even "just to see," is unauthorized access to a communications system in most jurisdictions, not a gray area.
- A deauth attack disconnects **every** device on the network briefly, including your own other devices (or a family member's) — expect and plan for that disruption even when testing your own network.
- Most laptop built-in Wi-Fi chipsets don't support monitor mode or packet injection — this is covered as a practical setup concern in [[04-lab-setup-and-os-choice|lab-setup-and-os-choice]].

## Related
- [[04-lab-setup-and-os-choice|lab-setup-and-os-choice]]
- [[08-common-tools|common-tools]]
- [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]]
