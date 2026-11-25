# Cloud Security

**This section is securing the rented computers almost everything now runs on: in the cloud the network wall is gone, so a single wrong setting is instantly reachable from the whole internet, and misconfiguration — not exotic exploits — causes nearly every breach.**

Cloud security heavily overlaps the [[devops/index|DevOps domain]], so this section cross-links there for the infrastructure mechanics and focuses on the *security* lens. The one idea underneath it all: the provider secures the cloud, you secure what you put in it — so cloud security is **identity and configuration discipline at scale**. The hands-on work is exactly that discipline: finding a public bucket, tightening an over-broad policy, hardening a container, and catching a misconfiguration in code before it ships.

## What you'll be able to do

By the end of this section you will be able to:

- map a deployment's responsibility split and find the customer-side misconfiguration;
- rewrite an over-permissioned IAM policy into a least-privilege one;
- trace the metadata-service attack that caused Capital One, and audit for its links;
- harden and scan a container, and catch a cloud misconfiguration in Terraform before it deploys.

## Reading order

1. [[cybersecurity/09-cloud-security/01-the-shared-responsibility-model|01 — The Shared Responsibility Model]] — **[Intermediate]** — who secures what, how the line moves with IaaS/PaaS/SaaS, why misconfiguration dominates, and a responsibility audit.
2. [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|02 — Identity Is the New Perimeter]] — **[Advanced]** — IAM as the primary control, least privilege, role credentials over static keys, privilege escalation, and a policy-rewrite lab.
3. [[cybersecurity/09-cloud-security/03-the-cloud-attack-surface|03 — The Cloud Attack Surface]] — **[Advanced]** — the ranked catalogue of misconfigurations and the metadata-via-SSRF path (Capital One), with an open-door audit.
4. [[cybersecurity/09-cloud-security/04-container-and-kubernetes-security|04 — Container and Kubernetes Security]] — **[Advanced]** — the three added layers (image, runtime, cluster) and their insecure defaults, with a Docker and Trivy hardening lab.
5. [[cybersecurity/09-cloud-security/05-cloud-native-defence|05 — Cloud-Native Defence]] — **[Advanced]** — shift-left (IaC scanning, policy-as-code), continuous posture (CSPM/CIEM/CNAPP), and detect-and-respond, with a Checkov lab.

## If you only take three things

1. **Your data and your access controls are always yours** — no cloud service secures those for you.
2. **Least privilege caps the blast radius of every other mistake** — a compromise can do exactly what the identity is permitted.
3. **A single misconfiguration is instantly internet-reachable** — so catch it in the pull request and scan production continuously.

## Related

- [[cybersecurity/index|The cybersecurity course]] — the whole map.
- [[devops/08-cloud/01-cloud-fundamentals|Cloud fundamentals (DevOps)]] — the shared-responsibility model from the ops side.
- [[devops/06-secret-management/index|Secret management (DevOps)]] — keeping keys out of code.
- [[cybersecurity/07-security-operations/index|Security operations]] — cloud detection and response.

## About this section

**How it's built:** five lessons on securing cloud workloads, each with a hands-on element against owned or local targets — a responsibility audit, a least-privilege policy rewrite, an open-door audit with `gitleaks`, a Docker/Trivy hardening lab, and a Checkov shift-left scan. All reproducible without a paid cloud account. Rebuilt to the [[COURSE-STANDARD|course standard]]: all five lessons converted. Live runs are tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
