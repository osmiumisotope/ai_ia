"""
Legacy & Estate Readiness Calculations.
"Is wealth transfer organized?"
"""

from typing import Optional
from datetime import date
from .models import ClientData, MetricResult, HealthStatus


class EstateReadiness:
    """
    Calculator for Section 5: Legacy & Estate Readiness.
    All methods are pure Python with no UI dependencies.
    """
    
    def __init__(self, client_data: ClientData):
        self.data = client_data
    
    def estate_planning_score(self) -> MetricResult:
        """
        Evaluate completeness of estate planning documents.
        """
        estate = self.data.estate
        score = 0
        max_score = 100
        
        checklist = {
            "Will": (estate.has_will, 25),
            "Trust": (estate.has_trust, 15),
            "Financial POA": (estate.has_poa_financial, 20),
            "Healthcare POA": (estate.has_poa_healthcare, 15),
            "Healthcare Directive": (estate.has_healthcare_directive, 15),
            "Beneficiaries Updated": (estate.beneficiaries_updated, 10)
        }
        
        completed = []
        missing = []
        
        for item, (has_it, points) in checklist.items():
            if has_it:
                score += points
                completed.append(item)
            else:
                missing.append(item)
        
        # Check if will is outdated (over 5 years)
        if estate.has_will and estate.will_last_updated:
            years_old = (date.today() - estate.will_last_updated).days / 365
            if years_old > 5:
                score -= 10
                missing.append("Will needs update (>5 years old)")
        
        score = max(0, min(100, score))
        
        if score >= 85:
            status = HealthStatus.EXCELLENT
        elif score >= 70:
            status = HealthStatus.GOOD
        elif score >= 50:
            status = HealthStatus.FAIR
        elif score >= 25:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        recommendations = []
        if not estate.has_will:
            recommendations.append("Create a will - essential for asset distribution")
        if not estate.has_poa_financial:
            recommendations.append("Establish financial power of attorney")
        if not estate.has_healthcare_directive:
            recommendations.append("Create healthcare directive/living will")
        if estate.has_will and estate.will_last_updated:
            years_old = (date.today() - estate.will_last_updated).days / 365
            if years_old > 3:
                recommendations.append(f"Review will (last updated {years_old:.0f} years ago)")
        if self.data.net_worth > 1000000 and not estate.has_trust:
            recommendations.append("Consider establishing a trust for tax efficiency")
        
        return MetricResult(
            value=score,
            display_value=f"{score:.0f}/100",
            status=status,
            benchmark=85.0,
            benchmark_label="85+ for comprehensive estate plan",
            description=f"Completed: {len(completed)}/6 key documents",
            recommendations=recommendations
        )
    
    def beneficiary_status(self) -> MetricResult:
        """
        Evaluate beneficiary designation status.
        """
        estate = self.data.estate
        
        if not estate.beneficiaries_updated:
            status = HealthStatus.CRITICAL
            score = 20
        elif estate.beneficiaries_last_reviewed:
            months_since_review = (date.today() - estate.beneficiaries_last_reviewed).days / 30
            if months_since_review <= 12:
                status = HealthStatus.EXCELLENT
                score = 100
            elif months_since_review <= 24:
                status = HealthStatus.GOOD
                score = 80
            elif months_since_review <= 36:
                status = HealthStatus.FAIR
                score = 60
            else:
                status = HealthStatus.POOR
                score = 40
        else:
            status = HealthStatus.FAIR
            score = 50
        
        recommendations = []
        if not estate.beneficiaries_updated:
            recommendations.append("Review and update all account beneficiaries")
            recommendations.append("Ensure beneficiaries align with current wishes and will")
        
        # Account-specific reminders
        accounts_with_beneficiaries = []
        if self.data.assets.retirement_401k > 0:
            accounts_with_beneficiaries.append("401(k)")
        if self.data.assets.ira_traditional > 0:
            accounts_with_beneficiaries.append("Traditional IRA")
        if self.data.assets.ira_roth > 0:
            accounts_with_beneficiaries.append("Roth IRA")
        if self.data.insurance.life_insurance_coverage > 0:
            accounts_with_beneficiaries.append("Life Insurance")
        
        if accounts_with_beneficiaries and not estate.beneficiaries_updated:
            recommendations.append(f"Check beneficiaries on: {', '.join(accounts_with_beneficiaries)}")
        
        if self.data.profile.marital_status == "married" and not estate.beneficiaries_updated:
            recommendations.append("Ensure spouse is primary beneficiary on retirement accounts")
        
        return MetricResult(
            value=score,
            display_value=f"{score:.0f}/100",
            status=status,
            benchmark=100.0,
            benchmark_label="Annual beneficiary review recommended",
            description="Beneficiary designation review status",
            recommendations=recommendations
        )
    
    def digital_estate_score(self) -> MetricResult:
        """
        Evaluate digital estate planning.
        """
        estate = self.data.estate
        
        if estate.digital_estate_documented:
            score = 100
            status = HealthStatus.EXCELLENT
        else:
            score = 0
            status = HealthStatus.POOR
        
        recommendations = []
        if not estate.digital_estate_documented:
            recommendations.append("Document digital assets and account access")
            recommendations.append("Consider a password manager with emergency access")
            recommendations.append("List cryptocurrency wallets and access keys")
            recommendations.append("Document social media account preferences (memorialize vs delete)")
        
        # Crypto-specific
        if self.data.assets.crypto > 0:
            if not estate.digital_estate_documented:
                recommendations.insert(0, f"URGENT: ${self.data.assets.crypto:,.0f} in crypto requires documented access")
        
        return MetricResult(
            value=score,
            display_value="Complete" if score == 100 else "Incomplete",
            status=status,
            benchmark=100.0,
            benchmark_label="Digital estate should be documented",
            description="Digital asset and account documentation",
            recommendations=recommendations
        )
    
    def account_titling_review(self) -> MetricResult:
        """
        Flag potential account titling issues.
        Simplified check based on marital status and asset types.
        """
        issues = []
        score = 100
        
        # Check for large taxable accounts without trust/TOD (simplified logic)
        taxable_assets = (
            self.data.assets.brokerage_taxable +
            self.data.assets.checking_accounts +
            self.data.assets.savings_accounts
        )
        
        if taxable_assets > 100000 and not self.data.estate.has_trust:
            issues.append("Large taxable accounts may benefit from trust titling")
            score -= 20
        
        # Real estate considerations
        if self.data.assets.real_estate_primary > 500000 and not self.data.estate.has_trust:
            issues.append("Consider trust for real estate to avoid probate")
            score -= 20
        
        # Joint account considerations for married couples
        if self.data.profile.marital_status == "married":
            if self.data.assets.brokerage_taxable > 250000:
                issues.append("Review joint vs individual account titling for tax efficiency")
                score -= 10
        
        score = max(0, score)
        
        if score >= 85:
            status = HealthStatus.EXCELLENT
        elif score >= 70:
            status = HealthStatus.GOOD
        elif score >= 50:
            status = HealthStatus.FAIR
        else:
            status = HealthStatus.POOR
        
        recommendations = issues if issues else ["Account titling appears appropriate"]
        
        return MetricResult(
            value=score,
            display_value=f"{score:.0f}/100",
            status=status,
            benchmark=85.0,
            benchmark_label="85+ indicates proper titling",
            description=f"{len(issues)} potential titling issues identified" if issues else "No issues identified",
            recommendations=recommendations
        )
    
    def get_section_summary(self) -> dict:
        """Get all metrics for this section with overall health score."""
        metrics = {
            "estate_planning": self.estate_planning_score(),
            "beneficiaries": self.beneficiary_status(),
            "digital_estate": self.digital_estate_score(),
            "account_titling": self.account_titling_review()
        }
        
        status_scores = {
            HealthStatus.EXCELLENT: 100,
            HealthStatus.GOOD: 75,
            HealthStatus.FAIR: 50,
            HealthStatus.POOR: 25,
            HealthStatus.CRITICAL: 0
        }
        
        # Weight estate planning more heavily
        weights = {
            "estate_planning": 2,
            "beneficiaries": 1.5,
            "digital_estate": 1,
            "account_titling": 1
        }
        
        total_score = sum(status_scores[metrics[k].status] * weights[k] for k in metrics)
        total_weight = sum(weights.values())
        avg_score = total_score / total_weight
        
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
            "section_title": "Legacy & Estate Readiness",
            "section_question": "Is wealth transfer organized?"
        }
