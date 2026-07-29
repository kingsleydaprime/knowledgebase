# Running Containers

> RHCSA V10

Part of [[README|RHCSA V10]]. RHEL's container tooling is **Podman**, not Docker — this shows up on newer RHCSA objectives (RHEL 8+) as its own section.

---

## Podman vs. Docker

| | Docker | Podman |
|---|---|---|
| Architecture | Client talks to a persistent background **daemon** (`dockerd`) running as root | **Daemonless** — each `podman` command is its own fork/exec, no background process |
| Root requirement | Daemon traditionally runs as root, containers inherit that | **Rootless by default** — a regular user can run containers without root at all |
| CLI | `docker ...` | `podman ...` — deliberately near-identical syntax |
| systemd integration | Bolted on | Native — a podman container maps cleanly onto a systemd unit (see below) |

The daemonless, rootless design is a direct security response to Docker's model: no single root-owned background process is a huge reduction in attack surface. Command-for-command the two tools are close enough that `alias docker=podman` genuinely works for most everyday use.

```bash
sudo dnf install podman
```

---

## Basic commands

```bash
podman search nginx                     # search configured registries
podman pull registry.access.redhat.com/ubi9/ubi   # pull an image — Red Hat's Universal Base Images are the "official" RHEL-family base
podman images                           # locally cached images
podman run -d --name web -p 8080:80 nginx    # run detached, name it, map host:container port
podman ps                               # running containers
podman ps -a                            # running + stopped
podman logs web                         # container's stdout/stderr
podman logs -f web                      # follow live
podman exec -it web /bin/bash           # shell into a running container
podman stop web
podman rm web                           # must be stopped first (or use -f to force)
podman inspect web                      # full JSON detail — networking, mounts, env, everything
```

---

## Registries

```bash
/etc/containers/registries.conf         # configured registries, search order
```
Common registries you'll actually pull from:

| Registry | Notes |
|---|---|
| `registry.redhat.io` | Red Hat's official images — requires `podman login` with a valid subscription |
| `registry.access.redhat.com` | Red Hat's free Universal Base Images (UBI) — no login required |
| `quay.io` | Red Hat's public registry (also self-hostable) |
| `docker.io` | Docker Hub — works fine with podman too |

```bash
podman login registry.redhat.io
```

---

## Rootless containers — how the UID mapping works

A rootless container's process shows up as `root` *inside* the container but maps to your unprivileged UID *outside* it, via a range of extra UIDs reserved for that user:

```bash
cat /etc/subuid          # kingsley:100000:65536  — kingsley owns a range of 65536 sub-UIDs starting at 100000
cat /etc/subgid          # same idea for groups
```
Podman uses that range to remap UIDs 0-65535 *inside* the container's namespace onto `100000-165535` on the *host* — so "root" inside the container has zero actual host privilege.

The practical consequence: **rootless containers can't bind ports below 1024** (privileged ports on the host), since the unprivileged host user genuinely can't. Workarounds are either running rootful (`sudo podman run ...`) or mapping to a high host port instead (`-p 8080:80` rather than trying `-p 80:80`).

---

## Persisting containers across reboots — systemd integration

A `podman run` container doesn't survive a reboot on its own — you need it managed by systemd, same as any other service in [[devops/01-linux/07-systemd-and-services|systemd & Services]].

### Generating a unit from a running container

```bash
podman run -d --name web -p 8080:80 nginx
podman generate systemd --new --name web --files
# writes container-web.service in the current directory
```

For a **rootless** container, the unit needs to live in the user's own systemd scope:
```bash
mkdir -p ~/.config/systemd/user
mv container-web.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now container-web.service
```

### The lingering gotcha

By default, a user's `systemctl --user` services **stop the moment that user logs out** — there's no active session to run them under. For a container that's supposed to act like a persistent server, that's the opposite of what you want. Fix it with lingering:
```bash
sudo loginctl enable-linger kingsley
```
This tells systemd to keep that user's service manager (and anything running under it) alive even with no active login session — the rootless-container equivalent of "start on boot" for a regular system service. This is the single most common reason a rootless container "works, then disappears after the exam VM reboots."

### Quadlets — the newer approach

Recent Podman versions support **Quadlet**: `.container` files (systemd-unit-like syntax, but container-specific) dropped into `~/.config/containers/systemd/` (rootless) or `/etc/containers/systemd/` (rootful), which systemd auto-generates a unit from. Worth knowing the name exists as the direction this is heading, even if `podman generate systemd` is still the more commonly tested/documented path right now.
