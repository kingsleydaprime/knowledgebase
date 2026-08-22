# DevSecOps

> **[Intermediate]** · Security as a pipeline stage instead of a gate at the end. What runs where, what each class of tool actually catches, and the failure mode that kills most rollouts.

Security's traditional shape was a **gate**: build for months, hand the finished thing to a security team, wait for a review, fix what comes back. That works at one release a quarter. It does not survive forty deploys a day — the gate is either bypassed or it becomes the [[devops/12-sre-and-platform-engineering/01-how-delivery-practice-evolved|bottleneck]], and in practice it becomes both.

**DevSecOps is the same move DevOps made, applied to security: stop treating it as a phase owned by another team, distribute it across the pipeline, and automate the parts a machine can do.**

The slogan is *shift left* — move security checks earlier, where defects are cheap. A vulnerability caught in the editor costs minutes. The same vulnerability caught in production costs an incident, a disclosure, and possibly a regulator.

## What runs where

The whole discipline is easier to hold as a table of pipeline stages:

| Stage | Control | Catches | Tools |
|---|---|---|---|
| **Plan** | Threat modelling | Design flaws — *auth in the wrong place* | STRIDE, attack trees |
| **Code** | **SAST**, IDE linting, pre-commit hooks | Injection, unsafe APIs, hardcoded secrets | Semgrep, CodeQL, SonarQube |
| **Code** | **Secret scanning** | Keys about to be committed | gitleaks, TruffleHog, GitHub secret scanning |
| **Build** | **SCA** + SBOM | Known CVEs **in your dependencies** | Dependabot, Snyk, Trivy, OWASP DC |
| **Build** | **Image scanning** | Vulnerable base images, bad layers | Trivy, Grype, Clair |
| **Build** | **IaC scanning** | Public S3 buckets, `0.0.0.0/0`, no encryption | Checkov, tfsec, KICS |
| **Test** | **DAST** | Runtime behaviour of the running app | OWASP ZAP, Burp |
| **Deploy** | Policy as code, admission control | Non-compliant workloads | OPA/Gatekeeper, Kyverno |
| **Deploy** | Signing and provenance | Tampered artefacts | Sigstore/cosign, SLSA |
| **Run** | Runtime detection, posture, drift | Live attacks, config drift | Falco, GuardDuty, CSPM |

The three-letter acronyms are worth separating properly, because they fail in different places:

**SAST** reads your source without running it. Fast, runs on every commit, and finds patterns — string-concatenated SQL, a disabled certificate check. **It cannot see anything that depends on runtime state**, and it produces false positives, which is the reason most SAST rollouts fail (below).

**SCA** looks at your dependency tree and compares it against vulnerability databases. **This is the highest-value scanner for most teams by a wide margin**, because the majority of code in a modern application is code you didn't write. It's also the cheapest to adopt: near-zero false positives, since a CVE either applies to your version or doesn't.

**DAST** attacks the running application from outside. Finds what SAST structurally can't — misconfiguration, auth logic errors, real header behaviour. Slower, needs a deployed environment, so it runs against staging rather than on every commit.

**They're complementary, not ranked.** SAST sees code paths DAST never reaches; DAST sees the deployed reality SAST can't model.

## SBOM and the supply chain

A **Software Bill of Materials** is an inventory of every component in your artefact, with versions. Formats: SPDX, CycloneDX.

The reason this became mandatory-ish rather than nice-to-have is one question, asked repeatedly during the Log4Shell period in December 2021: ***are we affected?*** Organisations without an SBOM spent days finding out, largely by hand. Organisations with one queried it.

Generate an SBOM per build, store it with the artefact, and you can answer "which of our 300 services ship this library" in seconds. **That's the value — not compliance, incident response speed.**

The related practice is **artefact signing** (Sigstore/cosign) and **provenance** (SLSA): proving that the image you're about to deploy was built by your pipeline from your source, and not substituted somewhere in between. This is the direct response to the SolarWinds-class attack, where the *build system* is the target — you don't compromise a thousand companies, you compromise the thing all of them install.

## Secrets

The rule is simple and constantly violated: **secrets never enter a repository.** Not in code, not in config, not in a `.env` that's "temporarily" committed.

Three layers, and you want all three:

1. **Prevention** — pre-commit hooks that block a commit containing something that looks like a key
2. **Detection** — repository-wide scanning, including full history, because a secret deleted in a later commit is still in the history and still valid
3. **Management** — a real secret store ([[devops/09-secret-management/README|Vault, SOPS, cloud KMS]]) that injects at runtime, with rotation

**A leaked secret is not fixed by deleting the commit.** Once it has touched a remote, assume it is compromised: rotate it, then clean the history. Public GitHub is scraped for keys within seconds — this is measured in seconds, not hours.

## Policy as code

Once security requirements are expressed as rules a machine evaluates — OPA/Rego, Kyverno, Sentinel — they can run in CI *and* at admission time in the cluster, which means the rule is applied identically no matter how the change arrives.

Examples of things that stop being a review conversation and become a failed check:
- No container runs as root
- Every resource carries an owner tag
- No security group opens `0.0.0.0/0` on port 22
- Every image comes from an approved registry and is signed

**The gain isn't automation for its own sake — it's that the standard becomes unambiguous and uniformly applied.** A written policy is interpreted differently by every reviewer on a tired Friday. A Rego rule is not.

## The failure mode that kills most rollouts

**Alert fatigue, and it's the same pathology as [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|noisy paging]] wearing a different hat.**

Turn on every scanner at maximum sensitivity and a mature codebase produces thousands of findings on day one. Predictably: developers cannot triage thousands of findings, so they ignore all of them, so the tooling gets disabled or routed around, so security posture is *worse* than before you started — because now everyone believes there's a scanner covering it.

What works instead:

- **Start with SCA only.** Highest signal, lowest false-positive rate, immediate credible wins
- **Baseline the existing findings** and fail the build only on *new* ones. Stops the bleeding without demanding a three-month cleanup before anything ships
- **Fail on severity, warn on the rest.** Critical blocks; medium is a ticket
- **Tune aggressively.** Every false positive that survives a week is teaching developers to ignore the tool
- **Adopt one class of scanner at a time**

**A scanner nobody acts on is worse than no scanner**, because it converts a known gap into a false sense of coverage.

## Who owns it

The common misreading is that DevSecOps means the security team runs the pipeline. It means close to the opposite: **development teams own the security of what they ship, and the security team's job becomes building the capability that makes that possible** — choosing tools, tuning them, writing the policies, providing threat-modelling expertise, and handling the work that genuinely needs specialists.

Which is the same structural move as [[devops/12-sre-and-platform-engineering/03-platform-engineering|platform engineering]]: a scarce central expertise, delivered as a paved path rather than a queue. In practice the security controls above are usually *part of* the golden path — a team that scaffolds a service from the platform inherits SCA, secret scanning, image scanning, signing and the admission policies without asking for any of them.

**That's the end state worth aiming at: the secure way is the default way, and opting out is the thing that takes effort.**

## Related
- [[cybersecurity/README|cybersecurity]] — the domain this borrows from, in depth
- [[devops/06-ci-cd/10-pipeline-security|pipeline security]] — securing the pipeline itself
- [[devops/09-secret-management/README|secret management]] — the tooling for the secrets section
- [[cybersecurity/09-cloud-security/01-cloud-and-infrastructure-security|cloud security]] — posture and misconfiguration
- [[cybersecurity/07-security-operations/04-incident-response|incident response]] — what happens when it gets through anyway

*Source: [reference] — from the freeCodeCamp IT Fundamentals course (final module), extended with OWASP, SLSA and CNCF supply-chain security material.*
