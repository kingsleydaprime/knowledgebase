# Attacker & Hacker Types

"Hacker" alone says nothing about intent — the word describes a skill (deep, creative technical ability to make systems do things they weren't obviously designed to do), not a moral position. The color-coded "hat" system is the field's shorthand for separating intent and authorization, which matters far more than raw skill when talking about what someone actually does.

## The hat spectrum

- **White hat** — hacks with explicit authorization, for defensive purposes: penetration testers, bug bounty hunters, security researchers reporting through responsible disclosure. This is what [[cybersecurity/02-ethical-hacking/README|ethical hacking]] refers to, and the entire rest of that folder assumes this context.
- **Black hat** — hacks without authorization, for malicious purposes: theft, extortion (ransomware), sabotage, espionage. Everything covered in this vault's ethical-hacking notes is framed against black-hat techniques specifically so they can be defended against, never framed as instructions to carry them out without authorization.
- **Grey hat** — somewhere in between: accessing or testing a system without explicit authorization, but without malicious intent (e.g. finding and reporting a vulnerability without having been asked to look) — technically often illegal despite good intentions, which is exactly why authorization (covered in [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]]) is the single factor separating "white hat" from "grey hat," not skill or motive.

## Attacker categories, by motive and resources

- **Script kiddies** — low skill, using existing tools/exploits built by others, often for notoriety or low-stakes disruption rather than a sophisticated goal.
- **Hacktivists** — motivated by political or social causes; targets and methods driven by ideology rather than direct financial gain.
- **Cybercriminals** — financially motivated: ransomware operators, credential thieves, fraud rings. The most common category by sheer incident volume.
- **Insider threats** — someone with legitimate access (an employee, contractor) misusing it, maliciously or through negligence. Often overlooked relative to external attackers despite being a major real-world source of breaches, precisely because existing access bypasses many external-facing defenses entirely.
- **Advanced Persistent Threats (APTs)** — well-resourced, often nation-state-linked groups pursuing long-term, stealthy objectives (espionage, strategic disruption) rather than quick, opportunistic wins. Characterized by patience, custom tooling, and a willingness to stay undetected for months or years.

## Why this taxonomy matters practically

Defensive priorities differ enormously by which attacker category is actually the realistic threat for a given organization — a small business's realistic threat model is mostly opportunistic cybercriminals and possibly insiders, not nation-state APTs, and over-investing in APT-grade defenses while under-investing in basic patching/access control is a common, costly prioritization mistake. Threat modeling (thinking specifically about "who would target us, and why") is what turns this taxonomy from trivia into an actual planning tool.

## Gotchas

- "Hacker" in casual/media use almost always implicitly means black hat — worth being precise in professional contexts, since the term technically describes a skillset, not an intent.
- Assuming external attackers are the primary risk while under-securing against insider threats is a common blind spot — access logging, least privilege, and separation of duties exist specifically to limit the damage a legitimate-but-malicious (or careless) insider can do.

## Related
- [[01-what-is-cybersecurity|what-is-cybersecurity]]
- [[cybersecurity/02-ethical-hacking/README|ethical-hacking]]
