# MySQL — Comprehensive Reference Guide

> A deep, practical reference covering MySQL specifically.
> Covers installation, configuration, data types, SQL dialect differences,
> storage engines, user management, performance, replication, and production patterns.
> Companion to the SQL Reference — read that first for general SQL concepts.

---

## Table of Contents

1. [MySQL vs PostgreSQL — Key Differences](#1-mysql-vs-postgresql--key-differences)
2. [Installation and Setup](#2-installation-and-setup)
3. [The MySQL CLI](#3-the-mysql-cli)
4. [Data Types — MySQL Specifics](#4-data-types--mysql-specifics)
5. [DDL — MySQL Specifics](#5-ddl--mysql-specifics)
6. [DML — MySQL Specifics](#6-dml--mysql-specifics)
7. [String Functions — MySQL](#7-string-functions--mysql)
8. [Date and Time Functions — MySQL](#8-date-and-time-functions--mysql)
9. [Control Flow Functions](#9-control-flow-functions)
10. [Storage Engines](#10-storage-engines)
11. [Indexes — MySQL Deep Reference](#11-indexes--mysql-deep-reference)
12. [Transactions and Locking](#12-transactions-and-locking)
13. [User Management and Permissions](#13-user-management-and-permissions)
14. [Database Administration](#14-database-administration)
15. [Performance and Query Optimisation](#15-performance-and-query-optimisation)
16. [MySQL Configuration](#16-mysql-configuration)
17. [Backup and Restore](#17-backup-and-restore)
18. [Replication](#18-replication)
19. [MySQL with Node.js and Java](#19-mysql-with-nodejs-and-java)
20. [Common Pitfalls and Gotchas](#20-common-pitfalls-and-gotchas)

---

## 1. MySQL vs PostgreSQL — Key Differences

Understanding where MySQL and PostgreSQL diverge prevents bugs when switching between them or reading docs for the wrong database.

### 1.1 Syntax Differences

| Feature | MySQL | PostgreSQL |
|---|---|---|
| String quoting | Single `'` or double `"` quotes | Single `'` only (double = identifier) |
| Identifier quoting | Backticks `` ` `` | Double quotes `"` |
| Auto-increment | `AUTO_INCREMENT` | `SERIAL` / `BIGSERIAL` |
| Boolean type | `TINYINT(1)` (no real BOOL) | Native `BOOLEAN` |
| Limit/offset | `LIMIT 10 OFFSET 20` | Same (also `FETCH NEXT`) |
| String concat | `CONCAT(a, b)` | `a || b` or `CONCAT(a, b)` |
| Upsert | `INSERT ... ON DUPLICATE KEY UPDATE` | `INSERT ... ON CONFLICT DO UPDATE` |
| Group by rules | Loose (non-standard) | Strict (standard) |
| Case sensitivity | Case-insensitive by default | Case-sensitive |
| JSON support | JSON type (MySQL 5.7+) | JSONB (richer, faster) |
| Arrays | Not supported | Native arrays |
| Window functions | MySQL 8.0+ | Full support |
| CTEs | MySQL 8.0+ | Full support |
| Full-text search | Built-in FULLTEXT indexes | `tsvector`/`tsquery` |

### 1.2 Behavioural Differences

**GROUP BY** — MySQL historically allowed non-aggregated columns in SELECT that aren't in GROUP BY (`ONLY_FULL_GROUP_BY` mode was off by default). PostgreSQL is strict — every non-aggregated SELECT column must be in GROUP BY. MySQL 5.7.5+ enables `ONLY_FULL_GROUP_BY` by default, but you may encounter legacy code without it.

```sql
-- MySQL (older default — works but non-standard):
SELECT user_id, email, COUNT(*) FROM orders GROUP BY user_id;
-- email is not in GROUP BY — MySQL picks an arbitrary email per group

-- PostgreSQL (and MySQL with ONLY_FULL_GROUP_BY):
-- ERROR: email must appear in GROUP BY or aggregate function
```

**NULL handling in CONCAT** — MySQL's `CONCAT()` returns NULL if any argument is NULL. PostgreSQL's `||` also returns NULL, but `CONCAT()` treats NULL as empty string.

```sql
-- MySQL
SELECT CONCAT('Hello', NULL, 'World');  -- NULL
SELECT CONCAT_WS(' ', 'Hello', NULL, 'World');  -- 'Hello World' (NULL-safe)

-- PostgreSQL
SELECT 'Hello' || NULL || 'World';  -- NULL
SELECT CONCAT('Hello', NULL, 'World');  -- 'HelloWorld' (NULL treated as '')
```

**Transactions** — MySQL defaults to `autocommit = 1` (every statement is its own transaction). PostgreSQL defaults to autocommit too, but behaves more predictably with explicit transactions.

**Case sensitivity in string comparisons** — MySQL string comparisons are case-insensitive by default (depends on collation). PostgreSQL is case-sensitive.

```sql
-- MySQL (with default utf8mb4_general_ci collation)
SELECT * FROM users WHERE email = 'USER@EXAMPLE.COM';  -- finds 'user@example.com'

-- PostgreSQL
SELECT * FROM users WHERE email = 'USER@EXAMPLE.COM';  -- finds nothing
SELECT * FROM users WHERE email ILIKE 'user@example.com';  -- case-insensitive
```

---

## 2. Installation and Setup

### 2.1 Install on Ubuntu/Debian

```bash
# Update package index
sudo apt update

# Install MySQL server
sudo apt install mysql-server -y

# Check status
sudo systemctl status mysql

# Enable on boot
sudo systemctl enable mysql

# Run the security script (set root password, remove test db, etc.)
sudo mysql_secure_installation
```

### 2.2 Install on macOS

```bash
# Using Homebrew
brew install mysql

# Start the service
brew services start mysql

# Secure the installation
mysql_secure_installation
```

### 2.3 MySQL with Docker (Development)

```yaml
# docker-compose.yml
services:
  mysql:
    image: mysql:8.0
    container_name: mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: myapp
      MYSQL_USER: appuser
      MYSQL_PASSWORD: apppassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql  # runs on first start

volumes:
  mysql_data:
```

```bash
docker compose up -d
docker exec -it mysql mysql -u root -p
```

### 2.4 First Login

```bash
# Connect as root (no password on fresh install — use sudo)
sudo mysql

# Or with password
mysql -u root -p

# Connect to a specific database
mysql -u root -p myapp

# Connect to a remote server
mysql -h hostname -P 3306 -u username -p database_name
```

---

## 3. The MySQL CLI

### 3.1 Essential CLI Commands

```sql
-- Show databases
SHOW DATABASES;

-- Select a database
USE database_name;

-- Show current database
SELECT DATABASE();

-- Show tables
SHOW TABLES;

-- Describe a table (show column structure)
DESCRIBE tablename;
DESC tablename;          -- shorthand

-- Show table definition (full CREATE TABLE statement)
SHOW CREATE TABLE tablename;

-- Show indexes on a table
SHOW INDEX FROM tablename;

-- Show all running processes
SHOW PROCESSLIST;
SHOW FULL PROCESSLIST;  -- includes full query text

-- Kill a running query
KILL process_id;

-- Show server status variables
SHOW STATUS;
SHOW STATUS LIKE 'Threads%';   -- filter by pattern

-- Show server configuration variables
SHOW VARIABLES;
SHOW VARIABLES LIKE 'max_connections';

-- Show storage engines
SHOW ENGINES;

-- Show warnings from last statement
SHOW WARNINGS;

-- Show errors from last statement
SHOW ERRORS;
```

### 3.2 CLI Options

```bash
# Execute a single query and exit
mysql -u root -p -e "SHOW DATABASES;"

# Execute a SQL file
mysql -u root -p database_name < script.sql

# Output in vertical format (one column per line — useful for wide rows)
mysql -u root -p --vertical -e "SELECT * FROM users LIMIT 1;"

# Suppress the column header
mysql -u root -p --skip-column-names -e "SELECT email FROM users;"

# Output as CSV
mysql -u root -p -e "SELECT * FROM users;" | sed 's/\t/,/g'

# Execute with no auto-reconnect (safer for long operations)
mysql -u root -p --disable-reconnect database_name
```

### 3.3 Useful CLI Shortcuts

```
\G   — display results vertically (SELECT * FROM users\G)
\c   — cancel current input
\q   — quit
\!   — execute a shell command (\! ls)
\s   — server status
\h   — help
```

---

## 4. Data Types — MySQL Specifics

### 4.1 Integer Types

```sql
TINYINT     -- 1 byte, -128 to 127 (or 0 to 255 UNSIGNED)
SMALLINT    -- 2 bytes, -32,768 to 32,767
MEDIUMINT   -- 3 bytes, -8.3M to 8.3M
INT         -- 4 bytes, -2.1B to 2.1B
BIGINT      -- 8 bytes, very large

-- UNSIGNED: shifts range to start at 0
INT UNSIGNED        -- 0 to 4.3 billion (doubles positive range)
BIGINT UNSIGNED     -- 0 to 18 quintillion

-- AUTO_INCREMENT: MySQL's auto-incrementing primary key
id INT AUTO_INCREMENT PRIMARY KEY
id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY  -- for large tables
```

> **Note on `INT(11)`:** The number in parentheses for integer types is a **display width hint** — it has nothing to do with storage size or the range of values. `INT(1)` and `INT(11)` store identical values. This syntax is deprecated in MySQL 8.0.

### 4.2 Decimal and Float Types

```sql
DECIMAL(p, s)   -- exact decimal. p = total digits, s = digits after decimal
NUMERIC(p, s)   -- same as DECIMAL
FLOAT           -- 4-byte floating point (approximate — avoid for money)
DOUBLE          -- 8-byte floating point (approximate — avoid for money)

-- For money: always DECIMAL
price DECIMAL(10, 2)      -- up to 99,999,999.99
amount DECIMAL(15, 4)     -- high-precision financial calculations
```

### 4.3 String Types

```sql
CHAR(n)         -- fixed length, n characters, padded with spaces
VARCHAR(n)      -- variable length, up to n characters (max 65,535)
TINYTEXT        -- up to 255 bytes
TEXT            -- up to 65,535 bytes (~64KB)
MEDIUMTEXT      -- up to 16,777,215 bytes (~16MB)
LONGTEXT        -- up to 4,294,967,295 bytes (~4GB)
TINYBLOB        -- binary version of TINYTEXT
BLOB            -- binary version of TEXT
MEDIUMBLOB      -- binary version of MEDIUMTEXT
LONGBLOB        -- binary version of LONGTEXT

-- VARCHAR vs TEXT:
-- VARCHAR can be indexed normally (up to index size limit)
-- TEXT columns cannot be fully indexed without a prefix length
-- VARCHAR is stored inline with the row; TEXT is stored separately for large values
-- For most string columns: VARCHAR(255) or VARCHAR(1000)
-- For long content (articles, descriptions): TEXT
```

### 4.4 Date and Time Types

```sql
DATE            -- 'YYYY-MM-DD'
TIME            -- 'HH:MM:SS'
DATETIME        -- 'YYYY-MM-DD HH:MM:SS' — no timezone info
TIMESTAMP       -- like DATETIME but stored as UTC, converted on read
YEAR            -- 1901 to 2155

-- DATETIME vs TIMESTAMP:
-- TIMESTAMP is timezone-aware (stored UTC, displayed in session timezone)
-- TIMESTAMP range: 1970-01-01 to 2038-01-19 (Y2K38 problem!)
-- DATETIME has no timezone but larger range: 1000-01-01 to 9999-12-31
-- For application timestamps: DATETIME (avoid Y2K38) or TIMESTAMP if you need TZ conversion
-- For server-side audit trails: TIMESTAMP (always UTC)

-- Auto-update timestamp
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

### 4.5 ENUM and SET

```sql
-- ENUM: stores one value from a predefined list
status ENUM('active', 'inactive', 'suspended') DEFAULT 'active'
gender ENUM('M', 'F', 'other')

-- SET: stores zero or more values from a predefined list (bitmask internally)
permissions SET('read', 'write', 'admin')

-- ENUM is stored as an integer (index into the list) — compact
-- Be careful with ENUM: adding values requires ALTER TABLE
-- For flexibility, TEXT + CHECK CONSTRAINT is often better than ENUM

-- Query ENUM by value or index
SELECT * FROM users WHERE status = 'active';
SELECT * FROM users WHERE status = 1;  -- 1 = 'active' (1-indexed)
```

### 4.6 JSON Type (MySQL 5.7+)

```sql
metadata JSON

-- Insert
INSERT INTO events (data) VALUES ('{"user_id": 42, "action": "login"}');

-- Extract value
SELECT data->>'$.user_id' FROM events;          -- returns string
SELECT data->'$.user_id' FROM events;           -- returns JSON value
SELECT JSON_EXTRACT(data, '$.user_id') FROM events;

-- Check if key exists
SELECT * FROM events WHERE JSON_CONTAINS_PATH(data, 'one', '$.user_id');

-- Filter on JSON value
SELECT * FROM events WHERE data->>'$.action' = 'login';

-- Update JSON
UPDATE events SET data = JSON_SET(data, '$.processed', true) WHERE id = 1;
UPDATE events SET data = JSON_REMOVE(data, '$.temp_key') WHERE id = 1;

-- Index a JSON field (virtual generated column + index)
ALTER TABLE events ADD COLUMN user_id INT GENERATED ALWAYS AS (data->>'$.user_id') STORED;
CREATE INDEX ON events (user_id);
```

### 4.7 Boolean (MySQL)

MySQL has no true BOOLEAN type. It uses `TINYINT(1)` as an alias.

```sql
-- These are identical in MySQL:
is_active BOOLEAN
is_active TINYINT(1)

-- TRUE and FALSE are aliases for 1 and 0:
INSERT INTO users (is_active) VALUES (TRUE);   -- stores 1
INSERT INTO users (is_active) VALUES (FALSE);  -- stores 0
SELECT * FROM users WHERE is_active = TRUE;    -- same as = 1
SELECT * FROM users WHERE is_active;           -- also works (non-zero = true)
```

---

## 5. DDL — MySQL Specifics

### 5.1 CREATE TABLE with MySQL Options

```sql
CREATE TABLE users (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email       VARCHAR(255) NOT NULL,
    full_name   VARCHAR(150) NOT NULL,
    status      ENUM('active','inactive','suspended') DEFAULT 'active',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY  uq_users_email (email),
    INDEX       idx_users_status (status)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
```

**Engine, charset, and collation explained:**

`ENGINE=InnoDB` — Always use InnoDB for application tables. It supports transactions, foreign keys, and row-level locking.

`CHARSET=utf8mb4` — Always use `utf8mb4`, NOT `utf8`. MySQL's `utf8` is a 3-byte encoding that can't store emoji (which are 4 bytes). `utf8mb4` is the true UTF-8 encoding.

`COLLATE=utf8mb4_unicode_ci` — `ci` = case-insensitive. Use `utf8mb4_unicode_ci` for general purpose (proper Unicode comparison rules). Use `utf8mb4_bin` when you need case-sensitive and binary comparisons.

### 5.2 ALTER TABLE — MySQL Specifics

```sql
-- Add column
ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email;   -- position hint
ALTER TABLE users ADD COLUMN score INT DEFAULT 0 FIRST;        -- make it first column

-- Modify column (change type or constraints)
ALTER TABLE users MODIFY COLUMN phone VARCHAR(30) NOT NULL;

-- Change column (rename + modify)
ALTER TABLE users CHANGE COLUMN phone mobile_number VARCHAR(30);

-- Drop column
ALTER TABLE users DROP COLUMN score;

-- Add index
ALTER TABLE users ADD INDEX idx_status (status);
ALTER TABLE users ADD UNIQUE KEY uq_phone (phone);
ALTER TABLE users ADD FULLTEXT INDEX ft_name (full_name);

-- Drop index
ALTER TABLE users DROP INDEX idx_status;

-- Add foreign key
ALTER TABLE orders ADD CONSTRAINT fk_orders_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;

-- Drop foreign key
ALTER TABLE orders DROP FOREIGN KEY fk_orders_user;

-- Change storage engine
ALTER TABLE old_table ENGINE = InnoDB;

-- Change charset
ALTER TABLE users CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Rename table
RENAME TABLE old_name TO new_name;
ALTER TABLE old_name RENAME TO new_name;
```

### 5.3 AUTO_INCREMENT Details

```sql
-- Check current AUTO_INCREMENT value
SHOW CREATE TABLE users;   -- shows AUTO_INCREMENT=N in the output

-- Reset AUTO_INCREMENT (only if new value > current max)
ALTER TABLE users AUTO_INCREMENT = 1000;

-- Get last inserted auto-increment ID (in the same connection)
SELECT LAST_INSERT_ID();

-- In application code after INSERT:
-- MySQL: LAST_INSERT_ID()
-- The value is connection-specific and safe for concurrent use
```

### 5.4 Generated (Computed) Columns

```sql
-- Virtual: computed on read, not stored
ALTER TABLE products ADD COLUMN revenue DECIMAL(12,2)
    GENERATED ALWAYS AS (price * stock_qty) VIRTUAL;

-- Stored: computed and stored on write (can be indexed)
ALTER TABLE products ADD COLUMN full_name VARCHAR(300)
    GENERATED ALWAYS AS (CONCAT(first_name, ' ', last_name)) STORED;

CREATE INDEX idx_full_name ON products(full_name);  -- index on stored generated column
```

---

## 6. DML — MySQL Specifics

### 6.1 INSERT with MySQL Extensions

```sql
-- INSERT IGNORE — skip rows that violate constraints (no error)
INSERT IGNORE INTO tags (name) VALUES ('tech'), ('devops'), ('tech');
-- 'tech' appears twice — second row is silently ignored

-- INSERT ... ON DUPLICATE KEY UPDATE (upsert)
INSERT INTO page_views (page_id, views)
VALUES (42, 1)
ON DUPLICATE KEY UPDATE views = views + 1;
-- If page_id 42 exists: increment views
-- If not: insert the row

-- Multiple row upsert
INSERT INTO product_stats (product_id, total_sales, last_sale_at)
VALUES (1, 100, NOW()), (2, 50, NOW())
ON DUPLICATE KEY UPDATE
    total_sales = total_sales + VALUES(total_sales),
    last_sale_at = VALUES(last_sale_at);
-- VALUES(column) refers to the value that WOULD have been inserted

-- REPLACE INTO — delete + insert (use ON DUPLICATE KEY instead)
-- Dangerous with foreign keys — avoid
REPLACE INTO settings (key, value) VALUES ('theme', 'dark');
```

### 6.2 UPDATE with ORDER BY and LIMIT

MySQL allows `ORDER BY` and `LIMIT` in single-table `UPDATE` and `DELETE`:

```sql
-- Update the 10 oldest inactive accounts
UPDATE users
SET status = 'archived'
WHERE status = 'inactive'
ORDER BY created_at ASC
LIMIT 10;

-- Delete the 100 oldest log entries
DELETE FROM logs
ORDER BY created_at ASC
LIMIT 100;
```

### 6.3 Multi-Table UPDATE and DELETE

MySQL supports updating and deleting across multiple tables in one statement:

```sql
-- Multi-table UPDATE
UPDATE orders o
JOIN customers c ON c.id = o.customer_id
SET o.status = 'cancelled', c.cancelled_orders = c.cancelled_orders + 1
WHERE o.created_at < NOW() - INTERVAL 30 DAY
  AND o.status = 'pending';

-- Multi-table DELETE
DELETE o, oi
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.status = 'cancelled'
  AND o.created_at < NOW() - INTERVAL 90 DAY;
-- Deletes from both orders and order_items simultaneously
```

### 6.4 LOAD DATA INFILE — Bulk Import

```sql
-- Load data from a CSV file (very fast bulk import)
LOAD DATA INFILE '/var/lib/mysql-files/users.csv'
INTO TABLE users
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS  -- skip header row
(email, full_name, status);

-- From client file (not server-side file)
LOAD DATA LOCAL INFILE '/path/on/client/users.csv'
INTO TABLE users
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

---

## 7. String Functions — MySQL

```sql
-- Length
LENGTH(str)                   -- byte length
CHAR_LENGTH(str)              -- character length (different for multibyte)

-- Case
UPPER(str), LOWER(str)
UCASE(str), LCASE(str)        -- aliases

-- Trimming
TRIM(str)
LTRIM(str), RTRIM(str)
TRIM(LEADING 'x' FROM str)   -- trim specific character from left
TRIM(TRAILING 'x' FROM str)  -- trim from right
TRIM(BOTH 'x' FROM str)      -- trim from both sides

-- Substring
SUBSTRING(str, pos, len)      -- 1-indexed
SUBSTR(str, pos, len)         -- alias
MID(str, pos, len)            -- alias
LEFT(str, len)
RIGHT(str, len)

-- Search
LOCATE(substr, str)           -- position of substr in str (0 if not found)
LOCATE(substr, str, pos)      -- start searching from pos
INSTR(str, substr)            -- same as LOCATE but arguments reversed
POSITION(substr IN str)       -- SQL standard syntax

-- Replace
REPLACE(str, from, to)        -- replace all occurrences
INSERT(str, pos, len, newstr) -- replace len chars at pos with newstr

-- Padding
LPAD(str, len, padstr)        -- left-pad to total length len
RPAD(str, len, padstr)        -- right-pad

-- Repetition
REPEAT(str, count)

-- Reversal
REVERSE(str)

-- Concatenation
CONCAT(str1, str2, ...)       -- NULL if any arg is NULL
CONCAT_WS(sep, str1, str2, ...)  -- with separator, skips NULLs

-- Comparison
STRCMP(str1, str2)            -- 0 if equal, -1 or 1 otherwise
LIKE                          -- pattern matching (case-insensitive with ci collation)
REGEXP / RLIKE                -- regex match

-- Encoding
HEX(str)                      -- hexadecimal representation
UNHEX(hex_str)                -- decode hex
TO_BASE64(str)                -- base64 encode
FROM_BASE64(str)              -- base64 decode

-- Formatting
FORMAT(number, decimals)      -- format number with commas: 1234567 → '1,234,567'

-- Other useful
FIELD(val, v1, v2, v3, ...)   -- returns position of val in list (useful in ORDER BY)
ELT(n, str1, str2, ...)       -- returns the nth string
FIND_IN_SET(str, strlist)     -- position in comma-separated list
GROUP_CONCAT(col ORDER BY col SEPARATOR ',')  -- aggregate into a string
```

### 7.1 GROUP_CONCAT — The MySQL Aggregation String

A MySQL-specific aggregate function that concatenates non-NULL values from a group into a single string:

```sql
-- Get all tags for each post as a comma-separated string
SELECT
    p.id,
    p.title,
    GROUP_CONCAT(t.name ORDER BY t.name SEPARATOR ', ') AS tags
FROM posts p
JOIN post_tags pt ON pt.post_id = p.id
JOIN tags t ON t.id = pt.tag_id
GROUP BY p.id, p.title;

-- With DISTINCT
GROUP_CONCAT(DISTINCT category ORDER BY category)

-- Control the max length (default is 1024 bytes)
SET SESSION group_concat_max_len = 65536;
```

---

## 8. Date and Time Functions — MySQL

```sql
-- Current date and time
NOW()                         -- current datetime: '2026-01-15 14:30:00'
CURDATE() / CURRENT_DATE()    -- current date: '2026-01-15'
CURTIME() / CURRENT_TIME()    -- current time: '14:30:00'
SYSDATE()                     -- like NOW() but evaluated at execution time per row
UTC_NOW() / UTC_TIMESTAMP()   -- current UTC datetime

-- Extraction
YEAR(date)
MONTH(date)
DAY(date) / DAYOFMONTH(date)
HOUR(time)
MINUTE(time)
SECOND(time)
DAYOFWEEK(date)               -- 1=Sunday, 7=Saturday
DAYOFYEAR(date)               -- 1–366
WEEKOFYEAR(date)
QUARTER(date)                 -- 1–4

EXTRACT(unit FROM date)       -- SQL standard extraction
-- Units: YEAR, MONTH, DAY, HOUR, MINUTE, SECOND, WEEK, QUARTER

-- Truncation (MySQL doesn't have DATE_TRUNC — use workarounds)
DATE(datetime)                -- extract date only: '2026-01-15'
TIME(datetime)                -- extract time only

-- For month truncation (PostgreSQL's DATE_TRUNC equivalent):
DATE_FORMAT(created_at, '%Y-%m-01')   -- first day of the month
STR_TO_DATE(DATE_FORMAT(created_at, '%Y-%m-01'), '%Y-%m-%d')  -- as DATE type

-- Arithmetic
DATE_ADD(date, INTERVAL n unit)
DATE_SUB(date, INTERVAL n unit)
ADDDATE(date, INTERVAL n unit)        -- alias for DATE_ADD
SUBDATE(date, INTERVAL n unit)        -- alias for DATE_SUB

-- Interval units: SECOND, MINUTE, HOUR, DAY, WEEK, MONTH, QUARTER, YEAR
-- Also compound: MINUTE_SECOND, HOUR_MINUTE, DAY_HOUR, YEAR_MONTH

NOW() + INTERVAL 7 DAY
NOW() - INTERVAL 30 MINUTE
DATE_ADD(NOW(), INTERVAL 1 MONTH)

-- Difference
DATEDIFF(date1, date2)        -- days between dates (date1 - date2)
TIMEDIFF(time1, time2)        -- time difference as HH:MM:SS
TIMESTAMPDIFF(unit, dt1, dt2) -- difference in specific unit
TIMESTAMPDIFF(DAY, created_at, NOW())    -- days since creation
TIMESTAMPDIFF(SECOND, start, end)        -- duration in seconds

-- Formatting
DATE_FORMAT(date, format)
-- Common format strings:
-- %Y — 4-digit year      %m — 2-digit month    %d — 2-digit day
-- %H — 24h hour          %i — minutes          %s — seconds
-- %W — weekday name      %M — month name
DATE_FORMAT(NOW(), '%Y-%m-%d')                 -- '2026-01-15'
DATE_FORMAT(NOW(), '%d/%m/%Y %H:%i')           -- '15/01/2026 14:30'
DATE_FORMAT(NOW(), '%W, %M %d, %Y')            -- 'Thursday, January 15, 2026'

-- Parsing strings to dates
STR_TO_DATE('15/01/2026', '%d/%m/%Y')          -- returns DATE
STR_TO_DATE('15-Jan-2026 14:30', '%d-%b-%Y %H:%i')

-- Unix timestamps
UNIX_TIMESTAMP()              -- current Unix timestamp
UNIX_TIMESTAMP(datetime)      -- convert datetime to Unix timestamp
FROM_UNIXTIME(ts)             -- convert Unix timestamp to datetime
FROM_UNIXTIME(ts, '%Y-%m-%d') -- with format

-- Last day of month
LAST_DAY(date)                -- '2026-01-31'

-- Week functions
WEEK(date)                    -- week number (0-53)
YEARWEEK(date)                -- year and week: 202602
```

---

## 9. Control Flow Functions

### 9.1 IF

```sql
IF(condition, true_value, false_value)

-- Simple ternary
SELECT IF(stock_qty > 0, 'In Stock', 'Out of Stock') AS availability FROM products;

-- In aggregations
SELECT
    COUNT(*) AS total,
    SUM(IF(status = 'active', 1, 0)) AS active_count,
    SUM(IF(status = 'inactive', 1, 0)) AS inactive_count
FROM users;
```

### 9.2 IFNULL and NULLIF

```sql
IFNULL(expr, alternative)     -- return alternative if expr is NULL
NULLIF(expr, value)           -- return NULL if expr = value, else expr

-- IFNULL is MySQL's name for COALESCE with two arguments
IFNULL(phone, 'No phone')     -- same as COALESCE(phone, 'No phone')
COALESCE(phone, 'No phone')   -- standard SQL — prefer this for portability

-- NULLIF for division by zero
total / NULLIF(count, 0)      -- returns NULL instead of error
```

### 9.3 CASE

Standard SQL CASE works in MySQL (see SQL Reference Section 17). MySQL also has `IF()` as a function alternative, but `CASE` is preferred for readability and portability.

### 9.4 ELT and FIELD

```sql
-- ELT: returns the nth element from a list
ELT(2, 'apple', 'banana', 'cherry')   -- 'banana'

-- FIELD: returns the position of a value in a list (useful for custom ORDER BY)
SELECT * FROM products
ORDER BY FIELD(status, 'active', 'pending', 'inactive', 'deleted');
-- Rows in custom sort order: active first, deleted last
```

---

## 10. Storage Engines

### 10.1 InnoDB — The Default Choice

InnoDB is the default and correct choice for almost all production tables. It provides:

- **ACID transactions** — `BEGIN`, `COMMIT`, `ROLLBACK` work correctly
- **Foreign key constraints** — enforced at the engine level
- **Row-level locking** — high concurrency with minimal contention
- **MVCC** — readers don't block writers
- **Crash recovery** — write-ahead log (WAL) ensures durability
- **Full-text search** — available since MySQL 5.6

```sql
-- Create an InnoDB table
CREATE TABLE orders (...) ENGINE=InnoDB;

-- Check a table's engine
SHOW TABLE STATUS WHERE Name = 'orders';

-- Convert a table to InnoDB
ALTER TABLE old_table ENGINE=InnoDB;
```

### 10.2 MyISAM — Legacy Only

MyISAM predates InnoDB. It's faster for read-heavy, non-concurrent workloads with simple full-text search requirements. Do not use for new tables.

Limitations:
- No transactions
- No foreign keys
- Table-level locking (one writer blocks all readers)
- No crash recovery — corruption risk on unclean shutdown

The only reason to encounter MyISAM today is in legacy databases. Migrate to InnoDB.

### 10.3 MEMORY — Volatile Cache

All data stored in RAM. Lightning fast for reads and writes. Data is completely lost on server restart.

```sql
CREATE TABLE session_cache (
    session_id VARCHAR(128) PRIMARY KEY,
    data TEXT,
    expires_at DATETIME
) ENGINE=MEMORY;
```

Use cases: temporary working tables during complex data processing, session caches where loss is acceptable, performance testing.

### 10.4 ARCHIVE — Compressed Read-Only History

Stores rows in compressed format. Supports only `INSERT` and `SELECT` — no `UPDATE` or `DELETE`. Extremely compact for write-once audit data.

```sql
CREATE TABLE audit_log_archive (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_data TEXT,
    created_at DATETIME
) ENGINE=ARCHIVE;
```

### 10.5 Checking and Comparing Engines

```sql
-- Show all supported storage engines
SHOW ENGINES;

-- Check which engine a table uses
SHOW TABLE STATUS LIKE 'orders'\G
-- Look for the Engine field in the output

-- Show all tables and their engines in a database
SELECT
    table_name,
    engine,
    table_rows,
    ROUND(data_length / 1024 / 1024, 2) AS data_mb,
    ROUND(index_length / 1024 / 1024, 2) AS index_mb
FROM information_schema.tables
WHERE table_schema = DATABASE()
ORDER BY data_length DESC;
```

---

## 11. Indexes — MySQL Deep Reference

### 11.1 Index Types in MySQL

**B-Tree** — Default index type. Supports `=`, `<`, `<=`, `>`, `>=`, `BETWEEN`, `LIKE 'prefix%'`. Stored in a balanced tree structure. Works for all data types.

**Hash** — Only supports exact equality (`=`). Cannot be used for ranges or sorting. Available in MEMORY engine; InnoDB creates adaptive hash indexes automatically — you don't create these manually.

**FULLTEXT** — For text search. Supports `MATCH ... AGAINST` queries. InnoDB supports FULLTEXT since MySQL 5.6.

**SPATIAL** — For geometric/geographic data types (`POINT`, `POLYGON`, etc.).

### 11.2 Creating Indexes

```sql
-- B-Tree index (default)
CREATE INDEX idx_email ON users(email);
CREATE INDEX idx_status_created ON orders(status, created_at);

-- Unique index
CREATE UNIQUE INDEX uq_email ON users(email);

-- Partial index using prefix (for TEXT/BLOB columns which can't be fully indexed)
CREATE INDEX idx_bio ON users(bio(100));   -- index first 100 characters

-- Full-text index
CREATE FULLTEXT INDEX ft_body ON posts(title, body);

-- In CREATE TABLE
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),                        -- regular index
    UNIQUE KEY uq_sku (sku),                          -- unique index
    FULLTEXT INDEX ft_name (name)                     -- full-text index
);
```

### 11.3 Full-Text Search

```sql
-- Basic full-text search
SELECT * FROM posts
WHERE MATCH(title, body) AGAINST('database design');

-- In boolean mode (supports +, -, *, "")
SELECT * FROM posts
WHERE MATCH(title, body) AGAINST('+database -tutorial' IN BOOLEAN MODE);
-- +word = must include, -word = must exclude, * = wildcard suffix

SELECT * FROM posts
WHERE MATCH(title, body) AGAINST('"database design"' IN BOOLEAN MODE);
-- Phrase search with quotes

-- With relevance score
SELECT
    id,
    title,
    MATCH(title, body) AGAINST('database') AS relevance
FROM posts
WHERE MATCH(title, body) AGAINST('database')
ORDER BY relevance DESC;

-- Natural language mode (default — relevance-ranked, stops words removed)
SELECT * FROM posts
WHERE MATCH(title, body) AGAINST('designing databases' IN NATURAL LANGUAGE MODE);
```

### 11.4 Index Hints

Sometimes MySQL's query planner chooses a non-optimal index. You can hint or force it:

```sql
-- Hint: suggest using this index
SELECT * FROM orders USE INDEX (idx_status) WHERE status = 'pending';

-- Hint: ignore this index
SELECT * FROM orders IGNORE INDEX (idx_created_at) WHERE status = 'pending';

-- Force: must use this index
SELECT * FROM orders FORCE INDEX (idx_status) WHERE status = 'pending';
```

Use hints sparingly — they lock in a query to a specific index even when the data distribution changes. Better to trust the planner and fix the query or index if needed.

### 11.5 Invisible Indexes (MySQL 8.0+)

An invisible index is maintained by the engine but not used by the query planner. Use this to test whether dropping an index would hurt performance — make it invisible first, test, then drop if safe.

```sql
-- Make an index invisible (planner ignores it, engine still maintains it)
ALTER TABLE users ALTER INDEX idx_phone INVISIBLE;

-- Make it visible again
ALTER TABLE users ALTER INDEX idx_phone VISIBLE;

-- Create as invisible from the start
CREATE INDEX idx_test ON users(phone) INVISIBLE;
```

---

## 12. Transactions and Locking

### 12.1 Transaction Basics

```sql
-- MySQL defaults to autocommit ON (every statement is its own transaction)
SHOW VARIABLES LIKE 'autocommit';

-- Disable autocommit for the session
SET autocommit = 0;

-- Or use explicit transaction syntax
START TRANSACTION;     -- begins a transaction (disables autocommit for this block)
BEGIN;                 -- alias for START TRANSACTION

COMMIT;                -- save all changes
ROLLBACK;              -- undo all changes since START TRANSACTION

-- Savepoints
SAVEPOINT before_risky_operation;
-- ... some statements ...
ROLLBACK TO SAVEPOINT before_risky_operation;   -- undo back to savepoint
RELEASE SAVEPOINT before_risky_operation;        -- discard the savepoint
```

### 12.2 Isolation Levels

```sql
-- Set for the current session
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;  -- almost never use

-- Set for the next transaction only
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- MySQL default: REPEATABLE READ
-- This is stricter than PostgreSQL's default (READ COMMITTED)
-- In MySQL REPEATABLE READ, reads within a transaction see the same snapshot
-- but writes can still cause phantom rows in some edge cases
-- SERIALIZABLE prevents this but has the highest locking overhead
```

### 12.3 Locking

```sql
-- Shared (read) lock — other transactions can read but not write
SELECT * FROM accounts WHERE id = 42 LOCK IN SHARE MODE;

-- Exclusive (write) lock — other transactions can neither read nor write
SELECT * FROM accounts WHERE id = 42 FOR UPDATE;

-- FOR UPDATE with SKIP LOCKED — skip rows locked by other transactions
-- Perfect for job queues: each worker gets a different row
SELECT * FROM jobs
WHERE status = 'pending'
ORDER BY created_at
LIMIT 1
FOR UPDATE SKIP LOCKED;

-- NOWAIT — fail immediately instead of waiting for lock
SELECT * FROM accounts WHERE id = 42 FOR UPDATE NOWAIT;

-- Table-level locking (rarely needed with InnoDB)
LOCK TABLES users READ, orders WRITE;
UNLOCK TABLES;
```

### 12.4 Deadlock Handling

MySQL automatically detects deadlocks and kills one transaction (error 1213). Always handle this in application code:

```javascript
// Node.js: retry on deadlock
async function executeWithRetry(queryFn, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await queryFn();
        } catch (err) {
            if (err.code === 'ER_LOCK_DEADLOCK' && attempt < maxRetries) {
                await new Promise(r => setTimeout(r, 100 * attempt));  // backoff
                continue;
            }
            throw err;
        }
    }
}
```

---

## 13. User Management and Permissions

### 13.1 Creating and Managing Users

```sql
-- Create a user
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'securepassword';
CREATE USER 'appuser'@'%' IDENTIFIED BY 'securepassword';  -- any host
CREATE USER 'appuser'@'192.168.1.%' IDENTIFIED BY 'pass';  -- subnet

-- View users
SELECT user, host FROM mysql.user;

-- Change password
ALTER USER 'appuser'@'localhost' IDENTIFIED BY 'newpassword';
SET PASSWORD FOR 'appuser'@'localhost' = 'newpassword';

-- Drop user
DROP USER 'appuser'@'localhost';
DROP USER IF EXISTS 'appuser'@'localhost';

-- Rename user
RENAME USER 'old'@'localhost' TO 'new'@'localhost';
```

### 13.2 Granting Permissions

```sql
-- Grant all permissions on a database
GRANT ALL PRIVILEGES ON myapp.* TO 'appuser'@'localhost';

-- Grant specific permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON myapp.* TO 'appuser'@'localhost';

-- Grant on specific table
GRANT SELECT ON myapp.products TO 'readonly'@'%';

-- Grant on specific columns
GRANT SELECT (id, name, price) ON myapp.products TO 'limited'@'%';

-- Grant with option to pass privileges to others (admin use)
GRANT ALL ON myapp.* TO 'admin'@'localhost' WITH GRANT OPTION;

-- Apply changes immediately
FLUSH PRIVILEGES;

-- Show grants for a user
SHOW GRANTS FOR 'appuser'@'localhost';
```

### 13.3 Revoking Permissions

```sql
REVOKE INSERT, UPDATE ON myapp.* FROM 'appuser'@'localhost';
REVOKE ALL PRIVILEGES ON myapp.* FROM 'appuser'@'localhost';
REVOKE GRANT OPTION ON myapp.* FROM 'appuser'@'localhost';
```

### 13.4 Roles (MySQL 8.0+)

```sql
-- Create a role
CREATE ROLE 'app_read', 'app_write', 'app_admin';

-- Grant permissions to the role
GRANT SELECT ON myapp.* TO 'app_read';
GRANT SELECT, INSERT, UPDATE, DELETE ON myapp.* TO 'app_write';
GRANT ALL ON myapp.* TO 'app_admin';

-- Assign role to user
GRANT 'app_write' TO 'appuser'@'localhost';

-- Set default roles (activated automatically on login)
SET DEFAULT ROLE 'app_write' TO 'appuser'@'localhost';

-- Activate a role in the current session
SET ROLE 'app_read';
SET ROLE ALL;   -- activate all granted roles

-- Show current active roles
SELECT CURRENT_ROLE();
```

### 13.5 Recommended User Setup

```sql
-- Application user: only what it needs
CREATE USER 'app'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON myapp.* TO 'app'@'localhost';

-- Read-only user for reporting
CREATE USER 'reporter'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT ON myapp.* TO 'reporter'@'%';

-- Migration user: can also modify schema
CREATE USER 'migrator'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON myapp.* TO 'migrator'@'localhost';

-- Never use root for application connections
```

---

## 14. Database Administration

### 14.1 Database Operations

```sql
-- Create database
CREATE DATABASE myapp;
CREATE DATABASE myapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS myapp;

-- Drop database
DROP DATABASE myapp;
DROP DATABASE IF EXISTS myapp;

-- Show databases
SHOW DATABASES;

-- Show database size
SELECT
    table_schema AS database_name,
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
GROUP BY table_schema
ORDER BY size_mb DESC;
```

### 14.2 Table Maintenance

```sql
-- Check table for errors
CHECK TABLE users;
CHECK TABLE users EXTENDED;  -- thorough check

-- Repair a corrupted table (MyISAM only)
REPAIR TABLE users;

-- Optimise a table (rebuild, reclaim space after many deletes)
OPTIMIZE TABLE users;

-- Analyse table statistics (helps query planner)
ANALYZE TABLE users;

-- Show table status
SHOW TABLE STATUS LIKE 'orders'\G
```

### 14.3 Process Management

```sql
-- See all running queries
SHOW PROCESSLIST;
SHOW FULL PROCESSLIST;   -- shows full query text (not truncated)

-- Or via information_schema (more detail)
SELECT
    id,
    user,
    host,
    db,
    command,
    time AS seconds,
    state,
    LEFT(info, 100) AS query
FROM information_schema.processlist
WHERE command != 'Sleep'
ORDER BY time DESC;

-- Kill a specific query
KILL QUERY 12345;    -- kill the query but keep the connection
KILL 12345;          -- kill the connection entirely
```

### 14.4 Binary Logs

MySQL's binary log records all changes to the database. Essential for replication and point-in-time recovery.

```sql
-- Check if binary logging is enabled
SHOW VARIABLES LIKE 'log_bin';

-- List binary log files
SHOW BINARY LOGS;

-- View binary log events
SHOW BINLOG EVENTS IN 'mysql-bin.000001' LIMIT 20;

-- Purge old binary logs (free up disk space)
PURGE BINARY LOGS BEFORE NOW() - INTERVAL 7 DAY;
PURGE BINARY LOGS TO 'mysql-bin.000010';  -- delete all before this file
```

### 14.5 Server Variables

```sql
-- View all variables
SHOW VARIABLES;
SHOW GLOBAL VARIABLES;
SHOW SESSION VARIABLES;

-- View specific variables
SHOW VARIABLES LIKE 'max_connections';
SHOW VARIABLES LIKE 'innodb%';    -- all InnoDB variables

-- Change a variable at runtime (session level)
SET SESSION max_allowed_packet = 67108864;   -- 64MB

-- Change globally (affects all new connections)
SET GLOBAL max_connections = 500;

-- Important variables to know:
-- max_connections     — max simultaneous connections (default 151)
-- innodb_buffer_pool_size — InnoDB cache (should be 70-80% of RAM)
-- max_allowed_packet  — max size of a single query/row packet
-- wait_timeout        — seconds before idle connection is closed
-- query_cache_size    — deprecated in MySQL 8.0 (removed)
-- slow_query_log      — enable slow query logging
-- long_query_time     — threshold for slow query log (seconds)
```

---

## 15. Performance and Query Optimisation

### 15.1 EXPLAIN

```sql
-- Basic EXPLAIN
EXPLAIN SELECT * FROM orders WHERE user_id = 42;

-- EXPLAIN with format options (MySQL 8.0+)
EXPLAIN FORMAT=TREE SELECT * FROM orders WHERE user_id = 42;
EXPLAIN FORMAT=JSON SELECT * FROM orders WHERE user_id = 42;

-- EXPLAIN ANALYZE (runs the query and shows actual timings — MySQL 8.0.18+)
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 42;
```

### 15.2 Reading EXPLAIN Output

```
id | select_type | table  | type | possible_keys | key          | rows | Extra
1  | SIMPLE      | orders | ref  | idx_user_id   | idx_user_id  | 15   | Using where
```

**Key columns:**

`type` — Join/access type (best to worst):
- `system` — single row table
- `const` — single row match via primary key or unique index
- `eq_ref` — one row from each joined table (best join type)
- `ref` — index lookup, may return multiple rows
- `range` — index range scan (BETWEEN, IN, >, <)
- `index` — full index scan (not ideal)
- `ALL` — full table scan (worst — needs an index)

`key` — The index actually used (NULL = no index used)

`rows` — Estimated number of rows examined (lower is better)

`Extra` — Important additional info:
- `Using index` — index covers all needed columns (fast)
- `Using where` — filter applied after index lookup
- `Using filesort` — sort operation (consider adding index)
- `Using temporary` — temp table created (expensive for large data)
- `Using index condition` — Index Condition Pushdown (ICP) optimisation

### 15.3 Slow Query Log

```sql
-- Enable slow query logging
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;      -- log queries taking more than 1 second
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';

-- Log queries not using indexes
SET GLOBAL log_queries_not_using_indexes = 'ON';

-- View the log location
SHOW VARIABLES LIKE 'slow_query_log_file';
```

Analyse the slow query log with `mysqldumpslow`:

```bash
# Top 10 slowest queries
mysqldumpslow -s t -t 10 /var/log/mysql/slow.log

# Top 10 by count (most frequent slow queries)
mysqldumpslow -s c -t 10 /var/log/mysql/slow.log
```

### 15.4 Performance Schema

MySQL's built-in performance monitoring:

```sql
-- Enable performance schema (usually on by default)
SHOW VARIABLES LIKE 'performance_schema';

-- Top queries by total execution time
SELECT
    DIGEST_TEXT AS query,
    COUNT_STAR AS executions,
    ROUND(SUM_TIMER_WAIT / 1000000000000, 2) AS total_seconds,
    ROUND(AVG_TIMER_WAIT / 1000000000000, 4) AS avg_seconds
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;

-- Tables with most full scans (candidates for indexing)
SELECT
    object_schema,
    object_name,
    count_read,
    count_fetch
FROM performance_schema.table_io_waits_summary_by_table
ORDER BY count_read DESC
LIMIT 10;
```

### 15.5 Optimisation Tips

```sql
-- 1. Use covering indexes — include all columns needed by the query
CREATE INDEX idx_orders_user_status_total ON orders(user_id, status, total);
-- Query: SELECT total FROM orders WHERE user_id=42 AND status='completed'
-- All data comes from the index — no table row access needed (Using index)

-- 2. Avoid functions on indexed columns in WHERE
-- BAD — prevents index use:
WHERE YEAR(created_at) = 2026
WHERE UPPER(email) = 'USER@EXAMPLE.COM'

-- GOOD — index can be used:
WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01'
WHERE email = 'user@example.com'  -- (with case-insensitive collation)

-- 3. Use LIMIT to short-circuit large result sets
SELECT * FROM products WHERE status = 'active' LIMIT 100;

-- 4. Avoid SELECT * — pull only what you need
-- BAD: SELECT * FROM orders
-- GOOD: SELECT id, user_id, total, status FROM orders

-- 5. Use EXPLAIN before deploying any non-trivial query
-- If type=ALL on a large table, you need an index

-- 6. Batch large operations
-- Instead of deleting 1M rows at once (locks table):
DELETE FROM logs WHERE created_at < NOW() - INTERVAL 90 DAY LIMIT 1000;
-- Repeat in a loop until rows affected = 0

-- 7. Use connection pooling in applications
-- Every MySQL connection is a thread — don't open thousands
```

---

## 16. MySQL Configuration

### 16.1 Configuration File

MySQL reads configuration from `/etc/mysql/mysql.conf.d/mysqld.cnf` (Ubuntu) or `/etc/my.cnf`.

```ini
[mysqld]
# Basic settings
datadir = /var/lib/mysql
socket  = /var/run/mysqld/mysqld.sock
pid-file = /var/run/mysqld/mysqld.pid

# Character set — always utf8mb4
character-set-server = utf8mb4
collation-server     = utf8mb4_unicode_ci

# InnoDB settings
innodb_buffer_pool_size = 1G           # 70-80% of available RAM
innodb_log_file_size    = 256M         # larger = less I/O, slower crash recovery
innodb_flush_log_at_trx_commit = 1     # 1=safe (fsync), 2=faster (OS cache), 0=risky
innodb_file_per_table   = 1            # each table in its own .ibd file (easier management)

# Connection settings
max_connections         = 500          # adjust based on your app's pool size
wait_timeout            = 28800        # 8 hours before idle connection closed
interactive_timeout     = 28800

# Query settings
max_allowed_packet      = 64M          # max size of a query or result row
sort_buffer_size        = 4M
join_buffer_size        = 4M

# Logging
slow_query_log          = 1
slow_query_log_file     = /var/log/mysql/slow.log
long_query_time         = 2            # log queries > 2 seconds
log_error               = /var/log/mysql/error.log
general_log             = 0            # disable in production (writes every query)

# Binary logging (for replication and PITR)
log_bin                 = mysql-bin
binlog_format           = ROW          # ROW is safest and recommended
expire_logs_days        = 7            # auto-purge binary logs after 7 days
server-id               = 1            # unique for each server in replication

# SQL mode — enforce strict standards
sql_mode = STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION,ONLY_FULL_GROUP_BY
```

### 16.2 SQL Mode

SQL mode controls MySQL's strict vs permissive behaviour. Always use strict mode in production:

```sql
-- Check current SQL mode
SELECT @@sql_mode;
SHOW VARIABLES LIKE 'sql_mode';

-- Important modes:
-- STRICT_TRANS_TABLES  — error on invalid data (not silent truncation)
-- ONLY_FULL_GROUP_BY   — enforce standard GROUP BY rules
-- NO_ZERO_DATE         — disallow '0000-00-00' as a date
-- NO_ZERO_IN_DATE      — disallow zeros in date parts
-- ERROR_FOR_DIVISION_BY_ZERO — error instead of NULL on / 0
-- NO_ENGINE_SUBSTITUTION — error if requested engine unavailable

-- Set for session (testing)
SET SESSION sql_mode = 'STRICT_TRANS_TABLES,ONLY_FULL_GROUP_BY';

-- The recommended production setting:
SET GLOBAL sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION,ONLY_FULL_GROUP_BY';
```

---

## 17. Backup and Restore

### 17.1 mysqldump — Logical Backup

`mysqldump` exports data as SQL statements. Portable, readable, but slower than physical backup for large databases.

```bash
# Dump a single database
mysqldump -u root -p myapp > myapp_backup.sql

# Dump with options
mysqldump -u root -p \
  --single-transaction \         # consistent snapshot without locking (InnoDB)
  --routines \                   # include stored procedures and functions
  --triggers \                   # include triggers
  --events \                     # include scheduled events
  myapp > myapp_full.sql

# Dump specific tables
mysqldump -u root -p myapp users orders order_items > partial.sql

# Dump all databases
mysqldump -u root -p --all-databases > all_databases.sql

# Compressed backup
mysqldump -u root -p myapp | gzip > myapp_$(date +%Y%m%d).sql.gz

# Dump without data (schema only)
mysqldump -u root -p --no-data myapp > schema.sql

# Dump data only (no CREATE TABLE statements)
mysqldump -u root -p --no-create-info myapp > data_only.sql
```

### 17.2 Restoring from mysqldump

```bash
# Restore a single database
mysql -u root -p myapp < myapp_backup.sql

# Restore compressed backup
gunzip < myapp_backup.sql.gz | mysql -u root -p myapp

# Restore all databases
mysql -u root -p < all_databases.sql

# Create database first if it doesn't exist
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS myapp;"
mysql -u root -p myapp < myapp_backup.sql
```

### 17.3 mysqlpump — Parallel Dump (MySQL 5.7+)

```bash
# Faster than mysqldump for large databases (parallel export)
mysqlpump -u root -p \
  --parallel-schemas=4 \   # 4 parallel schema workers
  myapp > myapp_pump.sql
```

### 17.4 Physical Backup with Percona XtraBackup

For large production databases, logical backup is too slow. Percona XtraBackup takes a hot physical backup of InnoDB files without locking.

```bash
# Install
sudo apt install percona-xtrabackup-80

# Full backup
xtrabackup --backup --target-dir=/backup/full --user=root --password=pass

# Prepare the backup (apply logs)
xtrabackup --prepare --target-dir=/backup/full

# Restore (stop MySQL first)
sudo systemctl stop mysql
xtrabackup --copy-back --target-dir=/backup/full
sudo chown -R mysql:mysql /var/lib/mysql
sudo systemctl start mysql
```

### 17.5 Binary Log Based Point-in-Time Recovery

```bash
# After restoring a full backup, replay binary logs to a specific point

# Find the position in the binary log
mysqlbinlog mysql-bin.000001 | grep -A 5 "2026-01-15 14:30:00"

# Replay from start of binary log to a specific position
mysqlbinlog mysql-bin.000001 --stop-position=12345 | mysql -u root -p

# Replay a time range
mysqlbinlog mysql-bin.000001 \
  --start-datetime="2026-01-15 00:00:00" \
  --stop-datetime="2026-01-15 14:30:00" \
  | mysql -u root -p
```

---

## 18. Replication

### 18.1 How Replication Works

MySQL replication copies changes from a **primary** (master) server to one or more **replica** (slave) servers. The primary writes changes to the binary log. Each replica reads the binary log and replays the events.

```
Primary (writes all changes to binlog)
    ↓
Binary Log
    ↓  (replica connects, downloads events)
Replica 1 — reads replica (reporting, analytics)
Replica 2 — hot standby (failover)
```

### 18.2 Setting Up Replication

**On the primary:**

```sql
-- In /etc/mysql/mysql.conf.d/mysqld.cnf:
-- server-id = 1
-- log_bin = mysql-bin
-- binlog_format = ROW

-- Create a replication user
CREATE USER 'replicator'@'replica-ip' IDENTIFIED BY 'replication_password';
GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'replica-ip';
FLUSH PRIVILEGES;

-- Get the current binary log position
SHOW MASTER STATUS;
-- Note the File and Position values
```

```bash
# Take a backup of the primary to initialise the replica
mysqldump -u root -p --single-transaction --master-data=2 myapp > primary_backup.sql
# --master-data=2 includes a CHANGE MASTER TO comment with the binlog position
```

**On the replica:**

```sql
-- In /etc/mysql/mysql.conf.d/mysqld.cnf:
-- server-id = 2  (must be different from primary)
-- relay-log = relay-bin
-- read_only = 1  (prevent accidental writes to replica)
```

```bash
# Restore the primary's backup
mysql -u root -p myapp < primary_backup.sql
```

```sql
-- Configure the replica
CHANGE MASTER TO
    MASTER_HOST = 'primary-server-ip',
    MASTER_USER = 'replicator',
    MASTER_PASSWORD = 'replication_password',
    MASTER_LOG_FILE = 'mysql-bin.000001',   -- from SHOW MASTER STATUS
    MASTER_LOG_POS = 12345;                  -- from SHOW MASTER STATUS

-- Start replication
START SLAVE;   -- MySQL 5.x
START REPLICA; -- MySQL 8.x (new name)

-- Check replication status
SHOW SLAVE STATUS\G    -- MySQL 5.x
SHOW REPLICA STATUS\G  -- MySQL 8.x
-- Check: Slave_IO_Running = Yes, Slave_SQL_Running = Yes
-- Check: Seconds_Behind_Master (should be close to 0)
```

### 18.3 GTID-Based Replication (MySQL 5.6+)

GTID (Global Transaction Identifier) replication is simpler to manage and more reliable than binary log position-based replication. Each transaction gets a globally unique ID, eliminating the need to track file names and positions.

```ini
# In my.cnf on both primary and replica:
gtid_mode = ON
enforce_gtid_consistency = ON
```

```sql
-- Configure replica with GTID
CHANGE MASTER TO
    MASTER_HOST = 'primary-ip',
    MASTER_USER = 'replicator',
    MASTER_PASSWORD = 'pass',
    MASTER_AUTO_POSITION = 1;   -- automatically use GTIDs
START REPLICA;
```

### 18.4 Monitoring Replication

```sql
-- Check replication lag
SHOW REPLICA STATUS\G
-- Seconds_Behind_Source: 0 = in sync, >0 = replica is behind

-- On the primary: see connected replicas
SHOW PROCESSLIST;
-- Look for "Binlog Dump" entries

-- Check GTID status
SHOW VARIABLES LIKE 'gtid_executed';   -- all executed GTIDs
```

---

## 19. MySQL with Node.js and Java

### 19.1 Node.js with mysql2

```bash
npm install mysql2
```

```javascript
const mysql = require('mysql2/promise');

// Create a connection pool (preferred over single connections)
const pool = mysql.createPool({
    host: process.env.DB_HOST || 'localhost',
    port: 3306,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    waitForConnections: true,
    connectionLimit: 10,         // max connections in pool
    queueLimit: 0,               // unlimited queue
    charset: 'utf8mb4',
    timezone: '+00:00',          // store/retrieve as UTC
});

// Query with parameterised statement (prevents SQL injection)
async function getUserById(id) {
    const [rows] = await pool.execute(
        'SELECT id, email, full_name FROM users WHERE id = ?',
        [id]
    );
    return rows[0] || null;
}

// Insert and get the inserted ID
async function createUser(email, fullName) {
    const [result] = await pool.execute(
        'INSERT INTO users (email, full_name) VALUES (?, ?)',
        [email, fullName]
    );
    return result.insertId;   // LAST_INSERT_ID()
}

// Transaction example
async function transferFunds(fromId, toId, amount) {
    const conn = await pool.getConnection();
    try {
        await conn.beginTransaction();

        await conn.execute(
            'UPDATE accounts SET balance = balance - ? WHERE id = ?',
            [amount, fromId]
        );

        // Check balance didn't go negative
        const [rows] = await conn.execute(
            'SELECT balance FROM accounts WHERE id = ?',
            [fromId]
        );
        if (rows[0].balance < 0) throw new Error('Insufficient funds');

        await conn.execute(
            'UPDATE accounts SET balance = balance + ? WHERE id = ?',
            [amount, toId]
        );

        await conn.commit();
    } catch (err) {
        await conn.rollback();
        throw err;
    } finally {
        conn.release();   // return connection to pool
    }
}
```

### 19.2 Node.js with TypeORM (used with NestJS)

```typescript
// app.module.ts — TypeORM MySQL configuration
import { TypeOrmModule } from '@nestjs/typeorm';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'mysql',
      host: process.env.DB_HOST,
      port: 3306,
      username: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_NAME,
      entities: [__dirname + '/**/*.entity{.ts,.js}'],
      synchronize: false,       // NEVER true in production — use migrations
      charset: 'utf8mb4',
      timezone: 'Z',            // UTC
      extra: {
        connectionLimit: 10,    // pool size
      },
    }),
  ],
})

// Entity definition
import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn } from 'typeorm';

@Entity('users')
export class User {
    @PrimaryGeneratedColumn('increment')
    id: number;

    @Column({ type: 'varchar', length: 255, unique: true })
    email: string;

    @Column({ name: 'full_name', type: 'varchar', length: 150 })
    fullName: string;

    @Column({
        type: 'enum',
        enum: ['active', 'inactive', 'suspended'],
        default: 'active',
    })
    status: string;

    @CreateDateColumn({ name: 'created_at' })
    createdAt: Date;
}
```

### 19.3 Java with JDBC

```java
// Maven dependency
// <dependency>
//     <groupId>com.mysql</groupId>
//     <artifactId>mysql-connector-j</artifactId>
//     <version>8.3.0</version>
// </dependency>

import java.sql.*;

public class MySQLExample {

    private static final String URL =
        "jdbc:mysql://localhost:3306/myapp" +
        "?useSSL=false" +
        "&serverTimezone=UTC" +
        "&characterEncoding=utf8mb4" +
        "&useUnicode=true";

    // Direct connection (use connection pool in production)
    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, "appuser", "password");
    }

    // Parameterised query (PreparedStatement — ALWAYS use this, never string concat)
    public User getUserById(long id) throws SQLException {
        String sql = "SELECT id, email, full_name FROM users WHERE id = ?";
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setLong(1, id);
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    return new User(
                        rs.getLong("id"),
                        rs.getString("email"),
                        rs.getString("full_name")
                    );
                }
                return null;
            }
        }
    }

    // Transaction
    public void transferFunds(long fromId, long toId, double amount) throws SQLException {
        try (Connection conn = getConnection()) {
            conn.setAutoCommit(false);   // begin transaction
            try {
                PreparedStatement debit = conn.prepareStatement(
                    "UPDATE accounts SET balance = balance - ? WHERE id = ?"
                );
                debit.setDouble(1, amount);
                debit.setLong(2, fromId);
                debit.executeUpdate();

                PreparedStatement credit = conn.prepareStatement(
                    "UPDATE accounts SET balance = balance + ? WHERE id = ?"
                );
                credit.setDouble(1, amount);
                credit.setLong(2, toId);
                credit.executeUpdate();

                conn.commit();
            } catch (SQLException e) {
                conn.rollback();
                throw e;
            }
        }
    }
}
```

### 19.4 Java with Spring Boot + JPA

```java
// application.properties
spring.datasource.url=jdbc:mysql://localhost:3306/myapp?useSSL=false&serverTimezone=UTC&characterEncoding=utf8mb4
spring.datasource.username=appuser
spring.datasource.password=password
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
spring.jpa.hibernate.ddl-auto=validate   // validate schema on startup (safe for prod)
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQL8Dialect
spring.datasource.hikari.maximum-pool-size=10  // connection pool size

// Entity
@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(precision = 10, scale = 2)
    private BigDecimal total;

    @Enumerated(EnumType.STRING)
    private OrderStatus status;

    @Column(name = "created_at", updatable = false)
    @CreationTimestamp
    private LocalDateTime createdAt;
}

// Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByUserIdAndStatus(Long userId, OrderStatus status);

    @Query("SELECT o FROM Order o WHERE o.total > :minAmount ORDER BY o.createdAt DESC")
    List<Order> findLargeOrders(@Param("minAmount") BigDecimal minAmount);
}
```

---

## 20. Common Pitfalls and Gotchas

### "utf8 vs utf8mb4"

Never use MySQL's `utf8` — it's actually a 3-byte encoding that silently drops emoji and some special characters. Always use `utf8mb4`:

```sql
-- Wrong
CREATE TABLE posts (...) CHARSET=utf8;

-- Right
CREATE TABLE posts (...) CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fix an existing table
ALTER TABLE posts CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### "DATETIME vs TIMESTAMP Y2K38"

`TIMESTAMP` stores values up to `2038-01-19 03:14:07 UTC`. If your application will still be running in 2038 (or stores future dates), use `DATETIME`. For audit columns where UTC conversion is needed, `TIMESTAMP` is fine.

### "GROUP BY non-determinism"

Without `ONLY_FULL_GROUP_BY`, MySQL lets you SELECT columns not in GROUP BY. The values returned are arbitrary — different executions may return different rows:

```sql
-- This "works" but returns an arbitrary email per user_id
SELECT user_id, email, COUNT(*) FROM orders GROUP BY user_id;

-- Fix: either group by email too, or use MAX/MIN/ANY_VALUE
SELECT user_id, MAX(email) AS email, COUNT(*) FROM orders GROUP BY user_id;
SELECT user_id, ANY_VALUE(email) AS email, COUNT(*) FROM orders GROUP BY user_id;
-- ANY_VALUE() explicitly says "I know this is non-deterministic and I accept it"
```

### "NULL in NOT IN"

Covered in the SQL reference but worth repeating — if a `NOT IN` subquery returns even one NULL, the entire result set is empty:

```sql
-- Danger: if category_id is NULL for any product:
SELECT * FROM products WHERE id NOT IN (SELECT product_id FROM order_items);

-- Safe: use NOT EXISTS
SELECT * FROM products p
WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.id);

-- Or: explicitly exclude NULLs from the subquery
SELECT * FROM products WHERE id NOT IN (
    SELECT product_id FROM order_items WHERE product_id IS NOT NULL
);
```

### "Foreign Keys Not Enforced by Default on MyISAM"

Foreign key constraints are only enforced by InnoDB. If a table was created with MyISAM (or ENGINE not specified with MyISAM as default), foreign keys are silently ignored:

```sql
-- Check if your tables are InnoDB
SELECT table_name, engine FROM information_schema.tables
WHERE table_schema = DATABASE();

-- Convert legacy MyISAM tables
ALTER TABLE users ENGINE = InnoDB;
```

### "ENUM Changes Require ALTER TABLE"

Adding values to an ENUM requires `ALTER TABLE`, which in older MySQL versions locks the table. In MySQL 8.0 the operation is instant for adding values at the end, but removing or reordering values still requires a full table rebuild:

```sql
-- Safe in MySQL 8.0 (adding to end — instant)
ALTER TABLE users MODIFY status ENUM('active','inactive','suspended','archived');

-- Consider TEXT + CHECK CONSTRAINT for flexibility:
status TEXT NOT NULL CHECK (status IN ('active','inactive','suspended'))
-- Adding a new value: just update your application code, no DDL needed
```

### "Implicit String-to-Number Conversion"

MySQL silently converts strings to numbers in comparisons:

```sql
-- This works but is a trap:
SELECT * FROM users WHERE id = '42abc';
-- MySQL converts '42abc' to 42 and matches. This can cause index scans.

-- This is safe:
SELECT * FROM users WHERE id = 42;     -- proper integer comparison
SELECT * FROM users WHERE id = '42';   -- string, but MySQL converts correctly for int columns
```

### "Connection Timeout in Production"

MySQL closes idle connections after `wait_timeout` seconds (default 8 hours). If your app holds connections in a pool for longer, you'll get "MySQL server has gone away" errors:

```javascript
// mysql2 pool configuration to handle reconnection
const pool = mysql.createPool({
    ...
    enableKeepAlive: true,
    keepAliveInitialDelay: 0,
});

// Or set a shorter pool connection lifetime than MySQL's wait_timeout
```

### "SELECT * in Production Code"

Beyond performance, `SELECT *` causes bugs when columns are added or reordered. Always name your columns:

```sql
-- Fragile
SELECT * FROM users;

-- Robust
SELECT id, email, full_name, status, created_at FROM users;
```

### "Missing Index on Foreign Key Column"

MySQL does not automatically create indexes on foreign key columns (unlike some other databases). Always create them manually:

```sql
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
    -- No automatic index on user_id!
);

-- Add the index:
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

---

*Last updated: 2026 — Built from real MySQL production experience at ITC and across backend projects.*
