"""The support tools as an MCP server, with the official Python SDK (mcp 2.x speaks 2026-07-28).
    python server.py              all three tools, over stdio
    python server.py --read-only  only the tools that change nothing
The type hints are the schema: the SDK turns them into inputSchema and validates every call against it."""
import sys
from typing import Annotated

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

from tools import load_orders, support_tools

OrderId = Annotated[str, Field(pattern=r"^[A-Z][0-9]{3}$", description="Like A123: one capital letter, three digits")]
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False)

tools = {t.name: t for t in support_tools(load_orders())}  # the same order store and rules as the tool loop
mcp = MCPServer("support-tools")


@mcp.tool(annotations=READ_ONLY)
def get_order(order_id: OrderId) -> dict:
    """Look up an order's status, total and tracking number. Use it before answering any question about an order."""
    return tools["get_order"].run({"order_id": order_id})


@mcp.tool(annotations=READ_ONLY)
def get_refund(order_id: OrderId) -> dict:
    """Look up the refund on an order, if there is one: its status, amount and dates."""
    return tools["get_refund"].run({"order_id": order_id})


if "--read-only" not in sys.argv:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
    def issue_refund(order_id: OrderId, amount: Annotated[float, Field(ge=0.01)]) -> dict:
        """Refund money to the customer. Only when the customer asks for a refund and none exists yet."""
        return tools["issue_refund"].run({"order_id": order_id, "amount": amount})  # the tool's own rules still apply


if __name__ == "__main__":
    mcp.run()  # stdio by default; logs go to stderr
