// mcp-server.ts — the support tools as an MCP server over stdio, protocol revision 2026-07-28, by hand.
// A client starts it as a subprocess and writes one JSON-RPC message per line to its stdin:
//   node mcp-server.ts              all three tools
//   node mcp-server.ts --read-only  only the tools that change nothing
import { createInterface } from "node:readline";
import { loadOrders, supportTools } from "./support-tools.ts";
import { execute, type Tool } from "./tools.ts";

export const PROTOCOL_VERSION = "2026-07-28";
const KEY = "io.modelcontextprotocol/"; // the prefix of MCP's reserved _meta keys
const SERVER_INFO = { name: "support-tools", version: "1.0.0" };

type Request = { jsonrpc: "2.0"; id?: string | number; method: string; params?: Record<string, any> };

export async function handle(message: Request, tools: Tool[]): Promise<object | null> {
  if (message.id === undefined) return null; // a notification: nothing to reply to
  const id = message.id;
  const result = (body: object) => ({
    jsonrpc: "2.0",
    id,
    result: { resultType: "complete", ...body, _meta: { [`${KEY}serverInfo`]: SERVER_INFO } },
  });
  const error = (code: number, text: string, data?: object) => ({ jsonrpc: "2.0", id, error: { code, message: text, ...(data && { data }) } });

  // No handshake: every request says which protocol version it speaks and what the client can do.
  const meta = message.params?._meta ?? {};
  const version = meta[`${KEY}protocolVersion`];
  if (version === undefined || meta[`${KEY}clientCapabilities`] === undefined) {
    return error(-32602, "every request must carry protocolVersion and clientCapabilities in _meta");
  }
  if (version !== PROTOCOL_VERSION) {
    return error(-32022, `unsupported protocol version ${version}`, { supported: [PROTOCOL_VERSION], requested: version });
  }

  switch (message.method) {
    case "server/discover":
      return result({
        supportedVersions: [PROTOCOL_VERSION],
        capabilities: { tools: {} },
        instructions: "Order and refund tools for a support assistant. Look an order up before answering about it.",
        ttlMs: 3_600_000,
        cacheScope: "public",
      });
    case "tools/list":
      return result({
        // Always the same order, so a client's cached list and a model's cached prompt stay valid.
        tools: tools.map(({ name, description, inputSchema, sideEffects }) => ({
          name,
          description,
          inputSchema,
          annotations: { readOnlyHint: !sideEffects, destructiveHint: sideEffects }, // hints: a client trusts them only from servers it trusts
        })),
        ttlMs: 300_000,
        cacheScope: "public",
      });
    case "tools/call": {
      const { name, arguments: args = {} } = message.params ?? {};
      // A protocol error: the request itself is wrong, and the model can't fix that by retrying.
      if (!tools.some((t) => t.name === name)) return error(-32602, `Unknown tool: ${name}`);
      // Approval is the host's job: it asks the person before sending a call to a destructive tool.
      const outcome = await execute({ id: String(id), name, arguments: JSON.stringify(args) }, tools, () => true);
      // A tool execution error: reported in the result, so the model can read it and correct itself.
      return result({ content: [{ type: "text", text: outcome.content }], isError: outcome.isError });
    }
    default:
      return error(-32601, `Method not found: ${message.method}`);
  }
}

if (import.meta.main) {
  const all = supportTools(loadOrders());
  const tools = process.argv.includes("--read-only") ? all.filter((t) => !t.sideEffects) : all;
  // stdout carries protocol messages and nothing else; logs go to stderr.
  console.error(`support-tools MCP server: ${tools.map((t) => t.name).join(", ")}`);
  for await (const line of createInterface({ input: process.stdin })) {
    if (!line.trim()) continue;
    let message: Request;
    try {
      message = JSON.parse(line);
    } catch {
      process.stdout.write(JSON.stringify({ jsonrpc: "2.0", error: { code: -32700, message: "Parse error" } }) + "\n");
      continue;
    }
    const reply = await handle(message, tools);
    if (reply) process.stdout.write(JSON.stringify(reply) + "\n");
  }
  // stdin closed: the client is done, so exit.
}
