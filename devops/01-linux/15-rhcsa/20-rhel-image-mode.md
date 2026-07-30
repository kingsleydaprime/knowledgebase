# RHEL Image Mode (bootc)

> RHCSA V10 — added after reviewing the official RH134 course book (Red Hat System Administration II, RHEL 10.0). This is RHEL 10's newest, most different-paradigm feature — zero prior coverage in this vault, and conceptually unlike everything else in this folder, which all assumes the traditional package-based install model.

Part of [[README|RHCSA V10]]. Everything else in this folder — `dnf`, RPM, Kickstart in [[02-installing-rhel|installing-rhel]] — is the **package mode** most of RHEL's history has worked. Image mode is a genuinely different way to install, run, and update RHEL itself, built on the same container tooling ([[13-running-containers|running-containers]]) already covers for applications.

---

## The core idea: treat the whole OS like a container image

Instead of installing individual RPM packages onto a system and mutating it in place over its lifetime (the traditional model — and the reason configuration drift happens, since two servers set up "the same way" months apart rarely end up identical), **image mode builds the entire operating system as a bootable container image** — kernel, bootloader, and all — using the same `Containerfile` + `podman build` workflow already used for application containers.

The base image for this is **`rhel-bootc`** (**b**oot**c** = "bootable container") — a specialized base image containing what a normal application container never needs: a real kernel, a boot loader, systemd itself.

```dockerfile
# Containerfile
FROM registry.redhat.io/rhel10/rhel-bootc:latest
RUN dnf -y install httpd mod_ssl && dnf clean all
RUN systemctl enable httpd && firewall-cmd --add-service=https
COPY ./index.html /var/www/html/index.html
```

Notice what's *different* from an application Containerfile: no `ENTRYPOINT` (systemd itself starts and manages `httpd` as a normal enabled service, exactly like a non-container RHEL install), no `EXPOSE` (real firewall config controls access instead), no `ENV`/`USER` (systemd services and normal user management handle those). This is the tell that you're building an OS, not an app.

```bash
podman build --squash -t registry.example.com/user/webserver-bootc:latest .   # --squash: merge layers, smaller final image
podman push registry.example.com/user/webserver-bootc:latest
```

You can even test the image in ordinary "application mode" first — `podman run` it locally like any container, and `podman exec -l ps -ef` shows `systemd` (PID 1) already managing services inside, before you ever deploy it as a real bootable system:
```bash
podman run -d -p 8080:80 registry.example.com/user/webserver-bootc
curl http://localhost:8080          # confirm it actually serves before deploying anywhere real
```

---

## Deploying it

Anaconda ([[02-installing-rhel|installing-rhel]]) supports image mode as an install target directly — bare metal or VM, via Kickstart automation pointing at the image instead of a traditional package set. For cloud targets, Red Hat's `bootc-image-builder` tool turns a bootc image into a disk image in whatever format the target cloud needs (`qcow2` for QEMU, `ami` for AWS, `vmdk` for vSphere, `gce` for Google Cloud).

---

## Managing a deployed image-mode system — the `bootc` command

```bash
bootc status              # what's currently booted, what's staged, what (if anything) you could roll back to
bootc upgrade              # fetch + stage the latest image from the registry — does NOT reboot automatically
bootc upgrade --check       # see if an update exists, without pulling/staging it
bootc upgrade --apply       # fetch, stage, AND reboot into it in one step
bootc rollback              # revert to the previous deployment on next boot
```

Updates are **transactional and layered** — `bootc upgrade` only downloads the layers that actually changed, stages the new deployment alongside the current one (the running system is untouched until reboot), and a reboot is *always* required to actually switch to it. This is the direct payoff of the container-image model: an update that goes wrong is a `bootc rollback` + reboot away from being undone, not a manual repair job.

By default a system checks for updates automatically via a systemd timer:
```bash
systemctl status bootc-fetch-apply-updates.timer
systemctl mask bootc-fetch-apply-updates.timer     # disable permanently — e.g. if Ansible or another tool owns updates instead
```

---

## What "immutable" actually means here — /etc and /var are the exception

The root filesystem is genuinely **read-only** by default (built on `composefs` + `OSTree`, which can hold multiple complete filesystem deployments side by side — conceptually version control, but for entire filesystem trees rather than individual files, which is exactly what makes instant rollback possible). Two directories are deliberately carved out as mutable, and behave differently from each other:

| Directory | Behavior across upgrades |
|---|---|
| `/etc` | **3-way merged.** Your local edits are preserved and carried forward; files you never touched get updated to whatever the new image ships |
| `/var` | **Never merged, never rolled back.** Copied once at initial install, then left alone by every future upgrade *and* every rollback — a `bootc rollback` does not undo changes made to `/var` |

The practical consequence worth remembering: you cannot push a change to `/var` via an image update (a new Containerfile instruction touching `/var` simply won't apply to already-deployed systems) — `/var` is genuinely local, persistent, per-machine state, by design.

Booting into a specific deployment (current vs. rolled-back) is a GRUB2 menu entry per OSTree deployment — same GRUB2 covered in [[11-control-the-boot-process|control-the-boot-process]], just now presenting multiple bootable OS versions instead of multiple kernel versions.

---

## Why this exists — the pitch, in one line

Package mode lets two "identically configured" servers drift apart over months of individual `dnf` runs and manual fixes; image mode makes the entire OS the same kind of versioned, rollback-able, registry-distributed artifact an application container already is — the Containerfile *is* the system definition, checked into version control like any other build spec.
