//! The support tools as an MCP server, with the official Rust SDK (rmcp 3.5 speaks 2026-07-28).
//!     cargo run --bin server              all three tools, over stdio
//!     cargo run --bin server -- --read-only  only the tools that change nothing
//! rmcp handles the protocol and the transport; `list_tools` and `call_tool` hand over to the
//! same registry and checks the tool loop uses.
use rmcp::model::{
    CacheScope, CallToolRequestParams, CallToolResponse, CallToolResult, ContentBlock,
    ListToolsResult, PaginatedRequestParams, ServerCapabilities, ServerConfig, Tool,
    ToolAnnotations,
};
use rmcp::service::{RequestContext, RoleServer};
use rmcp::{ErrorData, ServerHandler, ServiceExt};
use support_tools::{ToolCall, execute, load_orders, support_tools};

struct Support {
    tools: Vec<support_tools::Tool>,
}

impl ServerHandler for Support {
    fn get_info(&self) -> ServerConfig {
        ServerConfig::new(ServerCapabilities::builder().enable_tools().build())
    }

    async fn list_tools(
        &self,
        _request: Option<PaginatedRequestParams>,
        _context: RequestContext<RoleServer>,
    ) -> Result<ListToolsResult, ErrorData> {
        let tools = self.tools.iter().map(|t| {
            let schema = t.schema.as_object().cloned().unwrap_or_default();
            let hints = ToolAnnotations::from_raw(
                None,
                Some(!t.side_effects),
                Some(t.side_effects),
                None,
                None,
            );
            Tool::new(t.name, t.description, schema).with_annotations(hints)
        });
        // Always the same order; and 2026-07-28 requires cache hints on every list, which rmcp leaves to us.
        Ok(ListToolsResult::with_all_items(tools.collect())
            .with_ttl_ms(300_000)
            .with_cache_scope(CacheScope::Public))
    }

    async fn call_tool(
        &self,
        request: CallToolRequestParams,
        _context: RequestContext<RoleServer>,
    ) -> Result<CallToolResponse, ErrorData> {
        if !self.tools.iter().any(|t| t.name == request.name) {
            // a protocol error: the request itself is wrong
            return Err(ErrorData::invalid_params(
                format!("Unknown tool: {}", request.name),
                None,
            ));
        }
        let arguments =
            serde_json::Value::Object(request.arguments.unwrap_or_default()).to_string();
        let call = ToolCall {
            id: "mcp".into(),
            name: request.name.to_string(),
            arguments,
        };
        // Approval is the host's job: it asks the person before calling a destructive tool.
        let outcome = execute(&call, &self.tools, &|_, _| true);
        let content = vec![ContentBlock::text(outcome.content)];
        Ok(if outcome.is_error {
            CallToolResult::error(content)
        } else {
            CallToolResult::success(content)
        }
        .into())
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut tools = support_tools(&load_orders("../shared/orders.json"));
    if std::env::args().any(|a| a == "--read-only") {
        tools.retain(|t| !t.side_effects);
    }
    eprintln!(
        "support-tools MCP server: {}",
        tools.iter().map(|t| t.name).collect::<Vec<_>>().join(", ")
    ); // stderr only
    let server = Support { tools }.serve(rmcp::transport::stdio()).await?;
    server.waiting().await?; // returns when the client closes stdin
    Ok(())
}
