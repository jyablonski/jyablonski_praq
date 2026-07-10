from __future__ import annotations

from copy import deepcopy
from typing import Any


ALLOWED_FILTER_OPERATORS = {
    "afterDate",
    "beforeDate",
    "contains",
    "equals",
    "gt",
    "gte",
    "inDateRange",
    "lt",
    "lte",
    "notEquals",
    "notInDateRange",
    "notSet",
    "set",
}
ALLOWED_GRANULARITIES = {"day", "week", "month", "quarter", "year"}
ALLOWED_QUERY_KEYS = {
    "dimensions",
    "filters",
    "limit",
    "measures",
    "order",
    "timeDimensions",
    "timezone",
}


class PolicyViolation(ValueError):
    """Raised when an agent-generated query is outside the governed surface."""


def _public_members(meta: dict[str, Any]) -> tuple[set[str], set[str], set[str]]:
    measures: set[str] = set()
    dimensions: set[str] = set()
    time_dimensions: set[str] = set()

    for cube in meta.get("cubes", []):
        if not cube.get("public", True) or not cube.get("isVisible", True):
            continue

        for measure in cube.get("measures", []):
            if measure.get("public", True) and measure.get("isVisible", True):
                measures.add(measure["name"])

        for dimension in cube.get("dimensions", []):
            if dimension.get("public", True) and dimension.get("isVisible", True):
                dimensions.add(dimension["name"])
                if dimension.get("type") == "time":
                    time_dimensions.add(dimension["name"])

    return measures, dimensions, time_dimensions


def validate_and_normalize_query(
    query: dict[str, Any],
    meta: dict[str, Any],
    *,
    max_rows: int,
) -> dict[str, Any]:
    """Validate a structured Cube query and apply hard POC limits.

    Structured Cube REST queries cannot express DDL or DML, so this allowlist is
    the read-only boundary instead of attempting to sanitize arbitrary SQL.
    """
    if not isinstance(query, dict):
        raise PolicyViolation("Query must be a JSON object")

    unknown_keys = set(query) - ALLOWED_QUERY_KEYS
    if unknown_keys:
        raise PolicyViolation(f"Unsupported query fields: {sorted(unknown_keys)}")

    normalized = deepcopy(query)
    public_measures, public_dimensions, public_time_dimensions = _public_members(meta)

    measures = normalized.get("measures", [])
    dimensions = normalized.get("dimensions", [])
    time_dimensions = normalized.get("timeDimensions", [])
    filters = normalized.get("filters", [])

    if not isinstance(measures, list) or not 1 <= len(measures) <= 3:
        raise PolicyViolation("Queries must contain between one and three measures")
    if not isinstance(dimensions, list) or len(dimensions) > 3:
        raise PolicyViolation("Queries may contain at most three dimensions")
    if not isinstance(time_dimensions, list) or len(time_dimensions) > 1:
        raise PolicyViolation("Queries may contain at most one time dimension")
    if not isinstance(filters, list) or len(filters) > 5:
        raise PolicyViolation("Queries may contain at most five filters")

    for measure in measures:
        if measure not in public_measures:
            raise PolicyViolation(f"Unknown or non-public measure: {measure}")
    for dimension in dimensions:
        if dimension not in public_dimensions:
            raise PolicyViolation(f"Unknown or non-public dimension: {dimension}")

    for time_dimension in time_dimensions:
        if not isinstance(time_dimension, dict):
            raise PolicyViolation("Time dimensions must be objects")
        if set(time_dimension) - {"dateRange", "dimension", "granularity"}:
            raise PolicyViolation("Unsupported time dimension fields")
        member = time_dimension.get("dimension")
        if member not in public_time_dimensions:
            raise PolicyViolation(f"Unknown or non-public time dimension: {member}")
        granularity = time_dimension.get("granularity")
        if granularity not in ALLOWED_GRANULARITIES:
            raise PolicyViolation(f"Unsupported time granularity: {granularity}")
        date_range = time_dimension.get("dateRange")
        if date_range is not None:
            if not isinstance(date_range, list) or len(date_range) != 2:
                raise PolicyViolation("dateRange must contain a start and end date")
            if not all(
                isinstance(value, str) and len(value) <= 32 for value in date_range
            ):
                raise PolicyViolation("dateRange values must be short date strings")

    all_filterable_members = public_measures | public_dimensions
    for query_filter in filters:
        if not isinstance(query_filter, dict):
            raise PolicyViolation("Filters must be objects")
        if set(query_filter) - {"member", "operator", "values"}:
            raise PolicyViolation("Unsupported filter fields")
        member = query_filter.get("member")
        operator = query_filter.get("operator")
        values = query_filter.get("values", [])
        if member not in all_filterable_members:
            raise PolicyViolation(f"Unknown or non-public filter member: {member}")
        if operator not in ALLOWED_FILTER_OPERATORS:
            raise PolicyViolation(f"Unsupported filter operator: {operator}")
        if not isinstance(values, list) or len(values) > 20:
            raise PolicyViolation("Filters may contain at most 20 values")
        if not all(isinstance(value, str) and len(value) <= 128 for value in values):
            raise PolicyViolation("Filter values must be short strings")

    selected_members = set(measures) | set(dimensions)
    selected_members.update(item["dimension"] for item in time_dimensions)
    order = normalized.get("order", {})
    if not isinstance(order, dict) or len(order) > 2:
        raise PolicyViolation("Order must be an object with at most two members")
    for member, direction in order.items():
        if member not in selected_members:
            raise PolicyViolation(
                f"Order member must be selected in the query: {member}"
            )
        if direction not in {"asc", "desc"}:
            raise PolicyViolation(f"Unsupported order direction: {direction}")

    requested_limit = normalized.get("limit", max_rows)
    if not isinstance(requested_limit, int) or requested_limit < 1:
        raise PolicyViolation("Limit must be a positive integer")
    normalized["limit"] = min(requested_limit, max_rows)
    normalized["timezone"] = "UTC"
    normalized.setdefault("dimensions", [])
    normalized.setdefault("filters", [])
    normalized.setdefault("timeDimensions", [])

    return normalized
