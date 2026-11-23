
import pandas as pd
from pathlib import Path


EVALUATION_DIMENSIONS = [
    "correctness",
    "clarity",
    "depth"
]

HUMAN_EVALUATORS = [
    "human1",
    "human2",
    "human3"
]


def load_human_evaluations(csv_path):

    file_path = Path(csv_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Evaluation file not found: {csv_path}"
        )

    df = pd.read_csv(file_path)

    required_columns = ["answer_id"]

    for dimension in EVALUATION_DIMENSIONS:

        required_columns.append(f"ai_{dimension}")

        for evaluator in HUMAN_EVALUATORS:
            required_columns.append(
                f"{evaluator}_{dimension}"
            )

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing CSV columns: {missing_columns}"
        )

    return df


def calculate_human_agreement(csv_path):

    df = load_human_evaluations(csv_path)

    if len(df) != 20:
        raise ValueError(
            f"Expected 20 evaluated answers, but found {len(df)}."
        )

    score_columns = [
        f"ai_{dimension}"
        for dimension in EVALUATION_DIMENSIONS
    ]

    for dimension in EVALUATION_DIMENSIONS:

        for evaluator in HUMAN_EVALUATORS:

            score_columns.append(
                f"{evaluator}_{dimension}"
            )

    for column in score_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    if df[score_columns].isnull().any().any():
        raise ValueError(
            "Some evaluation scores are missing or invalid. "
            "Please complete all three human evaluations."
        )

    if not df[score_columns].apply(
        lambda column: column.between(1, 5).all()
    ).all():
        raise ValueError(
            "All evaluation scores must be between 1 and 5."
        )

    results = []

    for dimension in EVALUATION_DIMENSIONS:

        human_columns = [
            f"{evaluator}_{dimension}"
            for evaluator in HUMAN_EVALUATORS
        ]

        average_column = f"average_human_{dimension}"

        df[average_column] = df[human_columns].mean(axis=1)

        correlation = df[f"ai_{dimension}"].corr(
            df[average_column],
            method="pearson"
        )

        results.append({
            "Dimension": dimension.capitalize(),
            "Correlation": round(float(correlation), 4)
            if pd.notna(correlation) else None
        })

    return pd.DataFrame(results), df


def interpret_correlation(value):

    if pd.isna(value):
        return "Correlation could not be calculated."

    if value >= 0.7:
        return "Strong positive correlation."

    elif value >= 0.4:
        return "Moderate positive correlation."

    elif value >= 0.2:
        return "Weak positive correlation."

    elif value > -0.2:
        return "Very weak or no linear correlation."

    elif value > -0.4:
        return "Weak negative correlation."

    elif value > -0.7:
        return "Moderate negative correlation."

    else:
        return "Strong negative correlation."
