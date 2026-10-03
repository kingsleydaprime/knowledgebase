//! The arithmetic behind choosing a monolith, microservices or serverless, and a modular-monolith boundary
//! checker. The same numbers as the TypeScript lab.
use std::collections::{HashMap, HashSet};

pub fn coordination_links(people: u64) -> u64 {
    people * (people - 1) / 2
}

pub fn release_breaks(changes: i32, p: f64) -> f64 {
    1.0 - (1.0 - p).powi(changes)
}

/// (ms added, chance all calls succeed) when a module moves behind the network.
pub fn extract(calls_per_request: i32, network_ms: f64, call_availability: f64) -> (f64, f64) {
    (
        f64::from(calls_per_request) * network_ms,
        call_availability.powi(calls_per_request),
    )
}

pub struct Pricing {
    pub per_million_requests: f64,
    pub per_gb_second: f64,
}

pub fn serverless_monthly(requests: f64, ms: f64, memory_gb: f64, p: &Pricing) -> f64 {
    requests / 1e6 * p.per_million_requests + requests * (ms / 1000.0) * memory_gb * p.per_gb_second
}

pub fn break_even_requests(server_monthly: f64, ms: f64, memory_gb: f64, p: &Pricing) -> f64 {
    server_monthly / (p.per_million_requests / 1e6 + (ms / 1000.0) * memory_gb * p.per_gb_second)
}

pub fn cold_share(per_minute: f64, warm_minutes: f64) -> f64 {
    (-per_minute * warm_minutes).exp()
}

pub fn simulate_cold_share(per_minute: f64, warm_minutes: f64, requests: u32, seed: u32) -> f64 {
    let mut a = seed;
    let mut random = move || {
        // mulberry32, as in week 1's lab
        a = a.wrapping_add(0x6d2b79f5);
        let mut t = (a ^ (a >> 15)).wrapping_mul(a | 1);
        t ^= t.wrapping_add((t ^ (t >> 7)).wrapping_mul(t | 61));
        f64::from(t ^ (t >> 14)) / 4_294_967_296.0
    };
    let cold = (0..requests)
        .filter(|_| -(1.0 - random()).ln() / per_minute > warm_minutes)
        .count();
    cold as f64 / f64::from(requests)
}

pub struct Module {
    pub name: &'static str,
    pub imports: Vec<&'static str>,
}

/// Imports that reach inside another module. In a Rust workspace, items not marked `pub` can't be reached at all.
pub fn boundary_violations(modules: &[Module]) -> Vec<String> {
    let names: HashSet<&str> = modules.iter().map(|m| m.name).collect();
    let mut out = Vec::new();
    for m in modules {
        for imp in &m.imports {
            let (target, inside) = imp
                .split_once('/')
                .map_or((*imp, false), |(t, _)| (t, true));
            if target != m.name && names.contains(target) && inside {
                out.push(format!("{} → {imp}", m.name));
            }
        }
    }
    out
}

/// A dependency cycle as a path that starts and ends at the same module. (Cargo refuses cycles between crates.)
pub fn find_cycle(modules: &[Module]) -> Option<Vec<&'static str>> {
    let mut deps: HashMap<&str, Vec<&'static str>> = HashMap::new();
    for m in modules {
        let entry = deps.entry(m.name).or_default();
        for imp in &m.imports {
            let d = imp.split('/').next().unwrap_or(imp);
            if d != m.name && !entry.contains(&d) {
                entry.push(d);
            }
        }
    }
    fn visit(
        name: &'static str,
        deps: &HashMap<&str, Vec<&'static str>>,
        state: &mut HashMap<&'static str, bool>,
        path: &mut Vec<&'static str>,
    ) -> Option<Vec<&'static str>> {
        match state.get(name) {
            Some(true) => return None, // done
            Some(false) => {
                // still being visited: we've come back round
                let start = path.iter().position(|&p| p == name)?;
                return Some([&path[start..], &[name]].concat());
            }
            None => {}
        }
        state.insert(name, false);
        path.push(name);
        for &d in deps.get(name).into_iter().flatten() {
            if let Some(cycle) = visit(d, deps, state, path) {
                return Some(cycle);
            }
        }
        path.pop();
        state.insert(name, true);
        None
    }
    let (mut state, mut path) = (HashMap::new(), Vec::new());
    modules
        .iter()
        .find_map(|m| visit(m.name, &deps, &mut state, &mut path))
}

#[cfg(test)]
mod tests {
    use super::*;

    const PRICE: Pricing = Pricing {
        per_million_requests: 0.2,
        per_gb_second: 0.0000166667,
    };

    #[test]
    fn coordination_grows_with_the_square() {
        assert_eq!([4, 8, 50].map(coordination_links), [6, 28, 1_225]);
    }

    #[test]
    fn a_shared_release_breaks_more_often() {
        assert_eq!(
            format!(
                "{:.1} {:.1}",
                release_breaks(40, 0.01) * 100.0,
                release_breaks(5, 0.01) * 100.0
            ),
            "33.1 4.9"
        );
    }

    #[test]
    fn chatty_versus_coarse() {
        let ((ms, a), (cms, ca)) = (extract(40, 1.0, 0.9999), extract(1, 1.0, 0.9999));
        assert_eq!(
            format!("{ms} {:.2} {cms} {:.2}", a * 100.0, ca * 100.0),
            "40 99.60 1 99.99"
        );
    }

    #[test]
    fn serverless_until_traffic_is_steady() {
        assert_eq!(
            format!("{:.2}", serverless_monthly(1_000_000.0, 200.0, 0.5, &PRICE)),
            "1.87"
        );
        assert_eq!(
            format!(
                "{:.2}",
                serverless_monthly(50_000_000.0, 200.0, 0.5, &PRICE)
            ),
            "93.33"
        );
        assert_eq!(
            (break_even_requests(30.0, 200.0, 0.5, &PRICE) / 1e5).round() / 10.0,
            16.1
        );
    }

    #[test]
    fn cold_starts_hit_quiet_functions() {
        assert_eq!(
            [10.0, 1.0, 0.1].map(|r| format!("{:.2}", cold_share(r, 5.0) * 100.0)),
            ["0.00", "0.67", "60.65"]
        );
        for rate in [1.0, 0.1] {
            assert!(
                (simulate_cold_share(rate, 5.0, 100_000, 7) - cold_share(rate, 5.0)).abs() < 0.005
            );
        }
    }

    #[test]
    fn boundaries_and_cycles() {
        let mut shop = vec![
            Module {
                name: "orders",
                imports: vec!["billing", "catalog/internal/prices"],
            },
            Module {
                name: "billing",
                imports: vec!["customers"],
            },
            Module {
                name: "catalog",
                imports: vec!["catalog/internal/prices"],
            },
            Module {
                name: "customers",
                imports: vec![],
            },
        ];
        assert_eq!(
            boundary_violations(&shop),
            ["orders → catalog/internal/prices"]
        );
        assert_eq!(find_cycle(&shop), None);
        shop[3].imports.push("orders");
        assert_eq!(
            find_cycle(&shop),
            Some(vec!["orders", "billing", "customers", "orders"])
        );
    }
}
