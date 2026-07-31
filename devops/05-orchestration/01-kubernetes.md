# Kubernetes

**[reference]** — from roadmap.sh and the Kubernetes docs. Not yet run against a real cluster; the honest next step is a local `kind`/`minikube`/`k3s` cluster to make this concrete.

## The problem it solves

One container on one host is easy (`docker run`). The moment you have many containers across many hosts, you inherit a pile of hard problems: which host does each container run on? What happens when a container crashes, or a host dies? How does traffic reach a container whose IP changes every restart? How do you roll out a new version without downtime, or roll back a bad one? How do you scale from 3 replicas to 30?

**Kubernetes (k8s)** is the answer that won. It's a **declarative** container orchestrator: you describe the desired state ("I want 3 replicas of this image, reachable at this address"), and k8s continuously works to make reality match — rescheduling dead containers, replacing failed nodes, load-balancing traffic. You declare *what*; it figures out *how* and keeps it true.

## Architecture — control plane vs nodes

A cluster is a set of machines split into two roles:

**Control plane** (the brain — decides what should happen):
- **API server** — the front door; every command and component talks to it. `kubectl`, controllers, and nodes all go through it.
- **etcd** — the distributed key-value store holding the entire cluster state (the single source of truth). Lose etcd, lose the cluster's memory.
- **scheduler** — decides which node a new pod lands on, based on resource requests, affinity rules, and constraints.
- **controller manager** — runs the control loops that drive actual state toward desired state (e.g. the ReplicaSet controller creating pods until the count matches).

**Worker nodes** (the muscle — run the containers):
- **kubelet** — the agent on each node that talks to the API server and makes sure the pods it's assigned are actually running.
- **kube-proxy** — programs the node's network rules so Services route to the right pods.
- **container runtime** — actually runs containers (containerd, CRI-O).

The core mechanic is the **reconciliation loop**: controllers constantly compare desired state (in etcd) to observed state and act to close the gap. Self-healing, scaling, and rollouts are all the same loop applied to different objects.

## The core objects

Everything in k8s is a declarative object, usually written as YAML and applied with `kubectl apply -f`.

- **Pod** — the smallest deployable unit: one (or a few tightly-coupled) containers sharing a network namespace and storage. You rarely create pods directly — they're ephemeral and cattle, not pets.
- **Deployment** — the workhorse: declares *N replicas* of a pod template and manages rollouts/rollbacks. This is what you actually write for a stateless service.
- **ReplicaSet** — the layer a Deployment manages under the hood to maintain replica count (you don't touch it directly).
- **Service** — a stable network identity (a fixed virtual IP + DNS name) load-balancing across a set of pods, because pod IPs change constantly. Types: `ClusterIP` (internal only), `NodePort` (exposes a port on every node), `LoadBalancer` (provisions a cloud load balancer).
- **Ingress** — HTTP(S) routing into the cluster (host/path-based), fronted by an ingress controller (Nginx, Traefik). One entry point routing to many Services.
- **ConfigMap / Secret** — inject configuration and secrets into pods as env vars or mounted files. (k8s Secrets are only base64-encoded, not encrypted at rest by default — see [[devops/09-secret-management/01-secret-management|Secret Management]].)
- **Namespace** — a virtual partition of the cluster for isolating teams/environments.

A minimal Deployment + Service:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3                    # desired state: 3 pods, always
  selector:
    matchLabels: { app: web }
  template:
    metadata:
      labels: { app: web }
    spec:
      containers:
        - name: web
          image: myapp:1.4.0
          ports: [{ containerPort: 8080 }]
          readinessProbe:         # don't send traffic until this passes
            httpGet: { path: /health, port: 8080 }
---
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector: { app: web }         # routes to any pod with label app=web
  ports: [{ port: 80, targetPort: 8080 }]
```

`kubectl apply -f web.yaml` and k8s makes it so — schedules 3 pods, restarts any that die, and load-balances the Service across them.

## The workload controllers

Beyond `Deployment` (stateless), the object you pick encodes the workload's nature:

| Object | For |
|---|---|
| **Deployment** | stateless apps — interchangeable replicas |
| **StatefulSet** | stateful apps needing stable identity/storage per pod (databases, Kafka) — pods get ordered, persistent names |
| **DaemonSet** | one pod per node (log shippers, monitoring agents) |
| **Job / CronJob** | run-to-completion tasks / scheduled tasks |

## Health checks and self-healing

Three probes let k8s manage a pod's lifecycle correctly:

- **liveness** — is the app alive? Fail → restart the container.
- **readiness** — is it ready for traffic? Fail → remove from the Service load-balancer (but don't restart) until it recovers.
- **startup** — is a slow-starting app up yet? Protects a slow boot from being killed by the liveness probe.

Getting readiness right is what enables **zero-downtime rolling updates**: k8s brings up new-version pods, waits for their readiness probes, shifts traffic, then tears down old pods.

## Storage and networking, briefly

- **PersistentVolume (PV) / PersistentVolumeClaim (PVC)** — decouple storage from pods. A pod claims storage (PVC); k8s binds it to an actual volume (PV, often a cloud disk). Survives pod restarts.
- **Networking model** — every pod gets its own cluster-wide-routable IP; pods reach each other directly (a CNI plugin — Calico, Cilium — implements this). Services provide the stable front; DNS resolves Service names.

## Why it's simultaneously essential and heavy

Kubernetes is the industry standard for running containers at scale, and its declarative, self-healing model is genuinely powerful. It's also famously complex — a large API surface, a steep learning curve, and real operational burden. That complexity is exactly why **managed** k8s (GKE/EKS/AKS) and the alternatives exist — see [[devops/05-orchestration/02-orchestration-landscape|the landscape]] — and why [[devops/11-delivery-and-advanced/01-gitops|GitOps]] and [[devops/11-delivery-and-advanced/03-service-mesh|service meshes]] grew up around it to manage that complexity declaratively.

## Related
- [[devops/02-docker/README|Docker]] — the containers k8s schedules
- [[devops/05-orchestration/02-orchestration-landscape|The Orchestration Landscape]] — Swarm, managed k8s, OpenShift, Nomad
- [[devops/10-observability/README|Observability]] — Prometheus is the de-facto k8s monitoring stack
- [[devops/09-secret-management/01-secret-management|Secret Management]] — why k8s Secrets need help
