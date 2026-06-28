# Smart Cover Letter Generator

FastAPI service that streams a tailored cover letter using Gemini.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your Gemini API key to .env
```

## Run

```bash
uvicorn app.main:app --reload
```

## Test (in a second terminal)

```bash
curl -N -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Python Developer",
    "company_name": "Systems Ltd",
    "job_description": "Looking for a Python developer with FastAPI experience.",
    "candidate_background": "Final-year CS student, built 3 AI projects.",
    "tone": "confident"
  }'
```

## Health check

```bash
curl http://localhost:8000/health
```

## Interactive API docs

Open http://localhost:8000/docs in your browser.
