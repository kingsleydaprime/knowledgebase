# CI/CD Tools

**Partly grounded** — the GitHub Actions walkthrough dissects this vault's *actual* deploy pipeline (`.github/workflows/deploy.yml`). The other tools are `[reference]`. There's a fuller hands-on companion at [[git/github-actions-cicd-reference|git/github-actions-cicd-reference]].

## GitHub Actions — dissected from a real pipeline

This knowledgebase publishes itself to GitHub Pages via a GitHub Actions workflow. It's a genuine, working CI/CD pipeline, and every core concept from [[devops/06-ci-cd/01-ci-cd-concepts|the concepts note]] shows up in it. The real file, annotated:

```yaml
name: Deploy Quartz site to GitHub Pages

on:                          # TRIGGER — what starts the pipeline
  push:
    branches: [main]         # every push to main

permissions:                 # least-privilege — grant only what the job needs
  contents: read
  pages: write
  id-token: write

concurrency:                 # don't let two deploys race
  group: "pages"
  cancel-in-progress: false

jobs:
  build:                     # JOB 1 — produce the artifact
    runs-on: ubuntu-latest   # the RUNNER — an ephemeral VM GitHub provides
    defaults:
      run: { working-directory: quartz }
    steps:                   # STEPS run in order on the runner
      - uses: actions/checkout@v6        # reusable ACTION — clone the repo
      - uses: actions/setup-node@v6
        with: { node-version: 24 }
      - name: Cache dependencies         # CACHING — skip re-downloading unchanged deps
        uses: actions/cache@v5
        with:
          path: ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('quartz/package-lock.json') }}
      - run: npm ci                       # a shell step
      - run: npx quartz build             # the actual build
      - uses: actions/upload-pages-artifact@v3   # ARTIFACT — hand off to the next job
        with: { path: quartz/public }

  deploy:                    # JOB 2 — ship it
    needs: build             # DEPENDENCY — only runs if build succeeded
    runs-on: ubuntu-latest
    steps:
      - uses: actions/deploy-pages@v4
```

What this concretely demonstrates:

- **Event trigger** — `on: push` to `main` starts everything. No manual step.
- **Jobs + `needs`** — `deploy` depends on `build`; if the build fails, nothing ships. That's the *gate*.
- **Steps and reusable Actions** — `uses:` pulls a versioned, community-maintained action (`checkout`, `setup-node`, `cache`); `run:` executes shell. The marketplace of reusable actions is GitHub Actions' biggest advantage.
- **Runners** — `ubuntu-latest` is a fresh, ephemeral VM per run — no state carried between runs (which is *why* caching exists).
- **Caching** — the `hashFiles(...)` key means the cache is reused until the lockfile changes, cutting build time. A real, practical optimization.
- **Artifact hand-off** — job 1 uploads `quartz/public`; job 2 deploys it. **Build once, deploy that exact output** — the principle from the concepts note.
- **Least-privilege permissions** and **concurrency control** — production-grade details, not toy config.

This is Continuous *Deployment* in the strict sense: a push to `main` goes straight to the live site with no human gate — appropriate here because the "test" is a successful static build and the blast radius is a personal site.

## The tool landscape

All CI/CD tools express the same model (triggers → jobs → steps → artifacts → deploy); they differ in where they run and how they integrate.

| Tool | Model | Best for |
|---|---|---|
| **GitHub Actions** | YAML in-repo, runs on GitHub's runners; huge marketplace | anything on GitHub — the default there |
| **GitLab CI** | YAML (`.gitlab-ci.yml`) in-repo, tightly integrated with GitLab | GitLab shops; strong built-in registry + environments |
| **Jenkins** | self-hosted server, `Jenkinsfile` (Groovy), enormous plugin ecosystem | maximum flexibility/control, on-prem, legacy; you run and maintain the server |
| **CircleCI / Travis CI / Drone** | cloud SaaS runners, YAML config | teams wanting managed runners outside GitHub/GitLab |
| **TeamCity / Bamboo** | commercial (JetBrains / Atlassian) | enterprises in those ecosystems |
| **Argo Workflows / Tekton** | Kubernetes-native pipelines | CI/CD that runs *as* k8s resources |

The two axes that actually drive the choice: **hosted vs self-hosted** (managed runners like GitHub Actions/CircleCI vs running Jenkins yourself — control and cost vs operational burden), and **integration** (Actions with GitHub, GitLab CI with GitLab — the pipeline living next to the code it builds is a real convenience). Jenkins remains everywhere in enterprises for its flexibility and plugin depth, at the cost of being one more server to secure and maintain.

For the *delivery* half specifically on Kubernetes, note that GitOps tools ([[devops/11-delivery-and-advanced/01-gitops|ArgoCD/FluxCD]]) increasingly own the "deploy" stage, with the CI tool responsible only up to building and pushing the image.

## Related
- [[devops/06-ci-cd/01-ci-cd-concepts|CI/CD Concepts]] — the model this file makes concrete
- [[git/github-actions-cicd-reference|GitHub Actions reference (git/)]] — the fuller hands-on notes
- [[devops/11-delivery-and-advanced/01-gitops|GitOps]] — the k8s-native delivery model
