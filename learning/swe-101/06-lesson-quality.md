# Lesson Quality — SWE 101 against the course standard

> Which of the lessons this course sends you to actually meet [[COURSE-STANDARD|the course standard]], and which are still topic summaries. **Converted in week order, one block at a time**, so the lessons are ready before you reach them.

**Generated, not hand-written** — run `python3 learning/swe-101/scripts/audit-standard.py` from the vault root after converting a lesson.

**What the check looks for:** a kid version, a "Before you start" section, a numbered "Terms used in…" list, questions with answers hidden behind a fold, and a "Practice" task. Passing the check means the sections are there — not that the lesson teaches well. That is only established by studying it closed-book, so **note anywhere you got stuck** in the review log below.

**Order of work:** Software design (weeks 1–4) → Architecture (5–8) → Databases (9–11) → Networking (12–15) → Security (16–17) → the rest. References, interview banks and exercise sets keep their own shapes and are marked n/a.

<!-- AUDIT:START -->

**15 of 128 lessons meet the standard.**

| Week | Status | Missing | Lesson |
|---|---|---|---|
| 1 | ✅ meets | — | [[software-engineering/01-what-software-engineering-is\|01-what-software-engineering-is]] |
| 1 | ✅ meets | — | [[software-engineering/02-the-software-development-lifecycle\|02-the-software-development-lifecycle]] |
| 1 | ✅ meets | — | [[software-engineering/03-the-engineering-roles\|03-the-engineering-roles]] |
| 1 | n/a | keeps its own shape | [[PRIMETECHIE\|PRIMETECHIE]] |
| 2 | ✅ meets | — | [[concepts/04-best-practices/01-clean-code\|01-clean-code]] |
| 2 | ✅ meets | — | [[concepts/04-best-practices/08-coupling-and-cohesion\|08-coupling-and-cohesion]] |
| 2 | ✅ meets | — | [[concepts/04-best-practices/05-solid-principles\|05-solid-principles]] |
| 2 | ✅ meets | — | [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture\|04-hexagonal-and-clean-architecture]] |
| 2 | ✅ meets | — | [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature\|02-organising-by-layer-vs-by-feature]] |
| 2 | ✅ meets | — | [[concepts/03-design-patterns/02-structural-patterns\|02-structural-patterns]] |
| 3 | ✅ meets | — | [[concepts/03-design-patterns/01-creational-patterns\|01-creational-patterns]] |
| 3 | ✅ meets | — | [[concepts/03-design-patterns/03-behavioral-patterns\|03-behavioral-patterns]] |
| 3 | ✅ meets | — | [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring\|03-dependency-injection-and-wiring]] |
| 4 | ✅ meets | — | [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories\|01-layers-controllers-services-repositories]] |
| 4 | ✅ meets | — | [[backend/03-structuring-a-backend/05-modular-monolith-to-services\|05-modular-monolith-to-services]] |
| 5 | ⬜ not started | kid, start, terms, checks, practice | [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design\|01-how-to-approach-system-design]] |
| 5 | ⬜ not started | kid, start, terms, checks, practice | [[architecture/01-system-design-fundamentals/02-scalability-and-performance\|02-scalability-and-performance]] |
| 6 | ⬜ not started | kid, start, terms, checks, practice | [[architecture/01-system-design-fundamentals/03-availability-and-reliability\|03-availability-and-reliability]] |
| 6 | ⬜ not started | kid, start, terms, checks, practice | [[architecture/01-system-design-fundamentals/04-cap-and-consistency\|04-cap-and-consistency]] |
| 6 | ⬜ not started | kid, start, terms, checks, practice | [[architecture/02-building-blocks/01-load-balancing-and-proxies\|01-load-balancing-and-proxies]] |
| 6 | ⬜ not started | kid, start, terms, checks, practice | [[architecture/02-building-blocks/02-caching\|02-caching]] |
| 7 | ⬜ not started | kid, start, terms, checks, practice | [[architecture/02-building-blocks/03-databases-at-scale\|03-databases-at-scale]] |
| 7 | ⬜ not started | kid, start, terms, checks, practice | [[architecture/02-building-blocks/04-messaging-and-async\|04-messaging-and-async]] |
| 7 | ⬜ not started | kid, start, terms, checks, practice | [[architecture/02-building-blocks/05-communication\|05-communication]] |
| 8 | n/a | keeps its own shape | [[architecture/interview/01-system-design-round\|01-system-design-round]] |
| 8 | ⬜ not started | kid, start, terms, checks, practice | [[architecture/03-architectural-patterns/01-monolith-microservices-serverless\|01-monolith-microservices-serverless]] |
| 8 | ⬜ not started | kid, start, terms, checks, practice | [[architecture/03-architectural-patterns/02-resilience-patterns\|02-resilience-patterns]] |
| 8 | ⬜ not started | kid, start, terms, checks, practice | [[architecture/03-architectural-patterns/03-data-and-integration-patterns\|03-data-and-integration-patterns]] |
| 8 | ✅ meets | — | [[architecture/03-architectural-patterns/05-transactional-outbox\|05-transactional-outbox]] |
| 8 | ⬜ not started | kid, start, terms, checks, practice | [[architecture/03-architectural-patterns/04-microservices-patterns\|04-microservices-patterns]] |
| 9 | ⬜ not started | kid, start, terms, checks, practice | [[databases/01-what-a-database-is\|01-what-a-database-is]] |
| 9 | ⬜ not started | kid, start, terms, checks, practice | [[databases/02-the-relational-model\|02-the-relational-model]] |
| 9 | n/a | keeps its own shape | [[databases/sql-reference\|sql-reference]] |
| 9 | n/a | keeps its own shape | [[databases/database-design-reference\|database-design-reference]] |
| 10 | 🟡 partial | kid, terms, checks, practice | [[databases/03-storage-and-page-layout\|03-storage-and-page-layout]] |
| 10 | ⬜ not started | kid, start, terms, checks, practice | [[databases/04-b-trees-and-indexes\|04-b-trees-and-indexes]] |
| 10 | ⬜ not started | kid, start, terms, checks, practice | [[databases/05-lsm-trees\|05-lsm-trees]] |
| 10 | ⬜ not started | kid, start, terms, checks, practice | [[databases/06-the-query-pipeline\|06-the-query-pipeline]] |
| 10 | ⬜ not started | kid, start, terms, checks, practice | [[databases/07-join-algorithms-and-the-optimiser\|07-join-algorithms-and-the-optimiser]] |
| 11 | ⬜ not started | kid, start, terms, checks, practice | [[databases/08-transactions-and-acid\|08-transactions-and-acid]] |
| 11 | ⬜ not started | kid, start, terms, checks, practice | [[databases/09-mvcc-and-concurrency-control\|09-mvcc-and-concurrency-control]] |
| 11 | ⬜ not started | kid, start, terms, checks, practice | [[databases/10-durability-and-recovery\|10-durability-and-recovery]] |
| 11 | ⬜ not started | kid, start, terms, checks, practice | [[databases/11-replication-and-scaling\|11-replication-and-scaling]] |
| 11 | ⬜ not started | kid, start, terms, checks, practice | [[databases/12-operating-a-database\|12-operating-a-database]] |
| 12 | 🟡 partial | start, terms, checks, practice | [[networking/01-what-a-network-is\|01-what-a-network-is]] |
| 12 | 🟡 partial | start, terms, checks, practice | [[networking/04-routing\|04-routing]] |
| 12 | 🟡 partial | start, terms, checks, practice | [[networking/02-the-link-layer\|02-the-link-layer]] |
| 12 | 🟡 partial | start, terms, checks, practice | [[networking/03-ip-addressing-and-subnetting\|03-ip-addressing-and-subnetting]] |
| 13 | 🟡 partial | start, terms, checks, practice | [[networking/05-udp-and-ports\|05-udp-and-ports]] |
| 13 | 🟡 partial | start, terms, checks, practice | [[networking/09-sockets-and-the-network-api\|09-sockets-and-the-network-api]] |
| 13 | 🟡 partial | start, terms, checks, practice | [[networking/06-tcp-connection-lifecycle\|06-tcp-connection-lifecycle]] |
| 13 | 🟡 partial | start, terms, checks, practice | [[networking/07-tcp-reliability-and-flow-control\|07-tcp-reliability-and-flow-control]] |
| 13 | 🟡 partial | start, terms, checks, practice | [[networking/08-congestion-control\|08-congestion-control]] |
| 14 | 🟡 partial | start, terms, checks, practice | [[networking/10-dns-in-depth\|10-dns-in-depth]] |
| 14 | 🟡 partial | start, terms, checks, practice | [[networking/13-quic-and-modern-transport\|13-quic-and-modern-transport]] |
| 14 | 🟡 partial | start, terms, checks, practice | [[networking/11-http-evolution\|11-http-evolution]] |
| 14 | 🟡 partial | start, terms, checks, practice | [[networking/12-tls-and-transport-security\|12-tls-and-transport-security]] |
| 14 | ⬜ not started | kid, start, terms, checks, practice | [[backend/05-auth/01-authentication-flows\|01-authentication-flows]] |
| 15 | 🟡 partial | start, terms, checks, practice | [[networking/14-nat-firewalls-and-middleboxes\|14-nat-firewalls-and-middleboxes]] |
| 15 | ⬜ not started | kid, start, terms, checks, practice | [[networking/16-debugging-networks\|16-debugging-networks]] |
| 15 | 🟡 partial | start, terms, checks, practice | [[networking/15-network-performance\|15-network-performance]] |
| 16 | ⬜ not started | kid, start, terms, checks, practice | [[cybersecurity/04-web-security/02-secure-authentication\|02-secure-authentication]] |
| 16 | ⬜ not started | kid, start, terms, checks, practice | [[backend/05-auth/02-authorization\|02-authorization]] |
| 16 | ⬜ not started | kid, start, terms, checks, practice | [[cybersecurity/05-cryptography/03-hashing-and-integrity\|03-hashing-and-integrity]] |
| 16 | ⬜ not started | kid, start, terms, checks, practice | [[backend/05-auth/03-oauth-provider-integrations\|03-oauth-provider-integrations]] |
| 17 | ⬜ not started | kid, start, terms, checks, practice | [[cybersecurity/04-web-security/01-input-validation-and-output-encoding\|01-input-validation-and-output-encoding]] |
| 17 | ⬜ not started | kid, start, terms, checks, practice | [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy\|04-security-headers-and-same-origin-policy]] |
| 17 | ⬜ not started | kid, start, terms, checks, practice | [[cybersecurity/05-cryptography/02-symmetric-encryption\|02-symmetric-encryption]] |
| 17 | ⬜ not started | kid, start, terms, checks, practice | [[cybersecurity/05-cryptography/04-asymmetric-encryption\|04-asymmetric-encryption]] |
| 17 | ⬜ not started | kid, start, terms, checks, practice | [[cybersecurity/05-cryptography/05-digital-signatures-and-pki\|05-digital-signatures-and-pki]] |
| 17 | ⬜ not started | kid, start, terms, checks, practice | [[cybersecurity/04-web-security/03-https-and-tls\|03-https-and-tls]] |
| 17 | ⬜ not started | kid, start, terms, checks, practice | [[devops/09-secret-management/01-secret-management\|01-secret-management]] |
| 17 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/10-safety-and-production\|10-safety-and-production]] |
| 18 | ⬜ not started | kid, start, terms, checks, practice | [[backend/02-api-design/01-apis-and-rest\|01-apis-and-rest]] |
| 18 | 🟡 partial | start, terms, checks, practice | [[backend/01-foundations/01-what-a-backend-is\|01-what-a-backend-is]] |
| 18 | ⬜ not started | kid, start, terms, checks, practice | [[backend/01-foundations/02-http-servers\|02-http-servers]] |
| 18 | 🟡 partial | start, terms, checks, practice | [[backend/01-foundations/03-the-request-lifecycle\|03-the-request-lifecycle]] |
| 18 | 🟡 partial | start, terms, checks, practice | [[backend/01-foundations/04-runtime-and-concurrency-models\|04-runtime-and-concurrency-models]] |
| 19 | ⬜ not started | kid, start, terms, checks, practice | [[backend/07-practices/01-backend-best-practices\|01-backend-best-practices]] |
| 19 | 🟡 partial | start, terms, checks, practice | [[backend/07-practices/02-testing-a-backend\|02-testing-a-backend]] |
| 19 | ⬜ not started | kid, start, terms, checks, practice | [[backend/04-data-and-persistence/01-databases-in-the-backend\|01-databases-in-the-backend]] |
| 19 | n/a | keeps its own shape | [[concepts/interview/01-apis-auth-and-practices\|01-apis-auth-and-practices]] |
| 20 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/01-the-ai-engineer-role\|01-the-ai-engineer-role]] |
| 20 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/02-how-llms-work\|02-how-llms-work]] |
| 20 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/03-the-model-landscape\|03-the-model-landscape]] |
| 20 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/04-calling-models\|04-calling-models]] |
| 21 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/05-prompt-engineering\|05-prompt-engineering]] |
| 21 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/11-structured-output\|11-structured-output]] |
| 21 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/06-rag-and-embeddings\|06-rag-and-embeddings]] |
| 22 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/07-tools-and-mcp\|07-tools-and-mcp]] |
| 22 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/08-agents\|08-agents]] |
| 22 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/09-multimodal\|09-multimodal]] |
| 23 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/12-evals\|12-evals]] |
| 23 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/13-reliability-and-plumbing\|13-reliability-and-plumbing]] |
| 23 | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/14-cost-caching-and-latency\|14-cost-caching-and-latency]] |
| 23 | n/a | keeps its own shape | [[ai-ml/03-ai-engineer/19-practice-exercises\|19-practice-exercises]] |
| 23 | n/a | keeps its own shape | [[ai-ml/03-ai-engineer/20-practice-exercises-solutions\|20-practice-exercises-solutions]] |
| 24 | ⬜ not started | kid, start, terms, checks, practice | [[concepts/04-best-practices/04-testing-fundamentals\|04-testing-fundamentals]] |
| 24 | ⬜ not started | kid, start, terms, checks, practice | [[concepts/04-best-practices/02-pr-structure\|02-pr-structure]] |
| 24 | ⬜ not started | kid, start, terms, checks, practice | [[devops/10-observability/01-observability-fundamentals\|01-observability-fundamentals]] |
| 24 | ⬜ not started | kid, start, terms, checks, practice | [[devops/10-observability/02-the-observability-stack\|02-the-observability-stack]] |
| 25 | ⬜ not started | kid, start, terms, checks, practice | [[devops/02-docker/01-new-docker\|01-new-docker]] |
| 25 | ⬜ not started | kid, start, terms, checks, practice | [[devops/02-docker/04-multi-stage-builds\|04-multi-stage-builds]] |
| 25 | ⬜ not started | kid, start, terms, checks, practice | [[devops/06-ci-cd/01-ci-cd-concepts\|01-ci-cd-concepts]] |
| 25 | ⬜ not started | kid, start, terms, checks, practice | [[devops/06-ci-cd/08-ci-pipelines\|08-ci-pipelines]] |
| 25 | ⬜ not started | kid, start, terms, checks, practice | [[devops/06-ci-cd/09-cd-and-deployment\|09-cd-and-deployment]] |
| 25 | ⬜ not started | kid, start, terms, checks, practice | [[devops/06-ci-cd/10-pipeline-security\|10-pipeline-security]] |
| 25 | ⬜ not started | kid, start, terms, checks, practice | [[devops/06-ci-cd/12-troubleshooting-workflows\|12-troubleshooting-workflows]] |
| 26 | ⬜ not started | kid, start, terms, checks, practice | [[os/02-processes-and-threads\|02-processes-and-threads]] |
| 26 | ⬜ not started | kid, start, terms, checks, practice | [[os/03-scheduling\|03-scheduling]] |
| 26 | ⬜ not started | kid, start, terms, checks, practice | [[os/06-concurrency-primitives\|06-concurrency-primitives]] |
| 27 | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard\|01-what-makes-distributed-systems-hard]] |
| 27 | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/02-theoretical-limits\|02-theoretical-limits]] |
| 27 | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/03-time-and-ordering\|03-time-and-ordering]] |
| 27 | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/04-consistency-models\|04-consistency-models]] |
| 28 | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/05-replication\|05-replication]] |
| 28 | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/13-partitioning\|13-partitioning]] |
| 28 | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/07-consensus-and-paxos\|07-consensus-and-paxos]] |
| 28 | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/08-raft-in-depth\|08-raft-in-depth]] |
| 29 | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/10-distributed-transactions\|10-distributed-transactions]] |
| 29 | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/12-the-log-and-state-machines\|12-the-log-and-state-machines]] |
| 29 | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/14-failure-detection-and-membership\|14-failure-detection-and-membership]] |
| 29 | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/15-testing-distributed-systems\|15-testing-distributed-systems]] |
| 30 | n/a | keeps its own shape | [[INTERVIEW\|INTERVIEW]] |
| 30 | n/a | keeps its own shape | [[projects/nextvibe/interview/05-platform-payments-and-story\|05-platform-payments-and-story]] |
| 31+ | ⬜ not started | kid, start, terms, checks, practice | [[compilers/01-what-a-compiler-is\|01-what-a-compiler-is]] |
| 31+ | ⬜ not started | kid, start, terms, checks, practice | [[os/05-memory-allocation\|05-memory-allocation]] |
| 31+ | ⬜ not started | kid, start, terms, checks, practice | [[os/04-virtual-memory\|04-virtual-memory]] |
| 31+ | ⬜ not started | kid, start, terms, checks, practice | [[computer-architecture/08-the-memory-hierarchy\|08-the-memory-hierarchy]] |
| 31+ | ⬜ not started | kid, start, terms, checks, practice | [[computer-architecture/09-caches-in-depth\|09-caches-in-depth]] |
| 31+ | ⬜ not started | kid, start, terms, checks, practice | [[os/09-syscalls-interrupts-and-the-abi\|09-syscalls-interrupts-and-the-abi]] |
| 31+ | ⬜ not started | kid, start, terms, checks, practice | [[theory-of-computation/07-complexity-classes\|07-complexity-classes]] |
| 31+ | ⬜ not started | kid, start, terms, checks, practice | [[theory-of-computation/02-finite-automata\|02-finite-automata]] |
| 31+ | ⬜ not started | kid, start, terms, checks, practice | [[compilers/02-lexical-analysis\|02-lexical-analysis]] |
| 31+ | ⬜ not started | kid, start, terms, checks, practice | [[compilers/03-parsing\|03-parsing]] |
| 31+ | ⬜ not started | kid, start, terms, checks, practice | [[compilers/11-garbage-collection\|11-garbage-collection]] |
| 31+ | ⬜ not started | kid, start, terms, checks, practice | [[computer-architecture/12-performance\|12-performance]] |

<!-- AUDIT:END -->

## Review log

_Date · lesson · studied closed-book? · where the explanation, setup or exercise needed guessing._
