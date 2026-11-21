---
id: f48977ef-85d6-43c8-85b1-d492adaadd0e
---

# GitOps

**[reference]** — from roadmap.sh and the Argo/Flux docs.

## The idea
<!-- bite: 363790ea-4faa-49b7-b3e3-9879c65b7c57 -->

GitOps applies the [[devops/09-infrastructure-as-code/index|Infrastructure as Code]] philosophy to *deployment*: **git is the single source of truth for the desired state of your running system**, and an automated agent continuously makes the live environment match what's in git. You don't `kubectl apply` or run deploy scripts by hand — you open a pull request that changes a manifest, merge it, and an operator reconciles the cluster to match.

The four principles:

1. **Declarative** — the entire system state is described declaratively (k8s manifests, Helm charts, Kustomize).
2. **Versioned & immutable** — that state lives in git, with full history and rollback (revert the commit → the system reverts).
3. **Pulled automatically** — an agent *in the cluster* pulls approved changes from git.
4. **Continuously reconciled** — the agent constantly compares desired (git) vs actual (cluster) and corrects drift — if someone hand-edits the cluster, it's reverted back to git's state.

## Pull vs push delivery
<!-- bite: 43f265c4-88e9-4101-b3ce-4209baa00037 -->

This is the key distinction from traditional [[devops/05-ci-cd/index|CI/CD]]:

- **Push (traditional CD)** — the CI pipeline has cluster credentials and *pushes* changes in (`kubectl apply` from the pipeline). The pipeline needs powerful production access, and there's no continuous drift correction.
- **Pull (GitOps)** — an agent *inside* the cluster watches git and pulls changes in. The cluster's credentials never leave the cluster (better security posture), and drift is continuously reconciled, not just applied once.

```
Push CD:   pipeline ──(has prod creds)──► kubectl apply ──► cluster
GitOps:    git repo ◄──(watches/pulls)──── agent in cluster ──► reconciles cluster
```

A common combined pattern: CI builds and pushes the image + updates the image tag in the git manifests repo; the GitOps agent notices the git change and rolls it out. CI owns *build*, GitOps owns *deploy*.

## The tools
<!-- bite: f9708f47-b2aa-45ba-b919-dc263f6822bb -->

| Tool | Note |
|---|---|
| **Argo CD** | the popular choice; a rich UI showing sync status and diffs (desired vs live), strong multi-cluster support |
| **Flux CD** | CNCF, lightweight, GitOps-toolkit-based, controller-driven (no heavy UI) — composes well into automation |

Both do the same core loop: watch a git repo of manifests, reconcile the cluster to match, report and heal drift.

## Why it's compelling
<!-- bite: 4337c1ea-e733-4f9c-b30a-cc033c9de124 -->

- **Git is the audit log and the rollback button** — every change is a reviewed, reverted-able commit; "what's running in prod" is exactly "what's in this git repo."
- **Least-privilege deploys** — no external system holds standing production credentials.
- **Self-healing against drift** — manual changes don't stick, which kills configuration drift.

The catch it forces you to solve: **secrets can't sit in plaintext in the git repo** — which is exactly why Sealed Secrets / SOPS / External Secrets exist ([[devops/06-secret-management/01-secret-management|Secret Management]]).

## Related
<!-- bite: da373432-eb3e-4d21-ba50-eb4f5740df90 -->
- [[devops/09-infrastructure-as-code/index|Infrastructure as Code]] — the same declarative philosophy applied to provisioning
- [[devops/05-ci-cd/index|CI/CD]] — GitOps is the delivery half; CI builds the artifact
- [[devops/10-orchestration/01-kubernetes|Kubernetes]] — what GitOps agents reconcile
- [[devops/06-secret-management/01-secret-management|Secret Management]] — solving "secrets in git"
