-- The million orders every language's lab loads: the same rows as the Python lab's SETUP.
-- Each statement ends with a semicolon at the end of its line, so labs can split on ";\n" and run them one at a
-- time (VACUUM refuses to run inside the transaction a multi-statement call would create).
CREATE EXTENSION IF NOT EXISTS pageinspect;
CREATE TABLE orders AS
SELECT i AS id, i % 50000 AS customer_id,
       timestamptz '2026-01-01 00:00Z' + i * interval '30 seconds' AS created_at,
       (i::bigint * 7919 % 10000)::int AS total,
       CASE WHEN i % 100 = 0 THEN 'pending' ELSE 'complete' END AS status,
       'User' || i || '@Example.com' AS email
FROM generate_series(1, 1000000) AS i;
ALTER TABLE orders ADD PRIMARY KEY (id);
VACUUM ANALYZE orders;
