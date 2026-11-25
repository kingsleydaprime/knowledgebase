# Attacks and Threats

**This section is the attacker's catalogue: a structured tour of how attacks actually work, from fooling a person to abusing a bug in a program, so you can recognise, detect and defend against each one.**

The earlier sections mostly built defences. This one names and explains the attacks those defences exist for, organised by what they target: the person, the network, the web app, and the credentials and machine underneath. Every attack here has a defence somewhere earlier in the course, and each lesson points to it. It's educational and defensive throughout: how attacks work so you can stop them, practised only against targets you own.

## What you'll be able to do

By the end of this section you will be able to:

- recognise the forms of social engineering, and read an email's SPF, DKIM and DMARC results;
- run and detect an ARP-spoofing man-in-the-middle attack in an isolated lab;
- use the OWASP Top 10 as a vocabulary and a review checklist, and classify any web finding;
- tell the password attacks apart, detect password spraying from logs, and explain malware types and software exploits.

## Reading order

1. [[cybersecurity/06-attacks-and-threats/01-social-engineering|01 — Social Engineering]] — **[Beginner]** — attacking the person: phishing and its variants, BEC, pretexting, and reading email authentication.
2. [[cybersecurity/06-attacks-and-threats/02-network-attacks|02 — Network Attacks]] — **[Intermediate]** — man in the middle, ARP, DHCP and DNS spoofing, Wi-Fi attacks, DoS, replay, with an ARP-spoofing Docker lab.
3. [[cybersecurity/06-attacks-and-threats/03-web-application-attacks|03 — Web Application Attacks]] — **[Intermediate]** — the OWASP Top 10, broken access control, injection, XSS, SSRF, and the two root causes.
4. [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|04 — Password Attacks, Malware and Exploits]] — **[Intermediate→Advanced]** — spraying, stuffing, pass-the-hash, malware types, buffer overflows and zero-days, with a spraying-detection lab.

## Related

- [[cybersecurity/index|The cybersecurity course]] — the whole map.
- [[cybersecurity/02-ethical-hacking/index|Ethical hacking]] — the method for testing these safely and legally.
- [[cybersecurity/07-security-operations/index|Security operations]] — detecting and responding to these attacks.
- [[cybersecurity/04-web-security/index|Web security]] and [[cybersecurity/03-network-security/index|network security]] — the defences, built on the lab.

## About this section

**How it's built:** four lessons organised by target (person, network, web app, credentials and machine), each a structured catalogue with a hands-on element: reading email headers, an ARP-spoofing Docker lab, classifying Juice Shop findings by OWASP category, and a password-spraying detector. Every attack links to its defence earlier in the course. Rebuilt to the [[COURSE-STANDARD|course standard]]: all four lessons converted. Live runs are tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
