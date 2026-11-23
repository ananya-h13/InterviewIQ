
from modules.interviewer import generate_followup

role = "Python Developer"

question = "What is the difference between a list and a tuple in Python?"

answer = """
A list is mutable, which means we can modify its elements.
A tuple is immutable, so its elements cannot be changed
after creation.
"""

print("\nGenerating AI follow-up question...\n")

followup = generate_followup(
    role=role,
    question=question,
    answer=answer
)

print("ORIGINAL QUESTION:")
print(question)

print("\nCANDIDATE ANSWER:")
print(answer)

print("\nAI FOLLOW-UP QUESTION:")
print(followup)
