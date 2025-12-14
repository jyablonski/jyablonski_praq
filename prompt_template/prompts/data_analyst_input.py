# from pydantic import BaseModel, Field


# # Example: Data analysis specific input
# class DataAnalysisInput(BaseModel):
#     """Input specifically for data analysis prompts."""

#     dataset_description: str = Field(description="Description of the dataset")
#     columns: list[str] = Field(description="Column names in the dataset")
#     sample_rows: list[dict] = Field(
#         default_factory=list, description="Sample data rows"
#     )
#     analysis_goal: str = Field(description="What the user wants to analyze")
#     output_format: str = Field(default="markdown", description="Desired output format")
