# JA Assure AI Marketing Agent

Prototype based on the supplied JA Assure architecture:
Research -> Content/Leads -> Compliance -> Human Review -> Feedback Memory -> Future Generation.

## Stack
- Frontend: Streamlit
- Backend: FastAPI
- AI: Gemini API
- Agent orchestration: Python functions
- Database: SQLite
- Research: Gemini Google Search grounding

## Setup

### 1. Create a virtual environment
Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install
```bash
pip install -r requirements.txt
```

### 3. Configure Gemini
Copy `.env.example` to `.env` and put your Gemini API key in `GEMINI_API_KEY`.

Never commit `.env`.

### 4. Start backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### 5. Start frontend in another terminal
```bash
streamlit run frontend/app.py
```

Open the Streamlit URL shown by the terminal.

## Demo
Select:
- Brand: DoctorShield
- Platform: LinkedIn
- Objective: Create Content
- Topic: Preventive health and employee wellbeing

Click **Run AI Workflow**.

The workflow:
1. Research
2. Generate content
3. Compliance check
4. Human review
5. Store feedback
6. Regenerate improved content when rejected

## Important
This is a prototype. Public-source lead discovery and insurance compliance should be reviewed by a qualified human before real-world use. The AI does not automatically publish content.
