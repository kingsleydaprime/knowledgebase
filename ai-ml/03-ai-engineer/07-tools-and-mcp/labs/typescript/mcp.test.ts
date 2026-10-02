import { test } from "node:test";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { createInterface } from "node:readline";
import { Client } from "@modelcontextprotocol/client";
import { StdioClientTransport } from "@modelcontextprotocol/client/stdio";
import { answerWithTools, type Turn } from "./loop.ts";
import { toolsFrom } from "./mcp-host.ts";

const server = new URL("mcp-server.ts", import.meta.url).pathname;
const meta = { "io.modelcontextprotocol/protocolVersion": "2026-07-28", "io.modelcontextprotocol/clientCapabilities": {} };

/** Talk to the server the way any client does: one JSON-RPC message per line on its stdin and stdout. */
async function raw(lines: object[], args: string[] = []) {
  const child = spawn(process.execPath, [server, ...args], { stdio: ["pipe", "pipe", "pipe"] });
  const replies: any[] = [];
  const reading = (async () => {
    for await (const line of createInterface({ input: child.stdout })) replies.push(JSON.parse(line)); // every stdout line must parse
  })();
  for (const line of lines) child.stdin.write(JSON.stringify(line) + "\n");
  child.stdin.end(); // closing stdin is how a client says it's finished
  const [code] = await once(child, "exit");
  await reading;
  return { replies, code };
}

test("the wire: no handshake, versions checked on every request, errors in two kinds", async () => {
  const { replies, code } = await raw([
    { jsonrpc: "2.0", id: 1, method: "server/discover", params: { _meta: meta } },
    { jsonrpc: "2.0", id: 2, method: "tools/list", params: {} }, // no _meta
    { jsonrpc: "2.0", id: 3, method: "tools/list", params: { _meta: { ...meta, "io.modelcontextprotocol/protocolVersion": "2025-11-25" } } },
    { jsonrpc: "2.0", method: "notifications/cancelled", params: { requestId: 99 } }, // a notification: no reply
    { jsonrpc: "2.0", id: 4, method: "tools/call", params: { _meta: meta, name: "drop_tables", arguments: {} } },
    { jsonrpc: "2.0", id: 5, method: "tools/call", params: { _meta: meta, name: "get_order", arguments: { order_id: "nope" } } },
    { jsonrpc: "2.0", id: 6, method: "resources/list", params: { _meta: meta } },
  ]);
  assert.equal(code, 0); // it exited when stdin closed
  assert.deepEqual(replies.map((r) => r.id), [1, 2, 3, 4, 5, 6]);
  assert.deepEqual(replies[0].result.supportedVersions, ["2026-07-28"]);
  assert.equal(replies[1].error.code, -32602);
  assert.deepEqual(replies[2].error, {
    code: -32022,
    message: "unsupported protocol version 2025-11-25",
    data: { supported: ["2026-07-28"], requested: "2025-11-25" },
  });
  assert.deepEqual(replies[3].error, { code: -32602, message: "Unknown tool: drop_tables" }); // protocol error
  assert.deepEqual(replies[4].result.content, [{ type: "text", text: "arguments.order_id: must match ^[A-Z][0-9]{3}$" }]);
  assert.equal(replies[4].result.isError, true); // tool error: the model can read it and fix its call
  assert.equal(replies[5].error.code, -32601);
});

test("read-only mode exposes less: the safest tool is the one that isn't there", async () => {
  const list = { jsonrpc: "2.0", id: 1, method: "tools/list", params: { _meta: meta } };
  const all = (await raw([list])).replies[0].result.tools.map((t: any) => t.name);
  const readOnly = (await raw([list], ["--read-only"])).replies[0].result.tools.map((t: any) => t.name);
  assert.deepEqual(all, ["get_order", "get_refund", "issue_refund"]);
  assert.deepEqual(readOnly, ["get_order", "get_refund"]);
});

async function connect() {
  // Pinned: the official client must speak 2026-07-28 to this server, with no fallback to the old handshake.
  const client = new Client({ name: "lab-host", version: "1.0.0" }, { versionNegotiation: { mode: { pin: "2026-07-28" } } });
  await client.connect(new StdioClientTransport({ command: process.execPath, args: [server], stderr: "pipe" }));
  return client;
}

test("the official MCP client accepts the hand-written server", async () => {
  const client = await connect();
  try {
    const { tools } = await client.listTools();
    assert.deepEqual(tools.map((t) => [t.name, t.annotations?.destructiveHint]), [["get_order", false], ["get_refund", false], ["issue_refund", true]]);
    const refund = await client.callTool({ name: "get_refund", arguments: { order_id: "C789" } });
    assert.deepEqual(refund.content, [{ type: "text", text: '{"status":"paid","amount":15,"paid":"2026-09-20"}' }]);
    await assert.rejects(client.callTool({ name: "drop_tables", arguments: {} }), /Unknown tool: drop_tables/);
  } finally {
    await client.close();
  }
});

test("the host turns MCP tools into ordinary tools, so the same loop and the same approval gate apply", async () => {
  const client = await connect();
  try {
    const tools = await toolsFrom(client);
    assert.deepEqual(tools.map((t) => [t.name, t.sideEffects]), [["get_order", false], ["get_refund", false], ["issue_refund", true]]);
    const turns: Turn[] = [
      { content: "", toolCalls: [{ id: "c1", name: "get_refund", arguments: '{"order_id":"A123"}' }] },
      { content: "", toolCalls: [{ id: "c2", name: "issue_refund", arguments: '{"order_id":"B456","amount":120}' }] },
      { content: "Your refund is being processed.", toolCalls: [] },
    ];
    const asked: string[] = [];
    const { messages } = await answerWithTools(async () => turns.shift()!, [{ role: "user", content: "refund?" }], tools, {
      approve: ({ name }) => (asked.push(name), false),
    });
    assert.deepEqual(messages[2], { role: "tool", toolCallId: "c1", content: '{"status":"processing","amount":49.99,"requested":"2026-09-28"}' });
    assert.deepEqual(messages[4], { role: "tool", toolCallId: "c2", content: "ERROR: the user declined this action" });
    assert.deepEqual(asked, ["issue_refund"]); // the host asked the person; the server was never called
  } finally {
    await client.close();
  }
});
