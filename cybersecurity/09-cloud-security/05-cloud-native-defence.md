# Cloud-Native Defence

**[Advanced]** — how you actually defend a cloud environment at scale: shifting security left into code, scanning continuously, and detecting what still gets through.

## The kid version first

The previous notes were the *problems*. This one is the *program*: how you keep a cloud environment secure when it has thousands of resources, changes every day, and a single mistake is instantly internet-reachable. The answer is automation on three fronts — **catch misconfigurations in the code before they deploy** (shift left), **scan the running environment continuously** for drift, and **detect and respond** to what still gets through. You cannot do cloud security by hand at cloud scale.

## Shift left: security as code

Since infrastructure is now [[devops/07-infrastructure-as-code/README|code]] (Terraform, CloudFormation, Pulumi), security moves *into the code and the pipeline* — catching problems before they exist in production:

- **Scan IaC before apply** — Checkov, tfsec, Terrascan read your Terraform and flag insecure configs: the public bucket, the `0.0.0.0/0` database, the over-broad role. **Catch it in the pull request, not in a breach report** → [[devops/06-ci-cd/README|CI/CD]]
- **Policy as code** — encode guardrails (OPA/Sentinel, or Kubernetes admission controllers) so *non-compliant infrastructure cannot deploy at all*. "No public buckets, ever" becomes a rule the pipeline enforces, not a wiki page nobody reads → [[cybersecurity/09-cloud-security/04-container-and-kubernetes-security|admission control]]
- **Secret scanning** — gitleaks/trufflehog in CI, blocking commits that contain credentials → [[cybersecurity/09-cloud-security/03-the-cloud-attack-surface|exposed secrets]]
- **Never hardcode secrets** in IaC or state files; encrypt state

**This is the heart of DevSecOps** — security integrated into the pipeline rather than bolted on after, and a natural specialty for someone with both dev and ops skills → [[devops/12-sre-and-platform-engineering/README|platform engineering]]. The economic argument is blunt: **a misconfiguration caught in a PR costs minutes; the same one caught in a breach costs the company.**

## Scan continuously: posture management

Code review isn't enough, because production drifts — someone clicks something in the console, a resource is created outside IaC, a policy is loosened "temporarily." So you scan the *live* environment continuously:

- **CSPM (Cloud Security Posture Management)** — tools that continuously check your running cloud against best-practice and compliance rules, and alert the moment something drifts (a bucket goes public, a role gains admin, MFA is disabled). **The safety net for everything that escapes shift-left**
- **CIEM (Cloud Infrastructure Entitlement Management)** — specifically for the [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|IAM/least-privilege]] problem: continuously analyse who *can* do what, flag over-permissioning, and map privilege-escalation paths
- **CNAPP (Cloud-Native Application Protection Platform)** — the consolidation trend: CSPM + CIEM + workload scanning + runtime protection in one platform (Wiz, Prisma Cloud, and the cloud providers' own — Defender for Cloud, Security Command Center). The category is converging because these problems are one problem

**The point of continuous scanning: a single misconfiguration is instantly internet-reachable, so the window between "someone made a mistake" and "an attacker found it" is short — you need to find it in minutes, automatically, not in the next quarterly audit.**

## Detect and respond: when something gets through

Prevention is never complete, so you need eyes on what's actually happening → [[cybersecurity/07-security-operations/README|security operations]]:

- **Cloud audit logs are the foundation.** AWS CloudTrail, Azure Activity Log, GCP Cloud Audit Logs record **every API call** — who did what, when, from where. This is your ground truth for detection and forensics; **enable it everywhere and protect it** (an attacker's first move is often to disable logging)
- **Ship logs to a SIEM** and alert on the tells: a new access key created, a role assumed from an unusual location, MFA disabled, a bucket made public, mass data access, calls from an unexpected region → [[cybersecurity/07-security-operations/02-logging-siem-and-detection|SIEM and detection]]
- **Threat detection services** — GuardDuty, Defender, and CNAPP runtime modules apply ML and threat intelligence to the logs, flagging credential compromise, crypto-mining, and reconnaissance patterns automatically
- **Runtime workload protection** — Falco and CNAPP agents watch containers and VMs for anomalous behaviour → [[cybersecurity/09-cloud-security/04-container-and-kubernetes-security|runtime detection]]

## Incident response is different in the cloud

Cloud IR has its own shape, worth knowing → [[cybersecurity/07-security-operations/04-incident-response|incident response]]:

- **Everything is logged** (if you enabled it) — CloudTrail gives you a near-complete record of what the attacker did, which is a forensic gift on-prem rarely offers
- **Containment is fast and programmatic** — revoke the compromised role, rotate keys, snapshot for forensics, isolate a resource with a security-group change — all via API, in seconds
- **Blast radius follows IAM** — the first question is "what could this identity do?", which is why [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|least privilege]] limits not just the attack but the whole incident
- **Ephemerality cuts both ways** — a compromised container may already be gone (good for containment, hard for forensics — capture memory and logs fast)

## The whole picture

Cloud defence is a loop, not a checklist:

```
   shift left      → catch misconfig in the PR (policy-as-code, IaC + secret scanning)
   scan continuously → CSPM/CIEM/CNAPP catch drift in production, in minutes
   detect & respond  → CloudTrail → SIEM → threat detection catch what got through
        └────────── feed findings back into policy ──────────┘
```

Each layer catches what the previous missed, and the whole thing is **automated because cloud scale and cloud speed make manual security impossible**.

## Key insight

**Cloud defence is automation on three fronts — shift-left (catch misconfigurations in the pull request via IaC scanning and policy-as-code), continuous posture scanning (CSPM/CIEM/CNAPP catch drift in production within minutes), and detection-and-response (CloudTrail → SIEM catch what got through) — because a single misconfiguration is instantly internet-reachable and cloud scale makes manual security impossible.** DevSecOps is the discipline of pushing security earliest, where a mistake costs minutes instead of a breach; and cloud incident response, powered by complete API audit logs and programmatic containment, is genuinely faster than its on-prem equivalent — provided you turned the logging on before you needed it.

## Related
- [[cybersecurity/09-cloud-security/01-the-shared-responsibility-model|the shared responsibility model]] — where this all started
- [[devops/07-infrastructure-as-code/README|infrastructure as code]] — what shift-left scans
- [[cybersecurity/07-security-operations/README|security operations]] — SIEM, detection, IR
- [[devops/12-sre-and-platform-engineering/README|platform engineering]] — where DevSecOps lives

*Source: [reference] — Aug 2026.*
