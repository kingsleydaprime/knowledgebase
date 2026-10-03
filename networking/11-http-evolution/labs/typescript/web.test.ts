import { test } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import http2 from "node:http2";
import net from "node:net";
import { finishOrder, get1, get2, startHttp1, startHttp2 } from "./web.ts";

test("keep-alive: ten requests over one connection instead of ten", async () => {
  for (const [keepAlive, expected] of [[false, 10], [true, 1]] as const) {
    const server = await startHttp1();
    const agent = new http.Agent({ keepAlive, maxSockets: 1 });
    for (let i = 0; i < 10; i++) assert.equal((await get1(server.port, "/fast", agent)).body, "fast");
    assert.equal(server.stats.connections, expected, `keepAlive ${keepAlive}`); // each connection is a TCP (and TLS) handshake
    agent.destroy();
    await server.close();
  }
});

test("HTTP/1.1 head-of-line blocking: on one connection, the fast reply waits behind the slow one", async () => {
  const server = await startHttp1();
  const agent = new http.Agent({ keepAlive: true, maxSockets: 1 }); // one connection, as on a busy origin
  const order = await finishOrder([async () => (await get1(server.port, "/slow", agent)).body, async () => (await get1(server.port, "/fast", agent)).body]);
  assert.deepEqual(order, ["slow", "fast"]);
  agent.destroy();
  await server.close();
});

test("HTTP/2 multiplexing: on one connection, the fast reply overtakes the slow one", async () => {
  const server = await startHttp2();
  const session = http2.connect(`http://127.0.0.1:${server.port}`);
  const order = await finishOrder([() => get2(session, "/slow"), () => get2(session, "/fast")]);
  assert.deepEqual(order, ["fast", "slow"]); // two streams interleaved on one connection
  assert.equal(server.stats.connections, 1);
  session.close();
  await server.close();
});

test("revalidation: an ETag turns a second download into a 304 with no body", async () => {
  const server = await startHttp1();
  const agent = new http.Agent({ keepAlive: true });
  const first = await get1(server.port, "/style.css", agent);
  assert.equal(first.status, 200);
  assert.equal(first.headers["cache-control"], "max-age=60"); // fresh for a minute: no request at all
  const again = await get1(server.port, "/style.css", agent, { "if-none-match": first.headers.etag as string });
  assert.deepEqual([again.status, again.body], [304, ""]); // after that, a cheap "is it still the same?"
  agent.destroy();
  await server.close();
});

test("chunked transfer encoding, as it looks on the wire", async () => {
  const server = await startHttp1();
  try {
    const raw = await new Promise<string>((resolve) => {
      const socket = net.connect(server.port, "127.0.0.1", () => socket.write("GET /stream HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n"));
      let data = "";
      socket.on("data", (chunk) => (data += chunk));
      socket.on("end", () => resolve(data));
    });
    const split = raw.indexOf("\r\n\r\n"); // a blank line separates the head from the body
    const [head, body] = [raw.slice(0, split), raw.slice(split + 4)];
    assert.match(head, /^HTTP\/1\.1 200 OK/);
    assert.match(head, /Transfer-Encoding: chunked/i);
    assert.equal(body, "5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n"); // each chunk's length in hex, then the chunk; 0 ends it
  } finally {
    await server.close();
  }
});
