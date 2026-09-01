# Third-Party and Supply-Chain Risk

**[Intermediate → Advanced]** — the risk you inherit from everyone you depend on, why it's become the dominant breach vector, and why it's a governance problem more than a technical one.

## The kid version first

Your organisation's security is no longer just *yours*. You depend on dozens of vendors (your cloud, your SaaS tools, your payment processor), thousands of software libraries, and the tools your suppliers use in turn. **A weakness in any of them can breach *you*** — and you often have no visibility into their security at all. Defending your own perimeter perfectly doesn't help when the attacker walks in through a supplier you trusted.

This is **supply-chain risk**, and it's become one of the most important — and hardest — problems in security, precisely because it's about controlling risk you *don't* directly control.

## Why it became the dominant vector

Two structural shifts made this the risk of the era:

1. **Everything is assembled, not built.** A modern application is 90%+ third-party code — open-source libraries, their dependencies, and *their* dependencies (the "transitive" tree). You wrote a fraction of what you ship
2. **Everything is outsourced.** Your data lives in other companies' clouds and SaaS tools; your operations depend on vendors who depend on vendors

So the attack surface extends far beyond anything you own. And attackers noticed: **why attack a hardened target directly when you can compromise a weaker supplier and inherit access to all *their* customers at once?** One compromised vendor can breach thousands of organisations — the amplification is the whole appeal.

## The two flavours

**Software supply chain — compromised code:**

- **Malicious/compromised dependencies** — an attacker poisons a popular open-source package (via a hijacked maintainer account, typosquatting a package name, or a malicious update), and everyone who pulls it is compromised → [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|the same package-poisoning idea]]
- **Compromised build/update pipeline** — **SolarWinds (2020)** is the defining case: attackers compromised the *build system* of a network-management tool and inserted a backdoor into a legitimate, signed update, which ~18,000 organisations then installed themselves. The update was authentic — that's what made it devastating
- **Vulnerable dependencies** — not malicious, just flawed. **Log4Shell (2021)** — a critical bug in Log4j, a logging library embedded in countless applications — meant a single library's flaw was a global emergency, and most organisations didn't even know they *had* it → [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|vulnerable components]]

**Third-party/vendor risk — compromised suppliers:**

- A vendor with access to your systems or data gets breached, and the attacker pivots to you. **Target's 2013 breach came through an HVAC contractor** with network access
- A SaaS provider holding your data is breached → your data is breached
- A managed service provider compromised → all their clients exposed at once

## Why it's a governance problem

You can't *technically* secure code and systems you don't control — so third-party risk is managed through **governance and process**, which is why it lives in this folder → [[cybersecurity/08-governance-risk-and-compliance/03-governance-and-the-human-layer|governance]]:

**Know what you depend on — you can't manage unknown risk:**
- **SBOM (Software Bill of Materials)** — a complete inventory of every component in your software, so when the next Log4Shell drops you can answer "are we affected?" in minutes, not weeks. **The single most valuable supply-chain control**, and increasingly mandated
- **Vendor inventory** — who has access to what data and systems. The [[cybersecurity/14-api-security/06-the-api-security-lifecycle|"you can't secure what you've forgotten"]] principle, applied to suppliers

**Vet and monitor third parties:**
- **Vendor security assessments** — before onboarding, review a supplier's security (their SOC 2 report, questionnaires, certifications) → [[cybersecurity/08-governance-risk-and-compliance/01-risk-and-frameworks|SOC 2]]. This is often the *reason* your own company needs SOC 2 — customers demand it of *you*
- **Contractual requirements** — breach-notification clauses, security obligations, right-to-audit
- **Least privilege for vendors** — a supplier gets the minimum access needed, so a compromise of them is bounded (Target's HVAC contractor should never have been able to reach the payment network) → [[cybersecurity/01-fundamentals/04-security-principles|least privilege]], [[cybersecurity/03-network-security/02-network-segmentation|segmentation]]
- **Ongoing monitoring** — a vendor secure at onboarding may not stay secure

**Secure your own software supply chain:**
- **Scan dependencies** for known vulnerabilities (SCA — software composition analysis) in CI, continuously → [[cybersecurity/09-cloud-security/05-cloud-native-defence|shift-left scanning]]
- **Pin and verify** — lock dependency versions, verify signatures/hashes, use trusted registries
- **Secure the build pipeline** — it's a high-value target (SolarWinds); protect it like production, and use provenance attestation (SLSA) so you can prove what went into a build

## The uncomfortable truth

**You are only as secure as your least-secure dependency, and you have limited visibility into most of them.** Perfect internal security is undone by one poisoned library or one breached vendor. This is genuinely hard and not fully solvable — the honest goal is to **reduce and bound** the risk: know your dependencies (SBOM), vet and least-privilege your vendors, monitor continuously, and assume a supplier *will* eventually be compromised, so segment and limit what that compromise can reach. It's [[cybersecurity/07-security-operations/01-defensive-architecture|defence in depth]] extended to a perimeter you don't own.

## Key insight

**Supply-chain risk — inherited from your software dependencies and your vendors — has become a dominant breach vector because everything is assembled from third-party code and outsourced to third-party services, so attackers compromise a weak supplier to reach all its customers at once (SolarWinds, Log4Shell, Target).** You can't technically control what you don't own, so it's managed through governance: know your dependencies with an SBOM, vet and least-privilege your vendors, scan continuously, and assume a supplier will eventually be breached — then bound what that breach can reach. You are only as secure as your least-secure dependency, and the goal is to make that a bounded, known risk rather than an invisible one.

## Related
- [[cybersecurity/08-governance-risk-and-compliance/03-governance-and-the-human-layer|governance]] — the process side this depends on
- [[cybersecurity/08-governance-risk-and-compliance/01-risk-and-frameworks|risk and frameworks]] — SOC 2 and vendor assessment
- [[cybersecurity/09-cloud-security/04-container-and-kubernetes-security|container supply chain]] — image scanning and provenance
- [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|vulnerable components]] — the technical view

*Source: [reference] — Aug 2026.*
