# Sceneweaver AI

> An AI-powered script collaboration platform that intelligently merges multiple screenplay drafts into a single, polished scene — then analyzes, enhances, and compares them using Claude 3.5 Sonnet on AWS Bedrock.

Sceneweaver AI (branded in-app as **Genius AI**) is a [Streamlit](https://streamlit.io/) web application built for collaborative scriptwriting. Upload several drafts of the same scene and the app combines the best parts of each into one cohesive script, surfaces statistics about your drafts, and offers AI-driven analysis, enhancement, manual editing, and side-by-side draft comparison.

## Features

- **Multi-format upload** — Ingest script drafts as `.txt`, `.pdf`, or `.docx` files (multiple files at once).
- **Draft optimization** — A weighted scoring algorithm (length, cross-draft similarity, and narrative context) selects the strongest line at each position to assemble one optimized script.
- **Script statistics** — At-a-glance metrics: total drafts, average word count, unique character count, and average draft similarity.
- **AI analysis** — Claude 3.5 Sonnet provides analysis with selectable focus: Comprehensive, Character Development, Dialogue Quality, or Plot Structure.
- **AI enhancement** — Improve dialogue, character development, scene descriptions, emotional impact, and pacing. Enhancement preserves the original language of the script (e.g. Telugu, Hindi).
- **Manual editor** — Edit the optimized or enhanced script with a live formatted preview, undo history, and revert-to-original.
- **Draft comparison** — Compare any two drafts with similarity scoring, word/line/character metrics, scene-by-scene breakdowns, character presence charts, and a downloadable comparison report.
- **Screenplay-aware formatting** — Heuristics detect scene headings (INT./EXT.), transitions, character cues, parentheticals, and dialogue to render scripts in industry-style layout.
- **Downloads everywhere** — Export the optimized script, enhanced script, edited script, analysis report, and comparison report as plain text.

## Tech Stack

- **Language:** Python
- **Web framework / UI:** Streamlit
- **AI model:** Anthropic Claude 3.5 Sonnet via **AWS Bedrock** (`bedrock-runtime`)
- **AWS SDK:** boto3 / botocore
- **Document parsing:** pdfplumber, python-docx, pdfminer.six, pypdfium2, lxml
- **Text similarity:** Python standard library `difflib.SequenceMatcher` / `ndiff`
- **Data / utilities:** pandas, numpy, python-dotenv

> The `groq` package is listed in `requirements.txt`, but the current `app.py` performs all model calls through AWS Bedrock.

## How It Works

The entire application lives in a single module, `app.py`:

1. **File reading** (`read_file`) — Extracts text from uploaded `.txt`, `.pdf`, and `.docx` files.
2. **Optimization** (`choose_best_parts`) — Walks every draft line-by-line. For each position it scores candidate lines using a weighted blend of:
   - `base_score` — normalized line length/detail
   - `similarity` — average similarity to the corresponding line in other drafts (consensus)
   - `context` — continuity with the current character's prior dialogue

   The highest-scoring line at each position is selected and appended to the optimized script. Weights default to `{base_score: 0.3, similarity: 0.5, context: 0.2}`.
3. **Formatting** (`format_script`) — Classifies each line as character / action / dialogue and wraps it in styled HTML for display.
4. **AI calls** (`analyze_script_with_claude`) — Builds a prompt from per-mode templates (analyze / enhance / feedback, plus focus-specific variants), then invokes Claude via the configured Bedrock inference profile. Returns the generated text.
5. **UI** (`main`) — Renders the header, custom CSS, upload area, statistics, and the five feature tabs (Optimized Script, AI Analysis, AI Enhancement, Edit Script, Compare Drafts).

## Project Structure

```
Sceneweaver-AI/
├── app.py             # Entire Streamlit application (UI, optimization, formatting, Bedrock calls)
├── requirements.txt   # Pinned Python dependencies
├── .gitignore
└── .vscode/
    └── settings.json
```

## Prerequisites

- Python 3.10+ (dependencies are pinned for the 3.11/3.12 generation; `numpy 1.26.4`, `pandas 2.2.3`, etc.)
- An AWS account with **Amazon Bedrock** access and a Claude 3.5 Sonnet **inference profile**
- AWS credentials authorized to call `bedrock-runtime:InvokeModel`

## Installation

```bash
# Clone the repository
git clone https://github.com/KarthikRommula/Sceneweaver-AI.git
cd Sceneweaver-AI

# (Recommended) create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

The app loads configuration from a `.env` file in the project root (via `python-dotenv`). Create one with the following variables:

```env
# AWS region for Bedrock, e.g. us-east-1
AWS_REGION=

# AWS credentials with Bedrock InvokeModel permission
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# ARN of the Claude 3.5 Sonnet inference profile used for invoke_model
INFERENCE_PROFILE_ARN=
```

| Variable | Required | Description |
| --- | --- | --- |
| `AWS_REGION` | Yes | AWS region for the Bedrock runtime client. |
| `AWS_ACCESS_KEY_ID` | Yes | AWS access key with Bedrock permissions. |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS secret access key. |
| `INFERENCE_PROFILE_ARN` | Yes | Bedrock inference profile ARN passed as the `modelId` for Claude 3.5 Sonnet. |

> `.env` is git-ignored. Never commit real credentials.

## Usage

Run the app locally with Streamlit:

```bash
streamlit run app.py
```

Streamlit serves the app at `http://localhost:8501` by default. Then:

1. Upload two or more drafts of the same scene (`.txt`, `.pdf`, or `.docx`). At least two drafts are recommended for meaningful optimization.
2. Review the auto-generated **Script Statistics**.
3. Use the tabs:
   - **Optimized Script** — view and download the merged script.
   - **AI Analysis** — pick a focus and analyze with Claude.
   - **AI Enhancement** — select focus areas and generate an enhanced script, with optional diff against the original.
   - **Edit Script** — manually edit with live preview, undo, and revert.
   - **Compare Drafts** — compare two drafts and generate a detailed report.

The AI Analysis and AI Enhancement tabs require valid AWS Bedrock configuration (see [Configuration](#configuration)); the upload, optimization, editing, and comparison features work without it.

## Available Commands

This project does not define npm-style scripts. The relevant commands are:

| Command | Description |
| --- | --- |
| `pip install -r requirements.txt` | Install all dependencies. |
| `streamlit run app.py` | Launch the application. |
