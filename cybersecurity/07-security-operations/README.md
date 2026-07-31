# 07 — Security Operations

The **defensive / blue-team** half of security — detecting, investigating, and responding to attacks. This was the biggest gap in the course: the offensive side ([[cybersecurity/02-ethical-hacking/README|ethical hacking]]) and the attack taxonomy ([[cybersecurity/06-attacks-and-threats/README|attacks & threats]]) tell you what adversaries do; this section is how a Security Operations Center (SOC) and incident responders *catch and stop them*. Part of the [[cybersecurity/README|Cybersecurity course]].

## Reading order

1. [[cybersecurity/07-security-operations/01-defensive-architecture|Defensive Architecture]] — **[Intermediate]** — defense-in-depth, zero-trust, blue/red/purple teams, and hardening — how you build to be defensible in the first place
2. [[cybersecurity/07-security-operations/02-logging-siem-and-detection|Logging, SIEM & Detection]] — **[Intermediate → Advanced]** — logs as the raw material, SIEM correlation, IDS/IPS, EDR, and honeypots
3. [[cybersecurity/07-security-operations/03-threat-intelligence-and-hunting|Threat Intelligence & Hunting]] — **[Advanced]** — threat intel & OSINT, IOCs, proactive threat hunting, and the frameworks (cyber kill chain, MITRE ATT&CK, diamond model)
4. [[cybersecurity/07-security-operations/04-incident-response|Incident Response]] — **[Advanced]** — the IR lifecycle (prepare → identify → contain → eradicate → recover → lessons learned), SOAR, and runbooks
5. [[cybersecurity/07-security-operations/05-forensics-and-malware-analysis|Forensics & Malware Analysis]] — **[Advanced]** — digital forensics (memory/disk), evidence handling, and safely analyzing malware in a sandbox

## Related
- [[cybersecurity/06-attacks-and-threats/README|Attacks & Threats]] — what this section detects and responds to
- [[cybersecurity/03-network-security/04-intrusion-detection-and-prevention|IDS/IPS & SIEM (network-security)]] — the network-layer detection this builds on
- [[devops/10-observability/README|Observability (DevOps)]] — the same logging/monitoring foundation, from the ops-reliability angle
