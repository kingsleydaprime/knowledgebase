//! The arithmetic behind performance and scalability. The same numbers as the TypeScript lab, because the
//! random number generator is the same one, bit for bit.

/// Nearest rank: p99 of 1,000 samples is the 990th smallest. None for no samples.
pub fn percentile(samples: &[f64], p: f64) -> Option<f64> {
    if samples.is_empty() {
        return None;
    }
    let mut sorted = samples.to_vec();
    sorted.sort_by(f64::total_cmp); // f64 isn't Ord (NaN has no place), so say how to order it
    let rank = ((p / 100.0 * sorted.len() as f64).ceil() as usize).max(1);
    Some(sorted[rank - 1])
}

pub fn mean(samples: &[f64]) -> f64 {
    samples.iter().sum::<f64>() / samples.len() as f64
}

/// mulberry32. Plain + and * on u32 panic on overflow in a debug build, so the wrap-around is written out.
pub fn seeded(seed: u32) -> impl FnMut() -> f64 {
    let mut a = seed;
    move || {
        a = a.wrapping_add(0x6d2b79f5);
        let mut t = (a ^ (a >> 15)).wrapping_mul(a | 1);
        t ^= t.wrapping_add((t ^ (t >> 7)).wrapping_mul(t | 61));
        f64::from(t ^ (t >> 14)) / 4_294_967_296.0
    }
}

fn exponential(random: &mut impl FnMut() -> f64, mean: f64) -> f64 {
    -mean * (1.0 - random()).ln()
}

/// M/M/1: service time ÷ (1 − utilisation).
pub fn response_time(service_ms: f64, utilisation: f64) -> f64 {
    if utilisation >= 1.0 {
        f64::INFINITY
    } else {
        service_ms / (1.0 - utilisation)
    }
}

#[derive(Debug)]
pub struct Summary {
    pub mean: f64,
    pub p50: f64,
    pub p99: f64,
}

pub fn simulate_server(service_ms: f64, utilisation: f64, requests: usize, seed: u32) -> Summary {
    let mut random = seeded(seed);
    let gap_ms = service_ms / utilisation;
    let (mut arrives, mut free) = (0.0_f64, 0.0_f64);
    let mut times = Vec::with_capacity(requests);
    for _ in 0..requests {
        arrives += exponential(&mut random, gap_ms);
        let starts = arrives.max(free);
        free = starts + exponential(&mut random, service_ms);
        times.push(free - arrives);
    }
    let p = |q| percentile(&times, q).expect("at least one request");
    Summary {
        mean: mean(&times),
        p50: p(50.0),
        p99: p(99.0),
    }
}

/// Every request passes every stage, so the system handles only as many as its slowest.
pub fn throughput<'a>(stages: &[(&'a str, f64)]) -> (&'a str, f64) {
    *stages
        .iter()
        .min_by(|a, b| a.1.total_cmp(&b.1))
        .expect("at least one stage")
}

pub fn amdahl(n: f64, serial: f64) -> f64 {
    1.0 / (serial + (1.0 - serial) / n)
}

pub fn usl(n: f64, alpha: f64, beta: f64) -> f64 {
    n / (1.0 + alpha * (n - 1.0) + beta * n * (n - 1.0))
}

pub fn usl_peak(alpha: f64, beta: f64) -> f64 {
    ((1.0 - alpha) / beta).sqrt()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn percentiles_by_nearest_rank() {
        let tens = [10.0, 1.0, 9.0, 2.0, 8.0, 3.0, 7.0, 4.0, 6.0, 5.0];
        let got = [50.0, 90.0, 99.0, 100.0].map(|p| percentile(&tens, p).unwrap());
        assert_eq!(got, [5.0, 9.0, 10.0, 10.0]);
        assert_eq!(percentile(&[], 50.0), None);
    }

    #[test]
    fn the_average_hides_the_tail() {
        let mut random = seeded(42);
        let latencies: Vec<f64> = (0..1_000)
            .map(|_| {
                if random() < 0.02 {
                    1_500.0 + 1_000.0 * random()
                } else {
                    40.0 + 20.0 * random()
                }
            })
            .collect();
        let got = [
            mean(&latencies),
            percentile(&latencies, 50.0).unwrap(),
            percentile(&latencies, 95.0).unwrap(),
            percentile(&latencies, 99.0).unwrap(),
        ];
        assert_eq!(got.map(f64::round), [93.0, 50.0, 59.0, 2_208.0]);
    }

    #[test]
    fn waiting_grows_slowly_then_all_at_once() {
        let got = [0.5, 0.8, 0.9, 0.95, 0.99].map(|busy| response_time(10.0, busy).round());
        assert_eq!(got, [20.0, 50.0, 100.0, 200.0, 1_000.0]);
        assert_eq!(response_time(10.0, 1.0), f64::INFINITY);
    }

    #[test]
    fn the_simulation_agrees_with_the_formula() {
        for busy in [0.5, 0.8, 0.9] {
            let (sim, model) = (
                simulate_server(10.0, busy, 200_000, 7),
                response_time(10.0, busy),
            );
            assert!((sim.mean - model).abs() / model < 0.1, "{busy}: {sim:?}");
            assert!(
                (sim.p99 / sim.mean - 100f64.ln()).abs() < 0.5,
                "{busy}: {sim:?}"
            );
        }
    }

    #[test]
    fn performance_or_scalability() {
        let got = [
            response_time(300.0, 0.1),
            response_time(10.0, 0.95),
            response_time(10.0, 0.95 / 2.0),
            response_time(300.0, 0.05),
        ];
        assert_eq!(got.map(f64::round), [333.0, 200.0, 19.0, 316.0]);
    }

    #[test]
    fn the_slowest_stage() {
        let mut stages = [
            ("load balancer", 50_000.0),
            ("app servers", 4.0 * 800.0),
            ("database writes", 2_000.0),
        ];
        assert_eq!(throughput(&stages), ("database writes", 2_000.0));
        stages[1].1 = 8.0 * 800.0;
        assert_eq!(throughput(&stages), ("database writes", 2_000.0));
    }

    #[test]
    fn why_adding_machines_stops_helping() {
        assert_eq!(format!("{:.2}", amdahl(8.0, 0.05)), "5.93");
        assert!(amdahl(1_000_000.0, 0.05) < 20.0);
        assert_eq!(usl_peak(0.05, 0.001).round(), 31.0);
        assert_eq!(
            [8.0, 31.0, 60.0, 100.0].map(|n| format!("{:.1}", usl(n, 0.05, 0.001))),
            ["5.7", "9.0", "8.0", "6.3"]
        );
    }
}
