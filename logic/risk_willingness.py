"""
Risk Willingness Survey Module

Calculates an investor's risk willingness score (psychological/emotional comfort
with investment risk) through a 10-question survey across 3 categories.

The willingness score is intended to be used alongside a capacity score to
determine a target portfolio allocation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


# ============================================
# QUESTION DEFINITIONS
# ============================================

QUESTIONS = {
    "Q1": {
        "category": "loss_aversion",
        "prompt": "Your portfolio drops 20% in a single month. What do you do?",
        "weight": 1.5,
        "choices": [
            {"key": "a", "text": "Sell everything and move to cash", "points": 1},
            {"key": "b", "text": "Sell some to reduce further losses", "points": 2},
            {"key": "c", "text": "Hold and wait for recovery", "points": 3},
            {"key": "d", "text": "Buy more at the lower prices", "points": 4},
        ],
        "max_points": 4,
    },
    "Q2": {
        "category": "loss_aversion",
        "prompt": "You invest $100,000. After one year it's worth $85,000. How do you feel?",
        "weight": 1.5,
        "choices": [
            {"key": "a", "text": "I can't sleep at night, I need to get out", "points": 1},
            {"key": "b", "text": "Very uncomfortable, I'm questioning my strategy", "points": 2},
            {"key": "c", "text": "Disappointed but I understand markets fluctuate", "points": 3},
            {"key": "d", "text": "Unfazed, this is normal and I see an opportunity", "points": 4},
        ],
        "max_points": 4,
    },
    "Q3": {
        "category": "loss_aversion",
        "prompt": "Which scenario would bother you more?",
        "weight": 1.5,
        "choices": [
            {"key": "a", "text": "Losing $5,000 on an investment", "points": 1},
            {"key": "b", "text": "Both would bother me equally", "points": 2},
            {"key": "c", "text": "Missing out on a $5,000 gain by not investing", "points": 3},
        ],
        "max_points": 3,
    },
    "Q4": {
        "category": "loss_aversion",
        "prompt": "Your portfolio has gained 25% over two years. News suggests a possible recession ahead. What do you do?",
        "weight": 1.5,
        "choices": [
            {"key": "a", "text": "Sell and lock in the gains", "points": 1},
            {"key": "b", "text": "Sell half to protect some profits", "points": 2},
            {"key": "c", "text": "Stay the course with my current allocation", "points": 3},
            {"key": "d", "text": "Maintain or increase equity, since I'm investing for the long run", "points": 4},
        ],
        "max_points": 4,
    },
    "Q5": {
        "category": "self_assessment",
        "prompt": "Which statement best describes you as an investor?",
        "weight": 1.0,
        "choices": [
            {"key": "a", "text": "I want to preserve my capital above all else", "points": 1},
            {"key": "b", "text": "I want mostly stability with a small amount of growth", "points": 2},
            {"key": "c", "text": "I want balanced growth and am willing to accept moderate ups and downs", "points": 3},
            {"key": "d", "text": "I want maximum growth and can handle significant volatility", "points": 4},
        ],
        "max_points": 4,
    },
    "Q6": {
        "category": "self_assessment",
        "prompt": "When making important financial decisions, how would you characterize your approach?",
        "weight": 1.0,
        "choices": [
            {"key": "a", "text": "I avoid risk whenever possible", "points": 1},
            {"key": "b", "text": "I'm cautious but open to modest risk for better returns", "points": 2},
            {"key": "c", "text": "I'm comfortable weighing risk against potential reward", "points": 3},
            {"key": "d", "text": "I actively seek higher-risk, higher-reward opportunities", "points": 4},
        ],
        "max_points": 4,
    },
    "Q7": {
        "category": "self_assessment",
        "prompt": "Compared to others, how much financial risk are you willing to take?",
        "weight": 1.0,
        "choices": [
            {"key": "a", "text": "Much less than average", "points": 1},
            {"key": "b", "text": "Slightly less than average", "points": 2},
            {"key": "c", "text": "About average", "points": 3},
            {"key": "d", "text": "More than average", "points": 4},
        ],
        "max_points": 4,
    },
    "Q8": {
        "category": "experience_gambles",
        "prompt": "Choose one investment for a $50,000 lump sum:",
        "weight": 1.0,
        "choices": [
            {"key": "a", "text": "Guaranteed 3% annual return", "points": 1},
            {"key": "b", "text": "70% chance of 7% return, 30% chance of 2% return", "points": 2},
            {"key": "c", "text": "50% chance of 12% return, 50% chance of 0% return", "points": 3},
            {"key": "d", "text": "30% chance of 25% return, 70% chance of losing 5%", "points": 4},
        ],
        "max_points": 4,
    },
    "Q9": {
        "category": "experience_gambles",
        "prompt": "Think about the worst market downturn you've personally experienced (e.g., COVID crash 2020, 2022 drawdown). What did you actually do?",
        "weight": 1.0,  # default; overridden to 0.5 if 'e' is chosen
        "choices": [
            {"key": "a", "text": "I sold most or all of my holdings", "points": 1},
            {"key": "b", "text": "I reduced my positions meaningfully", "points": 2},
            {"key": "c", "text": "I held steady and did nothing", "points": 3},
            {"key": "d", "text": "I added to my positions", "points": 4},
            {"key": "e", "text": "I haven't experienced a major downturn yet", "points": 2.5},
        ],
        "max_points": 4,
        "special_key": "e",  # triggers reduced weight
        "special_weight": 0.5,
    },
    "Q10": {
        "category": "experience_gambles",
        "prompt": "How many years of investment experience do you have across equities, bonds, or alternatives?",
        "weight": 0.75,
        "choices": [
            {"key": "a", "text": "Less than 2 years", "points": 1},
            {"key": "b", "text": "2–5 years", "points": 2},
            {"key": "c", "text": "5–15 years", "points": 3},
            {"key": "d", "text": "More than 15 years", "points": 4},
        ],
        "max_points": 4,
    },
}

# Category definitions for grouping
CATEGORIES = {
    "loss_aversion": {
        "label": "Loss Aversion",
        "questions": ["Q1", "Q2", "Q3", "Q4"],
        "description": "Strongest predictors of actual portfolio behavior",
    },
    "self_assessment": {
        "label": "Self-Assessment",
        "questions": ["Q5", "Q6", "Q7"],
        "description": "How the investor perceives their own risk tolerance",
    },
    "experience_gambles": {
        "label": "Gambles & Experience",
        "questions": ["Q8", "Q9", "Q10"],
        "description": "Hypothetical choices and real-world investment experience",
    },
}

# Willingness level mapping
WILLINGNESS_LEVELS = [
    {"min": 0, "max": 25, "level": "low", "label": "Conservative"},
    {"min": 26, "max": 50, "level": "moderate", "label": "Balanced"},
    {"min": 51, "max": 75, "level": "moderately_high", "label": "Growth"},
    {"min": 76, "max": 100, "level": "high", "label": "Aggressive"},
]

# ============================================
# SCORING ENGINE
# ============================================


def _get_effective_weight(q_id: str, selected_key: str) -> float:
    """Return the effective weight for a question given the selected answer."""
    q = QUESTIONS[q_id]
    if q.get("special_key") and selected_key == q["special_key"]:
        return q["special_weight"]
    return q["weight"]


def _get_points(q_id: str, selected_key: str) -> float:
    """Return the points for the selected answer key."""
    q = QUESTIONS[q_id]
    for choice in q["choices"]:
        if choice["key"] == selected_key:
            return choice["points"]
    raise ValueError(f"Invalid answer key '{selected_key}' for question {q_id}")


def _compute_category_scores(
    answers: Dict[str, str],
) -> Dict[str, Dict[str, float]]:
    """
    Compute raw and normalized scores per category.

    Returns dict keyed by category name with raw, max, and normalized values.
    """
    category_scores: Dict[str, Dict[str, float]] = {}

    for cat_key, cat_info in CATEGORIES.items():
        raw = 0.0
        max_raw = 0.0
        min_raw = 0.0

        for q_id in cat_info["questions"]:
            if q_id not in answers:
                continue
            selected_key = answers[q_id]
            points = _get_points(q_id, selected_key)
            weight = _get_effective_weight(q_id, selected_key)
            q = QUESTIONS[q_id]

            raw += points * weight
            max_raw += q["max_points"] * weight
            # Minimum possible for this question
            min_points = min(c["points"] for c in q["choices"])
            min_raw += min_points * weight

        if max_raw - min_raw > 0:
            normalized = ((raw - min_raw) / (max_raw - min_raw)) * 100
        else:
            normalized = 0.0

        category_scores[cat_key] = {
            "raw": round(raw, 2),
            "max": round(max_raw, 2),
            "min": round(min_raw, 2),
            "normalized": round(normalized, 1),
        }

    return category_scores


def _detect_flags(
    answers: Dict[str, str],
    category_scores: Dict[str, Dict[str, float]],
    normalized_score: float,
) -> List[str]:
    """
    Detect consistency flags for advisor review.

    1. Loss aversion vs. self-assessment mismatch (>40 point difference)
    2. Past behavior vs. hypothetical mismatch (Q9 < Q1 by 2+ points)
    3. Low experience + high risk appetite (Q10 = 1 and normalized > 75)
    """
    flags: List[str] = []

    # Flag 1: Loss aversion vs self-assessment mismatch
    la_norm = category_scores.get("loss_aversion", {}).get("normalized", 50)
    sa_norm = category_scores.get("self_assessment", {}).get("normalized", 50)
    if abs(la_norm - sa_norm) > 40:
        if sa_norm > la_norm:
            flags.append(
                "Inconsistency: self-assessment indicates higher risk tolerance "
                "than loss-aversion scenario responses suggest. "
                f"(Self-assessment: {sa_norm:.0f}, Loss aversion: {la_norm:.0f})"
            )
        else:
            flags.append(
                "Inconsistency: loss-aversion scenario responses suggest higher "
                "risk tolerance than self-assessment indicates. "
                f"(Self-assessment: {sa_norm:.0f}, Loss aversion: {la_norm:.0f})"
            )

    # Flag 2: Past behavior vs hypothetical mismatch
    if "Q1" in answers and "Q9" in answers:
        q1_points = _get_points("Q1", answers["Q1"])
        q9_points = _get_points("Q9", answers["Q9"])
        if q1_points - q9_points >= 2:
            flags.append(
                "Past behavior vs. hypothetical mismatch: investor's actual past "
                "downturn behavior (Q9) is significantly more conservative than "
                "their stated hypothetical reaction (Q1). Past behavior is more "
                "predictive — consider biasing toward actual experience."
            )

    # Flag 3: Low experience + high risk appetite
    if "Q10" in answers:
        q10_points = _get_points("Q10", answers["Q10"])
        if q10_points == 1 and normalized_score > 75:
            flags.append(
                "Limited experience may not support stated risk appetite: "
                "investor has less than 2 years of experience but scores as "
                "aggressive. Consider a more conservative initial allocation "
                "with a plan to reassess as experience grows."
            )

    return flags


def _apply_behavioral_bias(
    answers: Dict[str, str],
    weighted_score: float,
    min_score: float,
    max_score: float,
) -> float:
    """
    If Q9 (actual past behavior) is 2+ points lower than Q1 (hypothetical),
    bias the final score toward Q9 by adjusting the weighted_score downward.

    Returns the (possibly adjusted) weighted_score.
    """
    if "Q1" not in answers or "Q9" not in answers:
        return weighted_score

    q1_points = _get_points("Q1", answers["Q1"])
    q9_points = _get_points("Q9", answers["Q9"])

    if q1_points - q9_points >= 2:
        # Penalize: shift weighted_score toward the lower (Q9-based) end
        # We replace Q1's contribution with Q9's contribution
        q1_weight = QUESTIONS["Q1"]["weight"]
        original_q1_contribution = q1_points * q1_weight
        biased_q1_contribution = q9_points * q1_weight
        adjustment = original_q1_contribution - biased_q1_contribution
        weighted_score -= adjustment

    return weighted_score


def score_survey(answers: Dict[str, str]) -> Dict[str, Any]:
    """
    Score a completed risk willingness survey.

    Args:
        answers: Dict mapping question IDs (e.g. "Q1") to selected answer keys
                 (e.g. "a", "b", "c", "d", or "e" for Q9).
                 All 10 questions must be answered.

    Returns:
        Dict with full scoring output including raw_score, normalized_score,
        willingness_level, category_scores, flags,
        and detailed answer breakdown.

    Raises:
        ValueError: If any required question is missing or has an invalid key.
    """
    # Validate all questions are answered
    for q_id in QUESTIONS:
        if q_id not in answers:
            raise ValueError(f"Missing answer for {q_id}")

    # Step 1: Calculate weighted score
    weighted_score = 0.0
    max_score = 0.0
    min_score = 0.0
    answer_details: Dict[str, Dict[str, Any]] = {}

    for q_id, q_def in QUESTIONS.items():
        selected_key = answers[q_id]
        points = _get_points(q_id, selected_key)
        weight = _get_effective_weight(q_id, selected_key)

        weighted_score += points * weight
        max_score += q_def["max_points"] * weight
        min_points = min(c["points"] for c in q_def["choices"])
        min_score += min_points * weight

        answer_details[q_id] = {
            "selected": selected_key,
            "points": points,
            "weight": weight,
        }

    # Step 2: Apply behavioral bias (Q9 vs Q1)
    weighted_score = _apply_behavioral_bias(
        answers, weighted_score, min_score, max_score
    )

    # Step 3: Normalize to 0–100
    if max_score - min_score > 0:
        normalized_score = ((weighted_score - min_score) / (max_score - min_score)) * 100
    else:
        normalized_score = 0.0

    # Clamp to [0, 100]
    normalized_score = max(0.0, min(100.0, normalized_score))

    # Step 4: Map to willingness level
    willingness_level = "moderate"
    willingness_label = "Balanced"
    for level_def in WILLINGNESS_LEVELS:
        if level_def["min"] <= normalized_score <= level_def["max"]:
            willingness_level = level_def["level"]
            willingness_label = level_def["label"]
            break

    # Category scores
    category_scores = _compute_category_scores(answers)

    # Consistency flags
    flags = _detect_flags(answers, category_scores, normalized_score)

    return {
        "raw_score": round(weighted_score, 2),
        "max_possible": round(max_score, 2),
        "min_possible": round(min_score, 2),
        "normalized_score": round(normalized_score, 1),
        "willingness_level": willingness_level,
        "willingness_label": willingness_label,
        "category_scores": category_scores,
        "flags": flags,
        "answers": answer_details,
    }


def get_questions() -> Dict[str, Any]:
    """Return the full question definitions for UI rendering."""
    return QUESTIONS


def get_categories() -> Dict[str, Any]:
    """Return category definitions."""
    return CATEGORIES
