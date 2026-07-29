# Cybersecurity

A map of this folder. Covers the fundamentals, a deep pass on ethical hacking, the two major defensive domains (network security, web security), and the cryptographic foundation underneath all of them.

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

## Related
- [[ai-ml/README|ai-ml curriculum map]] — same "orientation → deep dive → practice" shape
- [[foundations/dsa/README|DSA fundamentals]]
