"""Bayesian inference helpers for trait-state and career-signal updates."""

from typing import Any, Dict, Mapping

from data import careers, traits

# P(answer | trait is HIGH) — proper Bayesian likelihoods for scale questions.
# Answer 3 (neutral) gives 50/50 evidence. Answers 1–2 reduce trait belief,
# answers 4–5 increase it. These are NOT multipliers — they are probabilities.
SCALE_LIKELIHOODS: Dict[str, float] = {
    "1": 0.10,  # strongly disagree  → very unlikely if trait is high
    "2": 0.25,  # disagree           → unlikely if trait is high
    "3": 0.50,  # neutral            → equal evidence either way
    "4": 0.75,  # agree              → likely if trait is high
    "5": 0.90,  # strongly agree     → very likely if trait is high
}
# P(answer = high | trait is NOT high) — uniform baseline for all answers.
SCALE_BASELINE = 0.20
WEIGHT_LEARNING_RATE = 0.35
CAREER_LEARNING_RATE = 0.45


def initial_state() -> Dict[str, float]:
    """Return the fixed prior used for every new assessment."""
    return {trait: 0.5 for trait in traits}


def initial_career_signal() -> Dict[str, float]:
    """Return neutral per-career evidence scores for a new assessment."""
    return {career["role"]: 0.0 for career in careers}


def _clamp_probability(value: float) -> float:
    """Clamp any score-like value to probability bounds."""
    return max(0.0, min(1.0, value))


def _clamp_non_negative(value: float) -> float:
    """Clamp values for non-probability score tracks (>=0)."""
    return max(0.0, value)


def normalize_state(state: Dict[str, float]) -> Dict[str, float]:
    """Clamp each trait independently to [0, 1].

    Traits represent independent Bayesian beliefs — they are NOT a probability
    distribution and must NOT be forced to sum to 1. Dividing by the total
    creates false competition: increasing analytical would silently decrease
    social/creativity/risk even without any evidence about those traits.
    """
    return {trait: _clamp_probability(state.get(trait, 0.0)) for trait in traits}


def _validate_trait_weights(weight_map: Mapping[str, float], state: Dict[str, float]) -> None:
    for trait in weight_map:
        if trait not in state:
            raise ValueError(f"Question references unknown trait '{trait}'.")


def _validate_career_weights(weight_map: Mapping[str, float], career_signal: Dict[str, float]) -> None:
    for role in weight_map:
        if role not in career_signal:
            raise ValueError(f"Question references unknown career '{role}'.")


def _apply_weight_updates(
    state: Dict[str, float],
    weight_map: Mapping[str, float],
    learning_rate: float = WEIGHT_LEARNING_RATE,
) -> Dict[str, float]:
    """
    Increase weighted traits using a bounded additive update.

    Higher weight pushes traits toward 1.0 more strongly.
    """
    _validate_trait_weights(weight_map, state)
    updated_state = dict(state)

    for trait, weight in weight_map.items():
        bounded_weight = _clamp_probability(float(weight))
        current_value = updated_state[trait]
        delta = learning_rate * bounded_weight * (1.0 - current_value)
        updated_state[trait] = _clamp_probability(current_value + delta)

    return updated_state


def _apply_career_weight_updates(
    career_signal: Dict[str, float],
    weight_map: Mapping[str, float],
    learning_rate: float = CAREER_LEARNING_RATE,
) -> Dict[str, float]:
    """
    Increase per-career evidence with bounded additive updates.

    Scores remain in [0, 1] and accumulate soft evidence over multiple answers.
    """
    _validate_career_weights(weight_map, career_signal)
    updated_signal = dict(career_signal)

    for role, weight in weight_map.items():
        bounded_weight = _clamp_probability(float(weight))
        current_value = _clamp_non_negative(updated_signal[role])
        delta = learning_rate * bounded_weight * (1.0 - current_value)
        updated_signal[role] = _clamp_probability(current_value + delta)

    return updated_signal


def update_state(
    state: Dict[str, float],
    question: Mapping[str, Any],
    answer: Any,
) -> Dict[str, float]:
    """Apply a type-aware update and renormalize the full state."""
    question_type = question.get("type")
    if question_type not in {"scale", "binary", "mcq"}:
        raise ValueError(f"Unsupported question type '{question_type}'.")

    updated_state = dict(state)

    if question_type == "scale":
        trait = question.get("trait")
        if trait not in updated_state:
            raise ValueError(f"Unknown trait '{trait}'.")
        if not isinstance(answer, int) or isinstance(answer, bool) or not (1 <= answer <= 5):
            raise ValueError("Invalid scale answer; expected an integer from 1 to 5.")

        likelihoods = question.get("likelihood", SCALE_LIKELIHOODS)
        answer_key = str(answer)
        if answer_key not in likelihoods:
            raise ValueError(f"Invalid scale answer {answer}; expected an integer from 1 to 5.")

        # Proper Bayesian update: posterior = P(trait=high | answer)
        # = P(answer | trait=high) * prior / P(answer)
        prior = updated_state[trait]
        lk = float(likelihoods[answer_key])                    # P(answer | trait=high)
        denom = lk * prior + SCALE_BASELINE * (1.0 - prior)   # P(answer)
        posterior = (lk * prior) / denom if denom > 0 else prior
        updated_state[trait] = _clamp_probability(posterior)
        return normalize_state(updated_state)

    if question_type == "binary":
        if not isinstance(answer, str):
            raise ValueError("Invalid binary answer; expected 'yes' or 'no'.")

        answer_key = answer.strip().lower()
        if answer_key not in {"yes", "no"}:
            raise ValueError("Invalid binary answer; expected 'yes' or 'no'.")

        weights = question.get("weights")
        if not isinstance(weights, Mapping):
            raise ValueError("Binary question misconfigured: missing yes/no weights.")
        selected_weights = weights.get(answer_key)
        if not isinstance(selected_weights, Mapping):
            raise ValueError(f"Binary question misconfigured: missing '{answer_key}' weights.")

        updated_state = _apply_weight_updates(updated_state, selected_weights)
        return normalize_state(updated_state)

    # MCQ
    if not isinstance(answer, int) or isinstance(answer, bool):
        raise ValueError("Invalid mcq answer; expected an integer option index.")

    option_weights = question.get("weights")
    if not isinstance(option_weights, list):
        raise ValueError("MCQ misconfigured: missing option weights.")
    if answer < 0 or answer >= len(option_weights):
        raise ValueError(f"Invalid mcq answer {answer}; expected index in [0, {len(option_weights) - 1}].")
    selected_weights = option_weights[answer]
    if not isinstance(selected_weights, Mapping):
        raise ValueError("MCQ misconfigured: selected option weights must be a trait map.")

    updated_state = _apply_weight_updates(updated_state, selected_weights)
    return normalize_state(updated_state)


def update_career_signal(
    career_signal: Dict[str, float],
    question: Mapping[str, Any],
    answer: Any,
) -> Dict[str, float]:
    """Apply answer updates for career-based MCQ items."""
    question_type = question.get("type")
    if question_type != "mcq":
        raise ValueError("Career-signal updates currently support only mcq questions.")

    if not isinstance(answer, int) or isinstance(answer, bool):
        raise ValueError("Invalid career mcq answer; expected an integer option index.")

    option_weights = question.get("career_weights")
    if not isinstance(option_weights, list):
        raise ValueError("Career question misconfigured: missing option career weights.")
    if answer < 0 or answer >= len(option_weights):
        raise ValueError(
            f"Invalid career mcq answer {answer}; expected index in [0, {len(option_weights) - 1}]."
        )

    selected_weights = option_weights[answer]
    if not isinstance(selected_weights, Mapping):
        raise ValueError("Career question misconfigured: selected option must map careers to weights.")

    return _apply_career_weight_updates(career_signal, selected_weights)
