//! Pricing in exact integer money, prefix diagnosis, canonical JSON, a cascade and latency
//! percentiles. The same numbers as the TypeScript lab.
use std::fmt;
use std::iter::Sum;
use std::ops::{Add, Mul};
use std::time::Duration;
use tokio::sync::mpsc;
use tokio::time::Instant;

/// Millionths of a millionth of a dollar. A token count times a price in micro-dollars per million
/// tokens is a whole number of them, so sums are exact. A newtype keeps money from mixing with counts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Default)]
pub struct Picodollars(pub u64);

impl Add for Picodollars {
    type Output = Self;
    fn add(self, other: Self) -> Self {
        Picodollars(self.0 + other.0)
    }
}

impl Mul<u64> for Picodollars {
    type Output = Self;
    fn mul(self, n: u64) -> Self {
        Picodollars(self.0 * n)
    }
}

impl Sum for Picodollars {
    fn sum<I: Iterator<Item = Self>>(iter: I) -> Self {
        iter.fold(Picodollars(0), Add::add)
    }
}

impl fmt::Display for Picodollars {
    /// Dollars, without trailing zeros: 2.5138.
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let text = format!(
            "{}.{:012}",
            self.0 / 1_000_000_000_000,
            self.0 % 1_000_000_000_000
        );
        f.write_str(text.trim_end_matches('0').trim_end_matches('.'))
    }
}

/// Micro-dollars per million tokens: $2.50 is 2_500_000.
#[derive(Debug, Clone, Copy)]
pub struct Price {
    pub input: u64,
    pub output: u64,
    pub cache_write: u64,
    pub cache_read: u64,
}

/// Anthropic's list prices on 2026-10-02, with 5-minute cache writes. Check before relying on them.
pub const SONNET_5_5: Price = Price {
    input: 2_000_000,
    output: 10_000_000,
    cache_write: 2_500_000,
    cache_read: 200_000,
};
pub const HAIKU_4_5: Price = Price {
    input: 1_000_000,
    output: 5_000_000,
    cache_write: 1_250_000,
    cache_read: 100_000,
};
pub const OPUS_5_5: Price = Price {
    input: 4_000_000,
    output: 20_000_000,
    cache_write: 5_000_000,
    cache_read: 200_000,
};

/// `input` counts only input that was neither written to nor read from the cache.
#[derive(Debug, Clone, Copy, Default)]
pub struct Usage {
    pub input: u64,
    pub output: u64,
    pub cache_write: u64,
    pub cache_read: u64,
}

pub fn cost(u: Usage, p: Price) -> Picodollars {
    Picodollars(
        u.input * p.input
            + u.output * p.output
            + u.cache_write * p.cache_write
            + u.cache_read * p.cache_read,
    )
}

/// Caching n calls costs write + (n − 1) × read; not caching costs n × input.
pub fn break_even_calls(p: Price) -> u64 {
    (p.cache_write - p.cache_read) / (p.input - p.cache_read) + 1 // integer division is the floor here
}

/// Counted in bytes, which equals characters for ASCII text like this lesson's prompts.
pub fn shared_prefix(a: &str, b: &str) -> usize {
    a.bytes().zip(b.bytes()).take_while(|(x, y)| x == y).count()
}

/// serde_json's `Value` keeps object keys in a sorted map, so `to_string` is already canonical.
/// (Unless the `preserve_order` feature is on.) A std `HashMap` is different: its order changes
/// from one run of the program to the next, so never serialise one into a prompt.
pub fn stable_json(value: &serde_json::Value) -> String {
    value.to_string()
}

pub struct Tier<'a> {
    pub name: &'a str,
    pub cost: Picodollars, // per call
    pub answer: &'a dyn Fn(&str) -> String,
    pub accept: fn(&str) -> bool, // the last tier's answer is used whatever this says
}

pub fn cascade<'a>(input: &str, tiers: &[Tier<'a>]) -> (String, &'a str, Picodollars) {
    let mut spent = Picodollars(0);
    for (i, tier) in tiers.iter().enumerate() {
        let answer = (tier.answer)(input);
        spent = spent + tier.cost; // a rejected answer was still paid for
        if i == tiers.len() - 1 || (tier.accept)(&answer) {
            return (answer, tier.name, spent);
        }
    }
    panic!("a cascade needs at least one tier")
}

/// Nearest rank: the smallest value that at least p% of the values are less than or equal to.
pub fn percentile(values: &[Duration], p: f64) -> Duration {
    let mut sorted = values.to_vec();
    sorted.sort();
    sorted[((p / 100.0 * sorted.len() as f64).ceil() as usize).max(1) - 1]
}

/// Reads chunks until the sender is dropped, timing the first one separately.
pub async fn time_stream(mut chunks: mpsc::Receiver<String>) -> (String, Duration, Duration) {
    let started = Instant::now();
    let (mut text, mut ttft) = (String::new(), None);
    while let Some(chunk) = chunks.recv().await {
        ttft.get_or_insert_with(|| started.elapsed());
        text.push_str(&chunk);
    }
    let total = started.elapsed();
    (text, ttft.unwrap_or(total), total)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::collections::HashMap;

    #[test]
    fn output_costs_five_times_input() {
        assert_eq!(
            cost(
                Usage {
                    input: 2000,
                    output: 500,
                    ..Default::default()
                },
                SONNET_5_5
            )
            .to_string(),
            "0.009"
        );
        assert!(HAIKU_4_5.input < SONNET_5_5.input && SONNET_5_5.input < OPUS_5_5.input);
    }

    #[test]
    fn caching_a_6000_token_prefix_across_1000_calls() {
        let uncached = cost(
            Usage {
                input: 6150,
                output: 100,
                ..Default::default()
            },
            SONNET_5_5,
        ) * 1000;
        let first = cost(
            Usage {
                cache_write: 6000,
                input: 150,
                output: 100,
                ..Default::default()
            },
            SONNET_5_5,
        );
        let each = cost(
            Usage {
                cache_read: 6000,
                input: 150,
                output: 100,
                ..Default::default()
            },
            SONNET_5_5,
        );
        let cached: Picodollars = std::iter::once(first)
            .chain(std::iter::repeat_n(each, 999))
            .sum();
        assert_eq!(
            (uncached.to_string(), cached.to_string()),
            ("13.3".into(), "2.5138".into())
        ); // exact
        let output = cost(
            Usage {
                output: 100,
                ..Default::default()
            },
            SONNET_5_5,
        ) * 1000;
        assert_eq!((output.0 as f64 / cached.0 as f64 * 100.0).round(), 40.0);
    }

    #[test]
    fn a_cache_write_pays_for_itself_on_the_second_call() {
        let one_hour = Price {
            cache_write: 4_000_000,
            ..SONNET_5_5
        }; // 1-hour entries cost 2× to write
        assert_eq!(
            (break_even_calls(SONNET_5_5), break_even_calls(one_hour)),
            (2, 3)
        );
    }

    #[test]
    fn a_timestamp_at_the_front_leaves_nothing_to_cache() {
        let system =
            "You classify support tickets. Label by what the team has to do next. ".repeat(20);
        let front = |date: &str| format!("Today is {date}.\n{system}\nhelp");
        let end = |date: &str| format!("{system}\nToday is {date}.\nhelp");
        let (a, b) = ("2026-10-02T09:00:00Z", "2026-10-02T09:00:07Z");
        assert_eq!(shared_prefix(&front(a), &front(b)), 27);
        assert_eq!(shared_prefix(&end(a), &end(b)), system.len() + 28);
    }

    #[test]
    fn json_objects_come_out_sorted() {
        let b = json!({"user": {"tier": "pro", "id": 7}, "tools": ["search"]});
        assert_eq!(
            stable_json(&b),
            r#"{"tools":["search"],"user":{"id":7,"tier":"pro"}}"#
        );
        // A HashMap's order isn't even stable between two maps holding the same keys, so only the
        // sorted Value is safe to put in a prompt.
        let map: HashMap<&str, i32> = [("b", 1), ("a", 2)].into();
        assert_eq!(
            stable_json(&serde_json::to_value(&map).unwrap()),
            r#"{"a":2,"b":1}"#
        );
    }

    #[test]
    fn a_cascade_from_keywords_to_a_big_model() {
        let golden = evals::load_golden("../../../12-evals/labs/shared/golden.jsonl");
        let label: HashMap<&str, &str> = golden
            .iter()
            .map(|c| (c.ticket.as_str(), c.label.as_str()))
            .collect();
        let lookup = |t: &str| label[t].to_string(); // a stand-in for a big model that is always right
        let tiers = [
            Tier {
                name: "keywords",
                cost: Picodollars(0),
                answer: &evals::keywords,
                accept: |a| a != "other",
            },
            Tier {
                name: "big",
                cost: Picodollars(2_000_000_000),
                answer: &lookup,
                accept: |_| true,
            },
        ];
        let results: Vec<_> = golden
            .iter()
            .map(|c| (c, cascade(&c.ticket, &tiers)))
            .collect();
        let escalated: Vec<_> = results
            .iter()
            .filter(|(_, (_, by, _))| *by == "big")
            .map(|(c, _)| c.id.as_str())
            .collect();
        let wrong: Vec<_> = results
            .iter()
            .filter(|(c, (a, _, _))| *a != c.label)
            .map(|(c, _)| c.id.as_str())
            .collect();
        let total: Picodollars = results.iter().map(|(_, (_, _, spent))| *spent).sum();
        assert_eq!(escalated, ["t04", "t10", "t12", "t14", "t17", "t19"]);
        assert_eq!(wrong, ["t15", "t20"]);
        assert_eq!(total.to_string(), "0.012");
    }

    #[test]
    fn p95_shows_the_slow_call_the_median_hides() {
        let ms: Vec<Duration> = [1200, 900, 1100, 1000, 950, 1050, 980, 1020, 990, 9000]
            .map(Duration::from_millis)
            .to_vec();
        assert_eq!(
            (percentile(&ms, 50.0), percentile(&ms, 95.0)),
            (Duration::from_secs(1), Duration::from_secs(9))
        );
    }

    #[tokio::test(start_paused = true)]
    async fn time_to_first_token_is_measured_apart() {
        let (send, receive) = mpsc::channel(8);
        tokio::spawn(async move {
            tokio::time::sleep(Duration::from_millis(800)).await; // the model reads the prompt first
            for word in ["Your", " refund", " is", " on", " its", " way."] {
                if word != "Your" {
                    tokio::time::sleep(Duration::from_millis(100)).await;
                }
                send.send(word.to_string()).await.unwrap();
            }
        });
        let (text, ttft, total) = time_stream(receive).await;
        assert_eq!(
            (text.as_str(), ttft, total),
            (
                "Your refund is on its way.",
                Duration::from_millis(800),
                Duration::from_millis(1300)
            )
        );
    }
}
