# Container and Kubernetes Security

**[Advanced]** — the extra attack surface that containers and orchestration add, layer by layer, and why the defaults are not safe.

## The kid version first

Containers package an app with its dependencies so it runs anywhere; Kubernetes runs thousands of them across a cluster. Both are enormously useful and both **ship with insecure defaults** — a container runs as root unless told otherwise, one compromised container can often reach every other, and Kubernetes' own secrets are barely protected. Securing them means knowing each layer's traps: the **image**, the **container at runtime**, and the **cluster** around it.

## The layers

Container security stacks, and a weakness at any layer undermines the ones above → [[devops/02-docker/README|Docker]], [[devops/05-orchestration/README|Kubernetes]]:

```
   CLUSTER      Kubernetes RBAC, secrets, network policies, the API server
   RUNTIME      how the container actually runs — user, capabilities, isolation
   IMAGE        what's inside — dependencies, base image, baked-in secrets
   HOST         the node's OS (this is [[devops/01-linux/README|Linux hardening]])
```

## Image security — what's inside the box

An image is a filesystem plus metadata, and it's only as safe as its contents:

- **Vulnerable dependencies** — the app's libraries and the base image's packages carry known CVEs. **Scan every image** (Trivy, Grype, Snyk) in the build pipeline, and fail the build on critical findings → [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|vulnerable components]]
- **Minimal base images** — `alpine`, `distroless`, or scratch. **A smaller image has less to exploit** — no shell, no package manager, no extra binaries for an attacker to use → [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|living off the land]]. A `distroless` image with no shell defeats a lot of post-exploitation
- **No baked-in secrets** — a secret added in one layer stays in the image history even if a later layer deletes it. **Inject secrets at runtime, never build them in** → [[cybersecurity/09-cloud-security/03-the-cloud-attack-surface|exposed secrets]]
- **Trusted, signed images** — pull from trusted registries, pin by digest not by mutable tag, and verify signatures (Sigstore/cosign) so you run the image you think you're running → **supply-chain security**
- **The supply chain** — a compromised base image or a malicious dependency runs with your container's privileges. SBOMs (software bills of materials) and provenance attestation are the emerging answer

## Runtime security — how it actually runs

The container process on the node, and the defaults are the danger:

- **Don't run as root.** A container running as root that escapes its isolation is root *on the host*. Set a non-root `USER`; enforce it with a policy so nobody forgets → **the single highest-value container-runtime control**
- **Drop Linux capabilities.** Containers get a default set of kernel capabilities; most workloads need almost none. Drop `ALL` and add back only what's required → [[foundations/os/README|OS capabilities]]
- **Read-only root filesystem** where possible — malware can't write a payload to a filesystem it can't modify
- **No privileged containers.** `--privileged` disables most isolation and is a near-guaranteed host takeover if compromised. Ban it
- **Resource limits** — CPU/memory limits so one container can't starve the node (a container-level [[cybersecurity/14-api-security/05-rate-limiting-and-abuse|resource-exhaustion]] defence)
- **Runtime detection** — tools like Falco watch for anomalous container behaviour (a shell spawned in a container that should never spawn one, unexpected network connections) → [[cybersecurity/07-security-operations/README|detection]]

**The container is not a security boundary as strong as a VM.** It shares the host kernel, so a kernel exploit escapes it. For hostile multi-tenant workloads, stronger isolation (gVisor, Kata Containers, Firecracker microVMs) is warranted → [[foundations/os/11-isolation-and-containers|isolation]].

## Kubernetes security — the cluster

Kubernetes adds a control plane and networking, each with its own traps:

- **RBAC — least privilege for the cluster.** Kubernetes RBAC governs who (users and service accounts) can do what to which resources. **The defaults are often too broad**; a compromised pod's service-account token can, with loose RBAC, control the cluster. Scope it tightly → [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|least privilege]]
- **Secrets are barely secret.** Native Kubernetes `Secret` objects are only **base64-encoded, not encrypted** — anyone with read access (or etcd access) sees them in plaintext. Enable encryption-at-rest for etcd, and use a real secrets manager (Vault, Sealed Secrets, cloud secret stores + CSI driver) → [[devops/09-secret-management/01-secret-management|secret management]]
- **Network policies — segment the cluster.** By default, **every pod can talk to every other pod.** A compromised pod reaches the whole cluster. Network policies enforce which pods may communicate, containing a breach — the [[cybersecurity/03-network-security/02-network-segmentation|segmentation]] principle applied inside the cluster
- **Admission controllers** — policy checks at deploy time that *reject* non-compliant workloads (no root, no privileged, only signed images). OPA Gatekeeper and Kyverno are the standard — **policy-as-code that stops the misconfiguration before it runs** → [[cybersecurity/09-cloud-security/05-cloud-native-defence|policy as code]]
- **Protect the API server and etcd** — the cluster's brain and its database. Exposed or weakly-authenticated, they're total cluster compromise. Restrict access, require strong auth, encrypt etcd
- **Pod Security Standards** — the built-in baseline/restricted profiles that enforce the runtime rules above cluster-wide

## The through-line

Every item is the same instinct — **minimise privilege and blast radius at each layer**: minimal images (less to exploit), non-root drop-capabilities runtime (a compromise gains little), tight RBAC and network policies (a compromise spreads to nothing), admission control (the misconfiguration never deploys). It's [[cybersecurity/07-security-operations/01-defensive-architecture|defence-in-depth]] expressed as container configuration, and the defaults work against you at every layer, so it's opt-in.

## Key insight

**Containers and Kubernetes add three layers of attack surface — image, runtime, cluster — and every layer's defaults are insecure: containers run as root, pods can reach every other pod, and Kubernetes secrets are just base64.** Security is therefore opt-in, layer by layer, all following one instinct: minimise privilege and blast radius, so a compromise at any layer gains little and spreads to nothing. And remember the container itself is a weaker boundary than a VM — it shares the host kernel — so genuinely hostile workloads need stronger isolation, not just careful config.

## Related
- [[devops/02-docker/README|Docker]] · [[devops/05-orchestration/README|Kubernetes]] — the mechanics being secured
- [[foundations/os/11-isolation-and-containers|isolation and containers]] — namespaces, cgroups, the kernel boundary
- [[cybersecurity/09-cloud-security/05-cloud-native-defence|cloud-native defence]] — scanning and policy-as-code
- [[cybersecurity/03-network-security/02-network-segmentation|network segmentation]] — the network-policy principle

*Source: [reference] — Aug 2026.*
