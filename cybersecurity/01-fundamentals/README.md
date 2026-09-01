# Fundamentals

**The vocabulary and mental models the whole field runs on** — read these before anything else in [[cybersecurity/README|cybersecurity/]]. What the field *is*, the three things every control protects, who's actually attacking, the principles you reason from, and the planning tool that decides where to spend effort.

## Reading order

1. [[cybersecurity/01-fundamentals/01-what-is-cybersecurity|what-is-cybersecurity]] — **[Beginner]** — defensive vs offensive, the major domains, why "fully secure" isn't a real state, and risk as the vocabulary for prioritising
2. [[cybersecurity/01-fundamentals/02-cia-triad|cia-triad]] — **[Beginner]** — confidentiality, integrity, availability: the three properties nearly every security discussion reduces to, and how they trade off
3. [[cybersecurity/01-fundamentals/03-attacker-and-hacker-types|attacker-and-hacker-types]] — **[Beginner]** — white/grey/black hat (authorization, not skill, is the line), script kiddies through APTs, and why insider threats matter
4. [[cybersecurity/01-fundamentals/04-security-principles|security-principles]] — **[Beginner → Intermediate]** — **the durable design principles** (defence in depth, least privilege, fail securely, zero trust, minimise the surface, no security-through-obscurity) — a reasoning tool, not a checklist
5. [[cybersecurity/01-fundamentals/05-threat-modeling|threat-modeling]] — **[Intermediate]** — **the four-question planning tool** (what are we building / what can go wrong / what do we do / did we do well), STRIDE, and trust boundaries. Turns "be secure" into a concrete list

## The through-line

**04 and 05 are the two that turn the vocabulary into judgement.** Notes 01–03 give you the *words*; the principles (04) give you a way to reason about any security question from first principles instead of memorising rules; and threat modelling (05) is how you decide *which* principles to apply *where*, so finite effort lands on the real risk. Everything technical in the rest of the course is an application of these five.

## Related
- [[cybersecurity/README|the cybersecurity course map]]
- [[cybersecurity/07-security-operations/01-defensive-architecture|defensive architecture]] — the principles in operational practice
- [[cybersecurity/08-governance-risk-and-compliance/README|governance, risk & compliance]] — risk and prioritisation at the organisational level
- [[cybersecurity/10-protecting-yourself/README|protecting yourself]] — the same fundamentals for a non-technical reader
