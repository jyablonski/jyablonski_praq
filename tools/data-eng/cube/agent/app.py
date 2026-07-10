from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

from policies import PolicyViolation
from prompts import SYSTEM_PROMPT
from tools import TOOL_SCHEMAS, CubeTools


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)
    user_context: dict[str, Any] = Field(default_factory=dict)
    include_trace: bool = True


class AskResponse(BaseModel):
    answer: str
    tool_calls: int
    trace: list[dict[str, Any]] | None = None


app = FastAPI(title="Cube Analytics Agent POC", version="0.1.0")
cube_tools = CubeTools()


def _run_agent(request: AskRequest) -> AskResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not configured; set it before calling /ask",
        )

    model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    max_tool_calls = int(os.getenv("AGENT_MAX_TOOL_CALLS", "5"))
    client = OpenAI(api_key=api_key)
    trace: list[dict[str, Any]] = []
    tool_call_count = 0

    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=request.question,
        tools=TOOL_SCHEMAS,
    )

    while True:
        function_calls = [
            item for item in response.output if item.type == "function_call"
        ]
        if not function_calls:
            answer = response.output_text.strip()
            if not answer:
                raise RuntimeError(
                    "The model returned neither a tool call nor an answer"
                )
            return AskResponse(
                answer=answer,
                tool_calls=tool_call_count,
                trace=trace if request.include_trace else None,
            )

        tool_outputs = []
        for call in function_calls:
            tool_call_count += 1
            if tool_call_count > max_tool_calls:
                raise PolicyViolation(f"Tool-call budget exceeded ({max_tool_calls})")

            arguments = json.loads(call.arguments)
            try:
                if call.name == "run_semantic_query":
                    searched = any(
                        item["tool"] == "search_semantic_model" and item["output"]["ok"]
                        for item in trace
                    )
                    defined_metrics = {
                        item["arguments"]["metric_name"]
                        for item in trace
                        if item["tool"] == "get_metric_definition"
                        and item["output"]["ok"]
                    }
                    missing_definitions = (
                        set(arguments.get("measures", [])) - defined_metrics
                    )
                    if not searched:
                        raise PolicyViolation(
                            "Search the semantic model before querying"
                        )
                    if missing_definitions:
                        raise PolicyViolation(
                            "Load metric definitions before querying: "
                            f"{sorted(missing_definitions)}"
                        )

                result = cube_tools.dispatch(
                    call.name,
                    arguments,
                    user_context=request.user_context,
                )
                output: dict[str, Any] = {"ok": True, "result": result}
            except (PolicyViolation, ValueError, KeyError) as exc:
                output = {"ok": False, "error": str(exc)}

            trace.append({"tool": call.name, "arguments": arguments, "output": output})
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(output, default=str),
                }
            )

        response = client.responses.create(
            model=model,
            instructions=SYSTEM_PROMPT,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=TOOL_SCHEMAS,
        )


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "llm_configured": bool(os.getenv("OPENAI_API_KEY")),
        "model": os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
    }


@app.get("/evaluations")
def evaluations() -> dict[str, Any]:
    path = Path(__file__).with_name("evaluations.yml")
    return yaml.safe_load(path.read_text())


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        return _run_agent(request)
    except HTTPException:
        raise
    except PolicyViolation as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Agent request failed: {exc}"
        ) from exc
