// headers.mjs — the response headers that switch on the browser's protections.

export const SECURITY_HEADERS = {
  // Only load scripts, styles and images from our own origin; no plugins; nobody may frame us.
  "content-security-policy": "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
  "x-content-type-options": "nosniff",                 // don't guess file types; trust content-type
  "referrer-policy": "strict-origin-when-cross-origin", // other sites see our origin, never full URLs
  "strict-transport-security": "max-age=31536000; includeSubDomains", // HTTPS only, for a year
  "x-frame-options": "DENY",                           // older browsers' version of frame-ancestors
};

// MISCONFIGURED, and common: echo back whatever Origin asked, with credentials allowed.
// Every website on the internet can now read logged-in users' responses.
export function corsReflectAnything(origin) {
  return origin ? { "access-control-allow-origin": origin, "access-control-allow-credentials": "true" } : {};
}

// CORRECT: only origins on the list, and say the answer depends on Origin so caches don't mix them up.
export function corsAllowlist(origin, allowed) {
  const headers = { vary: "Origin" };
  if (origin && allowed.includes(origin)) {
    headers["access-control-allow-origin"] = origin;
    headers["access-control-allow-credentials"] = "true";
  }
  return headers;
}

// The session cookie: not readable by scripts, HTTPS only, not sent on cross-site requests.
export const sessionCookie = (id) => `session=${id}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=86400`;
