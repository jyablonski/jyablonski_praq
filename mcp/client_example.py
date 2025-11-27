import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession


async def run():
    # Connect to the SSE endpoint
    async with sse_client("http://localhost:8000/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 1. Initialize
            await session.initialize()

            # 2. List Available Tools
            tools = await session.list_tools()
            print(f"Connected! Found tool: {tools.tools[0].name}")

            # 3. Call the Tool
            result = await session.call_tool(
                "query_policy_docs", arguments={"query": "my refund is broken"}
            )

            # 4. Print Result
            print("\nTool Output:")
            print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(run())
