// app.mjs — an API that sets every header above. `cors` is swappable so the test can compare.
import { createServer } from "node:http";
import { SECURITY_HEADERS, corsAllowlist, sessionCookie } from "./headers.mjs";

export function createApp({ cors = (origin) => corsAllowlist(origin, ["https://app.example.com"]) } = {}) {
  return createServer((req, res) => {
    const base = { ...SECURITY_HEADERS, ...cors(req.headers.origin) };

    if (req.method === "OPTIONS") {
      // The browser's preflight: "may this origin send this kind of request?"
      res.writeHead(204, { ...base, "access-control-allow-methods": "GET, POST", "access-control-allow-headers": "content-type" });
      return res.end();
    }
    if (req.url === "/login" && req.method === "POST") {
      res.writeHead(204, { ...base, "set-cookie": sessionCookie("s3cr3t") });
      return res.end();
    }
    if (req.url === "/me") {
      // Real code checks the session cookie here. CORS does not do this for you.
      res.writeHead(200, { ...base, "content-type": "application/json" });
      return res.end(JSON.stringify({ email: "ada@x.com" }));
    }
    res.writeHead(404, base);
    res.end();
  });
}
