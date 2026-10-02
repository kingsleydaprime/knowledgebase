//! Structured output with serde and schemars: one struct is the type, the parsing target and the
//! schema sent to the model. Serde is strict by default: wrong types and missing fields are errors.

use chrono::NaiveDate;
use schemars::{JsonSchema, schema_for};
use serde::{Deserialize, Serialize};

#[derive(Debug, PartialEq, Serialize, Deserialize, JsonSchema)]
pub enum Currency {
    GBP,
    USD,
    EUR,
    NGN,
}

#[derive(Debug, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)] // → "additionalProperties": false, and an error on extra keys
pub struct LineItem {
    pub description: String,
    pub amount_cents: i64,
}

#[derive(Debug, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct Invoice {
    pub vendor: String,
    pub invoice_number: String,
    pub currency: Currency,
    /// ISO 8601 date, YYYY-MM-DD
    pub due_date: NaiveDate,
    pub line_items: Vec<LineItem>,
    pub total_cents: i64,
}

/// The schema for the model, generated from the struct. Doc comments become descriptions.
pub fn schema() -> serde_json::Value {
    serde_json::to_value(schema_for!(Invoice)).expect("a schema is always valid JSON")
}

/// JSON, then shape, then the invariant. The error is a message a model can act on.
pub fn parse(reply: &str) -> Result<Invoice, String> {
    let (Some(start), Some(end)) = (reply.find('{'), reply.rfind('}')) else {
        return Err("no JSON object in the reply".into());
    };
    if end < start {
        return Err("no JSON object in the reply".into());
    }
    // serde_json's messages name the problem and where: "invalid type: floating point `655.5`,
    // expected i64 at line 1 column 25"
    let invoice: Invoice = serde_json::from_str(&reply[start..=end]).map_err(|e| e.to_string())?;
    let sum: i64 = invoice
        .line_items
        .iter()
        .map(|item| item.amount_cents)
        .sum();
    if sum != invoice.total_cents {
        return Err(format!(
            "line items add up to {sum} cents but total_cents is {}",
            invoice.total_cents
        ));
    }
    Ok(invoice)
}

#[derive(Clone, Debug)]
pub struct Message {
    pub role: &'static str,
    pub content: String,
}

pub struct Reply {
    pub text: String,
    pub finish_reason: &'static str, // "stop", "length" or "other"
    pub refusal: Option<String>,
}

#[derive(Debug, PartialEq)]
pub enum Outcome {
    Ok { invoice: Invoice, attempts: u32 },
    Refused { detail: String, attempts: u32 },
    Invalid { detail: String, attempts: u32 },
}

pub fn extract(
    mut model: impl FnMut(&[Message]) -> Reply,
    document: &str,
    max_attempts: u32,
) -> Outcome {
    let mut messages = vec![
        Message {
            role: "system",
            content: format!(
                "Extract the invoice as JSON matching this schema. Amounts are integers in cents. \
                 Reply with only the JSON object.\n{}",
                schema()
            ),
        },
        Message {
            role: "user",
            content: document.into(),
        },
    ];
    let mut problem = String::new();
    for attempt in 1..=max_attempts {
        let reply = model(&messages);
        if let Some(detail) = reply.refusal {
            return Outcome::Refused {
                detail,
                attempts: attempt,
            }; // retrying won't change a refusal
        }
        if reply.finish_reason == "length" {
            problem = "your reply was cut off before the JSON was complete; reply with a shorter, complete object".into();
        } else {
            match parse(&reply.text) {
                Ok(invoice) => {
                    return Outcome::Ok {
                        invoice,
                        attempts: attempt,
                    };
                }
                Err(e) => problem = e,
            }
        }
        messages.push(Message {
            role: "assistant",
            content: reply.text,
        });
        messages.push(Message {
            role: "user",
            content: format!(
                "Your reply had these problems: {problem}. Return the corrected JSON object only."
            ),
        });
    }
    Outcome::Invalid {
        detail: problem,
        attempts: max_attempts,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::{Value, json};

    fn good() -> Value {
        json!({"vendor": "Brightline Studio Ltd", "invoice_number": "INV-2041", "currency": "GBP",
               "due_date": "2026-10-15",
               "line_items": [{"description": "Logo design", "amount_cents": 45000},
                              {"description": "Two revisions", "amount_cents": 12000},
                              {"description": "Brand guide PDF", "amount_cents": 8550}],
               "total_cents": 65550})
    }

    /// The good invoice with one field changed, added (Some) or removed (None).
    fn with(field: &str, value: Option<Value>) -> String {
        let mut invoice = good();
        match value {
            Some(v) => invoice[field] = v,
            None => {
                invoice.as_object_mut().unwrap().remove(field);
            }
        }
        invoice.to_string()
    }

    fn reply(text: impl Into<String>) -> Reply {
        Reply {
            text: text.into(),
            finish_reason: "stop",
            refusal: None,
        }
    }

    #[test]
    fn one_struct_gives_the_schema_for_the_model() {
        let schema = schema();
        assert_eq!(schema["additionalProperties"], json!(false));
        assert_eq!(schema["required"].as_array().unwrap().len(), 6);
        assert_eq!(schema["properties"]["due_date"]["format"], "date");
        assert_eq!(
            schema["properties"]["due_date"]["description"],
            "ISO 8601 date, YYYY-MM-DD"
        );
    }

    #[test]
    fn and_the_typed_value_for_your_code() {
        let invoice = parse(&format!("Sure! Here it is:\n```json\n{}\n```", good())).unwrap();
        assert_eq!(
            invoice.due_date,
            NaiveDate::from_ymd_opt(2026, 10, 15).unwrap()
        );
        assert_eq!(
            (invoice.currency, invoice.line_items[2].amount_cents),
            (Currency::GBP, 8550)
        );
    }

    #[test]
    fn strict_by_default() {
        let problem = |text: String| parse(&text).unwrap_err();
        assert!(
            problem(with("total_cents", Some(json!(655.5))))
                .starts_with("invalid type: floating point `655.5`, expected i64")
        );
        assert!(
            problem(with("vendor", Some(json!(1))))
                .starts_with("invalid type: integer `1`, expected a string")
        );
        assert!(
            problem(with("invoice_number", None)).starts_with("missing field `invoice_number`")
        );
        assert!(problem(with("notes", Some(json!("thanks")))).starts_with("unknown field `notes`"));
        assert!(
            problem(with("currency", Some(json!("pounds")))).starts_with(
                "unknown variant `pounds`, expected one of `GBP`, `USD`, `EUR`, `NGN`"
            )
        );
        assert!(
            problem(with("due_date", Some(json!("15 October 2026"))))
                .starts_with("input contains invalid characters")
        );
        assert_eq!(
            problem(with("total_cents", Some(json!(65500)))),
            "line items add up to 65550 cents but total_cents is 65500"
        );
        assert_eq!(
            problem("I can't find an invoice.".into()),
            "no JSON object in the reply"
        );
    }

    #[test]
    fn the_retry_loop() {
        let mut seen = Vec::new();
        let mut replies = vec![
            reply(with("total_cents", Some(json!(65500)))),
            reply(good().to_string()),
        ]
        .into_iter();
        let outcome = extract(
            |m: &[Message]| {
                seen.push(m.to_vec());
                replies.next().unwrap()
            },
            "…",
            3,
        );
        assert!(matches!(outcome, Outcome::Ok { attempts: 2, .. }));
        assert!(
            seen[1]
                .last()
                .unwrap()
                .content
                .contains("total_cents is 65500")
        );

        let mut seen = Vec::new();
        let mut replies = vec![
            Reply {
                text: r#"{"vendor": "Bright"#.into(),
                finish_reason: "length",
                refusal: None,
            },
            reply(good().to_string()),
        ]
        .into_iter();
        let outcome = extract(
            |m: &[Message]| {
                seen.push(m.to_vec());
                replies.next().unwrap()
            },
            "…",
            3,
        );
        assert!(
            matches!(outcome, Outcome::Ok { .. })
                && seen[1].last().unwrap().content.contains("cut off")
        );

        let mut calls = 0;
        let outcome = extract(
            |_: &[Message]| {
                calls += 1;
                Reply {
                    text: String::new(),
                    finish_reason: "stop",
                    refusal: Some("I can't help with that.".into()),
                }
            },
            "…",
            3,
        );
        assert_eq!(
            (outcome, calls),
            (
                Outcome::Refused {
                    detail: "I can't help with that.".into(),
                    attempts: 1
                },
                1
            )
        );

        let mut replies = vec![
            reply("nope"),
            reply("still no"),
            reply(with("vendor", Some(json!(1)))),
        ]
        .into_iter();
        let outcome = extract(|_: &[Message]| replies.next().unwrap(), "…", 3);
        assert!(
            matches!(&outcome, Outcome::Invalid { attempts: 3, detail } if detail.starts_with("invalid type: integer `1`"))
        );
    }
}
