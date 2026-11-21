---
id: 0e1ef6eb-a4cf-42d3-a5ec-2924bad7abb7
---

# What is Cybersecurity

Cybersecurity is the practice of protecting systems, networks, and data from unauthorized access, disruption, or damage. That's a broad definition on purpose — the field spans everything from how a single password is stored to how a nation defends critical infrastructure, and most confusion about "what cybersecurity actually is" comes from only having seen one narrow slice of it.

## The two sides of the same coin
<!-- bite: fd723218-f1b2-47b1-8c8b-3705f8ee8fb2 -->

- **Defensive security (blue team)** — building and operating systems so they resist attack: secure configuration, monitoring, incident response, patching, access control. Most cybersecurity work, by volume, is this.
- **Offensive security (red team / ethical hacking)** — deliberately trying to break into systems, under authorization, to find weaknesses before someone without authorization does. This is what [[cybersecurity/02-ethical-hacking/index|ethical-hacking]] covers in depth.

Neither side is complete without the other — offensive testing is how defenses actually get validated rather than just assumed to work, and defensive controls are what offensive findings ultimately feed back into.

## The major domains
<!-- bite: d071fa4d-0941-4aa8-9a0f-1f059002c219 -->

- **Network security** — protecting data as it moves between systems (firewalls, VPNs, network segmentation, intrusion detection).
- **Application/web security** — securing the software itself (input validation, authentication, secure coding practices — see the OWASP Top 10 mentioned in [[07-exploitation-concepts|exploitation-concepts]]).
- **Endpoint security** — protecting individual devices (antivirus/EDR, patching, device hardening).
- **Identity and access management (IAM)** — controlling who can access what (authentication, authorization, least privilege).
- **Cryptography** — the mathematical foundation for confidentiality and integrity (encryption, hashing, digital signatures) underlying most of the above.
- **Governance, risk, and compliance (GRC)** — policy, regulatory requirements, and risk management — the less technical, still essential side of the field.

This vault currently goes deep on [[cybersecurity/02-ethical-hacking/index|ethical-hacking]] specifically; the other domains are real gaps to fill in later, not omissions that mean they don't matter.

## Why "there's no such thing as a fully secure system"
<!-- bite: ac8216e6-fd9a-4ef9-8612-29f6a7f769a2 -->

Security is fundamentally about **raising the cost of an attack** above what an attacker is willing to pay, not achieving an absolute, permanent guarantee — new vulnerabilities get discovered, software changes introduce new bugs, and human error is a constant. This is why security is treated as an ongoing practice (patching, monitoring, testing) rather than a one-time project that gets "finished."

## Risk — the vocabulary for prioritizing what to fix
<!-- bite: c37a4e2b-a7fa-4339-8c74-cb6fe15c3238 -->

Not every vulnerability deserves the same urgency. Risk is typically thought of as roughly `likelihood × impact` — a severe vulnerability that's extremely hard to exploit may warrant less urgent attention than a moderate one that's trivially exploitable and exposed to the entire internet. This framing (also covered practically in [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]]) is why a security report ranks findings by severity rather than just listing them.

## Gotchas
<!-- bite: 7c9f898b-6ce7-4fb4-bbb8-35af1abff548 -->

- "Cybersecurity" and "ethical hacking" are often used interchangeably in casual conversation, but ethical hacking is one specific practice (offensive testing) within the much larger field — worth being precise about which you mean, since the skills and mindset differ substantially from defensive roles.
- Security is a property of an entire system, not any single control — a strong password policy doesn't help if the underlying application has an injection vulnerability; defense typically requires layering multiple controls ("defense in depth") rather than relying on one.

## Related
<!-- bite: 550d061e-1ce3-4aa1-9694-63c2769ff037 -->
- [[02-cia-triad|cia-triad]]
- [[03-attacker-and-hacker-types|attacker-and-hacker-types]]
- [[cybersecurity/02-ethical-hacking/index|ethical-hacking]]
