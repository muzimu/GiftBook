from os import getenv
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

client = OpenAI(
    api_key = getenv('api_key'),
    base_url = getenv('base_url'),
)

messages = [
        {
            "role": "user",
            "content": "hello",
        }
    ]
completion = client.chat.completions.create(
        model=getenv('model'),
        messages=messages,
    )

print(completion)