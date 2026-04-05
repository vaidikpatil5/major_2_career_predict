"""Career matching using cosine similarity."""

from typing import Dict, List

import numpy as np

from data import careers, traits

CAREER_MAX_SCALE = 10.0


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


def get_top_careers(state: Dict[str, float]) -> List[Dict[str, float]]:
    """Return the top three matching careers sorted by cosine similarity."""
    state_vector = state_to_vector(state)
    scored_careers: List[Dict[str, float]] = []

    for career in careers:
        career_vector = career_to_vector(career["vector"])
        score = cosine_similarity(state_vector, career_vector)
        scored_careers.append(
            {
                "role": career["role"],
                "score": round(score, 4),
            }
        )

    scored_careers.sort(key=lambda item: item["score"], reverse=True)
    return scored_careers[:3]
