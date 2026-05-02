import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

models_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash-exp",
    "gemini-1.5-pro",
]

for model in models_to_test:
    print(f"Testing {model}...")
    try:
        response = client.models.generate_content(
            model=model,
            contents="hi",
            config={'tools': [{'google_search': {}}]}
        )
        print(f"  SUCCESS: {response.text[:50]}")
    except Exception as e:
        print(f"  FAILED: {str(e)[:100]}")
