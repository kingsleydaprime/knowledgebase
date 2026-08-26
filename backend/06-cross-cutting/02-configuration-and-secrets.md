# Configuration and Secrets

> **[Intermediate]** · Config as an input, not a constant — and the rule that keeps credentials out of your repository.

## The twelve-factor rule, and why it holds

**Config is everything that differs between environments.** Database URLs, API keys, feature flags, log levels, timeouts.

**It belongs in the environment, not in the code**, because the alternative is a build per environment — and then "it works in staging" tells you nothing about production, since it's a *different artefact*.

**The test: could you open-source this repository right now without leaking anything?** If not, config and secrets are entangled with code.

## Layering

Nearly every ecosystem converges on the same precedence, later overriding earlier:

```
defaults in code → config file → environment-specific file → environment variables → CLI flags
```

**Environment variables win** because they're what a container orchestrator, a CI system and a PaaS can all set.

**Validate the whole config at startup, once:**

```ts
const Env = z.object({
  DATABASE_URL: z.string().url(),
  PORT: z.coerce.number().default(3000),
  JWT_SECRET: z.string().min(32),
  LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
});
export const env = Env.parse(process.env);      // throws at boot, not at 3am
```

**This is [[backend/06-cross-cutting/01-validation-and-dtos|parse, don't validate]] applied to config**, and it converts the worst class of production failure — a missing variable discovered on the code path that needs it, hours after deploy — into a container that refuses to start.

**Fail loudly at startup. A service running with half its config is worse than one that didn't start.**

## Secrets are different from config

**Config can be logged. Secrets cannot.**

| | Config | Secret |
|---|---|---|
| Example | `LOG_LEVEL`, `PORT` | `JWT_SECRET`, DB password, API key |
| In the repo? | **Yes**, defaults are fine | **Never** |
| Rotatable? | Rarely needed | **Must be** |
| In logs / error reports? | Fine | **Never** |

**The rules:**

**Never commit a secret.** Not in `appsettings.json`, not in `.env` — and `.env` goes in `.gitignore` on day one. Commit `.env.example` with the *keys* and no values.

**A leaked secret is not fixed by deleting the commit.** Once it has touched a remote, rotate it first, then clean history. **Public GitHub is scraped within seconds** → [[devops/12-sre-and-platform-engineering/04-devsecops|DevSecOps]].

**Use a real secret store in production** — Vault, cloud KMS/Secrets Manager, sealed secrets → [[devops/09-secret-management/README|secret management]].

**Redact in logs and error reporting.** A crash reporter that captures the environment will exfiltrate every variable. Configure a denylist by *name pattern* (`*_SECRET`, `*_KEY`, `*_TOKEN`, `*PASSWORD*`), and prefer typed config objects with a `ToString()` that refuses to print sensitive fields.

**Rotation must be possible without a redeploy.** If rotating a key requires rebuilding an image, it won't happen at the frequency it should.

## Feature flags

**A flag is config with a shorter lifetime**, and it's what lets you deploy without releasing:

- **Release flags** — ship dark, enable gradually. **Delete after rollout**
- **Ops flags / kill switches** — disable an expensive feature under load. Long-lived by design
- **Experiment flags** — A/B tests
- **Permission flags** — entitlements. Arguably not flags at all

**The failure mode is flags that never die.** Each one doubles the number of code paths, and ten flags is 1,024 possible configurations — of which you test maybe three. **Put an expiry date on release flags and enforce it**, or the codebase becomes untestable.

## What to avoid

**Config in a database your app needs config to reach.** A bootstrap cycle.

**Reading environment variables scattered through the code.** One typed object, parsed once, injected — otherwise you discover a missing variable when a rare code path runs.

**Different config *shapes* per environment.** Same keys everywhere, different values. A key that only exists in production is a key nobody tested.

**Secrets passed as command-line arguments** — they're visible in `ps` to every user on the host.

## Related
- [[backend/06-cross-cutting/01-validation-and-dtos|validation]] — the same technique, applied to config
- [[devops/09-secret-management/README|secret management]] — the tooling
- [[backend/frameworks/cross-language-recipes|cross-language recipes]] — env validation in six stacks
- [[devops/06-ci-cd/05-contexts-secrets-and-environments|CI secrets]]

*Source: [reference] — written Aug 2026.*
