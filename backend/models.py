"""Pydantic models for API validation and responses."""

from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

QuestionType = Literal["scale", "binary", "mcq"]


class Question(BaseModel):
    id: str
    text: str
    type: QuestionType
    options: Optional[List[str]] = None


class CareerMatch(BaseModel):
    role: str
    score: float
    trait_score: Optional[float] = None
    career_signal_score: Optional[float] = None
    blended_score: Optional[float] = None


class AssessmentResult(BaseModel):
    best_match: CareerMatch
    alternatives: List[CareerMatch]
    confidence: float
    state: Dict[str, float]


class StartResponse(BaseModel):
    session_id: str
    question: Question
    message: str = "Session started. Please submit an answer matching the question type."


class AnswerRequest(BaseModel):
    session_id: str
    answer: Union[int, str] = Field(
        description="scale: int 1..5, binary: 'yes'/'no', mcq: option index int (0-based)"
    )


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
