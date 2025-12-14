"""Pydantic models for prompt template input validation."""

from pydantic import BaseModel, Field
from typing import Any


class PromptContext(BaseModel):
    """Context/expertise information for the LLM."""

    role: str = Field(description="The role or persona the LLM should adopt")
    expertise: list[str] = Field(default_factory=list, description="Areas of expertise")
    constraints: list[str] = Field(
        default_factory=list, description="Constraints or rules to follow"
    )


class PromptVariables(BaseModel):
    """Variables to substitute into the prompt template."""

    variables: dict[str, Any] = Field(
        default_factory=dict, description="Key-value pairs for substitution"
    )

    def get(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)


class PromptInput(BaseModel):
    """Complete input for prompt compilation."""

    template_name: str = Field(description="Name of the XML template to use")
    context: PromptContext = Field(description="Context for the LLM")
    variables: PromptVariables = Field(
        description="Variables for template substitution"
    )
    user_query: str = Field(description="The actual user query/task")


# move this into the prompts folder in a production setting for better organization
class DataAnalysisInput(BaseModel):
    """Input specifically for data analysis prompts."""

    dataset_description: str = Field(description="Description of the dataset")
    columns: list[str] = Field(description="Column names in the dataset")
    sample_rows: list[dict] = Field(
        default_factory=list, description="Sample data rows"
    )
    analysis_goal: str = Field(description="What the user wants to analyze")
    output_format: str = Field(default="markdown", description="Desired output format")
