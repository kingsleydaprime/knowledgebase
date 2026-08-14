# 06 — CI/CD

Continuous Integration and Continuous Delivery/Deployment: automatically building, testing, and shipping code on every change, so integration problems surface in minutes instead of at a painful merge weeks later. Part of the [[devops/README|DevOps curriculum]].

**~9,000 words across 12 notes.** This section was a 142-line stub until August 2026, while 2,776 lines of GitHub Actions material sat in `git/` — the wrong folder, since Actions is CI/CD rather than version control. That material was moved here and split into notes 03–12; `git/` keeps version control.

**Grounding:** this vault deploys itself via a GitHub Actions workflow (`.github/workflows/deploy.yml`), which note 02 dissects line by line. Notes 03–12 come from real pipeline work on production deployments. The competing-tools comparison in note 02 is `[reference]`.

## Reading order

**The model**

1. [[devops/06-ci-cd/01-ci-cd-concepts|CI/CD Concepts]] — **[Intermediate]** — CI vs CD vs continuous deployment, the anatomy of a pipeline (stages, gates, artifacts), and the principles that make it work. Vendor-neutral
2. [[devops/06-ci-cd/02-ci-cd-tools|CI/CD Tools]] — **[Intermediate → Advanced]** — GitHub Actions dissected via this vault's own deploy pipeline, plus the Jenkins / GitLab CI / CircleCI landscape

**GitHub Actions in depth**

3. [[devops/06-ci-cd/03-github-actions-fundamentals|Fundamentals]] — **[Intermediate]** — workflow → job → step → action, where files live, the execution flow, and the complete top-level YAML including concurrency and permissions
4. [[devops/06-ci-cd/04-triggers-jobs-and-runners|Triggers, Jobs and Runners]] — **[Intermediate]** — `on:` in full, job and step structure, `run` vs `uses`, outputs, fan-out/fan-in, and the machines it all runs on
5. [[devops/06-ci-cd/05-contexts-secrets-and-environments|Contexts, Secrets and Environments]] — **[Intermediate]** — the context objects, expression functions, and how secrets and environments are scoped
6. [[devops/06-ci-cd/06-caching-artifacts-and-matrix|Caching, Artifacts and Matrix Builds]] — **[Intermediate]** — the three things that make a pipeline fast and broad
7. [[devops/06-ci-cd/07-reusable-workflows-and-actions|Reusable Workflows and Composite Actions]] — **[Intermediate → Advanced]** — how to stop copy-pasting YAML across repos

**Building real pipelines**

8. [[devops/06-ci-cd/08-ci-pipelines|CI Pipelines]] — **[Intermediate]** — a complete build, worked through in Node/NestJS and Java/Spring Boot
9. [[devops/06-ci-cd/09-cd-and-deployment|CD, Deployment Strategies and Releases]] — **[Intermediate → Advanced]** — deploy structure and rollback, recreate/rolling/blue-green/canary in depth, and automated releases
10. [[devops/06-ci-cd/10-pipeline-security|Securing the Pipeline]] — **[Intermediate → Advanced]** — your CI system holds production credentials and runs third-party code. Least privilege, OIDC, dependency scanning, supply-chain hardening
11. [[devops/06-ci-cd/11-real-world-pipelines|Real-World Pipelines, End to End]] — **[Advanced]** — two complete production pipelines, top to bottom
12. [[devops/06-ci-cd/12-troubleshooting-workflows|Troubleshooting Workflows]] — **[Reference]** — debug logging, tmate SSH into a runner, the errors you'll actually hit

## Where this borders other domains

CI/CD sits between several things and it's easy to duplicate them here. Deliberately kept elsewhere:

- **Branching strategies, branch protection, PR practice, semantic versioning** → [[git/README|the git course]]. A pipeline enforces these rules; it doesn't define them. Specifically [[git/13-branching-strategies|13-branching-strategies]] and [[git/14-github-and-ci|14-github-and-ci]]
- **The deploy targets** → [[devops/02-docker/README|Docker]], [[devops/05-orchestration/README|Orchestration]], [[devops/04-vps/vps-deployment-reference|VPS]]
- **What the deploy stage invokes** → [[devops/07-infrastructure-as-code/README|Infrastructure as Code]]
- **The pull-based alternative** → [[devops/11-delivery-and-advanced/01-gitops|GitOps]], where the cluster reconciles itself from git instead of CI pushing to it

## Related
- [[devops/README|DevOps curriculum map]]
- [[git/README|Git course]] — version control, the roadmap's VCS pillar
- [[languages/01-java/03-tooling/04-testing|Testing (Java)]] — the test gates a CI pipeline enforces
- [[devops/10-observability/README|Observability]] — how you know a deploy went well
