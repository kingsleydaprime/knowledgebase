# Real-World Pipelines, End to End

**[Advanced]** — Two complete production pipelines read top to bottom: NestJS + Docker + VPS, and Java/Spring Boot + MySQL + VPS. Every concept from the earlier notes, assembled.

## Full NestJS + Docker + VPS Pipeline

```yaml
# .github/workflows/main.yml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
  NODE_VERSION: '20'

jobs:
  # ── CI ──────────────────────────────────────────────────────────────────────

  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
      - run: npm ci --prefer-offline
      - run: npm run lint
      - run: npm run format:check

  test:
    name: Test
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: testdb
        options: --health-cmd pg_isready --health-interval 10s --health-retries 5
        ports: ['5432:5432']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
      - run: npm ci --prefer-offline
      - run: npm run test:cov
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
          JWT_SECRET: test-secret
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage
          path: coverage/
          retention-days: 7

  build-image:
    name: Build & Push Image
    runs-on: ubuntu-latest
    needs: [lint, test]
    permissions:
      contents: read
      packages: write
    outputs:
      tag: ${{ steps.meta.outputs.version }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ── CD ──────────────────────────────────────────────────────────────────────

  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    needs: build-image
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://yourdomain.com
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1
        env:
          IMAGE_TAG: ${{ needs.build-image.outputs.tag }}
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          envs: IMAGE_TAG
          script: |
            set -e
            cd ~/app

            # Pull the specific image
            docker pull ghcr.io/${{ github.repository }}:$IMAGE_TAG

            # Zero-downtime rolling deploy
            docker compose pull
            docker compose up -d --no-deps --scale app=2 --no-recreate app
            sleep 20
            docker compose up -d --no-deps --scale app=1 --no-recreate app
            docker image prune -f

            echo "${{ github.sha }}" > .current-sha

      - name: Health check
        run: |
          for i in {1..10}; do
            STATUS=$(curl -sf -o /dev/null -w "%{http_code}" https://yourdomain.com/health)
            [ "$STATUS" = "200" ] && echo "✅ Healthy" && exit 0
            echo "Attempt $i: $STATUS"
            sleep 10
          done
          exit 1

      - name: Notify on failure
        if: failure()
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            # Auto-rollback on health check failure
            cd ~/app
            PREV_SHA=$(cat .current-sha 2>/dev/null || echo "")
            if [ -n "$PREV_SHA" ]; then
              echo "Rolling back to $PREV_SHA"
              docker compose up -d --no-deps app
            fi
```

## Full Java / Spring Boot + MySQL + VPS Pipeline

```yaml
name: Java CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  JAVA_VERSION: '21'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: testpass
          MYSQL_DATABASE: testdb
        options: --health-cmd "mysqladmin ping" --health-interval 10s --health-retries 5
        ports: ['3306:3306']

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: ${{ env.JAVA_VERSION }}
          distribution: temurin
          cache: maven

      - name: Build and test
        run: mvn -B verify --no-transfer-progress
        env:
          SPRING_DATASOURCE_URL: jdbc:mysql://localhost:3306/testdb?useSSL=false&allowPublicKeyRetrieval=true
          SPRING_DATASOURCE_USERNAME: root
          SPRING_DATASOURCE_PASSWORD: testpass
          SPRING_JPA_HIBERNATE_DDL_AUTO: create-drop

      - name: Upload test reports
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-reports
          path: target/surefire-reports/

  build-image:
    name: Build & Push
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    outputs:
      digest: ${{ steps.push.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        id: push
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    name: Deploy
    needs: build-image
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd ~/app
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f
```

---

## Related
- [[devops/06-ci-cd/08-ci-pipelines|CI Pipelines]] — the build halves of these, explained stage by stage
- [[devops/06-ci-cd/09-cd-and-deployment|CD and Deployment]] — the deploy halves
- [[devops/04-vps/vps-deployment-reference|VPS Deployment]] — the servers these pipelines ship to
- [[devops/02-docker/README|Docker]] — the images they build and push
- [[devops/06-ci-cd/README|CI/CD module map]]
