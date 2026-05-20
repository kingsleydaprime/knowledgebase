# Database Design — Comprehensive Reference Guide

> A deep reference covering relational database design from first principles.
> Covers data modelling, relationships, normalisation, keys, constraints,
> indexing strategy, multi-tenancy, schema patterns, and real-world design decisions.
> The Postgres reference builds on top of this — understand design before optimisation.

---

## Table of Contents

1. [How Relational Databases Think](#1-how-relational-databases-think)
2. [Entities and Attributes](#2-entities-and-attributes)
3. [Keys — Primary, Foreign, and Composite](#3-keys--primary-foreign-and-composite)
4. [Relationships — The Core of Data Modelling](#4-relationships--the-core-of-data-modelling)
5. [Cardinality — One-to-One, One-to-Many, Many-to-Many](#5-cardinality--one-to-one-one-to-many-many-to-many)
6. [Junction Tables — Modelling Many-to-Many](#6-junction-tables--modelling-many-to-many)
7. [Normalisation — The Rules for Clean Schema Design](#7-normalisation--the-rules-for-clean-schema-design)
8. [Denormalisation — When to Break the Rules](#8-denormalisation--when-to-break-the-rules)
9. [Data Types — Choosing the Right One](#9-data-types--choosing-the-right-one)
10. [Constraints — Enforcing Integrity at the Database Level](#10-constraints--enforcing-integrity-at-the-database-level)
11. [Indexes — Design Strategy](#11-indexes--design-strategy)
12. [Entity-Relationship Diagrams (ERD)](#12-entity-relationship-diagrams-erd)
13. [Common Schema Patterns](#13-common-schema-patterns)
14. [Multi-Tenancy Patterns](#14-multi-tenancy-patterns)
15. [Audit Trails and Soft Deletes](#15-audit-trails-and-soft-deletes)
16. [Hierarchical and Recursive Data](#16-hierarchical-and-recursive-data)
17. [Polymorphic Relationships](#17-polymorphic-relationships)
18. [Schema Versioning and Migrations](#18-schema-versioning-and-migrations)
19. [Real-World Schema Examples](#19-real-world-schema-examples)
20. [Design Checklist](#20-design-checklist)

---

## 1. How Relational Databases Think

### 1.1 The Relational Model

A relational database organises data into **tables** (also called relations). Each table has:
- A fixed set of **columns** (attributes) — the structure
- A variable number of **rows** (tuples) — the data

The relational model was invented by Edgar Codd in 1970. The core insight: data should be stored in a way that is independent of how it will be accessed. You describe *what* you want, not *how* to get it — that's what SQL is for.

Every table represents a single concept. The relationships between concepts are expressed through keys, not through nesting or embedding. This is fundamentally different from document databases (MongoDB) where related data is often embedded together.

### 1.2 Why Relational Design Matters

A poorly designed schema is one of the hardest problems to fix in production. Changing a schema under load risks data loss, downtime, and application bugs. The cost of a schema change grows exponentially with the amount of data and the number of applications reading that data.

Getting the design right up front — or as right as possible — is one of the highest-leverage things you can do on a backend project.

**Signs of a poorly designed schema:**
- The same data appears in multiple places and gets out of sync
- Adding a new feature requires changing many tables
- Queries require multiple joins just to get basic information
- Columns that are usually NULL (storing different things for different rows)
- Columns named `data1`, `data2`, `extra_field` (catch-all columns)
- Storing comma-separated values in a single column

### 1.3 ACID — The Guarantees a Relational DB Makes

**Atomicity** — A transaction either fully completes or fully fails. If you're transferring money from A to B, you can't deduct from A without crediting B.

**Consistency** — The database moves from one valid state to another. Constraints are always enforced. Foreign keys always point to existing rows.

**Isolation** — Concurrent transactions don't see each other's partial states. Two users reading the same row at the same time get consistent results.

**Durability** — Once a transaction is committed, it survives crashes, power failures, and restarts.

These guarantees are what make relational databases appropriate for financial data, user accounts, inventory, and anything where correctness matters more than raw speed.

---

## 2. Entities and Attributes

### 2.1 Entities

An **entity** is a distinct thing in your domain that you need to store data about. It becomes a table.

Identifying entities: look for nouns in your requirements.

```
"Users can place orders for products. Each order has multiple items.
 Products belong to categories. Users have addresses."

Entities:
- User
- Order
- OrderItem
- Product
- Category
- Address
```

### 2.2 Attributes

An **attribute** is a property of an entity. It becomes a column.

```
User:
- id
- email
- password_hash
- first_name
- last_name
- created_at
- updated_at

Product:
- id
- name
- description
- price
- stock_quantity
- category_id
- created_at
```

### 2.3 Choosing What Deserves Its Own Table

The key question: **does this thing have its own existence independent of the entity it's attached to?**

```
User has one address  →  is address just attributes on user, or its own table?

If a user can only ever have one address → columns on users table (keep it simple)
If a user can have multiple addresses → address table with user_id foreign key
If addresses are shared between users (e.g. office buildings) → separate table
If you need to store address history → separate table with timestamps
```

Another signal: **does this thing have attributes of its own?**

```
A user has a "role" → if role is just a string (admin/user), it's a column
                    → if roles have permissions, descriptions, hierarchy → it's a table
```

---

## 3. Keys — Primary, Foreign, and Composite

### 3.1 Primary Keys

A primary key uniquely identifies each row in a table. Rules:
- Must be unique across all rows
- Must never be NULL
- Should never change once set (immutable)
- Should be meaningless to the business (surrogate key) — not a phone number, email, or anything that could change

**Surrogate key options:**

**Auto-incrementing integer (SERIAL / BIGSERIAL)**
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL
);
```
Pros: small (8 bytes), fast index, ordered by insertion time, human-readable in URLs.
Cons: predictable (sequential IDs expose record counts, allow scraping), single point of generation (hard to generate offline or in distributed systems).

**UUID (Universally Unique Identifier)**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL
);
```
Pros: globally unique (can generate anywhere without DB round-trip), non-sequential (no business intelligence leakage), good for distributed systems and merging databases.
Cons: larger (16 bytes vs 8), random UUIDs (v4) cause index fragmentation (inserts go to random positions), not human-friendly in URLs.

**ULID (Universally Unique Lexicographically Sortable Identifier)**
A modern alternative: 128-bit like UUID but time-ordered. Combines UUID's global uniqueness with BIGSERIAL's insertion order. Use when you want UUID benefits without index fragmentation.

**The recommendation:**
- Small to medium projects: `BIGSERIAL` — simple, fast, works well
- Distributed systems, public APIs, multi-tenant: `UUID` with `gen_random_uuid()`
- High-write systems where UUID index fragmentation matters: ULID or UUID v7 (time-ordered)

### 3.2 Foreign Keys

A foreign key is a column (or set of columns) that references the primary key of another table. It enforces **referential integrity** — you cannot have a row that references a non-existent row.

```sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    -- user_id must exist in users.id
    -- you cannot insert an order for a non-existent user
    total NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**ON DELETE behaviour** — what happens to child rows when the parent is deleted:

```sql
-- Error: prevent deletion of parent if children exist (default)
user_id BIGINT REFERENCES users(id) ON DELETE RESTRICT

-- Also prevents deletion but deferred to end of transaction
user_id BIGINT REFERENCES users(id) ON DELETE NO ACTION

-- Delete child rows when parent is deleted (cascade)
user_id BIGINT REFERENCES users(id) ON DELETE CASCADE

-- Set foreign key to NULL when parent deleted
user_id BIGINT REFERENCES users(id) ON DELETE SET NULL

-- Set foreign key to default value when parent deleted
user_id BIGINT REFERENCES users(id) ON DELETE SET DEFAULT
```

**ON UPDATE behaviour** — what happens when the parent's primary key changes (rare if using surrogate keys):

```sql
user_id BIGINT REFERENCES users(id) ON UPDATE CASCADE
```

**Choosing ON DELETE behaviour:**

| Relationship | ON DELETE |
|---|---|
| Order → User | RESTRICT (don't delete users with orders) |
| OrderItem → Order | CASCADE (deleting an order deletes its items) |
| Post → Author (optional) | SET NULL (post stays, author reference cleared) |
| Session → User | CASCADE (delete sessions when user is deleted) |
| Profile → User | CASCADE (profile is owned by user) |

### 3.3 Composite Keys

A composite primary key uses multiple columns together to uniquely identify a row.

```sql
-- Junction table for user-role assignments
CREATE TABLE user_roles (
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    role_id BIGINT REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id)  -- composite PK: each user-role pair is unique
);
```

Composite keys are natural for junction tables and tables where the identity is defined by a combination of foreign keys.

**Composite keys vs surrogate keys in junction tables:**

```sql
-- Option A: composite primary key (natural)
CREATE TABLE user_roles (
    user_id BIGINT REFERENCES users(id),
    role_id BIGINT REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

-- Option B: surrogate key + unique constraint
CREATE TABLE user_roles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    role_id BIGINT REFERENCES roles(id),
    UNIQUE (user_id, role_id)
);
```

Option B is preferred when:
- The junction table has its own attributes (assigned_at, assigned_by)
- Other tables reference the junction table by ID
- Your ORM handles it more easily

Option A is preferred when:
- The junction table is purely relational (just the two FKs)
- You want to enforce uniqueness at the PK level directly

---

## 4. Relationships — The Core of Data Modelling

### 4.1 What a Relationship Is

A relationship defines how two entities connect to each other. In a relational database, relationships are implemented through foreign keys — one table holds a column that references the primary key of another.

The three dimensions of every relationship:
1. **Cardinality** — how many of each side can exist (one-to-one, one-to-many, many-to-many)
2. **Optionality** — is the relationship required or optional (nullable vs NOT NULL foreign key)
3. **Direction** — which table holds the foreign key

### 4.2 Optionality

```sql
-- Required relationship (NOT NULL) — every order must have a user
user_id BIGINT NOT NULL REFERENCES users(id)

-- Optional relationship (nullable) — a post may or may not have an author
author_id BIGINT REFERENCES users(id)   -- NULL means "no author assigned"
```

The optionality should reflect the real business rule. If "every order must belong to a user" is a business rule, enforce it with NOT NULL — don't leave it to the application layer.

---

## 5. Cardinality — One-to-One, One-to-Many, Many-to-Many

### 5.1 One-to-One (1:1)

One row in table A corresponds to exactly one row in table B, and vice versa.

**When to use:**
- Splitting a table with many columns into two for performance (large optional fields)
- Storing sensitive data separately with different access controls
- Extending a table you can't modify (e.g., a third-party table)
- Optional extension data that only some rows have

```sql
-- User and UserProfile: every user has one profile, every profile belongs to one user
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- UNIQUE on user_id enforces the 1:1 — only one profile per user
    bio TEXT,
    avatar_url TEXT,
    website TEXT,
    location TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Implementation options:**

```sql
-- Option A: Separate table with unique FK (above) — most flexible
-- Option B: Shared primary key — profile.id IS the user.id
CREATE TABLE user_profiles (
    user_id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    -- user_id is both PK and FK — strongest 1:1 enforcement
    bio TEXT,
    avatar_url TEXT
);

-- Option C: Just put the columns on the users table
-- Use when: the data is always present and not sensitive
ALTER TABLE users ADD COLUMN bio TEXT;
ALTER TABLE users ADD COLUMN avatar_url TEXT;
```

Option C (columns directly on the table) is usually best for simple cases. Use a separate table when the extension data is optional, large, or needs different access controls.

### 5.2 One-to-Many (1:N)

One row in table A corresponds to many rows in table B. This is the most common relationship.

**Implementation:** The "many" side holds the foreign key.

```
User (one) → Orders (many)
The foreign key goes in Orders: orders.user_id → users.id

Category (one) → Products (many)
The foreign key goes in Products: products.category_id → categories.id

Order (one) → OrderItems (many)
The foreign key goes in OrderItems: order_items.order_id → orders.id
```

```sql
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL
);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    category_id BIGINT NOT NULL REFERENCES categories(id),
    -- product belongs to one category; category has many products
    name TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INT NOT NULL DEFAULT 0
);
```

**The foreign key always goes on the "many" side.** This is the fundamental rule of one-to-many.

### 5.3 Many-to-Many (M:N)

Many rows in table A correspond to many rows in table B.

You cannot implement many-to-many directly in SQL — you need a **junction table** (also called a join table, bridge table, or associative table) in between.

```
Students ←→ Courses: a student can be enrolled in many courses,
                      a course can have many students

Products ←→ Tags: a product can have many tags,
                   a tag can apply to many products

Users ←→ Roles: a user can have many roles,
                  a role can be assigned to many users
```

See Section 6 for full junction table coverage.

---

## 6. Junction Tables — Modelling Many-to-Many

### 6.1 The Basic Junction Table

```sql
-- Students and courses (many-to-many)
CREATE TABLE students (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

CREATE TABLE courses (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL
);

-- Junction table: enrollments
CREATE TABLE enrollments (
    student_id BIGINT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id BIGINT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (student_id, course_id)  -- a student can only enroll once per course
);
```

### 6.2 Junction Tables with Their Own Attributes

Junction tables often carry data about the relationship itself — not about the student or the course, but about the *enrollment*:

```sql
CREATE TABLE enrollments (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id BIGINT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    -- Attributes of the relationship itself:
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,          -- when did the student finish?
    grade CHAR(2),                     -- what grade did they get?
    enrollment_type TEXT DEFAULT 'standard' CHECK (enrollment_type IN ('standard', 'audit', 'credit')),
    UNIQUE (student_id, course_id)     -- still enforce uniqueness
);
```

When the junction table has its own attributes, it often makes sense to give it a surrogate primary key (the `id BIGSERIAL PRIMARY KEY` above) and a separate `UNIQUE` constraint.

### 6.3 Recognising When You Need a Junction Table

Ask: "Can A have multiple Bs, AND can B have multiple As?"

```
Can a product have multiple tags?     YES
Can a tag apply to multiple products? YES
→ Many-to-many → junction table needed

Can a user have multiple roles?       YES
Can a role be assigned to multiple users? YES
→ Many-to-many → junction table needed

Can a post have multiple authors?     YES (collaborative writing)
Can an author write multiple posts?   YES
→ Many-to-many → junction table needed

Can an order have multiple products?  YES
Can a product appear in multiple orders? YES
→ Many-to-many → order_items junction table
```

### 6.4 Self-Referential Many-to-Many

Sometimes a table has a many-to-many relationship with itself:

```sql
-- Social network: users can follow other users
-- User A follows User B, User B follows User C, etc.

CREATE TABLE follows (
    follower_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (follower_id, following_id),
    CHECK (follower_id != following_id)  -- can't follow yourself
);

-- Query: who does user 1 follow?
SELECT u.* FROM users u
JOIN follows f ON f.following_id = u.id
WHERE f.follower_id = 1;

-- Query: who follows user 1?
SELECT u.* FROM users u
JOIN follows f ON f.follower_id = u.id
WHERE f.following_id = 1;
```

### 6.5 Ordered Many-to-Many

When the order of items in a relationship matters:

```sql
-- Playlist: songs in a playlist have an order
CREATE TABLE playlist_songs (
    playlist_id BIGINT NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    song_id BIGINT NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    position INT NOT NULL,             -- the order of the song in the playlist
    added_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (playlist_id, song_id),
    UNIQUE (playlist_id, position)     -- no two songs at the same position
);

-- Get songs in playlist order
SELECT s.* FROM songs s
JOIN playlist_songs ps ON ps.song_id = s.id
WHERE ps.playlist_id = 42
ORDER BY ps.position;
```

---

## 7. Normalisation — The Rules for Clean Schema Design

### 7.1 What Normalisation Is

Normalisation is a process of organising a database schema to reduce data redundancy and improve data integrity. It's expressed as a series of "normal forms" — each one eliminates a specific class of anomaly.

**The anomalies normalisation prevents:**
- **Update anomaly** — the same data exists in multiple rows; updating one misses another
- **Insert anomaly** — can't insert some data without inserting other unrelated data
- **Delete anomaly** — deleting one row unintentionally deletes other unrelated data

### 7.2 First Normal Form (1NF)

**Rule: Every column must contain atomic (indivisible) values. No repeating groups.**

```sql
-- VIOLATION: storing multiple values in one column
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name TEXT,
    phone_numbers TEXT  -- "0201234567, 0559876543" ← NOT atomic
);

-- VIOLATION: repeating groups
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    product_1 TEXT,
    product_2 TEXT,
    product_3 TEXT    -- what if they order 4 products?
);

-- CORRECT: separate table for phone numbers
CREATE TABLE user_phone_numbers (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    phone_number TEXT NOT NULL,
    type TEXT DEFAULT 'mobile'  -- mobile, home, work
);

-- CORRECT: separate table for order items
CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id),
    quantity INT NOT NULL DEFAULT 1
);
```

**The rule of thumb:** if you ever find yourself storing comma-separated values in a column, or naming columns `thing_1`, `thing_2`, `thing_3` — you're violating 1NF.

### 7.3 Second Normal Form (2NF)

**Rule: Must be in 1NF. Every non-key column must depend on the ENTIRE primary key (no partial dependencies). Only relevant when you have a composite primary key.**

```sql
-- VIOLATION: partial dependency on composite key
-- order_items(order_id, product_id) is the composite PK
-- but product_name depends only on product_id, not the whole PK
CREATE TABLE order_items (
    order_id BIGINT,
    product_id BIGINT,
    quantity INT,
    product_name TEXT,   -- ← depends only on product_id, not on the (order, product) pair
    PRIMARY KEY (order_id, product_id)
);

-- CORRECT: product_name belongs in the products table
CREATE TABLE order_items (
    order_id BIGINT REFERENCES orders(id),
    product_id BIGINT REFERENCES products(id),
    quantity INT NOT NULL,
    PRIMARY KEY (order_id, product_id)
);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL     -- depends entirely on products.id
);
```

### 7.4 Third Normal Form (3NF)

**Rule: Must be in 2NF. Every non-key column must depend on the primary key, not on other non-key columns (no transitive dependencies).**

```sql
-- VIOLATION: transitive dependency
-- zip_code → city (city depends on zip_code, not directly on user_id)
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name TEXT,
    zip_code TEXT,
    city TEXT        -- ← depends on zip_code, not on id (transitive dependency)
);

-- CORRECT: extract zip codes
CREATE TABLE zip_codes (
    zip_code TEXT PRIMARY KEY,
    city TEXT NOT NULL,
    state TEXT NOT NULL
);

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name TEXT,
    zip_code TEXT REFERENCES zip_codes(zip_code)
);
```

Another common 3NF violation:

```sql
-- VIOLATION: department_name depends on department_id, not employee_id
CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    name TEXT,
    department_id INT,
    department_name TEXT  -- ← transitive: id → department_id → department_name
);

-- CORRECT
CREATE TABLE departments (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    name TEXT,
    department_id INT REFERENCES departments(id)
);
```

### 7.5 Boyce-Codd Normal Form (BCNF)

A stricter version of 3NF. For every functional dependency A → B, A must be a superkey (a key or superset of a key). In practice, BCNF issues are rare and the fix usually involves splitting the table.

### 7.6 Fourth Normal Form (4NF) and Beyond

4NF deals with multi-valued dependencies — having two independent one-to-many relationships in the same table. 5NF handles join dependencies. In practice, reaching 3NF (or BCNF) is sufficient for most real-world schemas. 4NF and beyond are academic territory unless you're building very complex systems.

### 7.7 Practical Normalisation Approach

Don't try to enumerate normal forms during design. Instead, ask these questions:

```
1. Is any data repeated in multiple places?
   → If the same city name appears in 10,000 rows, it probably belongs in its own table

2. If I update one piece of data, do I have to update it in multiple places?
   → That's an update anomaly — normalise

3. Does a column depend on the primary key, or on some other column?
   → If on another column, extract it

4. Are any columns usually NULL?
   → NULL often means "this data doesn't apply to this row" — split the table

5. Can I delete a row without losing information that should be separate?
   → If deleting an employee deletes the department info, separate them
```

---

## 8. Denormalisation — When to Break the Rules

### 8.1 Why Denormalise

Normalisation is correct for data integrity, but it requires joins — and joins have a cost. At high read volumes, sometimes the cost of joining many tables on every query outweighs the cost of duplicated data.

**Denormalisation is a deliberate performance optimisation, not a design failure.** The key word is deliberate — you understand the tradeoff and accept the cost of maintaining consistency manually.

### 8.2 Common Denormalisation Patterns

**Storing a computed value to avoid recalculating:**

```sql
-- Normalised: total must be calculated by summing order_items
SELECT SUM(oi.quantity * oi.unit_price) FROM order_items oi WHERE oi.order_id = 42;

-- Denormalised: store the total on the order (must be updated when items change)
ALTER TABLE orders ADD COLUMN total NUMERIC(10, 2);
-- Maintain it with a trigger or application logic
```

**Copying data that rarely changes to avoid a join:**

```sql
-- Normalised: to show order history, join orders → users to get the email
SELECT o.*, u.email FROM orders o JOIN users u ON u.id = o.user_id;

-- Denormalised: snapshot the email at order time
-- (the user might change their email later, but the order was placed with this email)
ALTER TABLE orders ADD COLUMN user_email TEXT;
-- This is actually semantically correct — it's a historical record
```

**Counter caches:**

```sql
-- Normalised: to get a user's post count, COUNT posts
SELECT COUNT(*) FROM posts WHERE user_id = 42;

-- Denormalised: maintain a counter on users
ALTER TABLE users ADD COLUMN posts_count INT DEFAULT 0;
-- Increment on INSERT, decrement on DELETE (via trigger or application)
```

### 8.3 The Denormalisation Rules

1. **Normalise first, denormalise later** — don't denormalise up front. Measure first.
2. **Document every denormalisation** — write a comment explaining why the duplication exists and how it's maintained
3. **Enforce consistency** — use triggers or application-level hooks to keep derived data in sync
4. **Consider materialised views** — often a better alternative (the DB maintains the denormalised view for you)

---

## 9. Data Types — Choosing the Right One

### 9.1 Numeric Types

```sql
-- Integers
SMALLINT        -- 2 bytes, -32768 to 32767
INT / INTEGER   -- 4 bytes, -2.1B to 2.1B
BIGINT          -- 8 bytes, -9.2 quintillion to 9.2 quintillion

-- Auto-incrementing (shorthand)
SERIAL          -- INT with auto-increment sequence
BIGSERIAL       -- BIGINT with auto-increment sequence

-- Exact decimal (for money — NEVER use FLOAT for money)
NUMERIC(precision, scale)  -- NUMERIC(10, 2) = up to 10 digits, 2 after decimal
DECIMAL(p, s)              -- Same as NUMERIC

-- Floating point (for scientific data, never money)
REAL            -- 4 bytes, ~6 decimal digits precision
DOUBLE PRECISION -- 8 bytes, ~15 decimal digits precision
FLOAT           -- alias for DOUBLE PRECISION

-- The golden rule: use NUMERIC for money, INT for quantities
```

**Why FLOAT is wrong for money:**

```sql
-- Floating point arithmetic is imprecise
SELECT 0.1 + 0.2;   -- Returns 0.30000000000000004 in many systems
-- This causes cents to disappear at scale

-- Always use NUMERIC for monetary values:
price NUMERIC(12, 2)   -- Up to 999,999,999.99
amount NUMERIC(19, 4)  -- For high-precision financial calculations
```

### 9.2 Text Types

```sql
-- Postgres-specific recommendation: use TEXT for almost everything
TEXT            -- Variable length, no practical limit
VARCHAR(n)      -- Variable length with max n characters
CHAR(n)         -- Fixed length, padded with spaces (rarely useful)

-- In Postgres, TEXT and VARCHAR have identical performance
-- Use TEXT unless you have a specific reason to enforce a length limit
-- Use VARCHAR(n) only when you need the CHECK constraint behavior

-- For constrained values, use CHECK instead of CHAR:
status TEXT CHECK (status IN ('active', 'inactive', 'suspended'))
-- This is clearer than CHAR(8) and gives better error messages
```

### 9.3 Date and Time Types

```sql
DATE            -- Date only: 2026-01-15
TIME            -- Time only (without timezone): 14:30:00
TIMETZ          -- Time with timezone (rarely useful)
TIMESTAMP       -- Date and time without timezone
TIMESTAMPTZ     -- Date and time WITH timezone (recommended)
INTERVAL        -- A duration: '3 days', '2 hours 30 minutes'

-- Always use TIMESTAMPTZ for application timestamps
-- It stores as UTC and converts to session timezone on read
-- TIMESTAMP (without TZ) has no timezone info — ambiguous and dangerous

created_at TIMESTAMPTZ DEFAULT NOW()
updated_at TIMESTAMPTZ DEFAULT NOW()
deleted_at TIMESTAMPTZ   -- NULL means not deleted (soft delete)
```

### 9.4 Boolean

```sql
BOOLEAN         -- TRUE / FALSE / NULL
is_active BOOLEAN NOT NULL DEFAULT TRUE
is_verified BOOLEAN NOT NULL DEFAULT FALSE
```

### 9.5 UUID

```sql
UUID            -- 128-bit universally unique identifier
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
-- gen_random_uuid() is built into Postgres 13+
-- For older versions: use pgcrypto extension's gen_random_uuid()
```

### 9.6 JSON Types

```sql
JSON            -- Stores JSON as text, validates on input
JSONB           -- Stores JSON in binary format, indexable

-- Always prefer JSONB over JSON for stored data
-- JSON is only useful if you need to preserve exact whitespace/key order

metadata JSONB DEFAULT '{}'
settings JSONB DEFAULT '{}'

-- Querying JSONB
SELECT metadata->>'key' FROM table;           -- Get as text
SELECT metadata->'nested'->>'key' FROM table; -- Nested access
SELECT * FROM table WHERE metadata @> '{"role": "admin"}'; -- Contains
CREATE INDEX ON table USING gin(metadata);    -- Full JSONB index
```

**When to use JSONB vs a proper table:**

```
Use JSONB when:
- The structure varies per row and is unpredictable
- You're storing user-defined settings or configuration
- The data is write-once and mostly read as a blob
- You're prototyping and haven't settled on structure

Use a proper table when:
- You need to query specific fields frequently
- You need foreign key constraints on the data
- The structure is known and consistent
- You need to aggregate or filter on specific fields
```

### 9.7 Arrays

```sql
-- Postgres supports arrays of any type
tags TEXT[]
scores INT[]
ip_addresses INET[]

-- Inserting
INSERT INTO posts (tags) VALUES (ARRAY['tech', 'devops', 'linux']);

-- Querying
SELECT * FROM posts WHERE 'devops' = ANY(tags);
SELECT * FROM posts WHERE tags @> ARRAY['tech', 'linux']; -- Contains both

-- Indexing
CREATE INDEX ON posts USING gin(tags);
```

Arrays are convenient but have the same downsides as comma-separated strings — you can't foreign key reference array elements, can't query individual elements efficiently without a GIN index. Use a junction table for relationships; use arrays for simple tag lists or flags.

### 9.8 Other Useful Types

```sql
INET            -- IP address (IPv4 or IPv6), validates format
CIDR            -- IP network: 192.168.1.0/24
MACADDR         -- MAC address
MONEY           -- Currency amount (avoid — use NUMERIC instead)
BYTEA           -- Binary data (images, files — usually store files in S3 instead)
ENUM            -- User-defined enumerated type (covered below)
TSVECTOR        -- Full-text search document
TSQUERY         -- Full-text search query
```

### 9.9 Custom ENUM Types

```sql
-- Create the type once
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'deleted');
CREATE TYPE order_status AS ENUM ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled');

-- Use in table
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    status user_status NOT NULL DEFAULT 'active'
);

-- Adding a new value to an enum (no table rewrite needed in Postgres)
ALTER TYPE user_status ADD VALUE 'pending_verification';

-- Note: you cannot remove values from an enum or change their order
-- For flexibility, TEXT + CHECK constraint is often better than ENUM:
status TEXT NOT NULL DEFAULT 'active'
    CHECK (status IN ('active', 'inactive', 'suspended', 'deleted'))
-- CHECK constraints can be modified; ENUMs cannot remove values
```

---

## 10. Constraints — Enforcing Integrity at the Database Level

### 10.1 Why Constraints at the Database Level

Application code has bugs. Migrations run directly against the database. Multiple applications may share the same database. If your data integrity rules only exist in the application, they can be bypassed.

Database constraints are the last line of defence. They're always enforced, regardless of how the data got there.

### 10.2 NOT NULL

```sql
-- Every row must have a value for this column
email TEXT NOT NULL

-- A nullable column (the default)
bio TEXT   -- NULL is valid here

-- NOT NULL vs empty string — they're different
-- NULL means "unknown" or "not provided"
-- '' means "explicitly set to nothing"
-- Be consistent: pick one convention and stick with it
-- Postgres community convention: prefer NULL over empty string
```

### 10.3 UNIQUE

```sql
-- Single column uniqueness
email TEXT UNIQUE NOT NULL

-- Multi-column uniqueness (combination must be unique)
UNIQUE (user_id, course_id)         -- In constraint block
CREATE UNIQUE INDEX ON enrollments(user_id, course_id);  -- Or as an index

-- Partial unique index (unique among a subset of rows)
CREATE UNIQUE INDEX ON users(email) WHERE deleted_at IS NULL;
-- Allows multiple deleted users with same email, but only one active user per email
```

### 10.4 CHECK

```sql
-- Validate column values
price NUMERIC(10, 2) CHECK (price >= 0)
quantity INT CHECK (quantity > 0)
status TEXT CHECK (status IN ('active', 'inactive', 'suspended'))
end_date DATE CHECK (end_date >= start_date)  -- Cross-column check
rating INT CHECK (rating BETWEEN 1 AND 5)
percentage NUMERIC(5, 2) CHECK (percentage >= 0 AND percentage <= 100)

-- Named constraint (better error messages)
CONSTRAINT price_positive CHECK (price >= 0)
CONSTRAINT valid_status CHECK (status IN ('active', 'inactive'))

-- Table-level CHECK (can reference multiple columns)
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    CONSTRAINT valid_date_range CHECK (end_date >= start_date)
);
```

### 10.5 DEFAULT

```sql
created_at TIMESTAMPTZ DEFAULT NOW()
updated_at TIMESTAMPTZ DEFAULT NOW()
is_active BOOLEAN DEFAULT TRUE
status TEXT DEFAULT 'pending'
view_count INT DEFAULT 0
metadata JSONB DEFAULT '{}'
```

### 10.6 EXCLUSION Constraints

Postgres-specific: like UNIQUE but more general. Prevents rows where a specified condition is true for any two rows.

```sql
-- Room booking: no two bookings for the same room with overlapping time ranges
CREATE TABLE room_bookings (
    id BIGSERIAL PRIMARY KEY,
    room_id INT NOT NULL,
    during TSTZRANGE NOT NULL,  -- a time range type
    EXCLUDE USING GIST (room_id WITH =, during WITH &&)
    -- && means "overlaps" for range types
);
```

### 10.7 Deferrable Constraints

By default, constraints are checked immediately. Deferrable constraints can be checked at the end of the transaction — useful when you need to insert rows in an order that temporarily violates a constraint.

```sql
-- Deferrable foreign key
REFERENCES other_table(id) DEFERRABLE INITIALLY DEFERRED

-- Within a transaction
BEGIN;
SET CONSTRAINTS ALL DEFERRED;
-- Now you can insert in any order within this transaction
INSERT INTO ...;
INSERT INTO ...;
COMMIT;  -- Constraints checked here
```

---

## 11. Indexes — Design Strategy

### 11.1 What an Index Is

An index is a separate data structure that the database maintains alongside the table, allowing it to find rows faster than scanning the entire table. A B-tree index on `users.email` means finding a user by email is O(log n) instead of O(n).

The tradeoff: indexes speed up reads but slow down writes (every INSERT, UPDATE, DELETE must also update the index) and consume storage.

### 11.2 When Indexes Are Created Automatically

```sql
-- PRIMARY KEY → automatically creates a unique B-tree index
id BIGSERIAL PRIMARY KEY

-- UNIQUE constraint → automatically creates a unique B-tree index
email TEXT UNIQUE NOT NULL
```

### 11.3 When to Add Indexes Manually

**Add an index on foreign key columns:**

```sql
-- Without an index on orders.user_id, finding all orders for a user
-- requires a full table scan of orders (gets slower as orders grows)
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
```

**Add an index on columns frequently used in WHERE clauses:**

```sql
-- If you often query: SELECT * FROM users WHERE status = 'active'
CREATE INDEX idx_users_status ON users(status);

-- If you often query by created_at ranges
CREATE INDEX idx_posts_created_at ON posts(created_at);
```

**Add an index on columns used in ORDER BY:**

```sql
-- Avoids sort operations in: SELECT * FROM posts ORDER BY created_at DESC
CREATE INDEX idx_posts_created_at_desc ON posts(created_at DESC);
```

### 11.4 Composite Indexes

A composite index covers multiple columns and can speed up queries that filter on combinations of those columns.

```sql
-- Query: SELECT * FROM orders WHERE user_id = 42 AND status = 'shipped'
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- The order of columns matters:
-- This index can also speed up: WHERE user_id = 42 (leftmost prefix)
-- But NOT: WHERE status = 'shipped' (doesn't start from the left)
```

**The leftmost prefix rule:** a composite index on `(a, b, c)` can be used for queries filtering on:
- `a`
- `a, b`
- `a, b, c`

But NOT for queries filtering on only `b`, `c`, or `b, c`.

### 11.5 Partial Indexes

A partial index only indexes rows that match a condition — smaller and faster:

```sql
-- Only index active users — don't waste space on deleted/inactive
CREATE INDEX idx_users_email_active ON users(email) WHERE status = 'active';

-- Only index unprocessed jobs
CREATE INDEX idx_jobs_pending ON jobs(created_at) WHERE status = 'pending';
```

### 11.6 Index Types

```sql
-- B-tree (default) — for =, <, <=, >=, >, BETWEEN, LIKE 'prefix%'
CREATE INDEX idx ON table(column);

-- Hash — only for = comparisons, slightly faster than B-tree for equality
CREATE INDEX idx ON table USING hash(column);

-- GIN (Generalised Inverted Index) — for JSONB, arrays, full-text search
CREATE INDEX idx ON posts USING gin(tags);           -- array contains
CREATE INDEX idx ON products USING gin(metadata);    -- JSONB search
CREATE INDEX idx ON posts USING gin(to_tsvector('english', body));  -- full text

-- GiST (Generalised Search Tree) — for geometric types, range types
CREATE INDEX idx ON bookings USING gist(during);     -- range overlap queries
CREATE INDEX idx ON locations USING gist(coordinates);  -- geometric queries

-- BRIN (Block Range Index) — for large tables with naturally ordered data
-- Very small index, useful for timestamp columns in append-only tables
CREATE INDEX idx ON events USING brin(created_at);
```

### 11.7 Index Design Principles

```
1. Don't over-index
   Every index slows writes. A table with 15 indexes is often slower overall
   than one with 5 well-chosen indexes.

2. Index foreign keys
   Almost always. The DB won't do it for you.

3. Index columns in WHERE, ORDER BY, JOIN ON
   But only if those queries are frequent and the table is large.

4. Consider selectivity
   Indexing a boolean column (TRUE/FALSE) is rarely useful — the index isn't
   selective enough. Postgres may ignore it and scan the table anyway.

5. Measure before adding
   Use EXPLAIN ANALYZE to see if an index is actually being used.
   See the Postgres reference for query analysis.

6. Use CONCURRENTLY for production
   CREATE INDEX CONCURRENTLY — builds index without locking the table.
   Takes longer but doesn't block reads/writes.

7. Partial indexes are your friend
   If 95% of your queries filter on WHERE status = 'active',
   a partial index on active rows is much smaller and faster.
```

---

## 12. Entity-Relationship Diagrams (ERD)

### 12.1 What ERDs Are For

An ERD is a visual representation of your database schema — entities, their attributes, and the relationships between them. Draw it before writing DDL. It's much easier to spot design mistakes in a diagram than in SQL.

### 12.2 Crow's Foot Notation

The most common ERD notation uses crow's foot symbols to show cardinality:

```
One (and only one):         |
One or more:               >|
Zero or one:               o|
Zero or more:             o>|

Examples:
User ||--o{ Orders      -- one user, zero or more orders
Order ||--|{ OrderItems  -- one order, one or more items
Product }o--|| Category  -- zero or more products, one category
Student }o--o{ Courses   -- students take courses (many-to-many, both optional)
```

### 12.3 A Simple ERD in Text Form

```
┌─────────────┐       ┌─────────────┐       ┌──────────────┐
│   USERS     │       │   ORDERS    │       │ ORDER_ITEMS  │
├─────────────┤       ├─────────────┤       ├──────────────┤
│ id (PK)     │──┐    │ id (PK)     │──┐    │ id (PK)      │
│ email       │  └───<│ user_id(FK) │  └───<│ order_id(FK) │
│ name        │       │ total       │       │ product_id(FK│>──┐
│ created_at  │       │ status      │       │ quantity     │   │
└─────────────┘       │ created_at  │       │ unit_price   │   │
                      └─────────────┘       └──────────────┘   │
                                                                │
┌──────────────┐       ┌─────────────┐                         │
│  CATEGORIES  │       │  PRODUCTS   │<────────────────────────┘
├──────────────┤       ├─────────────┤
│ id (PK)      │──┐    │ id (PK)     │
│ name         │  └───<│ category_id │
│ slug         │       │ name        │
└──────────────┘       │ price       │
                       │ stock       │
                       └─────────────┘
```

### 12.4 ERD Tools

- **dbdiagram.io** — write DBML (a simple DSL), get a visual diagram instantly. Free, online.
- **DrawSQL** — similar to dbdiagram.io, good UI
- **Lucidchart** — full-featured diagramming, good for complex schemas
- **pgAdmin** — can generate ERDs from existing Postgres databases
- **DBeaver** — desktop tool, generates ERDs from existing databases
- **Mermaid** — text-based diagrams you can embed in Markdown (good for docs)

```
erDiagram (Mermaid syntax)
    USERS ||--o{ ORDERS : places
    ORDERS ||--|{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : "included in"
    CATEGORIES ||--o{ PRODUCTS : has
```

---

## 13. Common Schema Patterns

### 13.1 User Authentication

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    email_verified_at TIMESTAMPTZ,
    password_hash TEXT,                -- NULL if using OAuth only
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ             -- soft delete
);

CREATE TABLE oauth_accounts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,            -- 'google', 'github', 'facebook'
    provider_user_id TEXT NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (provider, provider_user_id)
);

CREATE TABLE refresh_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,               -- NULL = not yet used
    revoked_at TIMESTAMPTZ,            -- NULL = not revoked
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE password_reset_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX ON oauth_accounts(user_id);
CREATE INDEX ON refresh_tokens(user_id);
CREATE INDEX ON refresh_tokens(token);
CREATE INDEX ON password_reset_tokens(token);
```

### 13.2 Role-Based Access Control (RBAC)

```sql
CREATE TABLE roles (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,          -- 'admin', 'editor', 'viewer'
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE permissions (
    id BIGSERIAL PRIMARY KEY,
    resource TEXT NOT NULL,             -- 'posts', 'users', 'reports'
    action TEXT NOT NULL,               -- 'create', 'read', 'update', 'delete'
    description TEXT,
    UNIQUE (resource, action)
);

CREATE TABLE role_permissions (
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id BIGINT NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE user_roles (
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    assigned_by BIGINT REFERENCES users(id),
    PRIMARY KEY (user_id, role_id)
);

-- Query: does user 42 have permission to 'update' 'posts'?
SELECT EXISTS (
    SELECT 1 FROM user_roles ur
    JOIN role_permissions rp ON rp.role_id = ur.role_id
    JOIN permissions p ON p.id = rp.permission_id
    WHERE ur.user_id = 42
      AND p.resource = 'posts'
      AND p.action = 'update'
);
```

### 13.3 Content / Blog

```sql
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    author_id BIGINT NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    body TEXT NOT NULL,
    body_tsvector TSVECTOR,            -- full-text search vector
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'published', 'archived')),
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL
);

CREATE TABLE post_tags (
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    tag_id BIGINT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);

CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    parent_id BIGINT REFERENCES comments(id) ON DELETE CASCADE, -- threaded comments
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX ON posts(author_id);
CREATE INDEX ON posts(status, published_at DESC);
CREATE INDEX ON posts(slug);
CREATE INDEX ON post_tags(tag_id);
CREATE INDEX ON comments(post_id);
CREATE INDEX ON comments(parent_id);
CREATE INDEX ON posts USING gin(body_tsvector);  -- full-text search
```

### 13.4 E-Commerce

```sql
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    category_id BIGINT REFERENCES categories(id),
    name TEXT NOT NULL,
    description TEXT,
    sku TEXT UNIQUE,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    compare_at_price NUMERIC(10, 2),   -- original price for showing discounts
    cost_price NUMERIC(10, 2),         -- what you paid (internal)
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded')),
    subtotal NUMERIC(10, 2) NOT NULL,
    tax NUMERIC(10, 2) NOT NULL DEFAULT 0,
    shipping_cost NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total NUMERIC(10, 2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    -- Snapshot shipping address (denormalised — address at time of order)
    shipping_name TEXT,
    shipping_address_line1 TEXT,
    shipping_address_line2 TEXT,
    shipping_city TEXT,
    shipping_country TEXT,
    shipping_postal_code TEXT,
    placed_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE RESTRICT,
    product_id BIGINT REFERENCES products(id) ON DELETE SET NULL,
    -- Snapshot product data at time of order (denormalised)
    product_name TEXT NOT NULL,
    product_sku TEXT,
    unit_price NUMERIC(10, 2) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    total NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 13.5 Notifications

```sql
CREATE TYPE notification_channel AS ENUM ('email', 'sms', 'push', 'in_app');

CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type TEXT NOT NULL,                        -- 'order_shipped', 'comment_reply', etc.
    channel notification_channel NOT NULL,
    title TEXT,
    body TEXT NOT NULL,
    data JSONB DEFAULT '{}',                   -- arbitrary extra data
    read_at TIMESTAMPTZ,                       -- NULL = unread
    sent_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    failure_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON notifications(user_id, read_at) WHERE read_at IS NULL;  -- unread by user
CREATE INDEX ON notifications(user_id, created_at DESC);
```

---

## 14. Multi-Tenancy Patterns

### 14.1 What Multi-Tenancy Is

A multi-tenant application serves multiple organisations (tenants) from a single deployment. Each tenant's data must be completely isolated from others. This is the architecture Traka needs — each business is a separate tenant, seeing only their own inventory, customers, and invoices.

There are three main patterns, each with different tradeoffs.

### 14.2 Pattern 1 — Separate Databases Per Tenant

Each tenant gets their own Postgres database.

```
tenant_acme    → database: db_acme
tenant_globex  → database: db_globex
tenant_initech → database: db_initech
```

**Pros:**
- Complete isolation — no risk of cross-tenant data leakage
- Easy to backup, restore, or migrate individual tenants
- Can place high-value tenants on better hardware
- Schema can differ per tenant (for custom requirements)

**Cons:**
- Expensive at scale — hundreds of databases = hundreds of connection pools
- Complex deployment — schema migrations must run against every database
- Hard to query across tenants (analytics, operations)
- Connection pooling is complicated

**When to use:** Regulated industries (healthcare, finance) where data isolation is a compliance requirement. Enterprise SaaS with a small number of large, paying customers. When tenants have custom schema requirements.

```javascript
// Application: pick database by tenant subdomain/ID
const db = getDatabaseForTenant(tenantId); // returns connection to right DB
```

### 14.3 Pattern 2 — Separate Schemas Per Tenant (Postgres-specific)

All tenants share one database but each has their own Postgres schema (namespace).

```sql
-- Create schema per tenant
CREATE SCHEMA tenant_acme;
CREATE SCHEMA tenant_globex;

-- Create the same tables in each schema
CREATE TABLE tenant_acme.users (...);
CREATE TABLE tenant_globex.users (...);

-- Set search path to isolate tenant
SET search_path = tenant_acme;
SELECT * FROM users;  -- only sees tenant_acme.users
```

**Pros:**
- Good isolation — separate namespaces
- Easier than separate databases (same connection pool, one DB server)
- Can still query across schemas when needed (for analytics)

**Cons:**
- Schema migrations must run for every tenant schema
- At hundreds of tenants, management becomes complex
- Postgres has per-connection overhead for many schemas

**When to use:** Medium number of tenants (10s to low 100s). When you want good isolation without the complexity of separate databases.

### 14.4 Pattern 3 — Shared Schema with Tenant ID Column (Row-Level Security)

All tenants share the same tables. Every table has a `tenant_id` column. Isolation is enforced through Row-Level Security (RLS) policies or application-level filtering.

```sql
-- All tables have tenant_id
CREATE TABLE tenants (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    plan TEXT NOT NULL DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    password_hash TEXT,
    role TEXT NOT NULL DEFAULT 'member',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (tenant_id, email)   -- email unique per tenant, not globally
);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index tenant_id on every table (critical for performance)
CREATE INDEX ON users(tenant_id);
CREATE INDEX ON products(tenant_id);
CREATE INDEX ON orders(tenant_id);

-- Composite indexes: tenant_id first for all tenant-scoped queries
CREATE INDEX ON products(tenant_id, created_at DESC);
CREATE INDEX ON orders(tenant_id, status);
```

**Enforcing isolation with Row-Level Security:**

```sql
-- Enable RLS on the table
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Create a policy: users can only see rows for their tenant
CREATE POLICY tenant_isolation ON products
    USING (tenant_id = current_setting('app.current_tenant_id')::BIGINT);

-- In your application, set the tenant on every connection
SET app.current_tenant_id = 42;  -- Set before any query
-- Now: SELECT * FROM products; automatically filters to tenant 42
```

**Enforcing isolation at the application level (simpler, more portable):**

```typescript
// NestJS example: inject tenant_id from JWT into every query
@Injectable()
export class ProductsRepository {
  findAll(tenantId: number) {
    return this.db.query(
      'SELECT * FROM products WHERE tenant_id = $1',
      [tenantId]
    );
    // NEVER do: SELECT * FROM products (without tenant_id filter)
  }
}
```

**Pros:**
- Simple to implement and operate
- One migration touches all tenants simultaneously
- Easy cross-tenant analytics
- Works well at any scale of tenants

**Cons:**
- Risk of cross-tenant data leakage if tenant_id filter is missed
- All tenants on same infrastructure (noisy neighbour problem)
- Harder to give a single tenant their own backup/restore
- Less isolation (regulatory/compliance concern)

**When to use:** Most SaaS applications. When you have many tenants (100s to 1000s+). When cross-tenant operations (analytics, billing, support) are important.

### 14.5 Hybrid Approach

Many production systems use a hybrid:

```
Free/Starter tenants → shared schema (Pattern 3)
Enterprise tenants   → dedicated database or schema (Pattern 1 or 2)
```

This lets you serve the long tail of small customers efficiently while giving enterprise customers the isolation and guarantees they require (and pay for).

### 14.6 Multi-Tenancy Design Rules

```
1. tenant_id goes on EVERY tenant-scoped table — no exceptions
2. Index tenant_id on every table — queries without it are table scans
3. Make tenant_id the first column in composite indexes
4. UNIQUE constraints must include tenant_id
   (email should be unique per tenant, not globally)
5. Use RLS or a base repository class that always appends WHERE tenant_id = ?
6. Never let raw IDs from one tenant be used in another tenant's context
7. Test isolation rigorously — it's a security requirement, not a feature
```

---

## 15. Audit Trails and Soft Deletes

### 15.1 Soft Deletes

A soft delete marks a row as deleted without removing it from the database. The row remains accessible for audit, recovery, or reference by other records.

```sql
-- Add deleted_at to any table that needs soft deletes
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMPTZ;

-- "Delete" a user
UPDATE users SET deleted_at = NOW() WHERE id = 42;

-- Query active users
SELECT * FROM users WHERE deleted_at IS NULL;

-- Query all users including deleted
SELECT * FROM users;

-- Query only deleted users
SELECT * FROM users WHERE deleted_at IS NOT NULL;

-- Restore a user
UPDATE users SET deleted_at = NULL WHERE id = 42;
```

**Partial unique index with soft deletes:**

```sql
-- Email should be unique among active users, but allow reuse after deletion
CREATE UNIQUE INDEX idx_users_email_active
    ON users(email)
    WHERE deleted_at IS NULL;
-- Deleted users don't conflict; new users can reuse an email
```

**Tradeoffs of soft deletes:**

```
Pros:
- Data recovery is trivial
- Audit trail of who was deleted and when
- Foreign key references remain valid
- Historical records (orders placed by a deleted user) remain intact

Cons:
- Queries must always include WHERE deleted_at IS NULL (easy to forget)
- Table grows indefinitely
- UNIQUE constraints are complicated (need partial indexes)
- Personal data regulations (GDPR) may require true deletion
   → Solution: soft delete + anonymise PII, or hard delete after soft delete period
```

### 15.2 Audit Tables

An audit trail records every change to a row — who changed it, when, and what the previous value was. Essential for regulated industries and debugging data integrity issues.

**Pattern 1 — Audit columns on the table:**

```sql
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by BIGINT REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by BIGINT REFERENCES users(id)
);
```

Simple but only stores the last modification — no history.

**Pattern 2 — Separate audit/history table:**

```sql
CREATE TABLE products_audit (
    audit_id BIGSERIAL PRIMARY KEY,
    action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    changed_by BIGINT REFERENCES users(id),
    -- Snapshot of the row at change time
    product_id BIGINT NOT NULL,
    name TEXT,
    price NUMERIC(10, 2),
    -- Add all columns from products that you want to audit
    old_data JSONB,    -- Previous state (NULL for INSERT)
    new_data JSONB     -- New state (NULL for DELETE)
);

-- Trigger to populate automatically
CREATE OR REPLACE FUNCTION audit_products()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO products_audit (action, product_id, new_data)
        VALUES ('INSERT', NEW.id, row_to_json(NEW));
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO products_audit (action, product_id, old_data, new_data)
        VALUES ('UPDATE', NEW.id, row_to_json(OLD), row_to_json(NEW));
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO products_audit (action, product_id, old_data)
        VALUES ('DELETE', OLD.id, row_to_json(OLD));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER products_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW EXECUTE FUNCTION audit_products();
```

**Pattern 3 — Temporal tables (versioned rows):**

```sql
-- Keep every version of a row with valid_from/valid_to timestamps
CREATE TABLE products (
    id BIGSERIAL,
    version INT NOT NULL DEFAULT 1,
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,              -- NULL means current version
    name TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (id, version)
);

-- "Update" by inserting a new version
-- 1. Close current version
UPDATE products SET valid_to = NOW() WHERE id = 42 AND valid_to IS NULL;
-- 2. Insert new version
INSERT INTO products (id, version, name, price)
VALUES (42, (SELECT MAX(version)+1 FROM products WHERE id = 42), 'New Name', 99.99);

-- Query current version
SELECT * FROM products WHERE valid_to IS NULL;

-- Query as of a specific time
SELECT * FROM products
WHERE valid_from <= '2025-06-01' AND (valid_to IS NULL OR valid_to > '2025-06-01');
```

### 15.3 Standard Timestamp Columns

Every table that has meaningful lifecycle should have these:

```sql
CREATE TABLE anything (
    id BIGSERIAL PRIMARY KEY,
    -- ... columns ...
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ               -- only if soft delete is needed
);

-- Auto-update updated_at on every UPDATE
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON anything
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

---

## 16. Hierarchical and Recursive Data

### 16.1 When You Need Hierarchies

Categories with subcategories. Comments with replies. Org charts. File systems. Geographic regions. These all have parent-child relationships of arbitrary depth.

### 16.2 Adjacency List (Simple)

Each row stores a reference to its parent. Simple to implement, hard to query deeply.

```sql
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    parent_id BIGINT REFERENCES categories(id),  -- NULL for root nodes
    name TEXT NOT NULL,
    slug TEXT NOT NULL
);

-- Electronics → Phones → Smartphones → Android

-- Query immediate children
SELECT * FROM categories WHERE parent_id = 42;

-- Query full path (requires recursive CTE)
WITH RECURSIVE category_path AS (
    -- Base case: start from the category
    SELECT id, parent_id, name, 1 AS depth
    FROM categories
    WHERE id = 42

    UNION ALL

    -- Recursive case: go up to parent
    SELECT c.id, c.parent_id, c.name, cp.depth + 1
    FROM categories c
    JOIN category_path cp ON cp.parent_id = c.id
)
SELECT * FROM category_path ORDER BY depth DESC;

-- Query all descendants
WITH RECURSIVE descendants AS (
    SELECT id, parent_id, name, 0 AS depth
    FROM categories
    WHERE id = 1  -- start node

    UNION ALL

    SELECT c.id, c.parent_id, c.name, d.depth + 1
    FROM categories c
    JOIN descendants d ON d.id = c.parent_id
)
SELECT * FROM descendants;
```

### 16.3 Materialised Path (Path Enumeration)

Store the full path as a string. Simpler queries but must be maintained on moves.

```sql
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL    -- '1.4.12.42' = IDs from root to this node
);

-- Query all descendants of node 4
SELECT * FROM categories WHERE path LIKE '1.4.%';

-- Query all ancestors (parse the path)
-- '1.4.12.42' → ancestors are 1, 4, 12

-- Index
CREATE INDEX ON categories(path text_pattern_ops);  -- for LIKE queries
```

### 16.4 Nested Sets (Read-Heavy Hierarchies)

Assigns left and right numbers to each node. Extremely fast for reading entire subtrees, but expensive to update.

```sql
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    lft INT NOT NULL,
    rgt INT NOT NULL
);

-- Query all descendants: WHERE lft > parent.lft AND rgt < parent.rgt
-- Query all ancestors: WHERE lft < node.lft AND rgt > node.rgt
-- Count children: (rgt - lft - 1) / 2
```

### 16.5 ltree Extension (Postgres-specific)

Postgres has a built-in `ltree` extension for hierarchical label trees — faster than LIKE queries, with proper indexing.

```sql
CREATE EXTENSION ltree;

CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    path ltree    -- 'electronics.phones.smartphones'
);

-- Index
CREATE INDEX ON categories USING gist(path);

-- Query descendants
SELECT * FROM categories WHERE path <@ 'electronics.phones';

-- Query ancestors
SELECT * FROM categories WHERE path @> 'electronics.phones.smartphones.android';

-- Depth
SELECT nlevel(path) AS depth FROM categories;
```

**Recommendation:**
- Simple hierarchy, rarely queried deeply → **adjacency list** with recursive CTE
- Frequent read of deep subtrees, rare updates → **ltree** (Postgres) or nested sets
- Frequent moves → **materialised path** or adjacency list

---

## 17. Polymorphic Relationships

### 17.1 The Problem

Sometimes you need a relationship where the "target" can be one of several different types. For example:
- Comments can belong to a Post OR a Product OR a Video
- Likes can be on a Post OR a Comment
- Files can be attached to an Order OR a User OR a Project

### 17.2 Anti-Pattern — Polymorphic Foreign Key

This is common in Rails/ActiveRecord but is an anti-pattern from a database integrity standpoint:

```sql
-- ANTI-PATTERN: no FK integrity possible
CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    commentable_type TEXT NOT NULL,    -- 'Post', 'Product', 'Video'
    commentable_id BIGINT NOT NULL,    -- ID in whichever table
    body TEXT NOT NULL
);
-- Cannot enforce FK because the target table depends on commentable_type
-- An invalid commentable_id will never be caught by the DB
```

### 17.3 Pattern 1 — Separate Junction Tables

Create a separate relationship table for each type:

```sql
CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    author_id BIGINT REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Separate table for each parent type
CREATE TABLE post_comments (
    comment_id BIGINT PRIMARY KEY REFERENCES comments(id) ON DELETE CASCADE,
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE product_comments (
    comment_id BIGINT PRIMARY KEY REFERENCES comments(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE
);
```

Clean FK integrity, but more tables to manage.

### 17.4 Pattern 2 — Nullable Foreign Keys

Use nullable FK columns for each possible parent, enforce that exactly one is set:

```sql
CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    post_id BIGINT REFERENCES posts(id) ON DELETE CASCADE,
    product_id BIGINT REFERENCES products(id) ON DELETE CASCADE,
    video_id BIGINT REFERENCES videos(id) ON DELETE CASCADE,
    CONSTRAINT exactly_one_parent CHECK (
        (post_id IS NOT NULL)::INT +
        (product_id IS NOT NULL)::INT +
        (video_id IS NOT NULL)::INT = 1
    )
);
```

Clear FK integrity. Becomes unwieldy if you add many types.

### 17.5 Pattern 3 — Shared Abstract Table

Create an abstract entity that all commentable things reference:

```sql
CREATE TABLE commentable_entities (
    id BIGSERIAL PRIMARY KEY,
    type TEXT NOT NULL  -- for reference only
);

CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY REFERENCES commentable_entities(id),
    title TEXT NOT NULL
);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY REFERENCES commentable_entities(id),
    name TEXT NOT NULL
);

CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    entity_id BIGINT NOT NULL REFERENCES commentable_entities(id),
    body TEXT NOT NULL
);
```

The cleanest in terms of FK integrity, but adds complexity.

**The pragmatic recommendation:** for most applications, the nullable FK pattern (Pattern 2) is the right tradeoff — you get FK integrity and it's simple to implement. If you have more than 3-4 types, consider the abstract table pattern.

---

## 18. Schema Versioning and Migrations

### 18.1 Why Migrations

Never manually `ALTER TABLE` in production. Every schema change should be:
- A versioned migration file committed to version control
- Reviewed in a PR like application code
- Applied by an automated tool, not by hand
- Rollback-capable (ideally)

### 18.2 Migration Tools

**Flyway** — Java-based, SQL migrations, sequential versioning. Widely used in enterprise.
**Liquibase** — XML/YAML/SQL, more complex, supports rollback.
**node-pg-migrate** — Node.js, SQL or JavaScript migrations.
**Prisma Migrate** — ORM-coupled, great DX for Node.js projects.
**TypeORM Migrations** — ORM-coupled, TypeScript.
**golang-migrate** — Go, simple SQL up/down migrations.
**Alembic** — Python, SQLAlchemy-coupled.

### 18.3 Migration File Structure

```
migrations/
├── 001_create_users.sql
├── 002_create_products.sql
├── 003_add_status_to_users.sql
├── 004_create_orders.sql
└── 005_add_index_orders_user_id.sql
```

### 18.4 Writing Safe Migrations

**Adding a column:**

```sql
-- SAFE: adds a nullable column, no table rewrite
ALTER TABLE users ADD COLUMN bio TEXT;

-- SAFE: adds a column with a default
ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE;

-- CAREFUL: adding NOT NULL without a default requires a table rewrite (locks table)
-- For large tables, do this in steps:
-- Step 1: Add nullable
ALTER TABLE users ADD COLUMN is_verified BOOLEAN;
-- Step 2: Backfill
UPDATE users SET is_verified = FALSE WHERE is_verified IS NULL;
-- Step 3: Add NOT NULL constraint
ALTER TABLE users ALTER COLUMN is_verified SET NOT NULL;
```

**Adding an index without locking:**

```sql
-- DANGEROUS for large tables — locks the table
CREATE INDEX ON users(email);

-- SAFE — builds index concurrently, no table lock
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
-- Takes longer but production stays live
```

**Renaming a column (zero-downtime):**

```sql
-- Phase 1: Add new column alongside old
ALTER TABLE users ADD COLUMN full_name TEXT;

-- Phase 2: Deploy app code that writes to BOTH old and new column
-- Update data
UPDATE users SET full_name = first_name || ' ' || last_name;

-- Phase 3: Deploy app code that reads from new column
-- Phase 4: Remove old column (after confirming nothing reads it)
ALTER TABLE users DROP COLUMN first_name;
ALTER TABLE users DROP COLUMN last_name;
```

**Dropping a column:**

```sql
-- First: deploy code that no longer references the column
-- Then: drop the column
ALTER TABLE users DROP COLUMN old_column;
-- Dropping a column is fast in Postgres (just marks it as dropped)
-- The space isn't reclaimed until VACUUM
```

### 18.5 The Expand-Contract Pattern

For zero-downtime schema changes:

```
1. EXPAND — add the new column/table/index alongside the old
2. MIGRATE — backfill data, update application code
3. CONTRACT — remove the old column/table/constraint
```

Never make a breaking schema change and a breaking application change at the same time.

---

## 19. Real-World Schema Examples

### 19.1 Traka — Multi-Tenant SME Business Management

```sql
-- Tenants (the businesses using Traka)
CREATE TABLE tenants (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    plan TEXT NOT NULL DEFAULT 'starter'
        CHECK (plan IN ('starter', 'growth', 'enterprise')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users belong to a tenant
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    password_hash TEXT,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'member'
        CHECK (role IN ('owner', 'admin', 'manager', 'member')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (tenant_id, email)
);

-- Customers of each business
CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Product catalogue
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    sku TEXT,
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    cost_price NUMERIC(12, 2),
    stock_quantity INT NOT NULL DEFAULT 0,
    low_stock_threshold INT DEFAULT 10,
    unit TEXT DEFAULT 'unit',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (tenant_id, sku)
);

-- Invoices
CREATE TABLE invoices (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    customer_id BIGINT REFERENCES customers(id),
    invoice_number TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'sent', 'paid', 'overdue', 'cancelled')),
    issued_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE,
    subtotal NUMERIC(12, 2) NOT NULL DEFAULT 0,
    tax_rate NUMERIC(5, 2) DEFAULT 0,
    tax_amount NUMERIC(12, 2) DEFAULT 0,
    total NUMERIC(12, 2) NOT NULL DEFAULT 0,
    notes TEXT,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (tenant_id, invoice_number)
);

CREATE TABLE invoice_items (
    id BIGSERIAL PRIMARY KEY,
    invoice_id BIGINT NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    product_id BIGINT REFERENCES products(id) ON DELETE SET NULL,
    description TEXT NOT NULL,
    quantity NUMERIC(10, 3) NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL,
    total NUMERIC(12, 2) NOT NULL
);

-- Indexes
CREATE INDEX ON users(tenant_id);
CREATE INDEX ON customers(tenant_id);
CREATE INDEX ON products(tenant_id);
CREATE INDEX ON invoices(tenant_id, status);
CREATE INDEX ON invoices(customer_id);
CREATE INDEX ON invoice_items(invoice_id);
```

### 19.2 Nextvibe — Social Event Platform

```sql
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    organizer_id BIGINT NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    location TEXT,
    latitude NUMERIC(9, 6),
    longitude NUMERIC(9, 6),
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ,
    capacity INT,                      -- NULL = unlimited
    price NUMERIC(10, 2) DEFAULT 0,
    currency TEXT DEFAULT 'NGN',
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'published', 'cancelled', 'completed')),
    cover_image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_event_dates CHECK (ends_at IS NULL OR ends_at > starts_at)
);

CREATE TABLE attendances (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'registered'
        CHECK (status IN ('registered', 'attended', 'cancelled', 'waitlisted')),
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    checked_in_at TIMESTAMPTZ,
    UNIQUE (event_id, user_id)
);

CREATE TABLE event_tags (
    event_id BIGINT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    tag_id BIGINT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (event_id, tag_id)
);

-- Indexes
CREATE INDEX ON events(organizer_id);
CREATE INDEX ON events(starts_at) WHERE status = 'published';
CREATE INDEX ON events(status, starts_at);
CREATE INDEX ON attendances(event_id);
CREATE INDEX ON attendances(user_id);
```

---

## 20. Design Checklist

A checklist to run through before finalising any schema.

### Entities and Structure

- [ ] Each table represents exactly one concept — no catch-all tables
- [ ] No comma-separated values stored in a single column
- [ ] No repeating column groups (`column_1`, `column_2`, `column_3`)
- [ ] No columns that are almost always NULL (usually means split the table)
- [ ] JSON/JSONB used intentionally, not to avoid thinking about structure

### Keys and Relationships

- [ ] Every table has a primary key
- [ ] Primary keys are surrogate (not email, phone, or other business data)
- [ ] Foreign keys are defined for every relationship
- [ ] `ON DELETE` behaviour is chosen intentionally for each FK
- [ ] Many-to-many relationships use junction tables, not arrays of IDs
- [ ] Junction tables have a unique constraint (composite PK or UNIQUE)
- [ ] Self-referential tables have appropriate FK setup

### Constraints and Integrity

- [ ] Columns that must have values are `NOT NULL`
- [ ] Columns with constrained values have CHECK constraints
- [ ] Columns that should be unique have UNIQUE constraints or unique indexes
- [ ] `UNIQUE` constraints include `tenant_id` where applicable (multi-tenant)
- [ ] Cross-column rules are expressed as table-level CHECK constraints

### Data Types

- [ ] Money/prices use `NUMERIC(p, s)`, never `FLOAT` or `DOUBLE`
- [ ] Timestamps use `TIMESTAMPTZ`, not `TIMESTAMP`
- [ ] Text uses `TEXT` or `VARCHAR(n)` (not `CHAR(n)`)
- [ ] Boolean columns have appropriate defaults and are `NOT NULL`
- [ ] ENUMs or CHECK constraints for status fields

### Indexes

- [ ] Foreign key columns are indexed
- [ ] Columns frequently in WHERE clauses are indexed
- [ ] Columns in ORDER BY are indexed
- [ ] Composite indexes use the most selective / leftmost column first
- [ ] Large table indexes use `CONCURRENTLY` in production migrations

### Multi-Tenancy (if applicable)

- [ ] Every tenant-scoped table has `tenant_id`
- [ ] `tenant_id` is indexed on every table
- [ ] UNIQUE constraints include `tenant_id`
- [ ] RLS policies or application filtering enforces isolation
- [ ] Tenant isolation is tested explicitly

### Timestamps and Audit

- [ ] All tables have `created_at` with `DEFAULT NOW()`
- [ ] Mutable tables have `updated_at` with auto-update trigger
- [ ] Tables that need history have `deleted_at` or an audit table
- [ ] Audit tables exist for tables requiring change history

### Migrations

- [ ] Every schema change is in a migration file, not applied manually
- [ ] Migrations are backwards-compatible (expand-contract pattern for breaking changes)
- [ ] Large table indexes use `CREATE INDEX CONCURRENTLY`
- [ ] Adding `NOT NULL` columns without defaults is done in steps
- [ ] Migration has been tested against a copy of production data

---

*Last updated: 2026 — Built from real schema design experience across SaaS and fintech systems.*

---

## 21. Time-Series Data

Data fundamentally ordered by time and queried in time ranges — metrics, analytics, IoT, financial tick data.

### 21.1 Key Design Principles

```sql
-- 1. Time is always the primary dimension — index first
CREATE INDEX idx_metrics_time ON metrics(recorded_at DESC);

-- 2. Always TIMESTAMPTZ — store in UTC
recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

-- 3. Partition by time — old data is never updated
PARTITION BY RANGE (recorded_at)

-- 4. Never update time-series rows — append only

-- 5. Aggregate into buckets for long-range queries
-- Instead of 1M individual rows, store hourly aggregates:
CREATE TABLE metric_hourly (
  metric_name TEXT,
  bucket      TIMESTAMPTZ,   -- truncated to hour
  avg_value   DECIMAL,
  max_value   DECIMAL,
  min_value   DECIMAL,
  sample_count INT,
  PRIMARY KEY (metric_name, bucket)
);
```

### 21.2 TimescaleDB

PostgreSQL extension that handles time-series automatically — automatic partitioning by time, transparent compression, continuous aggregates. Use for any serious time-series workload instead of rolling your own partitioning.

```sql
-- Convert a regular table into a hypertable (automatic time partitioning)
SELECT create_hypertable('metrics', 'recorded_at');

-- Continuous aggregate: auto-maintained rollup
CREATE MATERIALIZED VIEW metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
  time_bucket('1 hour', recorded_at) AS bucket,
  metric_name,
  AVG(value) AS avg_value,
  MAX(value) AS max_value
FROM metrics
GROUP BY bucket, metric_name;
```

---

## 22. Domain-Specific Schema Patterns

### 22.1 Finance / Banking

```
Core rules:
1. Use DECIMAL, never FLOAT for money
2. Store amounts in smallest currency unit (kobo, cents)
3. Every transaction is IMMUTABLE — never update, only append
4. Double-entry bookkeeping — every debit has a credit
5. Use database transactions (ACID) for all money movements
6. Idempotency keys — prevent duplicate charges
```

```sql
CREATE TABLE accounts (
  id        UUID PRIMARY KEY,
  owner_id  UUID REFERENCES users(id),
  currency  TEXT NOT NULL DEFAULT 'NGN',
  type      TEXT CHECK (type IN ('SAVINGS', 'CURRENT', 'WALLET'))
);

CREATE TABLE transactions (
  id              UUID PRIMARY KEY,
  account_id      UUID REFERENCES accounts(id),
  amount_kobo     BIGINT NOT NULL,           -- smallest unit, never FLOAT
  type            TEXT CHECK (type IN ('CREDIT', 'DEBIT')),
  reference       TEXT,
  idempotency_key TEXT UNIQUE,               -- prevents duplicate charges
  created_at      TIMESTAMPTZ DEFAULT NOW()
  -- NEVER add updated_at — transactions are immutable
);

CREATE TABLE ledger_entries (  -- double-entry bookkeeping
  id             UUID PRIMARY KEY,
  transaction_id UUID REFERENCES transactions(id),
  account_id     UUID REFERENCES accounts(id),
  debit          BIGINT DEFAULT 0,
  credit         BIGINT DEFAULT 0
);
```

### 22.2 Healthcare

```
Core rules:
1. Audit everything — who read what, when (legal requirement)
2. Soft delete only — records legally required even after "deletion"
3. Encryption at rest for PII and medical data
4. Row-level security — patients see only their own data
5. FHIR compliance for interoperability (if building for hospitals)
```

```sql
CREATE TABLE patients (
  id          UUID PRIMARY KEY,
  mrn         TEXT UNIQUE,           -- Medical Record Number
  first_name  TEXT NOT NULL,
  last_name   TEXT NOT NULL,
  date_of_birth DATE NOT NULL,
  blood_type  TEXT
);

CREATE TABLE encounters (
  id          UUID PRIMARY KEY,
  patient_id  UUID REFERENCES patients(id),
  doctor_id   UUID REFERENCES doctors(id),
  type        TEXT,                  -- OUTPATIENT, INPATIENT, EMERGENCY
  started_at  TIMESTAMPTZ,
  ended_at    TIMESTAMPTZ,
  notes       TEXT                   -- encrypted at application level
);

CREATE TABLE vitals (
  id           UUID PRIMARY KEY,
  encounter_id UUID REFERENCES encounters(id),
  type         TEXT,                 -- BLOOD_PRESSURE, TEMPERATURE, etc.
  value        DECIMAL,
  unit         TEXT,
  recorded_at  TIMESTAMPTZ           -- time-series data
);
```

### 22.3 E-Commerce

```
Core rules:
1. Snapshot product details on order — prices change over time
2. Inventory is an append-only ledger, not a counter
3. Cart is ephemeral — can live in Redis
4. Orders are immutable once placed
```

```sql
CREATE TABLE order_items (
  id                   UUID PRIMARY KEY,
  order_id             UUID REFERENCES orders(id),
  variant_id           UUID REFERENCES product_variants(id),
  product_name_snapshot TEXT NOT NULL,   -- snapshot — product may be deleted
  price_snapshot       DECIMAL(10,2) NOT NULL,  -- price at time of order
  quantity             INT NOT NULL
);

-- Inventory as ledger — never update a counter directly
CREATE TABLE inventory_movements (
  id          UUID PRIMARY KEY,
  variant_id  UUID REFERENCES product_variants(id),
  quantity_delta INT NOT NULL,          -- positive=restock, negative=sale
  type        TEXT CHECK (type IN ('SALE', 'RETURN', 'RESTOCK', 'ADJUSTMENT')),
  reference   TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
-- Current stock = SUM(quantity_delta) for variant
-- Or: maintain a denormalized stock_count with atomic updates
```

### 22.4 AI / ML Platform

```
Core rules:
1. Models and datasets are versioned — immutable versions
2. Experiments need full reproducibility — store all hyperparams
3. Inference logs are time-series — partition by time
4. Embeddings are vectors — use pgvector extension
```

```sql
CREATE TABLE models (
  id          UUID PRIMARY KEY,
  name        TEXT NOT NULL,
  description TEXT,
  created_by  UUID REFERENCES users(id)
);

CREATE TABLE model_versions (
  id           UUID PRIMARY KEY,
  model_id     UUID REFERENCES models(id),
  version      TEXT NOT NULL,          -- semver: 1.0.0, 1.1.0
  weights_path TEXT NOT NULL,          -- S3 path to model weights
  framework    TEXT,                   -- pytorch, tensorflow
  metrics      JSONB,                  -- { accuracy: 0.94, f1: 0.92 }
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (model_id, version)
);

CREATE TABLE experiments (
  id               UUID PRIMARY KEY,
  model_version_id UUID REFERENCES model_versions(id),
  dataset_id       UUID REFERENCES datasets(id),
  hyperparams      JSONB NOT NULL,     -- { lr: 0.001, epochs: 10, batch_size: 32 }
  status           TEXT,               -- RUNNING, COMPLETED, FAILED
  started_at       TIMESTAMPTZ,
  ended_at         TIMESTAMPTZ,
  results          JSONB               -- { val_accuracy: 0.94 }
);

-- Vector embeddings (requires pgvector extension)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE embeddings (
  id               UUID PRIMARY KEY,
  source_type      TEXT,               -- 'post', 'user', 'product'
  source_id        UUID NOT NULL,
  vector           VECTOR(1536),       -- OpenAI ada-002 dimension
  model_version_id UUID REFERENCES model_versions(id),
  created_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX ON embeddings USING ivfflat (vector vector_cosine_ops);
```

### 22.5 Multi-Tenant SaaS

Three tenancy models:

**Model 1 — Shared tables with tenant_id (most common):**
```sql
CREATE TABLE projects (
  id        UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  name      TEXT NOT NULL
);

-- Row-level security prevents cross-tenant data leakage
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON projects
  USING (tenant_id = current_setting('app.current_tenant')::UUID);
-- Set before each query: SET LOCAL app.current_tenant = 'tenant-uuid'
```

**Model 2 — Separate schema per tenant:**
```sql
CREATE SCHEMA tenant_abc;
CREATE TABLE tenant_abc.projects (...);
-- More isolation, harder to maintain, up to ~1,000 tenants
```

**Model 3 — Separate database per tenant:**
Maximum isolation, massive operational overhead. Only for regulated industries (healthcare, finance) or very large enterprise tenants.

---

## 23. Common Mistakes — Junior to Senior

| Mistake | Why it hurts | The fix |
|---|---|---|
| Storing arrays in columns (`user.skills = []`) | Can't query, paginate, or add metadata | Always create a join table for lists |
| Using FLOAT for money | `0.1 + 0.2 = 0.30000000000000004` in floating point | `DECIMAL(10,2)` or store as integer cents |
| No indexes on foreign keys | Every JOIN is a full table scan | Every FK gets an index, no exceptions |
| `SELECT *` in production | Fetches unused columns, wastes bandwidth | Always specify columns |
| OFFSET pagination on large tables | `OFFSET 10000` scans and discards 10,000 rows | Cursor-based pagination |
| Hard deleting everything | Breaks FK references, loses audit history | Soft delete with `deleted_at` |
| Timezone-naive timestamps | Summer time changes break queries | Always `TIMESTAMPTZ`, store in UTC |
| No `created_at`/`updated_at` | You will need them — debugging, sorting, auditing | Add to every table from day one |
| `VARCHAR(255)` for everything | Arbitrary limit — might truncate real data | `TEXT` for strings, add `CHECK` for real limits |
| Over-normalizing hot paths | 5-table JOIN on every page load | Denormalize counters and snapshots on hot paths |
| Low-cardinality shard key | Hot shards — one shard gets 90% of writes | Shard by `user_id` or `tenant_id` |
| No transaction on multi-step writes | Partial failure leaves inconsistent state | Wrap related writes in a database transaction |

---

## 24. Senior Engineer Mindset

### 24.1 Questions to Ask Before Writing Any Schema

```
1. What are the top 5 queries this schema will serve?
   Design indexes for those queries specifically.

2. What is the expected row count in 1 year? 5 years?
   Does this table need partitioning?

3. What is the read:write ratio?
   Read-heavy → optimise for reads.
   Write-heavy → minimise index count.

4. Which data is mutable? Which is immutable?
   Financial and audit data should never be updated.

5. What happens when a parent record is deleted?
   CASCADE, RESTRICT, or SET NULL?

6. Does this need an audit trail?
   Add audit_logs table or event sourcing from day one.

7. Is this a multi-tenant system?
   Add tenant_id to every table immediately.

8. What columns will be in WHERE clauses?
   Add indexes for those columns now, not after slow queries appear.
```

### 24.2 Schema Evolution Path

```
Day 1 (MVP):
  Normalised schema, basic indexes on FKs and common filters
  Soft delete on critical tables, timestamps everywhere

Month 3 (Growth):
  Add counter caches (like_count, comment_count) — verified by slow query log
  Add composite indexes based on EXPLAIN ANALYZE output
  Add read replicas — separate read traffic from write traffic

Year 1 (Scale):
  Partition large tables by time (events, transactions, logs)
  Materialised views for expensive aggregations
  Archiving strategy for old partitions

Year 3+ (Hyperscale):
  Evaluate sharding based on actual measured bottlenecks
  Purpose-built databases for specific workloads:
    Redis for sessions, Elasticsearch for search,
    TimescaleDB for metrics, pgvector for embeddings
```

### 24.3 The Cardinal Rules

1. **Design your schema around your queries, not just your entities.** The best schema is one where the most frequent queries need the fewest joins and always use indexes.

2. **Every index is a trade-off.** More indexes = faster reads + slower writes + more storage. Add indexes for proven query patterns, not hypothetical ones.

3. **Normalisation is the starting point, not the goal.** Start normalised, denormalise under measured performance pressure. Never denormalise speculatively.

4. **Never store money as FLOAT. Never store arrays in columns. Never skip transactions on multi-step writes.** These three cause production incidents that wake you up at 3am.
