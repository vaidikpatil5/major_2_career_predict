# Updated: Fixed Bayesian update, Shannon entropy IG, O*NET career vectors /
"""Adaptive question selector using simulation-based information gain."""

from typing import Dict, Iterable, Optional
import numpy as np

from bayesian import update_state
from data import questions

MAX_QUESTIONS = 10
MIN_QUESTIONS = 6


def entropy(state: Dict[str, float]) -> float:
    """Compute the sum of binary Shannon entropies across all independent trait beliefs."""
    p = np.array(list(state.values()), dtype=float)
    p = np.clip(p, 1e-9, 1.0 - 1e-9)
    return float(-np.sum(p * np.log2(p) + (1.0 - p) * np.log2(1.0 - p)))


def should_stop(state: Dict[str, float], questions_asked: int) -> bool:
    """Return True when the assessment meets its stopping condition.

    Stops when either:
    - questions_asked has reached MAX_QUESTIONS (hard cap), OR
    - at least MIN_QUESTIONS have been asked AND every trait is resolved,
      defined as: no trait value sits in the uncertain middle band [0.3, 0.7].

    This prevents premature exits from a single extreme answer while still
    allowing smart early termination once the full profile is clear.
    """
    if questions_asked >= MAX_QUESTIONS:
        return True
    if questions_asked < MIN_QUESTIONS:
        return False
    all_resolved = all(v < 0.3 or v > 0.7 for v in state.values())
    return all_resolved


def select_next_question(
    state: Dict[str, float],
    asked_question_ids: Iterable[str],
    questions_asked: int,
) -> Optional[dict]:
    """
    Select the unasked question with the highest expected information gain (Shannon entropy reduction).
    """
    if should_stop(state, questions_asked):
        return None

    asked_lookup = set(asked_question_ids)
    best_question: Optional[dict] = None
    best_ig = float("-inf")

    current_h = entropy(state)

    for question in questions:
        if question["id"] in asked_lookup:
            continue

        trait = question["trait"]
        prior_t = state[trait]
        likelihoods = question["likelihood"]

        expected_h = 0.0
        for simulated_answer in range(1, 6):
            p_a_given_t = likelihoods[str(simulated_answer)]
            p_a_given_not_t = 0.2
            p_a = p_a_given_t * prior_t + p_a_given_not_t * (1.0 - prior_t)

            simulated_state = update_state(
                state=state,
                trait=trait,
                answer=simulated_answer,
                likelihoods=likelihoods,
            )
            expected_h += p_a * entropy(simulated_state)

        ig = current_h - expected_h
        if ig > best_ig:
            best_ig = ig
            best_question = question

    return best_question

