
import json
import time

from google import genai
from google.genai.errors import ServerError

from config import GEMINI_API_KEY, MODEL_NAME
from modules.schemas import AnswerEvaluation


client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={"timeout": 30000}
)


def evaluate_answer(role, question, answer):

    prompt = f"""
You are an experienced technical and HR interview evaluator.

Job Role: {role}
Question: {question}
Candidate Answer: {answer}

Evaluate the answer on:

1. Correctness (1-5): Factual and technical accuracy.
2. Clarity (1-5): Communication and logical explanation.
3. Depth (1-5): Completeness and understanding.

Scoring:
1 = Very poor
2 = Below average
3 = Average
4 = Good
5 = Excellent

For HR questions, evaluate relevance, communication
and depth instead of technical correctness.

Provide:
- correctness_feedback
- clarity_feedback
- depth_feedback
- strengths (list of strings)
- weaknesses (list of strings)
- improvement_tips (list of strings)
- overall_feedback

Be fair, specific and constructive.

Return ONLY valid JSON using these exact keys:
correctness, clarity, depth,
correctness_feedback, clarity_feedback, depth_feedback,
strengths, weaknesses, improvement_tips, overall_feedback.

All scores must be integers between 1 and 5.
"""

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if not response.text:
                raise ValueError("Gemini returned an empty evaluation.")

            result = response.text.strip()

            if result.startswith("```"):

                result = result.split("\n", 1)[1]
                result = result.rsplit("```", 1)[0].strip()

            data = json.loads(result)

            return AnswerEvaluation.model_validate(data)

        except ServerError as error:

            if error.code == 503 and attempt < 2:

                wait_time = 2 ** (attempt + 1)

                print(
                    f"Gemini is busy. Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:
                raise

        except (json.JSONDecodeError, ValueError) as error:

            raise ValueError(
                f"Gemini returned an invalid evaluation: {error}"
            ) from error
