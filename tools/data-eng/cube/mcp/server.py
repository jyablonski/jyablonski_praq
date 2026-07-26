from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from shared.cube_tools import CubeTools


mcp = FastMCP("cube-analytics", stateless_http=True, json_response=True)
cube_tools = CubeTools()


@mcp.tool()
def search_semantic_model(question: str) -> dict[str, Any]:
    """Find public Cube measures and dimensions relevant to a stakeholder question."""
    return cube_tools.search_semantic_model(question)


@mcp.tool()
def get_metric_definition(metric_name: str) -> dict[str, Any]:
    """Return the governed definition and metadata for a public Cube measure."""
    return cube_tools.get_metric_definition(metric_name)


@mcp.tool()
def run_semantic_query(
    measures: list[str],
    dimensions: list[str] | None = None,
    time_dimension: dict[str, Any] | None = None,
    filters: list[dict[str, Any]] | None = None,
    order_by: str | None = None,
    order_direction: str = "asc",
    row_limit: int = 100,
) -> dict[str, Any]:
    """Run a read-only, policy-validated query against Cube's REST API."""
    return cube_tools.run_semantic_query(
        measures=measures,
        dimensions=dimensions or [],
        time_dimension=time_dimension,
        filters=filters or [],
        order_by=order_by,
        order_direction=order_direction,
        row_limit=row_limit,
        user_context={},
    )


app = mcp.streamable_http_app()
