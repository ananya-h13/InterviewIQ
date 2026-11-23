
import json
import time

from google import genai
from google.genai.errors import ServerError

from config import GEMINI_API_KEY, MODEL_NAME
from modules.schemas import InterviewReport

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_feedback_report(role, evaluations):

    if not evaluations:
        raise ValueError("No evaluations available to generate a report.")

    total = len(evaluations)

    average_correctness = round(
        sum(item["correctness"] for item in evaluations) / total, 2
    )

    average_clarity = round(
        sum(item["clarity"] for item in evaluations) / total, 2
    )

    average_depth = round(
        sum(item["depth"] for item in evaluations) / total, 2
    )

    prompt = f"""
You are an experienced interview coach.

The candidate completed an interview for the role: {role}.

Here are the answer evaluations:
{json.dumps(evaluations, indent=2)}

The average scores are:
Correctness: {average_correctness}
Clarity: {average_clarity}
Depth: {average_depth}

Generate a constructive final interview feedback report.

Include:
- total_questions
- average_correctness
- average_clarity
- average_depth
- overall_score (average of the three average scores)
- strengths (list of strings)
- weaknesses (list of strings)
- recommendations (list of actionable strings)
- final_summary

Return ONLY valid JSON using these exact keys.
All scores must be between 1 and 5.
Be specific and base the report on the supplied evaluations.
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            result = response.text.strip()

            if result.startswith("```"):
                result = result.split("\n", 1)[1]
                result = result.rsplit("```", 1)[0].strip()

            data = json.loads(result)

            data["total_questions"] = total
            data["average_correctness"] = average_correctness
            data["average_clarity"] = average_clarity
            data["average_depth"] = average_depth

            return InterviewReport.model_validate(data)

        except ServerError as e:
            if e.code == 503 and attempt < 2:
                wait_time = 2 ** (attempt + 1)
                print(f"Gemini busy. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise

        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"Gemini returned an invalid report: {e}"
            ) from e
