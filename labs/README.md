# Labs

This folder holds the **tools**; the labs themselves live beside their lessons. Every worked example marked "verified" in a lesson is real files, with tests, so it can be re-run whenever Node, Python or a library changes, and so a lesson can't quietly drift away from code that works.

## Running them

From the vault root:

```bash
python3 labs/run.py                    # every lab
python3 labs/run.py layers-controllers-services-repositories/typescript solid-principles/javascript   # just these
python3 labs/run.py --drift-only       # only check lessons still match the lab files (fast, offline)
```

A lab **fails** if any of its commands exits non-zero, **or** if a file it lists under `embedded` no longer appears word for word in its lesson. If you edit a code block in a lesson, edit the lab file too (or the other way round), then run the lab.

## Requirements

- **Node 23.6 or later** for the JavaScript and TypeScript labs. They use the built-in test runner (`node --test`) and run `.ts` files directly by stripping types, so they can't use TypeScript features that generate code: parameter properties (`constructor(private x: T)`) and enums. `transactional-outbox` uses `node:sqlite`, built in since Node 22.5. Checked with Node 26.
- **npm** for `layer-vs-feature-eslint`. The first run does `npm ci`; `node_modules/` is git-ignored.
- **Go, a JDK, Rust (cargo), GCC and CMake** for the five compiled-language layer-vs-feature labs. Checked with Go 1.26, Java 21, Rust 1.96, GCC 16 and CMake 4.3.
- **Podman** (or Docker) for C# labs: they run inside the official .NET SDK image, so .NET doesn't need installing. The first run downloads the image, about 1 GB.
- **uv** for the Python labs. Each command declares its own packages (`uv run --no-project --with django ...`), so there is no virtualenv to manage. The first run needs a network connection to fetch them.

## Adding a lab

1. Turn the lesson into a folder if it isn't one (`<lesson>.md` → `<lesson>/index.md`, fixing links to it), then put the code and its tests in `<lesson>/labs/<language>/`.
2. Add a `lab.json`:

```json
{
  "lesson": "path/to/the-lesson.md",
  "run": [["node", "--test"]],
  "embedded": ["the-file-shown-in-the-lesson.ts"]
}
```

`setup` (optional) runs once when `node_modules/` is missing. List under `embedded` only files the lesson shows **in full**; fragments and helper files stay out.

3. In the lesson, next to the "Run it" step, add: **Lab:** these files are in `labs/<language>/` beside this lesson. From the vault root, `python3 labs/run.py <lesson>/<language>` runs them and checks this page still shows the same code.
4. Run `python3 labs/run.py <name>`.

## The labs

Each lesson that has labs is a folder: `index.md` is the lesson, `in-other-languages.md` its companion, and `labs/<language>/` the code. The runner names a lab by the lesson folder (without its number) and the language — `python3 labs/run.py dependency-injection-and-wiring/go`.

| Runner name | Lesson | Labs |
|---|---|---|
| `local-and-open-models` | [[ai-ml/03-ai-engineer/16-local-and-open-models/index\|local and open models]] | python |
| `transactional-outbox` | [[architecture/03-architectural-patterns/05-transactional-outbox/index\|transactional outbox]] | javascript |
| `layers-controllers-services-repositories` | [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/index\|layers controllers services repositories]] · [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/in-other-languages\|in other languages]] | typescript, python, go, java, rust, c, cpp, csharp |
| `organising-by-layer-vs-by-feature` | [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index\|organising by layer vs by feature]] · [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/in-compiled-languages\|in compiled languages]] | go, java, rust, c, cpp, csharp, eslint, flask, django-by-feature, django-by-layer |
| `dependency-injection-and-wiring` | [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index\|dependency injection and wiring]] · [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/in-other-languages\|in other languages]] | typescript, python, go, java, rust, c, cpp, csharp |
| `hexagonal-and-clean-architecture` | [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture/index\|hexagonal and clean architecture]] · [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture/in-other-languages\|in other languages]] | typescript, python, go, java, rust, c, cpp, csharp |
| `modular-monolith-to-services` | [[backend/03-structuring-a-backend/05-modular-monolith-to-services/index\|modular monolith to services]] · [[backend/03-structuring-a-backend/05-modular-monolith-to-services/in-other-languages\|in other languages]] | typescript, python, go, java, rust, c, cpp, csharp |
| `backend-best-practices` | [[backend/07-practices/01-backend-best-practices/index\|backend best practices]] · [[backend/07-practices/01-backend-best-practices/in-other-languages\|in other languages]] | javascript, python, go, java, rust, c, cpp, csharp |
| `creational-patterns` | [[concepts/03-design-patterns/01-creational-patterns/index\|creational patterns]] | typescript |
| `structural-patterns` | [[concepts/03-design-patterns/02-structural-patterns/index\|structural patterns]] · [[concepts/03-design-patterns/02-structural-patterns/in-other-languages\|in other languages]] | typescript, python, go, java, rust, c, cpp, csharp |
| `behavioral-patterns` | [[concepts/03-design-patterns/03-behavioral-patterns/index\|behavioral patterns]] · [[concepts/03-design-patterns/03-behavioral-patterns/in-other-languages\|in other languages]] | typescript, python, go, java, rust, c, cpp, csharp |
| `clean-code` | [[concepts/04-best-practices/01-clean-code/index\|clean code]] | javascript |
| `testing-fundamentals` | [[concepts/04-best-practices/04-testing-fundamentals/index\|testing fundamentals]] · [[concepts/04-best-practices/04-testing-fundamentals/in-other-languages\|in other languages]] | javascript, python, go, java, rust, c, cpp, csharp |
| `solid-principles` | [[concepts/04-best-practices/05-solid-principles/index\|solid principles]] · [[concepts/04-best-practices/05-solid-principles/in-other-languages\|in other languages]] | javascript, python, go, java, rust, c, cpp, csharp |
| `coupling-and-cohesion` | [[concepts/04-best-practices/08-coupling-and-cohesion/index\|coupling and cohesion]] · [[concepts/04-best-practices/08-coupling-and-cohesion/in-other-languages\|in other languages]] | javascript, python, go, java, rust, c, cpp, csharp |
| `input-validation-and-output-encoding` | [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index\|input validation and output encoding]] | javascript |
| `security-headers-and-same-origin-policy` | [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/index\|security headers and same origin policy]] · [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/in-other-languages\|in other languages]] | javascript, python, go, java, rust, csharp |
| `observability-fundamentals` | [[devops/10-observability/01-observability-fundamentals/index\|observability fundamentals]] · [[devops/10-observability/01-observability-fundamentals/in-other-languages\|in other languages]] | javascript, python, go, java, rust, c, cpp, csharp |

Older labs written before this setup — the `dsa/04-patterns` labs, the databases and compilers labs — are still code blocks inside their lessons and are not run by this script yet.

**On the website**, lab folders are not published: Quartz lowercases paths and renames any file named after its folder (`go/go.mod` becomes `go/index.mod`), which would break downloaded code. Instead, every lab path in a lesson links to that folder on GitHub, where filenames are exact and the code can be browsed or downloaded. Build output (`node_modules`, `target/`, caches) is excluded from git entirely. A per-lab "download as zip" link is a possible next step.
