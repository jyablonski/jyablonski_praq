import os

import instructor
from pydantic import BaseModel
import google.generativeai as genai

# https://aistudio.google.com/app/apikey


class ReviewInfo(BaseModel):
    topics: list[str]
    company: str
    product: str


review_text = """I love the camera quality of this iPhone, but the battery life is disappointing.
The screen is sharp and responsive, but the phone heats up quickly."""


# models/gemini-1.5-flash-latest
def setup_gemini_client(model_name: str):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    client = instructor.from_gemini(
        client=genai.GenerativeModel(
            model_name=model_name,
        ),
        mode=instructor.Mode.GEMINI_JSON,
    )

    return client


def generate_client_response(
    client: instructor.AsyncInstructor, prompt: str, response_model: BaseModel
) -> dict[str, str]:
    response = client.chat.completions.create(
        response_model=response_model,
        messages=[
            {
                "role": "user",
                "content": (prompt),
            }
        ],
    )

    return response.dict()


client = setup_gemini_client("models/gemini-1.5-flash-latest")
prompt = (
    "Please extract the product and company name, along with any notable topics from this review.\n\n"
    f"{review_text}"
)

review_attrs = generate_client_response(
    client=client, prompt=prompt, response_model=ReviewInfo
)
