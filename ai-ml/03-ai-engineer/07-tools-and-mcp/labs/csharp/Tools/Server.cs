// The support tools as an MCP server, with the official C# SDK (ModelContextProtocol 2.2 speaks 2026-07-28).
//   dotnet Tools.dll serve              all three tools, over stdio
//   dotnet Tools.dll serve --read-only  only the tools that change nothing
// The SDK handles the protocol and the transport; the two handlers hand over to the same registry
// and checks the tool loop uses.
using System.Text.Json;
using ModelContextProtocol;
using ModelContextProtocol.Protocol;
using ModelContextProtocol.Server;
using McpTool = ModelContextProtocol.Protocol.Tool;

public static class Server
{
    public static async Task Run(string[] args)
    {
        var all = Tools.SupportTools(Tools.LoadOrders("../shared/orders.json"));
        var tools = args.Contains("--read-only") ? all.Where(t => !t.SideEffects).ToList() : all;
        Console.Error.WriteLine($"support-tools MCP server: {string.Join(", ", tools.Select(t => t.Name))}"); // stderr only
        var options = new McpServerOptions
        {
            ServerInfo = new Implementation { Name = "support-tools", Version = "1.0.0" },
            Handlers = new McpServerHandlers
            {
                ListToolsHandler = (request, ct) => ValueTask.FromResult(new ListToolsResult
                {
                    Tools = [.. tools.Select(t => new McpTool
                    {
                        Name = t.Name,
                        Description = t.Description,
                        InputSchema = JsonSerializer.SerializeToElement(t.InputSchema),
                        Annotations = new ToolAnnotations { ReadOnlyHint = !t.SideEffects, DestructiveHint = t.SideEffects },
                    })],
                    TimeToLive = TimeSpan.FromMinutes(5), // 2026-07-28 requires cache hints on every list
                    CacheScope = CacheScope.Public,
                }),
                CallToolHandler = (request, ct) =>
                {
                    var name = request.Params!.Name;
                    if (tools.All(t => t.Name != name))
                        throw new McpProtocolException($"Unknown tool: {name}", McpErrorCode.InvalidParams); // a protocol error
                    var arguments = JsonSerializer.Serialize(request.Params.Arguments ?? new Dictionary<string, JsonElement>());
                    // Approval is the host's job: it asks the person before calling a destructive tool.
                    var outcome = Tools.Execute(new ToolCall("mcp", name, arguments), tools, (_, _) => true);
                    return ValueTask.FromResult(new CallToolResult { Content = [new TextContentBlock { Text = outcome.Content }], IsError = outcome.IsError });
                },
            },
        };
        await using var server = McpServer.Create(new StdioServerTransport("support-tools"), options);
        await server.RunAsync(); // returns when the client closes stdin
    }
}
