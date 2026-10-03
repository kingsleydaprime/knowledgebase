// trifecta.ts — never let one session hold all three of: private data, untrusted content, and a way to send
// things out. With all three, an injected instruction can read your data and post it somewhere.
import type { Tool } from "../../../07-tools-and-mcp/labs/typescript/tools.ts";

export type Capability = "private_data" | "untrusted_content" | "external_action";

export class Session {
  readonly used = new Set<Capability>();

  /** Wrap a tool so that each call first checks whether it would complete the trifecta. */
  guard(tool: Tool, capabilities: Capability[]): Tool {
    return {
      ...tool,
      run: async (args) => {
        const after = new Set([...this.used, ...capabilities]);
        if (after.size === 3) {
          const missing = capabilities.filter((c) => !this.used.has(c));
          throw new Error(`blocked: ${missing.join(" and ")} would give this session private data, untrusted content and a way to send it out`);
        }
        capabilities.forEach((c) => this.used.add(c));
        return tool.run(args);
      },
    };
  }
}
