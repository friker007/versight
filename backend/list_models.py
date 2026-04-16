from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Available Models (Unified SDK):")
try:
    for m in client.models.list():
        # The new SDK has different attributes, we'll just print the name
        print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
