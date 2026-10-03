//! The three join algorithms, each counting its work, and two classic estimation failures. Same model as the
//! Python lab. Rows are (key, value) pairs; joins return (outer value, inner value) pairs.
use std::collections::HashMap;

pub type Row = (u32, String);
pub type Joined = Vec<(String, String)>;

/// For every outer row, look at every inner row: N × M comparisons.
pub fn nested_loop(outer: &[Row], inner: &[Row]) -> (Joined, u64) {
    let (mut out, mut comparisons) = (Vec::new(), 0);
    for (ok, ov) in outer {
        for (ik, iv) in inner {
            comparisons += 1;
            if ok == ik {
                out.push((ov.clone(), iv.clone()));
            }
        }
    }
    (out, comparisons)
}

/// A sorted inner side searched by halving: about N × log₂ M steps.
pub fn index_nested_loop(outer: &[Row], inner_sorted: &[Row]) -> (Joined, u64) {
    let (mut out, mut steps) = (Vec::new(), 0);
    for (ok, ov) in outer {
        let (mut lo, mut hi) = (0, inner_sorted.len());
        while lo < hi {
            steps += 1;
            let mid = (lo + hi) / 2;
            if inner_sorted[mid].0 < *ok {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        out.extend(
            inner_sorted[lo..]
                .iter()
                .take_while(|(k, _)| k == ok)
                .map(|(_, iv)| (ov.clone(), iv.clone())),
        );
    }
    (out, steps)
}

/// Build a HashMap on the inner side, probe it once per outer row: N + M operations. Equality only.
pub fn hash_join(outer: &[Row], inner: &[Row]) -> (Joined, u64) {
    let mut table: HashMap<u32, Vec<&str>> = HashMap::new();
    for (ik, iv) in inner {
        table.entry(*ik).or_default().push(iv);
    }
    let out = outer
        .iter()
        .flat_map(|(ok, ov)| {
            table
                .get(ok)
                .into_iter()
                .flatten()
                .map(move |iv| (ov.clone(), iv.to_string()))
        })
        .collect();
    (out, (inner.len() + outer.len()) as u64)
}

/// Both sides sorted by key: walk them together, about N + M steps.
pub fn merge_join(outer_sorted: &[Row], inner_sorted: &[Row]) -> (Joined, u64) {
    let (mut out, mut steps, mut i, mut j) = (Vec::new(), 0, 0, 0);
    while i < outer_sorted.len() && j < inner_sorted.len() {
        steps += 1;
        let (ok, ik) = (outer_sorted[i].0, inner_sorted[j].0);
        match ok.cmp(&ik) {
            std::cmp::Ordering::Less => i += 1,
            std::cmp::Ordering::Greater => j += 1,
            std::cmp::Ordering::Equal => {
                let group = inner_sorted[j..].iter().take_while(|(k, _)| *k == ok);
                out.extend(group.map(|(_, iv)| (outer_sorted[i].1.clone(), iv.clone())));
                i += 1; // the next outer row may share the key, so j stays at the start of the group
            }
        }
    }
    (out, steps)
}

pub fn independent_estimate(rows: f64, selectivities: &[f64]) -> f64 {
    selectivities.iter().fold(rows, |estimate, s| estimate * s)
}

pub fn rows_read_for_page(offset: u64, limit: u64, keyset: bool) -> u64 {
    if keyset { limit } else { offset + limit }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn data() -> (Vec<Row>, Vec<Row>) {
        let orders = (0..10_000)
            .map(|i| (1 + i % 1_000, format!("order {i}")))
            .collect();
        let customers = (1..=1_000).map(|c| (c, format!("customer {c}"))).collect();
        (orders, customers)
    }

    fn canonical(mut rows: Joined) -> Joined {
        rows.sort();
        rows
    }

    fn by_key(rows: &[Row]) -> Vec<Row> {
        let mut sorted = rows.to_vec();
        sorted.sort_by_key(|r| r.0); // stable
        sorted
    }

    #[test]
    fn all_three_give_the_same_answer() {
        let (orders, customers) = data();
        let expected = canonical(nested_loop(&orders, &customers).0);
        assert_eq!(expected.len(), 10_000);
        assert_eq!(
            canonical(index_nested_loop(&orders, &customers).0),
            expected
        );
        assert_eq!(canonical(hash_join(&orders, &customers).0), expected);
        assert_eq!(
            canonical(merge_join(&by_key(&orders), &customers).0),
            expected
        );
    }

    #[test]
    fn they_differ_enormously_in_work() {
        let (orders, customers) = data();
        let work = [
            nested_loop(&orders, &customers).1,
            index_nested_loop(&orders, &customers).1,
            hash_join(&orders, &customers).1,
            merge_join(&by_key(&orders), &customers).1,
        ];
        assert_eq!(work, [10_000_000, 99_780, 11_000, 10_999]);
        let one: Vec<Row> = orders.iter().filter(|r| r.0 == 42).cloned().collect();
        assert_eq!(
            (
                index_nested_loop(&one, &customers).1,
                hash_join(&one, &customers).1
            ),
            (100, 1_010)
        );
    }

    #[test]
    fn correlated_columns_and_pagination() {
        assert_eq!(independent_estimate(30_000.0, &[0.1, 0.3]).round(), 900.0);
        assert_eq!(independent_estimate(30_000.0, &[0.1]).round(), 3_000.0);
        assert_eq!(
            (
                rows_read_for_page(100_000, 20, false),
                rows_read_for_page(100_000, 20, true)
            ),
            (100_020, 20)
        );
    }
}
