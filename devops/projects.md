# DevOps — Projects

*The vault's second-largest domain (~148,000 words) and its largest **reference-to-reps gap** — you haven't run Kubernetes, Terraform or Prometheus in anger. This is the section where doing matters most, and every project produces something you can point at.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## The ladder

- 🟢 ⭐ **Containerize + deploy one of your apps end to end** — multi-stage [[devops/02-docker/README|Dockerfile]], docker-compose for local, then deploy to a [[devops/04-vps/vps-setup|VPS]] behind [[devops/08-networking-and-web/02-web-servers-and-proxies|Nginx]] with Let's Encrypt TLS. The practical capstone.
- 🟡 **A real CI/CD pipeline** — extend beyond this vault's deploy workflow: a [[devops/06-ci-cd/README|GitHub Actions]] pipeline for one of your apps that runs typecheck/lint/tests on PRs and deploys on merge, with a build-once-promote-artifact flow.
- 🟡 **Local Kubernetes deploy** — stand up a `kind`/`minikube` cluster, write the [[devops/05-orchestration/01-kubernetes|Deployment/Service/Ingress]] manifests, deploy a containerized app with health probes, and do a rolling update + rollback. Makes the biggest reference gap concrete.
- 🟡 **Terraform a small cloud setup** — provision a VM + network + managed DB on a throwaway cloud account with [[devops/07-infrastructure-as-code/01-provisioning-and-terraform|Terraform]], read the `plan`, `apply`, then `destroy`. Learn state the safe way.
- 🔴 **Observability stack** — instrument an app with metrics, run [[devops/10-observability/README|Prometheus + Grafana]] (+ Loki for logs), build a dashboard and an alert on an SLO. The "you can't operate what you can't see" lesson, hands-on.
- 🟢 **Secrets, done right** — take an app with a committed `.env` and move it to [[devops/09-secret-management/01-secret-management|SOPS or Vault]]; wire it into the deploy.


## Added reps — the operational ones

- 🟡 **Break something on purpose, then write the postmortem** — take down one of your own deployed services (fill a disk, exhaust connections, OOM a container), fix it, and write a blameless postmortem with a timeline. **Done when:** the postmortem names a systemic cause, not a person. Exercises: [[devops/12-sre-and-platform-engineering/README|SRE]].
- 🟡 **Define an SLO and burn its error budget** — pick a real service, define an availability or latency SLO, and alert on the burn rate rather than on raw errors. **Done when:** you've deliberately burned budget and the alert fired at the right time.
- 🟢 **Restore from a backup you've never tested** — back up a real database, then restore it into a fresh environment. **Done when:** the restore works and you know your actual RTO. **Untested backups are the most common operational lie in software.**


## If you only do one

**Containerize and deploy one app end to end.** It's the shortest path from reference knowledge to a running thing with a URL, and every other project here builds on having done it once.


## Related

- [[devops/README|the devops course]] · [[devops/interview/README|interview bank]]
- [[devops/01-linux/15-rhcsa/15-practice-exercises|RHCSA exercises]] — the Linux fundamentals drill
- [[project-ideas|Project Ideas]] — the vault-wide index
