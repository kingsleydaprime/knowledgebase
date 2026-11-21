---
id: 7cb3c6d7-52f5-4a08-a3a5-afd89a32b2fa
---

# Data Access

Data access is how a C# backend reads from and writes to its database. The two main tools are EF Core, which turns your C# code into database queries for you, and Dapper, which lets you write the queries yourself. Most slow .NET endpoints come down to three common mistakes covered here.

## EF Core
<!-- bite: f060ddc0-f7da-4252-b989-66b5dea83b0b -->

The default ORM. Full change tracking, LINQ-to-SQL translation, migrations.

```csharp
public class AppDb(DbContextOptions<AppDb> options) : DbContext(options)
{
    public DbSet<Order> Orders => Set<Order>();
    public DbSet<Customer> Customers => Set<Customer>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        b.Entity<Order>(e =>
        {
            e.HasIndex(o => new { o.Status, o.CreatedAt });     // composite index
            e.Property(o => o.Total).HasPrecision(18, 2);       // NOT float, for money
            e.HasOne(o => o.Customer).WithMany(c => c.Orders);
        });
    }
}
```

**`HasPrecision` on money is not optional.** Mapping a monetary column to a floating-point type is the [[programming-fundamentals/05-variables-and-types|float-money bug]] at the database layer. C#'s `decimal` and SQL `numeric` are the correct pair.

## The three mistakes
<!-- bite: 0a1bdf7d-0686-4ad3-a3aa-2e000562c5f4 -->

**1. N+1 — the most common, in every ORM.**

```csharp
foreach (var o in db.Orders.ToList())        // 1 query
    Console.WriteLine(o.Customer.Name);      // + 1 per order
```

```csharp
db.Orders.Include(o => o.Customer)           // ✓ one JOIN
db.Orders.Include(o => o.Items).ThenInclude(i => i.Product)
```

**EF Core throws on lazy loading by default in recent versions**, which surfaces this rather than hiding it — a genuinely good default. **Watch the query count, not the wall clock**, because on a local database with 10 rows it looks fine → [[databases/13-practice-exercises|databases exercise 7]].

**2. The `IQueryable` boundary.**

```csharp
db.Orders.Where(o => o.Total > 100).ToList();     // ✓ WHERE runs in SQL
db.Orders.ToList().Where(o => o.Total > 100);     // ✗ loads the whole table
```

**Those differ by the entire table** → [[languages/07-csharp/04-collections-and-linq|note 04]]. `ToList()`, `ToArray()` and `AsEnumerable()` are the boundary; everything after them runs in C#.

**And not all C# translates.** Calling your own method inside a `Where` on an `IQueryable` throws — EF can't turn it into SQL. Push translatable predicates into the query and do the rest after.

**3. Tracking you don't need.**

```csharp
db.Orders.AsNoTracking().Where(...)      // read-only: skips the change tracker
```

The change tracker snapshots every entity so `SaveChanges` can compute a diff. **On a read-only query that's pure overhead** — often 20–30% on large result sets. Use `AsNoTracking` for anything you won't modify.

## Migrations
<!-- bite: 5b1ca3d5-c73f-456a-96f8-7b0b6dd54df5 -->

```bash
dotnet ef migrations add AddOrderStatusIndex
dotnet ef database update
dotnet ef migrations script --idempotent      # for production
```

**Always read the generated migration before applying it.** EF infers intent from a model diff, and a *rename* is frequently detected as **drop-and-create — which is data loss** → [[databases/13-practice-exercises|databases exercise 4]].

**In production, apply migrations deliberately** — a generated SQL script reviewed and run by your deploy pipeline, not `Database.Migrate()` on startup. Startup migration races between instances and gives you no rollback → [[devops/05-ci-cd/index|CI/CD]].

## Dapper
<!-- bite: 9510cf1a-0e8b-4f94-8c4a-eaa77a320a08 -->

A micro-ORM: you write the SQL, it maps the results.

```csharp
var orders = await conn.QueryAsync<Order>(
    "SELECT id, total FROM orders WHERE status = @status LIMIT @take",
    new { status = "paid", take = 20 });
```

**No change tracking, no migrations, no LINQ translation** — and consequently no surprises about what SQL runs.

**When to prefer it:** complex reporting queries, hot read paths, anything where you want the SQL to be exactly what you wrote. **A very common architecture is both** — EF Core for writes and the domain model, Dapper for read queries.

**Parameters are non-negotiable in either.** `$"... WHERE id = {input}"` is SQL injection; the parameterised form is not → [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index|input validation]].

## Transactions and concurrency
<!-- bite: 6649ee52-91d8-48a0-93df-65e1470ae12e -->

```csharp
await using var tx = await db.Database.BeginTransactionAsync(ct);
// ... several SaveChangesAsync calls ...
await tx.CommitAsync(ct);
```

`SaveChanges` is already atomic for a single call — an explicit transaction is for spanning several, or for setting an isolation level → [[databases/08-transactions-and-acid/index|transactions]].

**Optimistic concurrency** with a `[Timestamp]`/`rowversion` column: EF adds the original value to the `WHERE` clause, and if zero rows update it throws `DbUpdateConcurrencyException`. **Handle it** — retry, or surface a conflict to the user. Ignoring it is a silent lost update.

## Connection pooling
<!-- bite: b339fbed-e3d5-4790-bd8c-4fb021a7a073 -->

`AddDbContext` is **scoped** — one `DbContext` per request → [[backend/frameworks/csharp/01-aspnet-core-and-the-pipeline|note 01]]. The underlying *connections* are pooled by ADO.NET regardless.

**`AddDbContextPool` also pools the contexts themselves**, which helps under high load — with the caveat that any state you put on your `DbContext` subclass survives into the next request.

**A `DbContext` is not thread-safe.** Using one across parallel tasks throws, and that's the framework protecting you.

## Related
<!-- bite: 320795d5-9ebc-4f04-a170-ac3568d1c354 -->
- [[backend/frameworks/csharp/04-testing-and-production|testing and production]]
- [[databases/index|the databases course]] — what EF generates, and why it matters
- [[backend/04-data-and-persistence/index|data and persistence]] — ORMs in general

## About this lesson
<!-- bite: 347c987f-7af4-4c7c-b577-c5111ff7d026 -->

**Level:** Intermediate. **Covers:** EF Core, Dapper, and the three mistakes that account for most slow .NET endpoints.

*Source: [reference] — from the EF Core and Dapper documentation, Aug 2026.*
