"""Pydantic models for API validation and responses."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Question(BaseModel):
    id: str
    text: str


class CareerMatch(BaseModel):
    role: str
    score: float


class AssessmentResult(BaseModel):
    best_match: CareerMatch
    alternatives: List[CareerMatch]
    confidence: float
    state: Dict[str, float]


class StartResponse(BaseModel):
    session_id: str
    question: Question
    message: str = "Session started. Please answer using a value from 1 to 5."


class AnswerRequest(BaseModel):
    session_id: str
    answer: int = Field(ge=1, le=5)


class NextResponse(BaseModel):
    session_id: str
    question: Optional[Question] = None
    result: Optional[AssessmentResult] = None
    message: str
    state: Dict[str, float]


class ResultResponse(AssessmentResult):
    session_id: str
    questions_answered: int


class AdviceRequest(BaseModel):
    analytical: float = Field(ge=0, le=1)
    creativity: float = Field(ge=0, le=1)
    social: float = Field(ge=0, le=1)
    risk: float = Field(ge=0, le=1)
    discipline: float = Field(ge=0, le=1)
    career: str


class AdviceResponse(BaseModel):
    explanation: str
    skill_gap: List[str]
    roadmap: List[str]
