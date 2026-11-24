# Fundamentals

**The fundamentals are the words and ways of thinking the whole field of cybersecurity runs on: what you protect, from whom, by which principles, and how you decide what to do first.**

Read this section before anything else in the course. It needs no tools and no lab, only one running example: **Mama Put**, a roadside food seller whose customers order on their phones, with a menu, customer accounts, kitchen-staff logins and card payments. Every idea here is tried on her app, so by the end you've done a small but real threat model.

## What you'll be able to do

By the end of this section you will be able to:

- talk about assets, threats, vulnerabilities and risk precisely, and rank risks by likelihood × impact;
- classify any incident by which of confidentiality, integrity and availability it hits;
- name the realistic attackers for an organisation, and say why permission is the line between ethical hacking and crime;
- review a design against the core security principles;
- threat-model a system: draw its data flows and trust boundaries, list threats with STRIDE, and decide what to do about each.

## Reading order

1. [[cybersecurity/01-fundamentals/01-what-is-cybersecurity|01 — What Is Cybersecurity]] — **[Beginner]** — the four words, the two sides, the map of the field, and ranking risks.
2. [[cybersecurity/01-fundamentals/02-cia-triad|02 — The CIA Triad]] — **[Beginner]** — confidentiality, integrity and availability, how they trade off, and classifying incidents.
3. [[cybersecurity/01-fundamentals/03-attacker-and-hacker-types|03 — Attacker and Hacker Types]] — **[Beginner]** — the hats, attackers by motive and resources, and defending against your realistic ones.
4. [[cybersecurity/01-fundamentals/04-security-principles|04 — Security Design Principles]] — **[Beginner→Intermediate]** — defence in depth, least privilege, fail securely, zero trust and the rest, as review questions.
5. [[cybersecurity/01-fundamentals/05-threat-modeling|05 — Threat Modelling]] — **[Intermediate]** — the four questions, trust boundaries, STRIDE, and ranking what to fix.

## How the five fit together

Lessons 01 to 03 give you the words: what's at risk, what kind of harm, and from whom. Lesson 04 gives you a way to reason about defences from first principles instead of memorising rules. Lesson 05 puts them together into a plan for one real system. Everything technical in the rest of the course applies one of these five.

## Related

- [[cybersecurity/index|The cybersecurity course]] — the whole map.
- [[cybersecurity/02-ethical-hacking/index|Ethical hacking]] — the next section, where you test a system the way an attacker would.
- [[cybersecurity/08-governance-risk-and-compliance/index|Governance, risk and compliance]] — risk at the scale of a whole organisation.
- [[cybersecurity/10-protecting-yourself/index|Protecting yourself]] — the same fundamentals for your own phone and accounts.

## About this section

**How it's built:** five short lessons with no lab, all worked on one running example, Mama Put (the same app the backend framework subjects build). Each lesson's practice task builds toward a threat model of the learner's own app in lesson 05. Rebuilt to the [[COURSE-STANDARD|course standard]]: all five lessons converted.
