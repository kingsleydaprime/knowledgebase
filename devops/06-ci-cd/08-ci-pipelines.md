# CI Pipelines — The Complete Build

**[Intermediate]** — What a good CI pipeline actually does, worked end to end in two real stacks: Node/NestJS and Java/Spring Boot.

## What a Good CI Pipeline Does

Every pull request and push should:
1. Fail fast on obvious issues (lint/format in seconds)
2. Run all tests in parallel where possible
3. Build the deployable artifact
4. Scan for security issues
5. Report status back to the PR

## Complete Node.js / NestJS CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
    types: [opened, synchronize, reopened]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

env:
  NODE_VERSION: '20'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ─── Fast checks ──────────────────────────────────────────────────────────────
  lint:
    name: Lint & Format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm

      - run: npm ci

      - name: Check formatting (Prettier)
        run: npm run format:check

      - name: Lint (ESLint)
        run: npm run lint

      - name: Type check
        run: npm run type-check

  # ─── Tests ────────────────────────────────────────────────────────────────────
  test-unit:
    name: Unit Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm

      - run: npm ci

      - name: Run unit tests
        run: npm run test:unit -- --coverage

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-unit
          path: coverage/
          retention-days: 3

  test-integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: testpassword
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm

      - run: npm ci

      - name: Run database migrations
        run: npm run db:migrate
        env:
          DATABASE_URL: postgresql://postgres:testpassword@localhost:5432/testdb

      - name: Run integration tests
        run: npm run test:integration
        env:
          DATABASE_URL: postgresql://postgres:testpassword@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379
          JWT_SECRET: test-secret-do-not-use-in-production

  # ─── Security ─────────────────────────────────────────────────────────────────
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check for known vulnerabilities in dependencies
        run: npm audit --audit-level=high

      - name: Scan for secrets in code
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  # ─── Build ────────────────────────────────────────────────────────────────────
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: [lint, test-unit, test-integration, security]
    permissions:
      contents: read
      packages: write

    outputs:
      image: ${{ steps.meta.outputs.tags }}
      digest: ${{ steps.push.outputs.digest }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata for Docker
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix=sha-
            type=semver,pattern={{version}}
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push
        id: push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            BUILD_DATE=${{ github.event.head_commit.timestamp }}
            GIT_SHA=${{ github.sha }}

      - name: Scan Docker image for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:sha-${{ github.sha }}
          format: sarif
          output: trivy-results.sarif
          severity: HIGH,CRITICAL
          exit-code: 1

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: trivy-results.sarif

  # ─── PR Summary ───────────────────────────────────────────────────────────────
  pr-comment:
    name: PR Status Comment
    runs-on: ubuntu-latest
    needs: [build]
    if: github.event_name == 'pull_request'
    permissions:
      pull-requests: write
    steps:
      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `✅ CI passed! Image built: \`sha-${{ github.sha }}\``
            })
```

## Complete Java / Spring Boot CI Pipeline

```yaml
name: Java CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: testpassword
          MYSQL_DATABASE: testdb
        options: >-
          --health-cmd "mysqladmin ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 3306:3306

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: temurin
          cache: maven

      - name: Build with Maven
        run: mvn -B package --no-transfer-progress
        env:
          SPRING_DATASOURCE_URL: jdbc:mysql://localhost:3306/testdb
          SPRING_DATASOURCE_USERNAME: root
          SPRING_DATASOURCE_PASSWORD: testpassword

      - name: Run tests
        run: mvn -B test --no-transfer-progress
        env:
          SPRING_DATASOURCE_URL: jdbc:mysql://localhost:3306/testdb
          SPRING_DATASOURCE_USERNAME: root
          SPRING_DATASOURCE_PASSWORD: testpassword

      - name: Upload test report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: surefire-reports
          path: target/surefire-reports/

      - name: Upload JAR
        uses: actions/upload-artifact@v4
        with:
          name: app-jar
          path: target/*.jar
```

---

## Related
- [[devops/06-ci-cd/01-ci-cd-concepts|CI/CD Concepts]] — the stages and gates these pipelines implement
- [[devops/06-ci-cd/09-cd-and-deployment|CD and Deployment]] — what happens after the build goes green
- [[languages/01-java/03-tooling/04-testing|Testing (Java)]] — the gate at the centre of the Spring Boot pipeline
- [[devops/06-ci-cd/11-real-world-pipelines|Real-World Pipelines]] — the same stacks taken all the way to a VPS
- [[devops/06-ci-cd/README|CI/CD module map]]
