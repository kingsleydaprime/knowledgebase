# Security Operations

**This section is the defender's side of the course: how a blue team builds a system to be defensible, hears an attack in the logs, hunts for the attacker who slipped past, responds when one is confirmed, and reconstructs afterwards what happened.**

The earlier sections showed what attackers do ([[cybersecurity/06-attacks-and-threats/index|attacks and threats]]) and how to test for weaknesses ([[cybersecurity/02-ethical-hacking/index|ethical hacking]]). This one is the other chair in the room — the Security Operations Centre (SOC) and the incident responders who catch and stop them. It runs as one loop: architect it well, detect, hunt, respond, investigate. Everything is hands-on against targets you own: your own machine, your lab VPS, your lab's logs, and a harmless test file.

## What you'll be able to do

By the end of this section you will be able to:

- harden a machine and measure the before-and-after, and explain defence in depth and zero trust;
- write a real detection rule three ways and tune it so it survives contact with reality;
- map an attack to MITRE ATT&CK and run a hypothesis-driven hunt that ends in a new rule;
- write and rehearse an incident-response runbook, and do a safe static analysis of a malware test file.

## Reading order

1. [[cybersecurity/07-security-operations/01-defensive-architecture|01 — Defensive Architecture]] — **[Intermediate]** — defence in depth, zero trust, hardening and the blue/red/purple teams, with an audit-and-harden lab using `ss` and `lynis`.
2. [[cybersecurity/07-security-operations/02-logging-siem-and-detection|02 — Logging, SIEM and Detection]] — **[Intermediate → Advanced]** — log sources, what a SIEM adds, and writing an SSH-spray detection as a one-liner, an SPL query and a portable Sigma rule.
3. [[cybersecurity/07-security-operations/03-threat-intelligence-and-hunting|03 — Threat Intelligence and Hunting]] — **[Advanced]** — IOCs vs TTPs, the kill chain, MITRE ATT&CK and the diamond model, and mapping your own attacks to ATT&CK then hunting for them.
4. [[cybersecurity/07-security-operations/04-incident-response|04 — Incident Response]] — **[Advanced]** — the six-phase PICERL lifecycle, runbooks and SOAR, with a runbook written and rehearsed for a compromised SSH account.
5. [[cybersecurity/07-security-operations/05-forensics-and-malware-analysis|05 — Forensics and Malware Analysis]] — **[Advanced]** — order of volatility, evidence handling, and a safe static analysis of the EICAR test file.

## Related

- [[cybersecurity/index|The cybersecurity course]] — the whole map.
- [[cybersecurity/06-attacks-and-threats/index|Attacks and threats]] — what this section detects and responds to.
- [[cybersecurity/03-network-security/04-intrusion-detection-and-prevention|IDS/IPS (network security)]] — the network-layer detection this builds on.
- [[devops/07-observability/index|Observability (DevOps)]] — the same logging and monitoring foundation, from the reliability angle.

## About this section

**How it's built:** five lessons as one blue-team loop — architect, detect, hunt, respond, investigate — each with a hands-on element against owned targets: a hardening audit, a detection rule, an ATT&CK mapping and hunt, an incident runbook, and static malware analysis. Every control links to the attack it defends against earlier in the course. Rebuilt to the [[COURSE-STANDARD|course standard]]: all five lessons converted. Live runs are tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
