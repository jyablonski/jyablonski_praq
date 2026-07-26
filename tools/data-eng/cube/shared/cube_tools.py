from __future__ import annotations

import json
import os
import re
from typing import Any
from uuid import uuid4

import httpx

from .policies import validate_and_normalize_query


class CubeTools:
    """Shared, policy-aware client for Cube's metadata and REST APIs."""

    def __init__(self) -> None:
        self.base_url = os.getenv("CUBE_API_URL", "http://cube:4000").rstrip("/")
        self.max_rows = int(os.getenv("AGENT_MAX_ROWS", "100"))
        self.timeout_seconds = float(os.getenv("AGENT_QUERY_TIMEOUT_SECONDS", "15"))

    def _client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, timeout=self.timeout_seconds)

    def get_meta(self) -> dict[str, Any]:
        with self._client() as client:
            response = client.get("/cubejs-api/v1/meta")
            response.raise_for_status()
            return response.json()

    @staticmethod
    def _visible_members(meta: dict[str, Any]) -> list[dict[str, Any]]:
        members: list[dict[str, Any]] = []
        for cube in meta.get("cubes", []):
            if not cube.get("public", True) or not cube.get("isVisible", True):
                continue
            for member_type in ("measures", "dimensions"):
                for member in cube.get(member_type, []):
                    if not member.get("public", True) or not member.get(
                        "isVisible", True
                    ):
                        continue
                    members.append(
                        {
                            "name": member["name"],
                            "kind": member_type.removesuffix("s"),
                            "title": member.get("shortTitle") or member.get("title"),
                            "description": member.get("description"),
                            "type": member.get("type"),
                            "format": member.get("format"),
                            "meta": member.get("meta", {}),
                            "cube": cube["name"],
                        }
                    )
        return members

    def search_semantic_model(self, question: str) -> dict[str, Any]:
        meta = self.get_meta()
        members = self._visible_members(meta)
        tokens = {
            token
            for token in re.findall(r"[a-z0-9_]+", question.lower())
            if len(token) >= 3
        }

        scored: list[tuple[int, dict[str, Any]]] = []
        for member in members:
            haystack = " ".join(
                str(member.get(key) or "")
                for key in ("name", "title", "description", "kind", "cube")
            ).lower()
            score = sum(1 for token in tokens if token in haystack)
            if score:
                scored.append((score, member))

        matches = [member for _, member in sorted(scored, key=lambda item: -item[0])]
        if not matches:
            matches = members

        return {"members": matches[:12], "total_public_members": len(members)}

    def get_metric_definition(self, metric_name: str) -> dict[str, Any]:
        measures = [
            member
            for member in self._visible_members(self.get_meta())
            if member["kind"] == "measure"
        ]
        exact = [member for member in measures if member["name"] == metric_name]
        if not exact and "." not in metric_name:
            exact = [
                member
                for member in measures
                if member["name"].endswith(f".{metric_name}")
            ]
        if len(exact) != 1:
            raise ValueError(f"Unknown or ambiguous public metric: {metric_name}")
        return exact[0]

    def run_semantic_query(
        self,
        *,
        measures: list[str],
        dimensions: list[str],
        time_dimension: dict[str, Any] | None,
        filters: list[dict[str, Any]],
        order_by: str | None,
        order_direction: str,
        row_limit: int,
        user_context: dict[str, Any],
    ) -> dict[str, Any]:
        query: dict[str, Any] = {
            "measures": measures,
            "dimensions": dimensions,
            "filters": filters,
            "limit": row_limit,
        }
        if time_dimension:
            cube_time_dimension: dict[str, Any] = {
                "dimension": time_dimension["dimension"],
                "granularity": time_dimension["granularity"],
            }
            if time_dimension.get("date_range"):
                cube_time_dimension["dateRange"] = time_dimension["date_range"]
            query["timeDimensions"] = [cube_time_dimension]
        if order_by:
            query["order"] = {order_by: order_direction}

        query = validate_and_normalize_query(
            query, self.get_meta(), max_rows=self.max_rows
        )
        request_id = str(uuid4())
        with self._client() as client:
            response = client.get(
                "/cubejs-api/v1/load",
                params={"query": json.dumps(query, separators=(",", ":"))},
                headers={"X-Request-ID": request_id},
            )
            response.raise_for_status()
            payload = response.json()

        return {
            "request_id": payload.get("requestId", request_id),
            "query": query,
            "data": payload.get("data", []),
            "last_refresh_time": payload.get("lastRefreshTime"),
            "row_count": len(payload.get("data", [])),
            "user_context_supplied": bool(user_context),
        }
