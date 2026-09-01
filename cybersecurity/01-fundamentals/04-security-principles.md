# Security Design Principles

**[Beginner → Intermediate]** — the handful of timeless principles every security decision comes back to, so you're reasoning from ideas rather than memorising a checklist.

## The kid version first

The rest of this course is *techniques* — how to hash a password, spot an injection, harden a server. Underneath them all sits a small set of **principles** — ways of thinking that were true forty years ago and will be true forty years from now, whatever the technology. Learn these and you can reason about a security question you've never seen before, instead of hunting for the specific rule.

Most of these come from Saltzer and Schroeder's 1975 paper — that's how durable they are.

## Defense in depth

**Never rely on a single control; layer them, so one failure isn't a breach.**

A castle doesn't have one wall — it has a moat, an outer wall, an inner wall, and guards. Security is the same: a firewall *and* input validation *and* least-privilege access *and* monitoring, so that when (not if) one fails, the others still stand.

**Why it's the master principle:** every control eventually fails — a patch is missed, a config drifts, a zero-day lands. Layering means a single failure is contained rather than catastrophic. When you see "the WAF will catch it" or "the firewall protects us," that's *reliance on one layer* — the anti-pattern this principle exists to prevent → [[cybersecurity/07-security-operations/01-defensive-architecture|defensive architecture]].

## Least privilege

**Grant every user, process, and system the minimum access it needs to do its job — and nothing more.**

The single most repeated principle in this vault, because it's the one that caps the damage of everything else. A compromised account, process, or key can do exactly what it was permitted to do → [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|cloud IAM]], [[cybersecurity/12-active-directory/06-defending-active-directory|AD tiering]]. Over-permissioning is how a small compromise becomes a total one.

**The related idea — need to know:** access to information, not just systems, on the same minimal basis.

## Fail securely (fail-safe defaults)

**When something breaks, it should break *closed* (deny), not *open* (allow).**

```python
try:
    authorized = check_permission(user, resource)
except Exception:
    authorized = False        # ← fail CLOSED. An error denies access, never grants it
```

An error in an auth check should deny access, not accidentally grant it. A firewall that crashes should block traffic, not pass it. **Default to deny; allow only what's explicitly permitted** — an allowlist, not a blocklist, because you can enumerate what's safe far more reliably than what's dangerous. This recurs everywhere: [[cybersecurity/14-api-security/03-authorization-and-bola|API authorization]], [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|input validation]], firewall rules.

## Minimise the attack surface

**Every feature, port, service, and line of code is something that can be attacked. The most secure component is the one that isn't there.**

Turn off unused services, close unused ports, remove unused code and dependencies, don't collect data you don't need. **A smaller surface is a smaller target** — it's why minimal container images ([[cybersecurity/09-cloud-security/04-container-and-kubernetes-security|distroless]]) and data minimisation ([[cybersecurity/10-protecting-yourself/07-your-privacy-footprint|don't collect it]]) are security wins, not just tidiness.

## Zero trust — "never trust, always verify"

**Don't trust something just because of where it is** (inside the network, behind the firewall). Verify every request, every time, regardless of origin.

The old model trusted the internal network — once you were inside the perimeter, you were trusted. That collapsed: attackers get inside (phishing, a compromised laptop), and cloud/remote work dissolved the perimeter entirely. **Zero trust treats every request as potentially hostile and authenticates/authorises it explicitly**, which is why [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|identity became the new perimeter]] → [[cybersecurity/07-security-operations/01-defensive-architecture|zero trust]].

## Separation of duties and privilege

**No single person or component should be able to complete a critical action alone.**

Two people to authorise a large payment; the developer who writes code isn't the one who approves its deploy; the person who requests access isn't the one who grants it. **It limits both fraud and the blast radius of one compromised account** — one corrupted party (or one stolen credential) can't do the damage alone. In the cloud this is [[cybersecurity/12-active-directory/06-defending-active-directory|tiering]] and multi-party approval.

## Keep it simple, and don't rely on secrecy

Two principles that pair:

- **Keep it simple (economy of mechanism).** Complexity is where bugs and misconfigurations hide. A simple system you fully understand is more secure than a clever one you don't — which is why [[web3/README|smart contract]] and [[cybersecurity/11-binary-exploitation/README|security-critical]] code is written to be *reviewable*, not impressive
- **No security through obscurity.** Don't rely on attackers *not knowing* how your system works. Assume they have your source code and your design (they often do). **Security must hold even when the design is public** — this is [[cybersecurity/05-cryptography/01-what-is-cryptography|Kerckhoffs's principle]] generalised: a hidden algorithm is not a secure one; a hidden key is. Obscurity can be a *thin extra layer* (defence in depth), never the foundation

## Complete mediation

**Check authorisation on *every* access, not just the first.**

Don't verify once and cache "they're allowed" forever — re-check, because permissions change and a cached "yes" outlives the reason it was granted. It's why [[cybersecurity/14-api-security/03-authorization-and-bola|every API request re-checks ownership]] and why a session that was valid an hour ago must still be validated now.

## How to actually use these

These aren't trivia — they're a **reasoning tool**. Faced with any security decision:

- *Am I relying on one control?* → defence in depth
- *Does this have more access than it needs?* → least privilege
- *What happens when this fails?* → fail securely
- *Do I need this feature/data/port at all?* → minimise the surface
- *Am I trusting this because of where it came from?* → zero trust
- *Am I hoping they won't figure it out?* → no security through obscurity

**When a specific rule isn't obvious, derive it from these.** That's the difference between someone who memorised the OWASP Top 10 and someone who understands security.

## Key insight

**A small set of durable principles — defence in depth, least privilege, fail securely, minimise the surface, zero trust, separation of duties, simplicity, no security-through-obscurity — underlies every specific technique in this course, and they've been true since 1975.** They're a reasoning tool, not a checklist: when you meet a security question you've never seen, you derive the answer from these rather than looking it up. Least privilege and defence in depth are the two that recur most, because between them they ensure a single failure is both *limited* and *contained*.

## Related
- [[cybersecurity/01-fundamentals/05-threat-modeling|threat modelling]] — deciding which principles to apply where
- [[cybersecurity/07-security-operations/01-defensive-architecture|defensive architecture]] — these principles in operational practice
- [[cybersecurity/01-fundamentals/02-cia-triad|the CIA triad]] — what the principles ultimately protect
- [[cybersecurity/05-cryptography/01-what-is-cryptography|Kerckhoffs's principle]] — no security through obscurity, in crypto

*Source: [reference] — Saltzer & Schroeder (1975) and modern practice. Aug 2026.*
