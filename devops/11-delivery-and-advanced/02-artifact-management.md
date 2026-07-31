# Artifact Management

**[reference]** — from roadmap.sh and vendor docs.

## What an artifact is

An **artifact** is a build output — the packaged, deployable result of your CI pipeline: a container image, a `.jar`/`.war`, an npm/PyPI package, a compiled binary, a Helm chart. The [[devops/06-ci-cd/01-ci-cd-concepts|CI/CD principle "build once, promote the artifact"]] only works if there's somewhere to *store* that one build and pull it into each environment — that somewhere is an artifact repository.

## Why a dedicated repository

- **Single source of built software** — the exact, immutable artifact that passed tests is what deploys to staging and prod; you never rebuild per environment.
- **Versioning & immutability** — artifacts are versioned and (ideally) immutable, so `myapp:1.4.0` always means the same bytes. Overwriting a published version is how "works in staging, breaks in prod" mysteries happen.
- **Caching proxy** — repository managers proxy public registries (Docker Hub, Maven Central, npm), caching dependencies so builds are faster and survive an upstream outage or a deleted package.
- **Access control & scanning** — private artifacts stay private, and the repo can scan for known vulnerabilities and enforce license/policy gates before an artifact is allowed to ship (supply-chain security).

## Container registries

The most common artifact today is the container image, stored in a **registry**:

- **Docker Hub** — the public default.
- **Cloud registries** — AWS ECR, Google Artifact Registry, Azure ACR — integrated with each cloud's IAM and k8s.
- **GitHub/GitLab registries** — bundled with the CI, so the image lives next to the code and pipeline.

`docker push`/`pull` (or the [[devops/05-orchestration/01-kubernetes|Kubernetes]] node pulling an image) talks to a registry; tags (`:1.4.0`, `:latest`) name versions. Immutable, digest-pinned tags (`@sha256:...`) are the safe way to reference exactly one image in production.

## Repository managers (multi-format)

| Tool | Note |
|---|---|
| **JFrog Artifactory** | the enterprise standard; universal (Docker, Maven, npm, PyPI, …) with strong access control and replication |
| **Sonatype Nexus** | the popular open-source/free alternative; multi-format repository manager |
| **Cloudsmith** | a hosted, cloud-native package/artifact platform |

These sit between your builds and both public registries and your deploys: your CI publishes built artifacts here and pulls dependencies through here, giving you one governed, cached, access-controlled software supply line.

## The supply-chain angle

Artifact management is increasingly a **security** topic, not just storage. Knowing exactly what's in a build (an SBOM — software bill of materials), scanning artifacts for vulnerabilities, and signing them (Sigstore/cosign) so you can verify an image wasn't tampered with are now standard concerns — a reaction to supply-chain attacks where compromised dependencies or images poison everyone downstream (the same class of risk as the Log4Shell incident noted in [[languages/01-java/03-tooling/05-logging-and-observability|logging]]).

## Related
- [[devops/06-ci-cd/README|CI/CD]] — produces the artifacts stored here
- [[devops/05-orchestration/01-kubernetes|Kubernetes]] — pulls images from a registry
- [[languages/01-java/03-tooling/01-build-tools|Build Tools]] — (in the Java domain) publishing built jars
