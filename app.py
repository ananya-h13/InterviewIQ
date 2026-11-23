
import streamlit as st

from modules.session_manager import (
    create_interview_session,
    save_answer
)
from modules.evaluator import evaluate_answer
from modules.interviewer import generate_followup
from modules.report_generator import generate_feedback_report

from database.db_manager import (
    initialize_database,
    save_interview_session
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="InterviewIQ | AI Interview Coach",
    page_icon="🎯",
    layout="wide"
)

initialize_database()


# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------

defaults = {
    "session": None,
    "last_evaluation": None,
    "followup_question": None,
    "followup_evaluation": None,
    "awaiting_followup": False,
    "followup_evaluations": [],
    "final_report": None,
    "saved_session_id": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("InterviewIQ")

st.subheader("Your Personal AI Interview Coach")

st.write(
    "Practice technical and HR interviews, "
    "receive AI-powered feedback, and track your progress."
)

st.divider()


# --------------------------------------------------
# START INTERVIEW
# --------------------------------------------------

st.header("Start Your Interview")

if st.session_state.session is None:

    role = st.selectbox(
        "Choose your interview role",
        ["Python Developer", "Data Analyst"]
    )

    if st.button("Start Interview"):

        st.session_state.session = create_interview_session(
            role=role,
            total_questions=5
        )

        st.session_state.last_evaluation = None
        st.session_state.followup_question = None
        st.session_state.followup_evaluation = None
        st.session_state.awaiting_followup = False
        st.session_state.followup_evaluations = []
        st.session_state.final_report = None
        st.session_state.saved_session_id = None

        st.rerun()


# --------------------------------------------------
# ACTIVE INTERVIEW
# --------------------------------------------------

else:

    session = st.session_state.session

    st.success(f"Interview started for {session['role']}!")

    total_questions = len(session["questions"])
    current_index = session["current_question"]

    st.write(f"Total Questions: {total_questions}")

    # ----------------------------------------------
    # MAIN INTERVIEW QUESTION
    # ----------------------------------------------

    if not session["completed"]:

        question_data = session["questions"][current_index]

        st.progress(current_index / total_questions)

        st.write(
            f"Question {current_index + 1} of {total_questions}"
        )

        st.markdown(
            f"**Category:** {question_data['type'].upper()}"
        )

        st.subheader(question_data["question"])

        answer = st.text_area(
            "Type your answer here:",
            height=180,
            key=f"answer_{current_index}"
        )

        pending_key = f"pending_answer_{current_index}"

        # ------------------------------------------
        # SUBMIT MAIN ANSWER
        # ------------------------------------------

        if st.button("Submit Answer"):

            if not answer.strip():

                st.warning("Please enter your answer first.")

            else:

                st.session_state[pending_key] = answer

                try:

                    with st.spinner(
                        "Gemini is evaluating your answer..."
                    ):

                        evaluation = evaluate_answer(
                            session["role"],
                            question_data["question"],
                            answer
                        )

                    with st.spinner(
                        "Generating personalized follow-up..."
                    ):

                        followup = generate_followup(
                            session["role"],
                            question_data["question"],
                            answer
                        )

                    save_answer(
                        session,
                        question_data["question"],
                        answer,
                        evaluation
                    )

                    st.session_state.last_evaluation = (
                        evaluation.model_dump()
                    )

                    st.session_state.followup_question = followup
                    st.session_state.awaiting_followup = True

                    st.session_state.pop(pending_key, None)

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Gemini could not process your answer: {error}"
                    )

                    st.warning(
                        "Your answer has been preserved. "
                        "Please try again."
                    )

        # ------------------------------------------
        # RETRY MAIN ANSWER
        # ------------------------------------------

        if pending_key in st.session_state:

            if st.button("Retry Answer Evaluation"):

                try:

                    with st.spinner("Retrying with Gemini..."):

                        evaluation = evaluate_answer(
                            session["role"],
                            question_data["question"],
                            st.session_state[pending_key]
                        )

                        followup = generate_followup(
                            session["role"],
                            question_data["question"],
                            st.session_state[pending_key]
                        )

                    save_answer(
                        session,
                        question_data["question"],
                        st.session_state[pending_key],
                        evaluation
                    )

                    st.session_state.last_evaluation = (
                        evaluation.model_dump()
                    )

                    st.session_state.followup_question = followup
                    st.session_state.awaiting_followup = True

                    st.session_state.pop(pending_key, None)

                    st.rerun()

                except Exception as error:

                    st.error(f"Retry failed: {error}")

    # ----------------------------------------------
    # MAIN ANSWER EVALUATION
    # ----------------------------------------------

    if st.session_state.last_evaluation:

        evaluation = st.session_state.last_evaluation

        st.divider()
        st.subheader("Your Answer Evaluation")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Correctness",
            f"{evaluation['correctness']}/5"
        )

        col2.metric(
            "Clarity",
            f"{evaluation['clarity']}/5"
        )

        col3.metric(
            "Depth",
            f"{evaluation['depth']}/5"
        )

        st.write("**Feedback:**")
        st.write(evaluation["overall_feedback"])

        st.write("**Strengths:**")

        for item in evaluation["strengths"]:
            st.write(f"- {item}")

        st.write("**Areas to Improve:**")

        for item in evaluation["weaknesses"]:
            st.write(f"- {item}")

        st.write("**Improvement Tips:**")

        for item in evaluation["improvement_tips"]:
            st.write(f"- {item}")

    # ----------------------------------------------
    # FOLLOW-UP QUESTION
    # ----------------------------------------------

    if st.session_state.awaiting_followup:

        st.divider()
        st.subheader("AI Follow-up Question")

        st.info(
            "Gemini generated this question based on your previous answer:"
        )

        st.markdown(
            f"**{st.session_state.followup_question}**"
        )

        current_index = session["current_question"] - 1

        followup_answer = st.text_area(
            "Answer the follow-up question:",
            height=150,
            key=f"followup_{current_index}"
        )

        pending_followup_key = (
            f"pending_followup_{current_index}"
        )

        # ------------------------------------------
        # SUBMIT FOLLOW-UP ANSWER
        # ------------------------------------------

        if st.button("Submit Follow-up Answer"):

            if not followup_answer.strip():

                st.warning("Please enter your answer first.")

            else:

                st.session_state[pending_followup_key] = (
                    followup_answer
                )

                try:

                    with st.spinner(
                        "Evaluating follow-up answer..."
                    ):

                        followup_evaluation = evaluate_answer(
                            session["role"],
                            st.session_state.followup_question,
                            followup_answer
                        )

                    followup_record = {
                        "question": st.session_state.followup_question,
                        "answer": followup_answer,
                        "evaluation": followup_evaluation.model_dump()
                    }

                    session["followups"].append(followup_record)

                    st.session_state.followup_evaluations.append(
                        followup_record
                    )

                    st.session_state.followup_evaluation = (
                        followup_evaluation.model_dump()
                    )

                    st.session_state.awaiting_followup = False
                    st.session_state.followup_question = None

                    st.session_state.pop(
                        pending_followup_key,
                        None
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Follow-up evaluation failed: {error}"
                    )

                    st.warning(
                        "Your follow-up answer has been preserved. "
                        "You can retry it."
                    )

        # ------------------------------------------
        # RETRY FOLLOW-UP ANSWER
        # ------------------------------------------

        if pending_followup_key in st.session_state:

            if st.button("Retry Follow-up Evaluation"):

                try:

                    with st.spinner("Retrying with Gemini..."):

                        followup_evaluation = evaluate_answer(
                            session["role"],
                            st.session_state.followup_question,
                            st.session_state[pending_followup_key]
                        )

                    followup_record = {
                        "question": st.session_state.followup_question,
                        "answer": st.session_state[pending_followup_key],
                        "evaluation": followup_evaluation.model_dump()
                    }

                    session["followups"].append(followup_record)

                    st.session_state.followup_evaluations.append(
                        followup_record
                    )

                    st.session_state.followup_evaluation = (
                        followup_evaluation.model_dump()
                    )

                    st.session_state.awaiting_followup = False
                    st.session_state.followup_question = None

                    st.session_state.pop(
                        pending_followup_key,
                        None
                    )

                    st.rerun()

                except Exception as error:

                    st.error(f"Retry failed: {error}")

    # ----------------------------------------------
    # FOLLOW-UP EVALUATION
    # ----------------------------------------------

    if st.session_state.followup_evaluation:

        evaluation = st.session_state.followup_evaluation

        st.divider()
        st.subheader("Follow-up Answer Evaluation")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Correctness",
            f"{evaluation['correctness']}/5"
        )

        col2.metric(
            "Clarity",
            f"{evaluation['clarity']}/5"
        )

        col3.metric(
            "Depth",
            f"{evaluation['depth']}/5"
        )

        st.write("**Feedback:**")
        st.write(evaluation["overall_feedback"])

        st.write("**Improvement Tips:**")

        for item in evaluation["improvement_tips"]:
            st.write(f"- {item}")

    # ----------------------------------------------
    # FINAL REPORT GENERATION
    # ----------------------------------------------

    if session["completed"] and not st.session_state.awaiting_followup:

        st.divider()

        st.success(
            "You have completed all five interview questions!"
        )

        st.write(
            f"Main questions answered: {len(session['answers'])}"
        )

        st.write(
            "Follow-up questions answered: "
            f"{len(session['followups'])}"
        )

        if st.session_state.final_report is None:

            if st.button("Generate Final Feedback Report"):

                try:

                    with st.spinner(
                        "Gemini is preparing your final report..."
                    ):

                        report = generate_feedback_report(
                            session["role"],
                            session["evaluations"]
                        )

                    st.session_state.final_report = report

                    if st.session_state.saved_session_id is None:

                        session_id = save_interview_session(
                            role=session["role"],
                            evaluations=session["evaluations"],
                            report=report,
                            answers=session["answers"],
                            followups=session["followups"]
                        )

                        st.session_state.saved_session_id = session_id

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Report generation failed: {error}"
                    )

                    st.warning(
                        "Your completed interview is still available. "
                        "You can retry report generation."
                    )

        # ------------------------------------------
        # DISPLAY FINAL REPORT
        # ------------------------------------------

        if st.session_state.final_report:

            report = st.session_state.final_report

            st.divider()
            st.header("Your Final Interview Report")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Correctness",
                f"{report.average_correctness}/5"
            )

            col2.metric(
                "Clarity",
                f"{report.average_clarity}/5"
            )

            col3.metric(
                "Depth",
                f"{report.average_depth}/5"
            )

            col4.metric(
                "Overall Score",
                f"{report.overall_score}/5"
            )

            st.subheader("Strengths")

            for item in report.strengths:
                st.write(f"- {item}")

            st.subheader("Weaknesses")

            for item in report.weaknesses:
                st.write(f"- {item}")

            st.subheader("Recommendations")

            for item in report.recommendations:
                st.write(f"- {item}")

            st.subheader("Final Summary")
            st.write(report.final_summary)

            st.success(
                f"Interview saved successfully! "
                f"Session ID: {st.session_state.saved_session_id}"
            )

            st.balloons()
