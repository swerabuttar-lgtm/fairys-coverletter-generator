"""
Pydantic request/response models. Every free-text field has a max_length —
this is cheap insurance against both runaway API costs and a user pasting
something designed to hijack the system prompt.
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional


class CoverLetterRequest(BaseModel):
    job_title: str = Field(..., max_length=120)
    company_name: str = Field(..., max_length=120)
    job_description: str = Field(..., max_length=4000)
    candidate_background: str = Field(..., max_length=3000)
    tone: Literal["formal", "conversational", "confident"] = "formal"
    word_limit: int = Field(default=300, ge=100, le=600)
    language: Literal["english", "urdu", "roman urdu"] = "english"


class CoverLetterResponse(BaseModel):
    letter: str
    word_count: int


class HealthResponse(BaseModel):
    status: str
    model: str