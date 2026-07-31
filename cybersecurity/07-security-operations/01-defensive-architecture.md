# Defensive Architecture

**[reference]** — from the roadmap.sh cyber-security roadmap. How you build systems to be *defensible in the first place* — the strategy that everything else in [[cybersecurity/07-security-operations/README|security operations]] operates within.

## Defense in depth

The foundational principle: **no single control is trusted to stop everything, so you layer them.** A firewall *and* segmentation *and* endpoint protection *and* MFA *and* logging *and* least privilege — so a failure or bypass of one layer is caught by the next. An attacker must defeat every layer; a defender only needs one to catch them.

```
perimeter (firewall) → network (segmentation) → host (hardening/EDR)
   → application (secure coding) → data (encryption) → identity (MFA, least privilege)
        ...with monitoring across all layers
```

This connects to the [[cybersecurity/01-fundamentals/02-cia-triad|CIA triad]]: each layer protects confidentiality, integrity, and availability from a different angle.

## Zero Trust

The modern evolution beyond "castle-and-moat" (trust everything inside the perimeter). **Zero Trust** assumes the network is already hostile and the perimeter is gone (cloud, remote work, mobile): **never trust, always verify.** Its tenets:

- **Verify explicitly** — authenticate and authorize *every* request based on identity, device health, and context — not on network location. Being "inside the network" grants nothing.
- **Least privilege** — give the minimum access needed, just-in-time; assume any account can be compromised so limit its blast radius.
- **Assume breach** — design as if attackers are already inside: microsegment, encrypt everywhere, monitor continuously.

Zero Trust is why a phished credential ([[cybersecurity/06-attacks-and-threats/01-social-engineering|social engineering]]) or a foothold on one host doesn't automatically reach everything — it's the architectural answer to lateral movement.

## Hardening

**System hardening** shrinks the attack surface by removing what isn't needed and locking down what remains:

- Disable unused services, ports, and default accounts; change default credentials.
- Apply the principle of least functionality — a server runs only what it must.
- Enforce secure configuration baselines (the **CIS Benchmarks** — [[cybersecurity/08-governance-risk-and-compliance/01-risk-and-frameworks|frameworks]]).
- Patch promptly, enforce least-privilege permissions, enable OS security features (ASLR/DEP, SELinux/AppArmor, [[devops/01-linux/README|Linux]] controls).
- **Group Policy** (Windows) / configuration management (Ansible — [[devops/07-infrastructure-as-code/02-configuration-management|IaC]]) to enforce hardening at scale.

Every disabled service is one fewer thing to exploit or patch — hardening directly reduces the [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|exploit surface]].

## The teams: blue, red, purple

Security operations is organized around adversarial roles:

- **Red team** — offensive; simulates real attackers to find weaknesses ([[cybersecurity/02-ethical-hacking/README|ethical hacking / pentesting]] is the discipline).
- **Blue team** — defensive; monitors, detects, and responds (the [[cybersecurity/07-security-operations/README|SOC]], this whole section).
- **Purple team** — collaboration between the two: red attacks, blue detects, and they share findings to improve detection in a tight loop. The most productive model — offense and defense sharpening each other rather than working in silos.

## Why architecture comes first

Detection, response, and forensics (the rest of this section) are what you do when prevention fails — and it *will* fail. But a well-architected system (defense-in-depth + zero-trust + hardening) means failures are contained, noisy, and survivable, rather than catastrophic. You can't monitor your way out of a flat, unhardened, over-permissioned network — architecture determines how much the blue team can actually defend.

## Related
- [[cybersecurity/07-security-operations/02-logging-siem-and-detection|Logging, SIEM & Detection]] — monitoring the layers this builds
- [[cybersecurity/03-network-security/02-network-segmentation|Network Segmentation]] — a core defense-in-depth/zero-trust layer
- [[cybersecurity/08-governance-risk-and-compliance/README|Governance, Risk & Compliance]] — the frameworks that mandate this
