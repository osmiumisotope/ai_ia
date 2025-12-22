"""
Financial Foundation & Safety Net Calculations.
"Is the client protected against life's shocks?"
"""

from typing import Optional
from .models import (
    ClientData, MetricResult, HealthStatus, RiskLevel
)


class FinancialFoundation:
    """
    Calculator for Section 1: Financial Foundation & Safety Net.
    All methods are pure Python with no UI dependencies.
    """
    
    def __init__(self, client_data: ClientData):
        self.data = client_data
    
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
        Evaluate life insurance as multiple of income and coverage of dependent needs.
        Rule of thumb: 10-12x income for those with dependents.
        """
        coverage = self.data.insurance.life_insurance_coverage
        annual_income = self.data.income.total_annual_income
        dependents = self.data.profile.dependents
        
        if annual_income > 0:
            coverage_multiple = coverage / annual_income
        else:
            coverage_multiple = 0
        
        # Adjust benchmark based on dependents
        if dependents > 0:
            recommended_multiple = 10 + (dependents * 2)  # 10x base + 2x per dependent
        else:
            recommended_multiple = 5  # Lower need without dependents
        
        if coverage_multiple >= recommended_multiple:
            status = HealthStatus.EXCELLENT
        elif coverage_multiple >= recommended_multiple * 0.8:
            status = HealthStatus.GOOD
        elif coverage_multiple >= recommended_multiple * 0.5:
            status = HealthStatus.FAIR
        elif coverage_multiple > 0:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL if dependents > 0 else HealthStatus.FAIR
        
        recommendations = []
        if dependents > 0 and coverage_multiple < recommended_multiple:
            gap = (recommended_multiple * annual_income) - coverage
            recommendations.append(f"Consider increasing life insurance by ${gap:,.0f}")
        if self.data.insurance.life_insurance_type == "whole":
            recommendations.append("Review if term insurance might be more cost-effective")
        
        return MetricResult(
            value=coverage_multiple,
            display_value=f"{coverage_multiple:.1f}x income",
            status=status,
            benchmark=recommended_multiple,
            benchmark_label=f"{recommended_multiple}x income recommended",
            description=f"Life insurance coverage: ${coverage:,.0f}",
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
