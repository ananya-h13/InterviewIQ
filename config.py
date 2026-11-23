
import os
from dotenv import load_dotenv

load_dotenv()


def get_gemini_api_key():

    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        return api_key

    try:
        import streamlit as st
        return st.secrets["GEMINI_API_KEY"]

    except Exception:
        return None


GEMINI_API_KEY = get_gemini_api_key()

MODEL_NAME = "gemini-3.5-flash-lite"

if not GEMINI_API_KEY:
    raise ValueError(
        "Gemini API key not found. "
        "Configure GEMINI_API_KEY in .env or Streamlit Secrets."
    )
