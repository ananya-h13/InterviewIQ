
from pydantic import BaseModel, Field
from typing import List


class AnswerEvaluation(BaseModel):
    correctness: int = Field(
        ge=1,
        le=5,
        description="Score for factual and technical correctness"
    )

    clarity: int = Field(
        ge=1,
        le=5,
        description="Score for communication and explanation clarity"
    )

    depth: int = Field(
        ge=1,
        le=5,
        description="Score for detail and depth of understanding"
    )

    correctness_feedback: str
    clarity_feedback: str
    depth_feedback: str

    strengths: List[str]
    weaknesses: List[str]

    improvement_tips: List[str]

    overall_feedback: str


class InterviewReport(BaseModel):
    total_questions: int

    average_correctness: float
    average_clarity: float
    average_depth: float

    overall_score: float = Field(
        ge=1,
        le=5
    )

    strengths: List[str]
    weaknesses: List[str]

    recommendations: List[str]

    final_summary: str
