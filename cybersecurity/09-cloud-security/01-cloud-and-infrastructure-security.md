# Cloud & Infrastructure Security

**[reference]** — from the roadmap.sh cyber-security roadmap. Securing modern cloud workloads, where **misconfiguration — not exotic exploits — causes most breaches**. This heavily overlaps the [[devops/README|DevOps domain]], so it cross-links there for the infrastructure mechanics and focuses on the security lens.

## The shared responsibility model

The foundational cloud-security concept: **the provider secures the cloud; you secure what you put in it** ([[devops/03-cloud/01-cloud-fundamentals|cloud fundamentals]]). The provider handles physical security, the hypervisor, and managed-service internals; **you** own your data, access controls, network config, and — depending on the service model — the OS and application. The line shifts with IaaS/PaaS/SaaS, and misunderstanding *where* it sits is itself a source of breaches (assuming the provider secures something they don't).

The critical consequence: **most cloud breaches are the customer's misconfiguration, not the provider being hacked** — a public S3 bucket, an over-permissive IAM role, an exposed database, a leaked API key. Cloud security is largely *configuration* security.

## Identity and Access Management (IAM)

In the cloud, **identity is the new perimeter** — there's no network edge to hide behind, so who-can-do-what-to-which-resource is the primary control. The disciplines:

- **Least privilege** — grant the minimum permissions needed, the cloud embodiment of [[cybersecurity/07-security-operations/01-defensive-architecture|zero-trust]]. Over-broad IAM roles are the most common and dangerous cloud misconfiguration.
- **No long-lived credentials** — prefer temporary, role-based credentials (an app assumes a role) over static access keys that leak and never expire. Leaked keys in a Git repo are a classic breach ([[devops/09-secret-management/README|secret management]]).
- **MFA everywhere**, especially on privileged/root accounts.
- **Audit everything** — cloud audit logs (CloudTrail, etc.) record every API call; feed them to a [[cybersecurity/07-security-operations/02-logging-siem-and-detection|SIEM]].

## The cloud attack surface

What attackers target in the cloud:

- **Misconfigured storage** — public buckets exposing sensitive data (the recurring headline breach).
- **Exposed secrets** — API keys/credentials in code, images, or client-side.
- **Over-permissioned IAM** — a compromised low-privilege identity that can escalate because roles are too broad.
- **Metadata service abuse** — [[cybersecurity/06-attacks-and-threats/03-web-application-attacks|SSRF]] reaching the cloud instance-metadata endpoint to steal credentials.
- **Insecure defaults & unpatched managed services** — leaving things open that ship open.

The defenses are **CSPM** (Cloud Security Posture Management — tools that continuously scan for misconfigurations) and infrastructure-as-code scanning (catch the misconfig *before* it deploys).

## Container and Kubernetes security

Containers ([[devops/02-docker/README|Docker]]) and [[devops/05-orchestration/01-kubernetes|Kubernetes]] add their own surface:

- **Image security** — scan images for vulnerable dependencies ([[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|vulnerable components]]), use minimal base images, never bake secrets into images, use trusted registries.
- **Runtime** — don't run containers as root, drop unneeeded Linux capabilities, enforce network policies (a compromised container shouldn't reach everything), use admission controllers.
- **K8s config** — RBAC (least privilege for the cluster), secrets management (native k8s Secrets are only base64 — [[devops/09-secret-management/01-secret-management|Sealed Secrets/Vault]]), network segmentation between namespaces.

## Infrastructure as Code security

Since infrastructure is now [[devops/07-infrastructure-as-code/README|code]] (Terraform, etc.), security shifts *left* — into the code and pipeline:

- **Scan IaC** for insecure configs before apply (Checkov, tfsec, Terrascan) — catch the public bucket in the pull request, not in production.
- **Never hardcode secrets** in IaC or state files.
- **Policy as code** — enforce guardrails (OPA/Sentinel) so non-compliant infrastructure can't deploy.

This is the heart of **DevSecOps** — security integrated into the [[devops/06-ci-cd/README|CI/CD pipeline]] rather than bolted on after, and a natural specialty for someone with both dev and ops skills.

## The through-line

Cloud security is less about novel attacks and more about **discipline at scale**: least-privilege identity, no exposed secrets, secure-by-default configuration, and continuous scanning — because in the cloud a single misconfiguration is instantly internet-reachable. It's the [[cybersecurity/07-security-operations/01-defensive-architecture|defense-in-depth and zero-trust]] principles applied to an environment with no perimeter.

## Related
- [[devops/03-cloud/01-cloud-fundamentals|Cloud Fundamentals (DevOps)]] — the shared-responsibility model and providers
- [[devops/09-secret-management/README|Secret Management (DevOps)]] — the exposed-secrets defense
- [[cybersecurity/07-security-operations/01-defensive-architecture|Defensive Architecture]] — zero-trust, which cloud security embodies
