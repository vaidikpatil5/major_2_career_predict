"""Adaptive question selector with uncertainty targeting and information-gain scoring."""

import math
import random
from collections import Counter
from typing import Dict, Iterable, Mapping, Optional, Set, Tuple

from bayesian import update_state
from data import questions

MIN_QUESTIONS = 5
MAX_QUESTIONS = 10
EARLY_STAGE_QUESTIONS = 4
TARGET_TRAIT_EXPOSURE = 2
DOMINANT_TRAIT_THRESHOLD = 0.40
UNCERTAINTY_STOP_THRESHOLD = 0.56


def _binary_entropy(probability: float) -> float:
    """Return normalized entropy for p in [0, 1]."""
    p = max(0.0, min(1.0, probability))
    if p in (0.0, 1.0):
        return 0.0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def calculate_uncertainty(state: Dict[str, float]) -> float:
    """Aggregate uncertainty across traits."""
    if not state:
        return 0.0
    return sum(_binary_entropy(value) for value in state.values()) / len(state)


def _normalize_scores(scores: Mapping[object, float]) -> Dict[object, float]:
    """Convert arbitrary non-negative scores to a probability distribution."""
    cleaned = {key: max(0.0, float(value)) for key, value in scores.items()}
    total = sum(cleaned.values())
    if total <= 0:
        uniform_prob = 1.0 / len(cleaned) if cleaned else 0.0
        return {key: uniform_prob for key in cleaned}
    return {key: value / total for key, value in cleaned.items()}


def _weight_map_affinity(state: Dict[str, float], weight_map: Mapping[str, float]) -> float:
    """
    Compute how likely an answer branch is, given current trait state.

    Higher state values on strongly weighted traits increase branch affinity.
    """
    if not weight_map:
        return 0.0
    affinity = 0.0
    for trait, weight in weight_map.items():
        if trait in state:
            affinity += max(0.0, float(weight)) * max(0.0, float(state[trait]))
    return affinity


def _estimate_answer_distribution(state: Dict[str, float], question: dict) -> Dict[object, float]:
    """Estimate probabilities of possible answers for a question."""
    question_type = question.get("type")

    if question_type == "scale":
        trait = question.get("trait")
        trait_value = float(state.get(trait, 0.5))
        scores = {
            1: (1.0 - trait_value) * 0.95,
            2: (1.0 - trait_value) * 0.70,
            3: 0.45,
            4: trait_value * 0.70,
            5: trait_value * 0.95,
        }
        return _normalize_scores(scores)

    if question_type == "binary":
        weights = question.get("weights", {})
        yes_weights = weights.get("yes", {}) if isinstance(weights, Mapping) else {}
        no_weights = weights.get("no", {}) if isinstance(weights, Mapping) else {}
        scores = {
            "yes": _weight_map_affinity(state, yes_weights) + 0.05,
            "no": _weight_map_affinity(state, no_weights) + 0.05,
        }
        return _normalize_scores(scores)

    if question_type == "mcq":
        options = question.get("weights", [])
        if not isinstance(options, list) or not options:
            return {}
        scores = {}
        for index, option_weight_map in enumerate(options):
            if isinstance(option_weight_map, Mapping):
                scores[index] = _weight_map_affinity(state, option_weight_map) + 0.05
            else:
                scores[index] = 0.05
        return _normalize_scores(scores)

    return {}


def _expected_entropy_after_question(state: Dict[str, float], question: dict) -> float:
    """Simulate all likely answers and return expected post-question uncertainty."""
    answer_distribution = _estimate_answer_distribution(state, question)
    if not answer_distribution:
        return calculate_uncertainty(state)

    expected_uncertainty = 0.0
    for answer, probability in answer_distribution.items():
        try:
            simulated_state = update_state(state=state, question=question, answer=answer)
        except ValueError:
            continue
        expected_uncertainty += probability * calculate_uncertainty(simulated_state)

    if expected_uncertainty <= 0:
        return calculate_uncertainty(state)
    return expected_uncertainty


def _information_gain(state: Dict[str, float], question: dict) -> float:
    """Expected reduction in uncertainty if we ask this question next."""
    current_uncertainty = calculate_uncertainty(state)
    expected_uncertainty = _expected_entropy_after_question(state, question)
    return max(0.0, current_uncertainty - expected_uncertainty)


def _question_target_traits(question: dict) -> Set[str]:
    """Extract all traits influenced by a question."""
    question_type = question.get("type")
    if question_type == "scale":
        trait = question.get("trait")
        return {trait} if trait else set()

    target_traits: Set[str] = set()
    if question_type == "binary":
        weights = question.get("weights", {})
        for branch in ("yes", "no"):
            branch_weights = weights.get(branch, {})
            target_traits.update(branch_weights.keys())
        return target_traits

    if question_type == "mcq":
        for option_weight in question.get("weights", []):
            if isinstance(option_weight, dict):
                target_traits.update(option_weight.keys())
    return target_traits


def _asked_trait_counts(asked_question_ids: Set[str]) -> Counter:
    """Count how often each trait has been targeted so far."""
    counts: Counter = Counter()
    if not asked_question_ids:
        return counts

    question_lookup = {question["id"]: question for question in questions}
    for question_id in asked_question_ids:
        question = question_lookup.get(question_id)
        if not question:
            continue
        for trait in _question_target_traits(question):
            counts[trait] += 1
    return counts


def _type_preference(question_type: str, questions_asked: int) -> float:
    """Prefer broader question types early, scale refinement later."""
    if questions_asked < EARLY_STAGE_QUESTIONS:
        preferences = {"mcq": 1.0, "binary": 0.9, "scale": 0.55}
    elif questions_asked < 7:
        preferences = {"mcq": 0.85, "binary": 0.8, "scale": 0.8}
    else:
        preferences = {"mcq": 0.75, "binary": 0.75, "scale": 1.0}
    return preferences.get(question_type, 0.5)


def _trait_coverage_bonus(target_traits: Set[str], trait_counts: Counter) -> float:
    """
    Reward questions that improve coverage of under-observed traits.

    Score is normalized to 0..1 based on remaining exposure deficit.
    """
    if not target_traits:
        return 0.0

    deficits = [max(0, TARGET_TRAIT_EXPOSURE - trait_counts.get(trait, 0)) for trait in target_traits]
    if not deficits:
        return 0.0

    mean_deficit = sum(deficits) / len(deficits)
    return min(1.0, mean_deficit / TARGET_TRAIT_EXPOSURE)


def _repeat_penalty(target_traits: Set[str], trait_counts: Counter, questions_asked: int) -> float:
    """Penalize over-targeting the same traits, especially in early stage."""
    if not target_traits:
        return 0.0
    if questions_asked < EARLY_STAGE_QUESTIONS:
        return max((trait_counts.get(trait, 0) for trait in target_traits), default=0) * 0.14
    return sum(trait_counts.get(trait, 0) for trait in target_traits) * 0.05


def _target_uncertainty_score(state: Dict[str, float], target_traits: Set[str]) -> float:
    """Uncertainty score focused on traits affected by this question."""
    if not target_traits:
        return 0.0
    uncertainties = [_binary_entropy(state.get(trait, 0.5)) for trait in target_traits]
    return sum(uncertainties) / len(uncertainties)


def _exploration_rate(questions_asked: int) -> float:
    """Use more exploration early and taper it as we gather evidence."""
    if questions_asked < EARLY_STAGE_QUESTIONS:
        return 0.10
    if questions_asked < 7:
        return 0.06
    return 0.03


def should_stop(state: Dict[str, float], questions_asked: int) -> bool:
    """Return True when minimum evidence is collected and confidence is strong enough."""
    if questions_asked >= MAX_QUESTIONS:
        return True
    if questions_asked < MIN_QUESTIONS:
        return False
    if not state:
        return False

    dominant_trait = max(state.values())
    uncertainty = calculate_uncertainty(state)
    return dominant_trait >= DOMINANT_TRAIT_THRESHOLD and uncertainty <= UNCERTAINTY_STOP_THRESHOLD


def select_next_question(
    state: Dict[str, float],
    asked_question_ids: Iterable[str],
    questions_asked: int,
) -> Optional[dict]:
    """
    Select the next question with mixed exploration/exploitation.

    Exploration: random unasked question at a small, stage-aware rate.
    Exploitation: score-based selection balancing expected information gain,
    trait coverage, targeted uncertainty, and question-type progression.
    """
    if should_stop(state, questions_asked):
        return None

    asked_lookup = set(asked_question_ids)
    unasked_questions = [question for question in questions if question["id"] not in asked_lookup]
    if not unasked_questions:
        return None

    if random.random() < _exploration_rate(questions_asked):
        return random.choice(unasked_questions)

    trait_counts = _asked_trait_counts(asked_lookup)
    scored_candidates: list[Tuple[float, dict]] = []

    for question in unasked_questions:
        target_traits = _question_target_traits(question)
        info_gain = _information_gain(state, question)
        uncertainty_score = _target_uncertainty_score(state, target_traits)
        coverage_bonus = _trait_coverage_bonus(target_traits, trait_counts)
        repeat_penalty = _repeat_penalty(target_traits, trait_counts, questions_asked)
        type_score = _type_preference(question.get("type", ""), questions_asked)

        final_score = (
            (0.45 * info_gain)
            + (0.25 * uncertainty_score)
            + (0.20 * coverage_bonus)
            + (0.10 * type_score)
            - repeat_penalty
        )
        scored_candidates.append((final_score, question))

    if scored_candidates:
        scored_candidates.sort(key=lambda item: item[0], reverse=True)
        return scored_candidates[0][1]
    return random.choice(unasked_questions)
