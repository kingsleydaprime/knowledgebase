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
