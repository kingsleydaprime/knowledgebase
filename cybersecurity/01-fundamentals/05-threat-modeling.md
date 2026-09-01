# Threat Modelling

**[Intermediate]** — the planning tool that turns "be secure" into a concrete list of what to defend against, so you spend effort where the real danger is.

## The kid version first

You can't defend against *everything* — you have finite time and money. So before building defences, you ask four questions: **What are we building? What can go wrong? What are we going to do about it? Did we do a good job?** Answering them, deliberately, is threat modelling — and it's what stops you from armour-plating the front door while leaving the back window open.

It's the bridge from the [[cybersecurity/01-fundamentals/03-attacker-and-hacker-types|"who would attack us"]] taxonomy to an actual plan.

## Why it matters

Without threat modelling, security is guesswork — you defend against whatever you happened to read about last, which is rarely your real risk. **A small business armour-plating against nation-state APTs while skipping basic patching is the classic failure**, and it comes from never asking "who would actually target *us*, and how?" → [[cybersecurity/01-fundamentals/03-attacker-and-hacker-types|attacker types]].

Threat modelling makes the danger *specific*, so the defences can be too. It's also cheapest done **early, at design time** — a threat found on a whiteboard costs a conversation; the same one found in production costs an incident.

## The four questions (Shostack's framework)

The whole discipline, and you can run it on a napkin:

**1. What are we building / working on?**
Draw the system. Data flow diagrams are the classic tool: components, data stores, the flows between them, and — critically — the **trust boundaries** (where data crosses from less-trusted to more-trusted, e.g. the internet → your API, or a user's browser → your server). **Attacks happen at trust boundaries**, so drawing them is half the work → [[architecture/README|system design]].

**2. What can go wrong?**
Enumerate the threats. This is where structured methods help you be thorough rather than relying on imagination:

**STRIDE** — the most common checklist, one threat category per letter, mapped to what each violates:

| | Threat | Violates | Example |
|---|---|---|---|
| **S** | **Spoofing** | Authentication | Pretending to be someone else |
| **T** | **Tampering** | Integrity | Modifying data in transit or at rest |
| **R** | **Repudiation** | Non-repudiation | Denying you did something (no audit trail) |
| **I** | **Information disclosure** | Confidentiality | Leaking data |
| **D** | **Denial of service** | Availability | Making it unavailable |
| **E** | **Elevation of privilege** | Authorization | Gaining more access than allowed |

**Run STRIDE against each element and each trust boundary** — "can this flow be spoofed? tampered? …" — and you systematically surface threats instead of hoping you thought of them. Notice STRIDE maps directly onto the [[cybersecurity/01-fundamentals/02-cia-triad|CIA triad]] plus authentication, authorization, and non-repudiation.

**Attack trees** are the other tool: put the attacker's goal at the root ("steal customer data"), branch into the ways to achieve it, and recurse. Good for reasoning about a specific high-value target.

**3. What are we going to do about it?**
For each threat, choose a response — the same four options as [[cybersecurity/08-governance-risk-and-compliance/01-risk-and-frameworks|risk treatment]]:
- **Mitigate** — add a control (the usual choice; apply the [[cybersecurity/01-fundamentals/04-security-principles|security principles]])
- **Eliminate** — remove the feature/data that creates the threat (minimise the attack surface)
- **Transfer** — shift it (insurance, a third party)
- **Accept** — document it and live with it, when the fix costs more than the risk

**4. Did we do a good job?**
Review the model, validate the mitigations actually work (this is what [[cybersecurity/02-ethical-hacking/README|penetration testing]] checks), and revisit as the system changes. **A threat model is a living document, not a one-time gate** — new features add new threats.

## Prioritise, because you still can't do everything

Threat modelling produces a *list*, and the list is longer than your budget. Rank it by **risk = likelihood × impact** → [[cybersecurity/08-governance-risk-and-compliance/01-risk-and-frameworks|risk]]:

- A trivially-exploitable, internet-facing threat to critical data → fix now
- A hard-to-exploit threat to a low-value asset → accept or defer

This is the same likelihood × impact framing as risk management — threat modelling is where it gets applied to concrete, enumerated threats rather than vague worries → [[cybersecurity/01-fundamentals/01-what-is-cybersecurity|risk]].

## Keeping it practical

Threat modelling has a reputation for being heavyweight (formal diagrams, hours of meetings), and that reputation kills its adoption. The antidote:

- **Do it lightly and often.** A 30-minute whiteboard session on a new feature beats a 40-page document once a year
- **Ask the four questions** even informally — just asking "what can go wrong here, and what would we do?" on every design catches most of the value
- **Focus on trust boundaries** — that's where the threats concentrate
- **Write down what you *accept*** — an explicitly accepted risk is a decision; an unnoticed one is a surprise

**The lightweight version — four questions on a whiteboard — is the one that actually gets done, which makes it the one that matters.**

## Key insight

**Threat modelling turns "be secure" into an enumerated, prioritised list of what to defend against, by asking four questions — what are we building, what can go wrong, what do we do about it, did we do a good job — structured by STRIDE and focused on trust boundaries where attacks concentrate.** It's the bridge from the attacker taxonomy to an actual plan, cheapest done early on a whiteboard, and its whole value is making the danger *specific* so effort lands where the real risk is rather than on whatever you last read about. Done lightly and often, it's the single highest-leverage planning habit in security.

## Related
- [[cybersecurity/01-fundamentals/03-attacker-and-hacker-types|attacker types]] — the "who" that threat modelling makes concrete
- [[cybersecurity/01-fundamentals/04-security-principles|security principles]] — the mitigations you apply
- [[cybersecurity/08-governance-risk-and-compliance/01-risk-and-frameworks|risk and frameworks]] — prioritising the resulting list
- [[cybersecurity/02-ethical-hacking/02-penetration-testing-methodology|penetration testing]] — validating the model holds

*Source: [reference] — Shostack's four-question frame, STRIDE. Aug 2026.*
