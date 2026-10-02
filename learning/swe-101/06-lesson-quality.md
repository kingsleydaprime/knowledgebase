# Lesson Quality — the SWE courses against the course standard

> Which of the lessons [[learning/swe-101/index|SWE 101]], [[learning/swe-102/index|102]] and [[learning/swe-103/index|103]] send you to meet [[COURSE-STANDARD|the course standard]]. **Core lessons are converted first, one course ahead of study.**

**Generated, not hand-written** — run `python3 learning/swe-101/scripts/audit-standard.py` from the vault root after converting a lesson.

**What the check looks for:** a kid version, a "Before you start" section, a numbered "Terms used in…" list, questions with answers hidden behind a fold, and a "Practice" task. Passing the check means the sections are there — not that the lesson teaches well. That is only established by studying it closed-book, so **note anywhere you got stuck** in the review log below.

**Order of work:** SWE 101 core → SWE 102 core → SWE 103 core, then optional lessons. References, interview banks and exercise sets keep their own shapes and are marked n/a.

<!-- AUDIT:START -->

**Core lessons: 14 of 43 meet the standard. Optional: 8 of 36.**

| Course | Week | Lane | Status | Missing | Lesson |
|---|---|---|---|---|---|
| SWE 101 | 1 | core | ✅ meets | — | [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories\|01-layers-controllers-services-repositories]] |
| SWE 101 | 1 | core | ✅ meets | — | [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature\|02-organising-by-layer-vs-by-feature]] |
| SWE 101 | 1 | optional | ✅ meets | — | [[backend/03-structuring-a-backend/02b-organising-by-feature-in-compiled-languages\|02b-organising-by-feature-in-compiled-languages]] |
| SWE 101 | 1 | optional | ✅ meets | — | [[software-engineering/01-what-software-engineering-is\|01-what-software-engineering-is]] |
| SWE 101 | 1 | optional | ✅ meets | — | [[software-engineering/02-the-software-development-lifecycle\|02-the-software-development-lifecycle]] |
| SWE 101 | 2 | core | ✅ meets | — | [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring\|03-dependency-injection-and-wiring]] |
| SWE 101 | 2 | core | ✅ meets | — | [[concepts/04-best-practices/04-testing-fundamentals\|04-testing-fundamentals]] |
| SWE 101 | 2 | optional | 🟡 partial | start, terms, checks, practice | [[backend/07-practices/02-testing-a-backend\|02-testing-a-backend]] |
| SWE 101 | 2 | optional | ✅ meets | — | [[backend/03-structuring-a-backend/03b-dependency-injection-in-other-languages\|03b-dependency-injection-in-other-languages]] |
| SWE 101 | 3 | core | ✅ meets | — | [[concepts/04-best-practices/08-coupling-and-cohesion\|08-coupling-and-cohesion]] |
| SWE 101 | 3 | core | ✅ meets | — | [[concepts/04-best-practices/05-solid-principles\|05-solid-principles]] |
| SWE 101 | 3 | optional | ✅ meets | — | [[concepts/04-best-practices/01-clean-code\|01-clean-code]] |
| SWE 101 | 4 | core | ✅ meets | — | [[concepts/03-design-patterns/03-behavioral-patterns\|03-behavioral-patterns]] |
| SWE 101 | 4 | core | ✅ meets | — | [[concepts/03-design-patterns/02-structural-patterns\|02-structural-patterns]] |
| SWE 101 | 4 | optional | ✅ meets | — | [[concepts/03-design-patterns/01-creational-patterns\|01-creational-patterns]] |
| SWE 101 | 5 | core | ✅ meets | — | [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture\|04-hexagonal-and-clean-architecture]] |
| SWE 101 | 5 | core | ✅ meets | — | [[backend/03-structuring-a-backend/05-modular-monolith-to-services\|05-modular-monolith-to-services]] |
| SWE 101 | 5 | optional | ✅ meets | — | [[architecture/03-architectural-patterns/05-transactional-outbox\|05-transactional-outbox]] |
| SWE 101 | 6 | core | ✅ meets | — | [[backend/07-practices/01-backend-best-practices\|01-backend-best-practices]] |
| SWE 101 | 6 | core | ✅ meets | — | [[devops/10-observability/01-observability-fundamentals\|01-observability-fundamentals]] |
| SWE 101 | 6 | optional | ⬜ not started | kid, start, terms, checks, practice | [[devops/10-observability/02-the-observability-stack\|02-the-observability-stack]] |
| SWE 101 | 7 | core | ✅ meets | — | [[cybersecurity/04-web-security/01-input-validation-and-output-encoding\|01-input-validation-and-output-encoding]] |
| SWE 101 | 7 | core | ✅ meets | — | [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy\|04-security-headers-and-same-origin-policy]] |
| SWE 101 | 7 | optional | ⬜ not started | kid, start, terms, checks, practice | [[devops/09-secret-management/01-secret-management\|01-secret-management]] |
| SWE 101 | 7 | optional | ⬜ not started | kid, start, terms, checks, practice | [[backend/05-auth/01-authentication-flows\|01-authentication-flows]] |
| SWE 102 | 1 | core | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/02-how-llms-work\|02-how-llms-work]] |
| SWE 102 | 1 | core | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/04-calling-models\|04-calling-models]] |
| SWE 102 | 1 | optional | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/01-the-ai-engineer-role\|01-the-ai-engineer-role]] |
| SWE 102 | 1 | optional | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/03-the-model-landscape\|03-the-model-landscape]] |
| SWE 102 | 1 | optional | ✅ meets | — | [[ai-ml/03-ai-engineer/16-local-and-open-models\|16-local-and-open-models]] |
| SWE 102 | 2 | core | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/11-structured-output\|11-structured-output]] |
| SWE 102 | 2 | core | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/05-prompt-engineering\|05-prompt-engineering]] |
| SWE 102 | 2 | optional | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/06-rag-and-embeddings\|06-rag-and-embeddings]] |
| SWE 102 | 3 | core | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/12-evals\|12-evals]] |
| SWE 102 | 3 | core | n/a | keeps its own shape | [[ai-ml/03-ai-engineer/19-practice-exercises\|19-practice-exercises]] |
| SWE 102 | 4 | core | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/13-reliability-and-plumbing\|13-reliability-and-plumbing]] |
| SWE 102 | 4 | core | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/14-cost-caching-and-latency\|14-cost-caching-and-latency]] |
| SWE 102 | 4 | optional | ⬜ not started | kid, start, terms, checks, practice | [[architecture/03-architectural-patterns/02-resilience-patterns\|02-resilience-patterns]] |
| SWE 102 | 5 | core | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/07-tools-and-mcp\|07-tools-and-mcp]] |
| SWE 102 | 5 | core | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/08-agents\|08-agents]] |
| SWE 102 | 5 | optional | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/09-multimodal\|09-multimodal]] |
| SWE 102 | 6 | core | ⬜ not started | kid, start, terms, checks, practice | [[ai-ml/03-ai-engineer/10-safety-and-production\|10-safety-and-production]] |
| SWE 103 | 1 | core | ⬜ not started | kid, start, terms, checks, practice | [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design\|01-how-to-approach-system-design]] |
| SWE 103 | 1 | core | ⬜ not started | kid, start, terms, checks, practice | [[architecture/01-system-design-fundamentals/02-scalability-and-performance\|02-scalability-and-performance]] |
| SWE 103 | 1 | optional | n/a | keeps its own shape | [[architecture/interview/01-system-design-round\|01-system-design-round]] |
| SWE 103 | 2 | core | ⬜ not started | kid, start, terms, checks, practice | [[architecture/02-building-blocks/02-caching\|02-caching]] |
| SWE 103 | 2 | core | ⬜ not started | kid, start, terms, checks, practice | [[architecture/02-building-blocks/01-load-balancing-and-proxies\|01-load-balancing-and-proxies]] |
| SWE 103 | 2 | optional | ⬜ not started | kid, start, terms, checks, practice | [[architecture/01-system-design-fundamentals/03-availability-and-reliability\|03-availability-and-reliability]] |
| SWE 103 | 2 | optional | ⬜ not started | kid, start, terms, checks, practice | [[architecture/01-system-design-fundamentals/04-cap-and-consistency\|04-cap-and-consistency]] |
| SWE 103 | 3 | core | ⬜ not started | kid, start, terms, checks, practice | [[architecture/02-building-blocks/04-messaging-and-async\|04-messaging-and-async]] |
| SWE 103 | 3 | core | ⬜ not started | kid, start, terms, checks, practice | [[architecture/02-building-blocks/05-communication\|05-communication]] |
| SWE 103 | 3 | optional | ⬜ not started | kid, start, terms, checks, practice | [[architecture/02-building-blocks/03-databases-at-scale\|03-databases-at-scale]] |
| SWE 103 | 4 | core | ⬜ not started | kid, start, terms, checks, practice | [[architecture/03-architectural-patterns/01-monolith-microservices-serverless\|01-monolith-microservices-serverless]] |
| SWE 103 | 4 | optional | ⬜ not started | kid, start, terms, checks, practice | [[architecture/03-architectural-patterns/03-data-and-integration-patterns\|03-data-and-integration-patterns]] |
| SWE 103 | 4 | optional | ⬜ not started | kid, start, terms, checks, practice | [[architecture/03-architectural-patterns/04-microservices-patterns\|04-microservices-patterns]] |
| SWE 103 | 5 | core | ⬜ not started | kid, start, terms, checks, practice | [[databases/04-b-trees-and-indexes\|04-b-trees-and-indexes]] |
| SWE 103 | 5 | core | ⬜ not started | kid, start, terms, checks, practice | [[databases/07-join-algorithms-and-the-optimiser\|07-join-algorithms-and-the-optimiser]] |
| SWE 103 | 5 | optional | ⬜ not started | kid, start, terms, checks, practice | [[databases/01-what-a-database-is\|01-what-a-database-is]] |
| SWE 103 | 5 | optional | ⬜ not started | kid, start, terms, checks, practice | [[databases/02-the-relational-model\|02-the-relational-model]] |
| SWE 103 | 5 | optional | ⬜ not started | kid, start, terms, checks, practice | [[databases/06-the-query-pipeline\|06-the-query-pipeline]] |
| SWE 103 | 6 | core | ⬜ not started | kid, start, terms, checks, practice | [[databases/08-transactions-and-acid\|08-transactions-and-acid]] |
| SWE 103 | 6 | core | ⬜ not started | kid, start, terms, checks, practice | [[databases/09-mvcc-and-concurrency-control\|09-mvcc-and-concurrency-control]] |
| SWE 103 | 6 | optional | ⬜ not started | kid, start, terms, checks, practice | [[databases/12-operating-a-database\|12-operating-a-database]] |
| SWE 103 | 6 | optional | ⬜ not started | kid, start, terms, checks, practice | [[databases/11-replication-and-scaling\|11-replication-and-scaling]] |
| SWE 103 | 7 | core | 🟡 partial | start, terms, checks, practice | [[networking/10-dns-in-depth\|10-dns-in-depth]] |
| SWE 103 | 7 | core | 🟡 partial | start, terms, checks, practice | [[networking/11-http-evolution\|11-http-evolution]] |
| SWE 103 | 7 | core | 🟡 partial | start, terms, checks, practice | [[networking/12-tls-and-transport-security\|12-tls-and-transport-security]] |
| SWE 103 | 7 | optional | 🟡 partial | start, terms, checks, practice | [[networking/06-tcp-connection-lifecycle\|06-tcp-connection-lifecycle]] |
| SWE 103 | 8 | core | 🟡 partial | start, terms, checks, practice | [[backend/01-foundations/03-the-request-lifecycle\|03-the-request-lifecycle]] |
| SWE 103 | 8 | core | 🟡 partial | start, terms, checks, practice | [[backend/01-foundations/04-runtime-and-concurrency-models\|04-runtime-and-concurrency-models]] |
| SWE 103 | 8 | optional | ⬜ not started | kid, start, terms, checks, practice | [[networking/16-debugging-networks\|16-debugging-networks]] |
| SWE 103 | 8 | optional | ⬜ not started | kid, start, terms, checks, practice | [[os/06-concurrency-primitives\|06-concurrency-primitives]] |
| SWE 103 | 9 | core | ⬜ not started | kid, start, terms, checks, practice | [[backend/05-auth/03-oauth-provider-integrations\|03-oauth-provider-integrations]] |
| SWE 103 | 9 | optional | ⬜ not started | kid, start, terms, checks, practice | [[backend/05-auth/02-authorization\|02-authorization]] |
| SWE 103 | 9 | optional | ⬜ not started | kid, start, terms, checks, practice | [[cybersecurity/05-cryptography/03-hashing-and-integrity\|03-hashing-and-integrity]] |
| SWE 103 | 9 | optional | ⬜ not started | kid, start, terms, checks, practice | [[cybersecurity/05-cryptography/05-digital-signatures-and-pki\|05-digital-signatures-and-pki]] |
| SWE 103 | 10 | core | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard\|01-what-makes-distributed-systems-hard]] |
| SWE 103 | 10 | core | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/04-consistency-models\|04-consistency-models]] |
| SWE 103 | 10 | optional | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/05-replication\|05-replication]] |
| SWE 103 | 10 | optional | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/13-partitioning\|13-partitioning]] |
| SWE 103 | 10 | optional | 🟡 partial | start, terms, checks, practice | [[architecture/04-distributed-systems/10-distributed-transactions\|10-distributed-transactions]] |

<!-- AUDIT:END -->

## Review log

_Date · lesson · studied closed-book? · where the explanation, setup or exercise needed guessing._
