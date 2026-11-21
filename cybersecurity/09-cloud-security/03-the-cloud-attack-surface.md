---
id: 2ab9bed1-12c0-4877-909f-8342fe59c5f5
---

# The Cloud Attack Surface

## The kid version first
<!-- bite: 6b3d4d40-e7ba-428d-a069-c847a911c942 -->

Cloud attackers rarely break the cloud itself — the provider's infrastructure is too well-defended. Instead they walk through doors *customers* left open: a storage bucket set to public, a secret key committed to code, an over-powered role, a server tricked into handing over its own credentials. **The cloud attack surface is a catalogue of misconfigurations**, and knowing it is knowing what to check first — on your own environment before an attacker does.

## The recurring headline: public storage
<!-- bite: 8d40a581-b711-4ed8-ad0d-d40b7efd713d -->

**Misconfigured storage buckets are the single most common cloud breach.** A bucket (S3, Azure Blob, GCS) set to public — often "just to make a demo work," then forgotten — exposes whatever's in it directly to the internet, where it gets indexed and scraped:

- Customer records, backups, internal documents, credentials
- The breach requires *no exploit* — the data is simply reachable at a URL
- Automated scanners continuously hunt for public buckets across the internet

**The fix is trivial and the mistake is endemic:** default-deny public access (providers now block it by default at the account level — leave that on), and use CSPM to alert the instant a bucket goes public → [[cybersecurity/09-cloud-security/05-cloud-native-defence|CSPM]]. This one category has caused more publicly-reported cloud breaches than everything else combined.

## Exposed secrets
<!-- bite: 330e026f-5ea9-46bd-af12-a2bb90cc3c89 -->

**Credentials leak, constantly, because they end up somewhere readable:**

- **In source code** — an access key hardcoded and committed. Public GitHub is scraped by bots within *minutes* of a push → [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|key hygiene]]
- **In container images** — a secret baked into a layer stays in the image history even if a later layer "removes" it → [[cybersecurity/09-cloud-security/04-container-and-kubernetes-security|image security]]
- **In client-side code** — a key shipped in a mobile app or SPA is public → [[mobile/12-security-on-device|no secrets in the app]]
- **In logs, error messages, and CI output** — secrets printed and retained
- **In infrastructure-as-code state files** — Terraform state stores secrets in plaintext by default

**Leaked long-lived credentials are the fastest path to a cloud breach**, which is the direct argument for the [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|"no static keys"]] discipline — you can't leak a credential that expires in an hour and never existed as a file. Defences: secret scanning in CI (gitleaks, trufflehog), a secret manager, and short-lived credentials → [[devops/06-secret-management/index|secret management]].

## Over-permissioned identities
<!-- bite: 67c03433-bbb0-4fe8-8d68-993105931d8f -->

Covered in depth in [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|note 02]], but it belongs in the attack-surface catalogue: **a compromised low-privilege identity that can escalate because roles are too broad.** The initial compromise (a leaked key, an SSRF, a vulnerable app) gives a foothold; over-broad IAM turns that foothold into account takeover. **The blast radius of any compromise equals the permissions of the thing compromised** — which is why least privilege caps the damage of everything else on this list.

## Metadata service abuse — SSRF's cloud payoff
<!-- bite: c22384bc-685a-4fce-bb5e-64aaf3604b01 -->

**Every cloud VM has an internal metadata endpoint** (`169.254.169.254`) that returns information about the instance — including, on misconfigured setups, its **IAM role credentials.** Combine that with a [[cybersecurity/14-api-security/04-input-validation-and-injection|Server-Side Request Forgery]] in an app running on that VM, and:

```
   SSRF makes the app fetch  http://169.254.169.254/latest/meta-data/iam/security-credentials/
        → returns the VM's role credentials
             → attacker now acts as that role, from anywhere
```

**This was the mechanism of the Capital One breach (2019, 100M+ records)** — an SSRF reached the metadata service, stole the role's credentials, and the role could read the storage buckets. It's the clearest example of how two "medium" issues (an SSRF, a role with bucket access) compose into a catastrophe.

**The defences:** use **IMDSv2** (requires a session token, defeating basic SSRF-to-metadata — this is the direct fix), least-privilege roles (so stolen credentials are worth little), and egress filtering so workloads can't reach the metadata IP unnecessarily → [[cybersecurity/14-api-security/04-input-validation-and-injection|SSRF defences]].

## Insecure defaults and the rest
<!-- bite: 6ed486f8-ff32-4aab-bcc0-02c0f3ab423f -->

- **Things that ship open** — a managed database reachable from `0.0.0.0/0`, a default admin password, debug endpoints exposed → [[cybersecurity/14-api-security/06-the-api-security-lifecycle|misconfiguration]]
- **Unpatched managed services and workloads** — the shared-responsibility line means *you* patch the OS on IaaS, and the provider patches the managed-service internals; forgetting your half leaves known CVEs open
- **Supply chain** — a compromised dependency, base image, or CI action running with cloud credentials → [[cybersecurity/09-cloud-security/04-container-and-kubernetes-security|container supply chain]]
- **Abandoned resources** — a forgotten VM, an old snapshot made public, an unused but still-privileged access key. **You can't defend what you've forgotten you have** — the cloud version of [[cybersecurity/14-api-security/06-the-api-security-lifecycle|shadow APIs]]

## The attacker's cloud kill chain
<!-- bite: 1f8c17a7-ec11-4b1b-826c-7bc2dac509dc -->

How these compose into a breach, so you see why order matters:

```
1. INITIAL ACCESS   leaked key / SSRF / vulnerable app / phished console login
2. CREDENTIAL THEFT metadata service, secrets in the environment, IAM
3. ESCALATION       over-broad IAM → assume a more powerful role
4. DISCOVERY        enumerate resources, buckets, other accounts
5. ACTIONS          exfiltrate data, deploy miners, ransomware, persist
```

**Each step is enabled by a misconfiguration on the customer's side of the line** — which is why cloud defence is configuration discipline, and why fixing the *first* step (no exposed secrets, no SSRF, least privilege) collapses the whole chain → [[cybersecurity/09-cloud-security/05-cloud-native-defence|defence]].

## Key insight
<!-- bite: 81bb1170-6f29-4a3d-aec5-dd99b4723c98 -->

**The cloud attack surface is a ranked list of customer misconfigurations — public storage, exposed secrets, over-permissioned identities, and the metadata-service-via-SSRF path (Capital One) — not exotic exploits against the provider.** They matter most in combination: an SSRF plus a powerful role, or a leaked key plus broad IAM, is how a "medium" issue becomes a total breach. Because each step of the cloud kill chain depends on a config mistake on your side of the line, fixing the early ones — no public buckets, no static keys, least privilege, IMDSv2 — collapses attacks that no single control would stop.

## Related
<!-- bite: a74a55d2-8ed0-425c-94ab-8c76333c5fd9 -->
- [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|identity is the perimeter]] — the escalation step
- [[cybersecurity/14-api-security/04-input-validation-and-injection|SSRF]] — the metadata-service attack
- [[cybersecurity/09-cloud-security/05-cloud-native-defence|cloud-native defence]] — CSPM and detection
- [[cybersecurity/06-attacks-and-threats/index|attacks and threats]] — the general taxonomy

## About this lesson
<!-- bite: 7d2f029e-6b9b-4daa-85ce-c5ccd6fadba4 -->

**Level:** Advanced. **Covers:** what attackers actually target in the cloud, in order of how often it's the way in, and why almost all of it is a configuration mistake rather than an exploit.

*Source: [reference] — Aug 2026.*
