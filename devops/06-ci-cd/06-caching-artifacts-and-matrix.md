# Caching, Artifacts and Matrix Builds

**[Intermediate]** — The three things that make a pipeline fast and broad: caching dependencies between runs, passing artifacts between jobs, and running the same job across many versions or platforms at once.

## Caching

### Why Caching Matters

Installing dependencies (`npm install`, `mvn install`, `pip install`) can take 2–5 minutes on every CI run. Caching stores the result of those installations and restores them on subsequent runs. With a warm cache, dependency installation drops to seconds.

### actions/cache

```yaml
- name: Cache node modules
  uses: actions/cache@v4
  with:
    path: ~/.npm                               # what to cache
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    # key: if this exact key exists, restore from cache (cache hit)
    # if not found (cache miss), the job runs normally and saves at the end

    restore-keys: |
      ${{ runner.os }}-npm-                   # partial match fallback keys
      ${{ runner.os }}-
    # restore-keys: tried in order if exact key misses
    # allows using a slightly stale cache when lock file changed
```

### Language-Specific Cache Examples

**Node.js:**

```yaml
# Option 1: Manual cache
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: ${{ runner.os }}-node-

- run: npm ci

# Option 2: Built into setup-node (recommended)
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'          # or 'yarn' or 'pnpm'
    # automatically caches ~/.npm and restores before npm ci
```

**Java/Maven:**

```yaml
- uses: actions/setup-java@v4
  with:
    java-version: '21'
    distribution: 'temurin'
    cache: 'maven'        # caches ~/.m2/repository

# Or manually:
- uses: actions/cache@v4
  with:
    path: ~/.m2/repository
    key: ${{ runner.os }}-maven-${{ hashFiles('**/pom.xml') }}
    restore-keys: ${{ runner.os }}-maven-
```

**Python:**

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'

# Or manually:
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: ${{ runner.os }}-pip-
```

**Docker layer caching:**

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push with cache
  uses: docker/build-push-action@v5
  with:
    push: true
    tags: myimage:latest
    cache-from: type=gha          # use GitHub Actions cache
    cache-to: type=gha,mode=max   # save all layers to cache
```

### Cache Keys Strategy

The cache key must balance:
- **Too specific** (hash of every file) → cache misses on any change
- **Too broad** (just the OS) → stale cache, wrong dependencies

```yaml
# Good cache key strategy:
key: ${{ runner.os }}-${{ matrix.node-version }}-npm-${{ hashFiles('**/package-lock.json') }}
# - Separate cache per OS (different binary paths)
# - Separate cache per Node version (different native module binaries)
# - Invalidate when lock file changes (new/updated dependencies)
# - Fall back to any cache for this OS+version combination
restore-keys: |
  ${{ runner.os }}-${{ matrix.node-version }}-npm-
  ${{ runner.os }}-${{ matrix.node-version }}-
```

---

## Artifacts

### What Artifacts Are

Artifacts are files uploaded from a workflow run that persist after the run ends. Uses:
- Pass build output between jobs (build in one job, deploy in another)
- Download test results, coverage reports, built binaries
- Debug failing builds by downloading logs

### Uploading and Downloading

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run build        # produces ./dist/

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: build-output          # artifact name
          path: ./dist/               # what to upload
          retention-days: 7           # how long to keep (default 90)
          if-no-files-found: error    # error | warn | ignore

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: build-output
          path: ./dist/               # where to put it

      - run: ls -la ./dist/
      - run: ./deploy.sh
```

### Common Artifact Patterns

**Test results:**

```yaml
- name: Run tests
  run: npm test -- --coverage --reporters=json
  continue-on-error: true   # upload results even if tests fail

- name: Upload test results
  uses: actions/upload-artifact@v4
  if: always()              # upload even if tests failed
  with:
    name: test-results
    path: |
      coverage/
      test-results.json
```

**Multiple files pattern:**

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: app-bundle
    path: |
      dist/
      Dockerfile
      docker-compose.yml
      !dist/**/*.map        # exclude source maps
```

**Download all artifacts from a run:**

```yaml
- uses: actions/download-artifact@v4
  # No 'name' specified — downloads all artifacts into separate directories
  with:
    path: ./artifacts/

# Results in:
# ./artifacts/build-output/
# ./artifacts/test-results/
```

---

## Matrix Builds

### What Matrix Builds Are

Matrix builds run a job multiple times with different configurations in parallel. Essential for testing across multiple Node versions, OSes, or any variable combination.

### Basic Matrix

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node: [18, 20, 22]
        # Creates 9 jobs: 3 OSes × 3 Node versions

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
```

### Matrix with Include and Exclude

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node: [18, 20]
    include:
      # Add an extra combination not in the base matrix
      - os: ubuntu-latest
        node: 22
        experimental: true        # extra variable available as matrix.experimental
    exclude:
      # Remove a specific combination
      - os: windows-latest
        node: 18

  fail-fast: false    # don't cancel all matrix jobs if one fails (default: true)
  max-parallel: 4     # limit concurrent jobs (default: unlimited)
```

### Dynamic Matrix from JSON

```yaml
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - id: set-matrix
        run: |
          # Build matrix dynamically based on changed files, config, etc.
          echo 'matrix={"service":["api","worker","frontend"]}' >> $GITHUB_OUTPUT

  test:
    needs: setup
    strategy:
      matrix: ${{ fromJSON(needs.setup.outputs.matrix) }}
    runs-on: ubuntu-latest
    steps:
      - run: echo "Testing ${{ matrix.service }}"
```

---

## Related
- [[devops/06-ci-cd/08-ci-pipelines|CI Pipelines]] — all three assembled into a real build
- [[devops/11-delivery-and-advanced/02-artifact-management|Artifact Management]] — what happens to a build output after the pipeline
- [[devops/06-ci-cd/01-ci-cd-concepts|CI/CD Concepts]] — "build once, promote the artifact"
- [[devops/06-ci-cd/README|CI/CD module map]]
