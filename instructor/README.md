# Instructor

Instructor is a Python Package that is designed to simplify structured outputs from LLMs by enabling automatic parsing of model responses into Pydantic models that you've defined.

Instead of handling raw JSON responses, Instructor ensures that these responses are structured directly in the Pydantic model you've defined. 

Pros:

- No need to manually parse JSON responses
- Reduces LLM hallucinations by enforcing strict response formatting
- Ideal for structured applications like APIs, chatbots, and automation

``` py
import openai
import instructor
from pydantic import BaseModel

# Initialize OpenAI with Instructor wrapper
client = instructor.from_openai(openai.Client())

# Define a structured response model
class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    steps: list[str]

# Call the LLM with structured output
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": "Give me a simple pancake recipe"}],
    response_model=Recipe  # Instructor ensures output is structured as Recipe
)

print(response)

# {
#     "name": "Classic Pancakes",
#     "ingredients": ["1 cup flour", "1 egg", "1 cup milk", "1 tbsp sugar"],
#     "steps": [
#         "Mix all ingredients in a bowl.",
#         "Heat a pan over medium heat.",
#         "Pour batter onto the pan and cook until golden brown."
#     ]
# }
```