# Prompt Template Compiler

A Python script for compiling XML prompt templates with variable substitution, using Pydantic for input validation and Instructor for structured LLM outputs.

## Overview

This lets you:

- Define reusable prompt templates in XML to give context to LLM
- Validate inputs with Pydantic models
- Substitute XML variables w/ input data you curate
- Get structured, validated responses from LLMs via Instructor

## Use Cases

1. Article Summarization
1. Email Drafting
1. Meeting Notes -> Action Items
1. Surveys
1. Customer Feedback
1. Report Generation

## Running

Set your API key before running:

```sh
export OPENAI_API_KEY=sk-...
python -m prompt_template.main
```

## Project Structure

```
prompt_template/
├── prompts/
│   └── data_analyst.xml    # XML prompt templates
├── compiler.py             # Template loading and variable substitution
├── models.py               # Pydantic models for input validation
├── main.py                 # Example usage with Instructor
```

## Usage

### 1. Define an XML Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt_template name="data_analyst">
    <context>
        <role>{{role}}</role>
        <expertise>
            {{#expertise}}
            <area>{{.}}</area>
            {{/expertise}}
        </expertise>
    </context>

    <task>
        <dataset>
            <description>{{dataset_description}}</description>
        </dataset>
        <user_query>{{user_query}}</user_query>
    </task>
</prompt_template>
```

### 2. Define Pydantic Models

```python
from pydantic import BaseModel, Field

class AnalysisResponse(BaseModel):
    summary: str = Field(description="Brief summary of findings")
    insights: list[str] = Field(description="Key insights")
    confidence: float = Field(ge=0, le=1)
```

### 3. Compile and Run

```python
import instructor
from compiler import TemplateCompiler
from models import PromptContext, PromptVariables

# Init client - note the provider/model split
client = instructor.from_provider(model="openai/gpt-4o")
compiler = TemplateCompiler(templates_dir="prompts")

# Define context
context = PromptContext(
    role="Senior Data Analyst",
    expertise=["SQL", "Python", "Statistics"],
    constraints=["Be concise"]
)

# Define variables
variables = PromptVariables(variables={
    "dataset_description": "Sales data Q4 2024",
    "columns": ["date", "revenue", "product"],
})

# Compile the prompt
compiled = compiler.compile(
    template_name="data_analyst",
    context=context,
    variables=variables,
    user_query="What are the top products?"
)

# Call LLM with structured output
response = client.chat.completions.create(
    model="gpt-4o",  # just the model name, no provider prefix
    response_model=AnalysisResponse,
    messages=[
        {"role": "system", "content": "You are a data analyst."},
        {"role": "user", "content": compiled},
    ],
)

print(response.summary)
```

## Template Syntax

| Syntax | Description | Example |
| ------------------------------- | ------------------- | ------------------------------ |
| `{{variable}}` | Simple substitution | `{{role}}` -> `"Data Analyst"` |
| `{{#list}}...{{.}}...{{/list}}` | List iteration | Iterates over list items |

## Key Files

### `models.py`

- `PromptContext` - Role, expertise, and constraints for the LLM
- `PromptVariables` - Key-value pairs for template substitution
- `DataAnalysisInput` - Domain-specific input model example

### `compiler.py`

- `TemplateCompiler` - Loads XML templates and handles substitution
- Supports simple variables and list iteration
- Resolves paths relative to the module location

### `main.py`

- `PromptClient` - Wraps Instructor client with template compilation
- Example usage with data analysis prompt
