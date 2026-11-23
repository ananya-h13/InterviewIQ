from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

print("\nAVAILABLE GEMINI MODELS\n")

for model in client.models.list():
    actions = model.supported_actions or []

    if "generateContent" in actions:
        print("Model:", model.name)
        print("Supported actions:", actions)
        print("-" * 50)