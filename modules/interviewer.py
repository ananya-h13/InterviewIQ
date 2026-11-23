
import time

from google import genai
from google.genai.errors import ServerError

from config import GEMINI_API_KEY, MODEL_NAME

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={"timeout": 30000}
)


def generate_followup(role, question, answer):

    prompt = f"""
You are an intelligent AI interviewer.

Job Role: {role}

Previous Question:
{question}

Candidate's Answer:
{answer}

Generate ONE relevant follow-up question based
on the candidate's answer.

Instructions:
1. Identify a concept that needs deeper exploration.
2. Test the candidate's understanding.
3. Do not repeat the original question.
4. Keep it relevant to the selected role.
5. Return ONLY the follow-up question.
"""

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response.")

            return response.text.strip()

        except ServerError as error:

            if error.code == 503 and attempt < 2:

                wait_time = 2 ** (attempt + 1)

                print(
                    f"Gemini is busy. Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:
                raise
