"""FastAPI backend for adaptive career recommendations."""

import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from advisor import generate_advice
from bayesian import initial_state, update_state
from matcher import get_top_careers
from models import (
    AdviceRequest,
    AdviceResponse,
    AnswerRequest,
    AssessmentResult,
    CareerMatch,
    NextResponse,
    Question,
    ResultResponse,
    StartResponse,
)
from selector import select_next_question, should_stop

SESSION_TTL_SECONDS = 30 * 60

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sessions: Dict[str, Dict[str, Any]] = {}


def cleanup_expired_sessions() -> None:
    """Remove expired in-memory sessions."""
    now = time.time()
    expired_session_ids = [
        session_id
        for session_id, session in sessions.items()
        if now - session["updated_at"] > SESSION_TTL_SECONDS
    ]
    for session_id in expired_session_ids:
        sessions.pop(session_id, None)


@asynccontextmanager
async def lifespan(_: FastAPI):
    cleanup_expired_sessions()
    yield


app = FastAPI(
    title="Career Predict API",
    description="Adaptive Bayesian career recommendation system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_result_payload(state: Dict[str, float]) -> AssessmentResult:
    """Build the top-three recommendation payload."""
    ranked_careers = get_top_careers(state)
    logger.debug("Ranked careers: %s", ranked_careers)
    return AssessmentResult(
        best_match=CareerMatch(**ranked_careers[0]),
        alternatives=[CareerMatch(**career) for career in ranked_careers[1:]],
        confidence=ranked_careers[0]["score"],
        state=state,
    )


def get_session(session_id: str) -> Dict[str, Any]:
    """Fetch a session and enforce TTL semantics."""
    cleanup_expired_sessions()
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    session["updated_at"] = time.time()
    return session


def require_active_question(session: Dict[str, Any]) -> Dict[str, Any]:
    """Return the question currently awaiting an answer."""
    current_question = session.get("current_question")
    if current_question is None:
        raise HTTPException(status_code=400, detail="Assessment is already complete.")
    return current_question


@app.get("/health")
async def healthcheck() -> Dict[str, str]:
    """Lightweight health endpoint for deployments."""
    return {"status": "ok"}


@app.post("/advice", response_model=AdviceResponse)
async def get_advice(request: AdviceRequest) -> AdviceResponse:
    """Generate structured career advice using Gemini (with fallback)."""
    state = {
        "analytical": request.analytical,
        "creativity": request.creativity,
        "social": request.social,
        "risk": request.risk,
        "discipline": request.discipline,
    }
    advice = generate_advice(state=state, career=request.career)
    return AdviceResponse(**advice)


@app.post("/start", response_model=StartResponse)
async def start_session() -> StartResponse:
    """Create a session and return the first adaptive question."""
    session_id = str(uuid.uuid4())
    state = initial_state()
    first_question = select_next_question(state=state, asked_question_ids=set(), questions_asked=0)
    if first_question is None:
        raise HTTPException(status_code=500, detail="Unable to start assessment.")

    sessions[session_id] = {
        "state": state,
        "asked_question_ids": {first_question["id"]},
        "answered_count": 0,
        "current_question": first_question,
        "result": None,
        "updated_at": time.time(),
    }
    logger.info("Created session %s", session_id)

    return StartResponse(
        session_id=session_id,
        question=Question(id=first_question["id"], text=first_question["text"]),
    )


@app.post("/next", response_model=NextResponse)
async def next_question(request: AnswerRequest) -> NextResponse:
    """Process an answer, then return the next question or the final result."""
    session = get_session(request.session_id)
    current_question = require_active_question(session)

    try:
        updated_state = update_state(
            state=session["state"],
            trait=current_question["trait"],
            answer=request.answer,
            likelihoods=current_question["likelihood"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    session["state"] = updated_state
    session["answered_count"] += 1
    logger.debug(
        "Session %s state after %s: %s",
        request.session_id,
        current_question["id"],
        updated_state,
    )

    if should_stop(updated_state, session["answered_count"]):
        result = build_result_payload(updated_state)
        session["result"] = result
        session["current_question"] = None
        logger.info("Completed session %s after %s answers", request.session_id, session["answered_count"])
        return NextResponse(
            session_id=request.session_id,
            result=result,
            message="Assessment complete.",
            state=updated_state,
        )

    next_question_item = select_next_question(
        state=updated_state,
        asked_question_ids=session["asked_question_ids"],
        questions_asked=session["answered_count"],
    )
    if next_question_item is None:
        result = build_result_payload(updated_state)
        session["result"] = result
        session["current_question"] = None
        return NextResponse(
            session_id=request.session_id,
            result=result,
            message="Assessment complete.",
            state=updated_state,
        )

    session["current_question"] = next_question_item
    session["asked_question_ids"].add(next_question_item["id"])
    logger.info(
        "Session %s processed answer %s and selected %s",
        request.session_id,
        request.answer,
        next_question_item["id"],
    )
    return NextResponse(
        session_id=request.session_id,
        question=Question(id=next_question_item["id"], text=next_question_item["text"]),
        message="Next question selected.",
        state=updated_state,
    )


@app.get("/result/{session_id}", response_model=ResultResponse)
async def get_result(session_id: str) -> ResultResponse:
    """Return the final result for a completed session."""
    session = get_session(session_id)
    result = session.get("result")
    if result is None:
        raise HTTPException(status_code=400, detail="Assessment is not complete yet.")

    return ResultResponse(
        session_id=session_id,
        best_match=result.best_match,
        alternatives=result.alternatives,
        confidence=result.confidence,
        state=result.state,
        questions_answered=session["answered_count"],
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
