# 05 — Container Orchestration

Once you have more than a handful of containers ([[devops/02-docker/README|02-docker]]), you need something to schedule them across machines, restart them when they die, scale them, and route traffic to them. That something is an orchestrator — and in practice it means **Kubernetes**. Part of the [[devops/README|DevOps curriculum]].

**[reference]** — covered from roadmap.sh and primary docs; the honest next step is running a real cluster (even a local `kind`/`minikube` one).

## Reading order

1. [[devops/05-orchestration/01-kubernetes|Kubernetes]] — **[Advanced]** — the architecture (control plane vs nodes), the core objects (pods, deployments, services, ingress), the declarative model, networking, storage, and config/secrets
2. [[devops/05-orchestration/02-orchestration-landscape|The Orchestration Landscape]] — **[Advanced]** — Docker Swarm, the managed offerings (GKE/EKS/AKS), OpenShift, and Nomad — what each trades off against raw Kubernetes

## Related
- [[devops/02-docker/README|Docker]] — the containers this section orchestrates
- [[devops/06-ci-cd/README|CI/CD]] — how images get built and deployed into a cluster
- [[devops/11-delivery-and-advanced/01-gitops|GitOps]] — declaratively driving a cluster from git
- [[devops/11-delivery-and-advanced/03-service-mesh|Service Mesh]] — the networking layer on top of k8s
