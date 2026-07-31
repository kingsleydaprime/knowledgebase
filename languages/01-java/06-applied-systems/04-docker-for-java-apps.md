# Docker for Java Apps

**Source:** condensed from the Docker sections of `record-id-generator-java/learning/10-docker-and-performance-tuning.md`.

## Core concepts

- **Image** — a blueprint (`mysql:8`, `eclipse-temurin:21-jdk-alpine`)
- **Container** — a running instance of an image
- **Volume** — data that persists beyond a single container's lifecycle
- **docker-compose** — orchestrates multiple containers (app + DB + broker) as one unit

```yaml
services:
  mysql:
    image: mysql:8
    ports: ["3306:3306"]
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: itc_db
    volumes:
      - mysql_data:/var/lib/mysql   # survives `docker compose down` (without -v)
  rabbitmq:
    image: rabbitmq:management
    ports: ["5672:5672", "15672:15672"]   # AMQP + management UI
volumes:
  mysql_data:
```

```bash
docker compose up -d      # start in background
docker compose ps         # check status
docker compose down       # stop (keeps volumes)
docker compose down -v    # stop AND delete volumes — only if losing that data is fine
```

## Multi-stage builds for a smaller production image

```dockerfile
# Stage 1: build with the full JDK
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY . .
RUN ./gradlew build -x test

# Stage 2: run with only the JRE — no build tools in the shipped image
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /app/app/build/libs/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

The build stage's JDK, Gradle cache, and source tree never make it into the final image — only the compiled jar does. Smaller image, smaller attack surface, faster pulls.

## File descriptor limits inside containers

A containerized broker or DB hitting Linux's default 1024-file-descriptor-per-process limit under real connection/queue volume rejects new connections with no obvious application-level cause. Fix via `ulimits` on the service:

```yaml
rabbitmq:
  image: rabbitmq:management
  ulimits:
    nofile:
      soft: 65536
      hard: 65536
```

`soft` is the limit the process starts with; `hard` is the ceiling it's allowed to raise itself to. 65536 is RabbitMQ's own documented minimum recommendation for anything beyond a single trivial connection — the kernel default of 1024 is a historical artifact, not a sensible modern default for a message broker or database.

## Related
- [[languages/01-java/03-tooling/01-build-tools|Build Tools & Project Structure]] — what actually goes into the jar this Dockerfile packages
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing & Performance]] — MySQL tuning flags set via the same `command:` block shown here
- [[devops/02-docker/README|Docker (devops)]] — general Docker/compose concepts not specific to Java
