---
id: 12d85ec9-2364-44ea-bca5-915fd6bab676
---

# Container and Kubernetes Security

**A container packages an app with all it needs to run, and Kubernetes runs many of them across many machines — and both ship with insecure defaults you must lock down.**

## Before you start
<!-- bite: 85ee6a89-0612-40a0-8612-ed49868b79eb -->

You should have:

- Met least privilege and blast radius → [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|identity is the perimeter]].
- Met network segmentation → [[cybersecurity/03-network-security/02-network-segmentation|network segmentation]].
- Docker installed (you used it for Juice Shop and the ARP lab), and a terminal.

After this lesson you will be able to:

1. Name the three layers of container attack surface and why each default is insecure.
2. Harden an image: scan it, use a minimal base, keep secrets out.
3. Harden a container's runtime: non-root, dropped capabilities, read-only filesystem — and verify it.
4. Name the key Kubernetes controls (RBAC, secrets, network policies, admission control).

**Study route.** Kid version and §1–4, then the worked example: hardening and scanning a container with Docker and Trivy.

## What container and Kubernetes security is
<!-- bite: 98c7ccb7-7924-4b0a-af52-d5373017a889 -->

Most cloud apps now run in **containers** — lightweight packages of an app plus its dependencies — orchestrated by **Kubernetes** across a cluster of machines. They're enormously useful, and they add *three new layers of attack surface*, each of which ships insecure by default.

This lesson is those layers: the **image** (what's inside the box), the **container at runtime** (how it actually runs), and the **cluster** (Kubernetes around it). The defaults work against you at every one — a container runs as root unless told otherwise, one compromised pod can often reach every other, and Kubernetes' own secrets are barely protected. Security is therefore opt-in, layer by layer, all following one instinct: minimise privilege and blast radius. By the end you'll have hardened and scanned a container by hand.

## The kid version
<!-- bite: 4d9b2ef0-a929-40ba-b204-f3092cb4d655 -->

Think of shipping something fragile. A container is like a sealed box with the item and its padding inside — it travels the same everywhere, which is why containers are so popular. But imagine every box arrived with the lid unlocked, the packing slip listing the sender's home keys, and — if one box in the truck is tampered with — a secret passage to every other box. That's the state of container *defaults*: convenient, and wide open.

Securing them is checking each layer: what's *in* the box (the image), how the box *behaves* when opened (the runtime), and the *truck* carrying thousands of boxes (the cluster). You have to lock each one on purpose, because none is locked for you.

**Where the analogy stops working.** A real box, once sealed, is a solid barrier. A container is *not* as strong a wall as it looks: all the boxes share one truck engine (the host's Linux kernel), so a clever attacker who breaks the engine escapes every box at once. That's why a container is a weaker boundary than a full virtual machine, and why genuinely hostile workloads need something stronger than careful configuration.

## 1. The layers
<!-- bite: 111671ff-2348-4761-aa6c-aecfb97b2ded -->

Container security stacks, and a weakness at any layer undermines the ones above it:

![The four stacked layers of container security from top to bottom — cluster (Kubernetes RBAC, secrets, network policies), runtime (user, capabilities, privilege, filesystem), image (dependencies, base image, baked-in secrets), and host (the node's OS) — where a weakness at any layer undermines the ones above.](../images/cl-container-layers.svg)

1. **Host** — the node's own OS, which is ordinary [[devops/01-linux/index|Linux hardening]].
2. **Image** — what's inside: dependencies, the base image, anything baked in.
3. **Runtime** — how the container actually runs: its user, capabilities, privilege, filesystem.
4. **Cluster** — Kubernetes around it: RBAC, secrets, network policies, the API server.

The next three sections take the image, runtime and cluster in turn.

## 2. Image security — what's inside the box
<!-- bite: e4b38284-f856-49e9-93b0-637af31f644c -->

An image is a filesystem plus metadata, only as safe as its contents:

1. **Scan for vulnerable dependencies.** The app's libraries and the base image's packages carry known CVEs. **Scan every image** (Trivy, Grype, Snyk) in the build pipeline and fail the build on critical findings → [[cybersecurity/08-governance-risk-and-compliance/04-third-party-and-supply-chain-risk|supply-chain risk]].
2. **Use minimal base images** — `alpine`, `distroless`, or scratch. **A smaller image has less to exploit**: no shell, no package manager, no extra binaries for an attacker to use after a compromise.
3. **No baked-in secrets.** A secret added in one layer stays in the image history even if a later layer deletes it. **Inject secrets at runtime, never build them in.**
4. **Trusted, signed images** — pull from trusted registries, pin by digest not by mutable tag, and verify signatures (Sigstore/cosign) so you run the image you think you're running.

## 3. Runtime security — how it actually runs
<!-- bite: 05d3ff5f-fdcb-4eaf-90ad-1a7edbe89a6c -->

The container process on the node, where the defaults are the danger:

1. **Don't run as root.** A container running as root that escapes its isolation is root *on the host*. Set a non-root `USER` and enforce it — **the single highest-value runtime control.**
2. **Drop Linux capabilities.** Containers get a default set of kernel capabilities; most workloads need almost none. Drop `ALL` and add back only what's required.
3. **Read-only root filesystem** where possible — malware can't write a payload to a filesystem it can't modify.
4. **No privileged containers.** `--privileged` disables most isolation and is near-guaranteed host takeover if compromised. Ban it.
5. **Runtime detection** — tools like Falco watch for anomalous behaviour (a shell spawned in a container that never should, unexpected network connections) → [[cybersecurity/07-security-operations/index|detection]].

**The container is not as strong a boundary as a VM** — it shares the host kernel, so a kernel exploit escapes it. For genuinely hostile multi-tenant workloads, stronger isolation (gVisor, Kata Containers, Firecracker) is warranted.

## 4. Kubernetes security — the cluster
<!-- bite: f229d1e3-746e-4eda-be1a-9188847a835b -->

Kubernetes adds a control plane and networking, each with its own traps:

1. **RBAC — least privilege for the cluster.** It governs who (users and service accounts) can do what. **Defaults are often too broad**; a compromised pod's service-account token can, with loose RBAC, control the cluster. Scope it tightly.
2. **Secrets are barely secret.** Native Kubernetes `Secret` objects are only **base64-encoded, not encrypted** — anyone with read (or etcd) access sees them in plaintext. Enable encryption-at-rest for etcd and use a real secrets manager (Vault, Sealed Secrets, a cloud store + CSI driver).
3. **Network policies — segment the cluster.** By default **every pod can talk to every other pod**, so one compromise reaches everything. Network policies enforce which pods may communicate — [[cybersecurity/03-network-security/02-network-segmentation|segmentation]] inside the cluster.
4. **Admission controllers** — deploy-time policy checks that *reject* non-compliant workloads (no root, no privileged, only signed images). OPA Gatekeeper and Kyverno are standard — **policy-as-code that stops the misconfiguration before it runs.**
5. **Protect the API server and etcd** — the cluster's brain and database; exposed or weakly authenticated, they're total compromise.

## Terms used in this lesson
<!-- bite: 780869d4-3d7c-4fe0-9cfb-aff014a00c03 -->

1. **Container**: This is a lightweight package of an app and its dependencies that runs the same anywhere, sharing the host's kernel rather than running a full OS.
2. **Image**: This is the filesystem-plus-metadata a container is created from — its dependencies, base image, and anything baked in.
3. **Capabilities**: These are fine-grained slices of Linux root power; containers get a default set, and most workloads should drop almost all of them.
4. **Privileged container**: This is a container run with `--privileged`, which disables most isolation — a near-guaranteed host takeover if compromised, so it's banned.

## Terms used in this lesson: the cluster
<!-- bite: 98b2d634-36a7-4870-8eb0-dcb1ceb32390 -->

5. **Kubernetes**: This is the orchestrator that runs and manages many containers across a cluster of machines.
6. **RBAC (Role-Based Access Control)**: This is Kubernetes' least-privilege system for who may do what in the cluster — its defaults are often too broad.
7. **Network policy**: This is a Kubernetes rule controlling which pods may talk to which — segmentation inside the cluster, since by default every pod can reach every other.
8. **Admission controller**: This is a deploy-time check (OPA Gatekeeper, Kyverno) that rejects non-compliant workloads before they run — policy-as-code.

## Worked example — harden and scan a container
<!-- bite: 2e18dab0-e46c-4fb9-ae44-8c63e70bac3d -->

Take an insecure Dockerfile and fix it, then scan it. The insecure version — runs as root, big base, nothing dropped:

```dockerfile
# insecure
FROM node:20
COPY . /app
WORKDIR /app
RUN npm install
CMD ["node", "server.js"]
```

**Predict first:** this image runs as root on a full Debian base. If an attacker gets code execution inside the container and then finds a kernel escape, what do they become on the host — and what tools are sitting right there in the image to help them?

## Worked example: the hardened version
<!-- bite: 1098886b-e705-438d-a5fb-6bd79d6bee60 -->

They become **root on the host** (the container ran as root, so the escaped process is root), and a full `node:20` image hands them a shell, `apt`, `curl`, and compilers to pull down and build their next stage. The hardened version removes all of that:

```dockerfile
# hardened
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .

FROM gcr.io/distroless/nodejs20-debian12    # no shell, no package manager
WORKDIR /app
COPY --from=build /app /app
USER 1000                                    # non-root
CMD ["server.js"]
```

`distroless` has no shell for an attacker to use, `USER 1000` means an escape is an *unprivileged* user not root, and the multi-stage build keeps build tools out of the final image. Run it with the runtime locks too:

```bash
docker run --user 1000 --read-only --cap-drop ALL --security-opt no-new-privileges myapp
```

## Worked example: scanning the image
<!-- bite: 19ab5530-0398-4e60-9512-1834686efb9b -->

Now scan it for known-vulnerable packages with **Trivy** — this is the "scan every image" rule, runnable locally:

```bash
# Trivy runs in Docker, no install needed:
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image myapp:latest
```

A finding looks like:

```text
myapp:latest (debian 12)
Total: 3 (CRITICAL: 1)
┌───────────┬────────────────┬──────────┬───────────────┬──────────────┐
│ Library   │ Vulnerability  │ Severity │ Installed Ver │ Fixed Version│
├───────────┼────────────────┼──────────┼───────────────┼──────────────┤
│ libssl3   │ CVE-2024-xxxx  │ CRITICAL │ 3.0.11        │ 3.0.13       │
└───────────┴────────────────┴──────────┴───────────────┴──────────────┘
```

That's image scanning in one command: it found a critical CVE in a base-image package and told you the fixed version. Wired into CI, a critical finding fails the build — the misconfiguration never ships. The hardened image, being `distroless`, also has *far fewer* packages to flag than the full `node:20` one, which is the minimal-base payoff made measurable.

## Common pitfalls and traps
<!-- bite: 7527ce89-9962-49bd-b27e-b0503bc8f4d3 -->

1. **Running as root because it "just works".** An escape from a root container is root on the host. Set a non-root `USER`; it's the highest-value fix.
2. **`--privileged` for convenience.** It disables isolation and is a direct host takeover path. Never in production.
3. **Baking secrets into the image.** They persist in the layer history even after a later `RUN rm`. Inject at runtime.
4. **Trusting the container as a strong boundary.** It shares the host kernel. For hostile workloads use gVisor/Kata/microVMs, not just config.
5. **Leaving Kubernetes defaults.** Broad RBAC, base64 "secrets", and every-pod-can-reach-every-pod networking are all insecure defaults you must override.

## Check your understanding
<!-- bite: 756341bd-01ce-4bc0-91a0-8ac9530590c8 -->

Try each one before you open the answer.

1. <!-- q: mcq id="ccd2c16e" -->
   Why is "don't run the container as root" called the single highest-value container-runtime control?

   - [ ] Root containers run more slowly.
   - [x] If a root container escapes its isolation (e.g. via a kernel bug), the escaped process is root *on the host*; a non-root container limits an escape to an unprivileged user.
   - [ ] Root containers can't access the network.
   - [ ] Kubernetes refuses to run root containers.

   <details><summary>Answer</summary>

   The container shares the host kernel, so a container breakout lands the process on the host with whatever user the container ran as. Root-in-container becomes root-on-host — total compromise. Running as a non-root `USER` means a breakout is an unprivileged user, drastically limiting the damage. It's the clearest example of minimising blast radius at the runtime layer.

   </details>

2. <!-- q: mcq id="585fbbde" -->
   Native Kubernetes `Secret` objects are often described as "barely secret". Why?

   - [ ] They're stored only in the pod's memory.
   - [x] They're only base64-encoded, not encrypted — anyone with read access (or etcd access) can decode them to plaintext.
   - [ ] They're printed to the container's logs.
   - [ ] They expire after one hour.

   <details><summary>Answer</summary>

   base64 is encoding, not encryption — trivially reversible. So a native Secret is readable by anyone with read access to it or to etcd. The fixes: enable encryption-at-rest for etcd, and use a real secrets manager (Vault, Sealed Secrets, or a cloud store via the CSI driver). Assuming base64 is "secure" is a common and dangerous mistake.

   </details>

3. <!-- q: gap id="6fa187f1" answers="distroless|minimal|scratch|alpine" -->
   Using a ___ base image (one with no shell, package manager, or extra binaries) reduces the attack surface because there's far less for an attacker to use after a compromise, and fewer packages to carry known vulnerabilities.

   <details><summary>Answer</summary>

   A distroless (or minimal/scratch/alpine) base image. Less inside the box means less to exploit — no shell to spawn, no `apt` or `curl` to pull down the next stage — and fewer packages means fewer CVEs for a scanner to flag. It's the "minimise what's there" instinct applied to the image layer.

   </details>

4. <!-- q: mcq id="f185bb97" -->
   By default in Kubernetes, which statement about pod-to-pod networking is true, and what's the fix?

   - [ ] Pods can't talk to each other at all; you must open every path manually.
   - [x] Every pod can talk to every other pod, so one compromise can reach the whole cluster — network policies restrict which pods may communicate.
   - [ ] Pods can only talk within their own node; network policies remove that limit.
   - [ ] Pod networking is encrypted and isolated by default.

   <details><summary>Answer</summary>

   Kubernetes defaults to a flat network where every pod reaches every other, so a single compromised pod can move laterally across the cluster. Network policies apply the segmentation principle inside the cluster — explicitly allowing only the pod-to-pod paths that are needed, containing a breach to a small blast radius.

   </details>

5. <!-- q: mcq id="23d8d380" -->
   You add `RUN echo $API_KEY > /tmp/key` in one Dockerfile layer and `RUN rm /tmp/key` in a later one. Why is the secret still exposed?

   - [ ] The rm command doesn't work in Docker.
   - [x] Each layer is preserved in the image history; the secret remains in the earlier layer even though a later layer deletes it. Anyone with the image can extract it.
   - [ ] The secret is only exposed if the container runs as root.
   - [ ] Environment variables are always encrypted.

   <details><summary>Answer</summary>

   Docker images are layered, and every layer is kept. A secret written in one layer stays recoverable from the image history even after a later layer removes the file. The rule is to never bake secrets into images at all — inject them at runtime (env from a secret store, mounted secret, or the orchestrator's mechanism).

   </details>

6. <!-- q: open id="9293d628" -->
   Every container-security control in this lesson is described as following "one instinct". State that instinct, and show how it applies at the image, runtime, and cluster layers with one example each.

   <details><summary>Answer</summary>

   The instinct is **minimise privilege and blast radius at every layer** — assume a compromise will happen and make sure it gains as little as possible and spreads nowhere. Image layer: use a minimal/distroless base, so a compromise finds no shell or tools to use and fewer packages to exploit (less to gain). Runtime layer: run as a non-root user with dropped capabilities and a read-only filesystem, so an escape is an unprivileged process that can't even write a payload (a compromise gains little). Cluster layer: tight RBAC plus network policies, so a compromised pod's token can't control the cluster and the pod can't reach other pods (a compromise spreads to nothing). Admission control enforces all of this at deploy time so the insecure default never runs. It's defence in depth expressed as container configuration — and because the defaults are all insecure, every layer's protection is opt-in.

   </details>

## Practice — harden and scan your own container
<!-- bite: 3c63bdbb-213e-4b2f-b6b2-1e03392e2f32 -->

**Task.** Take a Dockerfile you have (or the insecure example) and harden it end to end.

1. Convert it to a multi-stage build on a minimal base (`-slim` or `distroless`), add a non-root `USER`, and keep any secret out of the image.
2. Build it, and run it with `--read-only --cap-drop ALL --security-opt no-new-privileges`.
3. Scan both the original and hardened images with Trivy; record the vulnerability counts for each and note the difference.
4. Confirm the container still works as a non-root user (fix any permission errors the hardening surfaces — those are real findings).

## Practice: when it's done
<!-- bite: 125e17f3-cf61-44e4-9e79-40bf5d2bcd7b -->

Here's how you know the task is finished.

**Done when:** your hardened image runs as non-root with dropped capabilities, carries no baked-in secret, and has a lower Trivy vulnerability count than the original — and you can explain what an attacker who broke into it can no longer do. Record the before/after counts in `cybersecurity/LIVE-RUNS-TODO.md`. Confirm Trivy's current image-scan invocation for your version.

## Before moving on
<!-- bite: 8bed7954-616a-46ce-8d20-a77f6b8e88b6 -->

You can now name the three container layers and their insecure defaults, harden an image (scan, minimal base, no secrets), harden a runtime (non-root, drop caps, read-only), and name the key Kubernetes controls.

**Recap for later lookup:** layers = host, image, runtime, cluster; every default is insecure. Image: scan (Trivy/Grype), minimal/distroless base, no baked-in secrets, signed and pinned. Runtime: non-root `USER` (highest value), drop ALL capabilities, read-only filesystem, never `--privileged`; container is a weaker boundary than a VM. Cluster: tight RBAC, real secrets (not base64), network policies (default is every-pod-to-every-pod), admission controllers as policy-as-code. One instinct throughout: minimise privilege and blast radius.

Next: [[cybersecurity/09-cloud-security/05-cloud-native-defence|cloud-native defence]] — automating all of this at scale: catching misconfigurations in the pull request, scanning production continuously, and detecting what gets through.

## Related
<!-- bite: b499bbaf-9c2c-452d-b4ff-3c51cb712096 -->

- [[devops/03-docker/index|Docker]] and [[devops/10-orchestration/index|Kubernetes]] — the mechanics being secured.
- [[cybersecurity/03-network-security/02-network-segmentation|Network segmentation]] — the principle network policies apply inside the cluster.
- [[cybersecurity/09-cloud-security/05-cloud-native-defence|Cloud-native defence]] — scanning and policy-as-code at scale.

## About this lesson
<!-- bite: 46279db0-20ab-4643-90f3-60c9c3567457 -->

**Level:** Advanced. **Covers:** the three container layers (image, runtime, cluster) and their insecure defaults, image security (scanning with Trivy, minimal base images, no baked-in secrets, signing), runtime security (non-root, dropped capabilities, read-only filesystem, no privileged), Kubernetes controls (RBAC, base64 secrets, network policies, admission control), and a hands-on harden-and-scan lab with Docker and Trivy. **Where it sits:** lesson 4 of the [[cybersecurity/09-cloud-security/index|Cloud Security]] section. **Sources:** the original vault note (from the roadmap.sh cyber-security roadmap), rebuilt to the [[COURSE-STANDARD|course standard]] with a Docker/Trivy lab, tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
