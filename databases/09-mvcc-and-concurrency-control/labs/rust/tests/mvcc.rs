//! MVCC through the `postgres` crate: snapshots, blocked vacuum and a deadlock. Run through
//! ../shared/with-postgres.sh; without PGHOST, it does nothing.
use mvcc::{code, connect};
use postgres::Client;
use postgres::error::SqlState;
use std::time::Duration;

const BALANCE: &str = "SELECT balance FROM accounts WHERE id = 1";

fn balance(c: &mut Client) -> i32 {
    c.query_one(BALANCE, &[]).unwrap().get(0) // an int column reads as i32: the crate won't widen it for you
}

fn dead(c: &mut Client) -> i64 {
    c.query_one("SELECT dead_tuple_count FROM pgstattuple('accounts')", &[])
        .unwrap()
        .get(0)
}

fn reset(a: &mut Client) {
    a.batch_execute(
        "CREATE EXTENSION IF NOT EXISTS pgstattuple;
         DROP TABLE IF EXISTS accounts;
         CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL);
         INSERT INTO accounts SELECT i, 100 FROM generate_series(1, 1000) i;",
    )
    .unwrap();
    a.batch_execute("VACUUM accounts").unwrap(); // alone: VACUUM can't run inside a multi-statement call's transaction
}

#[test]
fn mvcc() {
    if std::env::var("PGHOST").is_err() {
        return;
    }
    let (mut a, mut b, mut watcher) = (connect(), connect(), connect());

    reset(&mut a); // readers don't block writers
    a.batch_execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
        .unwrap();
    assert_eq!(balance(&mut a), 100);
    b.batch_execute("SET lock_timeout = '100ms'; UPDATE accounts SET balance = 50 WHERE id = 1")
        .unwrap();
    assert_eq!(balance(&mut a), 100);
    a.batch_execute("COMMIT").unwrap();
    assert_eq!(balance(&mut a), 50);

    reset(&mut a); // writers block writers
    a.batch_execute("BEGIN; UPDATE accounts SET balance = 90 WHERE id = 1")
        .unwrap();
    let blocked = b.batch_execute("UPDATE accounts SET balance = 80 WHERE id = 1");
    assert_eq!(code(&blocked), Some(&SqlState::LOCK_NOT_AVAILABLE));
    a.batch_execute("COMMIT").unwrap();

    reset(&mut a); // an open snapshot stops vacuum
    a.batch_execute("BEGIN ISOLATION LEVEL REPEATABLE READ; SELECT 1")
        .unwrap();
    b.batch_execute("UPDATE accounts SET balance = balance + 1")
        .unwrap();
    b.batch_execute("VACUUM accounts").unwrap();
    assert_eq!(dead(&mut b), 1000);
    a.batch_execute("COMMIT").unwrap();
    b.batch_execute("VACUUM accounts").unwrap();
    assert_eq!(dead(&mut b), 0);

    reset(&mut a); // a deadlock: exactly one victim
    b.batch_execute("RESET lock_timeout").unwrap();
    for c in [&mut a, &mut b] {
        c.batch_execute("SET deadlock_timeout = '100ms'; BEGIN")
            .unwrap();
    }
    a.batch_execute("UPDATE accounts SET balance = 1 WHERE id = 1")
        .unwrap();
    b.batch_execute("UPDATE accounts SET balance = 2 WHERE id = 2")
        .unwrap();
    let a_pid: i32 = a.query_one("SELECT pg_backend_pid()", &[]).unwrap().get(0);
    let (a_result, b_result) = std::thread::scope(|s| {
        // A scoped thread may borrow `a` mutably: the scope ends before `a` is used again.
        let waiting = s.spawn(|| a.batch_execute("UPDATE accounts SET balance = 1 WHERE id = 2"));
        loop {
            let row = watcher
                .query_one(
                    "SELECT wait_event_type FROM pg_stat_activity WHERE pid = $1",
                    &[&a_pid],
                )
                .unwrap();
            if row.get::<_, Option<String>>(0).as_deref() == Some("Lock") {
                break;
            }
            std::thread::sleep(Duration::from_millis(10));
        }
        let b_result = b.batch_execute("UPDATE accounts SET balance = 2 WHERE id = 1");
        (waiting.join().unwrap(), b_result)
    });
    let victims = [code(&a_result), code(&b_result)]
        .iter()
        .filter(|c| **c == Some(&SqlState::T_R_DEADLOCK_DETECTED))
        .count();
    assert_eq!(victims, 1);
    a.batch_execute("ROLLBACK").unwrap();
    b.batch_execute("ROLLBACK").unwrap();
}
