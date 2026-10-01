# Labs

The runnable code behind the lessons. Every worked example marked "verified" in a lesson lives here as real files, with tests, so it can be re-run whenever Node, Python or a library changes, and so a lesson can't quietly drift away from code that works.

## Running them

From the vault root:

```bash
python3 labs/run.py                    # every lab
python3 labs/run.py layers solid-principles   # just these
python3 labs/run.py --drift-only       # only check lessons still match the lab files (fast, offline)
```

A lab **fails** if any of its commands exits non-zero, **or** if a file it lists under `embedded` no longer appears word for word in its lesson. If you edit a code block in a lesson, edit the lab file too (or the other way round), then run the lab.

## Requirements

- **Node 23.6 or later** for the JavaScript and TypeScript labs. They use the built-in test runner (`node --test`) and run `.ts` files directly by stripping types, so they can't use TypeScript features that generate code: parameter properties (`constructor(private x: T)`) and enums. `transactional-outbox` uses `node:sqlite`, built in since Node 22.5. Checked with Node 26.
- **npm** for `layer-vs-feature-eslint`. The first run does `npm ci`; `node_modules/` is git-ignored.
- **uv** for the Python labs. Each command declares its own packages (`uv run --no-project --with django ...`), so there is no virtualenv to manage. The first run needs a network connection to fetch them.

## Adding a lab

1. Make a folder `labs/<lesson-name>/` with the code and its tests.
2. Add a `lab.json`:

```json
{
  "lesson": "path/to/the-lesson.md",
  "run": [["node", "--test"]],
  "embedded": ["the-file-shown-in-the-lesson.ts"]
}
```

`setup` (optional) runs once when `node_modules/` is missing. List under `embedded` only files the lesson shows **in full**; fragments and helper files stay out.

3. In the lesson, next to the "Run it" step, add: **Lab:** these files are in `labs/<name>/`. From the vault root, `python3 labs/run.py <name>` runs them and checks this page still shows the same code.
4. Run `python3 labs/run.py <name>`.

## The labs

| Lab | Lesson | What it shows |
|---|---|---|
| `clean-code` | [[concepts/04-best-practices/01-clean-code\|clean code]] | A tangled function refactored, behaviour pinned by tests |
| `coupling-and-cohesion` | [[concepts/04-best-practices/08-coupling-and-cohesion\|coupling and cohesion]] | A tool measuring fan-in, fan-out, instability and import cycles — run it on your own `src/` |
| `solid-principles` | [[concepts/04-best-practices/05-solid-principles\|SOLID]] | Open/closed fees, dependency-inverted checkout, a Liskov violation |
| `layers` | [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories\|layers]] | Controller, service, repository with no framework |
| `layer-vs-feature-eslint` | [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature\|layer vs feature]] | Express and React feature boundaries enforced by ESLint |
| `layer-vs-feature-django-by-feature` | same | Apps in `apps/`, cross-app services, an import-linter contract |
| `layer-vs-feature-django-by-layer` | same | One `core` app with model and view packages |
| `layer-vs-feature-flask` | same | Blueprints per feature, an app factory, import-linter contracts |
| `dependency-injection` | [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring\|DI and wiring]] | The request-scope bug, reproduced and fixed two ways |
| `hexagonal-architecture` | [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture\|hexagonal]] | Ports in the domain, adapters outside, tests with no infrastructure |
| `modular-monolith` | [[backend/03-structuring-a-backend/05-modular-monolith-to-services\|modular monolith]] | Modules talking through events; at-least-once delivery and idempotency |
| `creational-patterns` | [[concepts/03-design-patterns/01-creational-patterns\|creational patterns]] | A singleton leaking state between tests; a checking builder |
| `structural-patterns` | [[concepts/03-design-patterns/02-structural-patterns\|structural patterns]] | Retry, cache and log wrappers, and why their order matters |
| `behavioral-patterns` | [[concepts/03-design-patterns/03-behavioral-patterns\|behavioural patterns]] | An order lifecycle as a state machine with observers |
| `testing-fundamentals` | [[concepts/04-best-practices/04-testing-fundamentals\|testing fundamentals]] | Stub, spy and fake clock; a month-end bug reproduced with fake timers; integration tests over real HTTP and SQLite |
| `transactional-outbox` | [[architecture/03-architectural-patterns/05-transactional-outbox\|transactional outbox]] | Lost and phantom events, the outbox and relay, deduplication |

Older labs written before this folder existed — the `dsa/04-patterns` labs, the databases and compilers labs — still live inside their lessons and are not run by this script yet.
