"""Adaptive question selector using simulation-based information gain."""

from typing import Dict, Iterable, Optional

from bayesian import update_state
from data import questions

MAX_QUESTIONS = 10


def calculate_uncertainty(state: Dict[str, float]) -> float:
    """Measure uncertainty exactly as requested: max(state) - min(state)."""
    values = state.values()
    return max(values) - min(values)


def should_stop(state: Dict[str, float], questions_asked: int) -> bool:
    """Return True when the assessment meets its stopping condition."""
    return max(state.values()) > 0.8 or questions_asked >= MAX_QUESTIONS


def select_next_question(
    state: Dict[str, float],
    asked_question_ids: Iterable[str],
    questions_asked: int,
) -> Optional[dict]:
    """
    Select the unasked question with the highest average simulated uncertainty.

    For every unasked question, simulate answers 1..5, update the state
    temporarily, calculate uncertainty, and average those values.
    """
    if should_stop(state, questions_asked):
        return None

    asked_lookup = set(asked_question_ids)
    best_question: Optional[dict] = None
    best_score = float("-inf")

    for question in questions:
        if question["id"] in asked_lookup:
            continue

        simulated_uncertainties = []
        for simulated_answer in range(1, 6):
            simulated_state = update_state(
                state=state,
                trait=question["trait"],
                answer=simulated_answer,
                likelihoods=question["likelihood"],
            )
            simulated_uncertainties.append(calculate_uncertainty(simulated_state))

        average_uncertainty = sum(simulated_uncertainties) / len(simulated_uncertainties)
        if average_uncertainty > best_score:
            best_score = average_uncertainty
            best_question = question

    return best_question
