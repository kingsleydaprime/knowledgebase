# What is Cybersecurity

Cybersecurity is the practice of protecting systems, networks, and data from unauthorized access, disruption, or damage. That's a broad definition on purpose — the field spans everything from how a single password is stored to how a nation defends critical infrastructure, and most confusion about "what cybersecurity actually is" comes from only having seen one narrow slice of it.

## The two sides of the same coin

- **Defensive security (blue team)** — building and operating systems so they resist attack: secure configuration, monitoring, incident response, patching, access control. Most cybersecurity work, by volume, is this.
- **Offensive security (red team / ethical hacking)** — deliberately trying to break into systems, under authorization, to find weaknesses before someone without authorization does. This is what [[cybersecurity/02-ethical-hacking/README|ethical-hacking]] covers in depth.

Neither side is complete without the other — offensive testing is how defenses actually get validated rather than just assumed to work, and defensive controls are what offensive findings ultimately feed back into.

## The major domains

- **Network security** — protecting data as it moves between systems (firewalls, VPNs, network segmentation, intrusion detection).
- **Application/web security** — securing the software itself (input validation, authentication, secure coding practices — see the OWASP Top 10 mentioned in [[07-exploitation-concepts|exploitation-concepts]]).
- **Endpoint security** — protecting individual devices (antivirus/EDR, patching, device hardening).
- **Identity and access management (IAM)** — controlling who can access what (authentication, authorization, least privilege).
- **Cryptography** — the mathematical foundation for confidentiality and integrity (encryption, hashing, digital signatures) underlying most of the above.
- **Governance, risk, and compliance (GRC)** — policy, regulatory requirements, and risk management — the less technical, still essential side of the field.

This vault currently goes deep on [[cybersecurity/02-ethical-hacking/README|ethical-hacking]] specifically; the other domains are real gaps to fill in later, not omissions that mean they don't matter.

## Why "there's no such thing as a fully secure system"

Security is fundamentally about **raising the cost of an attack** above what an attacker is willing to pay, not achieving an absolute, permanent guarantee — new vulnerabilities get discovered, software changes introduce new bugs, and human error is a constant. This is why security is treated as an ongoing practice (patching, monitoring, testing) rather than a one-time project that gets "finished."

## Risk — the vocabulary for prioritizing what to fix

Not every vulnerability deserves the same urgency. Risk is typically thought of as roughly `likelihood × impact` — a severe vulnerability that's extremely hard to exploit may warrant less urgent attention than a moderate one that's trivially exploitable and exposed to the entire internet. This framing (also covered practically in [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]]) is why a security report ranks findings by severity rather than just listing them.

## Gotchas

- "Cybersecurity" and "ethical hacking" are often used interchangeably in casual conversation, but ethical hacking is one specific practice (offensive testing) within the much larger field — worth being precise about which you mean, since the skills and mindset differ substantially from defensive roles.
- Security is a property of an entire system, not any single control — a strong password policy doesn't help if the underlying application has an injection vulnerability; defense typically requires layering multiple controls ("defense in depth") rather than relying on one.

## Related
- [[02-cia-triad|cia-triad]]
- [[03-attacker-and-hacker-types|attacker-and-hacker-types]]
- [[cybersecurity/02-ethical-hacking/README|ethical-hacking]]
