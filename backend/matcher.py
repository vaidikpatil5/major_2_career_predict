"""Career matching using cosine similarity."""

from typing import Dict, List, Optional

import numpy as np

from data import careers, traits

CAREER_MAX_SCALE = 10.0
DEFAULT_TRAIT_WEIGHT = 0.75
DEFAULT_CAREER_SIGNAL_WEIGHT = 0.25


def state_to_vector(state: Dict[str, float]) -> np.ndarray:
    """Convert trait-state values into a dense vector in 0..1 space."""
    return np.array([state[trait] for trait in traits], dtype=float)


def career_to_vector(career_vector: List[int]) -> np.ndarray:
    """Convert career vectors from 1..10 scale to 0..1 scale."""
    return np.array(career_vector, dtype=float) / CAREER_MAX_SCALE


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    """Compute cosine similarity for two non-zero vectors."""
    left_norm = np.linalg.norm(left)
    right_norm = np.linalg.norm(right)
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return float(np.dot(left, right) / (left_norm * right_norm))


def _career_signal_score(career_signal: Dict[str, float], role: str) -> float:
    """Read per-role career evidence in 0..1 range."""
    raw_value = float(career_signal.get(role, 0.0))
    return max(0.0, min(1.0, raw_value))


def _effective_weights(career_signal: Optional[Dict[str, float]]) -> tuple[float, float]:
    """Disable career signal blending when no signal is present."""
    if not career_signal or sum(float(value) for value in career_signal.values()) <= 0:
        return 1.0, 0.0
    total = DEFAULT_TRAIT_WEIGHT + DEFAULT_CAREER_SIGNAL_WEIGHT
    return DEFAULT_TRAIT_WEIGHT / total, DEFAULT_CAREER_SIGNAL_WEIGHT / total


def score_careers(state: Dict[str, float], career_signal: Optional[Dict[str, float]] = None) -> List[Dict[str, float]]:
    """Return scored careers with transparent trait/signal component breakdown."""
    state_vector = state_to_vector(state)
    signal_state = career_signal or {}
    trait_weight, signal_weight = _effective_weights(signal_state)
    scored_careers: List[Dict[str, float]] = []

    for career in careers:
        career_vector = career_to_vector(career["vector"])
        trait_score = cosine_similarity(state_vector, career_vector)
        signal_score = _career_signal_score(signal_state, career["role"])
        blended_score = (trait_weight * trait_score) + (signal_weight * signal_score)
        scored_careers.append(
            {
                "role": career["role"],
                "score": round(blended_score, 4),
                "trait_score": round(trait_score, 4),
                "career_signal_score": round(signal_score, 4),
                "blended_score": round(blended_score, 4),
            }
        )

    scored_careers.sort(key=lambda item: item["score"], reverse=True)
    return scored_careers


def get_top_careers(
    state: Dict[str, float],
    career_signal: Optional[Dict[str, float]] = None,
    top_n: int = 3,
) -> List[Dict[str, float]]:
    """Return top careers sorted by blended matching score."""
    return score_careers(state=state, career_signal=career_signal)[:top_n]
