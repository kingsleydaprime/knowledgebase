//! An eval harness: the shared golden set, exact-match scoring, error bars, case-by-case comparison,
//! a CI gate, baselines, and the checks on an LLM judge.

use regex::Regex;
use serde::Deserialize;
use std::collections::{BTreeMap, HashMap, HashSet};
use std::sync::LazyLock;

#[derive(Debug, Deserialize)]
pub struct Case {
    pub id: String,
    pub ticket: String,
    pub label: String,
    pub tags: Vec<String>,
}

pub fn load_golden(path: &str) -> Vec<Case> {
    std::fs::read_to_string(path)
        .expect("the golden set is beside the labs")
        .lines()
        .filter(|line| !line.trim().is_empty())
        .map(|line| serde_json::from_str(line).expect("each line is a case"))
        .collect()
}

static LABEL: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b(bug|billing|feature|other)\b").unwrap());

/// The one label in the reply, or None if there are none or several.
pub fn parse_label(reply: &str) -> Option<String> {
    let lower = reply.to_lowercase();
    let found: HashSet<&str> = LABEL.find_iter(&lower).map(|m| m.as_str()).collect();
    (found.len() == 1).then(|| found.into_iter().next().unwrap().to_string())
}

/// Where the true pass rate probably lies (95%), given a small sample.
pub fn wilson(passed: usize, total: usize) -> (f64, f64) {
    if total == 0 {
        return (0.0, 1.0);
    }
    let (z, n) = (1.96_f64, total as f64);
    let p = passed as f64 / n;
    let centre = p + z * z / (2.0 * n);
    let spread = z * (p * (1.0 - p) / n + z * z / (4.0 * n * n)).sqrt();
    (
        (centre - spread) / (1.0 + z * z / n),
        (centre + spread) / (1.0 + z * z / n),
    )
}

#[derive(Debug)]
pub struct CaseResult {
    pub id: String,
    pub expected: String,
    pub got: Option<String>,
    pub reply: String,
    pub pass: bool,
}

#[derive(Debug, Default)]
pub struct EvalResult {
    pub results: Vec<CaseResult>,
    pub by_tag: BTreeMap<String, (usize, usize)>, // tag -> (passed, total)
}

impl EvalResult {
    pub fn passed(&self) -> usize {
        self.results.iter().filter(|r| r.pass).count()
    }
    pub fn rate(&self) -> f64 {
        self.passed() as f64 / self.results.len() as f64
    }
}

pub fn run_eval(mut classify: impl FnMut(&str) -> String, cases: &[Case]) -> EvalResult {
    let mut result = EvalResult::default();
    for case in cases {
        let reply = classify(&case.ticket);
        let got = parse_label(&reply);
        let pass = got.as_deref() == Some(case.label.as_str());
        for tag in &case.tags {
            let counts = result.by_tag.entry(tag.clone()).or_default();
            counts.0 += usize::from(pass);
            counts.1 += 1;
        }
        result.results.push(CaseResult {
            id: case.id.clone(),
            expected: case.label.clone(),
            got,
            reply,
            pass,
        });
    }
    result
}

/// What a change fixed, and what it broke.
pub fn compare(before: &EvalResult, after: &EvalResult) -> (Vec<String>, Vec<String>) {
    let was: HashMap<&str, bool> = before
        .results
        .iter()
        .map(|r| (r.id.as_str(), r.pass))
        .collect();
    let ids = |want_pass: bool| -> Vec<String> {
        after
            .results
            .iter()
            .filter(|r| r.pass == want_pass && was.get(r.id.as_str()) == Some(&!want_pass))
            .map(|r| r.id.clone())
            .collect()
    };
    (ids(true), ids(false))
}

/// The reasons to fail the build; none means the change may merge.
pub fn gate(
    result: &EvalResult,
    min_rate: f64,
    baseline: Option<&EvalResult>,
    must_pass: &[&str],
) -> Vec<String> {
    let mut reasons = Vec::new();
    if result.rate() < min_rate {
        reasons.push(format!(
            "pass rate {:.0}% is below the floor of {:.0}%",
            result.rate() * 100.0,
            min_rate * 100.0
        ));
    }
    if let Some(base) = baseline {
        let (_, broke) = compare(base, result);
        if !broke.is_empty() {
            reasons.push(format!("regressed on {}", broke.join(", ")));
        }
    }
    for id in must_pass {
        if !result.results.iter().any(|r| r.id == *id && r.pass) {
            reasons.push(format!("must-pass case {id} failed"));
        }
    }
    reasons
}

/// Always the most common label.
pub fn majority(cases: &[Case]) -> impl FnMut(&str) -> String + use<> {
    let mut counts: HashMap<&str, usize> = HashMap::new();
    for case in cases {
        *counts.entry(&case.label).or_default() += 1;
    }
    let top = counts
        .into_iter()
        .max_by_key(|&(label, n)| (n, std::cmp::Reverse(label)))
        .unwrap()
        .0
        .to_string();
    move |_| top.clone()
}

static BILLING: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new("charg|refund|invoice|pay|price|subscription|discount|receipt").unwrap()
});
static BUG: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new("crash|error|broken|bug|blank|empty|doesn't work|not working").unwrap()
});
static FEATURE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new("add|would be great|should support|could you|please support").unwrap()
});

pub fn keywords(ticket: &str) -> String {
    let t = ticket.to_lowercase();
    let label = if BILLING.is_match(&t) {
        "billing"
    } else if BUG.is_match(&t) {
        "bug"
    } else if FEATURE.is_match(&t) {
        "feature"
    } else {
        "other"
    };
    label.to_string()
}

static FIRST: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"(?i)\bfirst\b").unwrap());
static SECOND: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"(?i)\bsecond\b").unwrap());

/// Asks in both orders, so a judge that prefers whatever comes first is caught, not trusted.
pub fn pairwise(
    mut ask: impl FnMut(&str) -> String,
    ticket: &str,
    a: &str,
    b: &str,
) -> &'static str {
    let prompt = |first: &str, second: &str| {
        format!(
            "Which support reply is better for this ticket? Answer only FIRST or SECOND.\n<ticket>\n{ticket}\n\
             </ticket>\n<first>\n{first}\n</first>\n<second>\n{second}\n</second>"
        )
    };
    let pick = |answer: String| {
        if FIRST.is_match(&answer) {
            "first"
        } else if SECOND.is_match(&answer) {
            "second"
        } else {
            ""
        }
    };
    match (pick(ask(&prompt(a, b))), pick(ask(&prompt(b, a)))) {
        ("first", "second") => "a",
        ("second", "first") => "b",
        _ => "inconsistent",
    }
}

/// (agreement, Cohen's kappa). Kappa removes the agreement you'd expect by chance.
pub fn agreement(judge: &[bool], human: &[bool]) -> (f64, f64) {
    let n = judge.len() as f64;
    let share = |xs: &[bool]| xs.iter().filter(|&&x| x).count() as f64 / n;
    let agree = judge.iter().zip(human).filter(|(j, h)| j == h).count() as f64 / n;
    let (j, h) = (share(judge), share(human));
    let chance = j * h + (1.0 - j) * (1.0 - h);
    (
        agree,
        if chance == 1.0 {
            1.0
        } else {
            (agree - chance) / (1.0 - chance)
        },
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    fn golden() -> Vec<Case> {
        load_golden("../shared/golden.jsonl")
    }

    fn round2(x: f64) -> f64 {
        (x * 100.0).round() / 100.0
    }

    fn with_change(part: &'static str, label: &'static str) -> impl FnMut(&str) -> String {
        move |t| {
            if t.contains(part) {
                label.to_string()
            } else {
                keywords(t)
            }
        }
    }

    #[test]
    fn labels_and_error_bars() {
        assert_eq!(parse_label("Category: BUG").as_deref(), Some("bug"));
        assert_eq!(parse_label("bug or billing"), None);
        let (low, high) = wilson(17, 20);
        assert_eq!((round2(low), round2(high)), (0.64, 0.95));
    }

    #[test]
    fn the_baselines_give_the_same_numbers_as_every_other_language() {
        let cases = golden();
        assert_eq!(run_eval(majority(&cases), &cases).passed(), 8);
        let rules = run_eval(keywords, &cases);
        let misses: Vec<String> = rules
            .results
            .iter()
            .filter(|r| !r.pass)
            .map(|r| format!("{}:{}", r.id, r.got.as_deref().unwrap_or("")))
            .collect();
        assert_eq!(rules.passed(), 15);
        assert_eq!(
            misses,
            [
                "t10:other",
                "t12:other",
                "t14:other",
                "t15:feature",
                "t20:billing"
            ]
        );
        assert_eq!(rules.by_tag["other-language"], (0, 2));
    }

    #[test]
    fn compare_and_gate() {
        let cases = golden();
        let base = run_eval(keywords, &cases);
        assert_eq!(
            compare(
                &base,
                &run_eval(with_change("La aplicación", "bug"), &cases)
            ),
            (vec!["t14".into()], vec![])
        );
        let worse = run_eval(with_change("charged twice", "bug"), &cases);
        assert!(gate(&base, 0.6, None, &[]).is_empty());
        assert_eq!(
            gate(&worse, 0.75, Some(&base), &["t02", "t18"]),
            [
                "pass rate 70% is below the floor of 75%",
                "regressed on t02",
                "must-pass case t02 failed"
            ]
        );
    }

    #[test]
    fn pairwise_exposes_position_bias() {
        assert_eq!(
            pairwise(|_| "FIRST".into(), "ticket", "reply A", "reply B"),
            "inconsistent"
        );
        let fair = |p: &str| {
            if p.find("reply B") < p.find("reply A") {
                "FIRST"
            } else {
                "SECOND"
            }
            .to_string()
        };
        assert_eq!(pairwise(fair, "ticket", "reply A", "reply B"), "b");
    }

    #[test]
    fn kappa_catches_a_lenient_judge() {
        let human = [
            true, true, false, false, true, false, true, false, false, true,
        ];
        let lenient = [true, true, true, true, true, true, true, true, false, true];
        let (agree, kappa) = agreement(&lenient, &human);
        assert_eq!((round2(agree), round2(kappa)), (0.6, 0.2));
    }
}
