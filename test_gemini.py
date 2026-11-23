from google import genai
from config import GEMINI_API_KEY, MODEL_NAME

client = genai.Client(api_key=GEMINI_API_KEY)

try:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents="Explain Python lists in two sentences."
    )

    print(response.text)

except Exception as e:
    print("Error:", type(e).__name__)
    print("Details:", str(e))