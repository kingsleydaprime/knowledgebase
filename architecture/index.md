# Architecture: System Design and Distributed Systems

## What software architecture is

**Software architecture is planning how the parts of a large system fit together, so it can serve many users, keep working when something breaks, and keep its data correct.**

A small app can run on one computer with one database. When millions of people use it, that stops working: one computer can't handle the load, and if it fails, everything goes down. So big systems are spread across many machines, with pieces like **load balancers** (sharing requests between servers), **caches** (keeping popular answers ready), and **message queues** (passing work along to be done later). Architecture is choosing those pieces and how they connect, and understanding the trade-off each choice makes.

The course has two halves. **System design** is the practical skill of planning a system for a given number of users, speed and reliability; it's also a standard interview for senior roles. **Distributed systems** is the theory underneath: why getting many machines to agree is genuinely hard, and the methods that make it work.

## What you'll be able to do

By the end you will be able to:
- plan a system step by step: work out what it must do, estimate the load, sketch the design, and explain the trade-offs;
- explain how systems grow to handle more users, and how they stay up when parts fail;
- choose between building blocks such as caches, queues and different kinds of database;
- choose between one big app and many small services;
- explain why machines on a network struggle to agree on what happened and when, and how methods like Raft fix that;
- answer system design interview questions.

## Where to start

**Before you start:** you should know how a [[backend/index|backend]] and a [[databases/index|database]] work. [[networking/index|Networking]] helps for section 02.

Read the sections in order. Sections 01–03 are system design; section 04 is the theory.

### 01. System design fundamentals

1. [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index|How to Approach System Design]]: a step-by-step method for designing a system, which is also how to pass the interview.
2. [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|Scalability and Performance]]: making a system handle more by using bigger machines or more machines, and the difference between fast and able-to-handle-a-lot.
3. [[architecture/01-system-design-fundamentals/03-availability-and-reliability|Availability and Reliability]]: keeping a system up, measuring uptime, and having spares ready when something fails.
4. [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP and Consistency]]: why, when a network breaks, a system must choose between always answering and always answering correctly.

### 02. Building blocks

5. [[architecture/02-building-blocks/01-load-balancing-and-proxies/index|Load Balancing and Proxies]]: sharing requests across servers, and the servers that sit in front of yours.
6. [[architecture/02-building-blocks/02-caching/index|Caching]]: keeping copies of popular data close by, and the hard problem of knowing when a copy is out of date.
7. [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]]: choosing a database, copying it across machines, and splitting data when one machine isn't enough.
8. [[architecture/02-building-blocks/04-messaging-and-async/index|Messaging and Async]]: passing work through queues so slow jobs don't hold up users.
9. [[architecture/02-building-blocks/05-communication/index|Communication]]: the different ways services talk to each other: REST, gRPC and GraphQL.

### 03. Architectural patterns

10. [[architecture/03-architectural-patterns/01-monolith-microservices-serverless/index|Monolith, Microservices, Serverless]]: one big app, many small services, or code that runs only on demand, and when each fits.
11. [[architecture/03-architectural-patterns/02-resilience-patterns/index|Resilience Patterns]]: designing for failure: retries, time limits, and stopping one broken part from bringing down the rest.
12. [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data and Integration Patterns]]: ways of keeping data consistent across services, and replacing an old system piece by piece.
13. [[architecture/03-architectural-patterns/04-microservices-patterns|Microservices Patterns]]: how many small services find each other and work together.
14. [[architecture/03-architectural-patterns/05-transactional-outbox/index|Transactional Outbox]]: saving data and sending a message about it, without ever doing one and not the other.

### 04. Distributed systems (the theory)

This is harder and more theoretical. It's what you need for building your own databases or coordination systems.

15. [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes Distributed Systems Hard]]: machines fail partly, networks lose messages, and there's no shared clock.
16. [[architecture/04-distributed-systems/02-theoretical-limits|Theoretical Limits]]: what's been proven impossible, and what that means in practice.
17. [[architecture/04-distributed-systems/03-time-and-ordering|Time and Ordering]]: working out what happened first without a shared clock.
18. [[architecture/04-distributed-systems/04-consistency-models|Consistency Models]]: the different promises a system can make about how up to date your reads are.
19. [[architecture/04-distributed-systems/05-replication|Replication]]: keeping copies of data on several machines.
20. [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|CRDTs and Conflict Resolution]]: data types that can be edited in several places at once and still merge correctly.
21. [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus and Paxos]]: getting machines to agree on one answer even when some fail.
22. [[architecture/04-distributed-systems/08-raft-in-depth|Raft in Depth]]: the most widely used method for reaching agreement, step by step.
23. [[architecture/04-distributed-systems/09-coordination-services|Coordination Services]]: tools like ZooKeeper and etcd that handle agreement for you.
24. [[architecture/04-distributed-systems/10-distributed-transactions|Distributed Transactions]]: making a change across several machines all-or-nothing.
25. [[architecture/04-distributed-systems/11-modern-distributed-transactions|Modern Distributed Transactions]]: how today's databases do this at scale.
26. [[architecture/04-distributed-systems/12-the-log-and-state-machines|The Log and State Machines]]: the simple idea at the heart of many reliable systems: an ordered list of everything that happened.
27. [[architecture/04-distributed-systems/13-partitioning|Partitioning]]: splitting data across machines evenly.
28. [[architecture/04-distributed-systems/14-failure-detection-and-membership|Failure Detection and Membership]]: noticing when a machine is gone, and keeping track of who's in the group.
29. [[architecture/04-distributed-systems/15-testing-distributed-systems|Testing Distributed Systems]]: how to find bugs that only appear when timing goes wrong.

### 05. Case studies

30. [[architecture/05-case-studies/01-designing-real-systems|Designing Real Systems]]: putting it all together on real examples.

## For quick lookup

- [[architecture/system-design-reference|System design reference]]: a dense cheat sheet of everything you might draw in a design, for looking up rather than reading.

## Practice

- [[architecture/projects|Projects]]: hands-on tasks, from easy (🟢) to hard (🔴), each with a clear "done when".
- [[architecture/interview/index|Architecture interview prep]]: the system design round, and distributed systems in depth.
- [[build-your-own-shit/index|Build Your Own]]: build your own Redis, database or Raft, the best way to make section 04 real.

## Key ideas to remember

1. **Every design choice is a trade-off.** There's no best architecture, only one that fits the needs you wrote down first. → [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index|How to Approach System Design]]
2. **Grow one machine before adding more.** Many machines bring problems one machine never has. → [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|Scalability]]
3. **When the network breaks, you choose between answering and being correct.** → [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP]]
4. **Design for failure.** In a large system, something is always broken. → [[architecture/03-architectural-patterns/02-resilience-patterns/index|Resilience Patterns]]
5. **Don't start with microservices.** Split a system only when you know where the natural boundaries are. → [[architecture/03-architectural-patterns/01-monolith-microservices-serverless/index|Monolith, Microservices, Serverless]]

## Related

- [[backend/index|Backend]]: one service, in depth.
- [[databases/index|Databases]]: the storage these systems are built on.
- [[devops/index|DevOps]]: running these systems for real.

---

## About this course

- **Where it came from:** sections 01–03 were checked against the [roadmap.sh system design roadmap](https://roadmap.sh/system-design). There's no roadmap for distributed systems, so section 04 comes from the standard sources: *Designing Data-Intensive Applications* (Kleppmann) and MIT's 6.824 distributed systems course.
