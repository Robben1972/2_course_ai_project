from environs import Env

env = Env()
env.read_env()
from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Hello."
        }
    ]
)

print(completion.choices[0].message)
