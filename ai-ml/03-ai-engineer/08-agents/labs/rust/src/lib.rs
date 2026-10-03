//! The agent loop with its controls, the same question as a workflow, and a trajectory scorer.
//! Uses the tools lab (`support_tools`) and the evals lab (`evals::keywords`).
use regex::Regex;
use serde_json::{Value, json};
use std::collections::{HashMap, HashSet};
use std::sync::LazyLock;
use support_tools::{Message, Tool, ToolCall, ToolResult, execute};

pub struct Limits {
    pub max_steps: usize,
    pub max_tokens: u32,
    pub max_repeats: u32,
}

pub const DEFAULT_LIMITS: Limits = Limits {
    max_steps: 8,
    max_tokens: 50_000,
    max_repeats: 2,
};

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Status {
    Answered,
    StepLimit,
    TokenLimit,
    Stuck,
}

#[derive(Debug)]
pub struct Step {
    pub tokens: u32,
    pub calls: Vec<(String, String, bool)>, // name, arguments, is_error
}

#[derive(Debug)]
pub struct Outcome {
    pub status: Status,
    pub answer: Option<String>,
    pub trace: Vec<Step>,
    pub messages: Vec<Message>,
}

/// One model turn: text, the calls it asks for, and the tokens it used.
pub type Turn = (String, Vec<ToolCall>, u32);

/// `approve` must be `Sync`: read-only calls run on several threads at once, and each may need it.
pub fn run_agent(
    model: &mut dyn FnMut(&[Message]) -> Turn,
    messages: Vec<Message>,
    tools: &[Tool],
    limits: &Limits,
    approve: &(dyn Fn(&str, &Value) -> bool + Sync),
) -> Outcome {
    let (mut history, mut trace, mut seen, mut total) = (messages, Vec::new(), HashMap::new(), 0);
    let side_effects: HashSet<&str> = tools
        .iter()
        .filter(|t| t.side_effects)
        .map(|t| t.name)
        .collect();
    for _ in 0..limits.max_steps {
        let (text, calls, used) = model(&history);
        total += used;
        history.push(Message::Assistant {
            content: text.clone(),
            calls: calls.clone(),
        });
        trace.push(Step {
            tokens: used,
            calls: vec![],
        });
        if calls.is_empty() {
            return Outcome {
                status: Status::Answered,
                answer: Some(text),
                trace,
                messages: history,
            };
        }
        for call in &calls {
            // the same call, again and again, is going round in circles
            let count = seen
                .entry(format!("{} {}", call.name, call.arguments))
                .or_insert(0);
            *count += 1;
            if *count > limits.max_repeats {
                return Outcome {
                    status: Status::Stuck,
                    answer: None,
                    trace,
                    messages: history,
                };
            }
        }

        // Read-only calls on scoped threads, which may borrow `tools` because they're joined before the
        // scope ends; side effects alone, in order, after them.
        let mut results: HashMap<&str, ToolResult> = std::thread::scope(|scope| {
            let reads: Vec<_> = calls
                .iter()
                .filter(|c| !side_effects.contains(c.name.as_str()))
                .map(|c| {
                    (
                        c.id.as_str(),
                        scope.spawn(move || execute(c, tools, approve)),
                    )
                })
                .collect();
            reads
                .into_iter()
                .map(|(id, handle)| (id, handle.join().expect("a tool thread panicked")))
                .collect()
        });
        for c in calls
            .iter()
            .filter(|c| side_effects.contains(c.name.as_str()))
        {
            results.insert(c.id.as_str(), execute(c, tools, approve));
        }

        for call in &calls {
            // results in the order of the calls, whatever order they finished in
            let r = results
                .remove(call.id.as_str())
                .expect("every call has a result");
            let content = if r.is_error {
                format!("ERROR: {}", r.content)
            } else {
                r.content
            };
            history.push(Message::Tool {
                call_id: call.id.clone(),
                content,
            });
            trace.last_mut().unwrap().calls.push((
                call.name.clone(),
                call.arguments.clone(),
                r.is_error,
            ));
        }
        if total > limits.max_tokens {
            return Outcome {
                status: Status::TokenLimit,
                answer: None,
                trace,
                messages: history,
            };
        }
    }
    Outcome {
        status: Status::StepLimit,
        answer: None,
        trace,
        messages: history,
    }
}

#[derive(Debug, PartialEq)]
pub enum Workflow {
    Answer { text: String, model_calls: u32 },
    Ask(String),
    Handoff(String),
}

static ORDER_ID: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\b([A-Za-z])(\d{3})\b").unwrap());

/// The same question as fixed steps: route, extract, look up, then one model call with no tools.
pub fn refund_status(
    question: &str,
    tools: &[Tool],
    write: &mut dyn FnMut(&str) -> String,
) -> Workflow {
    let label = evals::keywords(question);
    if label != "billing" {
        return Workflow::Handoff(format!("classified as {label}"));
    }
    let Some(m) = ORDER_ID.captures(question) else {
        return Workflow::Ask("Could you tell me your order number? It looks like A123.".into());
    };
    let id = format!("{}{}", m[1].to_uppercase(), &m[2]);
    let args = json!({ "order_id": id }).to_string();
    let refund = execute(
        &ToolCall {
            id: "w1".into(),
            name: "get_refund".into(),
            arguments: args,
        },
        tools,
        &|_, _| false,
    );
    if refund.is_error {
        return Workflow::Ask(format!(
            "I couldn't find order {id}. Could you check the number?"
        ));
    }
    let text = write(&format!(
        "Write a one-sentence reply to a customer about their refund, using only these facts.\nOrder: {id}\nRefund: {}\nTheir question: {question}",
        refund.content
    ));
    Workflow::Answer {
        text,
        model_calls: 1,
    }
}

#[derive(Default)]
pub struct Expect<'a> {
    pub status: Option<Status>,
    pub must_call: &'a [&'a str],
    pub must_not_call: &'a [&'a str],
    pub max_steps: Option<usize>,
    pub answer_matches: Option<Regex>,
}

pub fn score_trajectory(o: &Outcome, e: &Expect) -> Vec<String> {
    let called: Vec<&str> = o
        .trace
        .iter()
        .flat_map(|s| s.calls.iter().map(|c| c.0.as_str()))
        .collect();
    let mut failures = vec![];
    if let Some(status) = e.status.filter(|s| *s != o.status) {
        failures.push(format!("ended {:?}, expected {status:?}", o.status));
    }
    failures.extend(
        e.must_call
            .iter()
            .filter(|n| !called.contains(n))
            .map(|n| format!("never called {n}")),
    );
    failures.extend(
        e.must_not_call
            .iter()
            .filter(|n| called.contains(n))
            .map(|n| format!("called {n}")),
    );
    if let Some(max) = e.max_steps.filter(|m| o.trace.len() > *m) {
        failures.push(format!(
            "took {} steps, expected at most {max}",
            o.trace.len()
        ));
    }
    if let Some(re) = e
        .answer_matches
        .as_ref()
        .filter(|re| !re.is_match(o.answer.as_deref().unwrap_or("")))
    {
        failures.push(format!("answer doesn't match {re}"));
    }
    failures
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Mutex;
    use std::time::Duration;
    use support_tools::{load_orders, support_tools};

    fn load() -> Vec<Tool> {
        support_tools(&load_orders(
            "../../../07-tools-and-mcp/labs/shared/orders.json",
        ))
    }
    fn call(name: &str, args: &str, id: &str) -> ToolCall {
        ToolCall {
            id: id.into(),
            name: name.into(),
            arguments: args.into(),
        }
    }
    fn no(_: &str, _: &Value) -> bool {
        false
    }
    fn scripted(turns: Vec<Turn>) -> impl FnMut(&[Message]) -> Turn {
        let mut turns = turns.into_iter();
        move |_| turns.next().expect("the script ran out")
    }
    fn ask() -> Vec<Message> {
        vec![Message::User("Where is my refund for A123?".into())]
    }
    fn names(o: &Outcome) -> Vec<Vec<&str>> {
        o.trace
            .iter()
            .map(|s| s.calls.iter().map(|c| c.0.as_str()).collect())
            .collect()
    }

    #[test]
    fn a_two_step_answer_with_a_trace() {
        let mut model = scripted(vec![
            (
                String::new(),
                vec![
                    call("get_order", r#"{"order_id":"A123"}"#, "c1"),
                    call("get_refund", r#"{"order_id":"A123"}"#, "c2"),
                ],
                0,
            ),
            ("Your refund of 49.99 is being processed.".into(), vec![], 0),
        ]);
        let o = run_agent(&mut model, ask(), &load(), &DEFAULT_LIMITS, &no);
        assert_eq!(
            (o.status, names(&o)),
            (
                Status::Answered,
                vec![vec!["get_order", "get_refund"], vec![]]
            )
        );
        let expect = Expect {
            status: Some(Status::Answered),
            must_call: &["get_refund"],
            must_not_call: &["issue_refund"],
            max_steps: Some(3),
            ..Default::default()
        };
        assert!(score_trajectory(&o, &expect).is_empty());
    }

    #[test]
    fn reads_run_together_and_a_side_effect_waits() {
        let log = std::sync::Arc::new(Mutex::new(vec![]));
        let slow = |name: &'static str, side_effects: bool, ms: u64| {
            let log = log.clone();
            Tool {
                name,
                description: "",
                schema: json!({ "type": "object" }),
                side_effects,
                run: Box::new(move |_| {
                    log.lock().unwrap().push(format!("start {name}"));
                    std::thread::sleep(Duration::from_millis(ms));
                    log.lock().unwrap().push(format!("end {name}"));
                    Ok(json!(name))
                }),
            }
        };
        let tools = [
            slow("read_a", false, 30),
            slow("read_b", false, 10),
            slow("write_c", true, 1),
        ];
        let mut model = scripted(vec![
            (
                String::new(),
                vec![
                    call("write_c", "{}", "1"),
                    call("read_a", "{}", "2"),
                    call("read_b", "{}", "3"),
                ],
                0,
            ),
            ("done".into(), vec![], 0),
        ]);
        let o = run_agent(&mut model, vec![], &tools, &DEFAULT_LIMITS, &|_, _| true);
        let log = log.lock().unwrap();
        let ends: Vec<_> = log.iter().filter(|s| s.starts_with("end")).collect();
        assert_eq!(ends, ["end read_b", "end read_a", "end write_c"]);
        assert_eq!(log[4], "start write_c");
        let ids: Vec<_> = o
            .messages
            .iter()
            .filter_map(|m| {
                if let Message::Tool { call_id, .. } = m {
                    Some(call_id.as_str())
                } else {
                    None
                }
            })
            .collect();
        assert_eq!(ids, ["1", "2", "3"]);
    }

    #[test]
    fn a_step_limit_stops_a_wandering_agent() {
        let mut n = 100;
        let mut wandering = |_: &[Message]| {
            n += 1;
            (
                String::new(),
                vec![call(
                    "get_order",
                    &format!(r#"{{"order_id":"A{n}"}}"#),
                    &n.to_string(),
                )],
                0,
            )
        };
        let o = run_agent(
            &mut wandering,
            ask(),
            &load(),
            &Limits {
                max_steps: 3,
                max_tokens: u32::MAX,
                max_repeats: 5,
            },
            &no,
        );
        assert_eq!((o.status, o.trace.len()), (Status::StepLimit, 3));
        let expect = Expect {
            status: Some(Status::Answered),
            ..Default::default()
        };
        assert_eq!(
            score_trajectory(&o, &expect),
            ["ended StepLimit, expected Answered"]
        );
    }

    #[test]
    fn the_same_call_again_and_again_is_stuck() {
        let mut repeating = |_: &[Message]| {
            (
                String::new(),
                vec![call("get_refund", r#"{"order_id":"Z999"}"#, "x")],
                0,
            )
        };
        let o = run_agent(
            &mut repeating,
            ask(),
            &load(),
            &Limits {
                max_steps: 20,
                max_tokens: u32::MAX,
                max_repeats: 2,
            },
            &no,
        );
        assert_eq!((o.status, o.trace.len()), (Status::Stuck, 3));
    }

    #[test]
    fn a_token_budget() {
        let mut model = scripted(vec![
            (
                String::new(),
                vec![call("get_order", r#"{"order_id":"A123"}"#, "c1")],
                25_500,
            ),
            (
                String::new(),
                vec![call("get_order", r#"{"order_id":"B456"}"#, "c2")],
                25_500,
            ),
            ("never reached".into(), vec![], 25_500),
        ]);
        let o = run_agent(
            &mut model,
            ask(),
            &load(),
            &Limits {
                max_steps: 10,
                max_tokens: 50_000,
                max_repeats: 2,
            },
            &no,
        );
        assert_eq!(
            (
                o.status,
                o.trace.iter().map(|s| s.tokens).collect::<Vec<_>>()
            ),
            (Status::TokenLimit, vec![25_500, 25_500])
        );
    }

    #[test]
    fn the_scorer_names_each_broken_expectation() {
        let mut model = scripted(vec![
            (
                String::new(),
                vec![call(
                    "issue_refund",
                    r#"{"order_id":"B456","amount":120}"#,
                    "c1",
                )],
                0,
            ),
            ("I've asked for a refund.".into(), vec![], 0),
        ]);
        let o = run_agent(&mut model, ask(), &load(), &DEFAULT_LIMITS, &no);
        let expect = Expect {
            must_call: &["get_refund"],
            must_not_call: &["issue_refund"],
            answer_matches: Some(Regex::new("(?i)no refund").unwrap()),
            ..Default::default()
        };
        assert_eq!(
            score_trajectory(&o, &expect),
            [
                "never called get_refund",
                "called issue_refund",
                "answer doesn't match (?i)no refund"
            ]
        );
    }

    #[test]
    fn the_workflow() {
        let tools = load();
        let mut prompts = vec![];
        let mut write = |p: &str| {
            prompts.push(p.to_string());
            "Your refund of 49.99 for A123 is being processed.".to_string()
        };
        assert_eq!(
            refund_status("Where is my refund for order a123?", &tools, &mut write),
            Workflow::Answer {
                text: "Your refund of 49.99 for A123 is being processed.".into(),
                model_calls: 1
            }
        );
        assert!(matches!(
            refund_status("Has my refund come through?", &tools, &mut write),
            Workflow::Ask(_)
        ));
        // "address" contains "add": the keyword rules' known flaw, harmless when every other branch goes to a person
        assert_eq!(
            refund_status("Can you change my delivery address?", &tools, &mut write),
            Workflow::Handoff("classified as feature".into())
        );
        refund_status("Where is my refund for D012?", &tools, &mut write);
        assert!(prompts[0].contains(
            r#"Refund: {"amount":49.99,"requested":"2026-09-28","status":"processing"}"#
        )); // serde_json sorts keys
        assert!(!prompts[1].contains("IGNORE") && prompts.len() == 2);
    }
}
