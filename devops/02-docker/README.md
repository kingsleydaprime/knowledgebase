# Docker

Containers, in reading order: what Docker actually is, how containers talk to each other and the outside world, how they persist data despite being ephemeral, and how to keep the final image lean. No reading order existed here before this pass; newly authored.

## Reading order

1. [[01-new-docker|new-docker]] — **[Beginner]** — Docker, the big picture: what it is and why it exists, before any commands
2. [[02-docker-networking|docker-networking]] — **[Intermediate]** — containers are isolated by default; how to let them talk to each other and the outside world
3. [[03-docker-volumes|docker-volumes]] — **[Intermediate]** — containers are ephemeral; volumes store data outside the container lifecycle
4. [[04-multi-stage-builds|multi-stage-builds]] — **[Advanced]** — keeping the final image lean by not shipping build-time tooling

## Related
- [[devops/README|devops curriculum map]]
- [[devops/01-linux/README|linux fundamentals]]
