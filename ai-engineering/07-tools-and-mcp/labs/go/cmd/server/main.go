// The support tools as an MCP server, with the official Go SDK (go-sdk v1.8 speaks 2026-07-28).
//
//	go run ./cmd/server              all three tools, over stdio
//	go run ./cmd/server --read-only  only the tools that change nothing
package main

import (
	"context"
	"encoding/json"
	"log"
	"os"
	"slices"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"tools"
)

// add registers one tool. In is the argument type: the SDK decodes and validates the call into it
// before the handler runs, so the handler only re-encodes it for the tool's own Run.
func add[In any](server *mcp.Server, t tools.Tool) {
	annotations := &mcp.ToolAnnotations{ReadOnlyHint: !t.SideEffects, DestructiveHint: new(t.SideEffects)}
	mcp.AddTool(server, &mcp.Tool{Name: t.Name, Description: t.Description, InputSchema: t.Schema, Annotations: annotations},
		func(ctx context.Context, _ *mcp.CallToolRequest, in In) (*mcp.CallToolResult, any, error) {
			raw, err := json.Marshal(in)
			if err != nil {
				return nil, nil, err
			}
			out, err := t.Run(ctx, raw) // an error here becomes a tool error the model can read
			return nil, out, err
		})
}

func main() {
	orders, err := tools.LoadOrders("../shared/orders.json")
	if err != nil {
		log.Fatal(err) // log writes to stderr, so it never corrupts the protocol on stdout
	}
	byName := map[string]tools.Tool{}
	for _, t := range tools.SupportTools(orders) {
		byName[t.Name] = t
	}
	server := mcp.NewServer(&mcp.Implementation{Name: "support-tools", Version: "1.0.0"}, nil)
	add[tools.IDArgs](server, byName["get_order"])
	add[tools.IDArgs](server, byName["get_refund"])
	if !slices.Contains(os.Args[1:], "--read-only") {
		add[tools.RefundArgs](server, byName["issue_refund"])
	}
	if err := server.Run(context.Background(), &mcp.StdioTransport{}); err != nil {
		log.Fatal(err)
	}
}
