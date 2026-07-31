# 07 — Infrastructure as Code

Managing servers, networks, and cloud resources through version-controlled code instead of clicking around a console. Two related but distinct disciplines: **provisioning** (creating the infrastructure) and **configuration management** (setting up what runs on it). Part of the [[devops/README|DevOps curriculum]].

**[reference]** — covered from roadmap.sh and primary docs; the honest next step is a real `terraform apply` against a throwaway cloud account.

## Reading order

1. [[devops/07-infrastructure-as-code/01-provisioning-and-terraform|Provisioning & Terraform]] — **[Advanced]** — the IaC model (declarative, idempotent, stateful), Terraform in depth, and the Pulumi / CloudFormation / CDK landscape
2. [[devops/07-infrastructure-as-code/02-configuration-management|Configuration Management]] — **[Advanced]** — Ansible in depth, the Chef / Puppet / Salt landscape, and the provisioning-vs-configuration distinction

## Related
- [[devops/03-cloud/README|Cloud]] — what provisioning tools create
- [[devops/06-ci-cd/README|CI/CD]] — where IaC actually runs in a pipeline
- [[devops/09-secret-management/README|Secret Management]] — IaC must never hardcode secrets
- [[devops/README|DevOps curriculum map]]
