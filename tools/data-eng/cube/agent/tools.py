TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "search_semantic_model",
        "description": "Find public Cube measures and dimensions relevant to a stakeholder question.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The stakeholder question or concepts to search for.",
                }
            },
            "required": ["question"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_metric_definition",
        "description": "Return the governed definition and metadata for a public Cube measure.",
        "parameters": {
            "type": "object",
            "properties": {
                "metric_name": {
                    "type": "string",
                    "description": "Fully qualified measure name, such as orders.monthly_revenue.",
                }
            },
            "required": ["metric_name"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "run_semantic_query",
        "description": "Run a read-only structured query against Cube's governed REST API.",
        "parameters": {
            "type": "object",
            "properties": {
                "measures": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "One to three fully qualified public measure names.",
                },
                "dimensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Zero to three fully qualified public dimension names.",
                },
                "time_dimension": {
                    "anyOf": [
                        {
                            "type": "object",
                            "properties": {
                                "dimension": {"type": "string"},
                                "granularity": {
                                    "type": "string",
                                    "enum": ["day", "week", "month", "quarter", "year"],
                                },
                                "date_range": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 2,
                                    "maxItems": 2,
                                },
                            },
                            "required": ["dimension", "granularity"],
                            "additionalProperties": False,
                        },
                        {"type": "null"},
                    ],
                    "description": "Optional time dimension, grain, and inclusive date range.",
                },
                "filters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "member": {"type": "string"},
                            "operator": {"type": "string"},
                            "values": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["member", "operator", "values"],
                        "additionalProperties": False,
                    },
                },
                "order_by": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": "Selected member to order by, or null.",
                },
                "order_direction": {"type": "string", "enum": ["asc", "desc"]},
                "row_limit": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            "required": [
                "measures",
                "dimensions",
                "time_dimension",
                "filters",
                "order_by",
                "order_direction",
                "row_limit",
            ],
            "additionalProperties": False,
        },
    },
]
