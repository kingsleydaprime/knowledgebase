# The Shared Responsibility Model

**[Intermediate]** — the one concept cloud security is built on, why misconfiguration (not exotic exploits) causes most cloud breaches, and where the line actually sits. Overlaps the [[devops/README|DevOps domain]] — this is the *security* lens.

## The kid version first

When you rent space in the cloud, security is *split*: the provider (AWS, Azure, GCP) secures the building, the locks, and the plumbing; **you** secure everything you put inside your unit and who you give keys to. The provider is world-class at their half. **Almost every cloud breach is a customer leaving their own door open** — a public storage bucket, an over-powered access key, a database with no password.

Getting clear on *which* half is yours is the foundational skill, because assuming the provider handles something they don't is itself how people get breached.

## The model

> **The provider secures the cloud; you secure what you put in it.**

```
   PROVIDER secures:              YOU secure:
   physical data centres          your DATA (always yours)
   the hypervisor                 IAM / who can do what
   the network hardware           network config (security groups, firewalls)
   managed-service internals       your application code
                                  (and, lower down the stack, the OS and patching)
```

**The line moves with the service model** — this is the part people get wrong:

| Model | Provider handles | You handle |
|---|---|---|
| **IaaS** (a raw VM) | Hardware, hypervisor, network | **OS, patching, runtime, app, data, IAM, config** |
| **PaaS** (a managed platform) | + OS, runtime | App, data, IAM, config |
| **SaaS** (finished software) | + the app itself | **Data, and who has access** |

**Whatever the model, two things are *always* yours: your data, and your access controls.** No cloud service secures those for you — that's the through-line.

## Why misconfiguration dominates

**Most cloud breaches are the customer's misconfiguration, not the provider being hacked.** The providers' own infrastructure is exceptionally well-secured — you will almost never out-secure AWS's physical and hypervisor security. What breaks is the customer's config:

- A storage bucket set to public → sensitive data indexed by search engines
- An IAM role with `*` permissions → one compromised credential owns everything
- A database exposed to the internet with a default or no password
- An API key committed to a public Git repo → scraped within minutes → [[devops/09-secret-management/README|secret management]]

**Cloud security is therefore largely *configuration* security**, which is why the discipline looks different from classic pentesting. The attacker isn't finding a buffer overflow; they're finding the door you left open — and in the cloud, a single misconfiguration is **instantly internet-reachable**. There's no internal network to hide a mistake behind → [[cybersecurity/09-cloud-security/03-the-cloud-attack-surface|the attack surface]].

## Why the perimeter dissolved

On-premises security assumed a **network perimeter** — a firewall around the corporate network, trusted inside, untrusted outside. **The cloud demolishes that model:**

- Resources are internet-facing by default (a bucket, an API, a function all have public endpoints)
- Workloads are ephemeral — VMs and containers spin up and down constantly, so a fixed firewall around fixed machines makes no sense
- Everything is an API call — the "network" is now identity and authorization, not cables and firewalls

So cloud security replaces the perimeter with **identity as the new perimeter** — who-can-do-what-to-which-resource becomes the primary control, which is [[cybersecurity/07-security-operations/01-defensive-architecture|zero trust]] applied to infrastructure → [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|identity]].

## The through-line for the whole folder

Cloud security is **discipline at scale, not novel exploits**:

1. **Least-privilege identity** — the primary control now that there's no perimeter → [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|02]]
2. **No exposed secrets, no public-by-accident resources** → [[cybersecurity/09-cloud-security/03-the-cloud-attack-surface|03]]
3. **Secure-by-default configuration**, including containers and Kubernetes → [[cybersecurity/09-cloud-security/04-container-and-kubernetes-security|04]]
4. **Continuous scanning and detection**, because config drifts and a single mistake is instantly exposed → [[cybersecurity/09-cloud-security/05-cloud-native-defence|05]]

Each is [[cybersecurity/07-security-operations/01-defensive-architecture|defence-in-depth and zero-trust]] applied to an environment with no edge.

## Key insight

**The shared responsibility model draws a line — the provider secures the cloud, you secure what you put in it — and the line moves with the service model, but your *data* and your *access controls* are always yours.** Almost every cloud breach is a customer misconfiguration on their side of that line, because in a perimeter-less environment a single wrong setting is instantly internet-reachable. Cloud security is therefore configuration and identity discipline at scale, not exotic exploitation — and knowing exactly which half is yours is where it starts.

## Related
- [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|identity is the new perimeter]] — the primary control
- [[devops/03-cloud/01-cloud-fundamentals|cloud fundamentals (DevOps)]] — the model from the ops side
- [[cybersecurity/07-security-operations/01-defensive-architecture|defensive architecture]] — zero trust, which this embodies
- [[cybersecurity/09-cloud-security/03-the-cloud-attack-surface|the cloud attack surface]]

*Source: [reference] — Aug 2026.*
