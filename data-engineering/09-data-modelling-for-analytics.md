# Data Modelling for Analytics

**[Intermediate]** — how to structure warehouse tables so analysts can answer questions, and why it's the opposite of database normalisation.

## The kid version first

You *could* store analytical data the way an app database does — dozens of tightly-linked tables, no redundancy, every fact in exactly one place. **For analytics, that's the wrong shape.** Analysts would need ten-table joins to answer "revenue by product category by month," and the queries would be slow and unwriteable.

Analytical modelling deliberately does the opposite: **organise data around the *questions* people ask, accept some redundancy, and make the common query a simple two- or three-table join.** The classic shape is the **star schema**.

## Why analytical modelling inverts OLTP modelling

[[databases/02-the-relational-model|Operational databases normalise]] — eliminate redundancy so that every fact lives in one place and updates can't create inconsistencies. That's right for OLTP: many small writes, and correctness under concurrent updates.

**Analytics has the opposite profile:** few bulk writes, enormous reads, and no concurrent-update correctness worry (the data is a snapshot). So the priorities flip:

| | OLTP (normalise) | OLAP (dimensional) |
|---|---|---|
| Goal | No redundancy, safe writes | Fast, simple reads |
| Joins | Many, that's fine | **Few** — analysts write these by hand |
| Redundancy | Avoided | **Accepted** for query simplicity |
| Optimise for | Write integrity | Read speed and understandability |

**Denormalisation is a feature here, not a smell.** Storing the product category on every sale row (redundant) means "revenue by category" needs no join to a products table. Storage is cheap; analyst time and query speed are not.

## The star schema — facts and dimensions

Dimensional modelling (Ralph Kimball) splits every table into one of two kinds:

**Fact tables** — the *measurements*, the things you count and sum. Long and narrow: one row per event, mostly numbers plus foreign keys.

**Dimension tables** — the *context*, the things you filter and group by. Wide and short: one row per entity, lots of descriptive attributes.

```
                    dim_date
                       │
   dim_customer ── fact_sales ── dim_product      ← the "star"
                       │
                    dim_store

   fact_sales:  date_id, customer_id, product_id, store_id, quantity, amount
                └──────── foreign keys ────────┘  └── the MEASURES ──┘
   dim_product: product_id, name, category, brand, colour, ...  (the CONTEXT)
```

**The query becomes obvious:** "revenue by category by month" = join `fact_sales` to `dim_product` and `dim_date`, group by category and month, sum amount. **Two joins, both from the fact to a dimension, never dimension-to-dimension.** That regular shape is the whole point — every analytical question is the same pattern.

- **Facts** answer *"how much / how many"* — measures you aggregate
- **Dimensions** answer *"by what"* — the `GROUP BY` and `WHERE` attributes
- **Grain** — the single most important design decision: *what does one fact row represent?* "One row per order line" vs "one row per order" vs "one daily summary." Get the grain explicit and consistent, or the numbers become meaningless

**A snowflake schema** normalises the dimensions (category split into its own table). Usually *not* worth it — it re-introduces joins to save storage you don't care about. **Prefer the flatter star.**

## Slowly Changing Dimensions — the classic subtlety

A customer moves from London to Manchester. Their old orders happened while they lived in London. **If you just overwrite the address, last year's "revenue by city" retroactively changes** — London's history silently moves to Manchester. That's usually wrong.

**Slowly Changing Dimensions (SCD)** handle attribute changes over time:

- **Type 1** — overwrite. Simple, and **destroys history.** Fine for fixing typos, wrong for anything you report on over time
- **Type 2** — **add a new row** with valid-from/valid-to dates and a "current" flag. History is preserved; old orders still link to the London version. **The important one** — it's how you keep historical reports correct
- **Type 3** — keep a "previous value" column. Limited, rarely used

**SCD Type 2 is the canonical "did you actually think about history" question**, and getting it wrong is how reports quietly rewrite the past.

## The modern picture

Kimball's dimensional modelling is from the 1990s, and two things have shifted it:

**Cheap storage and compute loosened the rules.** With columnar warehouses, some teams build **One Big Table** — fully denormalised, everything on one wide row — because the warehouse handles it and analysts find it even simpler than a star. Valid for many cases; it trades storage and some maintainability for zero joins.

**dbt operationalised it.** The staging → intermediate → marts layering ([[data-engineering/07-transformation-and-dbt|dbt]]) is where dimensional models get *built* now — the marts layer is your facts and dimensions, produced by tested SQL.

**But the core ideas endure:** facts vs dimensions, explicit grain, and handling history (SCD2) are as relevant as ever, because they're about *how humans ask questions of data*, which hasn't changed.

## Key insight

**Analytical modelling inverts database normalisation on purpose: it accepts redundancy to make the common query a simple fact-to-dimension join.** The star schema works because it makes *every* analytical question the same shape — measures in the fact, context in the dimensions, joined by keys. The two ideas that separate someone who's done this from someone who hasn't are **explicit grain** (what one fact row means) and **SCD Type 2** (preserving history so last year's report doesn't silently change), and both survive whatever the tooling does.

## Related
- [[databases/02-the-relational-model|the relational model]] — normalisation, the thing this deliberately inverts
- [[data-engineering/07-transformation-and-dbt|transformation and dbt]] — where models get built
- [[data-engineering/02-warehouses-lakes-and-lakehouses|warehouses]] — where they live, and why columnar makes wide tables cheap
- [[databases/database-design-reference|database design reference]]

*Source: [reference] — Aug 2026.*
