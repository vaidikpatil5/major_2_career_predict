"""FastAPI backend for adaptive career recommendations."""

import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from advisor import generate_advice
from bayesian import initial_career_signal, initial_state, update_career_signal, update_state
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
from selector import calculate_uncertainty, select_next_question_with_debug, should_stop

SESSION_TTL_SECONDS = 30 * 60

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sessions: Dict[str, Dict[str, Any]] = {}
MAX_SELECTOR_TRACE_ENTRIES = 50


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
    ranked_careers = get_top_careers(state=state)
    logger.debug("Ranked careers: %s", ranked_careers)
    return AssessmentResult(
        best_match=CareerMatch(**ranked_careers[0]),
        alternatives=[CareerMatch(**career) for career in ranked_careers[1:]],
        confidence=ranked_careers[0]["score"],
        state=state,
    )


def build_result_payload_with_signal(state: Dict[str, float], career_signal: Dict[str, float]) -> AssessmentResult:
    """Build the top-three recommendation payload using blended scoring."""
    ranked_careers = get_top_careers(state=state, career_signal=career_signal)
    logger.debug("Ranked careers: %s", ranked_careers)
    return AssessmentResult(
        best_match=CareerMatch(**ranked_careers[0]),
        alternatives=[CareerMatch(**career) for career in ranked_careers[1:]],
        confidence=ranked_careers[0]["score"],
        state=state,
    )


def append_selector_trace(session: Dict[str, Any], entry: Dict[str, Any]) -> None:
    """Store bounded selector telemetry for session-level debugging."""
    trace = session.setdefault("selector_trace", [])
    if not isinstance(trace, list):
        trace = []
        session["selector_trace"] = trace
    trace.append(entry)
    if len(trace) > MAX_SELECTOR_TRACE_ENTRIES:
        del trace[:-MAX_SELECTOR_TRACE_ENTRIES]


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


def build_question_payload(question: Dict[str, Any]) -> Question:
    """Convert internal question dicts to API-safe response payloads."""
    question_type = question.get("type")
    payload = {
        "id": question["id"],
        "text": question["text"],
        "type": question_type,
    }
    if question_type == "mcq":
        payload["options"] = list(question.get("options", []))
    return Question(**payload)


def validate_answer_for_question(question: Dict[str, Any], answer: Any) -> Any:
    """Validate and normalize answer payload based on current question type."""
    question_type = question.get("type")
    question_id = question.get("id", "<unknown>")

    if question_type == "scale":
        if not isinstance(answer, int) or isinstance(answer, bool) or not (1 <= answer <= 5):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid answer for scale question '{question_id}'. Expected integer 1-5.",
            )
        return answer

    if question_type == "binary":
        if not isinstance(answer, str):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid answer for binary question '{question_id}'. Expected 'yes' or 'no'.",
            )
        normalized = answer.strip().lower()
        if normalized not in {"yes", "no"}:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid answer for binary question '{question_id}'. Expected 'yes' or 'no'.",
            )
        return normalized

    if question_type == "mcq":
        if not isinstance(answer, int) or isinstance(answer, bool):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid answer for mcq question '{question_id}'. Expected a 0-based option index.",
            )
        options = question.get("options", [])
        if answer < 0 or answer >= len(options):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid answer for mcq question '{question_id}'. "
                    f"Expected index in range [0, {len(options) - 1}]."
                ),
            )
        return answer

    raise HTTPException(
        status_code=500,
        detail=f"Question '{question_id}' has unsupported type '{question_type}'.",
    )


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


@app.post("/start", response_model=StartResponse, response_model_exclude_none=True)
async def start_session() -> StartResponse:
    """Create a session and return the first adaptive question."""
    session_id = str(uuid.uuid4())
    state = initial_state()
    career_signal = initial_career_signal()
    first_question, selector_debug = select_next_question_with_debug(
        state=state,
        career_signal=career_signal,
        asked_question_ids=set(),
        questions_asked=0,
    )
    if first_question is None:
        raise HTTPException(status_code=500, detail="Unable to start assessment.")

    sessions[session_id] = {
        "state": state,
        "career_signal": career_signal,
        "asked_question_ids": {first_question["id"]},
        "asked_career_questions": 1 if first_question.get("career_weights") else 0,
        "answered_count": 0,
        "current_question": first_question,
        "result": None,
        "selector_trace": [],
        "updated_at": time.time(),
    }
    append_selector_trace(
        sessions[session_id],
        {
            "event": "start_selection",
            "selected_question_id": first_question["id"],
            "debug": selector_debug,
            "timestamp": time.time(),
        },
    )
    logger.info("Created session %s", session_id)

    return StartResponse(
        session_id=session_id,
        question=build_question_payload(first_question),
    )


@app.post("/next", response_model=NextResponse, response_model_exclude_none=True)
async def next_question(request: AnswerRequest) -> NextResponse:
    """Process an answer, then return the next question or the final result."""
    session = get_session(request.session_id)
    current_question = require_active_question(session)

    normalized_answer = validate_answer_for_question(current_question, request.answer)

    updated_state = session["state"]
    updated_career_signal = session.get("career_signal", initial_career_signal())

    try:
        if current_question.get("type") == "scale" or current_question.get("weights") is not None:
            updated_state = update_state(
                state=session["state"],
                question=current_question,
                answer=normalized_answer,
            )
        if current_question.get("career_weights") is not None:
            updated_career_signal = update_career_signal(
                career_signal=updated_career_signal,
                question=current_question,
                answer=normalized_answer,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    session["state"] = updated_state
    session["career_signal"] = updated_career_signal
    session["answered_count"] += 1
    logger.debug(
        "Session %s state after %s: %s",
        request.session_id,
        current_question["id"],
        updated_state,
    )

    if should_stop(
        updated_state,
        session["answered_count"],
        asked_career_questions=session.get("asked_career_questions", 0),
    ):
        append_selector_trace(
            session,
            {
                "event": "stop_after_answer",
                "answered_count": session["answered_count"],
                "dominant_trait_score": max(updated_state.values()) if updated_state else 0.0,
                "uncertainty": calculate_uncertainty(updated_state),
                "timestamp": time.time(),
            },
        )
        result = build_result_payload_with_signal(updated_state, updated_career_signal)
        session["result"] = result
        session["current_question"] = None
        logger.info("Completed session %s after %s answers", request.session_id, session["answered_count"])
        return NextResponse(
            session_id=request.session_id,
            result=result,
            message="Assessment complete.",
            state=updated_state,
        )

    next_question_item, selector_debug = select_next_question_with_debug(
        state=updated_state,
        career_signal=updated_career_signal,
        asked_question_ids=session["asked_question_ids"],
        questions_asked=session["answered_count"],
    )
    if next_question_item is None:
        append_selector_trace(
            session,
            {
                "event": "selector_returned_none",
                "answered_count": session["answered_count"],
                "debug": selector_debug,
                "timestamp": time.time(),
            },
        )
        result = build_result_payload_with_signal(updated_state, updated_career_signal)
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
    if next_question_item.get("career_weights") is not None:
        session["asked_career_questions"] = session.get("asked_career_questions", 0) + 1
    append_selector_trace(
        session,
        {
            "event": "next_selection",
            "selected_question_id": next_question_item["id"],
            "answer_to_previous_question": normalized_answer,
            "answered_count": session["answered_count"],
            "debug": selector_debug,
            "timestamp": time.time(),
        },
    )
    logger.info(
        "Session %s processed answer %s and selected %s",
        request.session_id,
        normalized_answer,
        next_question_item["id"],
    )
    return NextResponse(
        session_id=request.session_id,
        question=build_question_payload(next_question_item),
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


@app.get("/debug/session/{session_id}")
async def get_session_debug(session_id: str) -> Dict[str, Any]:
    """Inspect adaptive selector telemetry for a given session."""
    session = get_session(session_id)
    state = session.get("state", {})
    return {
        "session_id": session_id,
        "answered_count": session.get("answered_count", 0),
        "asked_career_questions": session.get("asked_career_questions", 0),
        "current_question_id": (
            session.get("current_question", {}).get("id")
            if isinstance(session.get("current_question"), dict)
            else None
        ),
        "is_complete": session.get("result") is not None,
        "dominant_trait_score": max(state.values()) if state else 0.0,
        "uncertainty": calculate_uncertainty(state) if state else 0.0,
        "career_signal": session.get("career_signal", {}),
        "selector_trace": session.get("selector_trace", []),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
