---
id: 0bf33fe3-275c-4484-82fe-e63a938690d5
---

# The CIA Triad

Confidentiality, Integrity, and Availability — the three properties almost every security control is ultimately trying to protect. Any time you're evaluating whether something is a "security issue," asking "which of these three does this threaten?" is a fast way to clarify what's actually at stake.

## Confidentiality — only the right people can see it
<!-- bite: 26808a24-09cf-42af-a6dc-00ad9b9c5832 -->

Information is only accessible to those authorized to see it. Threatened by: eavesdropping, stolen credentials, misconfigured access controls, unencrypted data in transit or at rest.

Primary controls: encryption, access control (authentication + authorization), the principle of least privilege (give every user/system only the access it actually needs, nothing more).

## Integrity — the data is accurate and unaltered
<!-- bite: 81368ccd-f26f-4937-922d-5fd4cb02ccf3 -->

Information is trustworthy — it hasn't been tampered with, whether maliciously or by accident. Threatened by: unauthorized modification, man-in-the-middle tampering, malware corrupting files, even honest software bugs that silently corrupt data.

Primary controls: hashing (detecting whether data has changed — see the note on hashing in [[07-exploitation-concepts|exploitation-concepts]] for how this is attacked when done badly, e.g. weak password hashing), digital signatures, checksums, version control and audit logs.

## Availability — the system works when it's needed
<!-- bite: 54941d66-6ec8-49f7-b03c-fc810530cf2f -->

Authorized users can access information and systems when they need to. Threatened by: denial-of-service attacks, hardware failure, natural disasters, ransomware that locks legitimate users out of their own data.

Primary controls: redundancy, backups, capacity planning, DDoS mitigation.

## Why the three properties trade off against each other
<!-- bite: 27e5cea0-5cac-400d-ba89-0f05795a264e -->

Maximizing one can directly cost another. Extremely strict access controls (strong confidentiality) can slow down or block legitimate access during an emergency (hurting availability). Extensive audit logging (supporting integrity/accountability) can itself become a confidentiality liability if the logs contain sensitive data and aren't properly protected. Good security design is a balancing act across all three based on what actually matters most for a given system, not maximizing each independently.

## Applying the triad to prioritize a finding
<!-- bite: 178778d1-f81d-4d49-b677-694ec315c315 -->

When evaluating a vulnerability (see [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]] for how this shows up in a real engagement), naming which CIA property is impacted — and how severely — is the first step toward assessing real-world risk: a bug that exposes a public marketing page's cache is a very different finding from one that exposes customer payment data, even if both are technically "confidentiality" issues.

## Gotchas
<!-- bite: e2a807d1-5042-4540-96c2-6eaae1bff738 -->

- Not every security issue hits all three properties — a well-scoped denial-of-service vulnerability might threaten only availability, and treating it as if it also implies data exposure overstates the actual risk (or understates it, if it's dismissed as "just availability" when the availability of that particular system is critical).
- Availability is the property most often underweighted by people newer to security, since confidentiality ("don't leak data") gets most of the popular attention — but for many real businesses, an availability failure (a critical system going down) is the most expensive kind of incident.

## Related
<!-- bite: 3e6ce03f-210f-4403-a3d7-5f55a5c01554 -->
- [[01-what-is-cybersecurity|what-is-cybersecurity]]
- [[03-attacker-and-hacker-types|attacker-and-hacker-types]]
