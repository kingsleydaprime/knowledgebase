# 09 — Secret Management

Passwords, API keys, TLS private keys, and database credentials must never live in git or a plaintext env file in a repo. This section covers how secrets are stored, injected, and rotated safely. Part of the [[devops/README|DevOps curriculum]].

**[reference]** — covered from roadmap.sh and primary docs.

## Reading order

1. [[devops/09-secret-management/01-secret-management|Secret Management]] — **[Advanced]** — why secrets can't live in git, the tools (HashiCorp Vault in depth, plus SOPS, Sealed Secrets, External Secrets Operator, and cloud KMS/Secrets Manager), dynamic secrets, and rotation

## Related
- [[devops/07-infrastructure-as-code/README|Infrastructure as Code]] — IaC references secrets, never hardcodes them
- [[devops/05-orchestration/01-kubernetes|Kubernetes]] — k8s Secrets and why they need help (Sealed Secrets, ESO)
- [[devops/08-networking-and-web/01-networking-and-protocols|Networking & Protocols]] — TLS certificates are managed secrets
- [[devops/README|DevOps curriculum map]]
