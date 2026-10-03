//! Tools for a support assistant: the same checks, round trip and results as the TypeScript lab.
//! Arguments are checked with the `jsonschema` crate; the order store is shared behind a mutex
//! because the MCP server calls tools from async tasks.
use serde_json::{Value, json};
use std::sync::{Arc, Mutex};

pub type Run = Box<dyn Fn(&Value) -> Result<Value, String> + Send + Sync>;

pub struct Tool {
    pub name: &'static str,
    pub description: &'static str,
    pub schema: Value,
    pub side_effects: bool,
    pub run: Run,
}

impl Tool {
    /// What the model sees: never `run` or `side_effects`.
    pub fn spec(&self) -> Value {
        json!({ "name": self.name, "description": self.description, "inputSchema": self.schema })
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct ToolCall {
    pub id: String,
    pub name: String,
    pub arguments: String, // a JSON string, as models send it
}

#[derive(Debug, Clone, PartialEq)]
pub struct ToolResult {
    pub id: String,
    pub content: String,
    pub is_error: bool,
}

/// Every problem, as "arguments/field: message".
pub fn validate(schema: &Value, value: &Value) -> Vec<String> {
    let validator = jsonschema::validator_for(schema).expect("a tool's schema is itself valid");
    validator
        .iter_errors(value)
        .map(|e| format!("arguments{}: {e}", e.instance_path()))
        .collect()
}

pub fn execute(
    call: &ToolCall,
    tools: &[Tool],
    approve: &dyn Fn(&str, &Value) -> bool,
) -> ToolResult {
    let fail = |content: String| ToolResult {
        id: call.id.clone(),
        content,
        is_error: true,
    };
    let Some(tool) = tools.iter().find(|t| t.name == call.name) else {
        let names: Vec<_> = tools.iter().map(|t| t.name).collect();
        return fail(format!(
            "unknown tool \"{}\"; available: {}",
            call.name,
            names.join(", ")
        ));
    };
    let Ok(args) = serde_json::from_str::<Value>(if call.arguments.is_empty() {
        "{}"
    } else {
        &call.arguments
    }) else {
        return fail("arguments are not valid JSON".into());
    };
    let problems = validate(&tool.schema, &args);
    if !problems.is_empty() {
        return fail(problems.join("; "));
    }
    if tool.side_effects && !approve(tool.name, &args) {
        return fail("the user declined this action".into());
    }
    match (tool.run)(&args) {
        Ok(value) => {
            let content = value.to_string();
            let content = if content.len() > 2000 {
                format!("{} …[truncated]", &content[..2000])
            } else {
                content
            };
            ToolResult {
                id: call.id.clone(),
                content,
                is_error: false,
            }
        }
        Err(message) => fail(format!("{} failed: {message}", tool.name)), // the message, never a panic
    }
}

pub type Orders = Arc<Mutex<Value>>;

pub fn load_orders(path: &str) -> Orders {
    let text = std::fs::read_to_string(path).expect("the orders are beside the labs");
    Arc::new(Mutex::new(serde_json::from_str(&text).expect("valid JSON")))
}

pub fn support_tools(orders: &Orders) -> Vec<Tool> {
    let order_id = json!({ "type": "string", "pattern": "^[A-Z][0-9]{3}$", "description": "Like A123: one capital letter, three digits" });
    let one_id = json!({ "type": "object", "properties": { "order_id": order_id }, "required": ["order_id"], "additionalProperties": false });
    let refund_args = json!({ "type": "object", "properties": { "order_id": order_id, "amount": { "type": "number", "minimum": 0.01 } },
        "required": ["order_id", "amount"], "additionalProperties": false });
    // Each tool gets its own handle on the shared store; the lock is held only inside one call.
    let with_order = |orders: Orders, f: fn(&mut Value, &Value) -> Result<Value, String>| -> Run {
        Box::new(move |args| {
            let id = args["order_id"].as_str().unwrap_or_default();
            let mut all = orders.lock().unwrap();
            let order = all.get_mut(id).ok_or(format!("no order {id}"))?;
            f(order, args)
        })
    };
    vec![
        Tool {
            name: "get_order",
            description: "Look up an order's status, total and tracking number. Use it before answering any question about an order.",
            schema: one_id.clone(),
            side_effects: false,
            run: with_order(orders.clone(), |order, _| {
                let mut copy = order.clone();
                copy.as_object_mut().unwrap().remove("refund"); // the refund has its own tool
                Ok(copy)
            }),
        },
        Tool {
            name: "get_refund",
            description: "Look up the refund on an order, if there is one: its status, amount and dates.",
            schema: one_id,
            side_effects: false,
            run: with_order(orders.clone(), |order, _| {
                Ok(if order["refund"].is_null() {
                    json!({ "status": "none" })
                } else {
                    order["refund"].clone()
                })
            }),
        },
        Tool {
            name: "issue_refund",
            description: "Refund money to the customer. Only when the customer asks for a refund and none exists yet.",
            schema: refund_args,
            side_effects: true,
            run: with_order(orders.clone(), |order, args| {
                let (amount, total) = (
                    args["amount"].as_f64().unwrap(),
                    order["total"].as_f64().unwrap(),
                );
                if !order["refund"].is_null() {
                    return Err(format!(
                        "order {} already has a refund",
                        args["order_id"].as_str().unwrap()
                    ));
                }
                if amount > total {
                    return Err(format!(
                        "refund {amount} is more than the order total {total}"
                    ));
                }
                order["refund"] =
                    json!({ "status": "processing", "amount": amount, "requested": "today" });
                Ok(order["refund"].clone())
            }),
        },
    ]
}

#[derive(Debug, Clone, PartialEq)]
pub enum Message {
    User(String),
    Assistant {
        content: String,
        calls: Vec<ToolCall>,
    },
    Tool {
        call_id: String,
        content: String,
    },
}

/// One model turn: text, and zero or more calls. No calls means "this is my answer".
pub type Turn = (String, Vec<ToolCall>);

pub fn answer_with_tools(
    model: &mut dyn FnMut(&[Message], &[Value]) -> Turn,
    messages: Vec<Message>,
    tools: &[Tool],
    approve: &dyn Fn(&str, &Value) -> bool,
    max_rounds: usize,
) -> Result<(String, Vec<Message>, usize), String> {
    let mut history = messages;
    let specs: Vec<Value> = tools.iter().map(Tool::spec).collect();
    for round in 1..=max_rounds {
        let (content, calls) = model(&history, &specs);
        history.push(Message::Assistant {
            content: content.clone(),
            calls: calls.clone(),
        });
        if calls.is_empty() {
            return Ok((content, history, round));
        }
        for call in &calls {
            // one result per call, in the order of the calls
            let r = execute(call, tools, approve);
            let content = if r.is_error {
                format!("ERROR: {}", r.content)
            } else {
                r.content
            };
            history.push(Message::Tool {
                call_id: call.id.clone(),
                content,
            });
        }
    }
    Err(format!("no answer after {max_rounds} rounds of tool calls"))
}

#[cfg(test)]
mod tests {
    use super::*;

    const ORDERS: &str = "../shared/orders.json";

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

    /// A pretend model that plays back a script of turns and records what it was sent.
    fn scripted(
        turns: Vec<Turn>,
        seen: &mut Vec<Vec<Message>>,
    ) -> impl FnMut(&[Message], &[Value]) -> Turn + '_ {
        let mut turns = turns.into_iter();
        move |history, _| {
            seen.push(history.to_vec());
            turns.next().expect("the script ran out")
        }
    }

    #[test]
    fn validation_names_every_problem() {
        let tools = support_tools(&load_orders(ORDERS));
        assert_eq!(
            validate(
                &tools[2].schema,
                &json!({ "order_id": "a-1", "amount": 0, "note": "hi" })
            ),
            [
                "arguments/amount: 0 is less than the minimum of 0.01",
                "arguments/order_id: \"a-1\" does not match \"^[A-Z][0-9]{3}$\"",
                "arguments: Additional properties are not allowed ('note' was unexpected)",
            ]
        );
    }

    #[test]
    fn every_failure_becomes_a_result() {
        let tools = support_tools(&load_orders(ORDERS));
        let ok = execute(
            &call("get_order", r#"{"order_id":"B456"}"#, "c1"),
            &tools,
            &no,
        );
        assert_eq!(
            ok.content,
            r#"{"status":"shipped","total":120.0,"tracking":"LG-88213"}"#
        ); // 120.0, like Python
        let content = |c| execute(&c, &tools, &no).content;
        assert_eq!(
            content(call("delete_order", "{}", "c1")),
            r#"unknown tool "delete_order"; available: get_order, get_refund, issue_refund"#
        );
        assert_eq!(
            content(call("get_order", "{order_id: A123", "c1")),
            "arguments are not valid JSON"
        );
        assert_eq!(
            content(call("get_order", r#"{"order_id":"Z999"}"#, "c1")),
            "get_order failed: no order Z999"
        );
        assert_eq!(
            content(call(
                "issue_refund",
                r#"{"order_id":"B456","amount":120}"#,
                "c1"
            )),
            "the user declined this action"
        );
    }

    #[test]
    fn a_side_effect_needs_valid_arguments_then_approval_then_its_own_rules() {
        let orders = load_orders(ORDERS);
        let tools = support_tools(&orders);
        let asked = Mutex::new(vec![]);
        let yes = |name: &str, args: &Value| {
            asked.lock().unwrap().push(format!("{name} {args}"));
            true
        };
        assert!(
            execute(
                &call("issue_refund", r#"{"order_id":"B456","amount":-5}"#, "c1"),
                &tools,
                &yes
            )
            .is_error
        );
        assert!(asked.lock().unwrap().is_empty()); // nobody approves a malformed call
        assert!(
            !execute(
                &call("issue_refund", r#"{"order_id":"B456","amount":120}"#, "c1"),
                &tools,
                &yes
            )
            .is_error
        );
        assert_eq!(
            *asked.lock().unwrap(),
            [r#"issue_refund {"amount":120,"order_id":"B456"}"#]
        ); // serde_json sorts keys
        let again = execute(
            &call("issue_refund", r#"{"order_id":"B456","amount":120}"#, "c1"),
            &tools,
            &yes,
        );
        assert_eq!(
            again.content,
            "issue_refund failed: order B456 already has a refund"
        );
    }

    #[test]
    fn the_round_trip() {
        let mut seen = vec![];
        let turns = vec![
            (
                String::new(),
                vec![
                    call("get_order", r#"{"order_id":"A123"}"#, "c1"),
                    call("get_refund", r#"{"order_id":"A123"}"#, "c2"),
                ],
            ),
            ("Your refund of 49.99 is being processed.".into(), vec![]),
        ];
        let tools = support_tools(&load_orders(ORDERS));
        let (_, history, rounds) = answer_with_tools(
            &mut scripted(turns, &mut seen),
            vec![Message::User("Where is my refund for A123?".into())],
            &tools,
            &no,
            5,
        )
        .unwrap();
        assert_eq!((rounds, history.len()), (2, 5));
        assert_eq!(
            seen[1][2],
            Message::Tool {
                call_id: "c1".into(),
                content: r#"{"status":"delivered","total":49.99}"#.into()
            }
        );
        assert_eq!(
            seen[1][3],
            Message::Tool {
                call_id: "c2".into(),
                content: r#"{"amount":49.99,"requested":"2026-09-28","status":"processing"}"#
                    .into()
            }
        );
    }

    #[test]
    fn text_in_a_tool_result_cannot_approve_anything() {
        let orders = load_orders(ORDERS);
        let tools = support_tools(&orders);
        let mut seen = vec![];
        let turns = vec![
            (
                String::new(),
                vec![call("get_order", r#"{"order_id":"D012"}"#, "c1")],
            ),
            (
                String::new(),
                vec![call(
                    "issue_refund",
                    r#"{"order_id":"D012","amount":500}"#,
                    "c2",
                )],
            ), // fooled by the note
            ("I can't issue that refund.".into(), vec![]),
        ];
        answer_with_tools(
            &mut scripted(turns, &mut seen),
            vec![Message::User("Check D012".into())],
            &tools,
            &no,
            5,
        )
        .unwrap();
        let Message::Tool { content, .. } = &seen[1][2] else {
            panic!()
        };
        assert!(content.contains("IGNORE ALL PREVIOUS INSTRUCTIONS"));
        assert_eq!(
            seen[2][4],
            Message::Tool {
                call_id: "c2".into(),
                content: "ERROR: the user declined this action".into()
            }
        );
        assert!(orders.lock().unwrap()["D012"]["refund"].is_null());
        let approved = execute(
            &call("issue_refund", r#"{"order_id":"D012","amount":500}"#, "c3"),
            &tools,
            &|_, _| true,
        );
        assert_eq!(
            approved.content,
            "issue_refund failed: refund 500 is more than the order total 30"
        );
    }

    #[test]
    fn a_model_that_never_stops_is_cut_off() {
        let tools = support_tools(&load_orders(ORDERS));
        let mut forever = |_: &[Message], _: &[Value]| {
            (
                String::new(),
                vec![call("get_order", r#"{"order_id":"A123"}"#, "c1")],
            )
        };
        let result = answer_with_tools(
            &mut forever,
            vec![Message::User("?".into())],
            &tools,
            &no,
            3,
        );
        assert_eq!(
            result.unwrap_err(),
            "no answer after 3 rounds of tool calls"
        );
    }
}
