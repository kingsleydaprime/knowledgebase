# Modules and Project Layout

**[Intermediate]** — `go.mod`, the versioning rules that are stricter than npm's, and the layout argument you should know before someone tells you to use `pkg/`.

## Modules

```bash
go mod init github.com/kingsleydaprime/myservice
```

The module path is a **URL**, because that's how Go fetches dependencies — there's no central registry like npm or Maven Central. `go get github.com/foo/bar` fetches from GitHub directly (via a module proxy, by default).

```
module github.com/kingsleydaprime/myservice

go 1.24

require (
    github.com/go-chi/chi/v5 v5.1.0
    golang.org/x/sync v0.8.0
)

require github.com/x/indirect v1.0.0 // indirect
```

```bash
go get github.com/go-chi/chi/v5      # add or upgrade
go get -u ./...                      # upgrade all (minor/patch)
go get example.com/pkg@v1.2.3        # pin exactly
go get example.com/pkg@none          # remove
go mod tidy                          # add what's imported, drop what isn't
go mod download
go mod why github.com/x/y            # WHY is this in my graph?
go mod graph                         # the full dependency graph
```

`go mod tidy` before every commit. It's the `npm prune` you never remember to run, and it's fast enough to be a pre-commit hook.

**`go.sum` is a checksum file, not a lockfile.** Versions are pinned in `go.mod`; `go.sum` records cryptographic hashes so a dependency can't be swapped underneath you. Commit both. Verification runs against the public checksum database by default, which is a meaningfully stronger [[devops/06-ci-cd/10-pipeline-security|supply-chain]] story than npm's.

## Minimal Version Selection

The rule that surprises people coming from npm:

> Go builds with the **lowest** version that satisfies every requirement, not the highest available.

If your module needs `foo v1.2.0` and a dependency needs `foo v1.4.0`, you get **v1.4.0** — the minimum that satisfies both. Not v1.9.0, even if it exists.

The consequence is that **builds are reproducible without a lockfile**. Adding a dependency never silently upgrades an unrelated one. Upgrades only happen when you ask for them, which is the opposite of the npm default and much calmer to operate.

## Semantic import versioning

The other rule that catches people:

> **A major version ≥ 2 must appear in the import path.**

```
github.com/go-chi/chi/v5      ← the /v5 is part of the path
```

This is why you see `/v2`, `/v5` in import paths. It means v1 and v5 of the same library can coexist in one build — a real advantage during migrations — at the cost of a module path that has to change on every major release. It's the mechanism that makes "diamond dependency" conflicts rare in Go.

## Package rules

A **package** is a directory. All files in it share one package name, and there's no nesting relationship: `foo/bar` is not a sub-package of `foo`, just a different package.

**Capitalisation is the visibility mechanism.** No `public`/`private` keywords:

```go
func Exported()    { }   // visible outside the package
func unexported()  { }   // package-only
type User struct {
    Name string          // marshalled by encoding/json
    email string         // not — and json is silent about it
}
```

Two special directory names the toolchain enforces:

- **`internal/`** — importable only by code rooted at its parent. `myservice/internal/store` is invisible to anyone importing your module. This is the only real access control Go has above package level, and it's the right default for application code.
- **`vendor/`** — if present, `go build` uses it instead of the module cache. `go mod vendor` creates it. Mostly obsolete now that the proxy and checksum DB exist; still used where builds must run with no network.

Package names should be short, lowercase, no underscores, and **not** repeat in the identifier: `http.Server`, not `http.HTTPServer`. `chi.NewRouter()` reads well; `chi.NewChiRouter()` doesn't. A package named `util` or `common` is a design smell — it means you haven't decided what it's for.

## Layout

This is contentious, so here's the honest version.

**`golang-standards/project-layout`** is the repo everyone links, with `cmd/`, `pkg/`, `internal/`, `api/`, `configs/`, `build/`. It is **not official** — the name is misleading and the Go team has explicitly said so. Following it for a small service gives you eleven directories holding four files.

**What's actually agreed:**

```
myservice/
├── go.mod
├── main.go              ← for a single binary, this is fine
├── cmd/
│   ├── api/main.go      ← use cmd/ only when you have MULTIPLE binaries
│   └── worker/main.go
└── internal/
    ├── user/            ← by FEATURE: handler, service, store together
    │   ├── handler.go
    │   ├── service.go
    │   └── store.go
    └── order/
```

- **`cmd/<name>/main.go`** — one directory per binary. Skip it entirely if you have one.
- **`internal/`** — everything else, unless you're publishing a library.
- **`pkg/`** — a convention for "importable by others". Widely considered unnecessary; if it's importable, just put it at the top level.
- **Organise by feature, not by layer.** `internal/user/` beats `internal/handlers/`, `internal/services/`, `internal/repositories/` — adding a feature touches one directory instead of three, and Go's package-level visibility actually enforces the boundary. → [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|Organising by Layer vs by Feature]]

**Start flat.** A `main.go` and a couple of packages is a perfectly good Go service. Structure when the flatness hurts, not before — the cost of moving a file is one `git mv` and the compiler telling you what broke.

## Workspaces

For working on several modules at once without publishing:

```bash
go work init ./service ./sharedlib
go work use ./another
```

`go.work` overrides module resolution locally. **Don't commit it** — it's a developer-machine file, and committing it breaks CI in confusing ways. The alternative it replaced was a `replace` directive in `go.mod`, which people forgot to remove before merging.

## Publishing

There's no publish step. Tag the repo and it's released:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The proxy picks it up on first request. For v2+, remember the module path has to gain `/v2` — either in a subdirectory or on a branch.

That's the whole distribution model: a git tag. See [[git/11-tags-and-versioning|Tags and Versioning]] for what those tags should mean.

---

## Related
- [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|Organising by Layer vs by Feature]] — the argument, in general
- [[git/11-tags-and-versioning|Tags and Versioning]] — SemVer, which Go enforces structurally
- [[devops/06-ci-cd/10-pipeline-security|Securing the Pipeline]] — the checksum database in context
- [[languages/01-java/03-tooling/01-build-tools|Java: Build Tools]] — Maven/Gradle, for contrast
- [[languages/02-go/README|Go course map]]
