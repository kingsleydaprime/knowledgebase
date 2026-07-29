# The CIA Triad

Confidentiality, Integrity, and Availability — the three properties almost every security control is ultimately trying to protect. Any time you're evaluating whether something is a "security issue," asking "which of these three does this threaten?" is a fast way to clarify what's actually at stake.

## Confidentiality — only the right people can see it

Information is only accessible to those authorized to see it. Threatened by: eavesdropping, stolen credentials, misconfigured access controls, unencrypted data in transit or at rest.

Primary controls: encryption, access control (authentication + authorization), the principle of least privilege (give every user/system only the access it actually needs, nothing more).

## Integrity — the data is accurate and unaltered

Information is trustworthy — it hasn't been tampered with, whether maliciously or by accident. Threatened by: unauthorized modification, man-in-the-middle tampering, malware corrupting files, even honest software bugs that silently corrupt data.

Primary controls: hashing (detecting whether data has changed — see the note on hashing in [[07-exploitation-concepts|exploitation-concepts]] for how this is attacked when done badly, e.g. weak password hashing), digital signatures, checksums, version control and audit logs.

## Availability — the system works when it's needed

Authorized users can access information and systems when they need to. Threatened by: denial-of-service attacks, hardware failure, natural disasters, ransomware that locks legitimate users out of their own data.

Primary controls: redundancy, backups, capacity planning, DDoS mitigation.

## Why the three properties trade off against each other

Maximizing one can directly cost another. Extremely strict access controls (strong confidentiality) can slow down or block legitimate access during an emergency (hurting availability). Extensive audit logging (supporting integrity/accountability) can itself become a confidentiality liability if the logs contain sensitive data and aren't properly protected. Good security design is a balancing act across all three based on what actually matters most for a given system, not maximizing each independently.

## Applying the triad to prioritize a finding

When evaluating a vulnerability (see [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]] for how this shows up in a real engagement), naming which CIA property is impacted — and how severely — is the first step toward assessing real-world risk: a bug that exposes a public marketing page's cache is a very different finding from one that exposes customer payment data, even if both are technically "confidentiality" issues.

## Gotchas

- Not every security issue hits all three properties — a well-scoped denial-of-service vulnerability might threaten only availability, and treating it as if it also implies data exposure overstates the actual risk (or understates it, if it's dismissed as "just availability" when the availability of that particular system is critical).
- Availability is the property most often underweighted by people newer to security, since confidentiality ("don't leak data") gets most of the popular attention — but for many real businesses, an availability failure (a critical system going down) is the most expensive kind of incident.

## Related
- [[01-what-is-cybersecurity|what-is-cybersecurity]]
- [[03-attacker-and-hacker-types|attacker-and-hacker-types]]
