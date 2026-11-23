
from modules.report_generator import generate_feedback_report

sample_evaluations = [
    {
        "correctness": 4,
        "clarity": 4,
        "depth": 3,
        "strengths": ["Good understanding of Python"],
        "weaknesses": ["Needs more examples"],
        "improvement_tips": ["Explain concepts with examples"],
        "overall_feedback": "Good answer with room for improvement"
    },
    {
        "correctness": 5,
        "clarity": 4,
        "depth": 4,
        "strengths": ["Accurate explanation"],
        "weaknesses": ["Could be more detailed"],
        "improvement_tips": ["Add practical examples"],
        "overall_feedback": "Strong answer"
    },
    {
        "correctness": 4,
        "clarity": 3,
        "depth": 4,
        "strengths": ["Understands the concept"],
        "weaknesses": ["Explanation could be clearer"],
        "improvement_tips": ["Structure the answer better"],
        "overall_feedback": "Good technical understanding"
    },
    {
        "correctness": 3,
        "clarity": 4,
        "depth": 3,
        "strengths": ["Communicates confidently"],
        "weaknesses": ["Some technical gaps"],
        "improvement_tips": ["Revise core concepts"],
        "overall_feedback": "Average answer"
    },
    {
        "correctness": 5,
        "clarity": 5,
        "depth": 4,
        "strengths": ["Excellent explanation"],
        "weaknesses": ["Could include another example"],
        "improvement_tips": ["Continue practising"],
        "overall_feedback": "Very good answer"
    }
]

report = generate_feedback_report(
    role="Python Developer",
    evaluations=sample_evaluations
)

print("\nFINAL INTERVIEW REPORT")
print("----------------------")
print(report.model_dump_json(indent=4))
