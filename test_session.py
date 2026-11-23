
from modules.session_manager import create_interview_session

session = create_interview_session(
    role="Python Developer",
    total_questions=5
)

print("\nINTERVIEW SESSION CREATED")
print("-------------------------")

print("Role:", session["role"])
print("Total Questions:", len(session["questions"]))

print("\nSELECTED QUESTIONS:\n")

for index, question in enumerate(session["questions"], start=1):
    print(f"{index}. [{question['type']}] {question['question']}")

print("\nSESSION STATUS:")
print("Current Question:", session["current_question"] + 1)
print("Completed:", session["completed"])
