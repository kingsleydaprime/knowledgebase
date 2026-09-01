# Risk & Frameworks

**[reference]** — from the roadmap.sh cyber-security roadmap. The management layer that decides *what* security to do and *why* — because you can't protect everything equally, and "be secure" isn't a plan.

## Security is risk management

Perfect security is impossible and infinite budget doesn't exist, so security is fundamentally about **managing risk** — spending finite resources where they reduce the most danger. Everything technical in this course serves a risk decision.

**Risk = Likelihood × Impact.** A vulnerability that's trivial to exploit and would destroy the business is high risk; one that's near-impossible to exploit or would cause a shrug is low. Related vocabulary:

- **Asset** — what you're protecting (data, systems, reputation).
- **Threat** — what could harm it (an attacker, a disaster).
- **Vulnerability** — a weakness a threat can exploit.
- **Risk** — the potential loss when a threat exploits a vulnerability.

## The risk process

1. **Identify** — what assets, what threats, what vulnerabilities.
2. **Assess** — likelihood × impact for each, to *prioritize* (you'll never fix everything — fix the highest risk first). This drives [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|patch/vulnerability prioritization]] (CVSS scores rank severity).
3. **Treat** — choose a response:
   - **Mitigate** — reduce it (add a control) — the usual choice.
   - **Transfer** — shift it (cyber insurance, outsourcing).
   - **Accept** — live with it (when the cost of fixing exceeds the risk).
   - **Avoid** — don't do the risky thing at all.
4. **Monitor** — risk changes as threats and systems evolve; reassess continually.

The senior-security insight: **you can't secure everything, so knowing what's *worth* securing — and being able to justify it to leadership in business terms — is the actual job** at the top of this field.

## The frameworks

Rather than invent controls from scratch, organizations adopt established frameworks — shared, vetted checklists of what good security looks like:

| Framework | What it is |
|---|---|
| **NIST Cybersecurity Framework (CSF)** | a widely-used, flexible framework organized around five functions: **Identify, Protect, Detect, Respond, Recover** (which map neatly onto this course's sections). The common US reference. |
| **NIST RMF / 800-53** | a detailed risk-management process and control catalog (heavy, common in US government). |
| **ISO/IEC 27001** | the international standard for an Information Security Management System (ISMS); certifiable, common globally for demonstrating security maturity to customers. |
| **CIS Controls / Benchmarks** | a prioritized, prescriptive list of defensive actions (Controls) and concrete [[cybersecurity/07-security-operations/01-defensive-architecture\|hardening]] configs (Benchmarks). The most actionable starting point. |

Frameworks give a common language, avoid reinventing the wheel, and provide something to measure/audit against.

## Compliance

**Compliance** is meeting externally-imposed security obligations — laws, regulations, contracts. It's related to but distinct from security: compliance is the *floor* (the minimum you must do to be legal), not the ceiling (you can be compliant and still insecure). Major regimes:

- **GDPR** — EU data-protection law (consent, breach notification within 72 hours, big fines).
- **PCI-DSS** — mandatory for anyone handling payment-card data.
- **HIPAA** — US healthcare data.
- **SOC 2** — a widely-requested audit report on a service provider's security controls (common in B2B SaaS).

Governance ties it together: **policies** (the rules), **standards** (specific requirements), **procedures** (how-to steps), and the **auditors/roles** that verify adherence. The people side — assigning ownership, training, and accountability — is what makes controls actually happen rather than existing on paper.

## Related
- [[cybersecurity/01-fundamentals/02-cia-triad|CIA Triad]] — the goals risk protects
- [[cybersecurity/07-security-operations/01-defensive-architecture|Defensive Architecture]] — CIS Benchmarks and hardening in practice
- [[cybersecurity/08-governance-risk-and-compliance/02-certifications-and-career|Certifications & Career]] — the credentials that formalize this knowledge
