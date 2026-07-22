import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("API_BASE_URL")

if not BASE_URL:
    raise ValueError("API_BASE_URL is not set in .env")

URL = f"{BASE_URL.rstrip('/')}/events/bulk"

with open("sample_events.json", "r") as f:
    events = json.load(f)

response = requests.post(URL, json=events)

print(f"Status Code: {response.status_code}")
print(response.json())