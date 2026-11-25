# InterviewIQ

InterviewIQ is an AI-powered interview practice app built with Streamlit. Practice technical and HR interviews, get feedback from Google Gemini, and review your performance over time.

## Features

- Practice interviews for Python Developer and Data Analyst roles.
- Answer a randomized set of questions and receive AI-generated feedback on correctness, clarity, and depth.
- Get follow-up questions based on your answers.
- Review interview reports, recommendations, and previous sessions.
- Explore performance history and charts in a Streamlit dashboard.
- Compare AI scores with human evaluations using Pearson correlation analysis.

## Technology stack

- Python
- Streamlit
- Google Gemini API (`google-genai`)
- SQLite
- Pandas
- Plotly
- Pydantic

## Setup

### Prerequisites

- Python and pip
- A Google Gemini API key

### Windows PowerShell

From the project directory, create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create your local environment file from the template:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder with your Gemini API key:

```text
GEMINI_API_KEY=your_actual_gemini_api_key
```

Keep the real key in `.env`; do not commit or share that file. The repository ignore rules exclude it.

## Run the app

Start the app:

```powershell
streamlit run app.py
```

The interview experience opens by default. Use Streamlit's multipage navigation
to open the Performance Dashboard.

The application initializes its SQLite database at `database/interviewiq.db` when it starts. This database contains local interview history and is excluded from Git.

## Human evaluation

The dashboard can compare AI scores with ratings from three human evaluators. Prepare a CSV with 20 evaluated answers and these columns:

```text
answer_id,ai_correctness,ai_clarity,ai_depth,human1_correctness,human1_clarity,human1_depth,human2_correctness,human2_clarity,human2_depth,human3_correctness,human3_clarity,human3_depth
```

Use scores from 1 to 5 and save the completed file as `data/human_evaluation_template.csv`. The dashboard uses it to calculate Pearson correlations. The current `generate_human_evaluation_template.py` file does not create this CSV. The completed file may contain evaluation data; review it before sharing.

## Project structure

```text
.
├── app.py                         # Interview practice app
├── config.py                      # Gemini API configuration
├── data/
│   └── questions.json             # Role-based question bank
├── pages/
│   └── dashboard.py               # History and performance dashboard
├── database/
│   ├── db_manager.py              # SQLite persistence
│   └── __init__.py
├── modules/
│   ├── evaluator.py               # AI answer evaluation
│   ├── human_evaluation.py        # AI-human score comparison
│   ├── interviewer.py             # Follow-up questions
│   ├── report_generator.py        # Final interview reports
│   ├── schemas.py                 # Pydantic response schemas
│   └── session_manager.py         # Interview session logic
├── requirements.txt
└── .env.example                   # Safe environment-variable template
```

## Local data and secrets

`.env`, `.env.*` files (except `.env.example`), `.venv/`, Python cache files, Streamlit secrets, and SQLite `.db` files are ignored by Git. Interview history is stored locally in SQLite; do not commit the database.
