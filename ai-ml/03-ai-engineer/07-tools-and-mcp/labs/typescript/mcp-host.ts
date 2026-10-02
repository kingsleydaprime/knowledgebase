// mcp-host.ts — the host's side: turn an MCP server's tools into ordinary Tools, so the same loop uses them.
import type { Client } from "@modelcontextprotocol/client";
import type { Tool } from "./tools.ts";

/** Only for servers you trust: tool annotations are the server's own claims about itself. */
export async function toolsFrom(client: Client): Promise<Tool[]> {
  const { tools } = await client.listTools();
  return tools.map((t) => ({
    name: t.name,
    description: t.description ?? "",
    inputSchema: t.inputSchema as Tool["inputSchema"],
    sideEffects: t.annotations?.readOnlyHint !== true, // anything not marked read-only gets the approval gate
    run: async (args) => {
      const result = await client.callTool({ name: t.name, arguments: args });
      const text = result.content.map((c) => (c.type === "text" ? c.text : `[${c.type}]`)).join("\n");
      if (result.isError) throw new Error(text); // becomes an ERROR result in the loop, as for a local tool
      return JSON.parse(text);
    },
  }));
}
