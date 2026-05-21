# Updated: Fixed Bayesian update, Shannon entropy IG, O*NET career vectors /
"""Bayesian inference helpers for trait-state updates."""

from typing import Dict

from data import traits


def initial_state() -> Dict[str, float]:
    """Return the fixed prior used for every new assessment."""
    return {trait: 0.5 for trait in traits}


def bayesian_update(prior: float, likelihood: float) -> float:
    """Compute the Bayesian update for a single independent binary trait belief."""
    denom = likelihood * prior + 0.2 * (1.0 - prior)
    if denom == 0.0:
        return prior
    posterior = (likelihood * prior) / denom
    return max(0.001, min(0.999, posterior))


def update_state(
    state: Dict[str, float],
    trait: str,
    answer: int,
    likelihoods: Dict[str, float],
) -> Dict[str, float]:
    """Apply the requested Bayesian update to one trait, leaving other traits unchanged."""
    answer_key = str(answer)
    if answer_key not in likelihoods:
        raise ValueError(f"Invalid answer {answer}; expected an integer from 1 to 5.")
    if trait not in state:
        raise ValueError(f"Unknown trait '{trait}'.")

    updated_state = dict(state)
    prior = updated_state[trait]
    likelihood = likelihoods[answer_key]
    updated_state[trait] = bayesian_update(prior, likelihood)
    return updated_state

