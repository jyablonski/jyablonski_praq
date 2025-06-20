import instructor
from pydantic import BaseModel
from openai import OpenAI

# https://aistudio.google.com/app/apikey


# Define your desired output structure
class UserInfo(BaseModel):
    name: str
    age: int


# specify the LLM provider to use here
client = instructor.from_openai(OpenAI())

# making requests then looks the same regardless of what provider you use
user_info = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=UserInfo,
    messages=[{"role": "user", "content": "John Doe is 30 years old."}],
)

print(user_info.name)
# > John Doe
print(user_info.age)
# > 30
