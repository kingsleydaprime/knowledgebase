# Databases

## What a database is

**A database is a program that stores information and lets you find it, change it and keep it safe, even when many people use it at once.**

Your bank balance, your messages, the products in an online shop and the posts on social media all live in databases. You could store information in ordinary files, but files fall apart quickly: two people saving at the same moment can overwrite each other, a power cut halfway through a save can leave the file broken, and finding one customer among a million means reading the whole file. A database solves all of these problems for you.

Most databases are **relational**: they store information in tables, like spreadsheets, with rows and columns. You talk to them in a language called **SQL**, for example `SELECT name FROM customers WHERE city = 'Lagos'`.

This course explains **how a database works inside**: how it stores data on disk, how it finds rows quickly, how it stops two people's changes from clashing, and how it survives a crash.

## What you'll be able to do

By the end you will be able to:
- explain why databases exist and what they promise you;
- understand why some queries are fast and others are slow, and make slow ones fast with **indexes**;
- read a query plan, the database's explanation of how it will run your query;
- explain what happens when two people change the same data at the same time, and avoid the bugs that causes;
- explain how a database survives a crash without losing your data;
- change a live database's structure without taking the app down.

## Where to start

**If you've never used a database,** learn to write basic SQL first. The [[databases/sql-reference|SQL reference]] covers it, and [[backend/04-data-and-persistence/index|Backend: data and persistence]] shows how an app talks to a database. Then come back to this course.

**If you can already write SQL,** read the course in order. Notes 02–05 are about how data is stored, 06–07 about how queries run, 08–10 about safety when many people use the database at once, and 11–12 about running a database for real.

1. [[databases/01-what-a-database-is|What a Database Is]]: why not just use files, the promises a database makes (called ACID), and the different kinds of database.
2. [[databases/02-the-relational-model|The Relational Model]]: the idea behind tables, and why you describe *what* you want instead of *how* to get it.
3. [[databases/03-storage-and-page-layout|Storage and Page Layout]]: how rows are actually laid out on disk, in fixed-size blocks called pages. It has a hands-on lab you can do without installing a database; do it before moving on.
4. [[databases/04-b-trees-and-indexes/index|B-Trees and Indexes]]: how an index lets the database find one row among millions in a few steps, like the index at the back of a book. And when an index makes things worse.
5. [[databases/05-lsm-trees|LSM Trees]]: a different way of storing data that's built for writing very fast.
6. [[databases/06-the-query-pipeline|The Query Pipeline]]: the steps your SQL goes through, from text to results.
7. [[databases/07-join-algorithms-and-the-optimiser/index|Join Algorithms and the Optimiser]]: how the database combines tables, and how it guesses the fastest way to run your query (and how those guesses go wrong).
8. [[databases/08-transactions-and-acid/index|Transactions and ACID]]: grouping changes so they all happen or none do, and what can go wrong when two people change data at once.
9. [[databases/09-mvcc-and-concurrency-control/index|MVCC and Concurrency Control]]: how a database lets people read and write at the same time without blocking each other, and the clean-up work that causes.
10. [[databases/10-durability-and-recovery|Durability and Recovery]]: how a database makes sure saved data survives a crash or power cut.
11. [[databases/11-replication-and-scaling|Replication and Scaling]]: keeping copies of a database on several machines, and splitting data when one machine isn't enough.
12. [[databases/12-operating-a-database|Operating a Database]]: changing a live database safely, the most common performance mistake, monitoring, and choosing a database.

## For quick lookup

These reference files are for looking things up, not reading through.

- [[databases/sql-reference|SQL reference]]: how to write queries: joins, window functions, subqueries.
- [[databases/database-design-reference|Database design reference]]: designing tables: keys, normalisation (organising data to avoid repetition), and common patterns.
- [[databases/mysql-reference|MySQL reference]]: MySQL-specific setup and administration.
- [[databases/nosql-reference|NoSQL reference]]: databases that don't use tables: MongoDB, Redis, Cassandra, Neo4j and Elasticsearch.
- [[databases/migrations-reference|Migrations reference]]: changing a database's structure safely over time.

## Practice

- [[databases/13-practice-exercises|Practice Exercises]]: fourteen exercises against a real database, such as making a query thousands of times faster with one index, causing a deadlock on purpose, and killing the server mid-save to see what survives.
- [[databases/14-practice-exercises-solutions|Solutions]]: worked answers. Try first.
- [[databases/projects|Projects]]: hands-on tasks, from easy (🟢) to hard (🔴), each with a clear "done when".
- [[build-your-own-shit/06-your-own-database|Build your own database]]: write a small database yourself, step by step.

## Key ideas to remember

1. **Everything is stored in pages,** fixed-size blocks the database reads and writes as a unit. → [[databases/03-storage-and-page-layout|03]]
2. **An index on several columns only helps if your query uses the first one.** An index on `(a, b, c)` can't help `WHERE b = 2`. → [[databases/04-b-trees-and-indexes/index|04]]
3. **When a query is slow, compare the database's guessed row counts with the real ones** (`EXPLAIN ANALYZE`). The first big mismatch usually points to the problem. → [[databases/07-join-algorithms-and-the-optimiser/index|07]]
4. **Your database probably protects you less than you think by default.** Two people updating the same row can quietly lose one person's change. → [[databases/08-transactions-and-acid/index|08]]
5. **Long-running transactions cause most slowdowns** in databases like Postgres. → [[databases/09-mvcc-and-concurrency-control/index|09]]
6. **A copy of your database is not a backup.** If someone deletes a table, the copy deletes it too, a moment later. → [[databases/10-durability-and-recovery|10]]
7. **Make one machine faster before splitting across many.** Indexes, caching and a bigger machine are enough for most apps. → [[databases/11-replication-and-scaling|11]]
8. **The most common database mistake in apps is running one query per item in a loop** (called "N+1") instead of one query for all of them. → [[databases/12-operating-a-database|12]]

## Related

- [[backend/index|Backend]]: where apps use databases.
- [[data-engineering/index|Data Engineering]]: moving large amounts of data between databases for analysis.
- [[architecture/04-distributed-systems/index|Distributed Systems]]: what changes when data is spread across many machines.
- [[databases/interview/index|Databases interview prep]]: what interviewers ask about all this.

---

## About this course

- **Size:** the course is 14 notes, about 20,500 words, written in August 2026. The five reference files are older and much longer (about 11,600 lines).
- **Where it came from:** the standard books (*Database Internals*, *Designing Data-Intensive Applications*, *Architecture of a Database System*) and the Postgres and MySQL documentation, not from running a large database in production. It's strongest on how things work, and thinner on judgement, such as how bad a given slowdown is in practice.
- **Teaching quality:** note 03 has been revised to the full lesson standard (worked example, lab, checks). The other notes haven't yet.
- **Not covered yet:** a beginner's "your first SQL queries" lesson (the SQL reference covers it for now), data warehouses, stream processing, vector databases, and time-series databases.
- **Further reading:** *Database Internals* (Petrov), *Designing Data-Intensive Applications* (Kleppmann), *The Art of PostgreSQL*.
