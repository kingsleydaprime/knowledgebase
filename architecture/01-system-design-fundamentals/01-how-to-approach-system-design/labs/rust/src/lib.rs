//! Back-of-the-envelope estimates, and a leaderboard that ranks millions of players in about 20 steps.
//! The same numbers as the TypeScript lab.
use std::collections::HashMap;

pub const SECONDS_PER_DAY: f64 = 86_400.0;

pub struct Assumptions {
    pub daily_active_users: f64,
    pub writes_per_user_per_day: f64,
    pub reads_per_user_per_day: f64,
    pub peak_to_average: f64,
    pub bytes_per_write: f64,
    pub kept_for_days: f64,
    pub bytes_per_read: f64,
}

pub struct Rate {
    pub average: f64,
    pub peak: f64,
}

pub struct Estimate {
    pub writes_per_second: Rate,
    pub reads_per_second: Rate,
    pub reads_per_write: f64,
    pub storage_bytes: f64,
    pub peak_egress_bytes_per_second: f64,
}

pub fn estimate(a: &Assumptions) -> Estimate {
    let writes = a.daily_active_users * a.writes_per_user_per_day / SECONDS_PER_DAY;
    let reads = a.daily_active_users * a.reads_per_user_per_day / SECONDS_PER_DAY;
    Estimate {
        writes_per_second: Rate {
            average: writes,
            peak: writes * a.peak_to_average,
        },
        reads_per_second: Rate {
            average: reads,
            peak: reads * a.peak_to_average,
        },
        reads_per_write: a.reads_per_user_per_day / a.writes_per_user_per_day,
        storage_bytes: a.daily_active_users
            * a.writes_per_user_per_day
            * a.bytes_per_write
            * a.kept_for_days,
        peak_egress_bytes_per_second: reads * a.peak_to_average * a.bytes_per_read,
    }
}

/// Two significant figures in powers of 1,000: 912,500,000,000 → "910 GB".
pub fn human_bytes(mut n: f64) -> String {
    let units = ["B", "KB", "MB", "GB", "TB", "PB"];
    let mut i = 0;
    while n >= 1000.0 && i < units.len() - 1 {
        n /= 1000.0;
        i += 1;
    }
    // {:.1e} gives "9.1e2" for 910; parse it back, and Display prints the plain "910".
    let rounded: f64 = format!("{n:.1e}")
        .parse()
        .expect("a float we just formatted");
    format!("{rounded} {}", units[i])
}

/// Each player's best score, and a Fenwick tree of how many players have each score.
pub struct Leaderboard {
    max_score: u32,
    best: HashMap<String, u32>,
    tree: Vec<i64>,
    pub steps: u32, // the work the last rank() did
}

impl Leaderboard {
    pub fn new(max_score: u32) -> Self {
        Leaderboard {
            max_score,
            best: HashMap::new(),
            tree: vec![0; max_score as usize + 2],
            steps: 0,
        }
    }

    pub fn players(&self) -> usize {
        self.best.len()
    }

    /// Only a player's best counts. A score can't be 2.5 or negative: u32 rules both out.
    pub fn submit(&mut self, player: &str, score: u32) -> Result<bool, String> {
        if score > self.max_score {
            return Err(format!(
                "score must be from 0 to {}, got {score}",
                self.max_score
            ));
        }
        let old = self.best.get(player).copied();
        if old.is_some_and(|old| score <= old) {
            return Ok(false);
        }
        if let Some(old) = old {
            self.add(old, -1);
        }
        self.add(score, 1);
        self.best.insert(player.to_string(), score);
        Ok(true)
    }

    pub fn rank(&mut self, player: &str) -> Option<usize> {
        let score = *self.best.get(player)?;
        self.steps = 0;
        Some(1 + self.players() - self.count_at_most(score) as usize)
    }

    // usize has no negative, so the lowest set bit is i & i.wrapping_neg() rather than i & -i.
    fn add(&mut self, score: u32, delta: i64) {
        let mut i = score as usize + 1;
        while i < self.tree.len() {
            self.tree[i] += delta;
            i += i & i.wrapping_neg();
        }
    }

    fn count_at_most(&mut self, score: u32) -> i64 {
        let (mut count, mut i) = (0, score as usize + 1);
        while i > 0 {
            count += self.tree[i];
            self.steps += 1;
            i -= i & i.wrapping_neg();
        }
        count
    }
}

/// The obvious way: look at every player. Returns (rank, steps).
pub fn rank_by_scan(scores: &[u32], mine: u32) -> (usize, usize) {
    let higher = scores.iter().filter(|&&s| s > mine).count();
    (1 + higher, scores.len())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn game() -> Estimate {
        estimate(&Assumptions {
            daily_active_users: 10_000_000.0,
            writes_per_user_per_day: 5.0,
            reads_per_user_per_day: 10.0,
            peak_to_average: 3.0,
            bytes_per_write: 50.0,
            kept_for_days: 365.0,
            bytes_per_read: 2_000.0,
        })
    }

    #[test]
    fn the_estimate() {
        let g = game();
        let got = [
            g.writes_per_second.average,
            g.writes_per_second.peak,
            g.reads_per_second.peak,
        ]
        .map(f64::round);
        assert_eq!(got, [579.0, 1736.0, 3472.0]);
        assert_eq!(g.reads_per_write, 2.0);
        assert_eq!(human_bytes(g.storage_bytes), "910 GB");
        assert_eq!(human_bytes(g.peak_egress_bytes_per_second), "6.9 MB");
    }

    #[test]
    fn why_the_scan_cannot_work() {
        let peak_reads = game().reads_per_second.peak.round() as u32;
        let players: u32 = 50_000_000;
        assert_eq!(peak_reads.checked_mul(players), None); // too big for u32; plain * would panic in a debug build
        assert_eq!(u64::from(peak_reads) * u64::from(players), 173_600_000_000);
        assert_eq!(human_bytes(f64::from(players) * 100.0), "5 GB");
    }

    #[test]
    fn ranks_ties_and_best_scores() {
        let mut b = Leaderboard::new(1_000);
        for (p, s) in [("ada", 100), ("bo", 250), ("cy", 250), ("di", 90)] {
            b.submit(p, s).unwrap();
        }
        let ranks = |b: &mut Leaderboard, names: [&str; 4]| names.map(|n| b.rank(n).unwrap());
        assert_eq!(ranks(&mut b, ["bo", "cy", "ada", "di"]), [1, 1, 3, 4]);
        assert_eq!(b.submit("ada", 80), Ok(false));
        assert_eq!(b.submit("ada", 300), Ok(true));
        assert_eq!(ranks(&mut b, ["ada", "bo", "cy", "di"]), [1, 2, 2, 4]);
        assert_eq!(b.rank("nobody"), None);
        assert!(b.submit("ed", 1_001).is_err());
    }

    #[test]
    fn about_20_steps_instead_of_one_per_player() {
        let max_score = 1_000_000;
        let mut b = Leaderboard::new(max_score);
        let scores: Vec<u32> = (0..200_000)
            .map(|i| (i * 7_919) % (max_score + 1))
            .collect();
        for (i, &s) in scores.iter().enumerate() {
            b.submit(&format!("p{i}"), s).unwrap();
        }
        for i in [0, 1, 12_345, 199_999] {
            let (rank, steps) = rank_by_scan(&scores, scores[i]);
            assert_eq!(b.rank(&format!("p{i}")), Some(rank));
            assert!(b.steps <= 20, "{} steps", b.steps);
            assert_eq!(steps, 200_000);
        }
    }
}
