//! How a load balancer picks a server, health checks that take a failing server out and put it back, and
//! consistent hashing. The same numbers as the TypeScript lab.
use std::collections::VecDeque;

/// Chooses a server from how many requests each is still working on. FnMut, because round-robin keeps a turn.
pub trait Pick: FnMut(&[usize], &mut dyn FnMut() -> f64) -> usize {}
impl<F: FnMut(&[usize], &mut dyn FnMut() -> f64) -> usize> Pick for F {}

pub fn round_robin() -> impl Pick {
    let mut next = 0;
    move |outstanding: &[usize], _: &mut dyn FnMut() -> f64| {
        let chosen = next % outstanding.len();
        next += 1;
        chosen
    }
}

/// The fewest requests in progress; ties go to the lowest number.
pub fn least_outstanding(outstanding: &[usize], _: &mut dyn FnMut() -> f64) -> usize {
    let min = outstanding.iter().min().expect("at least one server");
    outstanding
        .iter()
        .position(|n| n == min)
        .expect("the minimum is in the list")
}

pub fn random(outstanding: &[usize], rand: &mut dyn FnMut() -> f64) -> usize {
    (rand() * outstanding.len() as f64) as usize
}

/// Two servers at random, and the less busy of the two.
pub fn two_choices(outstanding: &[usize], rand: &mut dyn FnMut() -> f64) -> usize {
    let a = (rand() * outstanding.len() as f64) as usize;
    let b = (rand() * outstanding.len() as f64) as usize;
    if outstanding[b] < outstanding[a] {
        b
    } else {
        a
    }
}

/// mulberry32, the same generator as week 1's lab.
pub fn seeded(seed: u32) -> impl FnMut() -> f64 {
    let mut a = seed;
    move || {
        a = a.wrapping_add(0x6d2b79f5);
        let mut t = (a ^ (a >> 15)).wrapping_mul(a | 1);
        t ^= t.wrapping_add((t ^ (t >> 7)).wrapping_mul(t | 61));
        f64::from(t ^ (t >> 14)) / 4_294_967_296.0
    }
}

#[derive(Debug, PartialEq)]
pub struct Latency {
    pub mean: f64,
    pub p50: f64,
    pub p99: f64,
}

/// Random traffic to servers that each work through their own queue. 1 in 20 requests takes 200 ms.
pub fn simulate(
    mut pick: impl Pick,
    servers: usize,
    busy: f64,
    requests: usize,
    seed: u32,
) -> Latency {
    let mut rand = seeded(seed);
    let mean_work_ms = 0.95 * 10.0 + 0.05 * 200.0;
    let gap_ms = mean_work_ms / (busy * servers as f64);
    let mut finishes: Vec<VecDeque<f64>> = vec![VecDeque::new(); servers]; // per server: when each queued request ends
    let (mut now, mut total) = (0.0_f64, 0.0);
    let mut times = Vec::with_capacity(requests);
    for _ in 0..requests {
        now += -gap_ms * (1.0 - rand()).ln();
        for queue in &mut finishes {
            while queue.front().is_some_and(|&ends| ends <= now) {
                queue.pop_front();
            }
        }
        let outstanding: Vec<usize> = finishes.iter().map(VecDeque::len).collect();
        let s = pick(&outstanding, &mut rand);
        let work_ms = if rand() < 0.05 { 200.0 } else { 10.0 };
        let ends = now.max(finishes[s].back().copied().unwrap_or(0.0)) + work_ms;
        finishes[s].push_back(ends);
        times.push(ends - now);
        total += ends - now;
    }
    times.sort_by(f64::total_cmp);
    let percentile = |p: f64| times[((p / 100.0 * times.len() as f64).ceil() as usize).max(1) - 1];
    Latency {
        mean: (total / requests as f64).round(),
        p50: percentile(50.0).round(),
        p99: percentile(99.0).round(),
    }
}

/// nginx's smooth weighted round-robin: each server gains its weight; the highest is chosen and pays the total.
pub fn smooth_weighted(weights: &[(&'static str, i32)]) -> impl FnMut() -> &'static str {
    let weights = weights.to_vec();
    let total: i32 = weights.iter().map(|w| w.1).sum();
    let mut current = vec![0; weights.len()];
    move || {
        let mut best = 0;
        for (i, (_, weight)) in weights.iter().enumerate() {
            current[i] += weight;
            if current[i] > current[best] {
                best = i;
            }
        }
        current[best] -= total;
        weights[best].0
    }
}

/// `fall` failures in a row mark a server down; `rise` successes in a row bring it back.
pub struct Health {
    pub up: bool,
    fall: u32,
    rise: u32,
    streak: u32,
}

impl Health {
    pub fn new(fall: u32, rise: u32) -> Self {
        Health {
            up: true,
            fall,
            rise,
            streak: 0,
        }
    }

    pub fn record(&mut self, ok: bool) {
        if ok == self.up {
            self.streak = 0;
            return;
        }
        self.streak += 1;
        if self.streak >= if self.up { self.fall } else { self.rise } {
            self.up = !self.up;
            self.streak = 0;
        }
    }
}

pub fn pick_healthy<'a>(
    servers: &'a [(&'a str, Health)],
    turn: usize,
) -> Result<&'a str, &'static str> {
    let up: Vec<&str> = servers
        .iter()
        .filter(|(_, h)| h.up)
        .map(|(name, _)| *name)
        .collect();
    if up.is_empty() {
        return Err("no healthy servers: answer 503");
    }
    Ok(up[turn % up.len()])
}

/// FNV-1a, then a mixing step. Over bytes, which for these ASCII keys are JavaScript's UTF-16 code units.
/// std's HashMap hasher is randomly seeded per process, so it can't be used to place keys on servers.
pub fn hash(text: &str) -> u32 {
    let mut h: u32 = 0x811c9dc5;
    for byte in text.bytes() {
        h = (h ^ u32::from(byte)).wrapping_mul(0x01000193);
    }
    h = (h ^ (h >> 16)).wrapping_mul(0x85ebca6b);
    h = (h ^ (h >> 13)).wrapping_mul(0xc2b2ae35);
    h ^ (h >> 16)
}

pub fn modulo<'a>(key: &str, servers: &[&'a str]) -> &'a str {
    servers[hash(key) as usize % servers.len()]
}

/// Servers and keys on one circle of hash values; a key belongs to the first server clockwise from it.
pub struct HashRing {
    points: Vec<(u32, String)>, // sorted by position
    replicas: usize,
}

impl HashRing {
    pub fn new(servers: &[&str], replicas: usize) -> Self {
        let mut ring = HashRing {
            points: Vec::new(),
            replicas,
        };
        for s in servers {
            ring.add(s);
        }
        ring
    }

    pub fn add(&mut self, server: &str) {
        self.points.extend(
            (0..self.replicas).map(|r| (hash(&format!("{server}#{r}")), server.to_string())),
        );
        self.points.sort_by_key(|p| p.0); // sort_by_key is stable, like JavaScript's sort
    }

    pub fn remove(&mut self, server: &str) {
        self.points.retain(|p| p.1 != server);
    }

    pub fn server_for(&self, key: &str) -> &str {
        assert!(!self.points.is_empty(), "the ring is empty");
        let h = hash(key);
        let i = self.points.partition_point(|p| p.0 < h); // the first point at or after h
        &self.points[i % self.points.len()].1 // past the last point, wrap round to the first
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    const FOUR: [&str; 4] = ["cache-a", "cache-b", "cache-c", "cache-d"];

    fn keys() -> Vec<String> {
        (0..10_000).map(|i| format!("user:{i}")).collect()
    }

    #[test]
    fn round_robin_takes_turns_least_outstanding_looks() {
        let (mut pick, queues) = (round_robin(), [5, 0, 0]);
        let mut never = || 0.0;
        let turns: Vec<usize> = (0..6).map(|_| pick(&queues, &mut never)).collect();
        assert_eq!(turns, [0, 1, 2, 0, 1, 2]);
        assert_eq!(least_outstanding(&queues, &mut never), 1);
    }

    #[test]
    fn smooth_weighted_round_robin() {
        let mut pick = smooth_weighted(&[("a", 5), ("b", 1), ("c", 1)]);
        assert_eq!((0..7).map(|_| pick()).collect::<String>(), "aabacaa");
    }

    #[test]
    fn algorithms_that_look_at_queues_win_in_the_tail() {
        let latency = |mean, p50, p99| Latency { mean, p50, p99 };
        assert_eq!(
            simulate(round_robin(), 4, 0.8, 100_000, 7),
            latency(214.0, 138.0, 1_158.0)
        );
        assert_eq!(
            simulate(random, 4, 0.8, 100_000, 7),
            latency(255.0, 159.0, 1_588.0)
        );
        assert_eq!(
            simulate(least_outstanding, 4, 0.8, 100_000, 7),
            latency(68.0, 17.0, 466.0)
        );
        assert_eq!(
            simulate(two_choices, 4, 0.8, 100_000, 7),
            latency(96.0, 25.0, 495.0)
        );
    }

    #[test]
    fn three_failures_to_go_down_two_successes_to_come_back() {
        let mut health = Health::new(3, 2);
        let states: Vec<bool> = [false, false, true, false, false, false, true, true]
            .iter()
            .map(|&ok| {
                health.record(ok);
                health.up
            })
            .collect();
        assert_eq!(states, [true, true, true, true, true, false, false, true]);
    }

    #[test]
    fn skips_down_servers_and_fails_when_all_are_down() {
        let mut servers = ["app-1", "app-2", "app-3"].map(|name| (name, Health::new(3, 2)));
        for _ in 0..3 {
            servers[1].1.record(false);
        }
        let picked: Vec<&str> = (0..4)
            .map(|turn| pick_healthy(&servers, turn).unwrap())
            .collect();
        assert_eq!(picked, ["app-1", "app-3", "app-1", "app-3"]);
        for (_, health) in &mut servers {
            for _ in 0..3 {
                health.record(false);
            }
        }
        assert!(pick_healthy(&servers, 0).is_err());
    }

    #[test]
    fn modulo_moves_four_in_five_a_ring_about_one_in_five() {
        let (keys, five) = (keys(), [FOUR.as_slice(), &["cache-e"]].concat());
        let moved_by_modulo = keys
            .iter()
            .filter(|k| modulo(k, &FOUR) != modulo(k, &five))
            .count();
        assert!(moved_by_modulo.abs_diff(8_000) < 200, "{moved_by_modulo}");
        let mut ring = HashRing::new(&FOUR, 100);
        let before: Vec<String> = keys
            .iter()
            .map(|k| ring.server_for(k).to_string())
            .collect();
        ring.add("cache-e");
        let moved: Vec<&String> = keys
            .iter()
            .zip(&before)
            .filter(|(k, b)| ring.server_for(k) != *b)
            .map(|(k, _)| k)
            .collect();
        assert!(moved.len().abs_diff(2_000) < 300, "{}", moved.len());
        assert!(moved.iter().all(|k| ring.server_for(k) == "cache-e"));
        ring.remove("cache-e");
        assert!(
            keys.iter()
                .zip(&before)
                .all(|(k, b)| ring.server_for(k) == b)
        );
    }

    #[test]
    fn virtual_nodes_even_out_the_keys() {
        let busiest = |replicas| {
            let ring = HashRing::new(&FOUR, replicas);
            let mut counts: HashMap<&str, usize> = HashMap::new();
            for k in keys() {
                *counts.entry(ring.server_for(&k)).or_default() += 1;
            }
            *counts.values().max().unwrap() as f64 / (10_000.0 / 4.0)
        };
        assert!(busiest(1) > 1.4, "{}", busiest(1));
        assert!(busiest(100) < 1.2, "{}", busiest(100));
    }
}
