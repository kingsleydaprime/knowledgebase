---
id: b19cdb23-4296-45c2-b47a-2383a5f73e96
---

# Artifact Management

An artifact is the finished, packaged result of a build, such as a container image or an app package, ready to deploy. Artifact management is storing those packages in one place with clear version numbers. That way the exact package that passed the tests is the one that goes live.

## What an artifact is
<!-- bite: 46b112ef-219f-4069-9fd9-b7049fbdc2f8 -->

An **artifact** is a build output — the packaged, deployable result of your CI pipeline: a container image, a `.jar`/`.war`, an npm/PyPI package, a compiled binary, a Helm chart. The [[devops/05-ci-cd/01-ci-cd-concepts|CI/CD principle "build once, promote the artifact"]] only works if there's somewhere to *store* that one build and pull it into each environment — that somewhere is an artifact repository.

## Why a dedicated repository
<!-- bite: f67dcbbe-bea3-4332-97fe-081445f2e9a3 -->

- **Single source of built software** — the exact, immutable artifact that passed tests is what deploys to staging and prod; you never rebuild per environment.
- **Versioning & immutability** — artifacts are versioned and (ideally) immutable, so `myapp:1.4.0` always means the same bytes. Overwriting a published version is how "works in staging, breaks in prod" mysteries happen.
- **Caching proxy** — repository managers proxy public registries (Docker Hub, Maven Central, npm), caching dependencies so builds are faster and survive an upstream outage or a deleted package.
- **Access control & scanning** — private artifacts stay private, and the repo can scan for known vulnerabilities and enforce license/policy gates before an artifact is allowed to ship (supply-chain security).

## Container registries
<!-- bite: 4dec1a87-8c89-44f9-b91a-303ad9920a77 -->

The most common artifact today is the container image, stored in a **registry**:

- **Docker Hub** — the public default.
- **Cloud registries** — AWS ECR, Google Artifact Registry, Azure ACR — integrated with each cloud's IAM and k8s.
- **GitHub/GitLab registries** — bundled with the CI, so the image lives next to the code and pipeline.

`docker push`/`pull` (or the [[devops/10-orchestration/01-kubernetes|Kubernetes]] node pulling an image) talks to a registry; tags (`:1.4.0`, `:latest`) name versions. Immutable, digest-pinned tags (`@sha256:...`) are the safe way to reference exactly one image in production.

## Repository managers (multi-format)
<!-- bite: 436c4fdf-02da-4131-ab2f-7eedd8a381f0 -->

| Tool | Note |
|---|---|
| **JFrog Artifactory** | the enterprise standard; universal (Docker, Maven, npm, PyPI, …) with strong access control and replication |
| **Sonatype Nexus** | the popular open-source/free alternative; multi-format repository manager |
| **Cloudsmith** | a hosted, cloud-native package/artifact platform |

These sit between your builds and both public registries and your deploys: your CI publishes built artifacts here and pulls dependencies through here, giving you one governed, cached, access-controlled software supply line.

## The supply-chain angle
<!-- bite: 9996647c-a013-428d-868f-77de044e8746 -->

Artifact management is increasingly a **security** topic, not just storage. Knowing exactly what's in a build (an SBOM — software bill of materials), scanning artifacts for vulnerabilities, and signing them (Sigstore/cosign) so you can verify an image wasn't tampered with are now standard concerns — a reaction to supply-chain attacks where compromised dependencies or images poison everyone downstream (the same class of risk as the Log4Shell incident noted in [[languages/01-java/03-tooling/05-logging-and-observability|logging]]).

## Related
<!-- bite: f66f57bb-ad6c-4d4d-8d7f-21b9f22e8850 -->
- [[devops/05-ci-cd/index|CI/CD]] — produces the artifacts stored here
- [[devops/10-orchestration/01-kubernetes|Kubernetes]] — pulls images from a registry
- [[languages/01-java/03-tooling/01-build-tools|Build Tools]] — (in the Java domain) publishing built jars

## About this lesson
<!-- bite: c07fba93-09a3-45fd-90ec-f0bffd44f32c -->

**Level:** reference. **Covers:** from roadmap.sh and vendor docs.
