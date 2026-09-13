# Module: Registries and the `.npmrc` File (Where Packages Come From)

**[Intermediate]** — `npm install lodash` is four words that hide a decision: **which server?** For a public package the answer is boring. The moment a project pulls from a private registry, a company Nexus, or GitHub Packages, that decision becomes configuration — and the file holding it is `.npmrc`.

This lesson is about that file: where npm looks for it, which copy wins when several exist, how one project pulls from several registries at once, and why the file can be committed to a public repository without leaking anything.

---

## Before you start

- You can run `npm install` and know what `package.json` and `node_modules/` are.
- You know what an environment variable is and how to set one for a single command — [[devops/01-linux/10-environment-variables|environment variables]].
- You know the difference between a URL's host and its path.

**After this lesson you will be able to:**

1. State npm's **configuration precedence** and predict which file supplies a given setting.
2. Point a **scope** at a different registry, and explain how one `npm install` run can hit two servers.
3. Explain what "the project `.npmrc`" actually means — it is **not** the nearest ancestor with an `.npmrc`.
4. Write an `.npmrc` that is safe to commit, using environment-variable substitution.

**Study route:** read 1–4, answer the prediction in section 3, then run the lab. It creates a sandbox, redirects `HOME`, never contacts a registry, and deletes itself.

---

## 1. Why this exists: `npm install` has to choose a server

A package name is not a location. `lodash` does not say where lodash lives — npm resolves it against a **registry**, which defaults to `https://registry.npmjs.org/`.

That default is fine until one of these is true:

1. Your company publishes internal packages that must not be public.
2. You consume packages from **GitHub Packages**, which is a different registry with different authentication.
3. You proxy the public registry through a cache (Artifactory, Nexus, Verdaccio) for speed, auditing, or supply-chain control.
4. You are in CI, where there is no interactive login and credentials must arrive some other way.

**Each of those is a line in `.npmrc`.** And because a machine, a user and a project can each have opinions, there are several `.npmrc` files and a defined order in which they win.

---

## Terms used here

1. **Registry**: This is an HTTP server that stores packages and answers queries about their versions. The public one is `registry.npmjs.org`. **Anything speaking the same API is a registry**, which is why GitHub Packages, Nexus and Verdaccio are drop-in alternatives.
2. **`.npmrc`**: This is npm's configuration file, in `key=value` INI format. Several may exist at once; they **merge**, with the more specific one winning per key.
3. **User-level `.npmrc`**: This is `~/.npmrc`, holding settings for you across every project. **This is where `npm login` writes your token by default.**
4. **Project-level `.npmrc`**: This is the `.npmrc` in the project's **local prefix**, holding settings for this project across every developer. Usually committed.
5. **Global `.npmrc`**: This is at `$PREFIX/etc/npmrc`, machine-wide. Rare outside a managed build image.
6. **Local prefix**: This is the directory npm treats as "the project" — the nearest ancestor of the working directory containing `package.json` or `node_modules`. **This is the definition people get wrong**, because it is not simply "the nearest directory with an `.npmrc`".
7. **Scope**: This is the `@name/` prefix on a package such as `@acme/widget`. Scopes act as namespaces, and **each scope can be pointed at its own registry** — the mechanism that lets one project draw from several servers.
8. **Auth token**: This is the credential proving who you are to a registry, stored under a host-specific key like `//npm.pkg.github.com/:_authToken`. **Note the leading `//`** — the key is the registry's host and path, so credentials are per-registry.
9. **Environment-variable substitution**: This is npm expanding `${VAR}` inside `.npmrc` when it reads the file, which is what lets a committed file reference a secret it does not contain.

---

## 2. The precedence order

Highest wins:

```
    1. command line flags        --registry=...
    2. environment variables     npm_config_registry=...
    3. project .npmrc            ./.npmrc  (in the local prefix)
    4. user .npmrc               ~/.npmrc
    5. global .npmrc             $PREFIX/etc/npmrc
    6. npm built-in defaults
```

**The critical property is that these merge per key rather than replacing wholesale.** The lab demonstrates it: a user-level file sets `save-exact=true` and a registry; a project-level file sets only a registry. The result:

```
  registry   = https://project-level.example.com/   <- project wins
  save-exact = true              <- still from user level
```

**The project file overrode only the key it actually set.** A project `.npmrc` is a patch on your personal configuration, not a replacement for it.

### Finding where a value came from

`npm config list` reports the origin of everything, which is the first command to run when a setting is not what you expect:

```
    ; "user" config from <SANDBOX>/fakehome/.npmrc

    ; registry = "https://user-level.example.com/" ; overridden by project
    save-exact = true

    ; "project" config from <SANDBOX>/project/.npmrc

    registry = "https://project-level.example.com/"
```

**Note the commented-out line marked `; overridden by project`.** npm shows you the value that lost and who beat it — which usually ends the debugging session immediately.

---

## 3. What counts as "the project"

> **Predict before reading on.** A project has `.npmrc` and `package.json` at its root. You `cd` into `project/nested/`, which contains neither. **Does the project's `.npmrc` still apply?**

**Yes — but not for the reason most people give.** It is not that npm walks up looking for an `.npmrc`. npm first determines the **local prefix**: the nearest ancestor directory containing `package.json` or `node_modules`. *That* directory's `.npmrc` is the project config.

The lab confirms it:

```
  cwd is project/nested, which has no .npmrc and no package.json.
  registry = https://project-level.example.com/
```

**The distinction matters in a real case.** In a monorepo, running npm inside a package that has its own `package.json` makes *that* package the local prefix — so the repository-root `.npmrc` is **not** read as project config. Teams hit this when root-level registry settings mysteriously fail to apply inside a workspace, and the fix is either an `.npmrc` per package or moving the setting to the user level.

---

## 4. Scoped registries: several servers, one install

A **scope** is the `@name/` prefix on a package. Point a scope at a registry and packages in that scope resolve there, while everything else keeps using the default:

```ini
registry=https://registry.npmjs.org/
@acme:registry=https://npm.pkg.github.com/
@internal:registry=https://nexus.example.com/repository/npm/
```

The lab confirms all three resolve independently. So in one project:

- `npm i lodash` → `registry.npmjs.org`
- `npm i @acme/widget` → `npm.pkg.github.com`
- `npm i @internal/logger` → the company Nexus

**This is the normal arrangement in any company with private packages**, and it is why scopes exist at all: they are not decoration on the name, they are the routing key.

**Each registry needs its own credentials**, keyed by host — which is [[02-authentication-and-private-packages|the next lesson]].

---

## 5. Why a committed `.npmrc` need not leak anything

The file must reference a token. Committing a token is a serious mistake. **The resolution is that npm expands `${VAR}` when it reads the file**, so the file names the variable and the environment supplies the value:

```ini
@acme:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
```

The lab shows the expansion happening and, crucially, what happens when the variable is missing:

```
  with LAB_REGISTRY set, npm expands it at read time:
    registry = https://expanded-from-env.example.com/
  with LAB_REGISTRY unset, the placeholder stays literal:
    registry = ${LAB_REGISTRY}
```

**An unset variable does not raise an error. The literal string `${LAB_REGISTRY}` is used as the value.** For a registry that produces a confusing URL error; for a token it produces a `401 Unauthorized` that looks like a permissions problem rather than a missing variable. **This is the most common private-registry failure in CI**, and knowing the mechanism turns a long debugging session into one `echo $NODE_AUTH_TOKEN`.

### npm will not read a token back to you

The lab tries:

```
  $ npm config get //npm.pkg.github.com/:_authToken
    npm error The //npm.pkg.github.com/:_authToken option is protected, and cannot be retrieved in this way
```

**That is a deliberate guard, not a bug.** Token-shaped keys cannot be printed through the CLI, so they do not land in shell history, CI logs, or a screen share, and `npm config list` redacts them too. To check whether a token is present, test the environment variable or run an authenticated command such as `npm whoami --registry=...`.

---

## 6. Worked example — complete runnable lab

Save as `npmrc_lab.sh`. Requires `npm` on your `PATH` and nothing else.

**Safety:** it creates a temporary directory, **redirects `HOME` into it so your real `~/.npmrc` is never read or written**, contacts no registry, publishes nothing, and deletes the sandbox on exit. The example registry hostnames do not resolve and are never requested.

```bash
bash npmrc_lab.sh
```

```bash
#!/usr/bin/env bash
# Where npm actually reads its configuration from, and which file wins.
#
# Run:  bash npmrc_lab.sh
#
# Creates a throwaway directory under /tmp, touches nothing else, and deletes
# it at the end. It never contacts a registry and never publishes anything.

set -u
LAB="$(mktemp -d)"
trap 'rm -rf "$LAB"' EXIT
cd "$LAB" || exit 1

echo "=== 0. Sandbox ==="
echo "  working in a temporary directory; HOME is redirected so your real"
echo "  ~/.npmrc is never read or written."
mkdir -p fakehome project/nested
echo '{"name":"lab","version":"1.0.0"}' > project/package.json
export HOME="$LAB/fakehome"

echo
echo "=== 1. With no .npmrc anywhere, npm uses its built-in defaults ==="
cd "$LAB/project" || exit 1
echo "  registry      = $(npm config get registry)"
echo "  save-exact    = $(npm config get save-exact)"

echo
echo "=== 2. A USER-level ~/.npmrc changes the default ==="
cat > "$HOME/.npmrc" <<'EOF'
save-exact=true
registry=https://user-level.example.com/
EOF
echo "  wrote ~/.npmrc:"
sed 's/^/    /' "$HOME/.npmrc"
echo "  registry   = $(npm config get registry)"
echo "  save-exact = $(npm config get save-exact)"

echo
echo "=== 3. A PROJECT-level .npmrc overrides the user level ==="
cat > "$LAB/project/.npmrc" <<'EOF'
registry=https://project-level.example.com/
EOF
echo "  wrote ./.npmrc:"
sed 's/^/    /' "$LAB/project/.npmrc"
echo "  registry   = $(npm config get registry)   <- project wins"
echo "  save-exact = $(npm config get save-exact)              <- still from user level"
echo "  -> the files MERGE. Project only overrides the keys it actually sets."

echo
echo "=== 4. The command line beats every file ==="
echo "  registry = $(npm config get registry --registry=https://cli.example.com/)"

echo
echo "=== 5. Where is each setting coming from? ==="
echo "  'npm config list' reports the origin of every value:"
npm config list 2>/dev/null \
  | grep -v -e 'node bin location' -e 'node version' -e 'npm version' \
            -e 'npm local prefix' -e 'cwd = ' -e 'HOME = ' -e 'Run `npm config' \
  | sed "s|$LAB|<SANDBOX>|g" | sed 's/^/    /' | grep -v '^    $'directive_placeholder

echo
echo "=== 6. Which directory counts as 'the project'? ==="
cd "$LAB/project/nested" || exit 1
echo "  cwd is project/nested, which has no .npmrc and no package.json."
echo "  registry = $(npm config get registry)"
echo "  -> npm looks for .npmrc in the LOCAL PREFIX -- the nearest ancestor"
echo "     containing package.json or node_modules -- not simply the nearest"
echo "     ancestor containing an .npmrc. Here that ancestor is project/, so"
echo "     project/.npmrc applies even though we are one level down."

echo
echo "=== 7. Scoped registries: different scopes, different servers ==="
cd "$LAB/project" || exit 1
cat > "$LAB/project/.npmrc" <<'EOF'
registry=https://registry.npmjs.org/
@acme:registry=https://npm.pkg.github.com/
@internal:registry=https://nexus.example.com/repository/npm/
EOF
echo "  wrote ./.npmrc:"
sed 's/^/    /' "$LAB/project/.npmrc"
echo "  default scope   -> $(npm config get registry)"
echo "  @acme:registry  -> $(npm config get @acme:registry)"
echo "  @internal:...   -> $(npm config get @internal:registry)"
echo "  -> 'npm i lodash' goes to npmjs.org; 'npm i @acme/widget' goes to GitHub."
echo "     ONE project can pull from several registries at once."

echo
echo "=== 8. Environment variables are expanded inside .npmrc ==="
cat > "$LAB/project/.npmrc" <<'EOF'
registry=${LAB_REGISTRY}
@acme:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
EOF
echo "  wrote ./.npmrc (note the LITERAL \${...} placeholders):"
sed 's/^/    /' "$LAB/project/.npmrc"
export LAB_REGISTRY="https://expanded-from-env.example.com/"
echo "  with LAB_REGISTRY set, npm expands it at read time:"
echo "    registry = $(npm config get registry)"
unset LAB_REGISTRY
echo "  with LAB_REGISTRY unset, the placeholder stays literal:"
echo "    registry = $(npm config get registry)"
echo "  -> THIS is what makes the file safe to commit: the secret never"
echo "     appears in it, only the name of the variable holding it."
echo "  -> and an unset variable does not error -- it silently leaves garbage,"
echo "     which is the single most common private-registry failure in CI."

echo
echo "=== 9. npm refuses to print auth tokens back to you ==="
export NODE_AUTH_TOKEN="tok_example_value"
echo "  \$ npm config get //npm.pkg.github.com/:_authToken"
npm config get //npm.pkg.github.com/:_authToken 2>&1 | grep -v 'debug-0.log' | sed 's/^/    /' 
echo "  -> a deliberate guard: token-shaped keys are 'protected' and cannot be"
echo "     read back through the CLI, so they do not end up in shell history,"
echo "     CI logs, or a screen share. 'npm config list' redacts them too."
unset NODE_AUTH_TOKEN

echo "=== 10. The precedence order, highest first ==="
cat <<'EOF'
    1. command line flags        --registry=...
    2. environment variables     npm_config_registry=...
    3. project .npmrc            ./.npmrc  (nearest ancestor directory)
    4. user .npmrc               ~/.npmrc
    5. global .npmrc             $PREFIX/etc/npmrc
    6. npm built-in defaults
EOF

echo
echo "=== 11. Environment variables as config, demonstrated ==="
echo "  registry = $(npm_config_registry=https://from-env.example.com/ npm config get registry)"
echo "  -> any setting can be set as npm_config_<key>, which is how CI images"
echo "     configure npm without writing a file at all."

echo
echo "=== done: the sandbox directory has been removed ==="
```

### Expected output

Generated by running the file above. The sandbox path is normalised to `<SANDBOX>` and volatile lines (npm/node versions, cwd) are filtered, so this reproduces across machines — verified by running it twice and diffing:

```
=== 0. Sandbox ===
  working in a temporary directory; HOME is redirected so your real
  ~/.npmrc is never read or written.

=== 1. With no .npmrc anywhere, npm uses its built-in defaults ===
  registry      = https://registry.npmjs.org/
  save-exact    = false

=== 2. A USER-level ~/.npmrc changes the default ===
  wrote ~/.npmrc:
    save-exact=true
    registry=https://user-level.example.com/
  registry   = https://user-level.example.com/
  save-exact = true

=== 3. A PROJECT-level .npmrc overrides the user level ===
  wrote ./.npmrc:
    registry=https://project-level.example.com/
  registry   = https://project-level.example.com/   <- project wins
  save-exact = true              <- still from user level
  -> the files MERGE. Project only overrides the keys it actually sets.

=== 4. The command line beats every file ===
  registry = https://cli.example.com/

=== 5. Where is each setting coming from? ===
  'npm config list' reports the origin of every value:
    ; "user" config from <SANDBOX>/fakehome/.npmrc
    
    ; registry = "https://user-level.example.com/" ; overridden by project
    save-exact = true
    save-prefix = ""
    
    ; "project" config from <SANDBOX>/project/.npmrc
    
    registry = "https://project-level.example.com/"
    

=== 6. Which directory counts as 'the project'? ===
  cwd is project/nested, which has no .npmrc and no package.json.
  registry = https://project-level.example.com/
  -> npm looks for .npmrc in the LOCAL PREFIX -- the nearest ancestor
     containing package.json or node_modules -- not simply the nearest
     ancestor containing an .npmrc. Here that ancestor is project/, so
     project/.npmrc applies even though we are one level down.

=== 7. Scoped registries: different scopes, different servers ===
  wrote ./.npmrc:
    registry=https://registry.npmjs.org/
    @acme:registry=https://npm.pkg.github.com/
    @internal:registry=https://nexus.example.com/repository/npm/
  default scope   -> https://registry.npmjs.org/
  @acme:registry  -> https://npm.pkg.github.com/
  @internal:...   -> https://nexus.example.com/repository/npm/
  -> 'npm i lodash' goes to npmjs.org; 'npm i @acme/widget' goes to GitHub.
     ONE project can pull from several registries at once.

=== 8. Environment variables are expanded inside .npmrc ===
  wrote ./.npmrc (note the LITERAL ${...} placeholders):
    registry=${LAB_REGISTRY}
    @acme:registry=https://npm.pkg.github.com/
    //npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
  with LAB_REGISTRY set, npm expands it at read time:
    registry = https://expanded-from-env.example.com/
  with LAB_REGISTRY unset, the placeholder stays literal:
    registry = ${LAB_REGISTRY}
  -> THIS is what makes the file safe to commit: the secret never
     appears in it, only the name of the variable holding it.
  -> and an unset variable does not error -- it silently leaves garbage,
     which is the single most common private-registry failure in CI.

=== 9. npm refuses to print auth tokens back to you ===
  $ npm config get //npm.pkg.github.com/:_authToken
    npm error The //npm.pkg.github.com/:_authToken option is protected, and cannot be retrieved in this way
  -> a deliberate guard: token-shaped keys are 'protected' and cannot be
     read back through the CLI, so they do not end up in shell history,
     CI logs, or a screen share. 'npm config list' redacts them too.
=== 10. The precedence order, highest first ===
    1. command line flags        --registry=...
    2. environment variables     npm_config_registry=...
    3. project .npmrc            ./.npmrc  (nearest ancestor directory)
    4. user .npmrc               ~/.npmrc
    5. global .npmrc             $PREFIX/etc/npmrc
    6. npm built-in defaults

=== 11. Environment variables as config, demonstrated ===
  registry = https://from-env.example.com/
  -> any setting can be set as npm_config_<key>, which is how CI images
     configure npm without writing a file at all.

=== done: the sandbox directory has been removed ===
```

---

## 7. Common pitfalls and traps

1. **Committing a token.** Once pushed it is compromised, and deleting the commit does not help — it is in the reflog, in forks, and possibly in a scraper's database. **Revoke it, then rotate.** Use `${VAR}` substitution instead.
2. **Expecting an unset `${VAR}` to fail loudly.** It does not; the literal text becomes the value, and you get a 401 that looks like a permissions problem.
3. **Assuming the nearest `.npmrc` above you is the project config.** It is the one in the **local prefix** — the nearest ancestor with `package.json` or `node_modules`. In a monorepo workspace this is frequently not the repository root.
4. **Forgetting the leading `//` on auth keys.** It is `//npm.pkg.github.com/:_authToken`, not `npm.pkg.github.com:_authToken`. The key encodes the registry's host *and path*, and a wrong key is silently ignored.
5. **Setting a scope's registry but not its credentials.** Requests go to the right server and get rejected. **Registry and token are two separate settings** and both are needed.
6. **Trailing-slash mismatches.** `//npm.pkg.github.com/:_authToken` and a registry of `https://npm.pkg.github.com` (no trailing slash) can fail to match. Keep the trailing slash on both.
7. **Running `npm login` and wondering why CI still fails.** `npm login` writes to your **user** `.npmrc`, on your machine only. CI needs the token supplied through its own secret store.
8. **A committed `.npmrc` overriding a developer's proxy.** A project file setting `registry=` wholesale defeats a developer's corporate proxy. Prefer scoped settings — `@acme:registry=` — which leave the default alone.

---

## 8. Check your understanding

1. **`~/.npmrc` sets `registry=A`; the project's sets `save-exact=true`. What is the registry?**
   <details><summary>Answer</summary>A. The files merge per key — the project file does not mention <code>registry</code>, so the user-level value stands, and <code>save-exact</code> comes from the project. A project <code>.npmrc</code> is a patch, not a replacement.</details>

2. **Why can a project `.npmrc` be committed to a public repository?**
   <details><summary>Answer</summary>Because it contains configuration, not credentials. Registry URLs and scope mappings are not secret — they are facts about where the project's packages live. The one line that touches a secret names an environment variable, <code>${NODE_AUTH_TOKEN}</code>, which npm expands at read time from an environment the repository does not contain.</details>

3. **You are in a monorepo at `packages/api/` which has its own `package.json`. The registry setting in the repository-root `.npmrc` is ignored. Why?**
   <details><summary>Answer</summary>Because npm's local prefix is the nearest ancestor with <code>package.json</code> — which is <code>packages/api/</code>, not the root. So the project config is <code>packages/api/.npmrc</code>, and the root file is never read as project config. Fix by adding an <code>.npmrc</code> per package, putting the setting at the user level, or setting <code>npm_config_registry</code> in the environment.</details>

4. **`npm install @acme/widget` returns 404 from `registry.npmjs.org`, but the package exists on GitHub Packages. What is missing?**
   <details><summary>Answer</summary>The scope-to-registry mapping: <code>@acme:registry=https://npm.pkg.github.com/</code>. Without it, <code>@acme/widget</code> resolves against the default registry, where it does not exist — hence a 404 rather than a 401. A <b>404</b> usually means the wrong registry; a <b>401 or 403</b> usually means the right registry and the wrong credentials. That distinction is the fastest first diagnostic.</details>

5. **How do you check whether an auth token is configured, given npm will not print it?**
   <details><summary>Answer</summary>Do not try to read it back — that is blocked by design. Instead check the source (<code>echo $NODE_AUTH_TOKEN | wc -c</code>, which reveals length without content), or test it end to end with <code>npm whoami --registry=https://npm.pkg.github.com/</code>, which returns your username if the token is valid and errors if not.</details>

---

## 9. Practice — independent task

**Part 1 — map your own setup.** Run `npm config list` and `npm config list -l`. Identify every `.npmrc` in play, and for three settings state which file supplied the value and which files were overridden.

**Part 2 — build the precedence ladder.** In a sandbox (copy the lab's `HOME` redirection so you cannot damage your real config), set the *same* key at all four levels — global, user, project, command line — and confirm experimentally which wins. **Predict the order before running it.**

**Part 3 — a multi-registry project.** Create a `package.json` and an `.npmrc` routing three scopes to three different registries. Using `npm view <pkg> --json` against the **public** registry only, show that scope routing changes which host is contacted. Use `npm view --loglevel=http` or a local proxy to observe the request.

**Part 4 — the substitution failure.** Write an `.npmrc` using `${MY_TOKEN}`. Run an install with the variable set to a wrong value, then unset. **Record the exact error text in each case** and write one line on how to tell them apart — this is the diagnostic you will want at 2am.

**Part 5 — the monorepo trap.** Build a two-package workspace with an `.npmrc` only at the root. Show that `npm config get registry` gives different answers at the root and inside a package. Then fix it three ways and state the trade-off of each.

**Safety:** do not publish anything; do not use a real token outside a sandbox; revoke any token you create for this exercise afterwards.

**Done when:** you can state for any setting on your machine which file it came from; part 2's measured order matches your prediction; part 4 has both error texts written down; and part 5 has three fixes with trade-offs.

---

## Before moving on

You can state npm's precedence order and find where any value came from, route scopes to different registries, explain what the local prefix is and why it is not the nearest `.npmrc`, and write a committable `.npmrc` that references a secret without containing one.

**Recap:** a package name is not a location — npm resolves it against a **registry**, default `registry.npmjs.org`. Configuration comes from several `.npmrc` files that **merge per key**, with precedence CLI → environment → project → user → global → defaults; `npm config list` shows the origin of each value and marks what was overridden. **"Project" means the local prefix** — the nearest ancestor with `package.json` or `node_modules` — which is why monorepo workspaces do not see the root file. **Scopes are routing keys**: `@acme:registry=` sends one namespace to another server while everything else keeps the default. `${VAR}` is expanded at read time, which is what makes the file safe to commit — and an unset variable produces a literal, not an error, which is the classic CI 401. npm refuses to print token-shaped settings back to you, deliberately.

**Next:** [[02-authentication-and-private-packages|Authentication and Private Packages]] — tokens, `npm login`, GitHub Packages, CI credentials, publishing, and installing straight from a Git repository.

---

## Related

- [[02-authentication-and-private-packages|Authentication and Private Packages]] — the credential half
- [[devops/01-linux/10-environment-variables|Environment Variables]] — what `${VAR}` substitution depends on
- [[devops/09-secret-management/index|Secret Management]] — where tokens should actually live
- [[devops/06-ci-cd/10-pipeline-security|Pipeline Security]] — credentials in CI
- [[tools/index|tools/]] — the parent folder
