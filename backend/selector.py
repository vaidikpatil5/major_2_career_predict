"""Adaptive question selector with uncertainty targeting and type balancing."""

import math
import random
from collections import Counter
from typing import Dict, Iterable, Optional, Set

from data import questions

CONFIDENCE_THRESHOLD = 0.75
MAX_QUESTIONS = 9
EARLY_STAGE_QUESTIONS = 4


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


def should_stop(state: Dict[str, float], questions_asked: int) -> bool:
    """Return True when the assessment meets its stopping condition."""
    if not state:
        return questions_asked >= MAX_QUESTIONS
    return max(state.values()) >= CONFIDENCE_THRESHOLD or questions_asked >= MAX_QUESTIONS


def select_next_question(
    state: Dict[str, float],
    asked_question_ids: Iterable[str],
    questions_asked: int,
) -> Optional[dict]:
    """
    Select the next question with mixed exploration/exploitation.

    20%: random unasked question (controlled randomness).
    80%: score-based selection that balances:
    - trait uncertainty targeting
    - early trait diversity (avoid repetition)
    - stage-aware question type preference
    """
    if should_stop(state, questions_asked):
        return None

    asked_lookup = set(asked_question_ids)
    unasked_questions = [question for question in questions if question["id"] not in asked_lookup]
    if not unasked_questions:
        return None

    if random.random() < 0.2:
        return random.choice(unasked_questions)

    trait_counts = _asked_trait_counts(asked_lookup)
    best_question: Optional[dict] = None
    best_score = float("-inf")

    for question in unasked_questions:
        target_traits = _question_target_traits(question)
        if not target_traits:
            continue

        trait_uncertainties = [_binary_entropy(state.get(trait, 0.5)) for trait in target_traits]
        uncertainty_score = max(trait_uncertainties) if trait_uncertainties else 0.0

        if questions_asked < EARLY_STAGE_QUESTIONS:
            repeat_penalty = max((trait_counts.get(trait, 0) for trait in target_traits), default=0) * 0.18
            diversity_bonus = 0.2 if any(trait_counts.get(trait, 0) == 0 for trait in target_traits) else 0.0
        else:
            repeat_penalty = sum(trait_counts.get(trait, 0) for trait in target_traits) * 0.06
            diversity_bonus = 0.0

        type_score = _type_preference(question.get("type", ""), questions_asked)
        final_score = (0.6 * uncertainty_score) + (0.3 * type_score) + diversity_bonus - repeat_penalty

        if final_score > best_score:
            best_score = final_score
            best_question = question

    if best_question is not None:
        return best_question
    return random.choice(unasked_questions)
