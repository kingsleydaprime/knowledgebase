# Why Go, and the Toolchain

**[Beginner]** — What Go was designed to fix, the deliberate omissions that follow from that, and the single built-in tool that replaces the pile you're used to.

**Source:** `[reference]` — cross-referenced against [roadmap.sh Go](https://roadmap.sh/golang). No Go project in this vault yet; the first one belongs in [[project-ideas|Project Ideas]] before these notes claim to be knowledge.

## The problem Go was built for

Go came out of Google in 2009, and its design goals are unusually legible: large codebases, many engineers, slow builds, and servers that need to handle a lot of concurrent connections.

Everything distinctive about the language falls out of those four:

| Goal | What it produced |
|---|---|
| Fast compilation | No header files, no circular imports, strict unused-import errors |
| Many engineers, one codebase | `gofmt` — one formatting, non-negotiable, argument over |
| Concurrent servers | Goroutines and channels in the language, not a library |
| Readable at scale | A small spec, few features, explicit error handling |

The last one is the controversial one. Go is *deliberately* less expressive than Java or Rust. The bet is that a language you can hold entirely in your head produces code that a stranger can read at 3am during an incident — and that this matters more than elegance. Whether you agree depends on whether you've been the stranger.

## The deliberate omissions

Things Go does not have, on purpose:

- **No exceptions.** Errors are ordinary values you return and check. Verbose, but the control flow is visible on the page. → [[languages/02-go/05-errors|Errors]]
- **No inheritance.** Composition and interfaces only. There is no `extends`. → [[languages/02-go/04-methods-and-interfaces|Methods and Interfaces]]
- **No constructors, no destructors, no operator overloading, no ternary.**
- **No generics until 1.18** (2022). They exist now, and the community remains cautious about them. → [[languages/02-go/09-generics|Generics]]

Coming from Java this feels like a language with things missing. That's the correct reading — the question is whether you miss them in practice, and for network services the honest answer is mostly no.

## Install and the toolchain

```bash
# Fedora
sudo dnf install golang
# or download from go.dev/dl and untar into /usr/local

go version
go env GOPATH GOROOT GOBIN
```

Go ships one tool that does what `mvn`/`gradle` + `npm` + `prettier` + `eslint` + `jest` do elsewhere:

```bash
go run main.go          # compile to a temp binary and run it
go run .                # run the package in this directory
go build                # produce a binary in the current directory
go build -o bin/api ./cmd/api
go install ./cmd/api    # build and drop the binary in $GOBIN

go test ./...           # test every package, recursively
go vet ./...            # static analysis for real bug patterns
go fmt ./...            # format (gofmt); do not argue about style
go mod tidy             # add missing deps, drop unused ones
go doc net/http.Server  # docs in the terminal
```

`./...` means "this package and everything under it" and appears in nearly every real command.

### Cross-compilation, which is genuinely a feature

```bash
GOOS=linux GOARCH=amd64 go build -o bin/api-linux ./cmd/api
GOOS=darwin GOARCH=arm64 go build -o bin/api-mac ./cmd/api
GOOS=windows GOARCH=amd64 go build -o bin/api.exe ./cmd/api
```

No toolchain to install, no container needed. This is why Go dominates CLI tooling and why so much of the infrastructure in [[devops/README|devops/]] — Docker, Kubernetes, Terraform, Prometheus, the `gh` CLI — is written in it. One static binary, no runtime to install on the target.

That last point is worth sitting with: a Go binary has no JVM to install and no `node_modules`. It's a single file you can `scp` to a server. Compare the Dockerfile you'd write for [[backend/frameworks/java/README|a Spring Boot service]] against `FROM scratch` + one binary.

## A first program

```go
package main

import "fmt"

func main() {
    fmt.Println("hello")
}
```

Three things are already unusual:

**`package main` is special.** A package named `main` with a `func main()` compiles to an executable. Anything else compiles to a library. There is no separate "is this an app or a lib" config.

**Imports are paths, not names.** `"fmt"` is a standard-library path; your own would be `"github.com/you/project/internal/store"`. The last path segment becomes the identifier.

**An unused import is a compile error.** Not a warning. This is the fast-compilation goal showing through, and it's the first thing that will annoy you.

```go
import "os"  // "os" imported and not used  → build fails
```

The intent is that dependency lists never rot. You will still find it irritating for about a week.

## `gofmt` is not negotiable

```bash
gofmt -l .        # list files that aren't formatted
gofmt -w .        # rewrite them
```

Go uses tabs, brace placement is fixed, and there is no config file. Every Go codebase looks the same. Whether you like the choices is beside the point — the language removed a category of argument, permanently, and the time saved is real.

Wire it into a pre-commit hook the same way as any other check → [[git/17-hooks-and-signing|Hooks and Signing]].

## Where Go actually fits

Being honest about it, since a language note that only lists strengths is useless:

**Good at:** network services, CLI tools, infrastructure, anything where deployment simplicity and predictable concurrency matter more than expressiveness. Compilation is fast enough that the edit-test loop feels like a scripting language.

**Bad at:** heavy generic abstraction (the type system fights you), numerical/scientific work (no operator overloading, weak numeric tower), GUI applications, and anything where you'd want a rich domain model with inheritance. Go code is often more verbose than the equivalent Java or Python and that verbosity is intentional, not a gap to be optimised away.

**The honest complaint:** `if err != nil` three times per function is genuinely tedious, and no amount of "explicit is better" rhetoric makes it not tedious. You get used to it. Some people never do.

---

## Related
- [[languages/02-go/02-language-fundamentals|Language Fundamentals]] — the syntax
- [[languages/02-go/12-modules-and-project-layout|Modules and Project Layout]] — `go.mod` in depth
- [[backend/frameworks/go/README|Go Backends]] — the frameworks built on this
- [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]] — where goroutines sit among the alternatives
- [[languages/02-go/README|Go course map]]
