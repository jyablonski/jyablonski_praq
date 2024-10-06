import os

import anthropic

# need to add a credit card to make requests
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

model_name = "claude-3-5-sonnet-20240620"

message = client.messages.create(
    model=model_name,
    max_tokens=1000,
    temperature=0,
    system="You are a world-class poet. Respond only with short poems.",
    messages=[
        {
            "role": "user",
            "content": [{"type": "text", "text": "Why is the ocean salty?"}],
        }
    ],
)
print(message.content)


# this returns the exact usage for a given request
print(message.usage)
