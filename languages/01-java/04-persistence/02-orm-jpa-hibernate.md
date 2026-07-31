# ORM: JPA & Hibernate

**Source:** **[reference — the projects deliberately used raw JDBC, not an ORM]**. That choice is itself the most useful lens here: knowing what an ORM does lets you say *why* raw JDBC was right for a high-throughput bulk pipeline, rather than reaching for Hibernate reflexively. Covered from [roadmap.sh Java](https://roadmap.sh/java).

## What an ORM does

Object-Relational Mapping maps Java objects to database rows so you work with objects instead of writing SQL by hand. The layers, which get conflated constantly:

- **JPA** (Jakarta Persistence API) — the *specification*. Annotations (`@Entity`, `@Id`) and the `EntityManager` API. JPA is an interface, not an implementation.
- **Hibernate** — the dominant *implementation* of JPA (the reference-quality one). This is what actually runs.
- **Spring Data JPA** — a layer *on top* that generates repository implementations from interface method names, so you write almost no query code.

```java
@Entity
@Table(name = "transactions")
public class Transaction {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false)
    private BigDecimal amount;
    @ManyToOne(fetch = FetchType.LAZY)
    private Merchant merchant;
}
```

With Spring Data JPA, a repository is just an interface — the implementation is generated:

```java
public interface TransactionRepository extends JpaRepository<Transaction, Long> {
    List<Transaction> findByMerchantIdAndAmountGreaterThan(String merchantId, BigDecimal amount);
    // no body — Spring derives the SQL from the method name
}
```

## The concepts that bite

- **Entity lifecycle & the persistence context** — an `EntityManager` tracks *managed* entities in a first-level cache; changes to a managed entity are flushed to the DB automatically at transaction commit (**dirty checking**) — you often don't call `save()` at all. Entities move through transient → managed → detached → removed states, and misunderstanding which state an object is in is a top source of "why didn't my change persist / why did it persist twice" confusion.
- **Lazy vs eager loading** — `FetchType.LAZY` defers loading a relationship until it's accessed; `EAGER` loads it immediately. Lazy is the sane default, but accessing a lazy relationship *after* the transaction/session closed throws `LazyInitializationException` — a rite-of-passage Hibernate error.
- **The N+1 problem** — the ORM's most infamous performance trap. Loading 100 transactions and then touching each one's `merchant` fires 1 query for the list + 100 more for the merchants = 101 queries where a single `JOIN` would do. The fix is a `JOIN FETCH` / `@EntityGraph` / batch fetching — but you only spot it if you're watching the generated SQL, which is exactly the danger of an ORM: it hides the SQL until the SQL is the problem.

## When an ORM helps — and when raw JDBC wins

An ORM earns its keep on a **rich domain model with lots of entity types and relationships** and mostly transactional, per-record CRUD — the typical business/CRUD backend. It removes enormous boilerplate and gives you caching, dirty checking, and portability.

It gets in the way for exactly the profile the record-generator pipeline had:

| | ORM (Hibernate/JPA) | Raw JDBC (what the pipeline used) |
|---|---|---|
| Bulk insert of millions of rows | Fights you — per-entity tracking, flush/clear tuning, still slower | Direct control: `addBatch`/`executeBatch`, `rewriteBatchedStatements`, `LOAD DATA` |
| Control over exact SQL | Abstracted away | Total — you write the statement |
| Boilerplate for simple CRUD | Minimal | More (manual mapping) |
| Hidden performance cliffs | N+1, lazy-load surprises, dirty-check overhead | None hidden — the SQL is the code |

The pipeline needed batch inserts at 30k+ rows/sec with `rewriteBatchedStatements=true` and load-then-index tuning ([[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing]]). An ORM's per-entity persistence context is the *wrong tool* for that — the entity tracking overhead is pure cost when you're firehosing rows. **Choosing JDBC there was a correct engineering decision, and being able to articulate why (against the ORM default) is the point of knowing both.**

## The landscape

**Hibernate** dominates. **EclipseLink** is the other major JPA implementation. **Spring Data JPA** sits on Hibernate for most Spring apps. **jOOQ** is the interesting middle ground — type-safe SQL as Java (not object-mapping), giving ORM-like safety with JDBC-like control. **Ebean** (a roadmap.sh node) is a lighter-weight ORM with a simpler session model than JPA. **MyBatis** maps hand-written SQL to objects — SQL-first, mapping-second, closer to the JDBC end.

## Related
- [[languages/01-java/04-persistence/01-jdbc-and-data-modeling|JDBC & Data Modeling]] — the layer under the ORM, and what the projects actually used
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing & Performance]] — why the bulk pipeline stayed on JDBC
- [[languages/01-java/03-tooling/02-dependency-injection|Dependency Injection]] — how Spring Data repositories get injected
