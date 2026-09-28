# CareerAI — AI-Powered Career Intelligence and Mock Interview Assessment System

**Final-Year B.Tech (Information Technology) — Internship II Project**
**Domain:** Artificial Intelligence / Natural Language Processing

---

## 1. Project Overview

CareerAI is an AI-powered career preparation platform. A student uploads their
resume and pastes a target job description; the system then:

- Extracts a structured profile from the resume (skills, education,
  projects, internships, certifications).
- Extracts a structured profile from the job description (role, required
  skills, preferred skills, experience/education requirements).
- Computes an explainable **Job Match Score** using semantic similarity +
  explicit skill overlap.
- Performs a **Skill Gap Analysis** (Strong Match / Partial Match / Missing)
  with per-skill learning recommendations.
- Generates a tailored **AI Mock Interview** (Technical / HR / Mixed,
  configurable difficulty and length) from a structured question bank.
- Evaluates the candidate's typed answers using NLP techniques (relevance,
  concept coverage, completeness) and gives constructive feedback.
- Produces a **personalized, priority-ranked, week-by-week learning
  roadmap**.
- Displays everything on an interactive **Streamlit dashboard**, and stores
  session results locally in **SQLite**.

The entire system runs **locally**, using **free and open-source
libraries only** — no paid AI API (OpenAI/Gemini/Claude/etc.) is required
or used anywhere.

---

## 2. Problem Statement

Final-year students preparing for placements typically have to manually:
(a) figure out how well their resume matches a job description,
(b) identify which skills they're missing,
(c) find relevant practice questions, and
(d) get feedback on their interview answers —
usually across four or five disconnected tools (or with no tool at all).

CareerAI consolidates this entire preparation workflow into a single,
explainable, locally-run application.

---

## 3. Objectives

1. Build an end-to-end resume ⇄ job-description matching pipeline using NLP.
2. Provide a transparent, documented scoring formula (not a black box).
3. Perform rule-based + semantic skill-gap analysis with recommendations.
4. Generate a tailored mock interview from a structured question bank.
5. Evaluate free-text interview answers using explainable NLP techniques.
6. Generate a personalized, prioritized learning roadmap.
7. Present all results through an interactive, professional dashboard.
8. Persist session data locally using SQLite.
9. Operate entirely offline-capable with a graceful fallback if the
   transformer model cannot be downloaded (no GPU required, ~8GB RAM is enough).

---

## 4. Features

| # | Feature | Module |
|---|---|---|
| 1 | PDF/DOCX resume text extraction | Resume Intelligence |
| 2 | Rule-based section detection (Education/Projects/Internships/Certs) | Resume Intelligence |
| 3 | Dictionary + alias + fuzzy skill extraction | Resume Intelligence / Job Intelligence |
| 4 | Job description parsing (role, required/preferred skills, experience) | Job Description Intelligence |
| 5 | Semantic similarity (Sentence-Transformers, TF-IDF fallback) | AI Job Matching |
| 6 | Transparent weighted Final Match Score | AI Job Matching |
| 7 | Strong / Partial / Missing skill classification | Skill Gap Analysis |
| 8 | Per-skill learning recommendations + mini-project ideas | Skill Gap Analysis |
| 9 | Configurable mock interview (count/difficulty/type) | AI Mock Interview |
| 10 | Resume/project/role-aware question selection | AI Mock Interview |
| 11 | Relevance / concept coverage / completeness scoring | Interview Evaluation |
| 12 | Constructive per-answer feedback | Interview Evaluation |
| 13 | Priority-ranked, week-by-week learning roadmap | Career Roadmap |
| 14 | Interactive Plotly dashboard | AI Career Dashboard |
| 15 | Local SQLite persistence | Database |

---

## 5. Architecture

```
USER
  │
  ▼
STREAMLIT WEB APPLICATION
  │
  ├── Resume Processing ───────► Text Extraction ─────┐
  └── Job Description Processing ─► Text Preprocessing ┤
                                                        ▼
                                                  NLP ENGINE
                              ┌────────────┬────────────────┐
                       Resume Skill   Job Skill        Semantic
                       Extraction     Extraction       Similarity
                              └────────────┴────────────────┘
                                           │
                                           ▼
                                    JOB MATCHING
                                           │
                                           ▼
                                 SKILL GAP ANALYSIS
                                           │
                                           ▼
                             INTERVIEW QUESTION ENGINE
                                           │
                                           ▼
                            INTERVIEW ANSWER ANALYSIS
                                           │
                                           ▼
                              PERFORMANCE ANALYSIS
                                           │
                                           ▼
                        PERSONALIZED LEARNING ROADMAP
                                           │
                                           ▼
                                  AI DASHBOARD
                                           │
                                           ▼
                                    SQLITE DB
```

**AI/ML vs. rule-based components (see also the in-app "About" page):**
- **Pre-trained AI model:** `sentence-transformers` (`all-MiniLM-L6-v2`) for
  semantic similarity.
- **Classical NLP:** spaCy (sentence segmentation/lemmatization, with a
  regex fallback), TF-IDF (fallback similarity engine).
- **Rule-based logic:** skill-dictionary matching, section detection,
  scoring formulas, skill-gap thresholds, roadmap prioritization.

---

## 6. Technology Stack

- **Language:** Python 3.10+
- **UI:** Streamlit
- **NLP/AI:** spaCy, sentence-transformers, scikit-learn (TF-IDF, cosine similarity)
- **Document Processing:** pypdf, python-docx
- **Data Processing:** pandas, numpy
- **Visualization:** Plotly
- **Database:** SQLite (via Python's built-in `sqlite3`)
- **Testing:** pytest

---

## 7. Folder Structure

```
CareerAI/
│
├── app.py                          # Streamlit entry point (Home page)
├── requirements.txt
├── README.md
├── .gitignore
├── config.py                       # Central configuration & scoring weights
│
├── data/
│   ├── skills.csv                  # Maintainable skill dictionary
│   ├── interview_questions.json    # Structured question bank
│   └── sample_job_descriptions/    # 5 sample JDs for demo purposes
│
├── database/
│   ├── database.py                 # SQLite connection + CRUD functions
│   └── schema.py                   # Table DDL
│
├── models/
│   ├── embeddings.py                # Sentence-Transformer + TF-IDF engine
│   ├── similarity.py                # Cosine similarity utilities
│   └── scoring.py                   # Job match score + skill-gap classification
│
├── nlp/
│   ├── text_preprocessor.py         # Cleaning / normalization / tokenizing
│   ├── resume_parser.py             # Module 1: Resume Intelligence
│   ├── skill_extractor.py           # Dictionary + alias + fuzzy skill matching
│   └── job_parser.py                # Module 2: Job Description Intelligence
│
├── interview/
│   ├── question_engine.py           # Module 5: question selection/generation
│   ├── answer_evaluator.py          # Module 6: answer scoring
│   └── feedback.py                  # Interview summary aggregation
│
├── roadmap/
│   └── roadmap_generator.py         # Module 7: prioritization + weekly plan
│
├── dashboard/
│   └── charts.py                    # Reusable Plotly chart builders
│
├── utils/
│   ├── file_utils.py
│   ├── validators.py
│   ├── helpers.py
│   └── session_state.py             # Shared Streamlit session-state keys
│
├── pages/
│   ├── 1_Resume_Analyzer.py
│   ├── 2_Job_Matcher.py
│   ├── 3_Skill_Gap_Analysis.py
│   ├── 4_Mock_Interview.py
│   ├── 5_Interview_Evaluation.py
│   ├── 6_Career_Roadmap.py
│   ├── 7_Dashboard.py
│   └── 8_About.py
│
└── tests/
    ├── test_resume_parser.py
    ├── test_skill_extractor.py
    ├── test_similarity.py
    ├── test_scoring.py
    └── test_roadmap.py
```

---

## 8. Installation

### Step 1 — Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Download the spaCy English model

```bash
python -m spacy download en_core_web_sm
```

> If this step fails (e.g. no internet access at that moment), the
> application will still run — it automatically falls back to a
> regex-based text-processing path. You'll see this reflected in the
> sidebar's "System Status" panel.

### Step 4 — (First run only) Sentence-Transformer model download

The first time the app computes a semantic similarity score, it will try
to download `all-MiniLM-L6-v2` from Hugging Face (~80MB, one-time,
cached afterwards). If your machine has no internet access at that
moment, the app **automatically switches to a TF-IDF fallback** — no
crash, no manual configuration needed. The active engine is always shown
in the sidebar.

---

## 9. How to Run

```bash
streamlit run app.py
```

This opens the app in your browser (typically `http://localhost:8501`).
Use the sidebar to navigate between pages.

---

## 10. How to Test

```bash
pytest tests/ -v
```

All tests are written to pass regardless of whether the sentence-transformer
model or the TF-IDF fallback is active, and regardless of whether the
spaCy model is installed, so `pytest` can be run immediately after
`pip install -r requirements.txt` even before downloading any models.

---

## 11. Example Workflow

1. **Resume Analyzer** — Upload a `.pdf` or `.docx` resume. View extracted
   skills, education, projects, internships, and certifications.
2. **Job Matcher** — Paste a job description (or load one of the 5 sample
   JDs). Click **Analyze Match** to see the Overall Job Match score,
   Semantic Similarity, Skill Overlap, and Matched/Missing/Partial skills.
3. **Skill Gap Analysis** — Review the Strong/Partial/Missing skill
   breakdown with per-skill recommended learning topics and mini-projects.
4. **Mock Interview** — Choose question count (5/10/15), difficulty
   (Easy/Medium/Hard/Mixed), and type (Technical/HR/Mixed). Generate
   questions and type your answers.
5. **Interview Evaluation** — Submit your answers to see per-question
   scores (Relevance / Concept Coverage / Completeness), an overall score,
   and constructive feedback.
6. **Career Roadmap** — Generate a week-by-week personalized study plan
   built from your skill gaps and interview weaknesses.
7. **Dashboard** — View a single consolidated summary of everything above.
8. **About Project** — Read the academic disclaimers and the AI/ML vs.
   rule-based component breakdown.

---

## 12. Screenshots

_Add screenshots here after running the application locally, e.g.:_

- `screenshots/01_home.png`
- `screenshots/02_resume_analyzer.png`
- `screenshots/03_job_matcher.png`
- `screenshots/04_skill_gap.png`
- `screenshots/05_mock_interview.png`
- `screenshots/06_interview_evaluation.png`
- `screenshots/07_roadmap.png`
- `screenshots/08_dashboard.png`

---

## 13. Limitations

- Resume section detection and field extraction are heuristic/rule-based;
  unusual formats (heavy graphics, multi-column layouts, scanned images
  without a text layer) may parse less accurately.
- The skill dictionary (`data/skills.csv`), while easily extensible, cannot
  recognize skills it has never seen — add new rows as needed.
- Interview answer evaluation assesses **textual** relevance, concept
  coverage, and completeness only. It cannot judge spoken delivery,
  confidence, or the kind of deep follow-up questioning a real interview
  panel would perform.
- No accuracy/precision/recall/F1 figures are claimed anywhere in this
  project, since no labeled ground-truth evaluation dataset was collected.
  If such an evaluation is required, `tests/` can be extended with
  real annotated data and appropriate metrics computed explicitly.
- Voice-based (speech-to-text) interview input is **not implemented** in
  this version — see Future Scope.

---

## 14. Future Scope

- Multilingual resume and interview support.
- Real-time voice-based mock interviews (e.g. via the `SpeechRecognition`
  library, already scaffolded as an optional dependency).
- Larger, ontology-based skill graph with skill-to-skill relationships.
- Cloud deployment with user authentication and a recruiter-facing view.
- Domain-specific fine-tuned embedding models for stronger semantic matching.
- Real-time interview analytics across multiple sessions.
- Facial/emotion analysis for interview delivery feedback — only with
  explicit user consent and clear ethical safeguards, if ever added.

---

## 15. Security & Privacy

- Resumes are processed **entirely locally**; no file content is sent to
  any external or paid AI service.
- No paid API key is required or used anywhere in this project.
- Uploaded resume files are held only in memory during analysis and are
  **not** permanently written to disk.
- Session analysis results (names, scores, extracted skills) are stored
  locally in `database/careerai.db` for the user's own reference across
  runs; this file is excluded from version control via `.gitignore`.

---

## 16. Academic Note

> This system is an academic prototype developed for a final-year B.Tech
> Internship-II project. The generated scores (Job Match, Skill Gap,
> Interview Evaluation) are AI-assisted **academic assessment metrics**
> intended to support self-assessment and learning. They are **not**
> scientifically validated hiring/recruitment scores and should not be
> treated as a substitute for professional recruitment decisions or a
> real interview panel's judgement.

---

## 17. Author

Final-Year B.Tech (Information Technology) Student — Internship II Project.
