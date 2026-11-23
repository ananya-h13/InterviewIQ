
from database.db_manager import get_all_sessions

sessions = get_all_sessions()

print("\nSAVED INTERVIEW SESSIONS")
print("------------------------")

if sessions:
    for session in sessions:
        print("Session ID:", session["id"])
        print("Role:", session["role"])
        print("Date:", session["session_date"])
        print("Questions:", session["total_questions"])
        print("Correctness:", session["average_correctness"])
        print("Clarity:", session["average_clarity"])
        print("Depth:", session["average_depth"])
        print("Overall Score:", session["overall_score"])
        print("------------------------")
else:
    print("No saved sessions found.")
