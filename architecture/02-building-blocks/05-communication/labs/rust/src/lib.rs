//! What an API style costs, counted: REST requests and bytes, a GraphQL-style query with the N+1 problem and
//! batching, Protocol Buffers' varints, and synchronous chains. The same numbers as the TypeScript lab.
use serde_json::{Map, Value, json};
use std::cell::Cell;
use std::collections::HashMap;

/// Compact JSON, as JSON.stringify writes it. `preserve_order` keeps fields in the order they were read.
pub fn size(v: &Value) -> usize {
    v.to_string().len()
}

/// A tiny shop database that counts its queries. The count is a Cell, so finding rows needs only `&self`.
pub struct Db {
    pub queries: Cell<u32>,
    tables: HashMap<String, HashMap<String, Value>>,
}

impl Db {
    pub fn new(shop: &Value) -> Self {
        let mut tables = HashMap::new();
        for table in ["customers", "products", "orders"] {
            let rows = shop[table]
                .as_array()
                .into_iter()
                .flatten()
                .map(|r| (r["id"].as_str().unwrap_or_default().to_string(), r.clone()));
            tables.insert(table.to_string(), rows.collect());
        }
        Db {
            queries: Cell::new(0),
            tables,
        }
    }

    /// One query for any number of rows: SELECT … WHERE id IN (…).
    pub fn find(&self, table: &str, ids: &[&str]) -> Vec<Value> {
        self.queries.set(self.queries.get() + 1);
        ids.iter()
            .map(|id| self.tables[table].get(*id).cloned().unwrap_or(Value::Null))
            .collect()
    }
}

/// One whole resource per URL. Counts requests and bytes sent.
pub struct RestApi<'a> {
    db: &'a Db,
    pub requests: u32,
    pub bytes: usize,
}

impl<'a> RestApi<'a> {
    pub fn new(db: &'a Db) -> Self {
        RestApi {
            db,
            requests: 0,
            bytes: 0,
        }
    }

    pub fn get(&mut self, path: &str) -> Result<Value, String> {
        let parts: Vec<&str> = path.split('/').collect(); // "/orders/o1" → "", "orders", "o1"
        let [_, kind @ ("orders" | "customers" | "products"), id] = parts[..] else {
            return Err(format!("404 {path}"));
        };
        let body = self.db.find(kind, &[id]).remove(0);
        if body.is_null() {
            return Err(format!("404 {path}"));
        }
        self.requests += 1;
        self.bytes += size(&body);
        Ok(body)
    }
}

fn text(v: &Value) -> &str {
    v.as_str().unwrap_or_default()
}

/// The order (round trip 1), then its customer and products together (round trip 2).
pub fn order_screen_rest(api: &mut RestApi, order_id: &str) -> Result<(Value, u32), String> {
    let order = api.get(&format!("/orders/{order_id}"))?;
    let customer = api.get(&format!("/customers/{}", text(&order["customerId"])))?;
    let mut items = Vec::new();
    for item in order["items"].as_array().into_iter().flatten() {
        let product = api.get(&format!("/products/{}", text(&item["productId"])))?;
        items.push(json!({ "quantity": item["quantity"], "product": { "name": product["name"] } }));
    }
    let screen = json!({ "id": order["id"], "totalPence": order["totalPence"], "customer": { "name": customer["name"] }, "items": items });
    Ok((screen, 2))
}

/// Fields wanted, in order: `None` for a plain field, `Some` to select inside an object or list.
pub struct Selection(pub Vec<(&'static str, Option<Selection>)>);

/// Fetches one field for every parent at one level of the query at once.
pub type Resolver<'a> = Box<dyn Fn(&[Value]) -> Vec<Value> + 'a>;

fn field_type(typ: &str, field: &str) -> &'static str {
    match (typ, field) {
        ("Order", "customer") => "Customer",
        ("Order", "items") => "Item",
        ("Item", "product") => "Product",
        _ => "",
    }
}

/// Runs a selection over every object at one level together, so each resolver sees the whole level.
pub fn execute(
    values: &[Value],
    selection: &Selection,
    resolvers: &HashMap<&str, Resolver>,
    typ: &str,
) -> Vec<Value> {
    let mut outs: Vec<Map<String, Value>> = values.iter().map(|_| Map::new()).collect();
    for (field, sub) in &selection.0 {
        let children = match resolvers.get(format!("{typ}.{field}").as_str()) {
            Some(resolve) => resolve(values),
            None => values.iter().map(|v| v[*field].clone()).collect(),
        };
        let child_type = field_type(typ, field);
        match sub {
            None => {
                for (out, child) in outs.iter_mut().zip(children) {
                    out.insert(field.to_string(), child);
                }
            }
            Some(sub) if children.first().is_some_and(Value::is_array) => {
                // a list field: all its elements form the next level
                let flat: Vec<Value> = children
                    .iter()
                    .flat_map(|c| c.as_array().cloned().unwrap_or_default())
                    .collect();
                let mut done = execute(&flat, sub, resolvers, child_type).into_iter();
                for (out, c) in outs.iter_mut().zip(&children) {
                    let n = c.as_array().map_or(0, Vec::len);
                    out.insert(
                        field.to_string(),
                        Value::Array(done.by_ref().take(n).collect()),
                    );
                }
            }
            Some(sub) => {
                for (out, r) in outs
                    .iter_mut()
                    .zip(execute(&children, sub, resolvers, child_type))
                {
                    out.insert(field.to_string(), r);
                }
            }
        }
    }
    outs.into_iter().map(Value::Object).collect()
}

/// One query per parent (the N+1 problem), or one query for the whole level.
pub fn resolvers(db: &Db, batched: bool) -> HashMap<&'static str, Resolver<'_>> {
    let make = move |table: &'static str, key: &'static str| -> Resolver<'_> {
        Box::new(move |parents: &[Value]| {
            if !batched {
                return parents
                    .iter()
                    .map(|p| db.find(table, &[text(&p[key])]).remove(0))
                    .collect();
            }
            let mut ids: Vec<&str> = Vec::new();
            for p in parents {
                if !ids.contains(&text(&p[key])) {
                    ids.push(text(&p[key])); // each ID once
                }
            }
            let rows: HashMap<&str, Value> =
                ids.iter().copied().zip(db.find(table, &ids)).collect();
            parents
                .iter()
                .map(|p| rows[text(&p[key])].clone())
                .collect()
        })
    };
    HashMap::from([
        ("Order.customer", make("customers", "customerId")),
        ("Item.product", make("products", "productId")),
    ])
}

/// Base-128, low bits first, top bit set if more follow.
pub fn varint(mut n: u64) -> Vec<u8> {
    let mut out = Vec::new();
    while n >= 0x80 {
        out.push((n as u8 & 0x7f) | 0x80);
        n >>= 7;
    }
    out.push(n as u8);
    out
}

pub fn encode_order_summary(id: u64, customer: &str, total_pence: u64) -> Vec<u8> {
    let mut out = varint(1 << 3);
    out.extend(varint(id));
    out.extend(varint(2 << 3 | 2));
    out.extend(varint(customer.len() as u64)); // len() is bytes, which is what protobuf wants
    out.extend(customer.as_bytes());
    out.extend(varint(3 << 3));
    out.extend(varint(total_pence));
    out
}

#[derive(Debug)]
pub struct Chain {
    pub availability: f64,
    pub sequential_ms: f64,
    pub parallel_ms: f64,
}

/// (availability, ms) for each call in a row.
pub fn chain(calls: &[(f64, f64)]) -> Chain {
    Chain {
        availability: calls.iter().map(|c| c.0).product(),
        sequential_ms: calls.iter().map(|c| c.1).sum(),
        parallel_ms: calls.iter().map(|c| c.1).fold(0.0, f64::max),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn shop() -> Value {
        serde_json::from_str(
            &std::fs::read_to_string("../shared/shop.json").expect("the shared shop"),
        )
        .expect("valid JSON")
    }

    fn screen_query() -> Selection {
        Selection(vec![
            ("id", None),
            ("totalPence", None),
            ("customer", Some(Selection(vec![("name", None)]))),
            (
                "items",
                Some(Selection(vec![
                    ("quantity", None),
                    ("product", Some(Selection(vec![("name", None)]))),
                ])),
            ),
        ])
    }

    #[test]
    fn rest_five_requests_two_round_trips() {
        let db = Db::new(&shop());
        let mut api = RestApi::new(&db);
        let (screen, round_trips) = order_screen_rest(&mut api, "o1").unwrap();
        assert_eq!(screen["customer"]["name"], "Gbenga Ali");
        assert_eq!(
            (api.requests, round_trips, api.bytes, size(&screen)),
            (5, 2, 912, 203)
        );
        assert!(api.get("/refunds/r1").is_err());
    }

    #[test]
    fn a_graphql_style_query_one_request_only_the_fields_asked_for() {
        let shop = shop();
        let rest_db = Db::new(&shop);
        let (want, _) = order_screen_rest(&mut RestApi::new(&rest_db), "o1").unwrap();
        for batched in [false, true] {
            let db = Db::new(&shop);
            let order = db.find("orders", &["o1"]);
            let screen =
                execute(&order, &screen_query(), &resolvers(&db, batched), "Order").remove(0);
            assert_eq!((&screen, size(&screen)), (&want, 203));
            assert_eq!(db.queries.get(), if batched { 3 } else { 5 });
        }
    }

    #[test]
    fn n_plus_one_41_queries_or_3() {
        let shop = shop();
        for batched in [false, true] {
            let db = Db::new(&shop);
            let ids: Vec<String> = (1..=10).map(|i| format!("o{i}")).collect();
            let orders = db.find(
                "orders",
                &ids.iter().map(String::as_str).collect::<Vec<_>>(),
            );
            let query = Selection(vec![
                ("id", None),
                ("customer", Some(Selection(vec![("name", None)]))),
                (
                    "items",
                    Some(Selection(vec![(
                        "product",
                        Some(Selection(vec![("name", None)])),
                    )])),
                ),
            ]);
            let page = execute(&orders, &query, &resolvers(&db, batched), "Order");
            assert_eq!(
                (page.len(), &page[0]["customer"]["name"]),
                (10, &json!("Gbenga Ali"))
            );
            assert_eq!(db.queries.get(), if batched { 3 } else { 41 });
        }
    }

    fn hex(bytes: &[u8]) -> String {
        bytes
            .iter()
            .map(|b| format!("{b:02x}"))
            .collect::<Vec<_>>()
            .join(" ")
    }

    #[test]
    fn varints_and_tags_as_in_the_protobuf_documentation() {
        assert_eq!(hex(&varint(1)), "01");
        assert_eq!(hex(&varint(150)), "96 01");
        assert_eq!(hex(&varint(300)), "ac 02");
        assert_eq!(hex(&varint(1 << 35)), "80 80 80 80 80 01");
        assert_eq!(
            hex(&encode_order_summary(150, "testing", 1)),
            "08 96 01 12 07 74 65 73 74 69 6e 67 18 01"
        );
    }

    #[test]
    fn the_same_summary_17_bytes_as_protobuf_50_as_json() {
        assert_eq!(encode_order_summary(1, "Gbenga Ali", 8996).len(), 17);
        assert_eq!(
            size(&json!({ "id": 1, "customer": "Gbenga Ali", "totalPence": 8996 })),
            50
        );
    }

    #[test]
    fn a_synchronous_chain() {
        let c = chain(&[(0.999, 20.0); 5]);
        assert_eq!(format!("{:.2}", c.availability * 100.0), "99.50");
        assert_eq!(c.sequential_ms, 100.0);
        assert_eq!(
            chain(&[(1.0, 30.0), (1.0, 50.0), (1.0, 20.0)]).parallel_ms,
            50.0
        );
    }
}
