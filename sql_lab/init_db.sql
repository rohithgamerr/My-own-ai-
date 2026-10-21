
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, join_date DATE);
CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, order_date DATE);
INSERT INTO users VALUES (1, 'Alice', 'alice@example.com', '2023-01-01'), (2, 'Bob', 'bob@example.com', '2023-02-01');
INSERT INTO orders VALUES (101, 1, 50.0, '2023-01-02'), (102, 1, 30.0, '2023-01-03'), (103, 2, 100.0, '2023-02-02');
