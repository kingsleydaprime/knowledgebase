// conformance.ts — check any language's support-tools MCP server with the official client, pinned to 2026-07-28.
//   node conformance.ts <command> [args...]      e.g. node conformance.ts python3 server.py
// The client starts the server itself, over stdio. Exits non-zero on the first broken expectation.
import assert from "node:assert/strict";
import { Client } from "@modelcontextprotocol/client";
import { StdioClientTransport } from "@modelcontextprotocol/client/stdio";

const [command, ...args] = process.argv.slice(2);
const client = new Client({ name: "conformance", version: "1.0.0" }, { versionNegotiation: { mode: { pin: "2026-07-28" } } });
await client.connect(new StdioClientTransport({ command, args, stderr: "pipe" }));

type Result = Awaited<ReturnType<typeof client.callTool>>;
// SDKs may send the value as structured content, as JSON text, or both. Compare values, not bytes.
const value = (r: Result) => r.structuredContent ?? JSON.parse(r.content.map((c) => (c.type === "text" ? c.text : "")).join(""));
const text = (r: Result) => r.content.map((c) => (c.type === "text" ? c.text : "")).join("");

try {
  const { tools } = await client.listTools();
  assert.deepEqual(tools.map((t) => t.name), ["get_order", "get_refund", "issue_refund"], "three tools, in a fixed order");
  assert.equal(tools[0].annotations?.readOnlyHint, true, "get_order is marked read-only");
  assert.equal(tools[2].annotations?.destructiveHint, true, "issue_refund is marked destructive");
  console.log("tools/list: get_order, get_refund, issue_refund, with annotations");

  const refund = await client.callTool({ name: "get_refund", arguments: { order_id: "C789" } });
  assert.notEqual(refund.isError, true);
  assert.deepEqual(value(refund), { status: "paid", amount: 15, paid: "2026-09-20" });
  console.log("tools/call get_refund C789: the refund");

  const bad = await client.callTool({ name: "get_order", arguments: { order_id: "nope" } });
  assert.equal(bad.isError, true, "a bad argument is a tool error the model can read");
  assert.match(text(bad), /order_id/, "and the message names the argument");
  console.log(`tools/call get_order "nope": tool error: ${text(bad).split("\n")[0].slice(0, 100)}`);

  const unknown = await client.callTool({ name: "drop_tables", arguments: {} }).then(
    (r) => `a tool error (isError ${r.isError})`,
    (e) => `a protocol error (${e.code})`,
  );
  // The spec's tools page lists an unknown tool among protocol errors, without a MUST; SDKs differ.
  // Either way it must be refused, so print which.
  console.log(`tools/call drop_tables: ${unknown}`);
  assert.match(unknown, /a protocol error \(-32602\)|a tool error \(isError true\)/, "an unknown tool is refused");
  console.log("conformance: pass");
} finally {
  await client.close();
}
