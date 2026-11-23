
from database.db_manager import (
    initialize_database,
    get_all_sessions
)

print("Initializing database...")

initialize_database()

print("Database initialized successfully!")

sessions = get_all_sessions()

print("\nEXISTING INTERVIEW SESSIONS")
print("---------------------------")

if sessions:
    for session in sessions:
        print(session)
else:
    print("No interview sessions found yet.")

print("\nDatabase test completed!")
