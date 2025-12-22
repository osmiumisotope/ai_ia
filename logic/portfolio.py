"""
Investment & Portfolio Health Calculations.
"Is their money working efficiently?"
"""

from typing import List, Optional, Dict
from .models import ClientData, MetricResult, HealthStatus, RiskLevel


class PortfolioHealth:
    """
    Calculator for Section 3: Investment & Portfolio Health.
    All methods are pure Python with no UI dependencies.
    """
    
    def __init__(self, client_data: ClientData):
        self.data = client_data
    
    def allocation_appropriateness(self) -> MetricResult:
        """
        Evaluate if portfolio allocation matches risk tolerance and time horizon.
        Uses age-based and risk-tolerance guidelines.
        """
        allocation = self.data.portfolio_allocation
        age = self.data.profile.age
        risk_tolerance = self.data.profile.risk_tolerance
        years_to_retirement = self.data.profile.retirement_age - age
        
        current_equity = allocation.total_equity
        current_fixed = allocation.total_fixed_income
        
        # Calculate target equity based on age and risk tolerance
        base_equity = 110 - age  # Classic rule: 110 - age in stocks
        
        # Adjust for risk tolerance
        risk_adjustments = {
            RiskLevel.LOW: -15,
            RiskLevel.MODERATE: 0,
            RiskLevel.HIGH: 10,
            RiskLevel.CRITICAL: 15  # Aggressive
        }
        target_equity = base_equity + risk_adjustments.get(risk_tolerance, 0)
        target_equity = max(20, min(90, target_equity))  # Bound between 20-90%
        
        # Calculate deviation from target
        deviation = abs(current_equity - target_equity)
        
        if deviation <= 5:
            status = HealthStatus.EXCELLENT
        elif deviation <= 10:
            status = HealthStatus.GOOD
        elif deviation <= 20:
            status = HealthStatus.FAIR
        elif deviation <= 30:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if current_equity > target_equity + 10:
            recommendations.append(f"Portfolio is {current_equity - target_equity:.0f}% overweight equities for your profile")
            recommendations.append("Consider rebalancing to reduce risk exposure")
        elif current_equity < target_equity - 10:
            recommendations.append(f"Portfolio is {target_equity - current_equity:.0f}% underweight equities")
            recommendations.append("May be missing growth potential given your time horizon")
        
        if years_to_retirement < 10 and current_equity > 60:
            recommendations.append("Consider reducing equity exposure as retirement approaches")
        
        return MetricResult(
            value=current_equity,
            display_value=f"{current_equity:.0f}% Equity / {current_fixed:.0f}% Fixed",
            status=status,
            benchmark=target_equity,
            benchmark_label=f"Target: {target_equity:.0f}% equity for your profile",
            description=f"Current allocation vs recommended for age {age} with {risk_tolerance.value} risk tolerance",
            recommendations=recommendations
        )
    
    def concentration_risk(self) -> MetricResult:
        """
        Evaluate concentration risk from company stock, single positions, or sector exposure.
        """
        assets = self.data.assets
        total_investments = assets.investment_assets + assets.company_stock_total
        
        if total_investments == 0:
            return MetricResult(
                value=0,
                display_value="N/A",
                status=HealthStatus.FAIR,
                description="No investment assets to evaluate",
                recommendations=["Start building investment portfolio"]
            )
        
        # Calculate company stock concentration
        company_stock_pct = (assets.company_stock_total / total_investments) * 100
        
        # Score based on concentration (lower is better, but we display as diversification score)
        if company_stock_pct <= 5:
            concentration_score = 95
            status = HealthStatus.EXCELLENT
        elif company_stock_pct <= 10:
            concentration_score = 80
            status = HealthStatus.GOOD
        elif company_stock_pct <= 20:
            concentration_score = 60
            status = HealthStatus.FAIR
        elif company_stock_pct <= 35:
            concentration_score = 35
            status = HealthStatus.POOR
        else:
            concentration_score = 15
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if company_stock_pct > 10:
            excess = assets.company_stock_total - (total_investments * 0.10)
            recommendations.append(f"Company stock at {company_stock_pct:.0f}% - consider diversifying ${excess:,.0f}")
        if company_stock_pct > 20:
            recommendations.append("High company stock concentration adds employment + investment risk")
            recommendations.append("Consider 10b5-1 plan for systematic diversification")
        if assets.rsu_unvested > assets.company_stock_vested:
            recommendations.append("Monitor RSU vesting schedule for diversification planning")
        
        return MetricResult(
            value=concentration_score,
            display_value=f"{concentration_score:.0f}/100",
            status=status,
            benchmark=80.0,
            benchmark_label="80+ score recommended",
            description=f"Company stock: {company_stock_pct:.1f}% of portfolio",
            recommendations=recommendations
        )
    
    def expense_ratio_drag(self) -> MetricResult:
        """
        Evaluate weighted expense ratio impact on returns.
        Target: Under 0.20% for passive, under 0.75% for active.
        """
        expense_ratio = self.data.portfolio_metrics.weighted_expense_ratio
        total_investments = self.data.assets.investment_assets
        
        # Calculate annual cost
        annual_cost = total_investments * (expense_ratio / 100)
        
        # Calculate 30-year impact assuming 7% returns
        # Simplified: just show annual drag
        if expense_ratio <= 0.10:
            status = HealthStatus.EXCELLENT
        elif expense_ratio <= 0.25:
            status = HealthStatus.GOOD
        elif expense_ratio <= 0.50:
            status = HealthStatus.FAIR
        elif expense_ratio <= 1.0:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        # Calculate 30-year difference vs 0.10% benchmark
        benchmark_ratio = 0.10
        years = 30
        future_value_current = total_investments * ((1 + 0.07 - expense_ratio/100) ** years)
        future_value_optimal = total_investments * ((1 + 0.07 - benchmark_ratio/100) ** years)
        lifetime_cost = future_value_optimal - future_value_current
        
        recommendations = []
        if expense_ratio > 0.25:
            recommendations.append(f"Annual fee drag: ${annual_cost:,.0f}")
            recommendations.append(f"Potential 30-year impact: ${lifetime_cost:,.0f}")
        if expense_ratio > 0.50:
            recommendations.append("Consider switching to low-cost index funds")
        if expense_ratio > 1.0:
            recommendations.append("Review actively managed funds - most underperform after fees")
        
        return MetricResult(
            value=expense_ratio,
            display_value=f"{expense_ratio:.2f}%",
            status=status,
            benchmark=0.20,
            benchmark_label="0.20% or less recommended",
            description=f"Annual fee impact: ${annual_cost:,.0f}",
            recommendations=recommendations
        )
    
    def tax_efficiency(self) -> MetricResult:
        """
        Evaluate tax-efficient asset location.
        Score based on proper placement of assets in taxable vs tax-advantaged accounts.
        """
        score = self.data.portfolio_metrics.tax_efficiency_score
        
        if score >= 85:
            status = HealthStatus.EXCELLENT
        elif score >= 70:
            status = HealthStatus.GOOD
        elif score >= 50:
            status = HealthStatus.FAIR
        elif score >= 30:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if score < 70:
            recommendations.append("Consider asset location optimization")
        if score < 50:
            recommendations.append("Place bonds and REITs in tax-advantaged accounts")
            recommendations.append("Hold tax-efficient index funds in taxable accounts")
        
        # Check for tax-loss harvesting opportunities (simplified)
        if self.data.assets.brokerage_taxable > 100000:
            recommendations.append("Review taxable accounts for tax-loss harvesting opportunities")
        
        return MetricResult(
            value=score,
            display_value=f"{score:.0f}/100",
            status=status,
            benchmark=80.0,
            benchmark_label="80+ score for optimal tax efficiency",
            description="Asset location optimization score",
            recommendations=recommendations
        )
    
    def illiquid_net_worth(self) -> MetricResult:
        """
        Calculate and evaluate illiquid asset exposure.
        Context: Too much illiquidity can create problems; some is fine for diversification.
        """
        illiquid = self.data.assets.illiquid_assets
        total_nw = self.data.net_worth
        
        if total_nw > 0:
            illiquid_pct = (illiquid / total_nw) * 100
        else:
            illiquid_pct = 0
        
        # Illiquidity isn't inherently bad, but should be balanced
        if illiquid_pct <= 30:
            status = HealthStatus.EXCELLENT
        elif illiquid_pct <= 50:
            status = HealthStatus.GOOD
        elif illiquid_pct <= 70:
            status = HealthStatus.FAIR
        elif illiquid_pct <= 85:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if illiquid_pct > 50:
            recommendations.append(f"{illiquid_pct:.0f}% of net worth is illiquid - may limit flexibility")
        if illiquid_pct > 70:
            recommendations.append("Consider building liquid assets before additional illiquid investments")
        if self.data.assets.real_estate_primary > total_nw * 0.5:
            recommendations.append("Primary residence represents significant portion of net worth")
        
        return MetricResult(
            value=illiquid_pct,
            display_value=f"{illiquid_pct:.0f}%",
            status=status,
            benchmark=40.0,
            benchmark_label="40% or less in illiquid assets",
            description=f"Illiquid assets: ${illiquid:,.0f}",
            recommendations=recommendations
        )
    
    def behavioral_flags(self) -> MetricResult:
        """
        Flag potential behavioral issues: overtrading, return chasing, etc.
        """
        metrics = self.data.portfolio_metrics
        flags = []
        score = 100  # Start perfect, deduct for issues
        
        # Check for overtrading
        if metrics.trades_last_12_months > 50:
            flags.append("High trading activity (50+ trades/year)")
            score -= 25
        elif metrics.trades_last_12_months > 24:
            flags.append("Elevated trading activity")
            score -= 10
        
        # Check turnover
        if metrics.annual_turnover > 100:
            flags.append(f"High portfolio turnover ({metrics.annual_turnover:.0f}%)")
            score -= 20
        elif metrics.annual_turnover > 50:
            flags.append("Moderate-high portfolio turnover")
            score -= 10
        
        # Check concentration (already covered but flag behavior aspect)
        if self.data.portfolio_metrics.concentration_score < 50:
            flags.append("Portfolio concentration may indicate conviction bias")
            score -= 15
        
        score = max(0, score)
        
        if score >= 85:
            status = HealthStatus.EXCELLENT
        elif score >= 70:
            status = HealthStatus.GOOD
        elif score >= 50:
            status = HealthStatus.FAIR
        elif score >= 30:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if metrics.trades_last_12_months > 24:
            recommendations.append("Consider reducing trading frequency - costs add up")
        if metrics.annual_turnover > 50:
            recommendations.append("High turnover creates tax drag and trading costs")
        if len(flags) == 0:
            flags.append("No behavioral red flags detected")
        
        return MetricResult(
            value=score,
            display_value=f"{score:.0f}/100",
            status=status,
            benchmark=85.0,
            benchmark_label="85+ indicates disciplined investing",
            description="; ".join(flags[:2]) if flags else "Disciplined investment behavior",
            recommendations=recommendations
        )
    
    def get_section_summary(self) -> dict:
        """Get all metrics for this section with overall health score."""
        metrics = {
            "allocation": self.allocation_appropriateness(),
            "concentration_risk": self.concentration_risk(),
            "expense_ratio": self.expense_ratio_drag(),
            "tax_efficiency": self.tax_efficiency(),
            "illiquid_assets": self.illiquid_net_worth(),
            "behavioral_flags": self.behavioral_flags()
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
            "section_title": "Investment & Portfolio Health",
            "section_question": "Is their money working efficiently?"
        }
