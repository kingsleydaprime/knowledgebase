# Flatpak

> RHCSA V10 — added after reviewing the official RH124 course book (Red Hat System Administration I, RHEL 10.0), which gives Flatpak its own chapter. Zero prior coverage in this vault — everything so far has been RPM/`dnf`.

Part of [[README|RHCSA V10]]. Builds on the package-management comparison table in [[01-getting-started-with-rhel|getting-started-with-rhel]] — Flatpak is a genuinely different packaging model from RPM, not just an alternate syntax for the same idea.

---

## Why Flatpak exists — a different problem than RPM solves

RPM (via `dnf`) ties a package to a specific distribution and version — the same reason a `.deb` built for Ubuntu doesn't just work on RHEL. Flatpak sidesteps this by borrowing container concepts for the *desktop*: an application is packaged with its own dependencies, runs in an isolated **sandbox**, and works the same way across distributions and versions, regardless of what's installed on the host system underneath.

The sandboxing is the other half of the pitch, not just portability: a Flatpak app can only access what it's explicitly granted — files, network, graphics, the system bus, other devices — nothing by default. This is a meaningfully different security model than an RPM-installed app, which generally runs with the full access of whatever user launched it.

To avoid every app bundling a full copy of every library it needs, Flatpak apps share **runtimes** — a runtime is a filesystem image of system-level libraries that multiple apps can depend on at once, so a security fix to a shared library is one runtime update, not a rebuild of every app that uses it.

---

## Setup

Flatpak ships installed by default on RHEL 10 (alongside `gnome-software`, the GUI front-end). If it's missing:
```bash
dnf install flatpak
flatpak --version
```

Applications and runtimes come from **remotes** (repositories) — RHEL's default remote is Red Hat's own catalog; the largest third-party one is **Flathub** (flathub.org), unsupported by Red Hat but widely used:

```bash
flatpak remotes                                   # what's configured
flatpak remotes -d                                 # with URL/priority detail
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak remote-ls --app                             # list apps available FROM a remote (add --app to skip runtimes)
```

`flatpak remote-add` defaults to system-wide (`--system`, implicit) — add `--user` to scope a remote (and anything installed from it) to just the current user instead:
```bash
flatpak remotes --system     # remotes available to everyone
flatpak remotes --user       # remotes available only to you
```

To retire a remote: `flatpak remote-delete <name>` (prompts to uninstall everything sourced from it first) or `flatpak remote-modify --disable <name>` if you just want to pause it without uninstalling anything already there.

---

## Installing, updating, removing

Flatpak IDs follow a reverse-domain format — `org.mozilla.Thunderbird` — but the short form (`thunderbird`) usually works too, as long as it's unambiguous across your configured remotes:

```bash
flatpak search thunderbird              # search all enabled remotes at once
flatpak install thunderbird             # installs the app AND any runtime it needs, prompting for both
flatpak list                             # everything installed locally
flatpak info org.mozilla.Thunderbird     # detail on one installed object
flatpak run org.mozilla.Thunderbird      # launch it (GUI apps also just appear in the desktop's app menu)
flatpak update                           # update everything installed
flatpak update com.redhat.Platform       # update just one
flatpak uninstall thunderbird            # remove
flatpak uninstall --delete-data thunderbird   # also remove the app's own data, not just the app
```

`flatpak update` only checks for a newer version on the **same branch** the app was installed from (`stable`, `beta`, etc.) — same mental model as a git branch: switching to a genuinely different branch is a different operation, not just "the next update."

---

## Related
- [[01-getting-started-with-rhel|getting-started-with-rhel]] — where dnf/RPM is covered, the packaging model Flatpak is an alternative to
