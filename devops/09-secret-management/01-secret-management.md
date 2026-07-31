# Secret Management

**[reference]** — from roadmap.sh and the Vault docs.

## The problem

Applications need secrets: database passwords, API keys, TLS private keys, signing keys. The wrong-but-common ways to handle them:

- **Hardcoded in source** — anyone with repo access (or a leaked repo) has your production DB password. Git never forgets, so a secret committed once is compromised *forever*, even if deleted in a later commit.
- **In a plaintext `.env` committed to the repo** — same problem.
- **Pasted into CI config or a Slack message** — sprayed across systems with no rotation or audit.

The [[languages/01-java/03-tooling/01-build-tools|Java build-tools note]] already draws the line for app config: a committed `application.properties` for non-secrets, a **gitignored** `application-local.properties` for secrets. That's the floor. Secret *management* is the ceiling: a dedicated system that stores secrets encrypted, injects them at runtime, controls who can read which, audits every access, and rotates them.

## What a secret manager provides

- **Encrypted storage** — secrets encrypted at rest, not sitting in plaintext anywhere.
- **Access control + audit** — fine-grained "which app/human can read which secret," with a log of every access (so a leak is detectable and scoped).
- **Dynamic secrets** — the strongest feature: instead of a long-lived static password, the manager generates a short-lived credential on demand (e.g. a database user valid for 1 hour) and revokes it automatically. A leaked dynamic secret is worthless minutes later.
- **Rotation** — change secrets on a schedule without an outage, so a compromise has a bounded blast radius.

## HashiCorp Vault

The reference secret manager. Apps authenticate to Vault (via a k8s service account, a cloud IAM role, a token) and request secrets at runtime rather than holding them:

```
app  ──authenticate──►  Vault  ──►  returns a short-lived DB credential
                          │          (generated on the fly, auto-revoked after TTL)
                          └─ encrypted storage, per-path policies, full audit log
```

Vault does static secret storage, **dynamic secrets** (databases, cloud creds, SSH), encryption-as-a-service (encrypt data without the app holding keys), and PKI (issuing certificates). Its power is also its cost — it's a critical, stateful service you must run, secure, and keep highly available (if Vault is down, apps can't get secrets).

## The Kubernetes wrinkle

Native **Kubernetes Secrets are only base64-encoded, not encrypted** — base64 is encoding, not security, and by default they sit readable in etcd. So a whole ecosystem exists to fix this, especially for the GitOps problem of "how do I store a secret in git safely":

| Tool | Approach |
|---|---|
| **Sealed Secrets** | encrypt a secret into a `SealedSecret` that's safe to commit to git; only the in-cluster controller can decrypt it |
| **External Secrets Operator (ESO)** | sync secrets from an external manager (Vault, AWS Secrets Manager) into k8s Secrets automatically |
| **SOPS** | encrypt values inside a YAML/JSON file (with a KMS/age key) so the file is git-safe with only the values encrypted |
| **Vault Agent / CSI driver** | inject Vault secrets straight into pods as files/env |

These exist specifically to reconcile "everything in git" ([[devops/11-delivery-and-advanced/01-gitops|GitOps]]) with "never put a plaintext secret in git."

## Cloud-native options

Each provider has a managed secret store — **AWS Secrets Manager / Parameter Store**, **Azure Key Vault**, **GCP Secret Manager** — integrated with that cloud's IAM, so an app assumes a role and reads its secrets with no long-lived credential at all. For teams already all-in on one cloud, this is often simpler than running Vault.

## The principles, regardless of tool

- **Never in git, never in an image, never in plaintext config.**
- **Least privilege** — each service reads only the secrets it needs.
- **Short-lived over long-lived** — dynamic/rotating secrets beat static ones; a leaked credential should expire fast.
- **Audit everything** — you must be able to answer "who accessed this secret, when."
- **Inject at runtime** — the app fetches secrets when it starts/needs them, rather than baking them in at build time.

This is the same least-privilege, secure-by-default mindset as the cloud [[devops/03-cloud/01-cloud-fundamentals|shared-responsibility model]] — most breaches are leaked or over-permissioned credentials, not broken crypto.

## Related
- [[devops/07-infrastructure-as-code/README|Infrastructure as Code]] — IaC references secrets, never hardcodes them
- [[devops/05-orchestration/01-kubernetes|Kubernetes]] — why native k8s Secrets need help
- [[devops/11-delivery-and-advanced/01-gitops|GitOps]] — the "secrets in git" problem these tools solve
- [[cybersecurity/05-cryptography/README|Cryptography]] — the encryption underneath
