# Data Access

> **[Intermediate]** · EF Core, Dapper, and the three mistakes that account for most slow .NET endpoints.

## EF Core

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

**`HasPrecision` on money is not optional.** Mapping a monetary column to a floating-point type is the [[foundations/programming-fundamentals/05-variables-and-types|float-money bug]] at the database layer. C#'s `decimal` and SQL `numeric` are the correct pair.

## The three mistakes

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

```bash
dotnet ef migrations add AddOrderStatusIndex
dotnet ef database update
dotnet ef migrations script --idempotent      # for production
```

**Always read the generated migration before applying it.** EF infers intent from a model diff, and a *rename* is frequently detected as **drop-and-create — which is data loss** → [[databases/13-practice-exercises|databases exercise 4]].

**In production, apply migrations deliberately** — a generated SQL script reviewed and run by your deploy pipeline, not `Database.Migrate()` on startup. Startup migration races between instances and gives you no rollback → [[devops/06-ci-cd/README|CI/CD]].

## Dapper

A micro-ORM: you write the SQL, it maps the results.

```csharp
var orders = await conn.QueryAsync<Order>(
    "SELECT id, total FROM orders WHERE status = @status LIMIT @take",
    new { status = "paid", take = 20 });
```

**No change tracking, no migrations, no LINQ translation** — and consequently no surprises about what SQL runs.

**When to prefer it:** complex reporting queries, hot read paths, anything where you want the SQL to be exactly what you wrote. **A very common architecture is both** — EF Core for writes and the domain model, Dapper for read queries.

**Parameters are non-negotiable in either.** `$"... WHERE id = {input}"` is SQL injection; the parameterised form is not → [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|input validation]].

## Transactions and concurrency

```csharp
await using var tx = await db.Database.BeginTransactionAsync(ct);
// ... several SaveChangesAsync calls ...
await tx.CommitAsync(ct);
```

`SaveChanges` is already atomic for a single call — an explicit transaction is for spanning several, or for setting an isolation level → [[databases/08-transactions-and-acid|transactions]].

**Optimistic concurrency** with a `[Timestamp]`/`rowversion` column: EF adds the original value to the `WHERE` clause, and if zero rows update it throws `DbUpdateConcurrencyException`. **Handle it** — retry, or surface a conflict to the user. Ignoring it is a silent lost update.

## Connection pooling

`AddDbContext` is **scoped** — one `DbContext` per request → [[backend/frameworks/csharp/01-aspnet-core-and-the-pipeline|note 01]]. The underlying *connections* are pooled by ADO.NET regardless.

**`AddDbContextPool` also pools the contexts themselves**, which helps under high load — with the caveat that any state you put on your `DbContext` subclass survives into the next request.

**A `DbContext` is not thread-safe.** Using one across parallel tasks throws, and that's the framework protecting you.

## Related
- [[backend/frameworks/csharp/04-testing-and-production|testing and production]]
- [[databases/README|the databases course]] — what EF generates, and why it matters
- [[backend/04-data-and-persistence/README|data and persistence]] — ORMs in general

*Source: [reference] — from the EF Core and Dapper documentation, Aug 2026.*
