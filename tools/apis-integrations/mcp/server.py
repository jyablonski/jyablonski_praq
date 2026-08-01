from mcp.server import MCPServer
import uvicorn

mcp = MCPServer(
    "policy-docs",
    version="0.1.0",
    instructions="Use query_policy_docs to retrieve company policy information.",
)


@mcp.tool()
def query_policy_docs(query: str) -> str:
    """Retrieves company policy information based on a search string."""
    return f"Found relevant docs for: {query}\n1. Refund Policy: 30 days."


app = mcp.streamable_http_app(
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
