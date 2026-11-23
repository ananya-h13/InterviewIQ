import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-3.5-flash-lite"

if not GEMINI_API_KEY:
    raise ValueError("Gemini API key not found. Check your .env file.")