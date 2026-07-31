# 06 — CI/CD

Continuous Integration and Continuous Delivery/Deployment: automatically building, testing, and shipping code on every change, so integration problems surface in minutes instead of at a painful merge weeks later. Part of the [[devops/README|DevOps curriculum]].

Partly grounded: this vault deploys itself via a GitHub Actions workflow, which the tools note dissects as a real example. The tool comparisons beyond that are `[reference]`.

## Reading order

1. [[devops/06-ci-cd/01-ci-cd-concepts|CI/CD Concepts]] — **[Intermediate]** — CI vs CD vs continuous deployment, the anatomy of a pipeline (stages, gates, artifacts), and the principles that make it work
2. [[devops/06-ci-cd/02-ci-cd-tools|CI/CD Tools]] — **[Intermediate → Advanced]** — GitHub Actions dissected via this vault's own deploy pipeline, plus the Jenkins / GitLab CI / CircleCI landscape

## Related
- [[git/github-actions-cicd-reference|GitHub Actions reference (git/)]] — the existing hands-on GitHub Actions notes this section builds on
- [[devops/07-infrastructure-as-code/README|Infrastructure as Code]] — pipelines often run `terraform apply` / `ansible-playbook`
- [[languages/01-java/03-tooling/04-testing|Testing (Java)]] — the test gates a CI pipeline enforces
- [[devops/README|DevOps curriculum map]]
