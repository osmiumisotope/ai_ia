"""
Unified Risk Assessment Module

Combines the Risk Willingness (psychological/emotional) and Risk Tolerance
(objective financial ability) scores into a single unified risk score, then
maps that score to a recommended portfolio allocation.

Unified score formula:
    unified = lower_score * 0.80 + higher_score * 0.20

The idea: the more conservative of the two dimensions dominates (80 %
weight), because an investor should not be placed in a portfolio that
exceeds *either* their emotional comfort or their financial capacity.

Portfolio profiles (9 levels, "Short Term" → "Most Aggressive") are each
mapped to a specific asset-class allocation table.
"""

from typing import Any, Dict, List, Optional, Tuple

# ============================================
# PORTFOLIO PROFILE DEFINITIONS
# ============================================

PROFILE_ORDER = [
    "short_term",
    "conservative",
    "moderate_with_income",
    "moderate",
    "balanced",
    "growth_with_income",
    "growth",
    "aggressive_growth",
    "most_aggressive",
]

PROFILE_LABELS = {
    "short_term": "Short Term",
    "conservative": "Conservative",
    "moderate_with_income": "Moderate with Income",
    "moderate": "Moderate",
    "balanced": "Balanced",
    "growth_with_income": "Growth with Income",
    "growth": "Growth",
    "aggressive_growth": "Aggressive Growth",
    "most_aggressive": "Most Aggressive",
}

# ============================================
# SCORE → PROFILE MAPPING
# ============================================
# Unified score (0-100) is mapped to one of 9 profiles.

SCORE_TO_PROFILE = [
    {"min": 0,  "max": 11,  "profile": "short_term"},
    {"min": 12, "max": 22,  "profile": "conservative"},
    {"min": 23, "max": 33,  "profile": "moderate_with_income"},
    {"min": 34, "max": 44,  "profile": "moderate"},
    {"min": 45, "max": 55,  "profile": "balanced"},
    {"min": 56, "max": 66,  "profile": "growth_with_income"},
    {"min": 67, "max": 77,  "profile": "growth"},
    {"min": 78, "max": 88,  "profile": "aggressive_growth"},
    {"min": 89, "max": 100, "profile": "most_aggressive"},
]

# ============================================
# ASSET ALLOCATION TABLE
# ============================================
# Each profile maps to percentages for five asset classes.
# Source: attached Non-US investor allocation chart.
#
# Asset classes:
#   global_equity   — Global world fund (80 % of equity sleeve)
#   home_country    — Home country tilt (20 % of equity sleeve)
#   fixed_income    — Bonds
#   cash            — Cash / money market
#   alternatives    — Alternatives / REITs

ASSET_ALLOCATIONS: Dict[str, Dict[str, float]] = {
    "short_term": {
        "global_equity": 0,
        "home_country": 0,
        "fixed_income": 30,
        "cash": 60,
        "alternatives": 10,
    },
    "conservative": {
        "global_equity": 12,
        "home_country": 3,
        "fixed_income": 55,
        "cash": 25,
        "alternatives": 5,
    },
    "moderate_with_income": {
        "global_equity": 20,
        "home_country": 5,
        "fixed_income": 45,
        "cash": 15,
        "alternatives": 15,
    },
    "moderate": {
        "global_equity": 28,
        "home_country": 7,
        "fixed_income": 40,
        "cash": 10,
        "alternatives": 15,
    },
    "balanced": {
        "global_equity": 36,
        "home_country": 9,
        "fixed_income": 35,
        "cash": 5,
        "alternatives": 15,
    },
    "growth_with_income": {
        "global_equity": 43,
        "home_country": 11,
        "fixed_income": 28,
        "cash": 2,
        "alternatives": 16,
    },
    "growth": {
        "global_equity": 52,
        "home_country": 13,
        "fixed_income": 18,
        "cash": 2,
        "alternatives": 15,
    },
    "aggressive_growth": {
        "global_equity": 64,
        "home_country": 16,
        "fixed_income": 8,
        "cash": 0,
        "alternatives": 12,
    },
    "most_aggressive": {
        "global_equity": 72,
        "home_country": 18,
        "fixed_income": 0,
        "cash": 0,
        "alternatives": 10,
    },
}

# Human-friendly labels for each asset class
ASSET_CLASS_LABELS = {
    "global_equity": "Global World Fund (80% of equity)",
    "home_country": "Home Country Tilt (20% of equity)",
    "fixed_income": "Fixed Income (Bonds)",
    "cash": "Cash / Money Market",
    "alternatives": "Alternatives / REITs",
}

# Derived convenience: total equity percentage per profile
TOTAL_EQUITY: Dict[str, float] = {
    profile: alloc["global_equity"] + alloc["home_country"]
    for profile, alloc in ASSET_ALLOCATIONS.items()
}


# ============================================
# CORE LOGIC
# ============================================

def compute_unified_score(
    willingness_score: float,
    tolerance_score: float,
) -> Dict[str, Any]:
    """
    Combine risk willingness and risk tolerance into a unified score.

    Formula:  unified = lower * 0.80 + higher * 0.20

    Both inputs must be normalised to 0-100.

    Returns a dict with:
        - willingness_score
        - tolerance_score
        - lower_score / higher_score (which is which)
        - lower_dimension ("willingness" or "tolerance")
        - unified_score  (0-100, rounded to 1 dp)
        - profile_key     e.g. "balanced"
        - profile_label   e.g. "Balanced"
        - allocation      dict of asset-class → percentage
        - total_equity    total equity percentage
    """
    lower = min(willingness_score, tolerance_score)
    higher = max(willingness_score, tolerance_score)

    if willingness_score <= tolerance_score:
        lower_dimension = "willingness"
    else:
        lower_dimension = "tolerance"

    unified = lower * 0.80 + higher * 0.20
    unified = round(max(0.0, min(100.0, unified)), 1)

    profile_key = _score_to_profile(unified)
    profile_label = PROFILE_LABELS[profile_key]
    allocation = ASSET_ALLOCATIONS[profile_key]
    total_eq = TOTAL_EQUITY[profile_key]

    return {
        "willingness_score": round(willingness_score, 1),
        "tolerance_score": round(tolerance_score, 1),
        "lower_score": round(lower, 1),
        "higher_score": round(higher, 1),
        "lower_dimension": lower_dimension,
        "unified_score": unified,
        "profile_key": profile_key,
        "profile_label": profile_label,
        "allocation": allocation,
        "total_equity": total_eq,
    }


def _score_to_profile(score: float) -> str:
    """Map a 0-100 unified score to a portfolio profile key."""
    for band in SCORE_TO_PROFILE:
        if band["min"] <= score <= band["max"]:
            return band["profile"]
    # Fallback – should not happen
    return "balanced"


def get_all_profiles() -> List[Dict[str, Any]]:
    """
    Return an ordered list of all profiles with their allocations.
    Useful for rendering comparison tables in the UI.
    """
    profiles = []
    for key in PROFILE_ORDER:
        profiles.append({
            "key": key,
            "label": PROFILE_LABELS[key],
            "allocation": ASSET_ALLOCATIONS[key],
            "total_equity": TOTAL_EQUITY[key],
        })
    return profiles


def get_allocation_for_profile(profile_key: str) -> Dict[str, float]:
    """Return the asset allocation dict for a given profile key."""
    return ASSET_ALLOCATIONS.get(profile_key, ASSET_ALLOCATIONS["balanced"])
