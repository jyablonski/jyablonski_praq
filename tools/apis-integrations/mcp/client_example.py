import asyncio
import os

from mcp import Client

SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8000/mcp")
EXPECTED_PROTOCOL_VERSION = "2026-07-28"


async def run() -> None:
    async with Client(SERVER_URL) as client:
        if client.protocol_version != EXPECTED_PROTOCOL_VERSION:
            raise RuntimeError(
                f"Expected MCP {EXPECTED_PROTOCOL_VERSION}, got {client.protocol_version}"
            )

        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools.tools]
        print(f"Connected with MCP {client.protocol_version}: {tool_names}")

        result = await client.call_tool(
            "query_policy_docs",
            {"query": "my refund is broken"},
        )
        if result.is_error or result.structured_content is None:
            raise RuntimeError("query_policy_docs did not return structured output")

        print("\nTool output:")
        print(result.structured_content["result"])


if __name__ == "__main__":
    asyncio.run(run())
