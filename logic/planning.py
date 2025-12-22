"""
Future Planning & Projections Calculations.
"Are they on track for their goals?"
"""

from typing import List, Dict, Optional
from datetime import date, timedelta
import math
from .models import ClientData, MetricResult, HealthStatus, GoalData


class FuturePlanning:
    """
    Calculator for Section 4: Future Planning & Projections.
    All methods are pure Python with no UI dependencies.
    """
    
    def __init__(self, client_data: ClientData):
        self.data = client_data
    
    def retirement_projection(self, 
                              expected_return: float = 0.07,
                              inflation: float = 0.03,
                              withdrawal_rate: float = 0.04) -> MetricResult:
        """
        Project retirement readiness using basic Monte Carlo concepts.
        """
        age = self.data.profile.age
        retirement_age = self.data.profile.retirement_age
        years_to_retirement = retirement_age - age
        
        # Current retirement assets
        retirement_assets = (
            self.data.assets.retirement_401k +
            self.data.assets.ira_traditional +
            self.data.assets.ira_roth +
            self.data.assets.brokerage_taxable * 0.8  # Assume some taxable for retirement
        )
        
        # Estimate annual contributions (simplified)
        annual_contribution = self.data.income.total_annual_income * 0.15  # Assume 15% savings
        
        # Future value calculation
        real_return = expected_return - inflation
        if real_return > 0 and years_to_retirement > 0:
            # FV of current assets
            fv_current = retirement_assets * ((1 + real_return) ** years_to_retirement)
            # FV of contributions (annuity)
            fv_contributions = annual_contribution * (((1 + real_return) ** years_to_retirement - 1) / real_return)
            projected_nest_egg = fv_current + fv_contributions
        else:
            projected_nest_egg = retirement_assets
        
        # Calculate sustainable withdrawal
        annual_withdrawal = projected_nest_egg * withdrawal_rate
        monthly_withdrawal = annual_withdrawal / 12
        
        # Compare to current expenses (adjusted for retirement - typically 70-80% of pre-retirement)
        retirement_expense_ratio = 0.75
        target_monthly = self.data.expenses.total_monthly_expenses * retirement_expense_ratio
        
        if target_monthly > 0:
            replacement_ratio = (monthly_withdrawal / target_monthly) * 100
        else:
            replacement_ratio = 100
        
        if replacement_ratio >= 100:
            status = HealthStatus.EXCELLENT
        elif replacement_ratio >= 85:
            status = HealthStatus.GOOD
        elif replacement_ratio >= 70:
            status = HealthStatus.FAIR
        elif replacement_ratio >= 50:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if replacement_ratio < 100:
            gap = target_monthly - monthly_withdrawal
            recommendations.append(f"Projected shortfall of ${gap:,.0f}/month in retirement")
            
            # Calculate additional savings needed
            additional_monthly = (gap / withdrawal_rate * 12) / (((1 + real_return) ** years_to_retirement - 1) / real_return) / 12
            recommendations.append(f"Increase monthly savings by ~${additional_monthly:,.0f} to close gap")
        
        if years_to_retirement < 10 and replacement_ratio < 85:
            recommendations.append("Consider delaying retirement or reducing expenses")
        
        return MetricResult(
            value=replacement_ratio,
            display_value=f"{replacement_ratio:.0f}% funded",
            status=status,
            benchmark=100.0,
            benchmark_label="100% = fully funded retirement",
            description=f"Projected nest egg: ${projected_nest_egg:,.0f} | Monthly income: ${monthly_withdrawal:,.0f}",
            recommendations=recommendations
        )
    
    def retirement_stress_test(self) -> MetricResult:
        """
        Stress test retirement plan against adverse scenarios.
        Simplified Monte Carlo probability of success.
        """
        # Run basic projections with different return assumptions
        base_projection = self.retirement_projection()
        
        # Pessimistic scenario (4% real return instead of 4%)
        pessimistic = self.retirement_projection(expected_return=0.05, inflation=0.035)
        
        # Calculate implied success probability based on scenarios
        if base_projection.value >= 100 and pessimistic.value >= 85:
            success_probability = 90
            status = HealthStatus.EXCELLENT
        elif base_projection.value >= 90 and pessimistic.value >= 70:
            success_probability = 75
            status = HealthStatus.GOOD
        elif base_projection.value >= 80 and pessimistic.value >= 60:
            success_probability = 60
            status = HealthStatus.FAIR
        elif base_projection.value >= 60:
            success_probability = 45
            status = HealthStatus.POOR
        else:
            success_probability = 30
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if success_probability < 75:
            recommendations.append("Plan shows vulnerability to market downturns")
        if success_probability < 60:
            recommendations.append("Consider building larger safety margin")
            recommendations.append("Explore part-time work options in early retirement")
        
        # Sequence of returns risk
        years_to_retirement = self.data.profile.retirement_age - self.data.profile.age
        if years_to_retirement < 5:
            recommendations.append("High sequence-of-returns risk - consider de-risking portfolio")
        
        return MetricResult(
            value=success_probability,
            display_value=f"{success_probability:.0f}% success rate",
            status=status,
            benchmark=80.0,
            benchmark_label="80%+ success rate recommended",
            description=f"Base case: {base_projection.value:.0f}% funded | Stress test: {pessimistic.value:.0f}% funded",
            recommendations=recommendations
        )
    
    def goal_progress(self, goal: GoalData) -> MetricResult:
        """
        Calculate progress toward a specific financial goal.
        """
        if goal.target_amount <= 0:
            return MetricResult(
                value=0,
                display_value="N/A",
                status=HealthStatus.FAIR,
                description="Goal target not set",
                recommendations=["Set a specific target amount for this goal"]
            )
        
        progress_pct = (goal.current_amount / goal.target_amount) * 100
        
        # Calculate if on track based on time
        today = date.today()
        days_total = (goal.target_date - today).days
        
        if days_total <= 0:
            # Goal date passed
            if progress_pct >= 100:
                status = HealthStatus.EXCELLENT
                on_track = True
            else:
                status = HealthStatus.CRITICAL
                on_track = False
        else:
            # Calculate required monthly savings
            months_remaining = max(1, days_total / 30)
            remaining_amount = goal.target_amount - goal.current_amount
            required_monthly = remaining_amount / months_remaining
            
            if goal.monthly_contribution >= required_monthly:
                on_track = True
                if progress_pct >= 75:
                    status = HealthStatus.EXCELLENT
                elif progress_pct >= 50:
                    status = HealthStatus.GOOD
                else:
                    status = HealthStatus.GOOD
            else:
                on_track = False
                shortfall_ratio = goal.monthly_contribution / required_monthly if required_monthly > 0 else 0
                if shortfall_ratio >= 0.8:
                    status = HealthStatus.FAIR
                elif shortfall_ratio >= 0.5:
                    status = HealthStatus.POOR
                else:
                    status = HealthStatus.CRITICAL
        
        recommendations = []
        if not on_track and days_total > 0:
            months_remaining = max(1, days_total / 30)
            remaining_amount = goal.target_amount - goal.current_amount
            required_monthly = remaining_amount / months_remaining
            gap = required_monthly - goal.monthly_contribution
            recommendations.append(f"Increase monthly contribution by ${gap:,.0f} to stay on track")
        
        return MetricResult(
            value=progress_pct,
            display_value=f"{progress_pct:.0f}%",
            status=status,
            benchmark=100.0,
            benchmark_label="100% = goal achieved",
            description=f"${goal.current_amount:,.0f} of ${goal.target_amount:,.0f} saved",
            recommendations=recommendations
        )
    
    def all_goals_summary(self) -> Dict[str, MetricResult]:
        """Get progress for all goals."""
        return {goal.goal_id: self.goal_progress(goal) for goal in self.data.goals}
    
    def scenario_analysis(self, 
                          income_change_pct: float = 0,
                          expense_change_pct: float = 0,
                          market_return_change: float = 0,
                          retirement_age_change: int = 0) -> MetricResult:
        """
        What-if scenario analysis for retirement.
        """
        # Create modified projection
        original = self.retirement_projection()
        
        # Adjust parameters
        modified_return = 0.07 + market_return_change
        modified_retirement_age = self.data.profile.retirement_age + retirement_age_change
        
        # Calculate modified projection (simplified)
        years_to_retirement = modified_retirement_age - self.data.profile.age
        
        retirement_assets = (
            self.data.assets.retirement_401k +
            self.data.assets.ira_traditional +
            self.data.assets.ira_roth +
            self.data.assets.brokerage_taxable * 0.8
        )
        
        # Modified income affects contributions
        modified_income = self.data.income.total_annual_income * (1 + income_change_pct/100)
        annual_contribution = modified_income * 0.15
        
        # Modified expenses affect target
        modified_expenses = self.data.expenses.total_monthly_expenses * (1 + expense_change_pct/100)
        
        real_return = modified_return - 0.03
        if real_return > 0 and years_to_retirement > 0:
            fv_current = retirement_assets * ((1 + real_return) ** years_to_retirement)
            fv_contributions = annual_contribution * (((1 + real_return) ** years_to_retirement - 1) / real_return)
            projected_nest_egg = fv_current + fv_contributions
        else:
            projected_nest_egg = retirement_assets
        
        monthly_withdrawal = (projected_nest_egg * 0.04) / 12
        target_monthly = modified_expenses * 0.75
        
        if target_monthly > 0:
            modified_replacement = (monthly_withdrawal / target_monthly) * 100
        else:
            modified_replacement = 100
        
        change = modified_replacement - original.value
        
        if modified_replacement >= 100:
            status = HealthStatus.EXCELLENT
        elif modified_replacement >= 85:
            status = HealthStatus.GOOD
        elif modified_replacement >= 70:
            status = HealthStatus.FAIR
        elif modified_replacement >= 50:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        scenario_desc = []
        if income_change_pct != 0:
            scenario_desc.append(f"Income {income_change_pct:+.0f}%")
        if expense_change_pct != 0:
            scenario_desc.append(f"Expenses {expense_change_pct:+.0f}%")
        if market_return_change != 0:
            scenario_desc.append(f"Returns {market_return_change*100:+.1f}%")
        if retirement_age_change != 0:
            scenario_desc.append(f"Retire at {modified_retirement_age}")
        
        return MetricResult(
            value=modified_replacement,
            display_value=f"{modified_replacement:.0f}% funded",
            status=status,
            benchmark=original.value,
            benchmark_label=f"Base case: {original.value:.0f}%",
            trend=change,
            description=" | ".join(scenario_desc) if scenario_desc else "Base scenario",
            recommendations=[f"This scenario {'improves' if change > 0 else 'worsens'} outlook by {abs(change):.0f}%"]
        )
    
    def get_section_summary(self) -> dict:
        """Get all metrics for this section with overall health score."""
        metrics = {
            "retirement_projection": self.retirement_projection(),
            "stress_test": self.retirement_stress_test(),
        }
        
        # Add goal progress
        for goal in self.data.goals:
            metrics[f"goal_{goal.goal_id}"] = self.goal_progress(goal)
        
        status_scores = {
            HealthStatus.EXCELLENT: 100,
            HealthStatus.GOOD: 75,
            HealthStatus.FAIR: 50,
            HealthStatus.POOR: 25,
            HealthStatus.CRITICAL: 0
        }
        
        # Weight retirement metrics more heavily
        retirement_weight = 2
        goal_weight = 1
        
        total_score = (
            status_scores[metrics["retirement_projection"].status] * retirement_weight +
            status_scores[metrics["stress_test"].status] * retirement_weight
        )
        total_weight = retirement_weight * 2
        
        for goal in self.data.goals:
            total_score += status_scores[metrics[f"goal_{goal.goal_id}"].status] * goal_weight
            total_weight += goal_weight
        
        avg_score = total_score / total_weight if total_weight > 0 else 50
        
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
            "section_title": "Future Planning & Projections",
            "section_question": "Are they on track for their goals?"
        }
