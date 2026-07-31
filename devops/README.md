# DevOps

A map of this folder, in reading order. The first four sections are the original foundation — a working Linux baseline, containers, cloud, and deploying to a real server. Sections **05–11 are the DevOps-discipline pillars**, added by cross-referencing this domain against the [roadmap.sh DevOps roadmap](https://roadmap.sh/devops): orchestration, CI/CD, infrastructure as code, networking, secrets, observability, and delivery.

## Where the content comes from

- The foundation (`01-linux` … `04-vps`) is grounded in real work — Linux/RHCSA study, actual Docker usage, and VPS deploys.
- Sections **05–11 are mostly `[reference]`** and marked as such: Kubernetes, Terraform, Ansible, Prometheus, service meshes, etc. are covered from roadmap.sh and primary docs, not from having run them in anger yet. Where a real grounded hook exists it's used — e.g. CI/CD is anchored to this vault's own GitHub Actions deploy workflow. DevOps is intensely hands-on, so the honest next step for these pillars is to *do* them (a real pipeline, a `terraform apply`, a k8s cluster), not just read them.
- Two roadmap.sh DevOps topics live elsewhere in the vault and are cross-linked rather than duplicated: **version control** → the top-level [[git/git-reference|git/]] domain, and **a programming language for automation** → [[languages/README|languages/]].

## Reading order

1. [[devops/01-linux/README|01-linux/]] — **[Beginner → Advanced]** — Linux fundamentals (filesystem, users, processes, services, networking, SSH) through to the RHCSA cert track
2. [[devops/02-docker/README|02-docker/]] — **[Intermediate]** — containers: the big picture, networking, volumes, multi-stage builds
3. [[devops/03-cloud/README|03-cloud/]] — **[Intermediate]** — cloud provider fundamentals: the AWS/Azure/GCP landscape, core service categories, serverless, and cloud design patterns
4. [[devops/04-vps/vps-setup|04-vps/]] — **[Intermediate]** — deploying to a real Linux VPS, the practical capstone of the first three
5. [[devops/05-orchestration/README|05-orchestration/]] — **[Advanced]** — Kubernetes and the container-orchestration landscape (Swarm, managed k8s, OpenShift)
6. [[devops/06-ci-cd/README|06-ci-cd/]] — **[Intermediate → Advanced]** — continuous integration/delivery: concepts, and the tooling (GitHub Actions, Jenkins, GitLab CI)
7. [[devops/07-infrastructure-as-code/README|07-infrastructure-as-code/]] — **[Advanced]** — provisioning (Terraform, Pulumi, CloudFormation) and configuration management (Ansible, Chef, Puppet)
8. [[devops/08-networking-and-web/README|08-networking-and-web/]] — **[Intermediate]** — networking & protocols (OSI, DNS, HTTP/S, TLS, SSH) and web servers/proxies (Nginx, load balancers, caching)
9. [[devops/09-secret-management/README|09-secret-management/]] — **[Advanced]** — secrets out of git: Vault, SOPS, Sealed Secrets, cloud KMS
10. [[devops/10-observability/README|10-observability/]] — **[Advanced]** — the three pillars (metrics, logs, traces), SLIs/SLOs, and the stack (Prometheus, Grafana, ELK, OpenTelemetry)
11. [[devops/11-delivery-and-advanced/README|11-delivery-and-advanced/]] — **[Advanced]** — GitOps (ArgoCD/FluxCD), artifact management, service mesh, cloud design patterns

## Also in this folder (not part of the numbered sequence)

- [[devops-reference|devops-reference]] — a full concept-first reference across the whole devops landscape, meant for lookup
- [[minio-guide|minio-guide]] — a specific self-hosted object storage guide

## Related
- [[git/git-reference|git/]] — version control, the roadmap's VCS pillar
- [[languages/README|languages/]] — a programming language for automation/tooling
- [[foundations/dsa/README|DSA fundamentals]]
