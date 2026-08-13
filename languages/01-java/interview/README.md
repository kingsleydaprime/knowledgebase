# Java — Interview Prep

Question bank from the [[languages/01-java/README|Java course]], weighted toward what a **low-latency / systems** role screens for — that's the stated target in [[PRIMETECHIE|the Primetechie path]], and file 02 is where those interviews are actually won or lost.

Format: the question, what a **strong answer covers**, and the **detail worth adding** that separates memorised from understood. 🔥 = comes up constantly.

## Files
1. [[languages/01-java/interview/01-language-and-collections|Language & Collections]] — the screening round: equals/hashCode, HashMap internals, generics, streams, records
2. [[languages/01-java/interview/02-jvm-and-concurrency|JVM & Concurrency]] — **the important one**: GC, the memory model, `volatile`, thread pools, virtual threads, false sharing, lock-free structures
3. [[languages/01-java/interview/03-spring-persistence-and-systems|Spring, Persistence & Systems]] — DI, N+1, `@Transactional`'s silent failures, concurrency control, idempotency, containers, testing

## The three answers that matter most

If you prepare nothing else:

1. **"Walk me through a p99 latency investigation."** (02 Q11) — it's the whole role in one question, and the answer is a *method*, not a list of causes.
2. **"How do you prevent overselling / lost updates?"** (03 Q5) — tests whether you understand isolation levels or just ORM syntax.
3. **"What does `volatile` guarantee?"** (02 Q4) — the fastest way to find out whether someone understands the memory model or has memorised a definition.

## Where your real projects come in

The strongest material you have is your own code. Have a crisp story ready for each:

- **[[projects/direct-debit-sandbox-java/learning/01-java-fundamentals|direct-debit-sandbox]]** → idempotency, transactions, payments correctness (03 Q5–Q6)
- **[[projects/record-id-generator-java/learning/01-java-fundamentals|record-id-generator]]** → ID generation tradeoffs, batch processing, throughput (03 Q8)
- **The gap to close:** no build-your-own systems project finished yet. A lock-free ring buffer or an order-book matching engine would answer 02 Q10 with "I built one" instead of "I've read about it" — see [[project-ideas|project-ideas]].

## Related
- [[languages/01-java/README|Java course]]
- [[foundations/networking/interview/README|Networking interview prep]] — 02 Q11 needs it
- [[architecture/interview/README|Architecture interview prep]] — the system design round
- [[foundations/dsa/interview/README|DSA interview prep]] — the coding round
