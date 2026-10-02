//! From a model's scores to one token. Same algorithm, seed and numbers as the TypeScript lab.

/// One token and its score or probability. A Vec keeps a fixed order, so sampling is reproducible.
pub type Dist = Vec<(&'static str, f64)>;

/// mulberry32. Rust's standard library has no seeded generator (the `rand` crate does);
/// this one gives the same numbers in every language in this companion.
pub fn seeded_random(seed: u32) -> impl FnMut() -> f64 {
    let mut a = seed;
    move || {
        a = a.wrapping_add(0x6d2b79f5); // wrapping_ makes the 32-bit overflow explicit
        let mut t = a;
        t = (t ^ (t >> 15)).wrapping_mul(t | 1);
        t ^= t.wrapping_add((t ^ (t >> 7)).wrapping_mul(t | 61));
        f64::from(t ^ (t >> 14)) / 4294967296.0
    }
}

pub fn softmax(scores: &Dist, temperature: f64) -> Dist {
    let top = scores
        .iter()
        .map(|&(_, s)| s / temperature)
        .fold(f64::NEG_INFINITY, f64::max);
    let exps = scores
        .iter()
        .map(|&(tok, s)| (tok, (s / temperature - top).exp()))
        .collect();
    renormalise(exps)
}

fn by_probability(dist: &Dist) -> Dist {
    let mut sorted = dist.clone();
    sorted.sort_by(|x, y| y.1.total_cmp(&x.1)); // stable, descending
    sorted
}

pub fn top_k(dist: &Dist, k: usize) -> Dist {
    renormalise(by_probability(dist).into_iter().take(k).collect())
}

pub fn top_p(dist: &Dist, p: f64) -> Dist {
    let mut kept = Vec::new();
    let mut cumulative = 0.0;
    for entry in by_probability(dist) {
        kept.push(entry);
        cumulative += entry.1;
        if cumulative >= p {
            break;
        }
    }
    renormalise(kept)
}

fn renormalise(entries: Dist) -> Dist {
    let total: f64 = entries.iter().map(|&(_, p)| p).sum();
    entries
        .into_iter()
        .map(|(tok, p)| (tok, p / total))
        .collect()
}

pub fn sample(dist: &Dist, random: &mut impl FnMut() -> f64) -> &'static str {
    let mut r = random();
    for &(tok, p) in dist {
        r -= p;
        if r < 0.0 {
            return tok;
        }
    }
    dist.last()
        .expect("an empty distribution has nothing to sample")
        .0
}

pub fn greedy(dist: &Dist) -> &'static str {
    by_probability(dist)[0].0
}

#[cfg(test)]
mod tests {
    use super::*;

    fn scores() -> Dist {
        vec![("Paris", 4.0), ("a", 2.0), ("the", 1.5), ("Lyon", 0.5)]
    }

    fn rounded(dist: &Dist) -> Vec<f64> {
        dist.iter()
            .map(|&(_, p)| (p * 1000.0).round() / 1000.0)
            .collect()
    }

    fn tokens(dist: &Dist) -> Vec<&str> {
        dist.iter().map(|&(tok, _)| tok).collect()
    }

    #[test]
    fn temperature_reshapes_the_same_scores() {
        assert_eq!(
            rounded(&softmax(&scores(), 1.0)),
            [0.802, 0.108, 0.066, 0.024]
        );
        assert_eq!(
            rounded(&softmax(&scores(), 0.5)),
            [0.975, 0.018, 0.007, 0.001]
        );
        assert_eq!(
            rounded(&softmax(&scores(), 2.0)),
            [0.547, 0.201, 0.157, 0.095]
        );
    }

    #[test]
    fn top_k_and_top_p() {
        let dist = softmax(&scores(), 1.0);
        assert_eq!(tokens(&top_k(&dist, 2)), ["Paris", "a"]);
        assert_eq!(tokens(&top_p(&dist, 0.9)), ["Paris", "a"]);
        assert_eq!(tokens(&top_p(&dist, 0.97)), ["Paris", "a", "the"]);
    }

    #[test]
    fn same_seed_same_numbers_as_every_other_language() {
        let mut r = seeded_random(42);
        assert_eq!(
            [r(), r(), r()],
            [0.6011037519201636, 0.44829055899754167, 0.8524657934904099]
        );
    }

    #[test]
    fn same_seed_same_tokens() {
        let dist = softmax(&scores(), 1.0);
        let mut r = seeded_random(42);
        let picks: Vec<_> = (0..10).map(|_| sample(&dist, &mut r)).collect();
        assert_eq!(
            picks.join(" "),
            "Paris Paris a Paris Paris Paris Paris Paris a Paris"
        );
        let mut r = seeded_random(42);
        let paris = (0..1000)
            .filter(|_| sample(&dist, &mut r) == "Paris")
            .count();
        assert_eq!(paris, 796); // about 80.2%, as expected
    }

    #[test]
    fn greedy_picks_the_top_token() {
        assert_eq!(greedy(&softmax(&scores(), 2.0)), "Paris");
    }
}
