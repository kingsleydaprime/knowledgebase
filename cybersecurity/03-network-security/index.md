# Network Security

**Network security is controlling who can reach what on a network, protecting data while it travels, and noticing when someone tries to get past those controls.**

The ethical-hacking section attacked your own VPS: you scanned it and found SSH, a web server and a database all answering the internet. This section is the other side of that same box. You defend what you attacked, one layer per lesson, and every lesson ends by proving the defence works and writing what would catch an attacker.

## What you'll be able to do

By the end of this section you will be able to:

- put a default-deny firewall on a server, prove it with a rescan, and read the block log;
- split an app into network zones so the database can't be reached by anything except the app, and prove each wall;
- build a WireGuard tunnel and hide SSH behind it, so the internet can't even find it;
- run an intrusion detection system and write your own rules that catch your own scan and SQL injection.

## The four layers

Each lesson adds one layer to the same VPS:

1. **Close the doors** — a firewall decides what reaches the box at all.
2. **Split the inside** — zones decide what can reach what once something is in.
3. **Hide the admin door** — a tunnel puts SSH out of the internet's sight.
4. **Watch** — an IDS notices when someone tries anyway.

No single layer is enough on its own. That's the point: each catches what the others miss.

## Reading order

1. [[cybersecurity/03-network-security/01-firewalls|01 — Firewalls]] — **[Beginner]** — default deny, stateful filtering, a UFW lockdown of your VPS proven with nmap, and the Docker gotcha.
2. [[cybersecurity/03-network-security/02-network-segmentation|02 — Network Segmentation]] — **[Intermediate]** — flat networks, the common zones, Zero Trust, and a Docker lab where the database has no route in or out.
3. [[cybersecurity/03-network-security/03-vpns-and-encryption-in-transit|03 — VPNs and Encryption in Transit]] — **[Intermediate]** — who can read your traffic, VPN versus TLS, and SSH moved behind your own WireGuard tunnel.
4. [[cybersecurity/03-network-security/04-intrusion-detection-and-prevention|04 — Intrusion Detection and Prevention]] — **[Advanced]** — IDS versus IPS, signatures and anomalies, and Suricata rules that catch your own attacks.

## Related

- [[cybersecurity/index|The cybersecurity course]] — the whole map.
- [[cybersecurity/02-ethical-hacking/index|Ethical hacking]] — the attacker's side of the same VPS.
- [[cybersecurity/04-web-security/index|Web security]] — what has to protect the app itself, since the network lets web traffic in on purpose.
- [[networking/index|Networking]] — ports, routing, NAT and TLS, the ground this section stands on.

## About this section

**How it's built:** the defender's side of the lab VPS from the ethical-hacking section, one layer per lesson, each lesson ending with a proof (a rescan, a wall test, a public scan, a caught attack) and a detection. Lessons 02 and 04 run on the laptop alone; 01 and 03 need the VPS. Rebuilt to the [[COURSE-STANDARD|course standard]]: all four lessons converted. Live runs of the commands are tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
