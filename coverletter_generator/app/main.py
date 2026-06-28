"""
FastAPI entrypoint. Run with: uvicorn app.main:app --reload
"""
import time
import json
import uuid
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()  # reads .env file so GEMINI_API_KEY is available

from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import CoverLetterRequest, CoverLetterResponse, HealthResponse
from app.prompts import SYSTEM_PROMPT, build_user_prompt
from app.llm_client import generate_cover_letter, MODEL

app = FastAPI(title="Fairy's Cover Letter Wala")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# ── History file path ──────────────────────────────────────────────────────────
HISTORY_FILE = Path(__file__).resolve().parent.parent / "history.json"
if not HISTORY_FILE.exists():
    HISTORY_FILE.write_text("[]", encoding="utf-8")

# ── Rate limiter ───────────────────────────────────────────────────────────────
_request_log: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 10
WINDOW_SECONDS = 60


def _check_rate_limit(ip: str) -> None:
    now = time.time()
    recent = [t for t in _request_log[ip] if now - t < WINDOW_SECONDS]
    if len(recent) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Zyada requests! Thoda ruko.")
    recent.append(now)
    _request_log[ip] = recent


def _save_to_history(req: CoverLetterRequest, letter: str, word_count: int) -> None:
    """Appends a generated letter entry to history.json"""
    try:
        history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        entry = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "job_title": req.job_title,
            "company_name": req.company_name,
            "tone": req.tone,
            "language": req.language,
            "word_limit": req.word_limit,
            "word_count": word_count,
            "letter": letter,
        }
        history.append(entry)
        HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"History save error: {e}")


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="Sab theek hai ✅", model=MODEL)


@app.post("/generate", response_model=CoverLetterResponse)
def generate(req: CoverLetterRequest, request: Request) -> CoverLetterResponse:
    client_ip = request.client.host if request.client else "127.0.0.1"
    _check_rate_limit(client_ip)

    user_prompt = build_user_prompt(
        job_title=req.job_title,
        company_name=req.company_name,
        job_description=req.job_description,
        candidate_background=req.candidate_background,
        tone=req.tone,
        word_limit=req.word_limit,
        language=req.language,
    )

    try:
        letter = generate_cover_letter(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        err_msg = str(e)
        if "API key not valid" in err_msg:
            raise HTTPException(status_code=400, detail="Gemini API Key valid nahi hai. Apni .env file check karein.")
        raise HTTPException(status_code=502, detail=f"Gemini API Error: {err_msg}")

    word_count = len(letter.split())

    _save_to_history(req, letter, word_count)

    return CoverLetterResponse(letter=letter, word_count=word_count)


@app.get("/history")
def get_history():
    """Returns all previously generated cover letters from history.json"""
    try:
        history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return JSONResponse(content={
            "total": len(history),
            "letters": history
        })
    except Exception:
        raise HTTPException(status_code=500, detail="History file read nahi ho rahi.")


@app.get("/templates")
def get_templates():
    """Returns 3 pre-filled example requests students can copy and use"""
    return JSONResponse(content={
        "templates": [
            {
                "name": "🖥️ Software Engineer — Formal English",
                "request": {
                    "job_title": "Junior Software Engineer",
                    "company_name": "Systems Limited",
                    "job_description": "We are looking for a Python developer with knowledge of REST APIs, SQL databases, and basic DevOps. Fresh graduates are encouraged to apply.",
                    "candidate_background": "BS Computer Science from FAST Lahore, 2024. Proficient in Python, Django, and PostgreSQL. Built a final year project: an online exam portal used by 200+ students.",
                    "tone": "formal",
                    "language": "english",
                    "word_limit": 280
                }
            },
            {
                "name": "📊 Data Analyst — Confident English",
                "request": {
                    "job_title": "Data Analyst",
                    "company_name": "Careem",
                    "job_description": "Seeking a data analyst skilled in Excel, Power BI, and Python for data cleaning and visualization. Strong communication skills required.",
                    "candidate_background": "BBA from IBA Karachi. Completed a 3-month internship at a fintech startup where I built Power BI dashboards tracking 50K+ daily transactions. Strong in Excel and basic Python.",
                    "tone": "confident",
                    "language": "english",
                    "word_limit": 300
                }
            },
            {
                "name": "🌙 Graphic Designer — Roman Urdu",
                "request": {
                    "job_title": "Graphic Designer",
                    "company_name": "Rozee.pk",
                    "job_description": "Creative graphic designer needed for social media content, branding, and UI mockups. Adobe Suite expertise required.",
                    "candidate_background": "2 saal ka experience hai graphic design mein. Adobe Illustrator, Photoshop aur Figma use karta hoon. 10+ brands ke liye social media content banaya hai freelance basis par.",
                    "tone": "conversational",
                    "language": "roman urdu",
                    "word_limit": 250
                }
            }
        ]
    })