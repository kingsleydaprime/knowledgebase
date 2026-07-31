# 11 — Delivery & Advanced

The advanced delivery topics that sit on top of everything before: driving deployments declaratively from git, storing build outputs, managing service-to-service traffic at scale, and the architectural patterns for building resilient cloud systems. Part of the [[devops/README|DevOps curriculum]].

**[reference]** — the most advanced/least-hands-on section in the domain.

## Reading order

1. [[devops/11-delivery-and-advanced/01-gitops|GitOps]] — **[Advanced]** — git as the single source of truth for infrastructure state, pull vs push delivery, ArgoCD and FluxCD
2. [[devops/11-delivery-and-advanced/02-artifact-management|Artifact Management]] — **[Advanced]** — what artifacts are, container registries, and repository managers (Artifactory, Nexus, Cloud Smith)
3. [[devops/11-delivery-and-advanced/03-service-mesh|Service Mesh]] — **[Advanced]** — the sidecar model, mTLS, traffic management and observability between services (Istio, Linkerd, Consul)
4. [[devops/11-delivery-and-advanced/04-cloud-design-patterns|Cloud Design Patterns]] — **[Advanced]** — availability, scalability, and resilience patterns (retry, circuit breaker, bulkhead, cache-aside) for architecting on the cloud

## Related
- [[devops/05-orchestration/README|Orchestration]] — what GitOps and service meshes operate on
- [[devops/06-ci-cd/README|CI/CD]] — GitOps is the delivery half of the pipeline
- [[devops/README|DevOps curriculum map]]
