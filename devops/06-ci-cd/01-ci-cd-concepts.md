# CI/CD Concepts

**[reference]** — the concepts; the [[devops/06-ci-cd/02-ci-cd-tools|tools note]] grounds them in this vault's real GitHub Actions pipeline.

## The three terms, precisely

They get blurred constantly; the distinctions matter:

- **Continuous Integration (CI)** — every change is merged to the mainline frequently (at least daily), and each merge automatically triggers a build + test run. The goal is to catch integration problems in *minutes*, when they're cheap, instead of at a giant painful merge weeks later. CI is fundamentally a *practice* (integrate often), enabled by *automation* (build/test on every push).
- **Continuous Delivery (CD)** — every change that passes CI is automatically built into a deployable artifact and pushed to a staging environment, so it's *always ready to release* at the click of a button. The release itself is a human decision.
- **Continuous Deployment (also CD)** — goes one step further: every change that passes the pipeline is deployed to **production automatically**, no human gate. Requires deep confidence in your automated tests.

```
Continuous Integration:  push → build → test                        (always integrated)
Continuous Delivery:     push → build → test → deploy to staging → [manual approve] → prod
Continuous Deployment:   push → build → test → deploy to staging → deploy to prod   (no gate)
```

## The anatomy of a pipeline

A pipeline is an automated sequence of **stages**, each with **steps**, triggered by an event (usually a push or PR). A typical shape:

```
trigger (push/PR)
  └─► build      — compile, produce an artifact (a jar, a container image)
  └─► test       — unit tests, then integration tests (the quality GATE)
  └─► scan       — lint, security/dependency scan, license check
  └─► package    — build + tag the container image, push to a registry
  └─► deploy     — to staging, then (gated or not) to production
```

Key concepts embedded there:

- **Gates** — a stage that must pass for the pipeline to continue. Failing tests stop the pipeline and (ideally) block the merge. This is why [[languages/01-java/03-tooling/04-testing|automated tests]] are the backbone of CI — they're the gate.
- **Artifacts** — the build output passed between stages and stored (a jar, an image). Built once, promoted through environments unchanged — you deploy the *same* artifact to staging and prod, never rebuild per environment ([[devops/11-delivery-and-advanced/02-artifact-management|Artifact Management]]).
- **Runners / agents** — the machines that execute the pipeline steps (ephemeral VMs or containers).
- **Environments** — staging, prod, etc., often with their own approval rules and secrets.

## The principles that make it work

- **Fast feedback** — a pipeline that takes an hour is a pipeline people route around. Keep the common path fast: run quick unit tests first (fail fast), push slow e2e/load tests later or nightly. This mirrors the [[languages/01-java/03-tooling/04-testing|test-pyramid]] logic — cheap tests early, expensive tests rarely.
- **Build once, promote the artifact** — never rebuild between staging and prod; deploy the identical, tested artifact, or you're not actually testing what ships.
- **Fail fast and loudly** — a broken build must stop the line and be visible, or "green" stops meaning anything.
- **Everything in version control** — the pipeline definition itself is code (a YAML file in the repo), reviewed and versioned like everything else ("pipeline as code").
- **Idempotent, repeatable deploys** — running the deploy twice yields the same result; this is where CI/CD meets [[devops/07-infrastructure-as-code/README|Infrastructure as Code]] (pipelines run `terraform apply` / `ansible-playbook`) and [[devops/11-delivery-and-advanced/01-gitops|GitOps]].

## Deployment strategies

How the deploy stage rolls out a new version without breaking users:

- **Rolling** — replace instances a few at a time (the k8s Deployment default). Simple, no extra capacity, but two versions run at once mid-rollout.
- **Blue-green** — stand up the new version (green) alongside the old (blue), switch all traffic at once, keep blue as instant rollback. Costs double capacity briefly.
- **Canary** — send a small % of traffic to the new version, watch metrics, then ramp up (or roll back). The safest for risky changes; needs good [[devops/10-observability/README|observability]] to judge the canary.

All three (plus *recreate*, the crude one) are covered properly — with the tradeoffs that pick between them — in [[devops/06-ci-cd/09-cd-and-deployment|CD, Deployment Strategies and Releases]].

## Related
- [[devops/06-ci-cd/02-ci-cd-tools|CI/CD Tools]] — these concepts in a real GitHub Actions pipeline
- [[devops/06-ci-cd/08-ci-pipelines|CI Pipelines]] — the stages above, built for real
- [[languages/01-java/03-tooling/04-testing|Testing (Java)]] — the gate at the center of CI
- [[devops/07-infrastructure-as-code/README|Infrastructure as Code]] — what the deploy stage often invokes
- [[devops/11-delivery-and-advanced/01-gitops|GitOps]] — a git-driven model for the CD half
