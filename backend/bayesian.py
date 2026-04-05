"""Bayesian inference helpers for trait-state updates."""

from typing import Dict

from data import traits


def initial_state() -> Dict[str, float]:
    """Return the fixed prior used for every new assessment."""
    return {trait: 0.5 for trait in traits}


def normalize_state(state: Dict[str, float]) -> Dict[str, float]:
    """Normalize the trait state so the values sum to 1."""
    total = sum(state.values())
    if total <= 0:
        return initial_state()
    return {trait: value / total for trait, value in state.items()}


def update_state(
    state: Dict[str, float],
    trait: str,
    answer: int,
    likelihoods: Dict[str, float],
) -> Dict[str, float]:
    """Apply the requested Bayesian update and renormalize the full state."""
    answer_key = str(answer)
    if answer_key not in likelihoods:
        raise ValueError(f"Invalid answer {answer}; expected an integer from 1 to 5.")
    if trait not in state:
        raise ValueError(f"Unknown trait '{trait}'.")

    updated_state = dict(state)
    updated_state[trait] = updated_state[trait] * likelihoods[answer_key]
    return normalize_state(updated_state)
