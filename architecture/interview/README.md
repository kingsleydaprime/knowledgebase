# Architecture — Interview Prep

From the [[architecture/README|Architecture course]]. Two rounds, tested very differently:

## Files
1. [[architecture/interview/01-system-design-round|The System Design Round]] — the framework, the numbers, and the classic problems (URL shortener, rate limiter, news feed, caching, scaling a database)
2. [[architecture/interview/02-distributed-systems-depth|Distributed Systems Depth]] — consensus, consistency models, exactly-once, sagas, failure detection, testing

## The one thing to internalise

**The system design round is not a knowledge test.** They already know you can look up what a CDN is. They're testing whether you can take an ambiguous problem, ask the questions that scope it, make a decision, and defend it — because that's the job.

The two failure modes, in order of frequency:
1. **Designing before scoping.** Drawing boxes before you know whether it's 1,000 or 100 million users. Always spend the first five minutes on requirements, out loud.
2. **Refusing to commit.** "It depends" is only a good answer when followed by "so I'd choose X, because our requirement is Y." An interviewer cannot distinguish thoughtful hedging from not knowing.

## Related
- [[architecture/README|Architecture course]] · [[architecture/system-design-reference|system-design cheat-sheet]]
- [[foundations/networking/interview/README|Networking interview prep]] — latency, tail latency, and load balancing all live there
- [[databases/interview/README|Databases interview prep]] — the storage half of every design
- [[languages/01-java/interview/README|Java interview prep]]
- [[PRIMETECHIE|The Primetechie Path]] — Ranks III–IV
