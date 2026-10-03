// web.ts — one small site served over HTTP/1.1 and over HTTP/2, with helpers that count connections and record
// the order responses finish in. Everything runs on 127.0.0.1; HTTP/2 here is "h2c", HTTP/2 without TLS, which
// browsers don't speak but Node's client does when told to (the TLS lesson covers how h2 is chosen over TLS).
import http from "node:http";
import http2 from "node:http2";
import { createHash } from "node:crypto";

const ASSET = "body { color: rebeccapurple; }\n";
const ETAG = `"${createHash("sha256").update(ASSET).digest("hex").slice(0, 16)}"`; // a fingerprint of the content

type Request = { url?: string; headers: Record<string, string | string[] | undefined> };
type Response = { writeHead: (status: number, headers?: Record<string, string>) => unknown; write: (s: string) => unknown; end: (s?: string) => unknown };

/** The site, the same for both versions: what changes between them is how requests share the connection. */
function route(req: Request, res: Response): void {
  if (req.url === "/fast") {
    res.writeHead(200, { "content-type": "text/plain" });
    res.end("fast");
  } else if (req.url === "/slow") {
    setTimeout(() => {
      res.writeHead(200, { "content-type": "text/plain" });
      res.end("slow");
    }, 200);
  } else if (req.url === "/style.css") {
    if (req.headers["if-none-match"] === ETAG) {
      res.writeHead(304, { etag: ETAG }); // "the copy you have is still right": headers only, no body
      res.end();
    } else {
      res.writeHead(200, { "content-type": "text/css", etag: ETAG, "cache-control": "max-age=60" });
      res.end(ASSET);
    }
  } else if (req.url === "/stream") {
    res.writeHead(200, { "content-type": "text/plain" }); // no Content-Length: HTTP/1.1 must send it chunked
    res.write("hello");
    // Writes in the same tick are coalesced into one chunk; where chunks begin and end is the sender's choice.
    setTimeout(() => {
      res.write(" world");
      res.end();
    }, 20);
  } else {
    res.writeHead(404);
    res.end();
  }
}

export async function startHttp1() {
  const server = http.createServer(route);
  const stats = { connections: 0 };
  server.on("connection", () => stats.connections++);
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const port = (server.address() as { port: number }).port;
  return { port, stats, close: () => new Promise<void>((resolve) => server.close(() => resolve())) };
}

export async function startHttp2() {
  const server = http2.createServer(route as any);
  const stats = { connections: 0 };
  server.on("connection", () => stats.connections++);
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const port = (server.address() as { port: number }).port;
  return { port, stats, close: () => new Promise<void>((resolve) => server.close(() => resolve())) };
}

/** One HTTP/1.1 GET through an agent, resolving to the status, headers and body. */
export function get1(port: number, path: string, agent: http.Agent, headers: Record<string, string> = {}) {
  return new Promise<{ status: number; headers: http.IncomingHttpHeaders; body: string }>((resolve, reject) => {
    http
      .get({ host: "127.0.0.1", port, path, agent, headers }, (res) => {
        let body = "";
        res.on("data", (chunk) => (body += chunk));
        res.on("end", () => resolve({ status: res.statusCode!, headers: res.headers, body }));
      })
      .on("error", reject);
  });
}

/** One HTTP/2 GET as a stream on an existing session. */
export function get2(session: http2.ClientHttp2Session, path: string) {
  return new Promise<string>((resolve, reject) => {
    const stream = session.request({ ":path": path });
    let body = "";
    stream.on("data", (chunk) => (body += chunk));
    stream.on("end", () => resolve(body));
    stream.on("error", reject);
  });
}

/** Starts the requests at the same moment and records the order they finish in. */
export async function finishOrder(requests: (() => Promise<string>)[]): Promise<string[]> {
  const order: string[] = [];
  await Promise.all(requests.map((r) => r().then((body) => void order.push(body))));
  return order;
}
