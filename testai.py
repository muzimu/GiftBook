from os import getenv
from dotenv import load_dotenv
import requests
load_dotenv()
url = "https://openai.qiniu.com/v1/chat/completions"
headers = {
    "Authorization": "Bearer " + getenv("api_key"),
    "Content-Type": "application/json"
}
payload = {
    "stream": False,
    "model": "moonshotai/kimi-k2-0905",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello!"
        }
    ]
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())