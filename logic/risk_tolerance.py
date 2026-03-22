"""
Risk Tolerance (Risk-Taking Ability) Module

Calculates an investor's objective risk-taking ability based on measurable
financial factors. This is distinct from risk *willingness* (psychological
comfort) and together they determine the target portfolio allocation.

Components and maximum scores:
    1. Time Horizon          — 25 pts  (years to planning age, max 25)
    2. Liquidity             — 20 pts  (emergency months coverage)
    3. Debt Burden (DTI)     — 15 pts  (debt-to-income ratio)
    4. Income Stability &
       Savings Rate          — 15 pts  (8 stability + 7 savings rate)
    5. Dependents            — 15 pts  (categorical scoring)
                              --------
    Total                     90 pts max
"""

from typing import Dict, Any, Optional


# ============================================
# EMPLOYMENT TYPE DEFINITIONS
# ============================================

EMPLOYMENT_TYPES = [
    {"key": "government_tenured", "label": "Government / Tenured", "stability_score": 8},
    {"key": "salaried_full_time", "label": "Salaried Full-Time", "stability_score": 7},
    {"key": "self_employed_stable", "label": "Self-Employed / Stable Business", "stability_score": 5},
    {"key": "commission_variable", "label": "Commission / Variable Income", "stability_score": 3},
    {"key": "contract_gig", "label": "Contract / Gig Worker", "stability_score": 1},
    {"key": "retired", "label": "Retired", "stability_score": 6},
]

EMPLOYMENT_TYPE_MAP = {e["key"]: e for e in EMPLOYMENT_TYPES}


# ============================================
# SCORING FUNCTIONS
# ============================================

def score_time_horizon(current_age: int, planning_age: int = 92) -> Dict[str, Any]:
    """
    Time Horizon — 25 points max.
    Each year from current age to planning age = 1 point, capped at 25.
    """
    years_to_planning = max(0, planning_age - current_age)
    score = min(25, years_to_planning)
    return {
        "score": score,
        "max": 25,
        "years_to_planning": years_to_planning,
        "planning_age": planning_age,
        "current_age": current_age,
    }


def score_liquidity(emergency_months: float) -> Dict[str, Any]:
    """
    Liquidity — 20 points max.
    Based on how many months of expenses the client can cover with liquid savings.
    <1 → 0, 1–3 → 5, 3–6 → 10, 6–12 → 15, 12+ → 20.
    """
    if emergency_months >= 12:
        score = 20
    elif emergency_months >= 6:
        score = 15
    elif emergency_months >= 3:
        score = 10
    elif emergency_months >= 1:
        score = 5
    else:
        score = 0
    return {
        "score": score,
        "max": 20,
        "emergency_months": round(emergency_months, 1),
    }


def score_debt_burden(monthly_debt: float, gross_monthly_income: float) -> Dict[str, Any]:
    """
    Debt Burden (DTI) — 15 points max.
    DTI = monthly_debt / gross_monthly_income.
    >50% → 0, 40–50% → 3, 30–40% → 7, 20–30% → 10, 10–20% → 13, <10% → 15.
    """
    if gross_monthly_income > 0:
        dti = (monthly_debt / gross_monthly_income) * 100
    else:
        dti = 100.0 if monthly_debt > 0 else 0.0

    if dti < 10:
        score = 15
    elif dti < 20:
        score = 13
    elif dti < 30:
        score = 10
    elif dti < 40:
        score = 7
    elif dti <= 50:
        score = 3
    else:
        score = 0

    return {
        "score": score,
        "max": 15,
        "dti_pct": round(dti, 1),
        "monthly_debt": monthly_debt,
        "gross_monthly_income": gross_monthly_income,
    }


def score_income_stability(employment_type: str) -> Dict[str, Any]:
    """
    Income Stability sub-score — 8 points max.
    Categorical based on employment type.
    """
    emp = EMPLOYMENT_TYPE_MAP.get(employment_type)
    stability_score = emp["stability_score"] if emp else 3
    return {
        "score": stability_score,
        "max": 8,
        "employment_type": employment_type,
    }


def score_savings_rate(
    monthly_income: float,
    monthly_expenses: float,
    monthly_debt: float,
) -> Dict[str, Any]:
    """
    Savings Rate sub-score — 7 points max.
    savings_rate = (income - expenses - debt) / income
    <5% → 1, 5–10% → 2, 10–20% → 4, 20–30% → 5, 30%+ → 7.
    """
    if monthly_income > 0:
        savings = monthly_income - monthly_expenses - monthly_debt
        rate = (savings / monthly_income) * 100
    else:
        rate = 0.0

    if rate >= 30:
        score = 7
    elif rate >= 20:
        score = 5
    elif rate >= 10:
        score = 4
    elif rate >= 5:
        score = 2
    else:
        score = 1

    return {
        "score": score,
        "max": 7,
        "savings_rate_pct": round(rate, 1),
    }


def score_income_and_savings(
    employment_type: str,
    monthly_income: float,
    monthly_expenses: float,
    monthly_debt: float,
) -> Dict[str, Any]:
    """
    Combined Income Stability & Savings Rate — 15 points max (8 + 7).
    """
    stability = score_income_stability(employment_type)
    savings = score_savings_rate(monthly_income, monthly_expenses, monthly_debt)
    return {
        "score": stability["score"] + savings["score"],
        "max": 15,
        "stability": stability,
        "savings": savings,
    }


def score_dependents(
    num_dependents: int,
    dual_income: bool,
) -> Dict[str, Any]:
    """
    Dependents — 15 points max.
    0 dependents → 15,
    1 dependent + dual income → 12,
    1 dependent + single income → 9,
    2–3 dependents + dual income → 7,
    2–3 dependents + single income → 4,
    4+ dependents → 2.
    """
    if num_dependents == 0:
        score = 15
    elif num_dependents == 1:
        score = 12 if dual_income else 9
    elif num_dependents <= 3:
        score = 7 if dual_income else 4
    else:
        score = 2

    return {
        "score": score,
        "max": 15,
        "num_dependents": num_dependents,
        "dual_income": dual_income,
    }


# ============================================
# AGGREGATE SCORING
# ============================================

def calculate_risk_tolerance(
    current_age: int,
    planning_age: int,
    emergency_months: float,
    monthly_debt: float,
    gross_monthly_income: float,
    employment_type: str,
    monthly_income: float,
    monthly_expenses: float,
    num_dependents: int,
    dual_income: bool,
) -> Dict[str, Any]:
    """
    Calculate the full risk-tolerance score (0–90) from the five components.

    Returns a dict with individual component scores and the total.
    """
    time_horizon = score_time_horizon(current_age, planning_age)
    liquidity = score_liquidity(emergency_months)
    debt_burden = score_debt_burden(monthly_debt, gross_monthly_income)
    income_savings = score_income_and_savings(
        employment_type, monthly_income, monthly_expenses, monthly_debt
    )
    dependents = score_dependents(num_dependents, dual_income)

    total_score = (
        time_horizon["score"]
        + liquidity["score"]
        + debt_burden["score"]
        + income_savings["score"]
        + dependents["score"]
    )
    max_score = 90

    # Normalise to 0–100 for display
    normalized = (total_score / max_score) * 100 if max_score > 0 else 0

    # Map to tolerance level
    if normalized >= 75:
        level = "high"
        label = "Aggressive"
    elif normalized >= 50:
        level = "moderate"
        label = "Moderate"
    elif normalized >= 25:
        level = "low_moderate"
        label = "Conservative-Moderate"
    else:
        level = "low"
        label = "Conservative"

    return {
        "total_score": total_score,
        "max_score": max_score,
        "normalized_score": round(normalized, 1),
        "tolerance_level": level,
        "tolerance_label": label,
        "components": {
            "time_horizon": time_horizon,
            "liquidity": liquidity,
            "debt_burden": debt_burden,
            "income_stability_savings": income_savings,
            "dependents": dependents,
        },
    }


def derive_values_from_client_data(client_data, client_id: str) -> Dict[str, Any]:
    """
    Derive default/calculated values from the existing client data model
    so they can be shown on the right-hand panel in the UI for easy copying.

    Returns a flat dict with all calculated values.
    """
    from database.db import get_client_dependents, get_client_by_id

    profile = client_data.profile
    income = client_data.income
    expenses = client_data.expenses
    assets = client_data.assets
    liabilities = client_data.liabilities

    # --- Time Horizon ---
    current_age = profile.age
    default_planning_age = 92

    # --- Liquidity ---
    monthly_expenses = expenses.total_monthly_expenses
    liquid_savings = (
        assets.checking_accounts + assets.savings_accounts + assets.money_market
    )
    if monthly_expenses > 0:
        calc_emergency_months = liquid_savings / monthly_expenses
    else:
        calc_emergency_months = 0.0

    # --- Debt Burden ---
    monthly_debt = expenses.debt_payments
    gross_monthly_income = income.monthly_income

    # --- Income & Savings ---
    # Employment type from DB (may not exist yet)
    client_row = get_client_by_id(client_id) or {}
    employment_type = client_row.get("employment_type", "salaried_full_time") or "salaried_full_time"

    # --- Dependents ---
    dependents_list = get_client_dependents(client_id)
    financially_dependent = [
        d for d in dependents_list if d.get("is_financially_dependent")
    ]
    num_dependents = len(financially_dependent)

    # Dual income heuristic: married/domestic partnership and not retired
    marital = profile.marital_status
    dual_income = marital in ("married", "domestic_partnership")

    return {
        "current_age": current_age,
        "planning_age": default_planning_age,
        "emergency_months": round(calc_emergency_months, 1),
        "liquid_savings": liquid_savings,
        "monthly_expenses": monthly_expenses,
        "monthly_debt": monthly_debt,
        "gross_monthly_income": gross_monthly_income,
        "employment_type": employment_type,
        "monthly_income": income.monthly_income,
        "num_dependents": num_dependents,
        "dual_income": dual_income,
    }
