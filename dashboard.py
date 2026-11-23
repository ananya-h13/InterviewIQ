
import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path

from database.db_manager import (
    initialize_database,
    get_all_sessions,
    get_session_details
)

from modules.human_evaluation import (
    calculate_human_agreement,
    interpret_correlation
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="InterviewIQ | Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

initialize_database()

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "data" / "human_evaluation_template.csv"


st.title("InterviewIQ Performance Dashboard")

st.write(
    "Track your interview performance, review previous "
    "answers and monitor your progress."
)

st.divider()


# --------------------------------------------------
# LOAD INTERVIEW HISTORY
# --------------------------------------------------

sessions = get_all_sessions()

if not sessions:

    st.info(
        "No interview sessions found. Complete an interview first."
    )

else:

    df = pd.DataFrame(sessions)

    # ----------------------------------------------
    # PERFORMANCE OVERVIEW
    # ----------------------------------------------

    st.header("Performance Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Interviews",
        len(df)
    )

    col2.metric(
        "Average Score",
        f"{df['overall_score'].mean():.2f}/5"
    )

    col3.metric(
        "Highest Score",
        f"{df['overall_score'].max():.2f}/5"
    )

    st.divider()

    # ----------------------------------------------
    # OVERALL SCORE PROGRESS
    # ----------------------------------------------

    st.header("Interview Score Progress")

    progress_df = df.sort_values("id").copy()

    progress_df["Session"] = (
        "Session " + progress_df["id"].astype(str)
    )

    fig = px.line(
        progress_df,
        x="Session",
        y="overall_score",
        color="role",
        markers=True,
        title="Overall Score Across Interview Sessions",
        labels={
            "overall_score": "Overall Score",
            "role": "Interview Role"
        }
    )

    fig.update_yaxes(range=[0, 5])

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    # ----------------------------------------------
    # SKILL-WISE PERFORMANCE
    # ----------------------------------------------

    st.header("Skill-wise Performance")

    skill_df = df[
        [
            "average_correctness",
            "average_clarity",
            "average_depth"
        ]
    ].mean().reset_index()

    skill_df.columns = ["Skill", "Score"]

    skill_df["Skill"] = skill_df["Skill"].map({
        "average_correctness": "Correctness",
        "average_clarity": "Clarity",
        "average_depth": "Depth"
    })

    fig2 = px.bar(
        skill_df,
        x="Skill",
        y="Score",
        color="Skill",
        title="Average Performance by Evaluation Criterion",
        range_y=[0, 5]
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.divider()

    # ----------------------------------------------
    # INTERVIEW HISTORY TABLE
    # ----------------------------------------------

    st.header("Interview History")

    display_df = df[
        [
            "id",
            "role",
            "session_date",
            "total_questions",
            "average_correctness",
            "average_clarity",
            "average_depth",
            "overall_score"
        ]
    ].copy()

    display_df.columns = [
        "Session ID",
        "Role",
        "Date",
        "Questions",
        "Correctness",
        "Clarity",
        "Depth",
        "Overall Score"
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ----------------------------------------------
    # FILTER BY ROLE
    # ----------------------------------------------

    st.header("Filter Interview History")

    selected_role = st.selectbox(
        "Select interview role",
        ["All Roles"] + sorted(df["role"].unique().tolist())
    )

    if selected_role == "All Roles":
        filtered_df = df
    else:
        filtered_df = df[df["role"] == selected_role]

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ----------------------------------------------
    # INDIVIDUAL INTERVIEW DETAILS
    # ----------------------------------------------

    st.header("Review Previous Interviews")

    session_options = {
        f"Session {row['id']} - {row['role']} - {row['session_date']}":
        row["id"]
        for _, row in df.iterrows()
    }

    selected_session = st.selectbox(
        "Choose an interview session",
        list(session_options.keys())
    )

    if st.button("View Interview Details"):

        st.session_state.selected_session_id = (
            session_options[selected_session]
        )

    if "selected_session_id" in st.session_state:

        details = get_session_details(
            st.session_state.selected_session_id
        )

        if details:

            st.divider()

            st.subheader(
                f"Interview Session #{details['id']}"
            )

            st.write("**Role:**", details["role"])
            st.write("**Date:**", details["session_date"])

            # --------------------------------------
            # FINAL REPORT
            # --------------------------------------

            st.subheader("Final Interview Report")

            report = details["report"]

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Correctness",
                f"{report['average_correctness']}/5"
            )

            col2.metric(
                "Clarity",
                f"{report['average_clarity']}/5"
            )

            col3.metric(
                "Depth",
                f"{report['average_depth']}/5"
            )

            col4.metric(
                "Overall Score",
                f"{report['overall_score']}/5"
            )

            st.write("**Strengths:**")

            for item in report["strengths"]:
                st.write(f"- {item}")

            st.write("**Weaknesses:**")

            for item in report["weaknesses"]:
                st.write(f"- {item}")

            st.write("**Recommendations:**")

            for item in report["recommendations"]:
                st.write(f"- {item}")

            st.write("**Final Summary:**")
            st.write(report["final_summary"])

            st.divider()

            # --------------------------------------
            # MAIN QUESTIONS AND ANSWERS
            # --------------------------------------

            st.subheader("Question and Answer History")

            answers = details["answers"]
            evaluations = details["evaluations"]

            if answers:

                for index, item in enumerate(answers):

                    with st.expander(
                        f"Question {index + 1}: {item['question']}"
                    ):

                        st.markdown("**Your Answer:**")
                        st.write(item["answer"])

                        if index < len(evaluations):

                            evaluation = evaluations[index]

                            st.markdown("**AI Evaluation:**")

                            c1, c2, c3 = st.columns(3)

                            c1.metric(
                                "Correctness",
                                f"{evaluation['correctness']}/5"
                            )

                            c2.metric(
                                "Clarity",
                                f"{evaluation['clarity']}/5"
                            )

                            c3.metric(
                                "Depth",
                                f"{evaluation['depth']}/5"
                            )

                            st.write(
                                "**Feedback:**",
                                evaluation["overall_feedback"]
                            )

                            st.write("**Strengths:**")

                            for strength in evaluation["strengths"]:
                                st.write(f"- {strength}")

                            st.write("**Areas to Improve:**")

                            for weakness in evaluation["weaknesses"]:
                                st.write(f"- {weakness}")

                            st.write("**Improvement Tips:**")

                            for tip in evaluation["improvement_tips"]:
                                st.write(f"- {tip}")

            else:

                st.info(
                    "Detailed answers are unavailable for this older "
                    "session because it was saved before answer-history "
                    "storage was added."
                )

            st.divider()

            # --------------------------------------
            # FOLLOW-UP QUESTIONS
            # --------------------------------------

            st.subheader("AI Follow-up History")

            followups = details["followups"]

            if followups:

                for index, item in enumerate(followups):

                    with st.expander(
                        f"Follow-up Question {index + 1}: "
                        f"{item['question']}"
                    ):

                        st.markdown("**Your Follow-up Answer:**")
                        st.write(item["answer"])

                        evaluation = item["evaluation"]

                        c1, c2, c3 = st.columns(3)

                        c1.metric(
                            "Correctness",
                            f"{evaluation['correctness']}/5"
                        )

                        c2.metric(
                            "Clarity",
                            f"{evaluation['clarity']}/5"
                        )

                        c3.metric(
                            "Depth",
                            f"{evaluation['depth']}/5"
                        )

                        st.write("**Feedback:**")
                        st.write(evaluation["overall_feedback"])

            else:

                st.info(
                    "No follow-up history available for this session."
                )


# --------------------------------------------------
# HUMAN EVALUATION AND AI CORRELATION
# --------------------------------------------------

st.divider()

st.header("Human Evaluation & AI Correlation")

st.write(
    "Compare AI-generated evaluation scores with scores "
    "provided independently by three human evaluators."
)

if not CSV_FILE.exists():

    st.warning(
        "Human evaluation CSV not found. "
        "Generate the template after collecting 20 "
        "AI-evaluated answers."
    )

else:

    st.write(
        "Human evaluation file:",
        str(CSV_FILE)
    )

    if st.button("Calculate AI-Human Correlation"):

        try:

            correlation_df, evaluation_df = (
                calculate_human_agreement(CSV_FILE)
            )

            st.session_state.correlation_results = (
                correlation_df
            )

            st.session_state.human_evaluation_data = (
                evaluation_df
            )

            st.success(
                "Correlation analysis completed successfully!"
            )

        except Exception as error:

            st.error(
                f"Unable to calculate correlation: {error}"
            )


# ----------------------------------------------
# DISPLAY CORRELATION RESULTS
# ----------------------------------------------

if "correlation_results" in st.session_state:

    correlation_df = st.session_state.correlation_results

    st.subheader("Pearson Correlation Results")

    col1, col2, col3 = st.columns(3)

    for col, (_, row) in zip(
        [col1, col2, col3],
        correlation_df.iterrows()
    ):

        value = row["Correlation"]

        if value is not None and pd.notna(value):

            col.metric(
                f"{row['Dimension']} Correlation",
                f"{value:.4f}"
            )

            col.caption(
                interpret_correlation(value)
            )

        else:

            col.metric(
                f"{row['Dimension']} Correlation",
                "N/A"
            )

    st.divider()

    # ------------------------------------------
    # CORRELATION CHART
    # ------------------------------------------

    st.subheader("AI vs Human Correlation Chart")

    chart_df = correlation_df.dropna(
        subset=["Correlation"]
    )

    if not chart_df.empty:

        fig3 = px.bar(
            chart_df,
            x="Dimension",
            y="Correlation",
            color="Dimension",
            title="Pearson Correlation by Evaluation Dimension",
            range_y=[-1, 1],
            text="Correlation"
        )

        fig3.update_traces(
            texttemplate="%{text:.4f}",
            textposition="outside"
        )

        fig3.add_hline(
            y=0,
            line_dash="dash"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    else:

        st.warning(
            "Correlation values could not be calculated. "
            "Check whether the scores have sufficient variation."
        )

    st.divider()

    # ------------------------------------------
    # DETAILED RESULTS TABLE
    # ------------------------------------------

    st.subheader("Detailed Correlation Table")

    st.dataframe(
        correlation_df,
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "Pearson correlation measures the strength and direction "
        "of the linear relationship between AI scores and the "
        "average scores assigned by the three human evaluators."
    )
