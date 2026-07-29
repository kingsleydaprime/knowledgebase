# Getting Started with Red Hat Enterprise Linux

> RHCSA V10

Part of [[README|RHCSA V10]].

---

## What RHEL actually is

Red Hat Enterprise Linux is the commercial, enterprise-support Linux distribution from Red Hat (owned by IBM since 2019). The product isn't really the software — RHEL's source is public — the product is the **support contract, certification, and stability guarantee**. Companies pay for RHEL because when something breaks in production, there's a phone number to call and a guaranteed fix timeline (an SLA).

This is the single biggest mental shift coming from Ubuntu/Debian: on your personal machine, "free and community-supported" is fine. In an enterprise data center running a bank's core systems, someone needs to be contractually liable when it breaks.

---

## The Fedora → CentOS Stream → RHEL pipeline

Red Hat doesn't build RHEL from scratch every release. There's a pipeline:

```
Fedora (upstream)  →  CentOS Stream (midstream)  →  RHEL (downstream)
   bleeding edge         preview of next RHEL         stable, supported
   new features first    minor release, ~6mo out      frozen, patched for 10yrs
```

| Distro | Role | Who uses it |
|---|---|---|
| **Fedora** | Upstream — new kernel features, new packages land here first | Developers who want the latest, RHEL engineers testing what's next |
| **CentOS Stream** | Midstream — a rolling preview of the *next* RHEL minor version | People who want to see what's coming, contribute upstream |
| **RHEL** | Downstream — frozen, tested, patched, supported for ~10 years per major version | Production enterprise systems |

Old CentOS Linux (the free 1:1 rebuild of RHEL) was discontinued in 2020 in favor of CentOS Stream. That gap got filled by **Rocky Linux** and **AlmaLinux** — free, community-maintained, binary-compatible rebuilds of RHEL, used by people who want RHEL's stability without the subscription cost. Everything in this RHCSA track transfers directly to Rocky/Alma.

---

## The subscription model

RHEL itself is free to *download and use* for development and small production workloads under the **Red Hat Developer Subscription for Individuals** — this is how you'll get RHEL for the exam labs and home practice. What you pay for at real enterprise scale is:

- Access to **patches and updates** via Red Hat's repos
- **Support cases** (phone/ticket access to Red Hat engineers)
- **Certification** — RHEL is certified to work with specific hardware/software vendors (Oracle, SAP, VMware), which matters for compliance in regulated industries

```bash
# Registering a system with Red Hat (post-install)
subscription-manager register --username <user> --password <pass>
subscription-manager attach --auto      # attach an available subscription
subscription-manager list --available   # see what's available
subscription-manager status             # check current status
```

Without registration, `dnf` has no repos to pull from — this is the RHEL equivalent of `apt update` failing because `/etc/apt/sources.list` is empty.

---

## Package management: dnf replaces apt

| Concept | Debian/Ubuntu | RHEL |
|---|---|---|
| Package manager | `apt` | `dnf` (yum is now a symlink to dnf) |
| Package format | `.deb` | `.rpm` |
| Repo config | `/etc/apt/sources.list`, `/etc/apt/sources.list.d/` | `/etc/yum.repos.d/*.repo` |
| Install | `apt install pkg` | `dnf install pkg` |
| Remove | `apt remove pkg` | `dnf remove pkg` |
| Update all | `apt update && apt upgrade` | `dnf update` (does both in one) |
| Search | `apt search term` | `dnf search term` |
| Show info | `apt show pkg` | `dnf info pkg` |
| List installed | `dpkg -l` | `rpm -qa` |
| Firewall | `ufw` | `firewalld` |
| Mandatory access control | AppArmor | **SELinux** — the biggest conceptual jump, gets its own note: [[07-manage-selinux-security|manage-selinux-security]] |

Full depth on package management already lives in [[devops/01-linux/05-package-management|Package Management]] — the concepts (repos, dependency resolution, caching) carry over 1:1 from what's there; `dnf` is just the RHEL-family syntax.

---

## Where the RHCSA exam fits

- **RHCSA (EX200)** — Red Hat Certified System Administrator. Tests exactly what this course is walking through: users/groups, permissions, storage, networking, SELinux, services, containers.
- **RHCE (EX294)** — Red Hat Certified Engineer. Builds on RHCSA, adds Ansible automation.

The exam is **entirely performance-based** — no multiple choice. You get a live RHEL VM (or several) and a list of tasks to complete in ~2.5 hours ("configure this user," "mount this NFS share persistently," "put this SELinux boolean in the right state"). It's graded by whether the system is in the correct end state when time's up, not by what commands you typed. That's why these notes lean so heavily on commands and verification steps rather than theory.
