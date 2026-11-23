
import json
import random
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
QUESTION_FILE = BASE_DIR / "data" / "questions.json"


def load_questions(role):

    with open(QUESTION_FILE, "r", encoding="utf-8") as file:
        question_bank = json.load(file)

    if role not in question_bank:
        raise ValueError("Invalid interview role selected.")

    return question_bank[role]


def create_interview_session(role, total_questions=5):

    questions = load_questions(role)

    selected_questions = random.sample(
        questions,
        min(total_questions, len(questions))
    )

    return {
        "role": role,
        "questions": selected_questions,
        "current_question": 0,
        "answers": [],
        "evaluations": [],
        "followups": [],
        "completed": False
    }


def save_answer(session, question, answer, evaluation):

    session["answers"].append({
        "question": question,
        "answer": answer
    })

    session["evaluations"].append(
        evaluation.model_dump()
    )

    session["current_question"] += 1

    if session["current_question"] >= len(session["questions"]):
        session["completed"] = True

    return session


def save_followup(session, question):

    session["followups"].append(question)

    return session
