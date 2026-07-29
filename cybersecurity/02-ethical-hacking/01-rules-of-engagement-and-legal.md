# Rules of Engagement & Legal Considerations

This is the note that actually separates "ethical hacking" from "a crime" — the exact same technical action (scanning a network, exploiting a vulnerability) is either a legitimate, valuable professional service or a serious offense, depending entirely on whether it was properly authorized beforehand. Every other note in this folder assumes this step already happened.

## Why authorization is the whole ballgame

Unauthorized access to a computer system is illegal in essentially every jurisdiction, regardless of intent — a security researcher who finds and "just checks" a vulnerability without permission, even with no malicious intent and even if they report it afterward, can still be committing a crime (this is exactly the [[03-attacker-and-hacker-types|grey-hat]] situation). Ethical hacking is defined by explicit, documented, informed authorization from someone with the legal authority to grant it — not by the tester's intentions alone.

## The Rules of Engagement (RoE) document

A formal, written agreement signed before any technical work begins, typically specifying:

- **Scope** — exactly which systems, networks, IP ranges, or applications are in bounds, and explicitly what is out of bounds. Anything outside the written scope is not authorized, even if discovered accidentally during testing, and needs to be reported to the client rather than tested further.
- **Timeframe** — the exact window during which testing is authorized to occur.
- **Permitted techniques** — whether social engineering, denial-of-service testing, or physical security testing are included, since these carry different risk profiles from purely technical testing and are often excluded or separately negotiated.
- **Rules around data handling** — what happens if genuinely sensitive data (real customer records, for instance) is encountered during testing; usually specifies minimal access/exfiltration, just enough to prove impact.
- **Emergency contacts and stop conditions** — who to contact and what to do if testing causes unexpected disruption, and predefined conditions under which testing should immediately halt.
- **Authorization / "get out of jail" letter** — a signed statement from someone with legal authority over the target systems, explicitly authorizing the specific testing described, which the tester can produce if their activity is detected and questioned (by the target's own security team, or even law enforcement) during the engagement.

## Relevant legal frameworks (know these exist, not exhaustively)

- **Computer Fraud and Abuse Act (CFAA)** — the primary US federal law criminalizing unauthorized computer access; broadly written and has been applied in ways that make "clearly authorized, clearly scoped" work especially important as a defense.
- **GDPR and similar data protection regulations** — relevant whenever testing might touch personal data, since handling (even briefly accessing) such data during a test can itself carry regulatory obligations.
- Equivalent computer misuse laws exist in most countries (e.g. the UK's Computer Misuse Act) — the specifics vary, but "authorization is the deciding factor" holds broadly across jurisdictions.

This is a map of what exists, not legal advice — a real engagement should involve an actual legal/contractual review appropriate to the jurisdictions involved, not just familiarity with these names.

## Scope creep — the practical daily risk

The most common real-world way testers get into trouble isn't ignoring authorization outright — it's **scope creep**: following an interesting lead into a system, subdomain, or account that turns out to be outside the agreed scope, without realizing it in the moment. This is exactly why [[03-reconnaissance|reconnaissance]] results should be checked against scope continuously, not just once at the start, and why "we found something interesting outside scope" should be reported to the client for a scope amendment rather than pursued unilaterally.

## Practicing legally without a client engagement

Learning and practicing these skills doesn't require live targets — dedicated legal platforms exist specifically for this: **CTF (Capture The Flag) competitions**, and intentionally vulnerable practice platforms (HackTheBox, TryHackMe, and similar) that provide systems built specifically to be legally tested. This is the appropriate way to build and practice the skills covered in [[06-scanning-and-enumeration|scanning-and-enumeration]] and [[07-exploitation-concepts|exploitation-concepts]] without needing a client relationship or any authorization paperwork at all — authorization is built into using the platform.

## Gotchas

- Verbal authorization ("yeah go ahead") is not a substitute for a signed, written RoE — if something goes wrong, a verbal agreement is far harder to rely on, for the tester and the organization both.
- Authorization from the wrong person (a department head who doesn't actually have authority over the specific systems in scope) doesn't count as valid authorization — RoE should be signed by someone with genuine authority over the systems being tested.
- Finding a critical vulnerability outside the agreed scope during an engagement is common — the correct response is documenting it and notifying the client to discuss a scope amendment, not testing further on the spot.

## Related
- [[02-penetration-testing-methodology|penetration-testing-methodology]]
- [[03-attacker-and-hacker-types|attacker-and-hacker-types]]
