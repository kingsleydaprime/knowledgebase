# Concepts Interview — Patterns, Code Quality & Review

The round that asks *"can you work in a codebase with other people?"* It shows up as a design-patterns question, a code-review exercise, or a "how would you refactor this" — and the grading is almost entirely about judgement rather than recall.

From [[concepts/03-design-patterns/README|design patterns]], [[concepts/04-best-practices/README|best practices]], and [[foundations/software-engineering/README|software engineering]].

---

### Q1. [Intermediate] 🔥 Name a design pattern you've used and why.

**Strong answer covers** a *specific* problem and the alternative you rejected. The pattern name is the least interesting part of the answer.

**The ones that genuinely come up:**

| Pattern | The problem it solves | Where you've met it |
|---|---|---|
| **Strategy** | Swapping one algorithm for another | Payment providers, sorting comparators, auth strategies |
| **Adapter** | Two incompatible interfaces | Wrapping a third-party SDK behind your own interface |
| **Observer** | One-to-many notification | Event emitters, `addEventListener`, pub/sub, React state |
| **Factory** | Construction logic that varies | Creating a client per environment |
| **Decorator** | Adding behaviour without subclassing | Middleware, Python decorators, HOCs |
| **Repository** | Isolating persistence from domain logic | Any layered backend |

**The answer that scores:** *"We had three payment providers with different SDKs. I put an interface in front of them — Strategy plus Adapter — so the checkout code has one code path and adding a provider is a new file, not an edit. The alternative was a switch statement, which we'd have had to find and edit in four places every time."*

**The senior point, worth raising unprompted:** **patterns are a vocabulary, not a goal.** Applying them speculatively is how you get `AbstractRequestHandlerFactoryBean`. The strongest version of this answer includes a pattern you *removed* because it was unnecessary indirection.

---

### Q2. [Intermediate] 🔥 What's wrong with a Singleton?

**Strong answer covers:** it's global mutable state with a nicer name.

- **Untestable** — tests can't substitute it, and state leaks between them, producing order-dependent failures
- **Hidden dependency** — a class using a singleton has a dependency its signature doesn't declare, so you can't tell what it needs by reading it
- **Concurrency** — shared mutable state across threads → [[foundations/os/06-concurrency-primitives|concurrency primitives]]
- **Lifecycle is unmanaged** — you can't control initialisation order or shut it down cleanly

**What to do instead:** create one instance and **inject** it. You get a single instance *and* substitutability, which is the actual requirement — "there should be one" and "it must be globally reachable" are different demands, and Singleton conflates them.

**Where it's defensible:** stateless utilities, a logger, or a connection pool that's genuinely process-wide — and even then, injected rather than reached for.

---

### Q3. [Intermediate] 🔥 SOLID — pick the one you use most and the one that's overrated.

**Strong answer covers** actual opinions, because reciting five definitions is the expected answer and scores nothing.

**Most useful in practice — Single Responsibility and Dependency Inversion.** SRP as *"one reason to change"* is the one that prevents the 2,000-line service. DI is what makes anything testable.

**The one worth arguing about — Open/Closed.** *"Open for extension, closed for modification"* was formulated when recompiling and redistributing was expensive. **With version control, tests and CI, editing a class is cheap.** Designing extension points speculatively usually produces indirection for variation that never arrives → [[foundations/systems-engineering/05-trade-studies|YAGNI]].

**Liskov** matters and is usually violated by inheritance that shouldn't exist — the square/rectangle case is really an argument for composition → [[foundations/programming-fundamentals/13-objects-and-classes|objects and classes]].

**The senior point:** SOLID is object-oriented-shaped. In a functional or data-oriented codebase the underlying goals — small pieces, explicit dependencies, substitutable parts — survive; the specific five don't map cleanly. **Knowing they're heuristics, not laws, is the answer.**

---

### Q4. [Intermediate] 🔥 Here's a PR. What do you comment on?

**Strong answer covers** an *order*, because reviewing linearly is what juniors do:

1. **Does it do the right thing?** Read the description and the tests before the diff. A well-implemented wrong feature is the most expensive outcome
2. **Correctness** — edge cases, error paths, concurrency, the empty/zero/null cases
3. **Security** — injection, authz on the new endpoint, secrets, unvalidated input → [[devops/12-sre-and-platform-engineering/04-devsecops|DevSecOps]]
4. **Tests** — do they actually assert, and would they fail if the code were wrong?
5. **Readability and naming**
6. **Style** — **which should be a formatter's job, not yours**

**How to comment, which is half of what's being assessed:**
- **Distinguish blocking from optional.** "nit:" for preferences, and mean it
- **Ask rather than assert** — "what happens if `items` is empty?" surfaces the bug *and* leaves room to be wrong
- **Explain the why**, with a link
- **Praise something specific.** Reviews that are purely negative make people defensive and slow

**The senior point:** review is where most engineering culture is actually transmitted. **The best signal in this answer is a candidate who mentions review *latency*** — a PR sitting for two days costs more than most of the issues found in it.

---

### Q5. [Intermediate] What makes a good test, and what's testing theatre?

**Strong answer covers:** a good test fails when behaviour breaks and passes otherwise. That sounds trivial and rules out most bad tests.

**Theatre:**
- **Tests with no meaningful assertion** — they execute code and prove nothing, while producing coverage
- **Testing the framework** — that `useState` updates, that the ORM saves
- **Mocking everything**, so the test asserts your assumptions rather than the system's behaviour. A suite full of mocks passes while the system is broken
- **Coverage as a target.** **Coverage measures what ran, not what was checked** → [[languages/06-python/13-testing-and-tooling|testing and tooling]]
- **Tests that restate the implementation** — they change whenever the code does, so they block refactoring instead of enabling it

**What good looks like:** the pyramid as a heuristic (many fast unit tests, fewer integration, few E2E), tests named for the behaviour, **a failing test written first when fixing a bug**, and mocks only at genuine boundaries — network, time, randomness, paid APIs.

**The senior point:** the purpose of tests is **to let you change the code**. A suite that must be rewritten for every refactor is a liability. Judge tests by whether they'd survive an internal rewrite that preserved behaviour.

---

### Q6. [Intermediate] How do you approach refactoring a codebase you don't understand?

**Strong answer covers:**

1. **Get it under test first.** Characterisation tests capture what it *currently* does, correct or not — that's your safety net
2. **Small, reversible steps**, each one shippable. A three-week refactor branch is a rewrite with worse odds
3. **Find the seams** — the natural boundaries where you can insert an interface without touching everything
4. **Don't mix refactoring with behaviour change.** Separate commits, ideally separate PRs. A reviewer can check "no behaviour changed" *or* "the new behaviour is right", not both at once
5. **Use the tooling** — automated renames and extractions are safer than hand-editing
6. **Leave it better than you found it**, in proportion to how much you touched

**The senior point, and the one interviewers listen for:** **the reason to refactor is a change you're about to make** — *"make the change easy, then make the easy change."* Refactoring with no upcoming feature behind it is difficult to justify against anything else on the backlog, and that's an honest thing to say.

---

### Q7. [Advanced] When is duplication better than abstraction?

**Strong answer covers:** **more often than DRY's reputation suggests.**

The failure mode is abstracting two things that *look* alike but aren't the same *concept*. When they diverge — and they do — you get a shared function with a boolean parameter, then two, then a config object, and every caller must now understand every branch.

**The heuristics worth naming:**
- **Rule of three** — wait for a third occurrence before extracting; two data points don't establish a pattern
- **"Duplication is far cheaper than the wrong abstraction"** (Sandi Metz) — the standard formulation, and the one to cite
- **Ask whether they'd change together.** Two pieces of code that would always change for the same reason are one concept. Coincidentally identical code is two → [[foundations/systems-engineering/04-architecture-and-interfaces|cohesion]]
- **Un-abstracting is harder than abstracting**, because callers have accumulated

**The senior point:** DRY is about **knowledge**, not characters — *"every piece of knowledge should have a single authoritative representation."* Two identical validation functions encoding *different business rules* that happen to agree today are not a DRY violation.

---

## Related
- [[concepts/interview/01-apis-auth-and-practices|APIs, auth & practices]]
- [[concepts/03-design-patterns/README|design patterns]] · [[concepts/04-best-practices/README|best practices]]
- [[foundations/software-engineering/README|software engineering]] — what the profession is
- [[backend/interview/README|Backend interview prep]]

*Source: [reference] — assembled Aug 2026.*
