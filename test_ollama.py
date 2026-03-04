import requests
import json
import sys

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"

prompt = "Extract city and state from 'I live in Chicago, IL' into JSON."
schema = {
  "type": "object",
  "properties": {
    "city": {"type": "string"},
    "state": {"type": "string"}
  }
}

payload_schema = {
    "model": MODEL_NAME,
    "prompt": prompt,
    "format": schema,
    "stream": False,
}

payload_json = {
    "model": MODEL_NAME,
    "prompt": prompt,
    "format": "json",
    "stream": False,
}

print("Testing with schema...")
try:
    res1 = requests.post(OLLAMA_URL, json=payload_schema, timeout=60)
    print("Schema status:", res1.status_code)
    print("Schema response:", res1.text[:200])
except Exception as e:
    print("Schema error:", e)

print("\nTesting with lit 'json'...")
try:
    res2 = requests.post(OLLAMA_URL, json=payload_json, timeout=60)
    print("JSON literal status:", res2.status_code)
    print("JSON literal response:", res2.text[:200])
except Exception as e:
    print("JSON literal error:", e)
