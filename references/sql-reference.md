# SQL — Comprehensive Reference Guide

> A deep reference covering SQL from first principles to senior-level concepts.
> Covers every clause, join type, aggregate, window function, subquery pattern,
> set operation, transaction, and advanced technique with real examples throughout.
> Written with PostgreSQL syntax — notes where behaviour differs across databases.

---

## Table of Contents

1. [What SQL Is and How It Thinks](#1-what-sql-is-and-how-it-thinks)
2. [Data Definition Language (DDL)](#2-data-definition-language-ddl)
3. [Data Manipulation Language (DML)](#3-data-manipulation-language-dml)
4. [The SELECT Statement — Complete Reference](#4-the-select-statement--complete-reference)
5. [Filtering — WHERE and HAVING](#5-filtering--where-and-having)
6. [Sorting — ORDER BY](#6-sorting--order-by)
7. [Limiting Results — LIMIT and OFFSET](#7-limiting-results--limit-and-offset)
8. [Joins — The Complete Guide](#8-joins--the-complete-guide)
9. [Aggregation and GROUP BY](#9-aggregation-and-group-by)
10. [Subqueries](#10-subqueries)
11. [Common Table Expressions (CTEs)](#11-common-table-expressions-ctes)
12. [Window Functions](#12-window-functions)
13. [Set Operations — UNION, INTERSECT, EXCEPT](#13-set-operations--union-intersect-except)
14. [String Functions and Operations](#14-string-functions-and-operations)
15. [Numeric Functions](#15-numeric-functions)
16. [Date and Time Functions](#16-date-and-time-functions)
17. [Conditional Logic — CASE, COALESCE, NULLIF](#17-conditional-logic--case-coalesce-nullif)
18. [NULL — The Complete Guide](#18-null--the-complete-guide)
19. [Transactions and Concurrency](#19-transactions-and-concurrency)
20. [Views](#20-views)
21. [Indexes in SQL](#21-indexes-in-sql)
22. [Stored Procedures and Functions](#22-stored-procedures-and-functions)
23. [Triggers](#23-triggers)
24. [JSON in SQL](#24-json-in-sql)
25. [Full-Text Search](#25-full-text-search)
26. [Query Optimisation — Reading and Thinking](#26-query-optimisation--reading-and-thinking)
27. [Advanced Patterns — Senior Level](#27-advanced-patterns--senior-level)
28. [Common Mistakes and How to Avoid Them](#28-common-mistakes-and-how-to-avoid-them)
29. [Practice — E-Commerce Schema](#29-practice--e-commerce-schema)
30. [Natural Joins](#30-natural-joins)
31. [Multicolumn Subqueries](#31-multicolumn-subqueries)
32. [Subqueries As Expression Generators](#32-subqueries-as-expression-generators)
33. [Data Fabrication with Subqueries](#33-data-fabrication-with-subqueries)
34. [Metadata and information_schema](#34-metadata-and-information_schema)
35. [Dynamic SQL Generation](#35-dynamic-sql-generation)
36. [Storage Engines and Locking Granularities](#36-storage-engines-and-locking-granularities)
37. [Multicolumn Grouping and Rollups — Deep Reference](#37-multicolumn-grouping-and-rollups--deep-reference)

---

## 1. What SQL Is and How It Thinks

### 1.1 SQL is Declarative

SQL is a **declarative** language — you describe *what* you want, not *how* to get it. You say "give me all users where status is active, sorted by name" and the database figures out the most efficient way to execute that.

This is fundamentally different from procedural programming. There are no loops, no step-by-step instructions. The database's query planner decides the execution strategy — which indexes to use, which tables to scan, in what order to join things.

Understanding this mental shift is key. You think about sets and transformations, not algorithms.

### 1.2 SQL Operates on Sets

Every SQL query operates on **sets of rows**. A table is a set. A query result is a set. Joins combine sets. Aggregations collapse sets. Window functions annotate sets without collapsing them.

This means order is not guaranteed unless you explicitly specify `ORDER BY`. A table has no inherent row order. Two queries that return the same rows in different orders are both correct unless you specify otherwise.

### 1.3 The Logical Order of Query Execution

The order you *write* a SELECT differs from the order the database *executes* it. Understanding execution order explains why you can't use a column alias from SELECT in a WHERE clause, but you can in ORDER BY.

```sql
-- Written order:
SELECT ...
FROM ...
JOIN ...
WHERE ...
GROUP BY ...
HAVING ...
ORDER BY ...
LIMIT ...

-- Execution order:
-- 1. FROM       — identify the source tables
-- 2. JOIN       — combine tables
-- 3. WHERE      — filter rows (before grouping)
-- 4. GROUP BY   — group rows
-- 5. HAVING     — filter groups (after grouping)
-- 6. SELECT     — compute output columns and aliases
-- 7. DISTINCT   — remove duplicates
-- 8. ORDER BY   — sort (aliases from SELECT are now available)
-- 9. LIMIT/OFFSET — trim the result
```

This explains:
```sql
-- This FAILS: WHERE runs before SELECT, so 'total' alias doesn't exist yet
SELECT price * quantity AS total FROM orders WHERE total > 100;

-- This WORKS: use the expression directly in WHERE
SELECT price * quantity AS total FROM orders WHERE price * quantity > 100;

-- This WORKS: ORDER BY runs after SELECT, aliases are visible
SELECT price * quantity AS total FROM orders ORDER BY total DESC;
```

### 1.4 SQL Sublanguages

SQL has four main sublanguages:

**DDL (Data Definition Language)** — structure: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`
**DML (Data Manipulation Language)** — data: `SELECT`, `INSERT`, `UPDATE`, `DELETE`
**DCL (Data Control Language)** — permissions: `GRANT`, `REVOKE`
**TCL (Transaction Control Language)** — transactions: `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`

---

## 2. Data Definition Language (DDL)

### 2.1 CREATE TABLE

```sql
CREATE TABLE users (
    id          BIGSERIAL PRIMARY KEY,
    email       TEXT UNIQUE NOT NULL,
    full_name   TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'inactive', 'suspended')),
    age         INT CHECK (age >= 0 AND age <= 150),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- With named constraints (better error messages)
CREATE TABLE products (
    id          BIGSERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    price       NUMERIC(10, 2),
    stock       INT NOT NULL DEFAULT 0,
    CONSTRAINT price_positive CHECK (price >= 0),
    CONSTRAINT stock_non_negative CHECK (stock >= 0)
);

-- CREATE TABLE IF NOT EXISTS (no error if table already exists)
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

### 2.2 ALTER TABLE

```sql
-- Add a column
ALTER TABLE users ADD COLUMN phone TEXT;
ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT FALSE;

-- Drop a column
ALTER TABLE users DROP COLUMN phone;
ALTER TABLE users DROP COLUMN IF EXISTS phone;  -- no error if doesn't exist

-- Rename a column
ALTER TABLE users RENAME COLUMN full_name TO name;

-- Change column type
ALTER TABLE users ALTER COLUMN age TYPE BIGINT;

-- Set/drop default
ALTER TABLE users ALTER COLUMN status SET DEFAULT 'active';
ALTER TABLE users ALTER COLUMN status DROP DEFAULT;

-- Set/drop NOT NULL
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
ALTER TABLE users ALTER COLUMN phone DROP NOT NULL;

-- Add constraint
ALTER TABLE users ADD CONSTRAINT email_format CHECK (email LIKE '%@%');
ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);

-- Drop constraint
ALTER TABLE users DROP CONSTRAINT email_format;

-- Rename table
ALTER TABLE users RENAME TO app_users;

-- Add foreign key
ALTER TABLE orders
    ADD CONSTRAINT orders_user_id_fk
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;
```

### 2.3 DROP TABLE

```sql
DROP TABLE users;                  -- Error if table doesn't exist
DROP TABLE IF EXISTS users;        -- No error
DROP TABLE users CASCADE;          -- Also drops dependent objects (views, FKs)
DROP TABLE users RESTRICT;         -- Refuse if anything depends on it (default)
```

### 2.4 TRUNCATE

```sql
-- Remove all rows (much faster than DELETE FROM table)
TRUNCATE TABLE logs;

-- Reset auto-increment sequence
TRUNCATE TABLE users RESTART IDENTITY;

-- Truncate multiple tables
TRUNCATE TABLE orders, order_items RESTART IDENTITY CASCADE;
```

### 2.5 CREATE INDEX

```sql
-- Basic
CREATE INDEX idx_users_email ON users(email);

-- Unique index
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Composite index
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial index
CREATE INDEX idx_users_active_email ON users(email) WHERE status = 'active';

-- Index with sort order
CREATE INDEX idx_posts_created ON posts(created_at DESC);

-- Without locking the table (production-safe)
CREATE INDEX CONCURRENTLY idx_users_phone ON users(phone);

-- Drop index
DROP INDEX idx_users_email;
DROP INDEX CONCURRENTLY idx_users_email;  -- Production-safe drop
```

---

## 3. Data Manipulation Language (DML)

### 3.1 INSERT

```sql
-- Single row
INSERT INTO users (email, full_name)
VALUES ('k@example.com', 'Kingsley');

-- Multiple rows (much faster than multiple single inserts)
INSERT INTO users (email, full_name, status)
VALUES
    ('alice@example.com', 'Alice', 'active'),
    ('bob@example.com', 'Bob', 'active'),
    ('carol@example.com', 'Carol', 'inactive');

-- Insert from a SELECT
INSERT INTO archived_users (email, full_name, archived_at)
SELECT email, full_name, NOW()
FROM users
WHERE created_at < NOW() - INTERVAL '2 years';

-- Return the inserted row(s)
INSERT INTO users (email, full_name)
VALUES ('new@example.com', 'New User')
RETURNING *;

-- Return specific columns
INSERT INTO users (email, full_name)
VALUES ('new@example.com', 'New User')
RETURNING id, created_at;

-- ON CONFLICT — upsert (insert or update)
INSERT INTO users (email, full_name)
VALUES ('k@example.com', 'Kingsley Updated')
ON CONFLICT (email) DO UPDATE
    SET full_name = EXCLUDED.full_name,
        updated_at = NOW();
-- EXCLUDED refers to the row that would have been inserted

-- ON CONFLICT DO NOTHING — ignore duplicates
INSERT INTO tags (name)
VALUES ('tech'), ('devops'), ('tech')  -- 'tech' appears twice
ON CONFLICT (name) DO NOTHING;
```

### 3.2 UPDATE

```sql
-- Basic update
UPDATE users
SET status = 'inactive'
WHERE id = 42;

-- Update multiple columns
UPDATE users
SET
    full_name = 'Kingsley Ihemelandu',
    updated_at = NOW()
WHERE id = 42;

-- Update with a calculation
UPDATE products
SET price = price * 1.10  -- 10% price increase
WHERE category_id = 5;

-- Update based on another table (UPDATE ... FROM)
UPDATE order_items oi
SET unit_price = p.price
FROM products p
WHERE oi.product_id = p.id
  AND oi.order_id = 100;

-- Update and return affected rows
UPDATE users
SET status = 'suspended'
WHERE last_login_at < NOW() - INTERVAL '1 year'
RETURNING id, email, status;

-- Update with CASE
UPDATE orders
SET status = CASE
    WHEN payment_received_at IS NOT NULL THEN 'paid'
    WHEN due_date < NOW() THEN 'overdue'
    ELSE status
END
WHERE status = 'pending';
```

### 3.3 DELETE

```sql
-- Basic delete
DELETE FROM users WHERE id = 42;

-- Delete with condition
DELETE FROM sessions
WHERE expires_at < NOW();

-- Delete based on another table (DELETE ... USING)
DELETE FROM order_items oi
USING orders o
WHERE oi.order_id = o.id
  AND o.status = 'cancelled';

-- Delete and return deleted rows
DELETE FROM users
WHERE status = 'deleted'
  AND deleted_at < NOW() - INTERVAL '30 days'
RETURNING id, email;

-- Delete all rows (slower than TRUNCATE but respects triggers)
DELETE FROM logs;
```

---

## 4. The SELECT Statement — Complete Reference

### 4.1 Basic SELECT

```sql
-- Select all columns
SELECT * FROM users;

-- Select specific columns
SELECT id, email, full_name FROM users;

-- Column aliases
SELECT
    id,
    email,
    full_name AS name,
    created_at AS "Member Since"  -- quoted alias for spaces/special chars
FROM users;

-- Computed columns
SELECT
    id,
    first_name || ' ' || last_name AS full_name,
    price * quantity AS total,
    UPPER(email) AS email_upper
FROM users;

-- Literal values
SELECT
    'Hello' AS greeting,
    42 AS answer,
    NOW() AS current_time,
    TRUE AS is_working;

-- DISTINCT — remove duplicate rows
SELECT DISTINCT status FROM users;
SELECT DISTINCT country, city FROM addresses;  -- distinct combinations

-- DISTINCT ON (Postgres-specific) — keep first row per distinct value
SELECT DISTINCT ON (user_id)
    user_id, created_at, amount
FROM orders
ORDER BY user_id, created_at DESC;
-- Returns the most recent order per user
```

### 4.2 SELECT with Expressions

```sql
-- Arithmetic
SELECT
    price,
    quantity,
    price * quantity AS subtotal,
    price * quantity * 0.075 AS tax,
    price * quantity * 1.075 AS total_with_tax
FROM order_items;

-- String operations
SELECT
    UPPER(first_name) AS first_upper,
    LOWER(email) AS email_lower,
    LENGTH(bio) AS bio_length,
    SUBSTRING(phone, 1, 3) AS area_code,
    first_name || ' ' || last_name AS full_name
FROM users;

-- Date operations
SELECT
    created_at,
    created_at::DATE AS date_only,
    EXTRACT(YEAR FROM created_at) AS year,
    AGE(NOW(), created_at) AS account_age,
    created_at + INTERVAL '30 days' AS trial_ends
FROM users;

-- Type casting
SELECT
    '42'::INT AS int_value,
    '3.14'::NUMERIC AS decimal_value,
    '2026-01-15'::DATE AS date_value,
    42::TEXT AS text_value,
    CAST(price AS INT) AS rounded_price
FROM products;
```

---

## 5. Filtering — WHERE and HAVING

### 5.1 WHERE Clause

```sql
-- Equality
WHERE status = 'active'
WHERE id = 42
WHERE price = 9.99

-- Comparison operators
WHERE age > 18
WHERE price <= 100
WHERE created_at >= '2026-01-01'
WHERE stock != 0          -- not equal
WHERE stock <> 0          -- also not equal (SQL standard)

-- Multiple conditions
WHERE status = 'active' AND age >= 18
WHERE status = 'inactive' OR status = 'suspended'
WHERE NOT (status = 'deleted')
WHERE age > 18 AND (status = 'active' OR role = 'admin')
-- Use parentheses to make precedence explicit
```

### 5.2 BETWEEN

```sql
-- Inclusive on both ends
WHERE price BETWEEN 10 AND 100
WHERE created_at BETWEEN '2026-01-01' AND '2026-12-31'
WHERE age BETWEEN 18 AND 65

-- NOT BETWEEN
WHERE price NOT BETWEEN 10 AND 100
```

### 5.3 IN and NOT IN

```sql
-- IN — value is in a list
WHERE status IN ('active', 'pending', 'verified')
WHERE id IN (1, 2, 3, 42, 99)
WHERE country IN ('NG', 'GH', 'KE', 'ZA')

-- IN with a subquery
WHERE user_id IN (
    SELECT id FROM users WHERE status = 'active'
)

-- NOT IN
WHERE status NOT IN ('deleted', 'banned')

-- WARNING: NOT IN with NULLs
-- If the list contains NULL, NOT IN returns no rows
-- Use NOT EXISTS instead (see Section 10)
WHERE id NOT IN (1, 2, NULL)  -- returns no rows!
```

### 5.4 LIKE and ILIKE

```sql
-- LIKE — case-sensitive pattern matching
WHERE email LIKE '%@gmail.com'       -- ends with
WHERE name LIKE 'King%'              -- starts with
WHERE name LIKE '%sley%'             -- contains
WHERE code LIKE 'ABC___'             -- ABC followed by exactly 3 characters

-- ILIKE — case-insensitive (PostgreSQL)
WHERE name ILIKE 'king%'             -- matches King, KING, king

-- Pattern characters:
-- % — matches any sequence of characters (including empty)
-- _ — matches exactly one character

-- NOT LIKE
WHERE email NOT LIKE '%@test.com'
```

### 5.5 Regular Expressions (PostgreSQL)

```sql
WHERE email ~ '^[a-z]+@[a-z]+\.[a-z]+$'     -- regex match (case-sensitive)
WHERE email ~* '^[a-z]+@[a-z]+\.[a-z]+$'    -- regex match (case-insensitive)
WHERE email !~ 'temp'                         -- does NOT match regex
WHERE email !~* 'temp'                        -- case-insensitive does not match
```

### 5.6 IS NULL and IS NOT NULL

```sql
WHERE deleted_at IS NULL          -- not deleted (active records)
WHERE deleted_at IS NOT NULL      -- deleted records
WHERE phone IS NULL               -- no phone on file

-- NEVER use = NULL (always returns false in SQL)
WHERE phone = NULL    -- WRONG — always returns empty result
WHERE phone IS NULL   -- CORRECT
```

### 5.7 HAVING

`HAVING` filters groups after `GROUP BY`. It's like `WHERE` but for aggregated data.

```sql
-- Find categories with more than 10 products
SELECT category_id, COUNT(*) AS product_count
FROM products
GROUP BY category_id
HAVING COUNT(*) > 10;

-- Find users who placed more than 5 orders
SELECT user_id, COUNT(*) AS order_count
FROM orders
GROUP BY user_id
HAVING COUNT(*) >= 5
ORDER BY order_count DESC;

-- WHERE vs HAVING
SELECT
    category_id,
    COUNT(*) AS active_product_count
FROM products
WHERE is_active = TRUE          -- filter BEFORE grouping (faster)
GROUP BY category_id
HAVING COUNT(*) > 5;            -- filter AFTER grouping
```

---

## 6. Sorting — ORDER BY

```sql
-- Basic sort
SELECT * FROM users ORDER BY full_name;
SELECT * FROM users ORDER BY created_at;

-- Direction
SELECT * FROM users ORDER BY created_at DESC;   -- newest first
SELECT * FROM users ORDER BY full_name ASC;     -- A-Z (default)

-- Multiple columns
SELECT * FROM orders
ORDER BY status ASC, created_at DESC;
-- Sort by status A-Z, then within each status by newest first

-- Sort by column position (valid but not recommended — fragile)
SELECT id, name, price FROM products ORDER BY 3 DESC;  -- sort by price

-- Sort by alias
SELECT price * quantity AS total FROM order_items ORDER BY total DESC;

-- Sort by expression
SELECT * FROM users ORDER BY LENGTH(full_name) DESC;

-- NULL handling in ORDER BY
ORDER BY value NULLS FIRST    -- NULLs appear first
ORDER BY value NULLS LAST     -- NULLs appear last (default for DESC)
ORDER BY value DESC NULLS LAST

-- CASE in ORDER BY (custom sort order)
ORDER BY CASE status
    WHEN 'urgent' THEN 1
    WHEN 'active' THEN 2
    WHEN 'pending' THEN 3
    ELSE 4
END;
```

---

## 7. Limiting Results — LIMIT and OFFSET

```sql
-- Take the first 10 rows
SELECT * FROM products LIMIT 10;

-- Skip first 20, take next 10 (page 3 with 10 per page)
SELECT * FROM products ORDER BY id LIMIT 10 OFFSET 20;

-- Pagination formula: OFFSET = (page - 1) * page_size
-- Page 1: LIMIT 10 OFFSET 0
-- Page 2: LIMIT 10 OFFSET 10
-- Page 3: LIMIT 10 OFFSET 20

-- FETCH/NEXT syntax (SQL standard, equivalent to LIMIT/OFFSET)
SELECT * FROM products
ORDER BY name
FETCH FIRST 10 ROWS ONLY;

SELECT * FROM products
ORDER BY name
OFFSET 20 ROWS
FETCH NEXT 10 ROWS ONLY;
```

**Why OFFSET pagination is bad at scale:**

```
At OFFSET 10000, the DB must read 10010 rows, discard 10000, return 10.
The further into the dataset, the slower the query.

Use cursor-based pagination instead:
-- Instead of: LIMIT 10 OFFSET 1000
-- Use: WHERE id > last_seen_id LIMIT 10
-- This uses the index efficiently regardless of position
```

```sql
-- Cursor-based pagination (keyset pagination)
-- First page:
SELECT * FROM posts ORDER BY created_at DESC, id DESC LIMIT 20;

-- Next page (cursor = last row's created_at and id from previous page):
SELECT * FROM posts
WHERE (created_at, id) < ('2026-01-15 10:30:00', 42)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

---

## 8. Joins — The Complete Guide

### 8.1 What Joins Do

A join combines rows from two or more tables based on a related column. The result is a new set of rows where each row contains columns from all joined tables.

### 8.2 INNER JOIN

Returns only rows where the join condition matches in **both** tables. Rows without a match are excluded.

```sql
-- Get all orders with their user's email
SELECT o.id, o.total, u.email
FROM orders o
INNER JOIN users u ON u.id = o.user_id;
-- Only orders that have a matching user (user_id is NOT NULL and user exists)

-- INNER JOIN is the default — JOIN alone means INNER JOIN
SELECT o.id, u.email
FROM orders o
JOIN users u ON u.id = o.user_id;  -- same as INNER JOIN

-- Multiple joins
SELECT
    o.id AS order_id,
    u.email,
    p.name AS product_name,
    oi.quantity,
    oi.unit_price
FROM orders o
JOIN users u ON u.id = o.user_id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE o.status = 'shipped';
```

### 8.3 LEFT JOIN (LEFT OUTER JOIN)

Returns **all rows from the left table** and matching rows from the right. If no match, right table columns are NULL.

```sql
-- Get all users, and their orders if they have any
-- Users with no orders still appear (with NULL order columns)
SELECT
    u.id,
    u.email,
    o.id AS order_id,
    o.total
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;

-- Find users who have NEVER placed an order
SELECT u.id, u.email
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.id IS NULL;  -- the NULL means no matching order was found
-- This is the "anti-join" pattern

-- Get products with their category name (some products may have no category)
SELECT p.name, c.name AS category
FROM products p
LEFT JOIN categories c ON c.id = p.category_id;
```

### 8.4 RIGHT JOIN (RIGHT OUTER JOIN)

Returns **all rows from the right table** and matching rows from the left. Mirror of LEFT JOIN. Less common — you can always rewrite a RIGHT JOIN as a LEFT JOIN by swapping table order.

```sql
-- All categories, including those with no products
SELECT c.name, p.name AS product_name
FROM products p
RIGHT JOIN categories c ON c.id = p.category_id;

-- Equivalent LEFT JOIN:
SELECT c.name, p.name AS product_name
FROM categories c
LEFT JOIN products p ON p.category_id = c.id;
```

### 8.5 FULL OUTER JOIN

Returns **all rows from both tables**. NULLs fill in where there's no match on either side.

```sql
-- All users and all orders — matched where possible
SELECT u.email, o.id AS order_id
FROM users u
FULL OUTER JOIN orders o ON o.user_id = u.id;
-- Rows with no matching user: u.email = NULL
-- Rows with no matching order: o.id = NULL

-- Use case: reconciling two datasets
SELECT
    a.id AS id_in_a,
    b.id AS id_in_b,
    CASE
        WHEN a.id IS NULL THEN 'Only in B'
        WHEN b.id IS NULL THEN 'Only in A'
        ELSE 'In both'
    END AS location
FROM table_a a
FULL OUTER JOIN table_b b ON a.key = b.key;
```

### 8.6 CROSS JOIN

Returns the Cartesian product — every combination of rows from both tables. Rarely used intentionally, but important to understand because accidental cross joins (forgetting ON) can destroy performance.

```sql
-- All combinations of sizes and colours
SELECT s.name AS size, c.name AS colour
FROM sizes s
CROSS JOIN colours c;
-- 5 sizes × 8 colours = 40 rows

-- Implicit cross join (old syntax — avoid)
SELECT * FROM table_a, table_b;  -- same as CROSS JOIN
SELECT * FROM table_a, table_b WHERE a.id = b.a_id;  -- accidental cross join becoming inner join
```

### 8.7 SELF JOIN

A table joined to itself. Used for hierarchical data, finding related rows within the same table.

```sql
-- Find all employees and their manager (manager is also an employee)
SELECT
    e.full_name AS employee,
    m.full_name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id;

-- Find users who signed up on the same day as user 42
SELECT u2.email
FROM users u1
JOIN users u2 ON DATE(u1.created_at) = DATE(u2.created_at)
WHERE u1.id = 42 AND u2.id != 42;
```

### 8.8 Join Conditions

```sql
-- ON — most explicit and flexible
JOIN orders o ON o.user_id = u.id

-- USING — when the column name is the same in both tables (simpler)
JOIN orders USING (user_id)   -- equivalent to ON users.user_id = orders.user_id

-- Multiple conditions
JOIN order_items oi ON oi.order_id = o.id AND oi.is_refunded = FALSE

-- Non-equi join (join on non-equality condition)
JOIN price_tiers pt ON o.total BETWEEN pt.min_amount AND pt.max_amount
```

### 8.9 Join Performance Intuition

```
- Index the foreign key columns (ON clause columns)
- Filter rows BEFORE joining when possible (WHERE before JOIN reduces join size)
- INNER JOINs are generally faster than OUTER JOINs
- The smaller table is usually best as the "driving" table
- EXPLAIN ANALYZE shows you what the DB actually does (Section 26)
```

---

## 9. Aggregation and GROUP BY

### 9.1 Aggregate Functions

Aggregate functions collapse a set of rows into a single value.

```sql
-- COUNT
COUNT(*)                    -- count all rows (including NULLs)
COUNT(column)               -- count non-NULL values in column
COUNT(DISTINCT column)      -- count distinct non-NULL values

-- SUM, AVG
SUM(price)                  -- total of all values
AVG(price)                  -- average (ignores NULLs)
SUM(price) / COUNT(*)       -- average including NULLs in denominator

-- MIN, MAX
MIN(price)                  -- smallest value
MAX(price)                  -- largest value
MIN(created_at)             -- earliest date
MAX(created_at)             -- latest date

-- STRING_AGG — aggregate strings
STRING_AGG(name, ', ')           -- 'Alice, Bob, Carol'
STRING_AGG(name, ', ' ORDER BY name)  -- sorted aggregation

-- ARRAY_AGG — aggregate into an array (PostgreSQL)
ARRAY_AGG(tag_name)              -- {tech, devops, linux}
ARRAY_AGG(DISTINCT tag_name ORDER BY tag_name)

-- BOOL_AND, BOOL_OR (PostgreSQL)
BOOL_AND(is_verified)       -- TRUE only if all rows are TRUE
BOOL_OR(is_verified)        -- TRUE if any row is TRUE

-- Statistical functions
STDDEV(price)               -- standard deviation
VARIANCE(price)             -- variance
PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price)  -- median
PERCENTILE_DISC(0.95) WITHIN GROUP (ORDER BY response_time)  -- 95th percentile
```

### 9.2 GROUP BY

```sql
-- Count orders per user
SELECT user_id, COUNT(*) AS order_count
FROM orders
GROUP BY user_id;

-- Total revenue per status
SELECT status, SUM(total) AS revenue
FROM orders
GROUP BY status;

-- Multiple grouping columns
SELECT
    category_id,
    status,
    COUNT(*) AS count,
    AVG(price) AS avg_price
FROM products
GROUP BY category_id, status
ORDER BY category_id, status;

-- Group by expression
SELECT
    DATE_TRUNC('month', created_at) AS month,
    COUNT(*) AS signups
FROM users
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month;

-- Group by alias (PostgreSQL allows this)
SELECT
    DATE_TRUNC('month', created_at) AS month,
    COUNT(*) AS signups
FROM users
GROUP BY month
ORDER BY month;
```

### 9.3 Aggregate with FILTER

Filter which rows contribute to an aggregate without removing them from the query:

```sql
-- Count total and active separately in one query
SELECT
    COUNT(*) AS total_users,
    COUNT(*) FILTER (WHERE status = 'active') AS active_users,
    COUNT(*) FILTER (WHERE status = 'inactive') AS inactive_users,
    AVG(age) FILTER (WHERE status = 'active') AS avg_age_active
FROM users;
```

### 9.4 ROLLUP, CUBE, GROUPING SETS

Advanced grouping that produces subtotals and grand totals:

```sql
-- ROLLUP: hierarchical subtotals
SELECT country, city, COUNT(*) AS users
FROM users
GROUP BY ROLLUP (country, city);
-- Returns: (country, city), (country, NULL=subtotal), (NULL, NULL=grand total)

-- CUBE: all combinations
SELECT year, quarter, region, SUM(revenue)
FROM sales
GROUP BY CUBE (year, quarter, region);
-- Returns all combinations of groupings

-- GROUPING SETS: custom combinations
SELECT country, city, COUNT(*)
FROM users
GROUP BY GROUPING SETS (
    (country, city),  -- by country and city
    (country),        -- by country only
    ()                -- grand total
);
```

---

## 10. Subqueries

### 10.1 What Subqueries Are

A subquery is a SELECT statement nested inside another query. It's evaluated first, and its result is used by the outer query.

### 10.2 Scalar Subqueries (Return One Value)

```sql
-- In SELECT
SELECT
    id,
    total,
    (SELECT AVG(total) FROM orders) AS avg_order_total,
    total - (SELECT AVG(total) FROM orders) AS diff_from_avg
FROM orders;

-- In WHERE
SELECT * FROM products
WHERE price > (SELECT AVG(price) FROM products);

-- In HAVING
SELECT category_id, AVG(price)
FROM products
GROUP BY category_id
HAVING AVG(price) > (SELECT AVG(price) FROM products);
```

### 10.3 Column Subqueries (Return One Column, Many Rows)

```sql
-- IN: is this value in the subquery result?
SELECT * FROM orders
WHERE user_id IN (
    SELECT id FROM users WHERE country = 'NG'
);

-- NOT IN: be careful with NULLs!
-- If subquery returns any NULL, NOT IN returns no rows
-- Use NOT EXISTS instead (see 10.5)
SELECT * FROM products
WHERE id NOT IN (
    SELECT product_id FROM order_items WHERE product_id IS NOT NULL
);

-- ANY/SOME: true if condition holds for any value
SELECT * FROM products
WHERE price > ANY (SELECT price FROM products WHERE category_id = 5);
-- Equivalent: price > MIN(price of category 5)

-- ALL: true if condition holds for ALL values
SELECT * FROM products
WHERE price > ALL (SELECT price FROM products WHERE category_id = 5);
-- Equivalent: price > MAX(price of category 5)
```

### 10.4 Table Subqueries (Return Multiple Columns and Rows)

Used in FROM clause — called a "derived table" or "inline view":

```sql
-- Derived table
SELECT u.email, order_stats.order_count, order_stats.total_spent
FROM users u
JOIN (
    SELECT
        user_id,
        COUNT(*) AS order_count,
        SUM(total) AS total_spent
    FROM orders
    GROUP BY user_id
) AS order_stats ON order_stats.user_id = u.id;

-- Filtering aggregated results
SELECT *
FROM (
    SELECT
        user_id,
        COUNT(*) AS purchase_count,
        SUM(total) AS lifetime_value
    FROM orders
    WHERE status = 'completed'
    GROUP BY user_id
) AS customer_stats
WHERE lifetime_value > 1000
ORDER BY lifetime_value DESC;
```

### 10.5 EXISTS and NOT EXISTS

`EXISTS` returns TRUE if the subquery returns any rows. More efficient than `IN` for large datasets, and handles NULLs correctly.

```sql
-- Find users who have at least one order
SELECT u.*
FROM users u
WHERE EXISTS (
    SELECT 1  -- the SELECT list doesn't matter — just need to know if rows exist
    FROM orders o
    WHERE o.user_id = u.id
);

-- Find users who have NEVER ordered (anti-join)
SELECT u.*
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- Safer than NOT IN because NULLs don't cause issues
-- EXISTS is typically faster than IN for large subqueries

-- EXISTS with condition
SELECT u.*
FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.user_id = u.id
      AND o.total > 500
      AND o.status = 'completed'
);
```

### 10.6 Correlated Subqueries

A correlated subquery references columns from the outer query. It's executed once for each row of the outer query — this can be slow for large datasets.

```sql
-- Find each user's most recent order (correlated)
SELECT u.id, u.email,
    (SELECT MAX(o.created_at)
     FROM orders o
     WHERE o.user_id = u.id) AS last_order_date
FROM users u;

-- Find products more expensive than the average in their category
SELECT p.name, p.price, p.category_id
FROM products p
WHERE p.price > (
    SELECT AVG(p2.price)
    FROM products p2
    WHERE p2.category_id = p.category_id  -- references outer query's p
);

-- This is usually better written as a window function or CTE (see Sections 11-12)
```

---

## 11. Common Table Expressions (CTEs)

### 11.1 What CTEs Are

A CTE (Common Table Expression) is a named temporary result set defined with `WITH`. It makes complex queries more readable by breaking them into named parts, like functions. Unlike subqueries, CTEs can be referenced multiple times in the same query.

```sql
-- Basic CTE
WITH active_users AS (
    SELECT id, email, full_name
    FROM users
    WHERE status = 'active'
      AND deleted_at IS NULL
)
SELECT * FROM active_users WHERE full_name ILIKE 'king%';

-- Multiple CTEs
WITH
    active_users AS (
        SELECT id, email FROM users WHERE status = 'active'
    ),
    user_orders AS (
        SELECT user_id, COUNT(*) AS order_count, SUM(total) AS total_spent
        FROM orders WHERE status = 'completed'
        GROUP BY user_id
    )
SELECT
    u.email,
    COALESCE(uo.order_count, 0) AS orders,
    COALESCE(uo.total_spent, 0) AS spent
FROM active_users u
LEFT JOIN user_orders uo ON uo.user_id = u.id
ORDER BY spent DESC;
```

### 11.2 CTEs vs Subqueries

```sql
-- Subquery version (harder to read)
SELECT u.email, stats.order_count
FROM users u
JOIN (
    SELECT user_id, COUNT(*) AS order_count
    FROM orders GROUP BY user_id
) stats ON stats.user_id = u.id
WHERE stats.order_count > 5;

-- CTE version (cleaner)
WITH order_stats AS (
    SELECT user_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY user_id
)
SELECT u.email, os.order_count
FROM users u
JOIN order_stats os ON os.user_id = u.id
WHERE os.order_count > 5;
```

### 11.3 Recursive CTEs

Recursive CTEs query hierarchical or graph data — trees, org charts, category hierarchies.

```sql
-- Traverse a category hierarchy
WITH RECURSIVE category_tree AS (
    -- Base case: start from root categories (no parent)
    SELECT id, name, parent_id, 0 AS depth, name::TEXT AS path
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive case: join children to their parent
    SELECT
        c.id,
        c.name,
        c.parent_id,
        ct.depth + 1,
        ct.path || ' > ' || c.name  -- build the path string
    FROM categories c
    JOIN category_tree ct ON ct.id = c.parent_id
)
SELECT * FROM category_tree ORDER BY path;

-- Find all reports of a manager (org chart)
WITH RECURSIVE org_chart AS (
    -- Start from a specific manager
    SELECT id, full_name, manager_id, 0 AS level
    FROM employees
    WHERE id = 1  -- CEO

    UNION ALL

    -- Find their direct reports
    SELECT e.id, e.full_name, e.manager_id, oc.level + 1
    FROM employees e
    JOIN org_chart oc ON oc.id = e.manager_id
)
SELECT level, full_name FROM org_chart ORDER BY level, full_name;

-- Fibonacci sequence (demo of recursive computation)
WITH RECURSIVE fib AS (
    SELECT 0 AS n, 0 AS a, 1 AS b
    UNION ALL
    SELECT n + 1, b, a + b FROM fib WHERE n < 10
)
SELECT n, a AS fibonacci FROM fib;
```

### 11.4 Writable CTEs (Data-Modifying CTEs)

CTEs can contain INSERT, UPDATE, or DELETE:

```sql
-- Move rows from one table to another atomically
WITH deleted AS (
    DELETE FROM active_jobs
    WHERE status = 'completed'
    RETURNING *
)
INSERT INTO completed_jobs SELECT * FROM deleted;

-- Update and log the change in one statement
WITH updated AS (
    UPDATE products
    SET price = price * 0.9
    WHERE category_id = 5
    RETURNING id, name, price
)
INSERT INTO price_change_log (product_id, new_price, changed_at)
SELECT id, price, NOW() FROM updated;
```

---

## 12. Window Functions

### 12.1 What Window Functions Are

Window functions perform calculations across a set of rows that are related to the current row — without collapsing those rows into a single output row like aggregate functions do. Every row keeps its identity; window functions just add new computed columns.

```sql
-- Aggregate: collapses rows, one result per group
SELECT department_id, AVG(salary) FROM employees GROUP BY department_id;
-- Returns one row per department

-- Window function: keeps rows, adds the aggregate as a column
SELECT
    employee_id,
    department_id,
    salary,
    AVG(salary) OVER (PARTITION BY department_id) AS dept_avg_salary
FROM employees;
-- Returns one row per employee, with their department's average salary added
```

### 12.2 Syntax

```sql
function_name() OVER (
    [PARTITION BY column1, column2, ...]  -- divide rows into groups
    [ORDER BY column3 ASC/DESC]           -- define order within each group
    [ROWS/RANGE frame_specification]      -- define the window frame
)
```

### 12.3 PARTITION BY

```sql
-- Average salary per department for each employee
SELECT
    name,
    department,
    salary,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg,
    salary - AVG(salary) OVER (PARTITION BY department) AS diff_from_avg
FROM employees;

-- No PARTITION BY = the whole table is one window
SELECT
    name,
    salary,
    AVG(salary) OVER () AS company_avg  -- all employees
FROM employees;
```

### 12.4 Ranking Functions

```sql
-- ROW_NUMBER: unique sequential number (no ties)
SELECT
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num
FROM employees;

-- RANK: gaps for ties (1, 2, 2, 4 — skips 3)
SELECT
    name,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS rank
FROM employees;

-- DENSE_RANK: no gaps for ties (1, 2, 2, 3 — no skip)
SELECT
    name,
    salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
FROM employees;

-- PERCENT_RANK: relative rank as percentage (0 to 1)
SELECT
    name,
    salary,
    PERCENT_RANK() OVER (ORDER BY salary) AS percentile
FROM employees;

-- NTILE: divide into N equal buckets
SELECT
    name,
    salary,
    NTILE(4) OVER (ORDER BY salary DESC) AS quartile  -- 1=top 25%, 4=bottom 25%
FROM employees;
```

### 12.5 Top N Per Group (Very Common Pattern)

```sql
-- Top 3 most expensive products per category
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY price DESC) AS rn
    FROM products
)
SELECT * FROM ranked WHERE rn <= 3;

-- Most recent order per user
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
    FROM orders
)
SELECT * FROM ranked WHERE rn = 1;

-- Alternatively using DISTINCT ON (PostgreSQL shortcut)
SELECT DISTINCT ON (user_id) *
FROM orders
ORDER BY user_id, created_at DESC;
```

### 12.6 LAG and LEAD — Accessing Other Rows

```sql
-- LAG: access a previous row's value
SELECT
    date,
    revenue,
    LAG(revenue) OVER (ORDER BY date) AS prev_revenue,
    revenue - LAG(revenue) OVER (ORDER BY date) AS change,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY date))
        / NULLIF(LAG(revenue) OVER (ORDER BY date), 0),
        2
    ) AS pct_change
FROM daily_revenue
ORDER BY date;

-- LEAD: access a future row's value
SELECT
    date,
    revenue,
    LEAD(revenue) OVER (ORDER BY date) AS next_day_revenue
FROM daily_revenue;

-- LAG with offset and default
LAG(revenue, 7) OVER (ORDER BY date)          -- 7 rows back (last week)
LAG(revenue, 1, 0) OVER (ORDER BY date)       -- 1 row back, default 0 if no previous row

-- LAG within partitions
LAG(revenue) OVER (PARTITION BY region ORDER BY date)  -- previous revenue in same region
```

### 12.7 FIRST_VALUE, LAST_VALUE, NTH_VALUE

```sql
-- First and last value in the window
SELECT
    name,
    salary,
    department,
    FIRST_VALUE(salary) OVER (PARTITION BY department ORDER BY salary DESC) AS highest_salary,
    LAST_VALUE(salary) OVER (
        PARTITION BY department ORDER BY salary DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS lowest_salary
    -- LAST_VALUE requires explicit frame to include all rows
FROM employees;

-- Nth value
NTH_VALUE(salary, 2) OVER (PARTITION BY department ORDER BY salary DESC)  -- 2nd highest
```

### 12.8 Running Totals and Moving Averages

```sql
-- Running total (cumulative sum)
SELECT
    date,
    daily_revenue,
    SUM(daily_revenue) OVER (ORDER BY date) AS running_total
FROM sales;

-- Running total per group
SELECT
    user_id,
    order_date,
    amount,
    SUM(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS cumulative_spend
FROM orders;

-- 7-day moving average
SELECT
    date,
    revenue,
    AVG(revenue) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d
FROM daily_revenue;

-- 30-day moving sum
SELECT
    date,
    new_signups,
    SUM(new_signups) OVER (
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_30d_signups
FROM daily_signups;
```

### 12.9 Window Frames

```sql
-- Frame defines which rows are included relative to the current row

ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW     -- from start to current row
ROWS BETWEEN 3 PRECEDING AND CURRENT ROW             -- current row + 3 before
ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING             -- current row + 1 before + 1 after
ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING     -- current row to end
ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING  -- all rows in partition

-- ROWS vs RANGE:
-- ROWS counts actual rows (physical)
-- RANGE counts rows with the same ORDER BY value (logical)
-- For non-duplicate data, they behave the same
-- RANGE can behave unexpectedly with ties
```

---

## 13. Set Operations — UNION, INTERSECT, EXCEPT

Set operations combine the results of two queries. Both queries must have the same number of columns with compatible types.

### 13.1 UNION

```sql
-- UNION: combine results, remove duplicates
SELECT id, name FROM customers
UNION
SELECT id, name FROM suppliers;

-- UNION ALL: combine results, keep duplicates (faster — no dedup step)
SELECT 'customer' AS type, email FROM customers
UNION ALL
SELECT 'supplier' AS type, email FROM suppliers;

-- Multiple UNIONs
SELECT email FROM users WHERE status = 'active'
UNION ALL
SELECT email FROM invited_users
UNION ALL
SELECT email FROM beta_users;
```

### 13.2 INTERSECT

```sql
-- INTERSECT: rows that appear in BOTH result sets
SELECT email FROM newsletter_subscribers
INTERSECT
SELECT email FROM paying_customers;
-- Emails that are both subscribers AND paying customers

-- INTERSECT ALL: keep duplicates
SELECT product_id FROM wishlist_items
INTERSECT ALL
SELECT product_id FROM cart_items;
```

### 13.3 EXCEPT

```sql
-- EXCEPT: rows in first set but NOT in second
SELECT email FROM all_users
EXCEPT
SELECT email FROM opted_out_users;
-- Users who haven't opted out

-- EXCEPT ALL: keep duplicates (count-sensitive)
SELECT product_id FROM inventory
EXCEPT ALL
SELECT product_id FROM sold_items;

-- ORDER BY applies to final result
SELECT email FROM list_a
EXCEPT
SELECT email FROM list_b
ORDER BY email;
```

---

## 14. String Functions and Operations

```sql
-- Concatenation
'Hello' || ' ' || 'World'          -- 'Hello World'
CONCAT('Hello', ' ', 'World')      -- 'Hello World' (NULL-safe)
CONCAT_WS(', ', 'Alice', 'Bob')    -- 'Alice, Bob' (with separator)

-- Case
UPPER('hello')                     -- 'HELLO'
LOWER('HELLO')                     -- 'hello'
INITCAP('hello world')             -- 'Hello World'

-- Length
LENGTH('hello')                    -- 5
CHAR_LENGTH('hello')               -- 5 (same, but counts characters not bytes)
BIT_LENGTH('hello')                -- 40 (bits)
OCTET_LENGTH('hello')              -- 5 (bytes)

-- Trimming
TRIM('  hello  ')                  -- 'hello'
LTRIM('  hello  ')                 -- 'hello  ' (left trim)
RTRIM('  hello  ')                 -- '  hello' (right trim)
TRIM('x' FROM 'xxhelloxx')         -- 'hello' (trim specific character)

-- Padding
LPAD('42', 5, '0')                 -- '00042'
RPAD('hi', 5, '.')                 -- 'hi...'

-- Substring
SUBSTRING('Hello World', 1, 5)     -- 'Hello' (1-indexed)
SUBSTRING('Hello World' FROM 7)    -- 'World' (from position 7 to end)
LEFT('Hello World', 5)             -- 'Hello'
RIGHT('Hello World', 5)            -- 'World'

-- Position / search
POSITION('World' IN 'Hello World') -- 7
STRPOS('Hello World', 'World')     -- 7 (PostgreSQL)
STARTS_WITH('Hello', 'He')         -- TRUE

-- Replace
REPLACE('Hello World', 'World', 'SQL')  -- 'Hello SQL'
REGEXP_REPLACE('foo123bar', '[0-9]+', 'NUM')  -- 'fooNUMbar'

-- Split
SPLIT_PART('a,b,c,d', ',', 2)     -- 'b' (1-indexed)
STRING_TO_ARRAY('a,b,c', ',')      -- {a,b,c}
ARRAY_TO_STRING(ARRAY['a','b','c'], ',')  -- 'a,b,c'

-- Repeat and Reverse
REPEAT('ab', 3)                    -- 'ababab'
REVERSE('hello')                   -- 'olleh'

-- Format (like printf)
FORMAT('Hello %s, you are %s years old', 'Kingsley', 21)

-- Regular expressions
REGEXP_MATCH('abc123', '\d+')      -- {123}
'hello' ~ '^he'                    -- TRUE (regex match)
REGEXP_REPLACE(phone, '[^0-9]', '', 'g')  -- strip non-numeric characters
```

---

## 15. Numeric Functions

```sql
-- Rounding
ROUND(3.14159, 2)           -- 3.14
ROUND(3.5)                  -- 4 (rounds half up)
CEIL(3.1)                   -- 4 (ceiling — round up)
FLOOR(3.9)                  -- 3 (floor — round down)
TRUNC(3.9)                  -- 3 (truncate toward zero)
TRUNC(-3.9)                 -- -3

-- Absolute value, sign
ABS(-42)                    -- 42
SIGN(-42)                   -- -1
SIGN(0)                     -- 0
SIGN(42)                    -- 1

-- Power and roots
POWER(2, 10)                -- 1024
SQRT(144)                   -- 12
CBRT(27)                    -- 3 (cube root)

-- Modulo
17 % 5                      -- 2
MOD(17, 5)                  -- 2

-- Logarithms
LN(2.718)                   -- ~1 (natural log)
LOG(100)                    -- 2 (base 10)
LOG(2, 8)                   -- 3 (log base 2 of 8)

-- Min and Max (non-aggregate — between two values)
LEAST(10, 20, 5)            -- 5 (minimum of the arguments)
GREATEST(10, 20, 5)         -- 20 (maximum of the arguments)

-- Random
RANDOM()                    -- 0.0 to 1.0 (exclusive)
FLOOR(RANDOM() * 100)       -- 0 to 99
FLOOR(RANDOM() * 100) + 1  -- 1 to 100

-- Division
10 / 3                      -- 3 (integer division)
10.0 / 3                    -- 3.3333... (float division)
10::NUMERIC / 3             -- 3.3333... (cast to get decimal)
```

---

## 16. Date and Time Functions

```sql
-- Current date and time
NOW()                       -- current timestamp with timezone
CURRENT_TIMESTAMP           -- same as NOW()
CURRENT_DATE                -- today's date (no time)
CURRENT_TIME                -- current time

-- Extracting parts
EXTRACT(YEAR FROM created_at)        -- 2026
EXTRACT(MONTH FROM created_at)       -- 1 (January)
EXTRACT(DAY FROM created_at)         -- 15
EXTRACT(HOUR FROM created_at)        -- 14
EXTRACT(MINUTE FROM created_at)      -- 30
EXTRACT(DOW FROM created_at)         -- 0=Sunday, 6=Saturday
EXTRACT(DOY FROM created_at)         -- day of year (1-366)
EXTRACT(WEEK FROM created_at)        -- ISO week number
EXTRACT(EPOCH FROM created_at)       -- Unix timestamp (seconds since 1970-01-01)
EXTRACT(EPOCH FROM AGE(end, start))  -- Duration in seconds

-- DATE_PART is synonymous with EXTRACT in PostgreSQL
DATE_PART('year', created_at)

-- Truncating
DATE_TRUNC('year', created_at)       -- 2026-01-01 00:00:00+00
DATE_TRUNC('month', created_at)      -- 2026-01-01 00:00:00+00
DATE_TRUNC('week', created_at)       -- Monday of the week
DATE_TRUNC('day', created_at)        -- Midnight of the day
DATE_TRUNC('hour', created_at)       -- Start of the hour

-- Arithmetic
NOW() + INTERVAL '1 day'
NOW() - INTERVAL '30 days'
NOW() + INTERVAL '2 hours 30 minutes'
created_at + INTERVAL '7 days'

-- Date difference
NOW() - created_at                   -- INTERVAL type
EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400  -- days as a number
AGE(NOW(), created_at)               -- human-readable interval (3 years 2 months...)
AGE(created_at)                      -- age from today

-- Formatting
TO_CHAR(NOW(), 'YYYY-MM-DD')                    -- '2026-01-15'
TO_CHAR(NOW(), 'DD/MM/YYYY HH24:MI:SS')         -- '15/01/2026 14:30:00'
TO_CHAR(NOW(), 'Month DD, YYYY')                -- 'January  15, 2026'
TO_CHAR(price, 'FM$999,999.00')                 -- '$1,234.56'

-- Parsing
TO_TIMESTAMP('2026-01-15', 'YYYY-MM-DD')
'2026-01-15'::DATE
'2026-01-15 14:30:00'::TIMESTAMPTZ

-- Timezone handling
NOW() AT TIME ZONE 'Africa/Lagos'       -- Convert to Lagos time
NOW() AT TIME ZONE 'UTC'               -- Convert to UTC
TIMESTAMPTZ '2026-01-15 14:30:00+01'  -- With explicit timezone

-- Generate a series of dates (very useful for reports)
SELECT generate_series(
    '2026-01-01'::DATE,
    '2026-12-31'::DATE,
    '1 month'::INTERVAL
) AS month;
```

---

## 17. Conditional Logic — CASE, COALESCE, NULLIF

### 17.1 CASE

```sql
-- Simple CASE (equality checks)
SELECT
    name,
    CASE status
        WHEN 'active' THEN 'Active User'
        WHEN 'inactive' THEN 'Inactive User'
        WHEN 'suspended' THEN 'Suspended'
        ELSE 'Unknown'
    END AS status_label
FROM users;

-- Searched CASE (any condition)
SELECT
    name,
    price,
    CASE
        WHEN price < 10 THEN 'Budget'
        WHEN price BETWEEN 10 AND 50 THEN 'Mid-range'
        WHEN price > 50 THEN 'Premium'
        ELSE 'Unpriced'
    END AS price_tier
FROM products;

-- CASE in ORDER BY
ORDER BY CASE status
    WHEN 'active' THEN 1
    WHEN 'pending' THEN 2
    ELSE 3
END;

-- CASE in aggregation (pivot)
SELECT
    category_id,
    COUNT(*) FILTER (WHERE status = 'active') AS active_count,
    COUNT(*) FILTER (WHERE status = 'inactive') AS inactive_count,
    -- equivalent with CASE:
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_count_alt
FROM products
GROUP BY category_id;
```

### 17.2 COALESCE

Returns the first non-NULL value in the list:

```sql
-- Return a default value when column is NULL
COALESCE(phone, 'No phone')
COALESCE(discount, 0)
COALESCE(nickname, first_name, 'Anonymous')  -- first non-null of the three

-- Common use: handle NULL in calculations
price * COALESCE(discount_rate, 1)  -- if no discount, multiply by 1 (no change)
COALESCE(total, 0) + COALESCE(tax, 0)  -- safe addition when either might be NULL

-- Replace NULLs in string aggregation
STRING_AGG(COALESCE(phone, 'N/A'), ', ')
```

### 17.3 NULLIF

Returns NULL if both arguments are equal, otherwise returns the first argument:

```sql
NULLIF(value, 0)         -- returns NULL if value is 0 (prevents division by zero)
NULLIF(value, '')        -- returns NULL if value is empty string

-- Classic use: prevent division by zero
100.0 / NULLIF(denominator, 0)
-- If denominator is 0, NULLIF returns NULL, and 100 / NULL = NULL (safe)

-- Treat empty strings as NULL
COALESCE(NULLIF(TRIM(email), ''), 'no-email@example.com')
```

### 17.4 IIF and SWITCH (Not Standard SQL)

PostgreSQL doesn't have IIF, but you can use:

```sql
-- Ternary-like with CASE
CASE WHEN condition THEN true_value ELSE false_value END
```

---

## 18. NULL — The Complete Guide

### 18.1 What NULL Is

NULL represents the absence of a value — not zero, not empty string, not false. NULL means "unknown" or "not applicable".

NULL has a unique property: **any operation with NULL returns NULL**.

```sql
NULL = NULL       -- NULL (not TRUE!)
NULL = 5          -- NULL
NULL + 5          -- NULL
NULL || 'hello'   -- NULL
NOT NULL          -- NULL
```

This is why you can't use `= NULL` in a WHERE clause — it always returns NULL, which is treated as FALSE.

### 18.2 NULL Comparisons

```sql
-- WRONG — always returns no rows
WHERE column = NULL
WHERE column != NULL

-- CORRECT
WHERE column IS NULL
WHERE column IS NOT NULL

-- IS DISTINCT FROM — treats NULL as a value, not unknown
WHERE column IS DISTINCT FROM other_column
-- equivalent to: column != other_column OR (column IS NULL AND other_column IS NOT NULL) ...

WHERE column IS NOT DISTINCT FROM other_column
-- equivalent to: column = other_column OR (both are NULL)
```

### 18.3 NULL in Aggregates

```sql
-- COUNT(*) counts all rows including NULLs
-- COUNT(column) counts only non-NULL values
SELECT
    COUNT(*) AS total_rows,
    COUNT(phone) AS rows_with_phone,  -- excludes NULLs
    AVG(age),                          -- ignores NULLs in calculation
    SUM(discount)                      -- NULLs treated as nothing (not zero)
FROM users;

-- NULL in aggregation can be surprising:
-- If all values are NULL, SUM returns NULL (not 0)
-- If all values are NULL, AVG returns NULL (not 0)
-- Use COALESCE to handle:
SUM(COALESCE(discount, 0))
```

### 18.4 NULL in Sorting

```sql
-- By default in PostgreSQL:
-- ORDER BY column ASC  → NULLs last
-- ORDER BY column DESC → NULLs first

-- Control explicitly
ORDER BY column ASC NULLS FIRST
ORDER BY column ASC NULLS LAST
ORDER BY column DESC NULLS LAST
```

### 18.5 NULL in Joins

```sql
-- NULL foreign keys are excluded from INNER JOINs
-- They appear as no-match rows in OUTER JOINs
SELECT u.name, o.id
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;
-- Users with no orders: o.id will be NULL in the result
```

### 18.6 NOT IN with NULLs — The Trap

```sql
-- This returns NO ROWS if subquery contains any NULL
SELECT * FROM a WHERE id NOT IN (SELECT b_id FROM b);
-- If any b_id is NULL, the comparison a.id != NULL is NULL (unknown)
-- SQL treats unknown as false, so no rows pass

-- SAFE alternative: NOT EXISTS
SELECT * FROM a WHERE NOT EXISTS (SELECT 1 FROM b WHERE b.a_id = a.id);

-- Or ensure no NULLs in subquery
SELECT * FROM a WHERE id NOT IN (
    SELECT b_id FROM b WHERE b_id IS NOT NULL
);
```

---

## 19. Transactions and Concurrency

### 19.1 What Transactions Are

A transaction is a unit of work that's either entirely committed or entirely rolled back. Either all the statements succeed, or none of them take effect.

```sql
-- Without a transaction, each statement is its own transaction (autocommit)
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
-- If the second statement fails, account 1 has lost $100 with no credit

-- With a transaction:
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
-- Either both succeed, or neither does
```

### 19.2 Transaction Commands

```sql
BEGIN;              -- Start a transaction
START TRANSACTION;  -- Same as BEGIN

COMMIT;             -- Save all changes permanently
ROLLBACK;           -- Undo all changes since BEGIN

-- Savepoints — partial rollback within a transaction
BEGIN;
    INSERT INTO orders (user_id) VALUES (42);
    SAVEPOINT before_items;

    INSERT INTO order_items (order_id, product_id) VALUES (1, 99);  -- might fail
    -- If it fails:
    ROLLBACK TO before_items;  -- Undo back to savepoint, keep the INSERT into orders

COMMIT;

-- Release a savepoint
RELEASE SAVEPOINT before_items;
```

### 19.3 Isolation Levels

Isolation levels control what a transaction can see of other concurrent transactions' changes.

**Phenomena they protect against:**

**Dirty read** — reading uncommitted data from another transaction. That other transaction might roll back, making your read invalid.

**Non-repeatable read** — you read a row twice in one transaction and get different results because another transaction committed a change between your reads.

**Phantom read** — you run the same query twice and get different sets of rows because another transaction inserted/deleted rows between your reads.

```sql
-- Set isolation level
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Or at BEGIN:
BEGIN ISOLATION LEVEL SERIALIZABLE;
```

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|---|---|---|---|
| READ UNCOMMITTED | Possible | Possible | Possible |
| READ COMMITTED | Protected | Possible | Possible |
| REPEATABLE READ | Protected | Protected | Possible |
| SERIALIZABLE | Protected | Protected | Protected |

```
PostgreSQL default: READ COMMITTED
- Reads committed data at the time of each statement
- The same query run twice in a transaction may return different data
- Good for most OLTP workloads

REPEATABLE READ:
- All reads in a transaction see the same snapshot (the state at transaction start)
- Use when you need consistent reads across multiple statements
- In PostgreSQL, also protects against phantoms (stricter than SQL standard)

SERIALIZABLE:
- Strongest isolation — transactions behave as if they ran one at a time
- PostgreSQL uses SSI (Serializable Snapshot Isolation) — no locking overhead
- Use for financial operations, inventory management, anything requiring strict consistency
- May cause serialization failures that need to be retried
```

### 19.4 Locking

```sql
-- SELECT FOR UPDATE — lock selected rows for update
-- Other transactions trying to SELECT FOR UPDATE on same rows will wait
BEGIN;
SELECT * FROM accounts WHERE id = 42 FOR UPDATE;
-- Now safely update knowing no one else can modify this row
UPDATE accounts SET balance = balance - 100 WHERE id = 42;
COMMIT;

-- FOR UPDATE SKIP LOCKED — skip rows already locked (useful for job queues)
SELECT * FROM jobs WHERE status = 'pending' LIMIT 1 FOR UPDATE SKIP LOCKED;
-- Gets the next available job that isn't being processed by another worker

-- FOR SHARE — shared lock (multiple readers, no writers)
SELECT * FROM accounts WHERE id = 42 FOR SHARE;

-- NOWAIT — fail immediately instead of waiting for lock
SELECT * FROM accounts WHERE id = 42 FOR UPDATE NOWAIT;

-- Table-level locks
LOCK TABLE products IN EXCLUSIVE MODE;
LOCK TABLE products IN SHARE MODE;
```

### 19.5 Transaction Best Practices

```sql
-- Keep transactions short
-- Long transactions hold locks, block other transactions, and fill up WAL logs
-- Move expensive work outside the transaction if possible

-- Handle errors properly
BEGIN;
    -- your statements
COMMIT;
-- In application code, catch errors and ROLLBACK

-- Avoid long transactions that do reads only (use REPEATABLE READ snapshot)
-- Use SELECT FOR UPDATE when you need to prevent concurrent modification
-- Use SKIP LOCKED for efficient job queues and task distribution
```

---

## 20. Views

### 20.1 What Views Are

A view is a saved SELECT query with a name. It looks and behaves like a table when queried, but it runs the underlying query each time.

```sql
-- Create a view
CREATE VIEW active_users AS
SELECT id, email, full_name, created_at
FROM users
WHERE status = 'active'
  AND deleted_at IS NULL;

-- Use it like a table
SELECT * FROM active_users;
SELECT * FROM active_users WHERE email LIKE '%@gmail.com';

-- Update the view definition
CREATE OR REPLACE VIEW active_users AS
SELECT id, email, full_name, created_at, last_login_at
FROM users
WHERE status = 'active'
  AND deleted_at IS NULL;

-- Drop a view
DROP VIEW active_users;
DROP VIEW IF EXISTS active_users;
DROP VIEW active_users CASCADE;  -- also drops dependent views
```

### 20.2 Useful View Patterns

```sql
-- Security view — hide sensitive columns
CREATE VIEW users_public AS
SELECT id, username, avatar_url, created_at
FROM users;
-- Grant access to users_public, not users table directly

-- Join view — simplify complex queries
CREATE VIEW order_details AS
SELECT
    o.id AS order_id,
    o.status,
    o.total,
    o.created_at,
    u.email AS customer_email,
    u.full_name AS customer_name
FROM orders o
JOIN users u ON u.id = o.user_id;

-- Aggregated view
CREATE VIEW monthly_revenue AS
SELECT
    DATE_TRUNC('month', created_at) AS month,
    COUNT(*) AS order_count,
    SUM(total) AS revenue
FROM orders
WHERE status = 'completed'
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month;
```

### 20.3 Materialised Views

A materialised view stores the query result physically. It doesn't run on every access — it must be explicitly refreshed. Excellent for expensive aggregate queries.

```sql
-- Create materialised view
CREATE MATERIALIZED VIEW monthly_sales_summary AS
SELECT
    DATE_TRUNC('month', o.created_at) AS month,
    p.category_id,
    COUNT(DISTINCT o.id) AS order_count,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.total) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE o.status = 'completed'
GROUP BY DATE_TRUNC('month', o.created_at), p.category_id;

-- Create index on the materialised view
CREATE INDEX ON monthly_sales_summary(month);
CREATE INDEX ON monthly_sales_summary(category_id);

-- Refresh the data (runs the query again, updates the stored result)
REFRESH MATERIALIZED VIEW monthly_sales_summary;

-- Refresh without blocking reads (PostgreSQL 9.4+)
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales_summary;
-- Requires a unique index on the view

-- Schedule refreshes with pg_cron or an external scheduler
-- SELECT cron.schedule('0 * * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales_summary');
```

### 20.4 Updatable Views

Simple views (no joins, no aggregations, no DISTINCT) can be updated through the view:

```sql
UPDATE active_users SET full_name = 'New Name' WHERE id = 42;
-- Runs: UPDATE users SET full_name = 'New Name' WHERE id = 42 AND status = 'active' ...

-- WITH CHECK OPTION prevents updates that would make the row invisible in the view
CREATE VIEW active_users AS
SELECT * FROM users WHERE status = 'active'
WITH CHECK OPTION;
-- UPDATE active_users SET status = 'inactive' WHERE id = 42;  -- ERROR
```

---

## 21. Indexes in SQL

*(Design strategy is covered in the Database Design reference. This section covers SQL syntax and usage.)*

```sql
-- Create
CREATE INDEX idx_name ON table(column);
CREATE UNIQUE INDEX idx_name ON table(column);
CREATE INDEX idx_name ON table(col1, col2);  -- composite
CREATE INDEX idx_name ON table(column) WHERE condition;  -- partial
CREATE INDEX idx_name ON table USING gin(jsonb_column);
CREATE INDEX CONCURRENTLY idx_name ON table(column);  -- no table lock

-- Drop
DROP INDEX idx_name;
DROP INDEX CONCURRENTLY idx_name;
DROP INDEX IF EXISTS idx_name;

-- List indexes (PostgreSQL)
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'users';

-- Check if index is being used
SELECT * FROM pg_stat_user_indexes WHERE relname = 'users';
-- idx_scan = number of times index was used for scans
-- If idx_scan = 0 after running for a while, the index may be unused

-- Rebuild an index (after heavy updates/deletes)
REINDEX INDEX idx_name;
REINDEX TABLE table_name;
REINDEX CONCURRENTLY INDEX idx_name;  -- no lock

-- See what indexes exist
\d table_name   -- in psql
```

---

## 22. Stored Procedures and Functions

### 22.1 Functions

A function takes parameters, performs operations, and returns a value. Can be called in a SELECT statement.

```sql
-- Simple function
CREATE OR REPLACE FUNCTION add_numbers(a INT, b INT)
RETURNS INT AS $$
    SELECT a + b;
$$ LANGUAGE SQL;

SELECT add_numbers(3, 4);  -- 7

-- Function with PL/pgSQL (procedural language)
CREATE OR REPLACE FUNCTION calculate_discount(
    price NUMERIC,
    discount_pct NUMERIC
)
RETURNS NUMERIC AS $$
BEGIN
    IF discount_pct < 0 OR discount_pct > 100 THEN
        RAISE EXCEPTION 'Discount must be between 0 and 100, got %', discount_pct;
    END IF;

    RETURN price * (1 - discount_pct / 100);
END;
$$ LANGUAGE plpgsql;

SELECT calculate_discount(100.00, 20);  -- 80.00

-- Function returning a table
CREATE OR REPLACE FUNCTION get_user_orders(p_user_id BIGINT)
RETURNS TABLE (
    order_id BIGINT,
    total NUMERIC,
    status TEXT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT o.id, o.total, o.status, o.created_at
    FROM orders o
    WHERE o.user_id = p_user_id
    ORDER BY o.created_at DESC;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM get_user_orders(42);

-- Drop function
DROP FUNCTION IF EXISTS calculate_discount(NUMERIC, NUMERIC);
```

### 22.2 Stored Procedures

Stored procedures (PostgreSQL 11+) can control transactions — functions cannot. Use procedures when you need `COMMIT` or `ROLLBACK` inside the routine.

```sql
CREATE OR REPLACE PROCEDURE transfer_funds(
    from_account INT,
    to_account INT,
    amount NUMERIC
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Deduct from sender
    UPDATE accounts
    SET balance = balance - amount
    WHERE id = from_account;

    -- Check sufficient funds
    IF (SELECT balance FROM accounts WHERE id = from_account) < 0 THEN
        RAISE EXCEPTION 'Insufficient funds';
    END IF;

    -- Credit receiver
    UPDATE accounts
    SET balance = balance + amount
    WHERE id = to_account;

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
$$;

-- Call a procedure
CALL transfer_funds(1, 2, 500.00);
```

---

## 23. Triggers

A trigger is a function that runs automatically when a specified event occurs on a table.

```sql
-- Step 1: Create the trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();   -- NEW refers to the row being inserted/updated
    RETURN NEW;               -- RETURN NEW to save the modified row
END;
$$ LANGUAGE plpgsql;

-- Step 2: Attach the trigger to a table
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON users           -- fires BEFORE each UPDATE row
    FOR EACH ROW                     -- fire once per row (not once per statement)
    EXECUTE FUNCTION update_updated_at();

-- Trigger timing: BEFORE or AFTER
-- BEFORE: can modify the row (NEW), prevent the operation (RETURN NULL)
-- AFTER: can't modify the row, used for side effects (logging, notifications)

-- Trigger events: INSERT, UPDATE, DELETE, TRUNCATE
-- You can combine: INSERT OR UPDATE OR DELETE

-- Trigger examples

-- Audit log trigger
CREATE OR REPLACE FUNCTION log_user_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO user_audit (user_id, action, old_data, changed_at)
        VALUES (OLD.id, 'DELETE', row_to_json(OLD), NOW());
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO user_audit (user_id, action, old_data, new_data, changed_at)
        VALUES (NEW.id, 'UPDATE', row_to_json(OLD), row_to_json(NEW), NOW());
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO user_audit (user_id, action, new_data, changed_at)
        VALUES (NEW.id, 'INSERT', row_to_json(NEW), NOW());
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_audit
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION log_user_changes();

-- Trigger variables
-- TG_OP: 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE'
-- TG_TABLE_NAME: name of the table
-- TG_WHEN: 'BEFORE' or 'AFTER'
-- NEW: new row data (INSERT, UPDATE)
-- OLD: old row data (UPDATE, DELETE)

-- Drop trigger
DROP TRIGGER IF EXISTS set_updated_at ON users;
```

---

## 24. JSON in SQL

### 24.1 JSON vs JSONB

```sql
-- JSON: stored as text, parsed on every operation
-- JSONB: stored as binary, indexed, faster to query
-- Always use JSONB unless you specifically need to preserve key order or whitespace

CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    metadata JSONB NOT NULL DEFAULT '{}'
);
```

### 24.2 Operators

```sql
-- Accessing values
metadata -> 'key'              -- returns JSON value (preserves type)
metadata ->> 'key'             -- returns TEXT value
metadata -> 'nested' ->> 'key' -- nested access
metadata #> '{a,b,c}'          -- path access (returns JSON)
metadata #>> '{a,b,c}'         -- path access (returns TEXT)

-- Examples
SELECT metadata -> 'user' ->> 'email' FROM events;
SELECT metadata #>> '{order,items,0,name}' FROM events;  -- array index access

-- Containment
metadata @> '{"status": "active"}'    -- contains this key-value
metadata <@ '{"a":1, "b":2}'         -- is contained by

-- Key existence
metadata ? 'key'                       -- has key?
metadata ?| ARRAY['key1', 'key2']      -- has any of these keys?
metadata ?& ARRAY['key1', 'key2']      -- has ALL of these keys?
```

### 24.3 Modifying JSONB

```sql
-- Set a key
UPDATE events
SET metadata = jsonb_set(metadata, '{status}', '"active"')
WHERE id = 1;

-- Set nested key
UPDATE events
SET metadata = jsonb_set(metadata, '{user,email}', '"new@example.com"')
WHERE id = 1;

-- Remove a key
UPDATE events
SET metadata = metadata - 'temp_key'
WHERE id = 1;

-- Remove multiple keys
UPDATE events
SET metadata = metadata - ARRAY['key1', 'key2']
WHERE id = 1;

-- Merge/concat two JSONB objects
UPDATE events
SET metadata = metadata || '{"new_key": "value", "another": 42}'
WHERE id = 1;
```

### 24.4 Querying and Aggregating JSON

```sql
-- Query by JSONB field
SELECT * FROM events WHERE metadata ->> 'status' = 'active';
SELECT * FROM events WHERE metadata @> '{"status": "active"}';
SELECT * FROM events WHERE (metadata ->> 'amount')::NUMERIC > 100;

-- Expand JSONB array to rows
SELECT jsonb_array_elements(metadata -> 'tags') AS tag FROM posts;

-- Expand JSONB object to key-value pairs
SELECT key, value FROM jsonb_each(metadata);
SELECT key, value FROM jsonb_each_text(metadata);  -- values as text

-- Build JSONB from query
SELECT jsonb_object_agg(key, value) FROM my_table;
SELECT jsonb_agg(row_to_json(t)) FROM my_table t;  -- array of row objects

-- Useful JSONB functions
jsonb_pretty(metadata)              -- formatted output for readability
jsonb_strip_nulls(metadata)         -- remove keys with NULL values
jsonb_typeof(metadata)              -- 'object', 'array', 'string', 'number', 'boolean', 'null'
jsonb_array_length(metadata->'tags') -- length of a JSONB array

-- Index JSONB for fast queries
CREATE INDEX ON events USING gin(metadata);           -- index all keys
CREATE INDEX ON events USING gin(metadata jsonb_path_ops);  -- more efficient, supports @>
CREATE INDEX ON events ((metadata ->> 'status'));     -- index specific field
```

---

## 25. Full-Text Search

### 25.1 How It Works

Full-text search converts text into a `tsvector` (a searchable document) and a search query into a `tsquery`. The `@@` operator checks if a document matches a query.

```sql
-- tsvector: a preprocessed document (stemmed, stop words removed, positions recorded)
SELECT to_tsvector('english', 'The quick brown fox jumped over the lazy dogs');
-- Returns: 'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2

-- tsquery: a search query with operators
SELECT to_tsquery('english', 'quick & fox');        -- quick AND fox
SELECT to_tsquery('english', 'quick | slow');        -- quick OR slow
SELECT to_tsquery('english', 'quick & !slow');       -- quick AND NOT slow
SELECT plainto_tsquery('english', 'quick brown fox'); -- phrase to query
SELECT websearch_to_tsquery('english', 'quick fox -slow');  -- web-style query

-- Match check
SELECT to_tsvector('english', 'The quick brown fox') @@ to_tsquery('english', 'fox');
-- TRUE
```

### 25.2 Full-Text Search in Practice

```sql
-- Search posts for 'database design'
SELECT id, title
FROM posts
WHERE to_tsvector('english', title || ' ' || body) @@ plainto_tsquery('english', 'database design');

-- Better: store the tsvector as a generated column (fast)
ALTER TABLE posts ADD COLUMN search_vector TSVECTOR
    GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(body, '')), 'B')
    ) STORED;
-- 'A' = highest weight, 'B' = lower weight (affects ranking)

-- Index the generated column
CREATE INDEX ON posts USING gin(search_vector);

-- Now search is fast
SELECT id, title
FROM posts
WHERE search_vector @@ plainto_tsquery('english', 'database design')
ORDER BY ts_rank(search_vector, plainto_tsquery('english', 'database design')) DESC;

-- ts_rank: how well does the document match the query?
-- Higher = better match

-- Highlight matching terms
SELECT
    title,
    ts_headline('english', body, query, 'StartSel=<b>, StopSel=</b>') AS excerpt
FROM posts, plainto_tsquery('english', 'database design') query
WHERE search_vector @@ query;
```

---

## 26. Query Optimisation — Reading and Thinking

### 26.1 EXPLAIN and EXPLAIN ANALYZE

```sql
-- EXPLAIN: show the query plan without running the query
EXPLAIN SELECT * FROM users WHERE email = 'k@example.com';

-- EXPLAIN ANALYZE: run the query AND show actual timing
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'k@example.com';

-- More detail
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders o
JOIN users u ON u.id = o.user_id
WHERE o.status = 'shipped';

-- FORMAT options: TEXT (default), JSON, XML, YAML
EXPLAIN (ANALYZE, FORMAT JSON) SELECT ...;
```

### 26.2 Reading the Query Plan

```
-- Example output:
Seq Scan on users  (cost=0.00..458.00 rows=1 width=120) (actual time=0.043..4.302 rows=1 loops=1)
  Filter: (email = 'k@example.com'::text)
  Rows Removed by Filter: 9999

-- Reading:
-- "Seq Scan" = sequential scan (reading every row)
-- "Index Scan" = using an index (good)
-- "Bitmap Index Scan" = using an index with bitmap (good for multi-condition)
-- cost=0.00..458.00 = estimated startup cost..total cost (in arbitrary units)
-- rows=1 = estimated rows returned
-- actual time=0.043..4.302 = actual milliseconds (startup..total)
-- actual rows=1 = actual rows returned
-- Rows Removed by Filter: 9999 = 9999 rows read and discarded (bad — needs an index)
```

### 26.3 Common Plan Nodes

```
Seq Scan       — full table scan (bad for large tables with selective conditions)
Index Scan     — uses index, fetches rows directly (good)
Index Only Scan — all data from index, no heap fetch (best)
Bitmap Heap Scan — index gives a bitmap of matching pages, then heap accessed
Hash Join      — hashes smaller table, probes with larger (good for large joins)
Nested Loop    — for each row in outer, scan inner (good for small tables/indexed inner)
Merge Join     — both inputs sorted, merge (good for sorted large datasets)
Sort           — explicit sort operation (look for indexes to eliminate)
Hash Aggregate — aggregation using a hash table
GroupAggregate — aggregation on sorted input
Limit          — LIMIT clause
```

### 26.4 What to Look For

```sql
-- Bad signs:
-- Seq Scan on large table with Filter removing many rows → add index
-- Sort on large dataset → add index matching the ORDER BY
-- Hash Join with very large hash table → check if a join condition is indexed
-- Nested Loop with large outer table and unindexed inner → add index to inner
-- Very high "Rows Removed by Filter" → index would help

-- Useful query to find slow queries (requires pg_stat_statements extension)
SELECT
    query,
    calls,
    total_exec_time / calls AS avg_ms,
    rows / calls AS avg_rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

### 26.5 Optimisation Techniques

```sql
-- 1. Add indexes (see Database Design reference and Section 21)

-- 2. Use EXISTS instead of IN for subqueries
-- BAD for large subqueries:
WHERE user_id IN (SELECT id FROM users WHERE status = 'active')
-- GOOD:
WHERE EXISTS (SELECT 1 FROM users WHERE id = orders.user_id AND status = 'active')

-- 3. Avoid functions on indexed columns in WHERE
-- BAD: function prevents index use
WHERE UPPER(email) = 'K@EXAMPLE.COM'
-- GOOD: use ILIKE or a functional index
WHERE email ILIKE 'k@example.com'
-- Or create functional index: CREATE INDEX ON users (UPPER(email));

-- 4. Avoid SELECT * in production code
-- Pull only the columns you need — less I/O, less network

-- 5. Use LIMIT when you only need some rows
-- Even with good indexes, LIMIT allows early termination

-- 6. Filter early
-- Put the most selective WHERE conditions first conceptually
-- (the planner reorders, but be explicit for readability)

-- 7. Use CTEs wisely
-- In PostgreSQL 12+, CTEs are inlined by default (the planner can optimise through them)
-- In older versions, CTEs were "optimization fences" — always materialised
-- Use WITH ... AS MATERIALIZED to force materialisation
-- Use WITH ... AS NOT MATERIALIZED to force inlining

-- 8. Use materialised views for expensive recurring queries

-- 9. Analyse statistics
ANALYZE users;  -- update statistics for better planner decisions
-- Usually runs automatically, but useful after bulk loads
```

---

## 27. Advanced Patterns — Senior Level

### 27.1 Upsert Patterns

```sql
-- Simple upsert: insert or update
INSERT INTO user_settings (user_id, key, value)
VALUES (42, 'theme', 'dark')
ON CONFLICT (user_id, key) DO UPDATE
    SET value = EXCLUDED.value,
        updated_at = NOW();

-- Upsert with condition: only update if newer
INSERT INTO cache (key, value, cached_at)
VALUES ('product:42', '{"name":"Widget"}', NOW())
ON CONFLICT (key) DO UPDATE
    SET value = EXCLUDED.value,
        cached_at = EXCLUDED.cached_at
    WHERE EXCLUDED.cached_at > cache.cached_at;  -- only update if fresher data

-- Upsert do nothing (idempotent inserts)
INSERT INTO processed_events (event_id, processed_at)
VALUES ('evt_abc123', NOW())
ON CONFLICT (event_id) DO NOTHING;
```

### 27.2 Gap and Island Problems

Finding ranges of consecutive data is a classic SQL interview and analytics challenge:

```sql
-- Find "islands" — consecutive ranges of values
-- Given: user login dates, find periods of consecutive daily activity

WITH ordered AS (
    SELECT
        user_id,
        login_date,
        login_date - ROW_NUMBER() OVER (
            PARTITION BY user_id ORDER BY login_date
        )::INT AS island_key
        -- Consecutive dates have the same island_key
        -- because date - sequential_number = constant
    FROM user_logins
),
islands AS (
    SELECT
        user_id,
        MIN(login_date) AS streak_start,
        MAX(login_date) AS streak_end,
        COUNT(*) AS streak_length
    FROM ordered
    GROUP BY user_id, island_key
)
SELECT * FROM islands ORDER BY streak_length DESC;
```

### 27.3 Pivot / Cross-Tabulation

Turning rows into columns:

```sql
-- Monthly revenue per product category (rows → columns)
SELECT
    DATE_TRUNC('month', o.created_at) AS month,
    SUM(oi.total) FILTER (WHERE p.category_id = 1) AS electronics,
    SUM(oi.total) FILTER (WHERE p.category_id = 2) AS clothing,
    SUM(oi.total) FILTER (WHERE p.category_id = 3) AS food,
    SUM(oi.total) AS total
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
GROUP BY DATE_TRUNC('month', o.created_at)
ORDER BY month;

-- Using CASE for pivoting
SELECT
    user_id,
    SUM(CASE WHEN type = 'purchase' THEN amount ELSE 0 END) AS purchases,
    SUM(CASE WHEN type = 'refund' THEN amount ELSE 0 END) AS refunds,
    SUM(CASE WHEN type = 'credit' THEN amount ELSE 0 END) AS credits
FROM transactions
GROUP BY user_id;
```

### 27.4 Generating Data with generate_series

```sql
-- Generate a complete date series (fill in missing dates for charts)
WITH date_range AS (
    SELECT generate_series(
        '2026-01-01'::DATE,
        '2026-12-31'::DATE,
        '1 day'::INTERVAL
    )::DATE AS date
),
daily_signups AS (
    SELECT DATE(created_at) AS date, COUNT(*) AS signups
    FROM users
    GROUP BY DATE(created_at)
)
SELECT
    dr.date,
    COALESCE(ds.signups, 0) AS signups  -- 0 for days with no signups
FROM date_range dr
LEFT JOIN daily_signups ds ON ds.date = dr.date
ORDER BY dr.date;

-- Generate a series of numbers
SELECT generate_series(1, 10) AS n;

-- Generate hours
SELECT generate_series(
    NOW()::DATE,
    NOW()::DATE + INTERVAL '1 day',
    '1 hour'::INTERVAL
) AS hour;
```

### 27.5 Lateral Joins

A LATERAL join can reference columns from preceding FROM items. Like a correlated subquery but as a join:

```sql
-- Get the 3 most recent orders for each user
SELECT u.id, u.email, recent.id AS order_id, recent.total
FROM users u
JOIN LATERAL (
    SELECT id, total
    FROM orders
    WHERE user_id = u.id
    ORDER BY created_at DESC
    LIMIT 3
) AS recent ON TRUE;

-- Better than a correlated subquery because LATERAL processes each user once
-- and can be more efficiently planned

-- Useful with functions that return rows
SELECT u.id, stats.*
FROM users u
JOIN LATERAL get_user_stats(u.id) AS stats ON TRUE;
```

### 27.6 Temporal Queries — Point in Time

```sql
-- Find the price of product 42 on a specific date
-- (requires price history table with valid_from/valid_to)
SELECT price
FROM product_prices
WHERE product_id = 42
  AND valid_from <= '2026-06-01'
  AND (valid_to IS NULL OR valid_to > '2026-06-01');

-- Overlapping date ranges (booking conflicts)
SELECT b1.id, b2.id
FROM bookings b1
JOIN bookings b2 ON b1.room_id = b2.room_id
    AND b1.id < b2.id  -- avoid duplicate pairs
    AND b1.check_in < b2.check_out  -- ranges overlap condition
    AND b2.check_in < b1.check_out;

-- Timeline query: what was the state at each point in time?
SELECT
    status,
    changed_at,
    LEAD(changed_at) OVER (ORDER BY changed_at) AS changed_until
FROM order_status_history
WHERE order_id = 42
ORDER BY changed_at;
```

### 27.7 Recursive Query Patterns

```sql
-- Bill of Materials (explode components recursively)
WITH RECURSIVE bom AS (
    SELECT component_id, parent_id, quantity, 1 AS level
    FROM components
    WHERE parent_id = 100  -- top-level product

    UNION ALL

    SELECT c.component_id, c.parent_id, c.quantity * b.quantity, b.level + 1
    FROM components c
    JOIN bom b ON b.component_id = c.parent_id
)
SELECT component_id, SUM(quantity) AS total_needed
FROM bom
GROUP BY component_id;

-- Shortest path between nodes (simple graph)
WITH RECURSIVE paths AS (
    SELECT from_node, to_node, ARRAY[from_node, to_node] AS path, 1 AS depth
    FROM edges WHERE from_node = 'A'

    UNION ALL

    SELECT e.from_node, e.to_node, p.path || e.to_node, p.depth + 1
    FROM edges e
    JOIN paths p ON p.to_node = e.from_node
    WHERE NOT e.to_node = ANY(p.path)  -- prevent cycles
      AND p.depth < 10
)
SELECT * FROM paths WHERE to_node = 'Z'
ORDER BY depth LIMIT 1;
```

### 27.8 Advanced Aggregation Patterns

```sql
-- Percentile by group
SELECT
    category_id,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS median_price,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY price) AS p90_price,
    PERCENTILE_DISC(0.95) WITHIN GROUP (ORDER BY price) AS p95_price
FROM products
GROUP BY category_id;

-- Mode (most common value)
SELECT
    category_id,
    MODE() WITHIN GROUP (ORDER BY price) AS most_common_price
FROM products
GROUP BY category_id;

-- Correlation
SELECT CORR(price, stock_quantity) AS price_stock_correlation
FROM products;

-- Regression
SELECT
    REGR_SLOPE(revenue, ad_spend) AS revenue_per_ad_dollar,
    REGR_INTERCEPT(revenue, ad_spend) AS base_revenue,
    REGR_R2(revenue, ad_spend) AS r_squared
FROM campaign_data;
```

---

## 28. Common Mistakes and How to Avoid Them

### "The query returns wrong results with JOINs and aggregation"

```sql
-- WRONG: joining before aggregating inflates counts
SELECT u.id, COUNT(o.id) AS order_count, COUNT(r.id) AS review_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
LEFT JOIN reviews r ON r.user_id = u.id
GROUP BY u.id;
-- If a user has 3 orders and 4 reviews → 12 combinations → COUNT = 12 for both

-- RIGHT: aggregate before joining, or use COUNT DISTINCT
SELECT u.id,
    COUNT(DISTINCT o.id) AS order_count,
    COUNT(DISTINCT r.id) AS review_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
LEFT JOIN reviews r ON r.user_id = u.id
GROUP BY u.id;

-- Or aggregate separately
SELECT u.id, oc.order_count, rc.review_count
FROM users u
LEFT JOIN (
    SELECT user_id, COUNT(*) AS order_count FROM orders GROUP BY user_id
) oc ON oc.user_id = u.id
LEFT JOIN (
    SELECT user_id, COUNT(*) AS review_count FROM reviews GROUP BY user_id
) rc ON rc.user_id = u.id;
```

### "NOT IN returns no results"

```sql
-- Happens when subquery contains NULL
WHERE id NOT IN (SELECT user_id FROM banned WHERE user_id IS NOT NULL)
-- Always add IS NOT NULL, or use NOT EXISTS
WHERE NOT EXISTS (SELECT 1 FROM banned WHERE banned.user_id = users.id)
```

### "DISTINCT doesn't do what I expect"

```sql
-- DISTINCT applies to the entire row, not just one column
SELECT DISTINCT user_id, status FROM orders;
-- Returns distinct (user_id, status) pairs, not distinct user_ids
-- If you want distinct user_ids: SELECT DISTINCT user_id FROM orders;
-- Or: use GROUP BY
```

### "Performance degrades as data grows"

```sql
-- Check: is there an index on the WHERE column?
-- Check: is a function wrapping the indexed column?
WHERE LOWER(email) = 'k@example.com'  -- index on email not used!
-- Fix: CREATE INDEX ON users (LOWER(email))  or use ILIKE

-- Check: are you using SELECT *?
-- Check: are you paginating with large OFFSETs?
-- Check: EXPLAIN ANALYZE to find the bottleneck
```

### "Using UPDATE without WHERE"

```sql
-- This updates EVERY ROW in the table
UPDATE users SET status = 'inactive';
-- Always double-check UPDATE and DELETE have a WHERE clause
-- Good practice: run the SELECT first, then convert to UPDATE/DELETE

SELECT * FROM users WHERE last_login_at < NOW() - INTERVAL '1 year';
-- Looks right? Then:
UPDATE users SET status = 'inactive'
WHERE last_login_at < NOW() - INTERVAL '1 year';
```

### "Division by zero"

```sql
-- WRONG:
SELECT total_revenue / total_orders AS avg_order_value FROM stats;

-- RIGHT: use NULLIF to avoid dividing by zero
SELECT total_revenue / NULLIF(total_orders, 0) AS avg_order_value FROM stats;
-- Returns NULL instead of error when total_orders = 0
```

### "Using HAVING instead of WHERE for non-aggregate filters"

```sql
-- WRONG: inefficient — filters after grouping
SELECT user_id, COUNT(*)
FROM orders
GROUP BY user_id
HAVING user_id > 100;

-- RIGHT: filter before grouping
SELECT user_id, COUNT(*)
FROM orders
WHERE user_id > 100
GROUP BY user_id;
```

### "Forgetting that NULL propagates"

```sql
-- Arithmetic with NULL returns NULL
SELECT 5 + NULL;       -- NULL
SELECT 5 * 0;          -- 0 (not NULL)

-- String concat with NULL
SELECT 'Hello ' || NULL;     -- NULL
SELECT CONCAT('Hello ', NULL); -- 'Hello ' (CONCAT is NULL-safe)

-- Conditionals with NULL
SELECT NULL = NULL;    -- NULL (not TRUE)
SELECT NULL OR TRUE;   -- TRUE
SELECT NULL AND TRUE;  -- NULL
SELECT NULL AND FALSE; -- FALSE
```

### "GROUP BY errors"

```sql
-- Every column in SELECT must be in GROUP BY or wrapped in an aggregate
-- WRONG:
SELECT user_id, email, COUNT(*) FROM orders GROUP BY user_id;
-- email is not in GROUP BY and not aggregated → ERROR

-- RIGHT:
SELECT user_id, COUNT(*) FROM orders GROUP BY user_id;
-- Or:
SELECT user_id, MAX(email) AS email, COUNT(*) FROM orders GROUP BY user_id;
```

---

---

## 29. Practice — E-Commerce Schema

A real schema with seed data and graded questions. Work through these in order — each group builds on the last.

> **Note:** The schema below uses MySQL syntax (`AUTO_INCREMENT`, `ENUM`, `IF NOT EXISTS` on `CREATE DATABASE`). The queries in the answers are written in standard SQL that works on both MySQL and PostgreSQL with minor adjustments noted where relevant.

---

### 29.1 Schema and Seed Data

```sql
-- Create and select the database (MySQL)
CREATE DATABASE IF NOT EXISTS ecommerce_db;
USE ecommerce_db;

-- Categories lookup table
CREATE TABLE IF NOT EXISTS categories (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    category_id INT,
    price       DECIMAL(10, 2) NOT NULL,
    stock_qty   INT DEFAULT 0,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(150) NOT NULL,
    email      VARCHAR(200) UNIQUE NOT NULL,
    region     VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    customer_id  INT,
    total_amount DECIMAL(10, 2),
    status       ENUM('PENDING', 'COMPLETED', 'CANCELLED') DEFAULT 'PENDING',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Order items (line items)
CREATE TABLE IF NOT EXISTS order_items (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    order_id   INT,
    product_id INT,
    quantity   INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id)   REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ─── Seed Data ────────────────────────────────────────────────────────────────

INSERT INTO categories (name) VALUES
    ('Electronics'),
    ('Clothing'),
    ('Home & Kitchen'),
    ('Sports'),
    ('Beauty');

INSERT INTO products (name, category_id, price, stock_qty) VALUES
    ('Wireless Headphones',  1, 150.00, 80),
    ('Bluetooth Speaker',    1,  75.50, 50),
    ('Laptop Stand',         1,  45.00, 120),
    ('Men\'s Running Shoes', 2,  89.99, 60),
    ('Women\'s Hoodie',      2,  55.00, 100),
    ('Denim Jacket',         2, 120.00, 35),
    ('Air Fryer',            3, 200.00, 25),
    ('Blender',              3,  65.00, 40),
    ('Yoga Mat',             4,  35.00, 90),
    ('Dumbbells 5kg Pair',   4,  48.00, 70),
    ('Face Serum',           5,  29.99, 200),
    ('Sunscreen SPF 50',     5,  18.00, 150);

INSERT INTO customers (name, email, region) VALUES
    ('Kwame Asante', 'kwame@email.com', 'Greater Accra'),
    ('Ama Boateng',  'ama@email.com',   'Ashanti'),
    ('John Mensah',  'john@email.com',  'Western'),
    ('Abena Owusu',  'abena@email.com', 'Greater Accra'),
    ('Kofi Darko',   'kofi@email.com',  'Eastern');

INSERT INTO orders (customer_id, total_amount, status) VALUES
    (1, 225.50, 'COMPLETED'),
    (2,  89.99, 'COMPLETED'),
    (3, 265.00, 'PENDING'),
    (4,  47.99, 'CANCELLED'),
    (5, 123.00, 'COMPLETED');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1,  1, 150.00),   -- Kwame: headphones
    (1, 2,  1,  75.50),   -- Kwame: speaker
    (2, 4,  1,  89.99),   -- Ama:   shoes
    (3, 7,  1, 200.00),   -- John:  air fryer
    (3, 9,  1,  35.00),   -- John:  yoga mat
    (4, 11, 1,  29.99),   -- Abena: face serum
    (4, 12, 1,  18.00),   -- Abena: sunscreen
    (5, 5,  1,  55.00),   -- Kofi:  hoodie
    (5, 10, 1,  48.00);   -- Kofi:  dumbbells
```

---

### 29.2 SELECT Questions

#### Q1 — Retrieve every column from the `products` table

```sql
SELECT * FROM products;
```

Straightforward. `*` returns all columns. In production code, prefer listing columns explicitly — this is fine for exploration.

---

#### Q2 — List `name` and `email` from `customers`, renamed to `customer_name` and `contact_email`

```sql
SELECT
    name  AS customer_name,
    email AS contact_email
FROM customers;
```

`AS` creates an alias — a label for the column in the output. Aliases don't change the underlying data.

---

#### Q3 — Retrieve all products sorted by `price` from most to least expensive

```sql
SELECT *
FROM products
ORDER BY price DESC;
```

`DESC` reverses the default ascending order. Without `ORDER BY`, SQL makes no guarantee about row order.

---

#### Q4 — Top 5 cheapest products, showing only `name` and `price`

```sql
SELECT name, price
FROM products
ORDER BY price ASC
LIMIT 5;
```

`ORDER BY price ASC` sorts cheapest first (ASC is the default and can be omitted). `LIMIT 5` keeps only the first 5 rows after sorting. Both together give you the 5 cheapest.

---

### 29.3 Arithmetic Questions

#### Q5 — Add a flat GH₵ 10 shipping fee to each product's price

```sql
SELECT
    name,
    price,
    price + 10 AS price_with_shipping
FROM products;
```

Arithmetic expressions in `SELECT` create computed columns. The result exists only in the query output — the table is not changed.

---

#### Q6 — Total stock value per product (price × quantity in stock)

```sql
SELECT
    name,
    price,
    stock_qty,
    price * stock_qty AS total_stock_value
FROM products;
```

Multiply two columns together. Useful for inventory valuation reports. A product with price `150.00` and `80` in stock has a total stock value of `12,000.00`.

---

#### Q7 — Apply a 10% discount to all products

```sql
SELECT
    name,
    price,
    ROUND(price * 0.90, 2) AS discounted_price
FROM products;
```

Multiplying by `0.90` keeps 90% of the price (removes 10%). `ROUND(..., 2)` ensures the result has exactly 2 decimal places. Alternatively: `price - (price * 0.10)`.

---

#### Q8 — Cost, gross profit, and margin percentage

```sql
SELECT
    name,
    price,
    ROUND(price * 0.30, 2)                         AS estimated_cost,
    ROUND(price - (price * 0.30), 2)               AS gross_profit,
    ROUND(((price - price * 0.30) / price) * 100, 2) AS margin_pct
FROM products;
```

Breaking down the margin formula:
- `estimated_cost` = 30% of selling price
- `gross_profit` = selling price − cost
- `margin_pct` = (gross profit / selling price) × 100

For a product at GH₵ 150: cost = 45, profit = 105, margin = 70%.

---

### 29.4 Filter and Conditions Questions

#### Q9 — Products priced between GH₵ 30 and GH₵ 100, sorted by price ascending

```sql
SELECT *
FROM products
WHERE price BETWEEN 30 AND 100
ORDER BY price ASC;
```

`BETWEEN` is inclusive on both ends — same as `price >= 30 AND price <= 100`. You should get: Sunscreen, Face Serum, Yoga Mat, Dumbbells, Laptop Stand, Blender, Women's Hoodie, Men's Running Shoes, Bluetooth Speaker.

---

#### Q10 — Customers in `Greater Accra`

```sql
SELECT *
FROM customers
WHERE region = 'Greater Accra';
```

Exact string match. Returns Kwame Asante and Abena Owusu.

---

#### Q11 — Products in `Electronics` or `Sports` categories, with category name and price

```sql
SELECT
    p.name        AS product_name,
    c.name        AS category_name,
    p.price
FROM products p
JOIN categories c ON c.id = p.category_id
WHERE c.name IN ('Electronics', 'Sports')
ORDER BY c.name, p.name;
```

This requires a JOIN because the category name lives in `categories`, not `products`. The filter goes on `c.name` after the join. `IN` is cleaner than `c.name = 'Electronics' OR c.name = 'Sports'`.

---

#### Q12 — Products whose name contains the word `Blender`

```sql
SELECT name, price
FROM products
WHERE name LIKE '%Blender%';
```

`%` matches any sequence of characters on either side. `LIKE '%Blender%'` matches any name containing "Blender" anywhere. For case-insensitive matching in PostgreSQL, use `ILIKE`. In MySQL, `LIKE` is case-insensitive by default.

---

#### Q13 — Label each product with a price tier

```sql
SELECT
    name,
    price,
    CASE
        WHEN price < 50          THEN 'Budget'
        WHEN price BETWEEN 50 AND 150 THEN 'Mid-range'
        ELSE                          'Premium'
    END AS price_tier
FROM products
ORDER BY price;
```

`CASE` evaluates conditions top to bottom and returns the first match. The `ELSE` catches everything that doesn't match any `WHEN` — here that's anything above GH₵ 150. Expected tiers: Air Fryer (200) → Premium; Wireless Headphones (150) → Mid-range (BETWEEN is inclusive); Sunscreen (18) → Budget.

---

### 29.5 Joins Questions

#### Q14 — Products with their category name, price, and stock quantity

```sql
SELECT
    p.name       AS product_name,
    c.name       AS category_name,
    p.price,
    p.stock_qty
FROM products p
JOIN categories c ON c.id = p.category_id
ORDER BY c.name ASC, p.name ASC;
```

An `INNER JOIN` (the default `JOIN`) returns only rows where a match exists in both tables. Since all products have a `category_id` that exists in `categories`, all 12 products appear. Table aliases (`p`, `c`) keep the query readable and are required when both tables have a column with the same name.

---

#### Q15 — Completed orders with customer name and order total

```sql
SELECT
    o.id           AS order_id,
    c.name         AS customer_name,
    o.total_amount,
    o.status
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'COMPLETED'
ORDER BY o.total_amount DESC;
```

The `WHERE` filter is applied after the join. Three orders are completed (Kwame: 225.50, Ama: 89.99, Kofi: 123.00). John's PENDING and Abena's CANCELLED orders are excluded.

---

#### Q16 — Full order breakdown: 4-table join

```sql
SELECT
    o.id                           AS order_id,
    c.name                         AS customer_name,
    p.name                         AS product_name,
    oi.quantity,
    oi.unit_price,
    oi.quantity * oi.unit_price    AS line_total
FROM orders o
JOIN customers   c  ON c.id  = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
JOIN products    p  ON p.id  = oi.product_id
ORDER BY o.id, line_total DESC;
```

Each join adds another table to the result. The execution path is:
1. `orders` — the anchor
2. `JOIN customers` — get the customer for each order
3. `JOIN order_items` — expand each order into its line items
4. `JOIN products` — get the product name for each line item

`line_total` is computed from the order item's `unit_price` (the price at the time of sale — not the current product price, which may have changed). This is why denormalising the price into `order_items` matters.

---

#### Q17 — Filter Q16 to line totals above GH₵ 100, sorted descending

```sql
SELECT
    o.id                        AS order_id,
    c.name                      AS customer_name,
    p.name                      AS product_name,
    oi.quantity,
    oi.unit_price,
    oi.quantity * oi.unit_price AS line_total
FROM orders o
JOIN customers   c  ON c.id        = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
JOIN products    p  ON p.id        = oi.product_id
WHERE oi.quantity * oi.unit_price > 100
ORDER BY line_total DESC;
```

You cannot use the alias `line_total` in the `WHERE` clause — aliases are defined in `SELECT`, which runs after `WHERE` in the logical execution order. You must repeat the expression: `oi.quantity * oi.unit_price > 100`.

Expected results: Kwame's headphones (150.00), John's air fryer (200.00), Kwame's speaker (75.50 — excluded, below 100), Ama's shoes (89.99 — excluded), Kofi's hoodie (55.00 — excluded).

---

### 29.6 Aggregation Questions

#### Q18 — Product count per category, sorted by count descending

```sql
SELECT
    c.name        AS category_name,
    COUNT(p.id)   AS product_count
FROM categories c
LEFT JOIN products p ON p.category_id = c.id
GROUP BY c.id, c.name
ORDER BY product_count DESC;
```

A `LEFT JOIN` is used here instead of `INNER JOIN` so that categories with zero products still appear in the result (with a count of 0). `COUNT(p.id)` counts non-NULL product IDs — when no products exist, `p.id` is NULL and the count is 0. `GROUP BY c.id, c.name` groups one row per category.

With an `INNER JOIN`, categories with no products would silently disappear from the results.

---

#### Q19 — Average, minimum, and maximum price per category

```sql
SELECT
    c.name              AS category_name,
    ROUND(AVG(p.price), 2) AS avg_price,
    MIN(p.price)           AS min_price,
    MAX(p.price)           AS max_price
FROM categories c
JOIN products p ON p.category_id = c.id
GROUP BY c.id, c.name
ORDER BY c.name;
```

Three aggregate functions applied to the same column within the same `GROUP BY`. Each produces one value per group. `ROUND(AVG(...), 2)` handles cases where the average isn't a clean decimal.

Sample output:
- Beauty: avg 23.995 → 24.00, min 18.00, max 29.99
- Electronics: avg 90.17, min 45.00, max 150.00

---

#### Q20 — Total spend per customer on COMPLETED orders only

```sql
SELECT
    c.name                  AS customer_name,
    COUNT(DISTINCT o.id)    AS completed_orders,
    SUM(o.total_amount)     AS total_spend
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.status = 'COMPLETED'
GROUP BY c.id, c.name
ORDER BY total_spend DESC;
```

`WHERE o.status = 'COMPLETED'` filters rows **before** grouping, so only completed orders enter the aggregation. `COUNT(DISTINCT o.id)` counts unique orders per customer (the `DISTINCT` guards against duplication if the join produced duplicates). `SUM(o.total_amount)` sums those orders.

Customers with no completed orders (John, Abena) are excluded entirely by the `INNER JOIN` + `WHERE` combination. If you wanted to show them with a 0, you'd need a `LEFT JOIN` and move the status filter into the join condition: `JOIN orders o ON o.customer_id = c.id AND o.status = 'COMPLETED'`.

---

#### Q21 — Customers who spent more than GH₵ 100 across completed orders

```sql
SELECT
    c.name              AS customer_name,
    SUM(o.total_amount) AS total_spend
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.status = 'COMPLETED'
GROUP BY c.id, c.name
HAVING SUM(o.total_amount) > 100
ORDER BY total_spend DESC;
```

**Why `HAVING` and not `WHERE` here?**

`WHERE` runs before grouping — it can't see aggregated values like `SUM(o.total_amount)` because those don't exist yet. `HAVING` runs after `GROUP BY`, once the aggregation is complete, so it can filter on the result of `SUM()`.

Rule of thumb:
- Filter on raw column values → `WHERE`
- Filter on the result of an aggregate function → `HAVING`

Expected result: Kwame (225.50) and Kofi (123.00). Ama (89.99) is excluded because her total is below 100.

---

### 29.7 Schema Diagram

```
categories          products
──────────          ────────────────────
id (PK)    ←──┐    id (PK)
name            └── category_id (FK)
created_at          name
                    price
                    stock_qty
                    is_active
                    created_at

customers           orders              order_items
─────────           ──────              ───────────
id (PK)    ←───┐   id (PK)    ←───┐   id (PK)
name            └── customer_id(FK) │   order_id (FK) ──┘
email               total_amount    │   product_id (FK) ──→ products.id
region              status          └── quantity
created_at          created_at          unit_price
```

---

### 29.8 Key Concepts Demonstrated by These Questions

| Question | Core Concept |
|---|---|
| Q1 | SELECT *, basic retrieval |
| Q2 | Column aliases with AS |
| Q3 | ORDER BY DESC |
| Q4 | ORDER BY + LIMIT |
| Q5–Q8 | Arithmetic in SELECT, ROUND() |
| Q9 | BETWEEN for range filtering |
| Q10 | String equality in WHERE |
| Q11 | IN with JOIN |
| Q12 | LIKE with wildcards |
| Q13 | CASE for conditional labelling |
| Q14 | INNER JOIN, table aliases |
| Q15 | JOIN + WHERE filter |
| Q16 | Multi-table (4-way) JOIN |
| Q17 | Can't use alias in WHERE — repeat expression |
| Q18 | LEFT JOIN to include zero-count groups |
| Q19 | Multiple aggregates in one GROUP BY |
| Q20 | WHERE vs JOIN condition for outer join |
| Q21 | HAVING for filtering aggregated results |

---

---

## 30. Natural Joins

### 30.1 What Natural Joins Are

A natural join automatically joins tables on all columns that share the same name and compatible data type — no explicit `ON` clause required. The database figures out the join condition for you.

```sql
-- Natural join: automatically joins on any columns with the same name
SELECT a.account_id, a.cust_id, c.city
FROM account a
NATURAL JOIN customer c;
-- Equivalent to: JOIN customer c ON c.cust_id = a.cust_id
-- (assuming cust_id is the only shared column name)
```

### 30.2 Why Natural Joins Are Dangerous

Natural joins look convenient but are a trap in real applications. The problem is that the join condition is **implicit** — it depends on column naming conventions that can change without warning.

```sql
-- If you add a column called "status" to both account and customer:
-- account.status = 'ACTIVE'
-- customer.status = 'VIP'
-- Your natural join now silently adds AND a.status = c.status
-- This is a bug, not a feature
```

**Avoid natural joins in production code.** Always be explicit with `ON` or `USING`. Natural joins make code fragile, hard to read, and prone to silent breakage when schemas change.

The only legitimate use case is in quickly exploring schemas you don't know well — never in code that goes to production.

---

## 31. Multicolumn Subqueries

### 31.1 The Problem They Solve

Sometimes you need to check multiple columns against a subquery simultaneously. Instead of two separate single-column subqueries, you can use a multicolumn subquery with tuple comparison.

```sql
-- Two separate single-column subqueries (more verbose):
SELECT account_id, product_cd, cust_id
FROM account
WHERE open_branch_id = (SELECT branch_id FROM branch WHERE name = 'Woburn Branch')
  AND open_emp_id IN (
      SELECT emp_id FROM employee
      WHERE title = 'Teller' OR title = 'Head Teller'
  );

-- One multicolumn subquery (more concise):
SELECT account_id, product_cd, cust_id
FROM account
WHERE (open_branch_id, open_emp_id) IN (
    SELECT b.branch_id, e.emp_id
    FROM branch b
    JOIN employee e ON b.branch_id = e.assigned_branch_id
    WHERE b.name = 'Woburn Branch'
      AND (e.title = 'Teller' OR e.title = 'Head Teller')
);
```

The column list on the left `(open_branch_id, open_emp_id)` is matched against pairs of values returned by the subquery. A row passes the filter only if both columns match a row in the subquery's result.

### 31.2 Multicolumn Subquery for Data Integrity Checking

A practical use: verify that two related columns in a table are consistent with what's in another table.

```sql
-- Check for accounts whose available/pending balance doesn't match transactions
SELECT account_id
FROM account a
WHERE (a.avail_balance, a.pending_balance) <> (
    SELECT
        SUM(CASE WHEN txn_type_cd = 'CDT' THEN amount ELSE -amount END),
        SUM(CASE WHEN txn_type_cd = 'CDT' AND funds_avail_date > NOW()
                 THEN amount ELSE 0 END)
    FROM transaction t
    WHERE t.account_id = a.account_id
);
```

### 31.3 Rules for Multicolumn Subqueries

- The number of columns in the tuple on the left must match the number of columns returned by the subquery
- Column order matters — the first column on the left matches the first column from the subquery
- Works with `IN`, `NOT IN`, and `=` (if subquery returns exactly one row)
- Does not work with `>`, `<`, `>=`, `<=` — those require scalar comparisons

---

## 32. Subqueries As Expression Generators

### 32.1 Scalar Subqueries in SELECT

A scalar subquery (returns one row, one column) can appear anywhere a single value expression is valid — including the SELECT list itself. This is useful when you want to annotate each row with data from another table without a full join.

```sql
-- Retrieve each employee along with their department name and branch name
-- using correlated scalar subqueries — no joins needed
SELECT
    e.emp_id,
    CONCAT(e.fname, ' ', e.lname) AS employee_name,
    (SELECT d.name FROM department d WHERE d.dept_id = e.dept_id) AS dept_name,
    (SELECT b.name FROM branch b WHERE b.branch_id = e.assigned_branch_id) AS branch_name
FROM employee e;
```

Each scalar subquery runs once per row of the outer query (correlated). The trade-off is that this can be slower than a join when the outer table has many rows, because the subqueries are executed row by row.

### 32.2 Scalar Subqueries in ORDER BY

Scalar subqueries can also appear in the `ORDER BY` clause — allowing you to sort by a value that requires a lookup:

```sql
-- Sort employees by their manager's last name, then by their own last name
SELECT
    e.emp_id,
    CONCAT(e.fname, ' ', e.lname) AS employee_name,
    (SELECT CONCAT(mgr.fname, ' ', mgr.lname)
     FROM employee mgr
     WHERE mgr.emp_id = e.superior_emp_id) AS manager_name
FROM employee e
WHERE e.superior_emp_id IS NOT NULL
ORDER BY
    (SELECT mgr.lname FROM employee mgr WHERE mgr.emp_id = e.superior_emp_id),
    e.lname;
```

### 32.3 Scalar Subqueries in INSERT VALUES

Subqueries can look up foreign key values when inserting rows — avoiding the need to run separate lookup queries first:

```sql
-- Insert an account row by looking up all foreign key values by name
INSERT INTO account
    (product_cd, cust_id, open_date, status, open_branch_id, open_emp_id, avail_balance)
VALUES (
    (SELECT product_cd FROM product WHERE name = 'savings account'),
    (SELECT cust_id FROM customer WHERE fed_id = '555-55-5555'),
    NOW(),
    'ACTIVE',
    (SELECT branch_id FROM branch WHERE name = 'Quincy Branch'),
    (SELECT emp_id FROM employee WHERE lname = 'Portman' AND fname = 'Frank'),
    0
);
```

> **Warning:** If any subquery returns no rows (e.g. a typo in the name), the column receives NULL. The insert will succeed if the column allows NULL, silently producing bad data. Validate lookups separately when data integrity matters.

### 32.4 Subqueries in HAVING

Subqueries can appear in the `HAVING` clause to filter groups based on an aggregate compared to another aggregate from a subquery:

```sql
-- Find the employee who opened the most accounts
SELECT open_emp_id, COUNT(*) AS how_many
FROM account
GROUP BY open_emp_id
HAVING COUNT(*) = (
    SELECT MAX(emp_cnt.how_many)
    FROM (
        SELECT COUNT(*) AS how_many
        FROM account
        GROUP BY open_emp_id
    ) emp_cnt
);
```

The inner subquery finds the maximum account-open count across all employees. The outer `HAVING` clause then keeps only the employee(s) who match that maximum.

---

## 33. Data Fabrication with Subqueries

### 33.1 Generating Data That Doesn't Exist in Tables

One of the most powerful uses of subqueries is to generate data on the fly — using `UNION ALL` to create virtual tables that are then joined to real data. This avoids cluttering the database with small special-purpose tables.

### 33.2 Customer Grouping Example

Suppose you want to bucket customers into spending tiers (Small Fry, Average Joes, Heavy Hitters) without storing those tiers anywhere. Build them inline:

```sql
-- Step 1: Define the tiers as a subquery
SELECT 'Small Fry'     AS name, 0       AS low_limit, 4999.99    AS high_limit
UNION ALL
SELECT 'Average Joes'  AS name, 5000    AS low_limit, 9999.99    AS high_limit
UNION ALL
SELECT 'Heavy Hitters' AS name, 10000   AS low_limit, 9999999.99 AS high_limit;

-- Step 2: Use it as a joined table
SELECT
    grp.name    AS tier,
    COUNT(*)    AS num_customers
FROM (
    -- Total deposit balance per customer
    SELECT SUM(avail_balance) AS cust_balance
    FROM account
    GROUP BY cust_id
) cust_rollup
JOIN (
    SELECT 'Small Fry'     name, 0       low_limit, 4999.99    high_limit
    UNION ALL
    SELECT 'Average Joes'  name, 5000    low_limit, 9999.99    high_limit
    UNION ALL
    SELECT 'Heavy Hitters' name, 10000   low_limit, 9999999.99 high_limit
) grp
ON cust_rollup.cust_balance BETWEEN grp.low_limit AND grp.high_limit
GROUP BY grp.name;
```

The fabricated `grp` table is joined to real aggregated data using a range condition. No permanent table needed.

### 33.3 Generating Number Series with UNION ALL

Before `generate_series()` was available (or in databases that don't have it), a cross join of fabricated number sets was the standard way to generate a sequence:

```sql
-- Generate numbers 1–100 using cross join of two fabricated sets
SELECT ones.x + tens.x + 1 AS n
FROM (
    SELECT 0 x UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3
    UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6
    UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9
) ones
CROSS JOIN (
    SELECT 0 x  UNION ALL SELECT 10 UNION ALL SELECT 20 UNION ALL SELECT 30
    UNION ALL SELECT 40 UNION ALL SELECT 50 UNION ALL SELECT 60
    UNION ALL SELECT 70 UNION ALL SELECT 80 UNION ALL SELECT 90
) tens
ORDER BY n;
```

The ones table (0–9) cross-joined with the tens table (0, 10, 20...90) produces 100 combinations. Adding 1 shifts the range from 0–99 to 1–100.

### 33.4 Experience Level Classification

A real pattern: join real data to a fabricated lookup table using range conditions:

```sql
-- Classify employees by their start date into experience bands
SELECT
    e.emp_id,
    e.fname,
    e.lname,
    levels.name AS experience_level
FROM employee e
JOIN (
    SELECT 'trainee' AS name, '2004-01-01' AS start_dt, '2005-12-31' AS end_dt
    UNION ALL
    SELECT 'worker',          '2002-01-01',              '2003-12-31'
    UNION ALL
    SELECT 'mentor',          '2000-01-01',              '2001-12-31'
) levels
ON e.start_date BETWEEN levels.start_dt AND levels.end_dt;
```

This pattern eliminates the need for a permanent `experience_levels` table that would only be used for this one query.

---

## 34. Metadata and information_schema

### 34.1 What Metadata Is

Metadata is data about data — information about the structure of your database: table names, column names and types, constraints, indexes, views. Every major database server stores this in a standard location called `information_schema`.

### 34.2 The information_schema Database

`information_schema` is a virtual database containing views that describe the database's structure. You query it just like any other table — but it's read-only and generated dynamically by the database engine.

```sql
-- Key views in information_schema
information_schema.tables          -- all tables and views
information_schema.columns         -- all columns in all tables
information_schema.statistics      -- all indexes
information_schema.table_constraints  -- all constraints (PK, FK, UNIQUE, CHECK)
information_schema.referential_constraints  -- foreign key relationships
information_schema.views           -- all view definitions
information_schema.routines        -- stored procedures and functions
```

### 34.3 Querying Metadata

```sql
-- List all tables in a specific database/schema
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'your_database'
ORDER BY table_name;

-- Describe a table's columns programmatically
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'your_database'
  AND table_name = 'users'
ORDER BY ordinal_position;

-- List all indexes in a schema
SELECT DISTINCT table_name, index_name
FROM information_schema.statistics
WHERE table_schema = 'your_database'
ORDER BY table_name, index_name;

-- List all foreign keys
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'your_database';

-- Count objects in a schema
SELECT
    COUNT(*) FILTER (WHERE table_type = 'BASE TABLE') AS tables,
    COUNT(*) FILTER (WHERE table_type = 'VIEW') AS views
FROM information_schema.tables
WHERE table_schema = 'your_database';
```

### 34.4 Deployment Verification

Metadata queries are useful for verifying that a schema is correctly deployed — checking that all expected tables, columns, and indexes exist before running application code:

```sql
-- Verify all required tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'your_database'
  AND table_name IN ('users', 'orders', 'products', 'order_items')
ORDER BY table_name;
-- If any required table is missing, it won't appear in the result

-- Verify specific columns exist with the right types
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'your_database'
  AND table_name = 'orders'
  AND column_name IN ('id', 'user_id', 'total', 'status', 'created_at');

-- Find any indexes on a specific table
SELECT index_name, column_name, non_unique
FROM information_schema.statistics
WHERE table_schema = 'your_database'
  AND table_name = 'orders'
ORDER BY index_name, seq_in_index;
```

### 34.5 Schema Generation Scripts

You can use metadata to generate DDL scripts programmatically — useful for documentation, migrations, or recreating a schema:

```sql
-- Generate ALTER TABLE statements to recreate indexes on a table
SELECT CONCAT(
    'ALTER TABLE ',
    table_name,
    ' ADD ',
    CASE WHEN non_unique = 0 THEN 'UNIQUE ' ELSE '' END,
    'INDEX ',
    index_name,
    ' (',
    GROUP_CONCAT(column_name ORDER BY seq_in_index),
    ');'
) AS index_statement
FROM information_schema.statistics
WHERE table_schema = 'your_database'
  AND table_name = 'employees'
  AND index_name <> 'PRIMARY'   -- skip the primary key
GROUP BY table_name, index_name, non_unique;
```

### 34.6 PostgreSQL-Specific Metadata Views

PostgreSQL has its own system catalog alongside `information_schema`:

```sql
-- pg_tables — tables with owner info
SELECT schemaname, tablename, tableowner FROM pg_tables WHERE schemaname = 'public';

-- pg_indexes — indexes with definition
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'users';

-- pg_stat_user_tables — table usage statistics
SELECT relname, seq_scan, idx_scan, n_live_tup FROM pg_stat_user_tables;

-- pg_stat_user_indexes — index usage statistics
SELECT relname, indexrelname, idx_scan FROM pg_stat_user_indexes;
-- idx_scan = 0 after running for a while → index may be unused and wasteful
```

---

## 35. Dynamic SQL Generation

### 35.1 What Dynamic SQL Is

Dynamic SQL means building and executing SQL statements as strings at runtime — the query text is constructed programmatically, not hardcoded. This is necessary when the structure of the query (table names, column names, number of conditions) isn't known until runtime.

### 35.2 Use Cases

- **Schema generation** — generating DDL based on metadata queries
- **Generic reporting tools** — building queries from user-selected filters, columns, and sorting
- **Database administration** — applying the same operation across many tables
- **Migration scripts** — running table-by-table operations

### 35.3 MySQL Dynamic SQL with PREPARE

```sql
-- Build and execute a dynamic SQL string in MySQL

-- Step 1: Build the SQL as a string into a user variable
SET @sql = CONCAT(
    'SELECT * FROM ',
    'users',              -- could be a variable
    ' WHERE status = ? LIMIT 10'
);

-- Step 2: Prepare the statement
PREPARE stmt FROM @sql;

-- Step 3: Execute it (bind parameters with USING)
SET @status = 'active';
EXECUTE stmt USING @status;

-- Step 4: Deallocate when done
DEALLOCATE PREPARE stmt;
```

### 35.4 Dynamic SQL in Application Code

In most real applications, dynamic SQL is built in the application layer (not in the DB), using parameterised queries to prevent SQL injection:

```javascript
// Node.js (pg library) — dynamic column selection with safe parameterisation
const columns = ['id', 'email', 'status'];  // validated whitelist
const query = `SELECT ${columns.join(', ')} FROM users WHERE status = $1`;
const result = await client.query(query, ['active']);
```

```python
# Python — dynamic table name (must be validated, cannot be parameterised)
table = 'orders'  # validated against a whitelist
cursor.execute(f'SELECT * FROM {table} WHERE status = %s', ('pending',))
```

> **Security rule:** Parameter values can always be safely parameterised (bound variables). Table names and column names cannot — they must be validated against a whitelist before being interpolated into a query string. Never interpolate user-supplied strings directly into SQL.

### 35.5 Generating DDL from Metadata

A practical example from the book: generating `ALTER TABLE ADD INDEX` statements for all indexes on a table, using metadata:

```sql
SELECT CONCAT(
    CASE
        WHEN seq_in_index = 1 THEN
            CONCAT(
                'ALTER TABLE ', table_name, ' ADD ',
                CASE WHEN non_unique = 0 THEN 'UNIQUE ' ELSE '' END,
                'INDEX ', index_name, ' (', column_name
            )
        ELSE CONCAT(' , ', column_name)
    END,
    CASE
        WHEN seq_in_index = (
            SELECT MAX(s2.seq_in_index)
            FROM information_schema.statistics s2
            WHERE s2.table_schema = s.table_schema
              AND s2.table_name   = s.table_name
              AND s2.index_name   = s.index_name
        ) THEN ');'
        ELSE ''
    END
) AS ddl_statement
FROM information_schema.statistics s
WHERE table_schema = 'your_database'
  AND table_name   = 'employee'
ORDER BY index_name, seq_in_index;
```

The output is a series of SQL strings that could be copied and re-run on another server to recreate the same index structure.

---

## 36. Storage Engines and Locking Granularities

### 36.1 Storage Engines (MySQL-Specific)

MySQL allows different tables in the same database to use different storage engines — each with different capabilities around transactions, locking, and performance. This concept doesn't exist in PostgreSQL, which has one engine.

**InnoDB** — The default and recommended engine. Supports transactions, foreign keys, row-level locking, crash recovery, and MVCC (Multi-Version Concurrency Control). Use for almost everything.

**MyISAM** — Older engine. No transactions, no foreign keys, table-level locking only. Fast for read-heavy workloads with no concurrency needs. Largely superseded by InnoDB.

**Memory (HEAP)** — Stores tables entirely in RAM. Extremely fast reads and writes. Data is lost on server restart. Use for temporary working sets or caching.

**Falcon** — Was a newer transactional engine being developed when the book was written. No longer actively developed.

```sql
-- Create a table with a specific storage engine
CREATE TABLE cache_data (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    expires_at DATETIME
) ENGINE = MEMORY;

-- Check which engine a table uses
SHOW CREATE TABLE orders;

-- Change a table's storage engine
ALTER TABLE old_table ENGINE = InnoDB;

-- See all available storage engines
SHOW ENGINES;
```

### 36.2 Locking Granularities

Locks prevent concurrent transactions from interfering with each other. The tradeoff: finer-grained locks allow more concurrency but use more memory; coarser locks are simpler but block more operations.

**Table locks** — Lock the entire table. Any write blocks all other reads and writes on the table. Very simple, very low overhead, but very restrictive concurrency. Used by MyISAM.

**Page locks** — Lock a page of disk (typically 8–16KB containing multiple rows). A middle ground between table and row locks. Less common in modern systems.

**Row locks** — Lock individual rows. Multiple transactions can work on different rows of the same table simultaneously. Higher memory overhead, much better concurrency. Used by InnoDB.

```
Coarser locks ←————————————————→ Finer locks
Table locks        Page locks        Row locks
Low overhead       Middle            High overhead
Low concurrency    Middle            High concurrency
```

### 36.3 Lock Types Within a Granularity

At any granularity level, locks come in two types:

**Read lock (shared lock)** — Multiple transactions can hold a read lock on the same resource simultaneously. Blocked by write locks.

**Write lock (exclusive lock)** — Only one transaction can hold a write lock. Blocks all other read and write locks.

```sql
-- Explicit locking in MySQL
LOCK TABLES users READ;           -- Shared lock on entire table
LOCK TABLES users WRITE;          -- Exclusive lock on entire table
UNLOCK TABLES;

-- Row-level locking in InnoDB (within a transaction)
BEGIN;
SELECT * FROM accounts WHERE id = 42 FOR UPDATE;   -- Exclusive row lock
UPDATE accounts SET balance = balance - 100 WHERE id = 42;
COMMIT;
```

### 36.4 Deadlocks

A deadlock occurs when two transactions each hold a lock the other needs — they wait for each other indefinitely. The database detects this and kills one transaction (the "deadlock victim"), which is rolled back. The other transaction proceeds.

```
Transaction A                    Transaction B
LOCK row 1                       LOCK row 2
Wait for row 2...     ←→        Wait for row 1...
                   DEADLOCK
```

To avoid deadlocks: always acquire locks in the same order across all transactions. If transaction A always locks row 1 before row 2, and transaction B does the same, they can never deadlock.

### 36.5 MVCC — Multi-Version Concurrency Control

InnoDB (and PostgreSQL) use MVCC instead of simple locks for reads. Each transaction sees a snapshot of the database as it existed at the start of the transaction — it doesn't see changes committed by other transactions after it started.

This means readers don't block writers and writers don't block readers. The database maintains multiple versions of each row and each transaction reads the appropriate version based on its isolation level and start time.

This is why `READ COMMITTED` in PostgreSQL shows committed changes made after your query started (it takes a snapshot per statement), while `REPEATABLE READ` shows the same data throughout the entire transaction (snapshot taken at transaction start).

---

## 37. Multicolumn Grouping and Rollups — Deep Reference

### 37.1 Multicolumn Grouping

You can group by any number of columns simultaneously. The result has one row per unique combination of all grouped columns.

```sql
-- Total balance by product type and branch
SELECT
    product_cd,
    open_branch_id,
    SUM(avail_balance) AS tot_balance
FROM account
GROUP BY product_cd, open_branch_id
ORDER BY product_cd, open_branch_id;
-- Returns one row per (product, branch) combination
```

If a product exists in 3 branches and there are 6 products, you get up to 18 rows — one for each combination that actually exists in the data.

### 37.2 WITH ROLLUP (MySQL syntax)

`WITH ROLLUP` adds subtotal rows automatically — one for each grouping level, plus a grand total.

```sql
SELECT
    product_cd,
    open_branch_id,
    SUM(avail_balance) AS tot_balance
FROM account
GROUP BY product_cd, open_branch_id WITH ROLLUP;
```

Result includes:
- Normal rows: `(product_cd, open_branch_id)` — individual combinations
- Subtotal rows: `(product_cd, NULL)` — total per product across all branches
- Grand total row: `(NULL, NULL)` — total across everything

The `NULL` in a subtotal row means "this value was rolled up across all values of this column". To distinguish rollup NULLs from actual NULLs in the data, use `GROUPING()`:

```sql
SELECT
    CASE WHEN GROUPING(product_cd) = 1 THEN 'ALL PRODUCTS' ELSE product_cd END AS product,
    CASE WHEN GROUPING(open_branch_id) = 1 THEN 'ALL BRANCHES' ELSE CAST(open_branch_id AS CHAR) END AS branch,
    SUM(avail_balance) AS tot_balance
FROM account
GROUP BY product_cd, open_branch_id WITH ROLLUP;
```

### 37.3 ROLLUP in Oracle and PostgreSQL Syntax

```sql
-- Oracle and PostgreSQL syntax (different from MySQL WITH ROLLUP)
GROUP BY ROLLUP (product_cd, open_branch_id)

-- Partial rollup — only roll up on a subset of columns
GROUP BY product_cd, ROLLUP (open_branch_id)
-- Adds subtotals per product, but not the grand total

-- Standard SQL syntax (PostgreSQL, Oracle, SQL Server)
GROUP BY GROUPING SETS (
    (product_cd, open_branch_id),   -- detail rows
    (product_cd),                    -- subtotals by product
    ()                               -- grand total
)
-- ROLLUP is shorthand for this GROUPING SETS pattern
```

### 37.4 WITH CUBE

`WITH CUBE` is like `ROLLUP` but generates subtotals for **every possible combination** of the grouped columns, not just the hierarchical rollup.

For grouping by `(product_cd, open_branch_id)`, `ROLLUP` gives:
- `(product, branch)` — detail
- `(product, NULL)` — subtotal per product
- `(NULL, NULL)` — grand total

`CUBE` additionally gives:
- `(NULL, branch)` — subtotal per branch (across all products)

```sql
-- SQL Server / Oracle (MySQL doesn't fully support CUBE in older versions)
SELECT product_cd, open_branch_id, SUM(avail_balance)
FROM account
GROUP BY CUBE (product_cd, open_branch_id);

-- PostgreSQL syntax
GROUP BY CUBE (product_cd, open_branch_id)
```

Use `CUBE` when you need all possible subtotal combinations — for example, in a report where users can drill down by either product or branch independently.

### 37.5 Aggregate Functions in HAVING Without SELECT

You can filter groups in `HAVING` using aggregate functions that don't appear in the `SELECT` list:

```sql
-- Find products where the minimum balance is at least 1000
-- AND the maximum balance is no more than 10000
-- The MIN and MAX don't have to appear in the SELECT
SELECT product_cd, SUM(avail_balance) AS prod_balance
FROM account
WHERE status = 'ACTIVE'
GROUP BY product_cd
HAVING MIN(avail_balance) >= 1000
   AND MAX(avail_balance) <= 10000;
```

The `HAVING` clause can reference any aggregate function, whether or not it appears in the SELECT. This is useful when you need to filter on an aggregate condition that you don't want to surface in the output.

---

*Last updated: 2026 — Built from real query writing experience across analytics, APIs, and production systems. Supplemented with concepts from Alan Beaulieu's Learning SQL (O'Reilly, 2nd ed.).*
