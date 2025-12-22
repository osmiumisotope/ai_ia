"""
Cash Flow & Spending Behavior Calculations.
"How healthy are their money habits?"
"""

from typing import List, Optional
from .models import ClientData, MetricResult, HealthStatus


class CashFlowBehavior:
    """
    Calculator for Section 2: Cash Flow & Spending Behavior.
    All methods are pure Python with no UI dependencies.
    """
    
    def __init__(self, client_data: ClientData, historical_expenses: Optional[List[float]] = None):
        self.data = client_data
        # Historical monthly expenses for trend analysis (last 12-24 months)
        self.historical_expenses = historical_expenses or []
    
    def savings_rate(self) -> MetricResult:
        """
        Calculate savings rate as percentage of gross income.
        Target: 20%+ for most, higher for late starters.
        """
        monthly_income = self.data.income.monthly_income
        monthly_expenses = self.data.expenses.total_monthly_expenses
        
        if monthly_income > 0:
            monthly_savings = monthly_income - monthly_expenses
            rate = (monthly_savings / monthly_income) * 100
        else:
            rate = 0
        
        # Calculate delta from last year if we have historical data
        delta = None
        delta_is_positive = None
        if len(self.historical_expenses) >= 12:
            # Calculate last year's average expenses
            last_year_avg_expenses = sum(self.historical_expenses[:12]) / 12
            last_year_savings = monthly_income - last_year_avg_expenses
            last_year_rate = (last_year_savings / monthly_income) * 100 if monthly_income > 0 else 0
            delta = abs(rate - last_year_rate)
            delta_is_positive = rate >= last_year_rate  # Higher savings rate is better
        
        # Adjust target based on age and retirement timeline
        years_to_retirement = self.data.profile.retirement_age - self.data.profile.age
        if years_to_retirement < 15:
            target_rate = 25  # Need to save more with shorter runway
        elif years_to_retirement < 25:
            target_rate = 20
        else:
            target_rate = 15
        
        if rate >= target_rate + 5:
            status = HealthStatus.EXCELLENT
        elif rate >= target_rate:
            status = HealthStatus.GOOD
        elif rate >= target_rate - 5:
            status = HealthStatus.FAIR
        elif rate > 0:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if rate < target_rate:
            gap = (target_rate - rate) * monthly_income / 100
            recommendations.append(f"Increase monthly savings by ${gap:,.0f} to reach {target_rate}% target")
        if rate < 10:
            recommendations.append("Review discretionary spending for potential cuts")
            recommendations.append("Consider automating savings transfers")
        
        return MetricResult(
            value=rate,
            display_value=f"{rate:.1f}%",
            status=status,
            benchmark=target_rate,
            benchmark_label=f"{target_rate}% target for your timeline",
            description=f"Monthly savings: ${monthly_income - monthly_expenses:,.0f}",
            recommendations=recommendations,
            delta=delta,
            delta_is_positive=delta_is_positive
        )
    
    def fixed_cost_ratio(self) -> MetricResult:
        """
        Calculate fixed costs as percentage of income.
        Target: Under 50% for financial flexibility.
        """
        fixed = self.data.expenses.fixed_expenses
        monthly_income = self.data.income.monthly_income
        
        if monthly_income > 0:
            ratio = (fixed / monthly_income) * 100
        else:
            ratio = 100 if fixed > 0 else 0
        
        # Calculate delta - estimate fixed costs from historical data (roughly 70% of total)
        delta = None
        delta_is_positive = None
        if len(self.historical_expenses) >= 12:
            last_year_total = sum(self.historical_expenses[:12]) / 12
            last_year_fixed_est = last_year_total * 0.7  # Estimate fixed portion
            last_year_ratio = (last_year_fixed_est / monthly_income) * 100 if monthly_income > 0 else 0
            delta = abs(ratio - last_year_ratio)
            delta_is_positive = ratio <= last_year_ratio  # Lower fixed cost ratio is better
        
        if ratio <= 40:
            status = HealthStatus.EXCELLENT
        elif ratio <= 50:
            status = HealthStatus.GOOD
        elif ratio <= 60:
            status = HealthStatus.FAIR
        elif ratio <= 75:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if ratio > 50:
            recommendations.append("Fixed costs exceeding 50% limits flexibility")
        if self.data.expenses.housing / monthly_income > 0.28:
            recommendations.append("Housing costs exceed recommended 28% of income")
        if ratio > 60:
            recommendations.append("Consider reducing fixed costs through refinancing or downsizing")
        
        return MetricResult(
            value=ratio,
            display_value=f"{ratio:.1f}%",
            status=status,
            benchmark=50.0,
            benchmark_label="50% or less recommended",
            description=f"Monthly fixed costs: ${fixed:,.0f}",
            recommendations=recommendations,
            delta=delta,
            delta_is_positive=delta_is_positive
        )
    
    def discretionary_spending(self) -> MetricResult:
        """
        Calculate discretionary spending as percentage of income.
        Context-dependent: Should leave room for savings goals.
        """
        discretionary = self.data.expenses.discretionary_expenses
        monthly_income = self.data.income.monthly_income
        
        if monthly_income > 0:
            ratio = (discretionary / monthly_income) * 100
        else:
            ratio = 0
        
        # Calculate delta - estimate discretionary from historical data (roughly 30% of total)
        delta = None
        delta_is_positive = None
        if len(self.historical_expenses) >= 12:
            last_year_total = sum(self.historical_expenses[:12]) / 12
            last_year_disc_est = last_year_total * 0.3  # Estimate discretionary portion
            last_year_ratio = (last_year_disc_est / monthly_income) * 100 if monthly_income > 0 else 0
            delta = abs(ratio - last_year_ratio)
            delta_is_positive = ratio <= last_year_ratio  # Lower discretionary ratio is better
        
        # After fixed costs and savings target, remaining is available for discretionary
        savings_target = 20  # Percent
        fixed_ratio = (self.data.expenses.fixed_expenses / monthly_income * 100) if monthly_income > 0 else 0
        available_for_discretionary = 100 - fixed_ratio - savings_target
        
        if ratio <= available_for_discretionary * 0.7:
            status = HealthStatus.EXCELLENT
        elif ratio <= available_for_discretionary:
            status = HealthStatus.GOOD
        elif ratio <= available_for_discretionary * 1.2:
            status = HealthStatus.FAIR
        elif ratio <= available_for_discretionary * 1.5:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if ratio > available_for_discretionary:
            excess = discretionary - (available_for_discretionary * monthly_income / 100)
            recommendations.append(f"Discretionary spending ${excess:,.0f}/mo over budget")
        
        # Identify top spending categories
        categories = {
            "Entertainment": self.data.expenses.entertainment,
            "Dining out": self.data.expenses.dining_out,
            "Shopping": self.data.expenses.shopping,
            "Travel": self.data.expenses.travel,
            "Subscriptions": self.data.expenses.subscriptions
        }
        top_category = max(categories, key=categories.get)
        if categories[top_category] > discretionary * 0.4:
            recommendations.append(f"{top_category} accounts for {categories[top_category]/discretionary*100:.0f}% of discretionary spending")
        
        return MetricResult(
            value=ratio,
            display_value=f"{ratio:.1f}%",
            status=status,
            benchmark=available_for_discretionary,
            benchmark_label=f"{available_for_discretionary:.0f}% available after fixed costs & savings",
            description=f"Monthly discretionary: ${discretionary:,.0f}",
            recommendations=recommendations,
            delta=delta,
            delta_is_positive=delta_is_positive
        )
    
    def guilt_free_spending(self) -> MetricResult:
        """
        Calculate guilt-free spending amount after all obligations and savings.
        This is "fun money" that won't derail financial goals.
        """
        monthly_income = self.data.income.monthly_income
        fixed = self.data.expenses.fixed_expenses
        
        # Calculate target savings
        years_to_retirement = self.data.profile.retirement_age - self.data.profile.age
        if years_to_retirement < 15:
            savings_rate = 0.25
        else:
            savings_rate = 0.20
        
        target_savings = monthly_income * savings_rate
        guilt_free = monthly_income - fixed - target_savings
        
        # Calculate delta based on historical fixed expenses
        delta = None
        delta_is_positive = None
        if len(self.historical_expenses) >= 12:
            last_year_total = sum(self.historical_expenses[:12]) / 12
            last_year_fixed_est = last_year_total * 0.7
            last_year_guilt_free = monthly_income - last_year_fixed_est - target_savings
            delta = abs(guilt_free - last_year_guilt_free)
            delta_is_positive = guilt_free >= last_year_guilt_free  # More guilt-free money is better
        
        if monthly_income > 0:
            gf_ratio = (guilt_free / monthly_income) * 100
        else:
            gf_ratio = 0
        
        if guilt_free >= monthly_income * 0.2:
            status = HealthStatus.EXCELLENT
        elif guilt_free >= monthly_income * 0.1:
            status = HealthStatus.GOOD
        elif guilt_free > 0:
            status = HealthStatus.FAIR
        else:
            status = HealthStatus.POOR
        
        recommendations = []
        if guilt_free <= 0:
            recommendations.append("Current budget leaves no room for guilt-free spending")
            recommendations.append("Review fixed costs to create breathing room")
        elif guilt_free < 500:
            recommendations.append("Consider ways to increase income or reduce fixed costs")
        
        return MetricResult(
            value=guilt_free,
            display_value=f"${guilt_free:,.0f}/mo",
            status=status,
            benchmark=monthly_income * 0.15,
            benchmark_label="~15% of income as guilt-free spending",
            description=f"{gf_ratio:.1f}% of income available for fun",
            recommendations=recommendations,
            delta=delta,
            delta_is_positive=delta_is_positive
        )
    
    def lifestyle_creep_tracker(self) -> MetricResult:
        """
        Track expense growth vs income growth over time.
        Flags when expenses are growing faster than income.
        """
        if len(self.historical_expenses) < 12:
            # Not enough data for trend analysis
            return MetricResult(
                value=0,
                display_value="Insufficient data",
                status=HealthStatus.FAIR,
                description="Need 12+ months of data for trend analysis",
                recommendations=["Continue tracking expenses to enable lifestyle creep detection"]
            )
        
        # Calculate expense growth rate (YoY if we have enough data)
        if len(self.historical_expenses) >= 24:
            old_avg = sum(self.historical_expenses[:12]) / 12
            new_avg = sum(self.historical_expenses[-12:]) / 12
        else:
            old_avg = sum(self.historical_expenses[:6]) / 6
            new_avg = sum(self.historical_expenses[-6:]) / 6
        
        if old_avg > 0:
            expense_growth = ((new_avg - old_avg) / old_avg) * 100
        else:
            expense_growth = 0
        
        # For demo, we'll assume income growth (in real app, would track historical income)
        assumed_income_growth = 3.0  # Typical annual raise
        
        creep_rate = expense_growth - assumed_income_growth
        
        if creep_rate <= 0:
            status = HealthStatus.EXCELLENT
        elif creep_rate <= 2:
            status = HealthStatus.GOOD
        elif creep_rate <= 5:
            status = HealthStatus.FAIR
        elif creep_rate <= 10:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if creep_rate > 0:
            recommendations.append(f"Expenses growing {creep_rate:.1f}% faster than income")
        if creep_rate > 5:
            recommendations.append("Consider implementing a spending freeze")
            recommendations.append("Review recent subscription additions")
        
        return MetricResult(
            value=creep_rate,
            display_value=f"{creep_rate:+.1f}%",
            status=status,
            benchmark=0.0,
            benchmark_label="Expenses should grow ≤ income growth",
            trend=expense_growth,
            description=f"Expense growth: {expense_growth:.1f}% vs income growth: {assumed_income_growth:.1f}%",
            recommendations=recommendations
        )
    
    def get_section_summary(self) -> dict:
        """Get all metrics for this section with overall health score."""
        metrics = {
            "savings_rate": self.savings_rate(),
            "fixed_cost_ratio": self.fixed_cost_ratio(),
            "discretionary_spending": self.discretionary_spending(),
            "guilt_free_spending": self.guilt_free_spending(),
            "lifestyle_creep": self.lifestyle_creep_tracker()
        }
        
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
            "section_title": "Cash Flow & Spending Behavior",
            "section_question": "How healthy are their money habits?"
        }
