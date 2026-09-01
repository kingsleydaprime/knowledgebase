# Cloud Security

Securing workloads in the cloud, where **the perimeter dissolves and misconfiguration — not exotic exploits — causes most breaches.** Heavily overlaps the [[devops/README|DevOps domain]], so this **cross-links there** for the infrastructure mechanics and focuses on the *security* lens. Part of the [[cybersecurity/README|Cybersecurity course]].

> **The one idea:** the provider secures the cloud, you secure what you put in it — and in a perimeter-less environment a single wrong setting is instantly internet-reachable. So cloud security is **identity and configuration discipline at scale**, not exploitation: least privilege, no exposed secrets, secure-by-default config, continuous scanning.

## Reading order

**Expanded from one note to five (Sep 2026)** — the topic is a whole domain, and one note undersold it.

1. [[cybersecurity/09-cloud-security/01-the-shared-responsibility-model|the-shared-responsibility-model]] — **[Intermediate]** — the foundational split, how the line moves with IaaS/PaaS/SaaS, **why misconfiguration dominates**, and how the perimeter dissolved
2. [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|identity-is-the-perimeter]] — **[Advanced]** — **IAM as the primary control**, least privilege, role-based over static keys, and the **privilege-escalation paths** over-permissioning enables
3. [[cybersecurity/09-cloud-security/03-the-cloud-attack-surface|the-cloud-attack-surface]] — **[Advanced]** — what attackers target, ranked: public storage, exposed secrets, over-broad IAM, and **the metadata-service-via-SSRF path (Capital One)**
4. [[cybersecurity/09-cloud-security/04-container-and-kubernetes-security|container-and-kubernetes-security]] — **[Advanced]** — the three added layers (image, runtime, cluster), **and why every default is insecure**
5. [[cybersecurity/09-cloud-security/05-cloud-native-defence|cloud-native-defence]] — **[Advanced]** — **shift-left (IaC scanning, policy-as-code)**, continuous posture (CSPM/CIEM/CNAPP), and detect-and-respond (CloudTrail → SIEM). DevSecOps

## If you only take three things

1. **Your data and your access controls are always yours** — no service secures those for you ([[cybersecurity/09-cloud-security/01-the-shared-responsibility-model|01]]).
2. **Least privilege caps the blast radius of every other mistake** — a compromise can do exactly what the identity is permitted ([[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|02]]).
3. **A single misconfiguration is instantly internet-reachable** — so catch it in the PR (shift-left) and scan production continuously ([[cybersecurity/09-cloud-security/05-cloud-native-defence|05]]).

## Related
- [[devops/03-cloud/01-cloud-fundamentals|Cloud Fundamentals (DevOps)]] — the shared-responsibility model, from the ops side
- [[devops/09-secret-management/README|Secret Management (DevOps)]] — keeping keys out of code
- [[devops/05-orchestration/README|Kubernetes (DevOps)]] — what container security secures
- [[cybersecurity/07-security-operations/README|Security Operations]] — cloud detection & response
- [[cybersecurity/14-api-security/04-input-validation-and-injection|API security: SSRF]] — the metadata-service attack path
