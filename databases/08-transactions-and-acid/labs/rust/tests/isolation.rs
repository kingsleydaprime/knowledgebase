//! The anomalies and their fixes through the `postgres` crate, two clients stepped one statement at a time.
//! Run through ../shared/with-postgres.sh; without PGHOST, it does nothing.
use isolation::{code, connect, with_retry};
use postgres::Client;
use postgres::error::SqlState;

const BALANCE: &str = "SELECT balance FROM accounts WHERE id = 1";

fn int(c: &mut Client, sql: &str) -> i64 {
    let row = c.query_one(sql, &[]).unwrap();
    row.try_get::<_, i64>(0)
        .unwrap_or_else(|_| i64::from(row.get::<_, i32>(0))) // count(*) is bigint; balance is int
}

fn reset(a: &mut Client) {
    a.batch_execute(
        "DROP TABLE IF EXISTS accounts, doctors;
         CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL CHECK (balance >= 0));
         INSERT INTO accounts VALUES (1, 100), (2, 50);
         CREATE TABLE doctors (name text PRIMARY KEY, on_call boolean NOT NULL);
         INSERT INTO doctors VALUES ('alice', true), ('bob', true);",
    )
    .unwrap();
}

fn go_off_call(c: &mut Client, name: &str) -> Result<(), postgres::Error> {
    c.batch_execute("BEGIN ISOLATION LEVEL SERIALIZABLE")?;
    let on_call: i64 = c
        .query_one("SELECT count(*) FROM doctors WHERE on_call", &[])?
        .get(0);
    if on_call >= 2 {
        c.execute(
            "UPDATE doctors SET on_call = false WHERE name = $1",
            &[&name],
        )?;
    }
    Ok(())
}

#[test]
fn isolation() {
    if std::env::var("PGHOST").is_err() {
        return;
    }
    let (mut a, mut b) = (connect(), connect());

    reset(&mut a); // a lost update at Read Committed
    a.batch_execute("BEGIN").unwrap();
    b.batch_execute("BEGIN").unwrap();
    let (seen_a, seen_b) = (int(&mut a, BALANCE) as i32, int(&mut b, BALANCE) as i32);
    a.execute(
        "UPDATE accounts SET balance = $1 WHERE id = 1",
        &[&(seen_a - 10)],
    )
    .unwrap();
    a.batch_execute("COMMIT").unwrap();
    b.execute(
        "UPDATE accounts SET balance = $1 WHERE id = 1",
        &[&(seen_b - 20)],
    )
    .unwrap();
    b.batch_execute("COMMIT").unwrap();
    assert_eq!(int(&mut a, BALANCE), 80);

    reset(&mut a); // Repeatable Read refuses the second write
    a.batch_execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
        .unwrap();
    b.batch_execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
        .unwrap();
    let seen = int(&mut b, BALANCE) as i32;
    a.batch_execute("UPDATE accounts SET balance = balance - 10 WHERE id = 1; COMMIT")
        .unwrap();
    let refused = b.execute(
        "UPDATE accounts SET balance = $1 WHERE id = 1",
        &[&(seen - 20)],
    );
    assert_eq!(code(&refused), Some(&SqlState::T_R_SERIALIZATION_FAILURE));
    b.batch_execute("ROLLBACK").unwrap();

    reset(&mut a); // FOR UPDATE makes the second reader wait
    a.batch_execute("BEGIN; SELECT balance FROM accounts WHERE id = 1 FOR UPDATE")
        .unwrap();
    b.batch_execute("BEGIN; SET LOCAL lock_timeout = '100ms'")
        .unwrap();
    let waited = b.batch_execute("SELECT balance FROM accounts WHERE id = 1 FOR UPDATE");
    assert_eq!(code(&waited), Some(&SqlState::LOCK_NOT_AVAILABLE));
    b.batch_execute("ROLLBACK").unwrap();
    a.batch_execute("COMMIT").unwrap();

    reset(&mut a); // write skew: Serializable aborts one, and the retry keeps the rule
    go_off_call(&mut a, "alice").unwrap();
    go_off_call(&mut b, "bob").unwrap();
    a.batch_execute("COMMIT").unwrap();
    assert_eq!(
        code(&b.batch_execute("COMMIT")),
        Some(&SqlState::T_R_SERIALIZATION_FAILURE)
    );
    with_retry(5, || {
        let result = go_off_call(&mut b, "bob").and_then(|()| b.batch_execute("COMMIT"));
        if result.is_err() {
            b.batch_execute("ROLLBACK")?;
        }
        result
    })
    .unwrap();
    let on_call: String = a
        .query_one(
            "SELECT string_agg(name, ',') FROM doctors WHERE on_call",
            &[],
        )
        .unwrap()
        .get(0);
    assert_eq!(on_call, "bob");
}
