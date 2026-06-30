import time

from mcp.server.fastmcp import FastMCP
import uvicorn

# 1. Initialize FastMCP
# This automatically handles the SSE connection, session management,
# and the /sse and /messages endpoints for you.
mcp = FastMCP("my-rag-server")


# 2. Define your tool
@mcp.tool()
def query_policy_docs(query: str) -> str:
    """Retrieves company policy information based on a search string."""
    # In a real app, you would query whatever 3rd party system you have here
    time.sleep(3)
    return f"Found relevant docs for: {query}\n1. Refund Policy: 30 days."


# 3. Expose the ASGI app
# This generates a production-ready Starlette app with correct routes
app = mcp.sse_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
