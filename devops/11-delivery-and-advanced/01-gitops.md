# GitOps

**[reference]** — from roadmap.sh and the Argo/Flux docs.

## The idea

GitOps applies the [[devops/07-infrastructure-as-code/README|Infrastructure as Code]] philosophy to *deployment*: **git is the single source of truth for the desired state of your running system**, and an automated agent continuously makes the live environment match what's in git. You don't `kubectl apply` or run deploy scripts by hand — you open a pull request that changes a manifest, merge it, and an operator reconciles the cluster to match.

The four principles:

1. **Declarative** — the entire system state is described declaratively (k8s manifests, Helm charts, Kustomize).
2. **Versioned & immutable** — that state lives in git, with full history and rollback (revert the commit → the system reverts).
3. **Pulled automatically** — an agent *in the cluster* pulls approved changes from git.
4. **Continuously reconciled** — the agent constantly compares desired (git) vs actual (cluster) and corrects drift — if someone hand-edits the cluster, it's reverted back to git's state.

## Pull vs push delivery

This is the key distinction from traditional [[devops/06-ci-cd/README|CI/CD]]:

- **Push (traditional CD)** — the CI pipeline has cluster credentials and *pushes* changes in (`kubectl apply` from the pipeline). The pipeline needs powerful production access, and there's no continuous drift correction.
- **Pull (GitOps)** — an agent *inside* the cluster watches git and pulls changes in. The cluster's credentials never leave the cluster (better security posture), and drift is continuously reconciled, not just applied once.

```
Push CD:   pipeline ──(has prod creds)──► kubectl apply ──► cluster
GitOps:    git repo ◄──(watches/pulls)──── agent in cluster ──► reconciles cluster
```

A common combined pattern: CI builds and pushes the image + updates the image tag in the git manifests repo; the GitOps agent notices the git change and rolls it out. CI owns *build*, GitOps owns *deploy*.

## The tools

| Tool | Note |
|---|---|
| **Argo CD** | the popular choice; a rich UI showing sync status and diffs (desired vs live), strong multi-cluster support |
| **Flux CD** | CNCF, lightweight, GitOps-toolkit-based, controller-driven (no heavy UI) — composes well into automation |

Both do the same core loop: watch a git repo of manifests, reconcile the cluster to match, report and heal drift.

## Why it's compelling

- **Git is the audit log and the rollback button** — every change is a reviewed, reverted-able commit; "what's running in prod" is exactly "what's in this git repo."
- **Least-privilege deploys** — no external system holds standing production credentials.
- **Self-healing against drift** — manual changes don't stick, which kills configuration drift.

The catch it forces you to solve: **secrets can't sit in plaintext in the git repo** — which is exactly why Sealed Secrets / SOPS / External Secrets exist ([[devops/09-secret-management/01-secret-management|Secret Management]]).

## Related
- [[devops/07-infrastructure-as-code/README|Infrastructure as Code]] — the same declarative philosophy applied to provisioning
- [[devops/06-ci-cd/README|CI/CD]] — GitOps is the delivery half; CI builds the artifact
- [[devops/05-orchestration/01-kubernetes|Kubernetes]] — what GitOps agents reconcile
- [[devops/09-secret-management/01-secret-management|Secret Management]] — solving "secrets in git"
