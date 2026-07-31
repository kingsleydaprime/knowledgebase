# Incident Response

**[reference]** — from the roadmap.sh cyber-security roadmap. What you do *when* (not if) something gets through — the disciplined process that turns a breach from a catastrophe into a contained, learned-from event.

## Why a process, not panic

During a live incident, ad-hoc reactions make things worse: tipping off the attacker, destroying evidence, or taking down more than necessary. A defined **incident response (IR) process** — decided calmly in advance — is what lets a team act fast *and* correctly under pressure. It's the security counterpart to a [[devops/README|DevOps]] on-call runbook.

## The IR lifecycle (NIST / SANS)

The standard phases (SANS's PICERL is a common mnemonic):

1. **Preparation** — *before* anything happens: an IR plan, a trained team with defined roles, tooling ([[cybersecurity/07-security-operations/02-logging-siem-and-detection|logging/EDR]] in place so you *have* evidence), communication plans, and **runbooks** for common scenarios. The most important phase — you can't improvise this mid-crisis.
2. **Identification / Detection** — recognize that an incident is happening and determine scope: what's affected, how bad, what kind. Triage a [[cybersecurity/07-security-operations/02-logging-siem-and-detection|SIEM alert]] or [[cybersecurity/07-security-operations/03-threat-intelligence-and-hunting|hunt]] finding from "event" to "incident."
3. **Containment** — stop the bleeding without destroying evidence. *Short-term* (isolate the affected host from the network) and *long-term* (temporary fixes to keep operating while you eradicate). The judgment call: contain fast, but don't tip off an attacker before you understand the full scope (they may burrow deeper).
4. **Eradication** — remove the threat: delete malware, close the vulnerability that was exploited, reset compromised credentials, remove attacker persistence/backdoors. Half-eradication means they're back tomorrow.
5. **Recovery** — restore systems to normal operation safely: rebuild from known-good [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|backups]] (the ransomware answer), verify systems are clean, monitor closely for the attacker's return, and gradually return to production.
6. **Lessons Learned** — a blameless post-incident review: what happened, how well the response went, and *what to change* (a new detection rule, a patch, a process fix) so it doesn't recur. This closes the loop back into **Preparation** — the phase teams most often skip and most regret skipping.

```
Preparation → Identification → Containment → Eradication → Recovery → Lessons Learned
     ↑___________________________________________________________________|
                      (lessons feed back into preparation)
```

## SOAR and runbooks

- **Runbooks / playbooks** — step-by-step procedures for specific incident types (ransomware, phishing, data breach), so responders follow a proven path instead of improvising. Preparation made concrete.
- **SOAR** (Security Orchestration, Automation and Response) — automates parts of the response: auto-enrich an alert with threat intel, auto-isolate a flagged host, auto-open a ticket. Fights alert volume and speeds the repetitive early steps, freeing analysts for judgment calls.

## The human and legal side

IR isn't purely technical: **communication** (who's informed, when — leadership, legal, PR, customers), **legal/regulatory** obligations (breach-notification laws like GDPR's 72-hour rule — [[cybersecurity/08-governance-risk-and-compliance/01-risk-and-frameworks|compliance]]), and **chain of custody** for any evidence that might be used legally ([[cybersecurity/07-security-operations/05-forensics-and-malware-analysis|forensics]]). Mishandling these can turn a well-handled technical response into a legal or reputational disaster.

## Related
- [[cybersecurity/07-security-operations/05-forensics-and-malware-analysis|Forensics & Malware Analysis]] — the deep investigation during/after an incident
- [[cybersecurity/07-security-operations/02-logging-siem-and-detection|Logging, SIEM & Detection]] — where incidents are first spotted
- [[cybersecurity/08-governance-risk-and-compliance/README|Governance, Risk & Compliance]] — the obligations IR must satisfy
