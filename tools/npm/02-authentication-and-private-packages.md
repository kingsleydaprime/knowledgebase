# Module: Authentication and Private Packages (Proving Who You Are to a Registry)

**[Intermediate]** — [[01-registries-and-the-npmrc-file|The previous lesson]] routed requests to the right registry. This one is about the registry saying **no**.

Private packages, GitHub Packages, publishing, and the CI authentication that works on your laptop and fails in the pipeline — that gap is where most of the real difficulty lives, and it is nearly always one of four causes.

---

## Before you start

- You can explain npm's config precedence and what the local prefix is — [[01-registries-and-the-npmrc-file|registries and the `.npmrc` file]].
- You know that `${VAR}` is expanded when npm reads `.npmrc`, and that an unset variable becomes a literal.
- You know what a Git remote is and the difference between HTTPS and SSH authentication — [[git/08-remotes-and-collaboration|remotes and collaboration]].

**After this lesson you will be able to:**

1. Choose the right credential for a registry, and say where it should be stored.
2. Diagnose a 401 or 403 from a private registry by working through four causes in order.
3. Configure **GitHub Packages** for both installing and publishing.
4. Decide between a registry dependency and a **Git URL** dependency, and say what each costs.

**Study route:** read 1–3, then section 4's diagnostic ladder is the part to keep. There is no runnable lab here — it would need real credentials and a real registry — so section 6 is a **safe checklist you can run against your own setup** instead.

---

## 1. Why this exists: `npm install` works, then CI fails

The failure is always the same shape. Locally, `npm install` works. In CI, the same commit produces:

```
npm error code E401
npm error Unable to authenticate, your authentication token seems to be invalid.
```

**Nothing is wrong with the code, and nothing is wrong with the `.npmrc`.** What differs is the *environment*: your machine has a token that CI does not, because `npm login` wrote it into `~/.npmrc` on your laptop and CI has a different, empty home directory.

Understanding that one sentence solves most private-registry problems. The rest of this lesson is the detail.

---

## Terms used here

1. **Authentication token**: This is also called an **access token** or **auth token**. This is a long random string proving your identity to a registry, sent as a bearer credential on every request. It is stored under a host-specific key like `//npm.pkg.github.com/:_authToken`.
2. **`npm login`**: This is the interactive command that authenticates you and **writes the resulting token into your user `~/.npmrc`**. It is for humans at a keyboard; it is not how CI authenticates.
3. **Granular / fine-grained token**: This is a token scoped to specific permissions and specific packages or repositories, rather than to everything your account can reach. **Prefer these**; a leaked read-only token scoped to one package is a far smaller incident.
4. **Automation token**: This is a token that bypasses two-factor prompts, intended for CI. On npmjs.com these are created explicitly as "Automation" tokens, because a normal token will fail a publish when 2FA is enforced.
5. **Private package**: This is a package the registry serves only to authenticated, authorised accounts. On npmjs.com, publishing privately requires a paid plan; **scoped packages default to private** unless you pass `--access public`.
6. **GitHub Packages**: This is GitHub's registry, at `npm.pkg.github.com`. Its distinguishing rule: **the scope must match the GitHub owner** — `@yourorg/pkg` must be published from the `yourorg` account or organisation.
7. **`GITHUB_TOKEN`**: This is the token GitHub Actions injects into every workflow run automatically. It can read and publish packages **in the same repository** without you configuring any secret; for cross-repository access you need a personal access token instead.
8. **Git URL dependency**: This is a dependency installed straight from a Git repository rather than a registry, written as `"pkg": "github:owner/repo#v1.2.3"` or a full Git URL.

---

## 2. Where the token goes, and where it must not

| Location | Use it for | Safe to commit? |
| :--- | :--- | :--- |
| `~/.npmrc` (user) | your own machine; written by `npm login` | **not a repo file** — but back it up carefully |
| project `.npmrc` with `${VAR}` | naming which variable holds the token | **yes** — it contains no secret |
| project `.npmrc` with the literal token | nothing, ever | **no** |
| CI secret store | pipeline runs | n/a — never in the repo |
| `.env` file | local development | **no** — and add it to `.gitignore` |

**The committable pattern, in full:**

```ini
# .npmrc -- safe to commit
@acme:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
```

The repository says *which* registry and *which variable*. The value arrives from the environment — your shell locally, the secret store in CI. **The file is identical in both places, which is the point: one configuration, two environments.**

### If a token is committed

**Revoke it first, before anything else.** Deleting the commit does not help: it survives in the reflog, in every clone and fork, in CI caches, and in the databases of the bots that scan public pushes within seconds. Rewriting history is a *second* step for tidiness, not a remediation. Then rotate and audit what the token could reach.

---

## 3. GitHub Packages, specifically

It is the most common private registry to meet first, and it has three rules that catch everyone.

**Rule 1: the scope must match the owner.** `@acme/widget` can only live under the GitHub account or organisation named `acme`. There is no way to publish `@somethingelse/widget` from the `acme` account.

**Rule 2: `package.json` must name the registry for publishing.**

```json
{
  "name": "@acme/widget",
  "version": "1.0.0",
  "publishConfig": {
    "registry": "https://npm.pkg.github.com/"
  }
}
```

Without `publishConfig`, `npm publish` targets the default registry and either fails or — worse, if the name is unscoped and free — publishes your internal package to the public npm registry.

**Rule 3: reading and writing need different token scopes.** Installing needs `read:packages`. Publishing needs `write:packages`. Private repositories additionally need `repo`. A token with only `read:packages` produces a 403 on publish that reads like a permissions bug in the registry, and is not.

**In GitHub Actions**, the automatic `GITHUB_TOKEN` covers same-repository access without any configured secret:

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 20
    registry-url: 'https://npm.pkg.github.com'
    scope: '@acme'
- run: npm ci
  env:
    NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

`setup-node` writes the `.npmrc` for you from `registry-url` and `scope`; your job is to supply `NODE_AUTH_TOKEN`. **For packages in a *different* repository, `GITHUB_TOKEN` is not enough** — it is scoped to the current repository — and you need a personal access token stored as a secret.

---

## 4. Diagnosing a 401 or 403 — in this order

**Start with the status code, because it splits the problem in half:**

- **404** — usually the **wrong registry**. The server is answering; it just has no such package. Check the scope mapping.
- **401** — the registry got **no credential, or an invalid one**.
- **403** — the credential was **understood and refused**: authenticated, but not authorised.

Then, for 401/403, work through four causes in order. They are ordered by how often they are the answer:

1. **The environment variable is not set.** The `.npmrc` expanded `${NODE_AUTH_TOKEN}` to the literal string. Check with `echo ${NODE_AUTH_TOKEN:+set}` — prints `set` without revealing the value. **This is the most common cause by a wide margin in CI.**
2. **The auth key does not match the registry.** The key is `//host/path/:_authToken` and must match the registry URL including the trailing slash. `//npm.pkg.github.com/:_authToken` with `registry=https://npm.pkg.github.com` (no slash) is a silent mismatch: npm finds no credential and sends none, giving a 401 that looks like a bad token.
3. **The token lacks the needed scope.** `read:packages` will not publish. This is the usual cause of a 403 specifically.
4. **The `.npmrc` is not being read at all.** Wrong local prefix, wrong working directory, or a Docker build that copied `package.json` but not `.npmrc`. Confirm with `npm config list`, which prints every file it loaded.

**Two commands that end most investigations:**

```bash
npm config list            # which files loaded, and what each contributed
npm whoami --registry=https://npm.pkg.github.com/   # is this token valid, right now?
```

`npm whoami` is the decisive test: it returns your username if the credential works and errors if it does not, without touching any package.

> **In Docker, cause 4 has a specific form.** A Dockerfile that does `COPY package*.json ./` does **not** copy `.npmrc`, because the glob does not match it. The build then installs with no registry configuration at all. Use a build secret (`RUN --mount=type=secret`) rather than `COPY .npmrc`, which would bake the token into a layer that ships with the image.

---

## 5. Git URLs as dependencies

npm can install straight from a Git repository, bypassing registries entirely:

```json
{
  "dependencies": {
    "widget": "github:acme/widget#v1.2.3",
    "tool": "git+ssh://git@github.com/acme/tool.git#semver:^2.0.0"
  }
}
```

**When this is genuinely the right call:** a fork with a fix not yet released; an internal package where standing up a registry is not worth it; pinning to a specific commit during a bisect.

**What you give up, and it is more than people expect:**

| | Registry dependency | Git dependency |
| :--- | :--- | :--- |
| Install speed | a tarball fetch | a clone, often of full history |
| Content | the **published** files only | the **repository**, including tests and CI config |
| Build step | already built | **nothing runs `npm run build` for you** |
| Versioning | full semver resolution | a tag, branch or commit |
| Immutability | published versions are immutable | **a tag can be moved** |
| Auth | registry token | Git credentials — SSH keys or HTTPS |

**The build point is the one that bites.** A TypeScript package normally publishes compiled `dist/`. Installed from Git you get the *source*, and unless the package has a `prepare` script that builds on install, your import resolves to nothing.

**And the authentication is different in kind.** A private Git dependency over SSH needs an SSH key in the environment — which in CI means a deploy key or an SSH agent, not an npm token. **Configuring `NODE_AUTH_TOKEN` does nothing for a `git+ssh://` dependency**, and that mismatch is a common source of confusion. Using `https://` with a token in the URL works but puts a credential in `package-lock.json`, which is then committed. Prefer SSH with a deploy key, or a registry.

---

## 6. A safe checklist against your own setup

No lab here — a real one would need real credentials. **These commands are read-only, publish nothing, and reveal no secrets.**

```bash
# 1. Which config files are in play, and what did each contribute?
npm config list

# 2. What registry will an unscoped install use?
npm config get registry

# 3. And a scoped one? (substitute your scope)
npm config get @acme:registry

# 4. Is the token variable set? Prints "set" or nothing -- never the value.
echo "${NODE_AUTH_TOKEN:+set}"

# 5. Is the credential actually valid, right now?
npm whoami --registry=https://registry.npmjs.org/

# 6. Would a publish go where you think? --dry-run publishes NOTHING.
npm publish --dry-run

# 7. What files would actually ship?
npm pack --dry-run
```

**Commands 6 and 7 are worth building a habit around.** `npm publish --dry-run` reports the target registry, the version, and the file list without uploading anything — it catches "about to publish an internal package to the public registry" *before* it becomes an incident rather than after.

---

## 7. Common pitfalls and traps

1. **Running `npm login` and expecting CI to work.** It writes to your machine's `~/.npmrc` only. CI needs the token through its own secret store.
2. **A committed token.** Revoke immediately; history rewriting is cleanup, not remediation.
3. **`COPY .npmrc` in a Dockerfile.** Bakes the credential into an image layer that ships. Use `RUN --mount=type=secret`.
4. **Publishing a scoped package without `--access public`.** Scoped packages default to **private**, and the publish fails on a free account with an error about payment that reads like a billing problem.
5. **Publishing an *unscoped* internal package by accident.** With no `publishConfig` and a free name, it goes to the public registry. `npm publish --dry-run` first, every time.
6. **A trailing-slash mismatch between registry URL and auth key.** No credential is sent; you get a 401 that looks like a bad token.
7. **Assuming `GITHUB_TOKEN` reaches other repositories.** It is scoped to the current one. Cross-repository access needs a PAT.
8. **A Git dependency without a build step.** You get source, not `dist/`, unless the package has a `prepare` script.
9. **Trusting a Git tag as immutable.** Tags can be force-moved; a registry version cannot be changed once published. Pin to a commit SHA if it matters.
10. **Using a token when the dependency needs SSH.** `git+ssh://` needs a key, not `NODE_AUTH_TOKEN`.

---

## 8. Check your understanding

1. **`npm install` works locally, fails with 401 in CI, same commit. What is the first thing to check?**
   <details><summary>Answer</summary>Whether the token environment variable is set in CI. Your machine has a credential — usually written by <code>npm login</code> into <code>~/.npmrc</code> — that CI does not, because CI starts with an empty home directory. Check with <code>echo "${NODE_AUTH_TOKEN:+set}"</code>, which prints <code>set</code> without exposing the value. This is the most common cause by a wide margin.</details>

2. **You get 404 from a private registry, not 401. What does that suggest?**
   <details><summary>Answer</summary>Usually the wrong registry rather than bad credentials — the server answered and has no such package. Check the scope mapping: <code>@acme/widget</code> without <code>@acme:registry=</code> resolves against the public registry, where it does not exist. As a rule: <b>404 = wrong place, 401 = no valid credential, 403 = valid credential without permission.</b></details>

3. **Why is a project `.npmrc` containing `//registry/:_authToken=${TOKEN}` safe to commit?**
   <details><summary>Answer</summary>Because it contains the variable's <i>name</i>, not its value. npm expands <code>${TOKEN}</code> when it reads the file, from the environment. The repository holds configuration; the environment holds the secret. The same file then works unchanged on a laptop and in CI, which is the reason to do it this way rather than merely the reason it is safe.</details>

4. **What does a Git dependency give you that a registry one does not, and what does it cost?**
   <details><summary>Answer</summary><b>Gives:</b> install directly from a fork or an unreleased commit, with no registry to run. <b>Costs:</b> a clone instead of a tarball; the whole repository rather than the published files; <b>no build step</b>, so a TypeScript package arrives as source unless it has a <code>prepare</code> script; a movable tag instead of an immutable version; and Git credentials rather than a registry token — <code>NODE_AUTH_TOKEN</code> does nothing for <code>git+ssh://</code>.</details>

5. **You are about to publish. Which single command catches the most mistakes?**
   <details><summary>Answer</summary><code>npm publish --dry-run</code>. It reports the target registry, the name and version, and the exact file list, while uploading nothing. It catches publishing to the wrong registry, publishing an internal package publicly, a missing <code>publishConfig</code>, an unintended version, and shipping files that should have been excluded — all before the publish is irreversible.</details>

---

## 9. Practice — independent task

**Safety first: use a throwaway token scoped as narrowly as possible, and revoke it when finished. Publish only to a scope you own, and only packages named for this exercise.**

**Part 1 — the four causes, deliberately reproduced.** For a private registry you control (GitHub Packages on a personal repo is free), reproduce each of section 4's four causes in turn and **record the exact error text for each**. You are building a lookup table for your future self.

**Part 2 — one config, two environments.** Write a project `.npmrc` using `${NODE_AUTH_TOKEN}`. Make `npm ci` succeed on your machine and in a GitHub Actions workflow **without changing the file**. Confirm the committed file contains no secret.

**Part 3 — publish for real.** Publish a trivial `@yourname/hello` package to GitHub Packages. Then: run `npm publish --dry-run` first and compare its report to what actually happened; check the published file list against `npm pack --dry-run`; and install it into a fresh project from a different directory.

**Part 4 — the Docker trap.** Write a Dockerfile that `npm ci`s a private dependency. First do it the wrong way (`COPY .npmrc`) and confirm with `docker history` that the token is visible in a layer. Then do it with `RUN --mount=type=secret` and confirm it is not.

**Part 5 — Git dependencies.** Install a TypeScript package from a Git URL that has no `prepare` script and observe the import failing. Then fork it, add `prepare`, and confirm it works. **Write one sentence on what `prepare` is doing and when it runs.**

**Part 6 — token scopes.** Create a `read:packages`-only token and attempt a publish. Record the status code and message, and confirm it matches your part 1 table.

**Done when:** part 1's table has four distinct error texts; part 2's file is committed and secret-free and works in both places; part 3's dry run matched reality; part 4 shows the token present in one image and absent in the other; and every token you created is revoked.

---

## Before moving on

You can choose and place a credential, diagnose a 401/403 by working four causes in order, configure GitHub Packages for reading and publishing, and weigh a Git dependency against a registry one.

**Recap:** the local-works-CI-fails gap is almost always that `npm login` wrote a token into your `~/.npmrc` and CI has an empty home. The committable pattern is a project `.npmrc` naming a **variable** — `${NODE_AUTH_TOKEN}` — with the value supplied by your shell locally and the secret store in CI: **one file, two environments**. Split diagnosis by status code — **404 wrong registry, 401 no valid credential, 403 valid but unauthorised** — then check, in order: variable unset, auth key/registry mismatch (trailing slashes), insufficient token scope, `.npmrc` not read at all. `npm config list` and `npm whoami --registry=...` end most investigations. For **GitHub Packages**, the scope must match the owner, `publishConfig` must name the registry, and read and write need different scopes; `GITHUB_TOKEN` covers the same repository only. **Git dependencies** skip the registry but cost you the build step, immutability, and a different kind of authentication entirely. Run `npm publish --dry-run` before every publish. If a token is ever committed, **revoke first**.

---

## Related

- [[01-registries-and-the-npmrc-file|Registries and the `.npmrc` File]] — the previous lesson: precedence, scopes, substitution
- [[devops/09-secret-management/01-secret-management|Secret Management]] — where credentials should live
- [[devops/06-ci-cd/10-pipeline-security|Pipeline Security]] — secrets in a pipeline
- [[git/08-remotes-and-collaboration|Git Remotes and Collaboration]] — SSH versus HTTPS, which Git dependencies depend on
- [[git/15-the-github-cli|The GitHub CLI]] — `gh auth`, and the token it manages
- [[devops/02-docker/04-multi-stage-builds|Multi-Stage Builds]] — keeping credentials out of image layers
- [[tools/npm/index|the npm folder]]
