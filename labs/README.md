# Labs

The runnable code behind the lessons. Every worked example marked "verified" in a lesson lives here as real files, with tests, so it can be re-run whenever Node, Python or a library changes, and so a lesson can't quietly drift away from code that works.

## Running them

From the vault root:

```bash
python3 labs/run.py                    # every lab
python3 labs/run.py layers/typescript solid-principles/javascript   # just these
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

1. Make a folder `labs/<lesson>/<language>/` with the code and its tests — the lesson folder groups every language's lab for that lesson.
2. Add a `lab.json`:

```json
{
  "lesson": "path/to/the-lesson.md",
  "run": [["node", "--test"]],
  "embedded": ["the-file-shown-in-the-lesson.ts"]
}
```

`setup` (optional) runs once when `node_modules/` is missing. List under `embedded` only files the lesson shows **in full**; fragments and helper files stay out.

3. In the lesson, next to the "Run it" step, add: **Lab:** these files are in `labs/<lesson>/<language>/`. From the vault root, `python3 labs/run.py <lesson>/<language>` runs them and checks this page still shows the same code.
4. Run `python3 labs/run.py <name>`.

## The labs

One folder per lesson; inside it, one folder per language (or, for layer vs feature, per framework). Lessons with an "…in other languages" companion list both.

| Lesson folder | Lessons | Labs inside |
|---|---|---|
| `backend-best-practices/` | [[backend/07-practices/01-backend-best-practices\|backend best practices]] · [[backend/07-practices/01b-backend-best-practices-in-other-languages\|backend best practices in other languages]] | javascript, python, go, java, rust, c, cpp, csharp |
| `behavioral-patterns/` | [[concepts/03-design-patterns/03-behavioral-patterns\|behavioral patterns]] · [[concepts/03-design-patterns/03b-behavioral-patterns-in-other-languages\|behavioral patterns in other languages]] | typescript, python, go, java, rust, c, cpp, csharp |
| `clean-code/` | [[concepts/04-best-practices/01-clean-code\|clean code]] | javascript |
| `coupling-and-cohesion/` | [[concepts/04-best-practices/08-coupling-and-cohesion\|coupling and cohesion]] · [[concepts/04-best-practices/08b-coupling-and-cohesion-in-other-languages\|coupling and cohesion in other languages]] | javascript, python, go, java, rust, c, cpp, csharp |
| `creational-patterns/` | [[concepts/03-design-patterns/01-creational-patterns\|creational patterns]] | typescript |
| `dependency-injection/` | [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring\|dependency injection and wiring]] · [[backend/03-structuring-a-backend/03b-dependency-injection-in-other-languages\|dependency injection in other languages]] | typescript, python, go, java, rust, c, cpp, csharp |
| `hexagonal-architecture/` | [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture\|hexagonal and clean architecture]] · [[backend/03-structuring-a-backend/04b-hexagonal-architecture-in-other-languages\|hexagonal architecture in other languages]] | typescript, python, go, java, rust, c, cpp, csharp |
| `input-validation-and-output-encoding/` | [[cybersecurity/04-web-security/01-input-validation-and-output-encoding\|input validation and output encoding]] | javascript |
| `layer-vs-feature/` | [[backend/03-structuring-a-backend/02b-organising-by-feature-in-compiled-languages\|organising by feature in compiled languages]] · [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature\|organising by layer vs by feature]] | go, java, rust, c, cpp, csharp, eslint, flask, django-by-feature, django-by-layer |
| `layers/` | [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories\|layers controllers services repositories]] · [[backend/03-structuring-a-backend/01b-layers-in-other-languages\|layers in other languages]] | typescript, python, go, java, rust, c, cpp, csharp |
| `local-and-open-models/` | [[ai-ml/03-ai-engineer/16-local-and-open-models\|local and open models]] | python |
| `modular-monolith/` | [[backend/03-structuring-a-backend/05-modular-monolith-to-services\|modular monolith to services]] · [[backend/03-structuring-a-backend/05b-modular-monolith-in-other-languages\|modular monolith in other languages]] | typescript, python, go, java, rust, c, cpp, csharp |
| `observability/` | [[devops/10-observability/01-observability-fundamentals\|observability fundamentals]] · [[devops/10-observability/01b-observability-in-other-languages\|observability in other languages]] | javascript, python, go, java, rust, c, cpp, csharp |
| `security-headers/` | [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy\|security headers and same origin policy]] · [[cybersecurity/04-web-security/04b-security-headers-in-other-languages\|security headers in other languages]] | javascript, python, go, java, rust, csharp |
| `solid-principles/` | [[concepts/04-best-practices/05-solid-principles\|solid principles]] · [[concepts/04-best-practices/05b-solid-in-other-languages\|solid in other languages]] | javascript, python, go, java, rust, c, cpp, csharp |
| `structural-patterns/` | [[concepts/03-design-patterns/02-structural-patterns\|structural patterns]] · [[concepts/03-design-patterns/02b-structural-patterns-in-other-languages\|structural patterns in other languages]] | typescript, python, go, java, rust, c, cpp, csharp |
| `testing-fundamentals/` | [[concepts/04-best-practices/04-testing-fundamentals\|testing fundamentals]] · [[concepts/04-best-practices/04b-testing-fundamentals-in-other-languages\|testing fundamentals in other languages]] | javascript, python, go, java, rust, c, cpp, csharp |
| `transactional-outbox/` | [[architecture/03-architectural-patterns/05-transactional-outbox\|transactional outbox]] | javascript |

Older labs written before this folder existed — the `dsa/04-patterns` labs, the databases and compilers labs — still live inside their lessons and are not run by this script yet.
