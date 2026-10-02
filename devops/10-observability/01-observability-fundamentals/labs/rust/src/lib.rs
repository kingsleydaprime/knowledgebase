//! A Prometheus-style histogram. In services, the `metrics` crate with a Prometheus exporter
//! (or the `prometheus` crate) records these; the estimate below is what Prometheus computes.
pub struct Histogram {
    bounds: Vec<f64>, // ascending upper bounds; one extra bucket for +Inf
    counts: Vec<u64>,
}

impl Histogram {
    pub fn new(bounds: &[f64]) -> Self {
        Histogram {
            bounds: bounds.to_vec(),
            counts: vec![0; bounds.len() + 1],
        }
    }

    pub fn observe(&mut self, value: f64) {
        // "le": the first bucket whose bound is >= the value
        let i = self
            .bounds
            .iter()
            .position(|&b| value <= b)
            .unwrap_or(self.bounds.len());
        self.counts[i] += 1;
    }

    pub fn estimate_quantile(&self, q: f64) -> f64 {
        let total: u64 = self.counts.iter().sum();
        let rank = q * total as f64;
        let (mut lower, mut cumulative) = (0.0, 0.0);
        for (i, &count) in self.counts.iter().enumerate() {
            let before = cumulative;
            cumulative += count as f64;
            if cumulative >= rank {
                return match self.bounds.get(i) {
                    Some(&upper) => {
                        lower + (upper - lower) * (rank - before) / (cumulative - before)
                    }
                    None => lower, // the +Inf bucket
                };
            }
            if let Some(&upper) = self.bounds.get(i) {
                lower = upper;
            }
        }
        lower
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bucket_estimates_versus_exact() {
        let mut h = Histogram::new(&[25.0, 50.0, 100.0, 250.0, 500.0, 1000.0, 2500.0, 5000.0]);
        (0..97).for_each(|i| h.observe(20.0 + (i % 10) as f64));
        [1800.0, 2100.0, 3000.0]
            .into_iter()
            .for_each(|ms| h.observe(ms));
        assert!((h.estimate_quantile(0.50) - 20.83).abs() < 0.01); // exact: 24
        assert_eq!(h.estimate_quantile(0.99), 2500.0); // exact: 2100
    }
}
