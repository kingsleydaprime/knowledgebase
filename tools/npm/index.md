# npm

**Where your dependencies actually come from, and how you prove you are allowed to have them.**

Two lessons, written to [[COURSE-STANDARD|the course standard]]. This folder is not about using npm — `npm install` needs no explanation — it is about the configuration layer underneath it, which is invisible until a project pulls from a private registry and then becomes most of the problem.

> **It belongs in `tools/` by this folder's own test: if the config file has opinions in it, the opinions belong here.** `.npmrc` is a config file that is almost entirely opinions.

## The lessons

1. [[01-registries-and-the-npmrc-file|Registries and the `.npmrc` File]] — **[Intermediate]** — what a registry is and why `npm install lodash` has to choose one; the precedence order across global, user and project `.npmrc` files and how they **merge per key**; what "the project" actually means (the local prefix, not the nearest `.npmrc` — the monorepo trap); scoped registries routing one project to several servers; and `${VAR}` substitution, which is what makes the file safe to commit.
2. [[02-authentication-and-private-packages|Authentication and Private Packages]] — **[Intermediate]** — tokens and where they should live; the four causes of a 401 in order of likelihood; GitHub Packages' three rules; publishing safely with `--dry-run`; keeping credentials out of Docker layers; and Git URLs as dependencies, with what they cost.

## The one thing to take away

**Configuration belongs in the repository; credentials belong in the environment.** A project `.npmrc` naming `${NODE_AUTH_TOKEN}` is identical on a laptop and in CI — the file says *which* variable, the environment supplies the value. Every recurring npm auth problem is a variation on that separation breaking down:

1. The variable is not set in CI → the literal `${NODE_AUTH_TOKEN}` is used → **401**.
2. The token is committed → the separation is gone → **revoke it, immediately**.
3. `COPY .npmrc` in a Dockerfile → the credential ships inside the image.
4. `npm login` on a laptop → a credential that exists in exactly one place and cannot be reproduced.

## Reading the error before debugging it

| Status | Usually means | Check first |
| :--- | :--- | :--- |
| **404** | wrong registry | the scope mapping — `@acme:registry=` |
| **401** | no credential sent, or invalid | is the environment variable set? |
| **403** | valid credential, insufficient permission | the token's scopes — `read:` vs `write:packages` |

## What is verified

[[01-registries-and-the-npmrc-file|Lesson 01]] ships a runnable lab that **redirects `HOME` into a sandbox so your real `~/.npmrc` is never touched**, contacts no registry, and deletes itself. It demonstrates from a live npm:

- config files **merging per key** — a project file overriding the registry while the user file's `save-exact` survives;
- `npm config list` naming the losing value and what beat it;
- the **local prefix** rule, with project config applying from a subdirectory that has no `.npmrc` of its own;
- three scopes resolving to three different registries;
- `${VAR}` expanding when set and **staying a literal when unset** — the CI 401 in miniature;
- npm **refusing to print a token back**, by design.

It was run twice and diffed to confirm the output reproduces.

[[02-authentication-and-private-packages|Lesson 02]] has no lab, because a real one would need real credentials — it ships a **read-only checklist** instead, which publishes nothing and prints no secrets.

## Related

- [[devops/09-secret-management/01-secret-management|Secret Management]] — the general problem this is one instance of
- [[devops/06-ci-cd/10-pipeline-security|Pipeline Security]] — credentials in a pipeline
- [[git/index|Git]] — Git dependencies authenticate through Git, not through npm
- [[devops/01-linux/10-environment-variables|Environment Variables]] — what `${VAR}` substitution rests on
- [[tools/index|tools/]] — the parent folder
