"""Career advice generation using Gemini with deterministic fallback."""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List
from urllib import error, request

from dotenv import load_dotenv

from matcher import get_top_careers

logger = logging.getLogger(__name__)

# Auto-load secrets from backend/.env if present.
load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=False)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={api_key}"
)


def _extract_json_object(text: str) -> Dict[str, object]:
    """Extract and parse the first JSON object from model output text."""
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Gemini response did not contain a JSON object.")
    return json.loads(text[start : end + 1])


def _validate_advice_payload(payload: Dict[str, object]) -> Dict[str, object]:
    """Validate shape required by API response contract."""
    required = {"explanation", "skill_gap", "roadmap"}
    if set(payload.keys()) != required:
        raise ValueError("Gemini response keys do not match required contract.")
    if not isinstance(payload["explanation"], str):
        raise ValueError("Field 'explanation' must be a string.")
    if not isinstance(payload["skill_gap"], list) or not all(
        isinstance(item, str) for item in payload["skill_gap"]
    ):
        raise ValueError("Field 'skill_gap' must be a list of strings.")
    if not isinstance(payload["roadmap"], list) or not all(
        isinstance(item, str) for item in payload["roadmap"]
    ):
        raise ValueError("Field 'roadmap' must be a list of strings.")
    return payload


def _build_fallback_advice(state: Dict[str, float], career: str, alternatives: List[str]) -> Dict[str, object]:
    """Generate deterministic advice when Gemini is unavailable."""
    ranked_traits = sorted(state.items(), key=lambda item: item[1], reverse=True)
    strongest_traits = [name for name, _ in ranked_traits[:2]]
    weakest_traits = [name for name, _ in ranked_traits[-2:]]

    explanation_lines = [
        f"- Best-fit career: {career}",
        f"- Top 2 alternatives: {alternatives[0]}, {alternatives[1]}",
        f"- Strongest traits driving fit: {strongest_traits[0]}, {strongest_traits[1]}",
        "- Match rationale: your strongest traits align well with role demands.",
    ]

    skill_gap = [
        f"{trait}: lower relative score may reduce consistency or performance in high-pressure tasks."
        for trait in weakest_traits
    ]

    roadmap = [
        "Week 1-2: Build core foundations in your chosen domain and define a weekly study schedule.",
        "Week 3-4: Practice one mini-project focused on problem-solving and communication.",
        "Week 5-6: Learn role-specific tools and publish project outcomes.",
        "Week 7-8: Simulate interviews, collect feedback, and refine weak traits with targeted exercises.",
        "Ongoing: Maintain a portfolio, track progress monthly, and iterate with mentor input.",
    ]

    return {
        "explanation": "\n".join(explanation_lines),
        "skill_gap": skill_gap,
        "roadmap": roadmap,
    }


def _build_prompt(state: Dict[str, float], career: str, alternatives: List[str]) -> str:
    """Create a strict prompt that requests contract-compliant JSON output."""
    return f"""
You are an expert career advisor.

User profile:
- Analytical: {state["analytical"]:.3f}
- Creativity: {state["creativity"]:.3f}
- Social: {state["social"]:.3f}
- Risk: {state["risk"]:.3f}
- Discipline: {state["discipline"]:.3f}

Recommended career: {career}
Top 2 alternative careers: {alternatives[0]}, {alternatives[1]}

Tasks:
1. Explain why this career suits the user and which traits contributed most.
2. Identify weak traits and explain their impact on success.
3. Provide a step-by-step roadmap with skills, tools, and practical actions.

Constraints:
- Keep response concise and structured.
- No long paragraphs.
- Use bullet points.

Return only valid JSON in this exact shape:
{{
  "explanation": "...",
  "skill_gap": ["..."],
  "roadmap": ["..."]
}}
""".strip()


def _call_gemini(prompt: str) -> Dict[str, object]:
    """Call Gemini and return parsed JSON payload."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    url = GEMINI_API_URL_TEMPLATE.format(model=GEMINI_MODEL, api_key=api_key)
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "responseMimeType": "application/json",
        },
    }
    payload = json.dumps(body).encode("utf-8")
    req = request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=20) as resp:
        raw_response = json.loads(resp.read().decode("utf-8"))

    parts = raw_response["candidates"][0]["content"]["parts"]
    text = "".join(part.get("text", "") for part in parts)
    parsed = _extract_json_object(text)
    return _validate_advice_payload(parsed)


def generate_advice(state: Dict[str, float], career: str) -> Dict[str, object]:
    """Generate advisor output using Gemini, fallback locally on failures."""
    top_matches = get_top_careers(state)
    alternatives = [item["role"] for item in top_matches if item["role"] != career][:2]
    if len(alternatives) < 2:
        alternatives = [item["role"] for item in top_matches[:2]]

    prompt = _build_prompt(state=state, career=career, alternatives=alternatives)
    try:
        return _call_gemini(prompt)
    except (RuntimeError, KeyError, ValueError, json.JSONDecodeError, error.URLError) as exc:
        logger.warning("Gemini advice generation failed, using fallback: %s", exc)
        return _build_fallback_advice(state=state, career=career, alternatives=alternatives)
