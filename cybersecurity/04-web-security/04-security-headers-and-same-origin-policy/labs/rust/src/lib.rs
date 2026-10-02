//! The header policy as plain functions, so it's testable without a server. In Axum, the same
//! policy is tower-http layers: `CorsLayer::new().allow_origin(...)` and
//! `SetResponseHeaderLayer::overriding(...)` for each security header.
pub const SECURITY_HEADERS: [(&str, &str); 4] = [
    (
        "content-security-policy",
        "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
    ),
    ("x-content-type-options", "nosniff"),
    ("referrer-policy", "strict-origin-when-cross-origin"),
    (
        "strict-transport-security",
        "max-age=31536000; includeSubDomains",
    ),
];

const ALLOWED_ORIGINS: [&str; 1] = ["https://app.example.com"];

/// Every response gets the security headers; CORS headers only for an allowlisted origin.
pub fn response_headers(origin: Option<&str>) -> Vec<(&'static str, String)> {
    let mut headers: Vec<(&'static str, String)> = SECURITY_HEADERS
        .iter()
        .map(|&(k, v)| (k, v.to_string()))
        .collect();
    headers.push(("vary", "Origin".into()));
    if let Some(origin) = origin.filter(|o| ALLOWED_ORIGINS.contains(o)) {
        headers.push(("access-control-allow-origin", origin.into()));
        headers.push(("access-control-allow-credentials", "true".into()));
    }
    headers
}

#[cfg(test)]
mod tests {
    use super::*;

    fn get<'a>(headers: &'a [(&str, String)], name: &str) -> Option<&'a str> {
        headers
            .iter()
            .find(|(k, _)| *k == name)
            .map(|(_, v)| v.as_str())
    }

    #[test]
    fn security_headers_always() {
        let h = response_headers(None);
        assert_eq!(get(&h, "x-content-type-options"), Some("nosniff"));
        assert!(
            get(&h, "content-security-policy")
                .unwrap()
                .contains("frame-ancestors 'none'")
        );
    }

    #[test]
    fn cors_only_for_the_allowlist() {
        let ours = response_headers(Some("https://app.example.com"));
        assert_eq!(
            get(&ours, "access-control-allow-origin"),
            Some("https://app.example.com")
        );
        let evil = response_headers(Some("https://evil.example"));
        assert_eq!(get(&evil, "access-control-allow-origin"), None);
    }
}
