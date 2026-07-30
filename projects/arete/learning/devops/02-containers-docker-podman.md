# Arete DevOps — Containers: Docker & Podman

Split out from the original single-file `devops-learning.md`. See also
`01-fundamentals-and-environment.md`.

---

## Part 2 — Containers

### The concepts, precisely

| Term | What it is | Analogy |
|---|---|---|
| **Image** | A frozen filesystem + start command (`postgres:16-alpine`) | A class |
| **Container** | A running (or stopped) instance of an image | An object |
| **Volume** | Named storage that outlives containers | The hard drive |
| **Network** | Private DNS + routing between containers | The office LAN |
| **Port mapping** | `host:container` — `5432:5432` exposes the container to your laptop | A doorway |
| **Registry** | Where images come from (Docker Hub by default) | npm for machines |

The core promise: a container bundles the app *and* its OS-level dependencies, so "works on my machine" becomes "works on any machine with a container runtime."

### Arete's docker-compose.dev.yml, annotated

```yaml
services:
  postgres:
    image: postgres:16-alpine          # official image, alpine = tiny base OS
    container_name: arete_postgres_dev
    restart: unless-stopped            # auto-restart on crash/reboot, unless you stopped it
    environment:                       # the image reads these on first boot
      POSTGRES_USER: arete
      POSTGRES_PASSWORD: arete_dev_secret
      POSTGRES_DB: arete_dev
    ports:
      - "5432:5432"                    # host:container — lets localhost:5432 reach it
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data   # data survives `down`
    healthcheck:                       # how the runtime knows it's *ready*, not just running
      test: ["CMD-SHELL", "pg_isready -U arete -d arete_dev"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes: [redis_dev_data:/data]

volumes:                               # named volumes are declared at top level
  postgres_dev_data:
  redis_dev_data:
```

Key insights:
- **Volumes are why `down` is safe.** We took the stack down after seeding; the 281 variants + 210 messages persisted in `postgres_dev_data`. Only `down -v` (or `volume rm`) destroys data.
- **Healthcheck vs running:** `podman ps` showed `Up 8 seconds (starting)` → the process was up but `pg_isready` hadn't passed yet. Migrations run against a "starting" DB fail confusingly; wait for `(healthy)`.
- `version: "3.9"` at the top is obsolete — compose warns and ignores it now.

### Docker vs Podman — what actually differs

| | Docker | Podman |
|---|---|---|
| Architecture | Client → **root daemon** (`dockerd`) | **Daemonless** — each container is a child process |
| Default privileges | Daemon runs as root | **Rootless** — runs as your user |
| Ships with Fedora/RHEL | No | **Yes** (Red Hat project) |
| CLI | `docker ...` | Same verbs: `podman ps`, `podman run`... |
| Compose | `docker compose` built in | Delegates to a compose provider |
| Images | OCI standard — **identical images work in both** |

Because both implement the **OCI spec**, `postgres:16-alpine` is byte-for-byte the same under either. Kubernetes uses neither directly (containerd/CRI-O) — the image is the portable artifact, the runtime is an implementation detail.

**The three Podman gotchas we actually hit on this project:**

```bash
# 1. `docker ps` failed:
#    "failed to connect to the docker API at unix:///var/run/docker.sock"
#    → there IS no docker daemon on Fedora. Use podman.

# 2. `podman compose up -d` failed:
#    "dial unix /run/user/1000/podman/podman.sock: connect: no such file"
#    → compose talks to podman through a user socket that wasn't started:
systemctl --user start podman.socket        # start it now
systemctl --user enable --now podman.socket # start it on every login (permanent fix)

# 3. `podman ps` showed NOTHING — but postgres was clearly serving on :5432.
#    Rootless containers are per-user: containers started as root (sudo) or by
#    another user are invisible to your `podman ps`. Diagnose from the network side:
ss -tlnp | grep -E '5432|6379'   # ss shows listeners regardless of who owns them
sudo podman ps                    # root's containers live in a separate world
```

`systemctl --user` manages services for *your user session* (rootless), as opposed to system-wide `systemctl` — consistent with Podman's whole rootless philosophy.

### The container commands used on Arete (your cheat sheet)

```bash
# bring the dev stack up (detached)
podman compose -f docker-compose.dev.yml up -d
#              ^^ which file            ^^ -d = detached (don't tie up the terminal)

# see what's running (+ health state)
podman ps
podman ps -a                          # -a includes stopped containers
podman ps --format '{{.Names}} {{.Status}}'   # Go-template output: just the columns you want

# logs, shells, inspection
podman logs -f arete_postgres_dev     # -f = follow (live tail)
podman exec -it arete_postgres_dev psql -U arete -d arete_dev   # shell INTO the container
podman inspect arete_postgres_dev     # full JSON: mounts, env, network, health

# tear down (containers + network removed; named VOLUMES KEPT)
podman compose -f docker-compose.dev.yml down
podman compose -f docker-compose.dev.yml down -v   # ⚠ also deletes volumes = data loss

# housekeeping
podman volume ls
podman images
podman system prune                   # remove stopped containers + dangling images
```

---

