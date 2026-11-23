
from modules.evaluator import evaluate_answer

role = "Python Developer"

question = "What is the difference between a list and a tuple in Python?"

answer = """
A list is mutable, which means we can modify its elements
after creating it. A tuple is immutable, so its elements
cannot be changed after creation. Lists use square brackets
while tuples use parentheses.
"""

print("\nEvaluating candidate answer...\n")

result = evaluate_answer(
    role=role,
    question=question,
    answer=answer
)

print("INTERVIEWIQ EVALUATION")
print("----------------------")

print(result.model_dump_json(indent=4))

print("\nOVERALL RESULT")
print("Correctness:", result.correctness, "/5")
print("Clarity:", result.clarity, "/5")
print("Depth:", result.depth, "/5")
