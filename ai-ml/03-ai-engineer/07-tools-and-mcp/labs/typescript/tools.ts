// tools.ts — what a tool is, how its arguments are checked, and how one requested call is carried out.

/** The subset of JSON Schema that tool arguments need. Real apps use Ajv or Zod for the full language. */
export type JsonSchema = {
  type?: "object" | "string" | "number" | "integer" | "boolean";
  description?: string;
  properties?: Record<string, JsonSchema>;
  required?: string[];
  additionalProperties?: boolean;
  pattern?: string;
  enum?: unknown[];
  minimum?: number;
  maximum?: number;
};

/** What the model sees: a name, a description it chooses by, and the shape of the arguments. */
export type ToolSpec = { name: string; description: string; inputSchema: JsonSchema };

/** What your code holds: the spec, whether calling it changes anything, and the function itself. */
export type Tool = ToolSpec & {
  sideEffects: boolean; // true for anything that writes, sends, pays or deletes
  run: (args: Record<string, unknown>) => unknown | Promise<unknown>;
};

/** A request from the model. `arguments` is a JSON string, as models send it, and may not even parse. */
export type ToolCall = { id: string; name: string; arguments: string };
export type ToolResult = { id: string; content: string; isError: boolean };

/** Every problem with a value, as short messages a model can act on. An empty list means valid. */
export function validate(schema: JsonSchema, value: unknown, path = "arguments"): string[] {
  const kind = Array.isArray(value) ? "array" : value === null ? "null" : typeof value;
  if (schema.type === "integer" ? !Number.isInteger(value) : schema.type && kind !== schema.type) {
    return [`${path}: expected ${schema.type}, got ${kind}`];
  }
  const errors: string[] = [];
  if (schema.enum && !schema.enum.includes(value)) errors.push(`${path}: must be one of ${schema.enum.join(", ")}`);
  if (schema.pattern && typeof value === "string" && !new RegExp(schema.pattern).test(value)) {
    errors.push(`${path}: must match ${schema.pattern}`);
  }
  if (schema.minimum !== undefined && typeof value === "number" && value < schema.minimum) errors.push(`${path}: must be at least ${schema.minimum}`);
  if (schema.maximum !== undefined && typeof value === "number" && value > schema.maximum) errors.push(`${path}: must be at most ${schema.maximum}`);
  if (kind === "object") {
    const object = value as Record<string, unknown>;
    for (const key of schema.required ?? []) if (!(key in object)) errors.push(`${path}.${key}: required`);
    for (const [key, item] of Object.entries(object)) {
      const child = schema.properties?.[key];
      if (child) errors.push(...validate(child, item, `${path}.${key}`));
      else if (schema.additionalProperties === false) errors.push(`${path}.${key}: not allowed`);
    }
  }
  return errors;
}

export type Approve = (call: { name: string; args: Record<string, unknown> }) => boolean | Promise<boolean>;

/** Carry out one requested call. Every failure becomes a result the model reads, not an exception:
 *  a model told "order_id: must match ^[A-Z][0-9]{3}$" can fix its next call. */
export async function execute(call: ToolCall, tools: Tool[], approve: Approve, maxChars = 2000): Promise<ToolResult> {
  const fail = (content: string): ToolResult => ({ id: call.id, content, isError: true });
  const tool = tools.find((t) => t.name === call.name);
  if (!tool) return fail(`unknown tool "${call.name}"; available: ${tools.map((t) => t.name).join(", ")}`);

  let args: unknown;
  try {
    args = JSON.parse(call.arguments || "{}");
  } catch {
    return fail("arguments are not valid JSON");
  }
  const problems = validate(tool.inputSchema, args);
  if (problems.length) return fail(problems.join("; "));

  // Checked before asking a person: nobody should be asked to approve a malformed call.
  if (tool.sideEffects && !(await approve({ name: tool.name, args: args as Record<string, unknown> }))) {
    return fail("the user declined this action");
  }

  try {
    const content = JSON.stringify(await tool.run(args as Record<string, unknown>)) ?? "null";
    return { id: call.id, isError: false, content: content.length > maxChars ? content.slice(0, maxChars) + " …[truncated]" : content };
  } catch (error) {
    return fail(`${tool.name} failed: ${(error as Error).message}`); // the message, never a stack trace
  }
}

/** Only the parts the model should see. `run` and `sideEffects` stay on your side of the boundary. */
export const specs = (tools: Tool[]): ToolSpec[] => tools.map(({ name, description, inputSchema }) => ({ name, description, inputSchema }));
