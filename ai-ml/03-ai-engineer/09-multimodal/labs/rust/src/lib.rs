//! What an uploaded file really is, what an image costs, the three providers' formats, and checked extraction.
//! The same results as the TypeScript lab; reuses the structured-output lab's `invoice::parse`.
use base64::Engine;
use base64::engine::general_purpose::STANDARD as BASE64;
use serde_json::{Value, json};

#[derive(Debug, PartialEq)]
pub struct Info {
    pub kind: &'static str,
    pub width: u32,
    pub height: u32,
}

const PNG_SIGNATURE: &[u8] = b"\x89PNG\r\n\x1a\n";

/// The type from the file's first bytes, never its name or Content-Type. Slice patterns read like the format.
pub fn sniff(b: &[u8]) -> Option<Info> {
    match b {
        _ if b.starts_with(PNG_SIGNATURE) && b.len() >= 24 => {
            let be = |i: usize| u32::from_be_bytes(b[i..i + 4].try_into().unwrap());
            Some(Info {
                kind: "image/png",
                width: be(16),
                height: be(20),
            })
        }
        [0xff, 0xd8, 0xff, ..] => Some(jpeg(b)),
        [b'G', b'I', b'F', b'8', _, _, w0, w1, h0, h1, ..] => Some(Info {
            kind: "image/gif",
            width: u16::from_le_bytes([*w0, *w1]).into(),
            height: u16::from_le_bytes([*h0, *h1]).into(),
        }),
        [
            b'R',
            b'I',
            b'F',
            b'F',
            _,
            _,
            _,
            _,
            b'W',
            b'E',
            b'B',
            b'P',
            ..,
        ] => Some(Info {
            kind: "image/webp",
            width: 0,
            height: 0,
        }),
        _ => None,
    }
}

fn jpeg(b: &[u8]) -> Info {
    let be16 = |i: usize| u32::from(u16::from_be_bytes([b[i], b[i + 1]]));
    let mut i = 2;
    while i + 9 < b.len() && b[i] == 0xff {
        let marker = b[i + 1];
        if (0xc0..=0xcf).contains(&marker) && ![0xc4, 0xc8, 0xcc].contains(&marker) {
            return Info {
                kind: "image/jpeg",
                width: be16(i + 7),
                height: be16(i + 5),
            };
        }
        i += 2 + be16(i + 2) as usize;
    }
    Info {
        kind: "image/jpeg",
        width: 0,
        height: 0,
    }
}

pub struct Limits {
    pub max_long_edge: f64,
    pub max_tokens: f64,
}

pub const HIGH_RES: Limits = Limits {
    max_long_edge: 2576.0,
    max_tokens: 4784.0,
}; // Anthropic, 2026-10: Opus 4.7+, Sonnet 5+
pub const STANDARD: Limits = Limits {
    max_long_edge: 1568.0,
    max_tokens: 1600.0,
}; // earlier models

/// Scaled to the model's limits; tokens ≈ width × height / 750 (Anthropic's documented approximation).
pub fn fit(width: f64, height: f64, l: &Limits) -> (u32, u32, u32) {
    let mut scale = (l.max_long_edge / width.max(height)).min(1.0);
    let tokens = width * scale * (height * scale) / 750.0;
    if tokens > l.max_tokens {
        scale *= (l.max_tokens / tokens).sqrt();
    }
    let (w, h) = ((width * scale).floor(), (height * scale).floor());
    (w as u32, h as u32, (w * h / 750.0).ceil() as u32)
}

pub fn shrink_to(width: f64, height: f64, long_edge: f64) -> (f64, f64) {
    let s = (long_edge / width.max(height)).min(1.0);
    ((width * s).round(), (height * s).round())
}

pub fn image_message(b: &[u8], question: &str, provider: &str) -> Result<Value, String> {
    let info = sniff(b).ok_or("not a supported image")?;
    let data = BASE64.encode(b); // Rust's standard library has no base64: the `base64` crate is the usual choice
    Ok(match provider {
        "anthropic" => json!({ "role": "user", "content": [
            { "type": "image", "source": { "type": "base64", "media_type": info.kind, "data": data } },
            { "type": "text", "text": question } ] }),
        "openai" => json!({ "role": "user", "content": [
            { "type": "text", "text": question },
            { "type": "image_url", "image_url": { "url": format!("data:{};base64,{data}", info.kind) } } ] }),
        _ => json!({ "role": "user", "content": question, "images": [data] }), // Ollama's own /api/chat
    })
}

pub const EXTRACT_PROMPT: &str = "Read this invoice and reply with JSON only, in the invoice schema.\n\
    If you can't read a value, don't guess: reply {\"unreadable\": \"<which field>\"}.";

/// Image in, checked data out. The structured-output lab's `parse` checks shape and arithmetic.
pub fn extract_invoice(
    see: impl Fn(&[u8], &str) -> String,
    b: &[u8],
) -> Result<invoice::Invoice, String> {
    sniff(b).ok_or("not a supported image")?;
    let reply = see(b, EXTRACT_PROMPT);
    let (Some(start), Some(end)) = (reply.find('{'), reply.rfind('}')) else {
        return Err("no JSON in the reply".into());
    };
    if let Ok(Value::Object(probe)) = serde_json::from_str(&reply[start..=end]) {
        if let Some(field) = probe.get("unreadable").and_then(Value::as_str) {
            return Err(format!("unreadable: {field}"));
        }
    }
    invoice::parse(&reply)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Just enough of each format's header to identify it and read its size. (The TypeScript lab builds a whole PNG.)
    fn png_header(w: u32, h: u32) -> Vec<u8> {
        [
            PNG_SIGNATURE,
            &13u32.to_be_bytes(),
            b"IHDR",
            &w.to_be_bytes(),
            &h.to_be_bytes(),
            &[8, 0, 0, 0, 0],
        ]
        .concat()
    }

    fn jpeg_header(w: u16, h: u16) -> Vec<u8> {
        let app0 = [
            0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, b'J', b'F', b'I', b'F', 0, 1, 1, 0, 0, 1, 0, 1, 0,
            0,
        ];
        [
            &app0[..],
            &[0xff, 0xc0, 0x00, 0x11, 0x08],
            &h.to_be_bytes(),
            &w.to_be_bytes(),
            &[3, 1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1],
        ]
        .concat()
    }

    #[test]
    fn the_type_comes_from_the_bytes() {
        assert_eq!(
            sniff(&png_header(1200, 800)),
            Some(Info {
                kind: "image/png",
                width: 1200,
                height: 800
            })
        );
        assert_eq!(
            sniff(&jpeg_header(4000, 3000)),
            Some(Info {
                kind: "image/jpeg",
                width: 4000,
                height: 3000
            })
        );
        assert_eq!(
            sniff(b"GIF89a\x40\x01\xf0\x00"),
            Some(Info {
                kind: "image/gif",
                width: 320,
                height: 240
            })
        );
        assert_eq!(sniff(b"#!/bin/sh\nrm -rf /\n"), None);
        assert_eq!(sniff(b"<svg onload=alert(1)>"), None);
    }

    #[test]
    fn what_a_photo_costs() {
        assert_eq!(fit(4000.0, 3000.0, &HIGH_RES), (2187, 1640, 4783));
        assert_eq!(fit(4000.0, 3000.0, &STANDARD), (1264, 948, 1598));
        let (w, h) = shrink_to(4000.0, 3000.0, 1024.0);
        assert_eq!(fit(w, h, &HIGH_RES), (1024, 768, 1049));
        assert_eq!(fit(1920.0, 1080.0, &HIGH_RES), (1920, 1080, 2765));
    }

    #[test]
    fn three_formats() {
        let png = png_header(4, 4);
        let data = BASE64.encode(&png);
        assert_eq!(
            image_message(&png, "What is this?", "anthropic").unwrap()["content"][0],
            json!({ "type": "image", "source": { "type": "base64", "media_type": "image/png", "data": data } })
        );
        assert_eq!(
            image_message(&png, "What is this?", "openai").unwrap()["content"][1]["image_url"]["url"],
            format!("data:image/png;base64,{data}")
        );
        assert_eq!(
            image_message(&png, "What is this?", "ollama").unwrap(),
            json!({ "role": "user", "content": "What is this?", "images": [data] })
        );
        assert_eq!(
            image_message(b"not an image", "?", "openai"),
            Err("not a supported image".into())
        );
    }

    #[test]
    fn checked_extraction() {
        let good = r#"{"vendor":"Paper Co","invoice_number":"INV-7","currency":"GBP","due_date":"2026-10-15","line_items":[{"description":"A4 paper","amount_cents":1250},{"description":"Pens","amount_cents":480}],"total_cents":1730}"#;
        let png = png_header(8, 8);
        let reply = |text: &str| {
            let text = format!("Here you go: {text}");
            move |_: &[u8], _: &str| text.clone()
        };
        assert_eq!(
            extract_invoice(reply(good), &png).unwrap().total_cents,
            1730
        );
        let misread = good.replace(r#""total_cents":1730"#, r#""total_cents":1780"#);
        assert_eq!(
            extract_invoice(reply(&misread), &png).unwrap_err(),
            "line items add up to 1730 cents but total_cents is 1780"
        );
        assert_eq!(
            extract_invoice(reply(r#"{"unreadable": "due_date"}"#), &png).unwrap_err(),
            "unreadable: due_date"
        );
        assert_eq!(
            extract_invoice(|_, _| "I can't see an invoice.".into(), &png).unwrap_err(),
            "no JSON in the reply"
        );
        assert_eq!(
            extract_invoice(reply(good), b"%PDF-1.7").unwrap_err(),
            "not a supported image"
        );
    }
}
