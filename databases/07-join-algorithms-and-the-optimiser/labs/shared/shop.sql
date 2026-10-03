-- The customers, orders and addresses every language's lab loads: the same rows as the Python lab's SETUP.
-- Each statement ends with a semicolon at the end of its line, so labs can split on ";\n" and run them one at a time.
CREATE TABLE customers AS
SELECT i AS id, 'Customer ' || i AS name, i * 37 % 5000 AS credit_limit FROM generate_series(1, 50000) i;
ALTER TABLE customers ADD PRIMARY KEY (id);
CREATE TABLE orders AS
SELECT i AS id, 1 + i % 50000 AS customer_id, (i::bigint * 7919 % 10000)::int AS total FROM generate_series(1, 1000000) i;
ALTER TABLE orders ADD PRIMARY KEY (id);
CREATE INDEX orders_customer_id ON orders (customer_id);
CREATE TABLE addresses AS
SELECT i AS id,
       (ARRAY['London','Manchester','Leeds','Paris','Lyon','Lille','Berlin','Munich','Hamburg','Cologne'])[1 + i % 10] AS city,
       (ARRAY['UK','UK','UK','France','France','France','Germany','Germany','Germany','Germany'])[1 + i % 10] AS country
FROM generate_series(1, 30000) i;
VACUUM ANALYZE customers;
VACUUM ANALYZE orders;
ANALYZE addresses;
