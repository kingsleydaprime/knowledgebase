# Penetration Testing Methodology

Ethical hacking isn't improvisation — it follows a structured methodology so findings are thorough, repeatable, and defensible afterward (both technically and legally). The classic phases, echoed across most formal frameworks (PTES, OSSTMM, NIST SP 800-115):

## The phases

```
1. Rules of Engagement / Authorization  ->  before anything else happens at all
2. Reconnaissance                       ->  gather information about the target
3. Scanning & Enumeration               ->  map what's actually reachable and running
4. Exploitation                         ->  attempt to leverage a weakness to gain access
5. Post-Exploitation                    ->  determine actual impact (privilege escalation, lateral movement, data access)
6. Reporting                            ->  document findings, severity, and remediation — the actual deliverable
```

Each phase is its own note in this folder: [[03-reconnaissance|reconnaissance]], [[06-scanning-and-enumeration|scanning-and-enumeration]], [[07-exploitation-concepts|exploitation-concepts]], [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]] — and [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]] for the authorization step that has to happen before phase 2 even begins.

## Why order matters

Each phase's output feeds the next: reconnaissance identifies what to scan, scanning identifies what's plausibly exploitable, exploitation (if successful) opens up post-exploitation, and everything gets synthesized into the report. Skipping straight to exploitation without proper reconnaissance/scanning means testing blind — more likely to miss things, more likely to cause unintended disruption on a live system, and harder to explain afterward why a particular attempt was made at all.

## Types of engagement

- **Black-box** — the tester starts with no inside knowledge of the target, simulating a genuine external attacker's starting position. Most realistic in terms of what an actual attacker faces, but slower and can miss internal-only weaknesses.
- **White-box** — the tester is given full information up front (source code, architecture diagrams, credentials) — more thorough and efficient, common for application security reviews where the goal is finding as many issues as possible rather than simulating a realistic attacker.
- **Grey-box** — partial information given (e.g. a standard user account, but no source code) — a common, practical middle ground reflecting what a malicious insider or a successfully phished attacker would actually have.

## Red team vs. penetration test — a scope distinction

A **penetration test** typically has a defined scope and timeframe, aiming to find as many vulnerabilities as reasonably possible within it. A **red team engagement** is usually more narrowly goal-oriented ("can you reach this specific system/data without being detected") and often explicitly tests the defensive (blue) team's detection and response capability, not just whether a vulnerability exists. Confusing the two leads to mismatched expectations about what a report should contain — a red team report is as much about detection gaps as it is about the specific vulnerabilities used to get in.

## Gotchas

- Every phase past reconnaissance assumes [[01-rules-of-engagement-and-legal|explicit written authorization]] is already in place — without it, identical technical actions are illegal, regardless of intent.
- A methodology is a checklist for thoroughness, not a rigid script — real engagements loop back (a post-exploitation finding often triggers renewed reconnaissance/scanning against a newly discovered internal system) rather than executing the six phases strictly once, in order.

## Related
- [[03-reconnaissance|reconnaissance]]
- [[06-scanning-and-enumeration|scanning-and-enumeration]]
- [[07-exploitation-concepts|exploitation-concepts]]
- [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]]
- [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]]
