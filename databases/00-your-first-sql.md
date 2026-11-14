# Your First SQL Queries

**[Beginner]** · How to put information into a database and ask it questions, using SQL. This comes before the rest of the course: the later notes explain how a database works inside, and this one teaches you to use one.

## Before you start

You need:
- to be able to open a terminal and run a command;
- one way to run SQL. Either install the `sqlite3` program (one command, shown in section 2), or use Python 3.12 or newer, which has one built in.

You don't need to know any programming.

**After this lesson you will be able to:**
1. create a table and fill it with rows;
2. ask questions that pick, filter and sort rows;
3. count and add up values, for everything or for each group;
4. combine two tables to answer one question;
5. change and delete rows without destroying the wrong ones.

**How to study it:** type every query yourself rather than copying and pasting. Before each result, guess what it will show, then check.

## The kid version

Imagine a shop owner who keeps two exercise books. One lists every customer: their name and city. The other lists every sale: who bought what, how much it cost and when. Each book is a **table**: every line is one customer or one sale, and every column is one piece of information about it.

Now imagine a very fast assistant who has read both books. You ask questions like "Who are my customers in Lagos?" or "How much did Ada spend in total?", and the assistant answers instantly, even if the books have a million lines. **SQL is the language you ask the assistant questions in.** You say *what* you want; the assistant works out *how* to find it.

**Where the picture stops working:** a real assistant would understand a sloppy question. A database won't. SQL has strict grammar, and a question that's even slightly wrong either fails with an error or, worse, quietly answers a different question from the one you meant.

## 1. Why this exists

A shop owner with a spreadsheet can scroll to find a customer. With 200,000 sales that stops working. "How much did customers in Lagos spend last month?" means filtering, matching each sale to its customer, and adding up, all by hand. Worse, the spreadsheet can't stop two staff from saving over each other's changes.

A database stores the same information safely, and SQL lets you ask that whole question in one sentence. The same SQL works, with small differences, in SQLite, PostgreSQL, MySQL and most other databases. Learn it once and you can use it almost everywhere.

## Terms used in this lesson

1. **Database**: This is a program that stores information and lets you add, find, change and delete it safely. In this lesson the whole database is one file, `shop.db`.
2. **Table**: This is a set of information about one kind of thing, laid out in rows and columns like a spreadsheet. Our database has two tables: `customers` and `orders`.
3. **Row**: This is also known as a **record**. This is one entry in a table: one customer, or one order.
4. **Column**: This is one piece of information that every row has, such as `name` or `city`. Each column has a type, such as text (`TEXT`) or whole number (`INTEGER`).
5. **Primary key**: This is a column whose value is different for every row, so it picks out exactly one row. Our tables use a column called `id` for this. Two customers can share a name, but never an `id`.
6. **Foreign key**: This is a column in one table that holds the primary key of a row in another table. In `orders`, the column `customer_id` holds the `id` of the customer who placed the order. That's how an order "points at" its customer.
7. **SQL**: The letters stand for structured query language. It is the language used to create tables, add information and ask questions of a database. People say it as "S-Q-L" or "sequel".
8. **Query**: This is one question or instruction written in SQL, such as "give me every customer in Lagos". It ends with a semicolon (`;`).
9. **Clause**: This is one part of a query, starting with a keyword. In `SELECT name FROM customers WHERE city = 'Lagos'`, there are three clauses: `SELECT name`, `FROM customers` and `WHERE city = 'Lagos'`.
10. **Result**: This is the table of rows a query gives back. It isn't stored anywhere; it's just the answer.

## 2. Getting set up

**Install `sqlite3`.** SQLite is a small database that keeps everything in one file and needs no server.

```sh
sudo dnf install sqlite        # Fedora
sudo apt install sqlite3       # Ubuntu or Debian
brew install sqlite            # macOS
```

On Windows, download the "command-line tools" bundle from [sqlite.org/download.html](https://sqlite.org/download.html).

**No install?** If you have Python 3.12 or newer, use `python3 -m sqlite3` wherever this lesson says `sqlite3`. Everything works the same, except results print as plain rows like `('Ada Okafor', 'Lagos')` instead of neat tables.

**Create the shop.** Make a folder for this lesson, and save the following as `shop.sql` inside it. It creates the two tables and fills them in. You'll understand every line by the end of section 3.

```sql
CREATE TABLE customers (
  id   INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  city TEXT
);
INSERT INTO customers (id, name, city) VALUES
  (1, 'Ada Okafor',   'Lagos'),
  (2, 'Tunde Bakare', 'Ibadan'),
  (3, 'Chioma Eze',   'Lagos'),
  (4, 'Musa Bello',   'Kano'),
  (5, 'Ngozi Obi',    'Enugu');
CREATE TABLE orders (
  id          INTEGER PRIMARY KEY,
  customer_id INTEGER REFERENCES customers(id),
  item        TEXT NOT NULL,
  amount      INTEGER NOT NULL,
  ordered_on  TEXT NOT NULL
);
INSERT INTO orders (id, customer_id, item, amount, ordered_on) VALUES
  (1, 1, 'Rice (50kg)',      85000, '2026-10-02'),
  (2, 1, 'Groundnut oil',    12000, '2026-10-15'),
  (3, 2, 'Rice (50kg)',      85000, '2026-10-03'),
  (4, 3, 'Indomie (carton)',  9500, '2026-10-04'),
  (5, 3, 'Rice (50kg)',      85000, '2026-10-20'),
  (6, 3, 'Sugar',             4500, '2026-11-01'),
  (7, 4, 'Groundnut oil',    12000, '2026-11-02'),
  (8, 1, 'Sugar',             4500, '2026-11-05');
```

Then, in a terminal in that folder:

```sh
sqlite3 shop.db < shop.sql     # build the database from the file (once)
sqlite3 shop.db                # open it and start asking questions
```

Inside `sqlite3`, run these two lines once so results print as neat tables with column names:

```
.mode table
.headers on
```

Type `.quit` to leave. If you ever make a mess, delete `shop.db` and run the first command again to start fresh.

## 3. Making a table and filling it

Look back at `shop.sql`. It uses two kinds of statement.

**`CREATE TABLE` makes an empty table** and says what columns it has:

```sql
CREATE TABLE customers (
  id   INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  city TEXT
);
```

Read it as: "make a table called `customers`. Every row has an `id`, a whole number that's different for every row; a `name`, which is text and must always be filled in (`NOT NULL`); and a `city`, which is text and may be left empty."

**`INSERT INTO` adds rows.** You list the columns, then the values in the same order:

```sql
INSERT INTO customers (id, name, city) VALUES
  (1, 'Ada Okafor', 'Lagos');
```

Text goes in **single quotes** (`'Lagos'`). Numbers don't.

Notice two choices in the `orders` table:
- **`amount` is a whole number of naira** (`85000`), never a decimal. Computers store decimals slightly inaccurately, which is fine for measurements and wrong for money.
- **`customer_id REFERENCES customers(id)`** makes `customer_id` a foreign key. Each order stores *which* customer placed it, instead of copying their name and city into every order. If Ada moves, you change her city in one place.

## 4. Asking questions: `SELECT`

Every question starts with `SELECT` (which columns you want) and `FROM` (which table).

```sql
SELECT * FROM customers;
```

The `*` means "every column".

```
+----+--------------+--------+
| id | name         | city   |
+----+--------------+--------+
| 1  | Ada Okafor   | Lagos  |
| 2  | Tunde Bakare | Ibadan |
| 3  | Chioma Eze   | Lagos  |
| 4  | Musa Bello   | Kano   |
| 5  | Ngozi Obi    | Enugu  |
+----+--------------+--------+
```

To get only some columns, name them:

```sql
SELECT name, city FROM customers;
```

### Picking rows: `WHERE`

`WHERE` keeps only the rows that match a condition.

```sql
SELECT name, city FROM customers WHERE city = 'Lagos';
```

```
+------------+-------+
| name       | city  |
+------------+-------+
| Ada Okafor | Lagos |
| Chioma Eze | Lagos |
+------------+-------+
```

In SQL a single `=` *compares*; there's no `==`. The other comparisons are `!=` (not equal), `<`, `>`, `<=` and `>=`. Combine conditions with `AND` and `OR`:

```sql
SELECT item, amount FROM orders WHERE amount > 10000 AND ordered_on >= '2026-10-10';
```

Dates written as `'YYYY-MM-DD'` sort correctly as text, which is why `>=` works on them.

### Sorting and limiting: `ORDER BY` and `LIMIT`

**Predict first:** which orders cost more than ₦10,000, most expensive first?

```sql
SELECT item, amount FROM orders WHERE amount > 10000 ORDER BY amount DESC;
```

```
+---------------+--------+
| item          | amount |
+---------------+--------+
| Rice (50kg)   | 85000  |
| Rice (50kg)   | 85000  |
| Rice (50kg)   | 85000  |
| Groundnut oil | 12000  |
| Groundnut oil | 12000  |
+---------------+--------+
```

`ORDER BY amount` sorts smallest first; `DESC` (descending) flips it. `LIMIT` keeps only the first few rows of the result, so here are the three most recent orders:

```sql
SELECT item, ordered_on FROM orders ORDER BY ordered_on DESC LIMIT 3;
```

```
+---------------+------------+
| item          | ordered_on |
+---------------+------------+
| Sugar         | 2026-11-05 |
| Groundnut oil | 2026-11-02 |
| Sugar         | 2026-11-01 |
+---------------+------------+
```

## 5. Counting and adding up

Some questions want one number rather than a list of rows. These are **aggregate functions**: they squash many rows into one value.

```sql
SELECT COUNT(*) FROM orders;      -- how many orders?   → 8
SELECT SUM(amount) FROM orders;   -- total takings?     → 297500
```

The others you'll use most are `AVG` (average), `MIN` (smallest) and `MAX` (largest). Anything after `--` on a line is a comment, which the database ignores.

### One answer per group: `GROUP BY`

"How much did *each* customer spend?" needs one total per customer. `GROUP BY` puts the rows into piles, one pile per value, and runs the aggregate on each pile:

```sql
SELECT customer_id, COUNT(*) AS orders, SUM(amount) AS total
FROM orders
GROUP BY customer_id;
```

```
+-------------+--------+--------+
| customer_id | orders | total  |
+-------------+--------+--------+
| 1           | 3      | 101500 |
| 2           | 1      | 85000  |
| 3           | 3      | 99000  |
| 4           | 1      | 12000  |
+-------------+--------+--------+
```

`AS` gives a result column a name. A query can run across several lines; it ends at the semicolon.

**Filtering groups: `HAVING`.** `WHERE` filters rows *before* they're grouped. To filter the groups themselves, for example "customers who spent over ₦50,000", use `HAVING`, which runs *after* grouping:

```sql
SELECT customer_id, SUM(amount) AS total
FROM orders
GROUP BY customer_id
HAVING SUM(amount) > 50000;
```

That returns customers 1, 2 and 3.

## 6. Combining two tables: `JOIN`

The result above says "customer 1", but you want names, and names live in the other table. **A `JOIN` lines up rows from two tables that belong together.** You say how they match with `ON`:

```sql
SELECT customers.name, orders.item, orders.amount
FROM orders
JOIN customers ON orders.customer_id = customers.id;
```

Read it as: "for every order, find the customer whose `id` equals the order's `customer_id`, and put them side by side." When two tables both have a column called `id`, you write `table.column` so the database knows which you mean.

```
+--------------+------------------+--------+
| name         | item             | amount |
+--------------+------------------+--------+
| Ada Okafor   | Rice (50kg)      | 85000  |
| Ada Okafor   | Groundnut oil    | 12000  |
| Tunde Bakare | Rice (50kg)      | 85000  |
| Chioma Eze   | Indomie (carton) | 9500   |
| Chioma Eze   | Rice (50kg)      | 85000  |
| Chioma Eze   | Sugar            | 4500   |
| Musa Bello   | Groundnut oil    | 12000  |
| Ada Okafor   | Sugar            | 4500   |
+--------------+------------------+--------+
```

**Look for who's missing.** Ngozi Obi is a customer, but she isn't in the result. A plain `JOIN` only keeps rows that found a match, and she has no orders. Section 8 shows how to keep her.

## 7. Changing and deleting rows

**`UPDATE` changes rows that already exist.** Tunde moves to Abuja:

```sql
UPDATE customers SET city = 'Abuja' WHERE id = 2;
```

**`DELETE` removes rows.** Order 8 was a mistake:

```sql
DELETE FROM orders WHERE id = 8;
```

**The `WHERE` is doing all the safety work here.** Without it, `UPDATE customers SET city = 'Abuja';` moves *every* customer to Abuja, and `DELETE FROM orders;` deletes every order. The database won't ask "are you sure?". Before any `UPDATE` or `DELETE`, run a `SELECT` with the same `WHERE` and check it picks exactly the rows you mean.

## Worked example: who is the best customer?

Build the query one step at a time, running it after each step.

**Step 1: what's each customer's total?** Join orders to customers so you have names, then group by customer:

```sql
SELECT customers.name, SUM(orders.amount) AS total
FROM orders
JOIN customers ON orders.customer_id = customers.id
GROUP BY customers.id;
```

We group by `customers.id`, not by `name`, because two different customers could share a name.

**Step 2: biggest first.** Add `ORDER BY total DESC`:

```
+--------------+--------+
| name         | total  |
+--------------+--------+
| Ada Okafor   | 101500 |
| Chioma Eze   | 99000  |
| Tunde Bakare | 85000  |
| Musa Bello   | 12000  |
+--------------+--------+
```

**Step 3: just the top one.** Add `LIMIT 1`:

```sql
SELECT customers.name, SUM(orders.amount) AS total
FROM orders
JOIN customers ON orders.customer_id = customers.id
GROUP BY customers.id
ORDER BY total DESC
LIMIT 1;
```

```
+------------+--------+
| name       | total  |
+------------+--------+
| Ada Okafor | 101500 |
+------------+--------+
```

That's the shape of most real queries: **join** to get everything you need side by side, **filter** the rows, **group** and add up, **sort**, and **limit**. The clauses always go in this order:

```
SELECT … FROM … JOIN … ON … WHERE … GROUP BY … HAVING … ORDER BY … LIMIT …;
```

## Common pitfalls

1. **`UPDATE` or `DELETE` without `WHERE`.** It changes every row. Always `SELECT` with the same `WHERE` first.
2. **Double quotes around text.** Write `'Lagos'`, not `"Lagos"`. In standard SQL, double quotes mean a column name, so `WHERE city = "Lagos"` can fail or quietly compare against a column instead.
3. **Clauses in the wrong order.** `WHERE` must come before `GROUP BY`, and `ORDER BY` near the end. The order isn't optional.
4. **Using `WHERE` to filter a total.** `WHERE SUM(amount) > 50000` is an error, because `WHERE` runs before the totals exist. Use `HAVING`.
5. **Forgetting the `ON` in a join.** Without it you get every customer paired with every order: 5 × 8 = 40 rows of nonsense.
6. **Checking for an empty value with `=`.** An empty value is called `NULL`, and `city = NULL` is never true, not even for an empty city. Write `city IS NULL`.
7. **Expecting a plain `JOIN` to keep unmatched rows.** It drops them, as Ngozi showed.

## Check your understanding

Try each one in `sqlite3` before opening the answer. If you've run section 7, delete `shop.db` and rebuild it first, so your numbers match.

**1. What does `SELECT name FROM customers WHERE city = 'Kano';` return?**

<details><summary>Answer</summary>

One row: `Musa Bello`. He's the only customer whose city is exactly `Kano`.

</details>

**2. Write a query for the total amount spent on `'Rice (50kg)'`.**

<details><summary>Answer</summary>

`SELECT SUM(amount) FROM orders WHERE item = 'Rice (50kg)';` gives `255000`. `WHERE` keeps the three rice orders, then `SUM` adds them up: 3 × 85,000.

</details>

**3. Why is `UPDATE customers SET city = 'Abuja';` dangerous?**

<details><summary>Answer</summary>

It has no `WHERE`, so it changes every row: all five customers now live in Abuja. The database doesn't warn you. Run a `SELECT` with your intended `WHERE` first, then put the same `WHERE` on the `UPDATE`.

</details>

**4. What's the difference between `WHERE` and `HAVING`?**

<details><summary>Answer</summary>

`WHERE` filters individual rows before they're grouped. `HAVING` filters whole groups after `GROUP BY` has made them, so it can use totals like `SUM(amount)`. "Orders over ₦10,000" is a `WHERE`; "customers whose orders add up to over ₦50,000" is a `HAVING`.

</details>

**5. Ngozi Obi doesn't appear when you join `orders` to `customers`. Why?**

<details><summary>Answer</summary>

A plain `JOIN` only keeps rows that found a match in both tables. Ngozi has no orders, so no order row matches her. A `LEFT JOIN` keeps every row from the first table even without a match (section 8).

</details>

**6. Why does `orders` store `customer_id` instead of the customer's name and city?**

<details><summary>Answer</summary>

So each fact is stored once. If Ada moves, you update one row in `customers`, and every order still points at the right person. Copying her city into every order would mean updating every one of them, and missing one leaves the data contradicting itself. Names also aren't unique, but an `id` is.

</details>

## Practice: answer the shop owner's questions

Rebuild a fresh `shop.db`, then write one query for each question.

1. Which customers are **not** in Lagos?
2. Which orders were placed in November 2026 or later?
3. How many times was each item ordered, most popular first? If two items tie, list them alphabetically.
4. How much has each **city** spent in total, biggest first?
5. Which customers (by name) have spent more than ₦50,000?

**Done when:** every query runs without an error and matches the expected results below. Then change one thing in the data, such as adding an order for Ngozi with an `INSERT`, and predict how each answer changes before you rerun it.

<details><summary>Expected results</summary>

1. `SELECT name, city FROM customers WHERE city != 'Lagos';` gives Tunde Bakare (Ibadan), Musa Bello (Kano) and Ngozi Obi (Enugu).
2. `SELECT item, amount, ordered_on FROM orders WHERE ordered_on >= '2026-11-01';` gives Sugar (2026-11-01), Groundnut oil (2026-11-02) and Sugar (2026-11-05).
3. `SELECT item, COUNT(*) AS times_ordered FROM orders GROUP BY item ORDER BY times_ordered DESC, item;` gives Rice (50kg) 3, Groundnut oil 2, Sugar 2, Indomie (carton) 1. The `, item` is the tie-breaker: without it, SQL doesn't promise which of two equal rows comes first.
4. `SELECT customers.city, SUM(orders.amount) AS total FROM orders JOIN customers ON orders.customer_id = customers.id GROUP BY customers.city ORDER BY total DESC;` gives Lagos 200500, Ibadan 85000, Kano 12000. Enugu is missing for the same reason Ngozi was.
5. `SELECT customers.name, SUM(orders.amount) AS total FROM orders JOIN customers ON orders.customer_id = customers.id GROUP BY customers.id HAVING SUM(orders.amount) > 50000;` gives Ada Okafor 101500, Tunde Bakare 85000 and Chioma Eze 99000.

</details>

## 8. Going further

- **Keeping unmatched rows: `LEFT JOIN`.** It keeps every row from the first table, filling the missing side with empty values. Counting orders per customer, Ngozi included:

  ```sql
  SELECT customers.name, COUNT(orders.id) AS orders
  FROM customers
  LEFT JOIN orders ON orders.customer_id = customers.id
  GROUP BY customers.id;
  ```

  Ngozi now appears with `0`. `COUNT(orders.id)` counts only rows where an order exists, which is why her count is 0 rather than 1.
- **Other databases.** PostgreSQL and MySQL use the same SQL for everything in this lesson. They differ in setup (they run as a server you connect to) and in more advanced features.
- **More SQL:** subqueries, window functions and the rest are in the [[databases/sql-reference|SQL reference]].

## Before moving on

You're ready for the next note when you can, without looking:
- create a table and insert rows into it;
- write a query that joins two tables, filters, groups, sorts and limits;
- explain why an `UPDATE` without `WHERE` is dangerous, and what to do first.

**Recap:** a database holds tables of rows and columns. `SELECT … FROM` asks, `WHERE` filters rows, `ORDER BY` sorts, `LIMIT` trims, `COUNT` and `SUM` total things up, `GROUP BY` totals per group, `HAVING` filters groups, and `JOIN … ON` lines up related rows from two tables. `INSERT`, `UPDATE` and `DELETE` change data, and the last two always need a `WHERE`.

**Next:** [[databases/01-what-a-database-is|What a Database Is]]. Now that you've used a database, it explains what the database is doing for you behind each of these queries, and why you couldn't get the same from plain files.

## Related

- [[databases/sql-reference|SQL reference]]: every part of SQL, for looking things up.
- [[databases/database-design-reference|Database design reference]]: deciding what tables and columns to make.
- [[backend/04-data-and-persistence/index|Backend: data and persistence]]: using a database from an app's code.
