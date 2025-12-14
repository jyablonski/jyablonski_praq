"""Main script demonstrating XML prompt compilation with instructor."""

import instructor
from pydantic import BaseModel, Field

from prompt_template.models import PromptContext, PromptVariables, DataAnalysisInput
from prompt_template.compiler import TemplateCompiler

DEFAULT_MODEL = "gpt-5-nano"


# Define structured output model for the LLM response
class AnalysisResponse(BaseModel):
    """Structured response from the data analysis."""

    summary: str = Field(description="Brief summary of findings")
    insights: list[str] = Field(description="Key insights from the analysis")
    recommendations: list[str] = Field(description="Actionable recommendations")
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")


class PromptClient:
    """Client for running compiled prompts through an LLM."""

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.client = instructor.from_provider(model=f"openai/{model}")
        self.compiler = TemplateCompiler(templates_dir="prompts")

    def run_analysis(
        self, analysis_input: DataAnalysisInput, context: PromptContext
    ) -> AnalysisResponse:
        """
        Compile the prompt template and run it through the LLM.

        Uses instructor for structured output validation.
        """
        # Prepare variables from the analysis input
        variables = PromptVariables(
            variables={
                "dataset_description": analysis_input.dataset_description,
                "columns": analysis_input.columns,
                "sample_rows": analysis_input.sample_rows,
                "output_format": analysis_input.output_format,
            }
        )

        # Compile the prompt
        compiled_prompt = self.compiler.compile(
            template_name="data_analyst",
            context=context,
            variables=variables,
            user_query=analysis_input.analysis_goal,
        )

        print("=" * 60)
        print("COMPILED PROMPT:")
        print("=" * 60)
        print(compiled_prompt)
        print("=" * 60)

        # Build system prompt from context
        system_prompt = self._build_system_prompt(context)

        # Call the LLM with structured output
        response = self.client.chat.completions.create(
            model=self.model,
            response_model=AnalysisResponse,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": compiled_prompt},
            ],
            max_retries=2,
        )

        return response

    def _build_system_prompt(self, context: PromptContext) -> str:
        """Build a system prompt from the context."""
        parts = [f"You are a {context.role}."]

        if context.expertise:
            parts.append(f"Your areas of expertise: {', '.join(context.expertise)}.")

        if context.constraints:
            parts.append("Guidelines: " + "; ".join(context.constraints) + ".")

        return " ".join(parts)


def main():
    # Define the LLM context/persona
    context = PromptContext(
        role="Senior Data Analyst specializing in e-commerce metrics",
        expertise=[
            "Statistical analysis",
            "Revenue optimization",
            "Customer behavior analysis",
            "SQL and Python",
        ],
        constraints=[
            "Base conclusions only on provided data",
            "Acknowledge limitations and uncertainties",
            "Provide actionable recommendations",
        ],
    )

    # Define the analysis input
    analysis_input = DataAnalysisInput(
        dataset_description="E-commerce sales transactions for Q4 2024",
        columns=[
            "transaction_id",
            "date",
            "product_category",
            "revenue",
            "quantity",
            "customer_segment",
        ],
        sample_rows=[
            {
                "transaction_id": "T001",
                "date": "2024-10-01",
                "product_category": "Electronics",
                "revenue": 299.99,
                "quantity": 1,
                "customer_segment": "Premium",
            },
            {
                "transaction_id": "T002",
                "date": "2024-10-01",
                "product_category": "Clothing",
                "revenue": 89.50,
                "quantity": 2,
                "customer_segment": "Standard",
            },
            {
                "transaction_id": "T003",
                "date": "2024-10-02",
                "product_category": "Electronics",
                "revenue": 599.99,
                "quantity": 1,
                "customer_segment": "Premium",
            },
            {
                "transaction_id": "T004",
                "date": "2024-10-02",
                "product_category": "Home",
                "revenue": 45.00,
                "quantity": 3,
                "customer_segment": "Budget",
            },
        ],
        analysis_goal="Identify which product categories and customer segments drive the most revenue, and suggest strategies to increase sales.",
        output_format="markdown",
    )

    # Initialize client and run analysis
    client = PromptClient()
    result = client.run_analysis(analysis_input, context)

    # # Display results
    print("\n" + "=" * 60)
    print("STRUCTURED RESPONSE:")
    print("=" * 60)
    print(f"\nSummary: {result.summary}")
    print(f"\nConfidence: {result.confidence:.0%}")
    print("\nInsights:")
    for i, insight in enumerate(result.insights, 1):
        print(f"  {i}. {insight}")
    print("\nRecommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i}. {rec}")


if __name__ == "__main__":
    main()
