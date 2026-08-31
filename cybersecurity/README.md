# Cybersecurity

A map of this folder. Sections **01–05** are the original course — fundamentals, offensive security (ethical hacking), the network/web defensive domains, and cryptography. Sections **06–09** (added by cross-referencing the [roadmap.sh cyber-security roadmap](https://roadmap.sh/cyber-security)) fill in the rest of the field: a systematic **attacks & threats** taxonomy, the **security-operations / blue-team** half (SIEM, threat hunting, incident response, forensics) that was the biggest gap, **governance/risk/compliance**, and **cloud security**.

## Fundamentals **[Beginner]**
1. [[01-what-is-cybersecurity|what-is-cybersecurity]] — defensive vs offensive security, the major domains, why "fully secure" isn't a real state
2. [[02-cia-triad|cia-triad]] — confidentiality, integrity, availability — the vocabulary nearly every security discussion reduces to
3. [[03-attacker-and-hacker-types|attacker-and-hacker-types]] — white/grey/black hat, script kiddies through APTs, and why insider threats matter

## Ethical Hacking (offensive, in depth) **[Beginner → Advanced]**

[[cybersecurity/02-ethical-hacking/README|ethical-hacking/]] — the full offensive-security methodology: rules of engagement and legal grounding, reconnaissance, scanning/enumeration, exploitation concepts (the major vulnerability classes and why they work), post-exploitation and reporting, the standard tool landscape (with concrete usage examples), Wi-Fi/document security testing on your own devices, lab/OS setup, and the career path to senior level.

## Network Security (defensive) **[Intermediate]**

[[cybersecurity/03-network-security/README|network-security/]] — firewalls, network segmentation (VLANs, DMZs, Zero Trust), VPNs and encryption in transit, intrusion detection/prevention (IDS/IPS, SIEM). The network-layer counterpart to ethical-hacking's offensive framing.

## Web / Application Security (defensive) **[Intermediate]**

[[cybersecurity/04-web-security/README|web-security/]] — secure authentication (password hashing, MFA, sessions), input validation and output encoding (the actual fixes for injection and XSS), HTTPS/TLS, security headers and the same-origin policy (CORS, CSP, clickjacking, CSRF). The defensive counterpart to exploitation-concepts' vulnerability categories.

## Cryptography (the foundation underneath the rest of this folder) **[Intermediate → Advanced]**

[[cybersecurity/05-cryptography/README|cryptography/]] — the four goals (confidentiality, integrity, authentication, non-repudiation), symmetric encryption (AES, modes of operation), asymmetric encryption (RSA, Diffie-Hellman, ECC, hybrid encryption), hashing and HMAC, digital signatures and the PKI chain of trust, and the attacks/best practices (padding oracles, side channels, weak randomness, key management) that account for almost every real-world cryptography failure.

## Attacks & Threats (the threat catalog) **[Beginner → Advanced]**

[[cybersecurity/06-attacks-and-threats/README|06-attacks-and-threats/]] — a systematic taxonomy of how attacks work: social engineering, network attacks (MITM, ARP/DNS poisoning, DoS, Wi-Fi), the OWASP Top 10 web attacks, and password/malware/exploitation. The structured "know your enemy" companion to ethical-hacking.

## Security Operations (the defensive / blue-team half) **[Intermediate → Advanced]**

[[cybersecurity/07-security-operations/README|07-security-operations/]] — detecting and responding to attacks, the SOC/DFIR side: defensive architecture (defense-in-depth, zero-trust), logging/SIEM/detection, threat intelligence and hunting, the frameworks (cyber kill chain, MITRE ATT&CK), incident response, and forensics/malware analysis.

## Governance, Risk & Compliance **[Intermediate]**

[[cybersecurity/08-governance-risk-and-compliance/README|08-governance-risk-and-compliance/]] — the management side: risk assessment, the standard frameworks (NIST, ISO 27001, CIS) and compliance regimes, and the certification/career landscape.

## Cloud Security **[Advanced]**

[[cybersecurity/09-cloud-security/README|09-cloud-security/]] — securing cloud workloads: shared responsibility, IAM, the cloud attack surface, and container/Kubernetes/IaC security — cross-linking the DevOps domain for the infrastructure mechanics.

## Related
- [[cybersecurity/projects|Projects]] — **the reps for this domain**, graded 🟢🟡🔴 with a *done when* for each
- [[ai-ml/README|ai-ml curriculum map]] — same "orientation → deep dive → practice" shape
- [[foundations/dsa/README|DSA fundamentals]]
