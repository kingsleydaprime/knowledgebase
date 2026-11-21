---
id: e99893db-d1b1-49bc-9100-07ca02685f39
---

# Getting Into Infrastructure

The previous four notes describe the machine, the building and the wiring. **This one is about working on them**, because "data centre" covers several genuinely different jobs.

## The roles, and what separates them
<!-- bite: 7e1a3d19-a513-4971-8fb5-538526a6372c -->

| Role | Owns | Core skill | Ceiling |
|---|---|---|---|
| **Data centre technician** | Racking, cabling, hands-on remediation | Physical, methodical, follows procedure | Modest — but a real door in |
| **Network engineer** | Switching, routing, the fabric | **Deep networking** | High; specialised |
| **Systems / infrastructure engineer** | Servers, OS, virtualisation, storage | Linux, automation | High |
| **Cloud engineer** | Cloud infrastructure as code | Terraform, one cloud deeply | High, and the largest market |
| **SRE / platform** | Reliability, delivery platforms | Software + operations | Highest → [[devops/12-sre-and-platform-engineering/index\|12]] |
| **Hardware / capacity** | Procurement, power, cooling, planning | Electrical + facilities | Specialised, scarce |

**The split that matters: hands-on-metal versus infrastructure-as-software.**

**Hands-on** roles — technician, cabling, hardware — are geographically bound (you must be at the building), pay less, and have a lower ceiling. They're a genuine entry point with few prerequisites, and a poor destination.

**Infrastructure-as-software** roles — cloud, SRE, platform, network automation — are remote-friendly, pay well, and are where the field has moved. **This is the direction to aim at**, and it is reachable directly.

## The honest market picture
<!-- bite: b58caafe-d710-4a62-b4a1-e310fa359be4 -->

**Physical data centre work is growing** — AI capacity build-out is enormous, and there's real demand for technicians, electricians and facilities engineers. But it is **local work**: you must be near a data centre, and the big ones cluster in specific regions.

**Cloud and platform work is the larger, remote-friendly market**, and it doesn't require the physical layer as a prerequisite — only as *understanding*, which is what notes 01–04 are for.

**For you specifically:** the remote-work goal in your [[learning/catalogue|catalogue]] points clearly at the second column. **Understand the physical layer; work on the software layer.** Notes 01–04 exist so that "availability zone" and "IOPS" and "oversubscription" mean something physical when you're reasoning about a cloud bill or a latency graph — not so you can rack a server.

## What you actually need
<!-- bite: da4f0d2e-0021-4cc9-b115-c8b230318429 -->

**Non-negotiable, in this order:**

**1. Linux, deeply.** Not "I can `cd`" — processes, systemd, networking, storage, permissions, logs, troubleshooting a box that won't boot. **This is the single highest-return skill in infrastructure and there is no way around it** → [[devops/01-linux/index|01-linux]], and the [[devops/01-linux/15-rhcsa/index|RHCSA track]] is a genuinely good structure for it.

**2. Networking.** Subnetting, routing, DNS, TLS, firewalls, and the ability to debug why two machines can't talk. **The most common gap in self-taught infrastructure people** → [[networking/index|networking]].

**3. One cloud, properly.** Not three shallowly. AWS has the largest market; Azure dominates enterprise; GCP is strong in data/ML → [[devops/08-cloud/index|08-cloud]].

**4. Infrastructure as code.** Terraform, and configuration management. **The line between "sysadmin" and "infrastructure engineer" is essentially whether your infrastructure is in git** → [[devops/09-infrastructure-as-code/index|07-IaC]].

**5. A scripting language.** Python and Bash → [[languages/06-python/index|Python]] · [[devops/01-linux/12-bash-scripting|Bash]].

**6. Containers and orchestration.** Docker, then Kubernetes → [[devops/03-docker/index|03-docker]] · [[devops/10-orchestration/index|10-orchestration]].

**Then:** observability → [[devops/07-observability/index|07]], CI/CD → [[devops/05-ci-cd/index|05]], and security posture → [[cybersecurity/09-cloud-security/index|cloud security]].

## Certifications — where they actually help
<!-- bite: 3ff40c98-711c-4123-b5bf-334062be7804 -->

**More than in software development, and this is a real difference between the fields.** Infrastructure hiring uses certs as a filter far more than dev hiring does, particularly for a first role and particularly outside a strong personal network.

**Worth it:**
- **AWS Solutions Architect Associate** — the broadest signal, widely recognised
- **RHCSA** — proves real Linux ability, hands-on exam, hard to fake. **This vault already has a track for it** → [[devops/01-linux/15-rhcsa/index|RHCSA]]
- **CCNA** — still the networking credential, if you're going that direction
- **CKA** — Kubernetes, hands-on, respected

**The honest caveat:** a cert gets you past a filter. **A cert with nothing behind it fails the interview**, and infrastructure interviews are unusually practical — you will be asked to debug something. Pair every cert with something you actually built.

## The realistic routes in
<!-- bite: ba2efc41-e149-4cd5-839d-8bfa4a61d7a8 -->

**From software development — your position, and the shortest path.** You already write code, use git, and understand systems. Adding Linux depth, one cloud and Terraform makes you a **cloud/platform engineer**, and the software background is an *advantage*, not a starting deficit: the field has moved toward infrastructure-as-software, and most people in it came from operations and had to learn to code. You already did the harder half.

**From help desk / IT support.** The classic route: support → sysadmin → infrastructure → cloud. Slower, and it works.

**From a technician role.** Genuinely available with few prerequisites, and the way to use it is to automate your own job and move sideways into engineering.

**From a degree.** Systems engineering is directly relevant — capacity, power, cooling, reliability and interfaces are the discipline → [[systems-engineering/index|systems engineering]].

## What to build
<!-- bite: 2dae65eb-0c14-4385-bd52-16f952b3d6a3 -->

**Infrastructure is proven by what you've run, not what you've read**, and the vault's standing position applies here more than anywhere → [[PRIMETECHIE|reading is not a rank]].

1. **A real VPS, doing something real.** Buy one, harden it, deploy something, keep it up → [[devops/04-vps/vps-setup|04-vps]]. **Publicly reachable and actually used beats any lab**
2. **Everything in Terraform**, in a public repo. VPC, subnets, security groups, an instance. Destroy and recreate it from scratch — that's the claim IaC makes, and doing it proves you understand it
3. **A CI/CD pipeline** that deploys on push → [[devops/05-ci-cd/index|05-ci-cd]]
4. **Monitoring, with an alert that has actually fired** → [[devops/07-observability/index|07]]
5. **A small Kubernetes cluster** — k3s on cheap VPSes teaches more than a managed control plane, because you have to fix it
6. **A home lab**, if hardware appeals — an old machine, a hypervisor, some VMs → [[devops/00-the-physical-layer/02-virtualisation-and-hypervisors|virtualisation]]. This is where the physical notes stop being abstract

**Write up what broke.** An infrastructure portfolio is post-incident notes more than it is repositories — the ability to describe a failure clearly is most of the interview.

## Related
<!-- bite: 6449e2a6-27bd-4fc5-b369-402c0a35a8d2 -->
- [[devops/index|devops]] — the whole track, in order
- [[devops/00-the-physical-layer/index|the physical layer]] — notes 01–04
- [[devops/12-sre-and-platform-engineering/index|SRE and platform engineering]] — where the ceiling is
- [[networking/index|networking]] — the most-skipped prerequisite
- [[PRIMETECHIE|the Primetechie path]] — the gated progression

## About this lesson
<!-- bite: 95a68005-e38b-43c5-a276-3bf93e91a28d -->

**Level:** Beginner. **Covers:** The roles that own the physical and platform layers, what each actually requires, and the realistic routes in — including from where you already are.

*Source: [reference] — written Aug 2026; cross-referenced against the [roadmap.sh devops](https://roadmap.sh/devops) and [network-engineer](https://roadmap.sh/network-engineer) roadmaps.*
