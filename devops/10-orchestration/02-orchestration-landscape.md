---
id: 17058ff2-1ec6-41d0-818c-d3bc521d5088
---

# The Orchestration Landscape

**[reference]** — from roadmap.sh and vendor docs.

Kubernetes ([[devops/10-orchestration/01-kubernetes|previous note]]) won the orchestration war, but it isn't the only option, and "run raw upstream k8s yourself" is rarely the right choice. This note maps the alternatives and — more usefully — the *managed* options that most teams actually use.

## Self-managed alternatives to raw Kubernetes
<!-- bite: 7261f74a-9798-4f5d-aa38-c924052ce8cf -->

| Tool | Position |
|---|---|
| **Docker Swarm** | Docker's built-in orchestrator. Far simpler than k8s (`docker service` commands, compose-like), good enough for small clusters — but a shrinking ecosystem. Choose it when k8s is overkill and the team already knows Docker. |
| **HashiCorp Nomad** | A simpler, general-purpose scheduler that orchestrates containers *and* non-container workloads (raw binaries, VMs). Lighter than k8s; pairs with Consul/Vault. Niche but loved where k8s complexity isn't wanted. |
| **k3s / kind / minikube** | Lightweight/local Kubernetes distributions. `k3s` for edge/IoT and small prod; `kind` and `minikube` for local development and CI. Same k8s API, less overhead — the right way to *learn* k8s hands-on. |

## Managed Kubernetes — what most teams use
<!-- bite: 9630449b-08a6-4200-9db4-fd84f9bb96fe -->

Running the control plane (etcd, API server, upgrades, HA) yourself is a serious operational burden. The cloud providers run it for you, and you just manage workloads:

| Service | Provider |
|---|---|
| **EKS** (Elastic Kubernetes Service) | AWS |
| **GKE** (Google Kubernetes Engine) | GCP — generally regarded as the most polished; Google created k8s |
| **AKS** (Azure Kubernetes Service) | Azure |

Managed k8s removes the hardest, most dangerous part (control-plane operation and upgrades) while keeping the standard k8s API — so your YAML and tooling are portable across all three. This portability is the quiet superpower of standardizing on k8s: the same manifests run on any provider or on-prem, which is the main hedge against cloud lock-in.

## OpenShift — the enterprise distribution
<!-- bite: 62fa81ac-cf28-481a-91f2-34f2a9e15681 -->

**Red Hat OpenShift** is Kubernetes plus an opinionated enterprise layer: built-in CI/CD, an integrated container registry, stricter security defaults (it won't let containers run as root by default), a developer console, and commercial support. It's k8s underneath, so skills transfer, but it adds guardrails and batteries that large regulated organizations want. Common in enterprises already on Red Hat — which connects to the RHEL material in [[devops/01-linux/15-rhcsa/index|the RHCSA track]].

## How to choose
<!-- bite: 1ab8a96d-72c0-4375-a471-d2e9a736d31f -->

- **Learning / local dev** → `kind`, `minikube`, or `k3s`.
- **Small team, simple needs, already on Docker** → Docker Swarm (or honestly, a managed platform / [[devops/08-cloud/02-serverless|serverless containers]] to skip orchestration entirely).
- **Production at real scale on a cloud** → managed k8s (GKE/EKS/AKS) — don't run the control plane yourself unless you have a strong reason.
- **Large regulated enterprise wanting a supported, opinionated platform** → OpenShift.
- **Mixed container + non-container workloads, wanting simplicity** → Nomad.

The meta-point: the interesting decision is rarely "which orchestrator" — it's "do I need an orchestrator at all, or would managed containers / serverless / a PaaS deliver this with far less operational surface?" Reach for Kubernetes when you genuinely have the scale and complexity that justify it, not by default.

## Related
<!-- bite: 69e80ca1-eea2-41e4-94e6-830e3b481db0 -->
- [[devops/10-orchestration/01-kubernetes|Kubernetes]] — the standard the rest of this landscape is measured against
- [[devops/08-cloud/index|Cloud]] — where managed k8s runs
- [[devops/08-cloud/02-serverless|Serverless]] — the "skip orchestration" alternative
