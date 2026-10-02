# Security Headers in Other Languages

> **[Beginner→Intermediate]** · A companion to [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|security headers and the same-origin policy]], which sets the headers and a CORS allowlist on a Node server. The headers are HTTP, so they're identical everywhere. What differs is **where each framework wants you to set them** — and in several, most are set for you.

## Before you start

You can already:

- Explain the same-origin policy, the CORS allowlist and its reflected-origin misconfiguration, CSP, and the cookie flags → [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|the main lesson]].
- Read code in at least one language below.

After this lesson you will be able to:

1. Set the security headers and a CORS allowlist in your framework, in the place it expects.
2. Say which of them your framework already sets by default.
3. Test the policy without a browser.

## The kid version

Every house on a street needs a lock, but some builders fit one as standard and with others you buy your own. The lock is the same kind of lock either way. **Knowing which builder you have tells you whether you still need to fit one.**

**Where the analogy stops working.** A lock fitted as standard is still yours to check — a framework's default headers are a starting point, and a CORS allowlist is never a default: only you know which origins are yours.

## 1. Where each framework puts them

| Framework | Security headers | CORS | Default? |
|---|---|---|---|
| Express | `helmet()` | `cors({ origin: [...] })` | no — add helmet |
| Django | `SecurityMiddleware` + settings (`SECURE_HSTS_SECONDS`, `SECURE_CONTENT_TYPE_NOSNIFF`) | `django-cors-headers` | partly — `nosniff` and `X-Frame-Options` on by default |
| FastAPI / Starlette | a middleware, or `secure` | `CORSMiddleware` | no |
| Flask | Flask-Talisman | Flask-CORS | no |
| Go `net/http` | your own middleware | your own, or `rs/cors` | no |
| Spring Boot | **Spring Security's `headers()`** | a `CorsConfigurationSource` bean | **yes** — Spring Security sets most headers by default |
| Rust — Axum | `tower-http` `SetResponseHeaderLayer` | `tower-http` `CorsLayer` | no |
| ASP.NET Core | middleware, plus `UseHsts()` | **`AddCors` + `UseCors`** | HSTS via `UseHsts` in production templates |
| C, C++ | — | — | rarely the language of a web API; frameworks such as Drogon expose response headers directly |

**CORS is never a default anywhere** — only you know which origins are your frontends. And every framework's CORS support has the same footgun the main lesson showed: an "allow any origin" option that, combined with credentials, hands your API to every website.

## Terms used in this lesson

1. **Middleware**: This is code that runs around every request — the natural place to add response headers once instead of in every handler.
2. **WSGI (web server gateway interface)**: The letters stand for those four words. It is Python's standard interface between web servers and apps; Django and Flask are WSGI apps.
3. **`Vary: Origin`**: This is a response header telling caches that the response depends on the request's `Origin`, so one origin's answer isn't served to another.

## 2. Python

Underneath Django and Flask is **WSGI**: an app is a function taking a request dictionary and a `start_response` callback. Middleware wraps that function — the lab does it by hand, which is what Django's middleware stack and Flask-Talisman do for you. Testing a WSGI app needs no server: call it.

```python
"""app.py — a WSGI app (what Flask and Django are underneath) wrapped in security middleware."""
import json

SECURITY_HEADERS = [
    ("Content-Security-Policy", "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"),
    ("X-Content-Type-Options", "nosniff"),
    ("Referrer-Policy", "strict-origin-when-cross-origin"),
    ("Strict-Transport-Security", "max-age=31536000; includeSubDomains"),
]
ALLOWED_ORIGINS = {"https://app.example.com"}


def api(environ, start_response):
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps({"email": "ada@x.com"}).encode()]


def security_middleware(app):
    """Adds the headers to every response, and CORS headers only for allowlisted origins."""
    def wrapped(environ, start_response):
        origin = environ.get("HTTP_ORIGIN")

        def start(status, headers, exc_info=None):
            headers = headers + SECURITY_HEADERS + [("Vary", "Origin")]
            if origin in ALLOWED_ORIGINS:
                headers += [("Access-Control-Allow-Origin", origin), ("Access-Control-Allow-Credentials", "true")]
            return start_response(status, headers, exc_info)

        return app(environ, start)
    return wrapped


application = security_middleware(api)
```

**Lab:** `labs/security-headers/javascript/python/` — checked with Python 3.14, standard library only.

## 3. Go

A middleware wraps `http.Handler` and sets headers before calling the next one — the [[concepts/03-design-patterns/02b-structural-patterns-in-other-languages|decorator shape]] from structural patterns. `httptest.NewRecorder` tests it with no network.

```go
// Package headers: security headers and a CORS allowlist as net/http middleware.
package headers

import (
	"encoding/json"
	"net/http"
	"slices"
)

var allowedOrigins = []string{"https://app.example.com"}

func Secure(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		h := w.Header()
		h.Set("Content-Security-Policy", "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
		h.Set("X-Content-Type-Options", "nosniff")
		h.Set("Referrer-Policy", "strict-origin-when-cross-origin")
		h.Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
		h.Add("Vary", "Origin")
		if origin := r.Header.Get("Origin"); slices.Contains(allowedOrigins, origin) {
			h.Set("Access-Control-Allow-Origin", origin)
			h.Set("Access-Control-Allow-Credentials", "true")
		}
		next.ServeHTTP(w, r)
	})
}

func Me(w http.ResponseWriter, _ *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"email": "ada@x.com"})
}
```

**Lab:** `labs/security-headers/javascript/go/` — checked with Go 1.26.

## 4. Java

The lab uses the JDK's built-in HTTP server and a `Filter`. In **Spring Boot**, add Spring Security and most headers are on by default (`X-Content-Type-Options`, `X-Frame-Options`, cache control, HSTS over HTTPS); you add a CSP with `http.headers(h -> h.contentSecurityPolicy(...))` and CORS with a `CorsConfigurationSource` bean.

```java
package headers;

import com.sun.net.httpserver.Filter;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Set;

// The JDK's built-in HTTP server with a Filter adding headers. In Spring, Spring Security's
// http.headers(...) sets these by default, and a CorsConfigurationSource holds the allowlist.
public final class Server {
    static final Set<String> ALLOWED = Set.of("https://app.example.com");

    static final class SecurityHeaders extends Filter {
        @Override public void doFilter(HttpExchange ex, Chain chain) throws IOException {
            var h = ex.getResponseHeaders();
            h.set("Content-Security-Policy", "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'");
            h.set("X-Content-Type-Options", "nosniff");
            h.set("Referrer-Policy", "strict-origin-when-cross-origin");
            h.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
            h.add("Vary", "Origin");
            String origin = ex.getRequestHeaders().getFirst("Origin");
            if (origin != null && ALLOWED.contains(origin)) {
                h.set("Access-Control-Allow-Origin", origin);
                h.set("Access-Control-Allow-Credentials", "true");
            }
            chain.doFilter(ex);
        }
        @Override public String description() { return "security headers and CORS"; }
    }

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        var context = server.createContext("/me", ex -> {
            byte[] body = "{\"email\":\"ada@x.com\"}".getBytes(StandardCharsets.UTF_8);
            ex.getResponseHeaders().set("Content-Type", "application/json");
            ex.sendResponseHeaders(200, body.length);
            try (var out = ex.getResponseBody()) { out.write(body); }
        });
        context.getFilters().add(new SecurityHeaders());
        server.start();
        try (var client = HttpClient.newHttpClient()) {
            String base = "http://127.0.0.1:" + server.getAddress().getPort() + "/me";
            // Origin is a restricted header in java.net.http; check.sh allows it with a system property.
            HttpResponse<String> ours = client.send(request(base, "https://app.example.com"), HttpResponse.BodyHandlers.ofString());
            HttpResponse<String> evil = client.send(request(base, "https://evil.example"), HttpResponse.BodyHandlers.ofString());
            assert ours.headers().firstValue("x-content-type-options").orElse("").equals("nosniff");
            assert ours.headers().firstValue("access-control-allow-origin").orElse("").equals("https://app.example.com");
            assert evil.headers().firstValue("access-control-allow-origin").isEmpty();
            assert evil.body().contains("ada@x.com") : "CORS is not access control";
            System.out.println("ok: filter headers, CORS allowlist, and the body still reaches non-browsers");
        } finally {
            server.stop(0);
        }
    }

    static HttpRequest request(String url, String origin) {
        return HttpRequest.newBuilder(URI.create(url)).header("Origin", origin).build();
    }
}
```

**Lab:** `labs/security-headers/javascript/java/` — checked with Java 21. `Origin` is a restricted header in `java.net.http`, so the check script allows it with a system property — a reminder that browsers, not servers, set `Origin`.

## 5. Rust

In Axum, the policy is `tower-http` layers. The lab expresses the same policy as a plain function, which is how you'd unit-test the rules before wiring them into layers.

```rust
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
```

**Lab:** `labs/security-headers/javascript/rust/` — checked with Rust 1.96.

## 6. C#

ASP.NET Core has **CORS built in**: register a named policy with `AddCors`, apply it with `UseCors`. Typed properties such as `Response.Headers.ContentSecurityPolicy` set the security headers. `UseHsts()` is in the production template, and deliberately does nothing in Development or over plain HTTP.

```csharp
// ASP.NET Core: a named CORS policy with an allowlist, and a small middleware for the
// security headers. (app.UseHsts() adds HSTS too, but only outside Development and over HTTPS.)
var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
builder.Services.AddCors(options => options.AddPolicy("frontend", policy => policy
    .WithOrigins("https://app.example.com")
    .AllowCredentials()
    .AllowAnyHeader()));

var app = builder.Build();
app.Use(async (context, next) =>
{
    var h = context.Response.Headers;
    h.ContentSecurityPolicy = "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'";
    h.XContentTypeOptions = "nosniff";
    h["Referrer-Policy"] = "strict-origin-when-cross-origin";
    await next();
});
app.UseCors("frontend");
app.MapGet("/me", () => new { email = "ada@x.com" });

app.Urls.Add("http://127.0.0.1:5099");
await app.StartAsync();

using var client = new HttpClient();
async Task<HttpResponseMessage> Get(string origin)
{
    var request = new HttpRequestMessage(HttpMethod.Get, "http://127.0.0.1:5099/me");
    request.Headers.Add("Origin", origin);
    return await client.SendAsync(request);
}

var ours = await Get("https://app.example.com");
var evil = await Get("https://evil.example");
Check(ours.Headers.GetValues("X-Content-Type-Options").Single() == "nosniff", "security headers");
Check(ours.Headers.GetValues("Access-Control-Allow-Origin").Single() == "https://app.example.com", "allowed origin");
Check(!evil.Headers.Contains("Access-Control-Allow-Origin"), "evil origin not allowed");
Check((await evil.Content.ReadAsStringAsync()).Contains("ada@x.com"), "CORS is not access control");
Console.WriteLine("ok: CORS policy, header middleware, and the body still reaches non-browsers");
await app.StopAsync();

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }
```

**Lab:** `labs/security-headers/javascript/csharp/` — runs a real Kestrel server inside the .NET 10 SDK container.

## Check your understanding

1. Which framework here sets most security headers by default, and what do you still have to add?
2. Why is CORS never on by default?
3. In Python, what is WSGI middleware, and why can you test a WSGI app without starting a server?
4. Why does ASP.NET Core's `UseHsts()` do nothing in Development?
5. Every lab shows the evil origin still receiving the response body. What does that prove again, and what actually protects the endpoint?

<details>
<summary>Answers — after your attempt</summary>

1. Spring Boot with Spring Security (Django sets a few too). You still add the CSP — it's app-specific — and the CORS allowlist.
2. Only you know which origins are your frontends. A default would either block your own frontend or allow everyone.
3. A function that wraps the app function, adjusting the request or the response. Because a WSGI app is just a function, the test calls it with a request dictionary and a fake `start_response`.
4. HSTS tells browsers to use only HTTPS for the domain, often for a year. Sent from `localhost` during development, it would break plain-HTTP local sites in that browser.
5. CORS only tells browsers whether a page may read the response; non-browser clients ignore it. Authentication and authorisation in the endpoint protect it.

</details>

## Practice — independent task

**On the flagship, in whatever its backend is written in:** move header and CORS setup into the framework's standard place from §1, and write a test like the labs' — security headers present, allowlisted origin allowed, another origin not.

**Done when:** the test passes in CI and `curl -sI` against the deployed flagship shows every header from the main lesson.

## Before moving on

You can set the headers and CORS allowlist where your framework expects, and test them without a browser.

**Recap.** Same headers everywhere. Spring Security sets most by default; Django a few; Express needs helmet; Go, Axum and FastAPI need middleware or layers; ASP.NET Core has CORS built in. CORS allowlists are never a default, and never access control.

**Next.** That's the end of SWE 101's core lessons. Week 8 is shipping the flagship.

## Related
- [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|Security headers and the same-origin policy]] — the main lesson
- [[concepts/03-design-patterns/02b-structural-patterns-in-other-languages|Structural patterns in other languages]] — middleware as decorators
