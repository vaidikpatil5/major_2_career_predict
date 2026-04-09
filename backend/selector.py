"""Adaptive question selector with uncertainty targeting and information-gain scoring."""

import math
import random
from collections import Counter
from typing import Any, Dict, Iterable, Mapping, Optional, Set, Tuple

from bayesian import update_state
from data import career_questions, questions
from matcher import get_top_careers

MIN_QUESTIONS = 5
MAX_QUESTIONS = 10
EARLY_STAGE_QUESTIONS = 4
TARGET_TRAIT_EXPOSURE = 2
DOMINANT_TRAIT_THRESHOLD = 0.40
UNCERTAINTY_STOP_THRESHOLD = 0.56
MIN_CAREER_QUESTIONS = 1
MAX_CAREER_QUESTIONS = 3
CAREER_TIEBREAK_MARGIN = 0.06

ALL_QUESTIONS = questions + career_questions
QUESTION_LOOKUP = {question["id"]: question for question in ALL_QUESTIONS}


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
        if question.get("career_weights") is not None:
            return set()
        for option_weight in question.get("weights", []):
            if isinstance(option_weight, dict):
                target_traits.update(option_weight.keys())
    return target_traits


def _is_career_question(question: dict) -> bool:
    """Return True for question items that contribute direct career evidence."""
    return question.get("career_weights") is not None


def _asked_trait_counts(asked_question_ids: Set[str]) -> Counter:
    """Count how often each trait has been targeted so far."""
    counts: Counter = Counter()
    if not asked_question_ids:
        return counts

    for question_id in asked_question_ids:
        question = QUESTION_LOOKUP.get(question_id)
        if not question:
            continue
        for trait in _question_target_traits(question):
            counts[trait] += 1
    return counts


def _asked_career_question_count(asked_question_ids: Set[str]) -> int:
    """Count number of career-based questions asked in a session."""
    return sum(1 for question_id in asked_question_ids if _is_career_question(QUESTION_LOOKUP.get(question_id, {})))


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


def _career_tiebreak_needed(state: Dict[str, float], career_signal: Optional[Dict[str, float]]) -> bool:
    """
    Return True when top blended careers are close enough to justify tie-break questions.
    """
    ranked = get_top_careers(state=state, career_signal=career_signal, top_n=2)
    if len(ranked) < 2:
        return False
    margin = ranked[0]["score"] - ranked[1]["score"]
    return margin <= CAREER_TIEBREAK_MARGIN


def _career_question_discrimination(question: dict, state: Dict[str, float], career_signal: Optional[Dict[str, float]]) -> float:
    """
    Measure how much a career question can separate the top two current candidates.
    """
    ranked = get_top_careers(state=state, career_signal=career_signal, top_n=2)
    if len(ranked) < 2:
        return 0.0
    top_role = ranked[0]["role"]
    second_role = ranked[1]["role"]

    option_weights = question.get("career_weights", [])
    if not isinstance(option_weights, list) or not option_weights:
        return 0.0

    max_delta = 0.0
    for weight_map in option_weights:
        if not isinstance(weight_map, Mapping):
            continue
        delta = abs(float(weight_map.get(top_role, 0.0)) - float(weight_map.get(second_role, 0.0)))
        if delta > max_delta:
            max_delta = delta
    return max_delta


def _career_question_score(
    question: dict,
    asked_career_questions: int,
    state: Dict[str, float],
    career_signal: Optional[Dict[str, float]],
) -> float:
    """
    Score career questions using discriminative power + stage-dependent priority.
    """
    discrimination = _career_question_discrimination(question, state=state, career_signal=career_signal)
    early_bonus = 0.2 if asked_career_questions < MIN_CAREER_QUESTIONS else 0.0
    diminishing = max(0.0, 0.25 - (asked_career_questions * 0.08))
    return (0.7 * discrimination) + early_bonus + diminishing


def should_stop(state: Dict[str, float], questions_asked: int, asked_career_questions: int = 0) -> bool:
    """Return True when minimum evidence is collected and confidence is strong enough."""
    if questions_asked >= MAX_QUESTIONS:
        return True
    if questions_asked < MIN_QUESTIONS:
        return False
    if asked_career_questions < MIN_CAREER_QUESTIONS:
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
    career_signal: Optional[Dict[str, float]] = None,
) -> Optional[dict]:
    """Backward-compatible selector that returns only the chosen question."""
    question, _ = select_next_question_with_debug(
        state=state,
        asked_question_ids=asked_question_ids,
        questions_asked=questions_asked,
        career_signal=career_signal,
    )
    return question


def select_next_question_with_debug(
    state: Dict[str, float],
    asked_question_ids: Iterable[str],
    questions_asked: int,
    career_signal: Optional[Dict[str, float]] = None,
) -> Tuple[Optional[dict], Dict[str, Any]]:
    """
    Select the next question with mixed exploration/exploitation.

    Exploration: random unasked question at a small, stage-aware rate.
    Exploitation: score-based selection balancing expected information gain,
    trait coverage, targeted uncertainty, and question-type progression.
    """
    debug: Dict[str, Any] = {
        "questions_asked": questions_asked,
        "current_uncertainty": round(calculate_uncertainty(state), 6),
    }
    asked_lookup = set(asked_question_ids)
    asked_career_questions = _asked_career_question_count(asked_lookup)
    debug["asked_career_questions"] = asked_career_questions

    if should_stop(state, questions_asked, asked_career_questions=asked_career_questions):
        debug["decision"] = "stop"
        debug["reason"] = "stopping_condition_met"
        return None, debug

    unasked_trait_questions = [question for question in questions if question["id"] not in asked_lookup]
    unasked_career_questions = [question for question in career_questions if question["id"] not in asked_lookup]
    force_early_career = questions_asked < 3 and asked_career_questions < MIN_CAREER_QUESTIONS
    force_min_career_coverage = questions_asked >= MIN_QUESTIONS and asked_career_questions < MIN_CAREER_QUESTIONS
    tie_break_mode = _career_tiebreak_needed(state=state, career_signal=career_signal)

    can_ask_career = asked_career_questions < MAX_CAREER_QUESTIONS and (
        force_early_career or force_min_career_coverage or tie_break_mode
    )
    force_career_only = force_early_career or force_min_career_coverage

    if force_career_only:
        # Guarantee career coverage when possible; otherwise degrade gracefully.
        if unasked_career_questions:
            unasked_questions = list(unasked_career_questions)
        else:
            unasked_questions = list(unasked_trait_questions)
            debug["career_force_fallback"] = "no_unasked_career_questions"
    else:
        unasked_questions = list(unasked_trait_questions)
        if can_ask_career:
            unasked_questions.extend(unasked_career_questions)

    debug["force_early_career"] = force_early_career
    debug["force_min_career_coverage"] = force_min_career_coverage
    debug["force_career_only"] = force_career_only
    debug["tie_break_mode"] = tie_break_mode
    debug["career_candidate_enabled"] = can_ask_career

    if not unasked_questions:
        debug["decision"] = "stop"
        debug["reason"] = "no_unasked_questions"
        return None, debug

    exploration_rate = _exploration_rate(questions_asked)
    debug["exploration_rate"] = round(exploration_rate, 4)
    if random.random() < exploration_rate:
        selected = random.choice(unasked_questions)
        debug["decision"] = "exploration"
        debug["selected_question_id"] = selected["id"]
        debug["selected_question_type"] = selected.get("type")
        debug["candidate_count"] = len(unasked_questions)
        return selected, debug

    trait_counts = _asked_trait_counts(asked_lookup)
    scored_candidates: list[Tuple[float, dict]] = []
    candidate_details = []

    for question in unasked_questions:
        if _is_career_question(question):
            final_score = _career_question_score(
                question=question,
                asked_career_questions=asked_career_questions,
                state=state,
                career_signal=career_signal,
            )
            scored_candidates.append((final_score, question))
            candidate_details.append(
                {
                    "question_id": question["id"],
                    "type": question.get("type"),
                    "kind": "career",
                    "targets": [],
                    "final_score": round(final_score, 6),
                    "components": {
                        "career_discrimination": round(
                            _career_question_discrimination(question, state=state, career_signal=career_signal), 6
                        ),
                        "asked_career_questions": asked_career_questions,
                    },
                }
            )
            continue

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
        candidate_details.append(
            {
                "question_id": question["id"],
                "type": question.get("type"),
                "kind": "trait",
                "targets": sorted(target_traits),
                "final_score": round(final_score, 6),
                "components": {
                    "info_gain": round(info_gain, 6),
                    "target_uncertainty": round(uncertainty_score, 6),
                    "coverage_bonus": round(coverage_bonus, 6),
                    "type_score": round(type_score, 6),
                    "repeat_penalty": round(repeat_penalty, 6),
                },
            }
        )

    if scored_candidates:
        scored_candidates.sort(key=lambda item: item[0], reverse=True)
        selected = scored_candidates[0][1]
        candidate_details.sort(key=lambda item: item["final_score"], reverse=True)

        debug["decision"] = "exploitation"
        debug["selected_question_id"] = selected["id"]
        debug["selected_question_type"] = selected.get("type")
        debug["candidate_count"] = len(candidate_details)
        debug["top_candidates"] = candidate_details[:5]
        return selected, debug

    fallback = random.choice(unasked_questions)
    debug["decision"] = "fallback_random"
    debug["selected_question_id"] = fallback["id"]
    debug["selected_question_type"] = fallback.get("type")
    debug["candidate_count"] = len(unasked_questions)
    return fallback, debug
