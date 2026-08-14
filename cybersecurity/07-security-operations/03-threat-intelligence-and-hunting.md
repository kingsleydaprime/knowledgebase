# Threat Intelligence & Hunting

**[reference]** — from the roadmap.sh cyber-security roadmap. Moving from *reactive* (wait for an alert) to *proactive* (know your adversary, go looking) defense — and the frameworks that give the whole field a shared language for attacker behavior.

## Threat intelligence

**Threat intelligence** is knowledge about adversaries — who they are, what they target, how they operate — used to defend proactively. It ranges from:

- **Strategic** — high-level trends for leadership (which threat actors target our industry).
- **Operational** — attacker campaigns, tactics, and infrastructure.
- **Tactical** — concrete **IOCs** (Indicators of Compromise): malicious IPs, domains, file hashes, URLs you can feed into [[cybersecurity/07-security-operations/02-logging-siem-and-detection|detection]].

**OSINT** (Open-Source Intelligence) is gathering intel from public sources — WHOIS, DNS records, certificate transparency, social media, breach dumps, Shodan. It's how attackers do [[cybersecurity/02-ethical-hacking/03-reconnaissance|reconnaissance]] *and* how defenders discover their own exposed assets and track adversaries. Sources feed threat-intel **platforms** (MISP, commercial feeds) that share indicators across the community.

The maturity note: IOCs (hashes, IPs) are the *lowest* rung — attackers change them cheaply. Higher-value intel is **TTPs** (Tactics, Techniques, Procedures) — *how* an adversary behaves — which is much harder for them to change, which is exactly what the frameworks below capture.

## The frameworks — a shared language for attacks

These give defenders a structured way to describe, detect, and communicate about attacker behavior:

### Cyber Kill Chain (Lockheed Martin)

Models an intrusion as sequential stages: **Reconnaissance → Weaponization → Delivery → Exploitation → Installation → Command & Control (C2) → Actions on Objectives.** The value: every stage is a chance to *break the chain* — detect and disrupt at any step and the attack fails. It maps cleanly onto the offensive [[cybersecurity/02-ethical-hacking/02-penetration-testing-methodology|pentest methodology]].

### MITRE ATT&CK

The industry-standard **knowledge base of adversary tactics and techniques**, observed from real attacks. Organized as a matrix: **tactics** (the *why* — the adversary's goal, e.g. Initial Access, Persistence, Privilege Escalation, Lateral Movement, Exfiltration) across the top, and **techniques** (the *how* — specific methods, each with an ID like T1566 Phishing) underneath. It's the lingua franca of blue teams — detection rules, threat reports, and hunts are all mapped to ATT&CK technique IDs, so everyone means the same thing. If you learn one framework deeply, learn this one.

### Diamond Model

Analyzes an intrusion via four linked vertices — **Adversary, Capability, Infrastructure, Victim** — for understanding *who* is attacking *how* against *whom*, useful for attribution and connecting related incidents.

## Threat hunting

**Threat hunting** is *proactively* searching for attackers who evaded automated [[cybersecurity/07-security-operations/02-logging-siem-and-detection|detection]] — assuming breach and going to look, rather than waiting for an alert. A hunt is **hypothesis-driven**: "if an attacker used pass-the-hash for lateral movement (an ATT&CK technique), I'd see *this* pattern in the logs — let me search for it." The hunter queries the SIEM/EDR data, confirms or refutes, and — crucially — **turns any finding into a new automated detection** so the next occurrence alerts on its own.

Hunting is what separates a mature SOC from an alert-monitoring one: it finds the sophisticated, low-and-slow adversaries ([[cybersecurity/01-fundamentals/03-attacker-and-hacker-types|APTs]]) that never trip a signature. It depends on good telemetry (logs/EDR), knowledge of ATT&CK, and understanding your own environment's "normal."

## Related
- [[cybersecurity/07-security-operations/02-logging-siem-and-detection|Logging, SIEM & Detection]] — the data hunts run against
- [[cybersecurity/07-security-operations/04-incident-response|Incident Response]] — what a confirmed hunt finding triggers
- [[cybersecurity/02-ethical-hacking/03-reconnaissance|Reconnaissance]] — OSINT from the offensive side
