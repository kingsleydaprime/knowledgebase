//! The same PostgreSQL checks through the `postgres` crate. Run through ../shared/with-postgres.sh; without
//! PGHOST set, it does nothing.
use postgres::{Client, Config, NoTls};
use serde_json::Value;

fn nodes(plan: &Value, out: &mut Vec<Value>) {
    out.push(plan.clone());
    for child in plan["Plans"].as_array().into_iter().flatten() {
        nodes(child, out);
    }
}

fn explain(db: &mut Client, sql: &str) -> Vec<Value> {
    let row = db
        .query_one(
            &format!("EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) {sql}"),
            &[],
        )
        .unwrap();
    let json: Value = row.get(0); // the with-serde_json-1 feature turns a json column into a serde_json::Value
    let mut out = Vec::new();
    nodes(&json[0]["Plan"], &mut out);
    out
}

fn pages(plan: &[Value]) -> u64 {
    plan[0]["Shared Hit Blocks"].as_u64().unwrap() + plan[0]["Shared Read Blocks"].as_u64().unwrap()
}

#[test]
fn postgres() {
    let Ok(host) = std::env::var("PGHOST") else {
        return;
    }; // no database: nothing to check
    let port: u16 = std::env::var("PGPORT").unwrap().parse().unwrap();
    // The crate doesn't read PG* variables itself. A host starting with "/" is a Unix-socket folder.
    let mut db = Config::new()
        .host(&host)
        .port(port)
        .user("postgres")
        .dbname("postgres")
        .connect(NoTls)
        .unwrap();
    let setup = std::fs::read_to_string("../shared/orders.sql").unwrap();
    for statement in setup.split(";\n") {
        let code: String = statement
            .lines()
            .filter(|l| !l.trim_start().starts_with("--"))
            .collect();
        if !code.trim().is_empty() {
            db.batch_execute(statement).unwrap(); // one at a time, as VACUUM requires
        }
    }

    let level: i64 = db
        .query_one("SELECT level FROM bt_metap('orders_pkey')", &[])
        .unwrap()
        .get(0); // bigint is i64
    assert_eq!(level, 2);
    let lookup = explain(&mut db, "SELECT * FROM orders WHERE id = 424242");
    assert_eq!(
        (lookup[0]["Node Type"].as_str(), pages(&lookup)),
        (Some("Index Scan"), 4)
    );

    db.batch_execute("CREATE INDEX orders_customer_created ON orders (customer_id, created_at)")
        .unwrap();
    let both = explain(
        &mut db,
        "SELECT * FROM orders WHERE customer_id = 42 AND created_at > '2026-06-01'",
    );
    assert!(
        both.iter()
            .any(|n| n["Index Name"] == "orders_customer_created")
    );
    let hour = explain(
        &mut db,
        "SELECT * FROM orders WHERE created_at >= '2026-06-01' AND created_at < '2026-06-01 01:00'",
    );
    assert_eq!(hour[0]["Node Type"], "Seq Scan");
    db.batch_execute("DROP INDEX orders_customer_created")
        .unwrap();

    db.batch_execute("CREATE INDEX orders_customer_total ON orders (customer_id) INCLUDE (total)")
        .unwrap();
    db.batch_execute("VACUUM orders").unwrap();
    let clean = explain(&mut db, "SELECT total FROM orders WHERE customer_id = 42");
    assert_eq!(
        (
            clean[0]["Node Type"].as_str(),
            clean[0]["Heap Fetches"].as_u64()
        ),
        (Some("Index Only Scan"), Some(0))
    );
    db.batch_execute("UPDATE orders SET total = total + 1 WHERE customer_id = 42")
        .unwrap();
    assert!(
        explain(&mut db, "SELECT total FROM orders WHERE customer_id = 42")[0]["Heap Fetches"]
            .as_u64()
            .unwrap()
            > 0
    );
}
