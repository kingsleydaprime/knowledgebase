//! The PostgreSQL checks through the `postgres` crate. Run through ../shared/with-postgres.sh; without PGHOST
//! set, it does nothing.
use postgres::{Client, Config, NoTls};
use serde_json::Value;

fn nodes(plan: &Value, out: &mut Vec<Value>) {
    out.push(plan.clone());
    for child in plan["Plans"].as_array().into_iter().flatten() {
        nodes(child, out);
    }
}

fn explain(db: &mut Client, sql: &str) -> Vec<Value> {
    let json: Value = db
        .query_one(
            &format!("EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) {sql}"),
            &[],
        )
        .unwrap()
        .get(0);
    let mut out = Vec::new();
    nodes(&json[0]["Plan"], &mut out);
    out
}

fn hash_batches(db: &mut Client) -> u64 {
    let plan = explain(
        db,
        "SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id",
    );
    plan.iter().find(|n| n["Node Type"] == "Hash").unwrap()["Hash Batches"]
        .as_u64()
        .unwrap()
}

#[test]
fn postgres() {
    let Ok(host) = std::env::var("PGHOST") else {
        return;
    };
    let port: u16 = std::env::var("PGPORT").unwrap().parse().unwrap();
    let mut db = Config::new()
        .host(&host)
        .port(port)
        .user("postgres")
        .dbname("postgres")
        .connect(NoTls)
        .unwrap();
    for statement in std::fs::read_to_string("../shared/shop.sql")
        .unwrap()
        .split(";\n")
    {
        let code: String = statement
            .lines()
            .filter(|l| !l.trim_start().starts_with("--"))
            .collect();
        if !code.trim().is_empty() {
            db.batch_execute(statement).unwrap();
        }
    }

    assert_eq!(hash_batches(&mut db), 1);
    db.batch_execute("SET work_mem = '64kB'").unwrap();
    assert_eq!(hash_batches(&mut db), 16);
    db.batch_execute("RESET work_mem").unwrap();

    let query = "SELECT * FROM addresses WHERE city = 'London' AND country = 'UK'";
    let before = &explain(&mut db, query)[0];
    assert_eq!(
        (before["Plan Rows"].as_u64(), before["Actual Rows"].as_f64()),
        (Some(900), Some(3000.0))
    ); // actual rows: a decimal in PostgreSQL 18
    db.batch_execute("CREATE STATISTICS addresses_city_country (dependencies) ON city, country FROM addresses; ANALYZE addresses").unwrap();
    assert_eq!(explain(&mut db, query)[0]["Plan Rows"].as_u64(), Some(3000));

    let offset = explain(
        &mut db,
        "SELECT * FROM orders ORDER BY id OFFSET 100000 LIMIT 20",
    );
    let keyset = explain(
        &mut db,
        "SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20",
    );
    assert_eq!(
        (
            offset[1]["Actual Rows"].as_f64(),
            keyset[1]["Actual Rows"].as_f64()
        ),
        (Some(100_020.0), Some(20.0))
    );
}
