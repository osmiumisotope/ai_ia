"""
Financial Foundation & Safety Net Calculations.
"Is the client protected against life's shocks?"
"""

from datetime import date
from typing import Optional
from .models import (
    ClientData, MetricResult, HealthStatus, RiskLevel
)

# Life Insurance Calculation Constants
DISCOUNT_RATE = 0.035  # 3.5% real return
TAX_HAIRCUT_RETIREMENT = 0.25  # 25% tax on retirement accounts
DISCOUNT_COMPANY_STOCK = 0.50  # 50% discount on vested company stock
DISCOUNT_INVESTMENT_RE = 0.30  # 30% illiquidity discount on investment real estate
EXPENSE_REDUCTION_POST_KIDS = 0.70  # 70% of expenses after kids independent
INDEPENDENCE_AGE = 18
DEFAULT_YOUNGEST_DEPENDENT_AGE = 5  # Fallback assumption


def _pv_annuity(annual_amount: float, years: int, rate: float) -> float:
    """Calculate present value of an annuity."""
    if years <= 0:
        return 0
    if rate <= 0:
        return annual_amount * years
    return annual_amount * (1 - (1 + rate) ** -years) / rate


class FinancialFoundation:
    """
    Calculator for Section 1: Financial Foundation & Safety Net.
    All methods are pure Python with no UI dependencies.
    """
    
    def __init__(self, client_data: ClientData):
        self.data = client_data
    
    def _estimate_years_until_dependents_independent(self) -> int:
        """
        Estimate years until youngest dependent turns 18.
        Uses college goals to back-calculate ages, or assumes youngest is 5.
        """
        if self.data.profile.dependents == 0:
            return 0
        
        # Try to infer from college goals
        college_goals = [
            goal for goal in self.data.goals
            if any(keyword in goal.name.lower() 
                   for keyword in ['college', 'education', 'university'])
        ]
        
        if college_goals:
            latest_goal = max(college_goals, key=lambda g: g.target_date)
            years_to_college = (latest_goal.target_date - date.today()).days / 365
            return max(0, int(years_to_college))
        else:
            # Conservative fallback: assume youngest dependent is 5
            return INDEPENDENCE_AGE - DEFAULT_YOUNGEST_DEPENDENT_AGE  # 13 years
    
    def _calculate_insurance_need(self) -> dict:
        """
        Calculate life insurance need using needs-based approach.
        Returns dictionary with all components for transparency.
        """
        # Component 1: Outstanding Loans
        outstanding_loans = self.data.liabilities.total_liabilities
        
        # Component 2: Education Goals
        college_goals = [
            goal for goal in self.data.goals
            if any(keyword in goal.name.lower() 
                   for keyword in ['college', 'education', 'university'])
        ]
        education_goals_total = sum(
            max(0, goal.target_amount - goal.current_amount) 
            for goal in college_goals
        )
        
        # Component 3: Present Value of Expenses (Two-Phase Model)
        # Monthly expenses excluding housing (mortgage paid off in loans component)
        monthly_expenses_ex_housing = (
            self.data.expenses.total_monthly_expenses - 
            self.data.expenses.housing
        )
        annual_expenses_ex_housing = monthly_expenses_ex_housing * 12
        
        # Phase 1: Until dependents are independent
        phase1_years = self._estimate_years_until_dependents_independent()
        pv_expenses_phase1 = _pv_annuity(
            annual_expenses_ex_housing, 
            phase1_years, 
            DISCOUNT_RATE
        )
        
        # Phase 2: After dependents independent until retirement
        current_age = self.data.profile.age
        retirement_age = self.data.profile.retirement_age
        phase2_years = max(0, retirement_age - current_age - phase1_years)
        
        # Phase 2 expenses at reduced level (70%)
        phase2_annual_expenses = annual_expenses_ex_housing * EXPENSE_REDUCTION_POST_KIDS
        
        # PV of phase 2 annuity (at the start of phase 2)
        pv_phase2_at_start = _pv_annuity(
            phase2_annual_expenses, 
            phase2_years, 
            DISCOUNT_RATE
        )
        
        # Discount phase 2 PV back to today
        if phase1_years > 0 and DISCOUNT_RATE > 0:
            pv_expenses_phase2 = pv_phase2_at_start / ((1 + DISCOUNT_RATE) ** phase1_years)
        else:
            pv_expenses_phase2 = pv_phase2_at_start
        
        total_pv_expenses = pv_expenses_phase1 + pv_expenses_phase2
        
        # Component 4: Discounted Assets
        # Investment real estate equity (with 30% illiquidity discount)
        investment_re_equity = max(0, 
            self.data.assets.real_estate_investment - 
            self.data.liabilities.mortgage_investment
        ) * (1 - DISCOUNT_INVESTMENT_RE)
        
        # Retirement accounts (with 25% tax haircut)
        retirement_accounts = (
            self.data.assets.ira_traditional + 
            self.data.assets.ira_roth + 
            self.data.assets.retirement_401k + 
            self.data.assets.hsa
        ) * (1 - TAX_HAIRCUT_RETIREMENT)
        
        discounted_assets = (
            self.data.assets.liquid_assets +                              # 100%
            self.data.assets.brokerage_taxable +                          # 100%
            retirement_accounts +                                          # 75%
            self.data.assets.company_stock_vested * DISCOUNT_COMPANY_STOCK +  # 50%
            investment_re_equity +                                         # 70%
            self.data.insurance.life_insurance_coverage                   # 100%
        )
        
        # Net Insurance Need Calculation
        gross_need = outstanding_loans + total_pv_expenses + education_goals_total
        net_need = gross_need - discounted_assets
        
        # Component 5: Minimum Floor (1 year income)
        annual_income = self.data.income.total_annual_income
        minimum_floor = annual_income
        
        final_insurance_need = max(net_need, minimum_floor)
        is_self_insured = (net_need <= 0)
        
        return {
            'outstanding_loans': outstanding_loans,
            'education_goals': education_goals_total,
            'pv_expenses_phase1': pv_expenses_phase1,
            'pv_expenses_phase2': pv_expenses_phase2,
            'total_pv_expenses': total_pv_expenses,
            'phase1_years': phase1_years,
            'phase2_years': phase2_years,
            'discounted_assets': discounted_assets,
            'gross_need': gross_need,
            'net_need': net_need,
            'minimum_floor': minimum_floor,
            'final_insurance_need': final_insurance_need,
            'is_self_insured': is_self_insured,
            'existing_coverage': self.data.insurance.life_insurance_coverage
        }
    
    def emergency_fund_months(self) -> MetricResult:
        """
        Calculate emergency fund as multiple of monthly expenses.
        Benchmark: 3-6 months for employed, 6-12 for self-employed/variable income.
        """
        monthly_expenses = self.data.expenses.total_monthly_expenses
        liquid_cash = (self.data.assets.checking_accounts + 
                      self.data.assets.savings_accounts +
                      self.data.assets.money_market)
        
        if monthly_expenses == 0:
            months = 0
        else:
            months = liquid_cash / monthly_expenses
        
        # Determine status based on months covered
        if months >= 6:
            status = HealthStatus.EXCELLENT
        elif months >= 4:
            status = HealthStatus.GOOD
        elif months >= 3:
            status = HealthStatus.FAIR
        elif months >= 1:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if months < 3:
            shortfall = (3 * monthly_expenses) - liquid_cash
            recommendations.append(f"Build emergency fund by ${shortfall:,.0f} to reach 3-month minimum")
        if months < 6:
            recommendations.append("Consider high-yield savings account for emergency funds")
        
        return MetricResult(
            value=months,
            display_value=f"{months:.1f} months",
            status=status,
            benchmark=6.0,
            benchmark_label="6 months recommended",
            description="Cash reserves as multiple of monthly expenses",
            recommendations=recommendations
        )
    
    def liquid_net_worth(self) -> MetricResult:
        """
        Calculate liquid net worth (immediately accessible accounts minus high-interest debt).
        """
        liquid_nw = self.data.liquid_net_worth
        total_nw = self.data.net_worth
        
        # Liquid NW should ideally be at least 20% of total for flexibility
        if total_nw > 0:
            liquid_ratio = liquid_nw / total_nw
        else:
            liquid_ratio = 0
        
        if liquid_ratio >= 0.3:
            status = HealthStatus.EXCELLENT
        elif liquid_ratio >= 0.2:
            status = HealthStatus.GOOD
        elif liquid_ratio >= 0.1:
            status = HealthStatus.FAIR
        elif liquid_nw > 0:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if liquid_ratio < 0.2:
            recommendations.append("Consider increasing liquid asset allocation for flexibility")
        if self.data.liabilities.high_interest_debt > 0:
            recommendations.append(f"Pay down ${self.data.liabilities.high_interest_debt:,.0f} in high-interest debt")
        
        return MetricResult(
            value=liquid_nw,
            display_value=f"${liquid_nw:,.0f}",
            status=status,
            benchmark=total_nw * 0.2 if total_nw > 0 else 0,
            benchmark_label="20% of net worth",
            description="Immediately accessible assets minus high-interest debt",
            recommendations=recommendations
        )
    
    def life_insurance_coverage(self) -> MetricResult:
        """
        Evaluate life insurance using needs-based calculation.
        Accounts for actual liabilities, future expenses, and existing assets.
        """
        # Calculate insurance need using needs-based approach
        calc = self._calculate_insurance_need()
        
        existing_coverage = calc['existing_coverage']
        needed_coverage = calc['final_insurance_need']
        is_self_insured = calc['is_self_insured']
        minimum_floor = calc['minimum_floor']
        dependents = self.data.profile.dependents
        
        # Health Status Determination
        if needed_coverage > 0:
            coverage_ratio = existing_coverage / needed_coverage
        else:
            coverage_ratio = float('inf')
        
        if existing_coverage >= needed_coverage:
            status = HealthStatus.EXCELLENT
        elif coverage_ratio >= 0.8:
            status = HealthStatus.GOOD
        elif coverage_ratio >= 0.5:
            status = HealthStatus.FAIR
        elif existing_coverage > 0:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL if dependents > 0 else HealthStatus.FAIR
        
        # Recommendations Logic
        recommendations = []
        
        if is_self_insured:
            recommendations.append(
                f"You are effectively self-insured. Minimum ${minimum_floor:,.0f} "
                f"(1 year income) recommended for probate/bridge needs."
            )
            if existing_coverage > needed_coverage * 1.5:
                recommendations.append(
                    "Consider if current coverage level is cost-effective given your asset base."
                )
        else:
            coverage_gap = needed_coverage - existing_coverage
            if coverage_gap > 0:
                recommendations.append(
                    f"Consider increasing life insurance by ${coverage_gap:,.0f} to fully cover needs."
                )
        
        if self.data.insurance.life_insurance_type == "whole" and dependents > 0:
            recommendations.append(
                "Review if term insurance might provide more coverage at lower cost."
            )
        
        # Build description
        description = f"Current: ${existing_coverage:,.0f} | Need: ${needed_coverage:,.0f}"
        if is_self_insured:
            description += " (Self-insured)"
        
        return MetricResult(
            value=existing_coverage,
            display_value=f"${existing_coverage:,.0f}",
            status=status,
            benchmark=needed_coverage,
            benchmark_label=f"${needed_coverage:,.0f} needed",
            description=description,
            recommendations=recommendations
        )
    
    def disability_coverage(self) -> MetricResult:
        """
        Evaluate disability insurance coverage.
        Should cover 60-70% of pre-tax income.
        """
        monthly_coverage = self.data.insurance.disability_coverage_monthly
        monthly_income = self.data.income.monthly_income
        
        if monthly_income > 0:
            coverage_ratio = monthly_coverage / monthly_income
        else:
            coverage_ratio = 0
        
        if coverage_ratio >= 0.65:
            status = HealthStatus.EXCELLENT
        elif coverage_ratio >= 0.5:
            status = HealthStatus.GOOD
        elif coverage_ratio >= 0.3:
            status = HealthStatus.FAIR
        elif coverage_ratio > 0:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if coverage_ratio < 0.6:
            target = monthly_income * 0.6
            gap = target - monthly_coverage
            recommendations.append(f"Consider additional disability coverage of ${gap:,.0f}/month")
        if self.data.insurance.disability_coverage_type == "short-term":
            recommendations.append("Add long-term disability coverage for comprehensive protection")
        
        return MetricResult(
            value=coverage_ratio * 100,
            display_value=f"{coverage_ratio * 100:.0f}% of income",
            status=status,
            benchmark=60.0,
            benchmark_label="60% of income recommended",
            description=f"Monthly disability benefit: ${monthly_coverage:,.0f}",
            recommendations=recommendations
        )
    
    def debt_to_income_ratio(self) -> MetricResult:
        """
        Calculate debt-to-income ratio.
        Total monthly debt payments / gross monthly income.
        """
        monthly_debt = self.data.expenses.debt_payments
        monthly_income = self.data.income.monthly_income
        
        if monthly_income > 0:
            dti = (monthly_debt / monthly_income) * 100
        else:
            dti = 100 if monthly_debt > 0 else 0
        
        if dti <= 20:
            status = HealthStatus.EXCELLENT
        elif dti <= 35:
            status = HealthStatus.GOOD
        elif dti <= 43:
            status = HealthStatus.FAIR
        elif dti <= 50:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if dti > 35:
            recommendations.append("Focus on paying down debt to improve financial flexibility")
        if dti > 43:
            recommendations.append("DTI above 43% may limit mortgage qualification")
        if self.data.liabilities.credit_cards > 0:
            recommendations.append("Prioritize paying off high-interest credit card debt")
        
        return MetricResult(
            value=dti,
            display_value=f"{dti:.1f}%",
            status=status,
            benchmark=35.0,
            benchmark_label="35% or less recommended",
            description="Monthly debt payments as percentage of gross income",
            recommendations=recommendations
        )
    
    def get_section_summary(self) -> dict:
        """
        Get all metrics for this section with overall health score.
        """
        metrics = {
            "emergency_fund": self.emergency_fund_months(),
            "life_insurance": self.life_insurance_coverage(),
            "disability_insurance": self.disability_coverage(),
            "debt_to_income": self.debt_to_income_ratio(),
            "liquid_net_worth": self.liquid_net_worth()
        }
        
        # Calculate overall section health
        status_scores = {
            HealthStatus.EXCELLENT: 100,
            HealthStatus.GOOD: 75,
            HealthStatus.FAIR: 50,
            HealthStatus.POOR: 25,
            HealthStatus.CRITICAL: 0
        }
        
        total_score = sum(status_scores[m.status] for m in metrics.values())
        avg_score = total_score / len(metrics)
        
        if avg_score >= 85:
            overall_status = HealthStatus.EXCELLENT
        elif avg_score >= 65:
            overall_status = HealthStatus.GOOD
        elif avg_score >= 45:
            overall_status = HealthStatus.FAIR
        elif avg_score >= 25:
            overall_status = HealthStatus.POOR
        else:
            overall_status = HealthStatus.CRITICAL
        
        return {
            "metrics": metrics,
            "overall_score": avg_score,
            "overall_status": overall_status,
            "section_title": "Financial Foundation & Safety Net",
            "section_question": "Is the client protected against life's shocks?"
        }
