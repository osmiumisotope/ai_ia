"""
Data models and type definitions for the Financial Advisor Dashboard.
These models are framework-agnostic and can be used with any frontend.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import date
from enum import Enum


class RiskLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class HealthStatus(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class MetricResult:
    """Standard result format for any calculated metric."""
    value: float
    display_value: str
    status: HealthStatus
    benchmark: Optional[float] = None
    benchmark_label: Optional[str] = None
    trend: Optional[float] = None  # Percentage change
    description: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    delta: Optional[float] = None  # Absolute change from previous period
    delta_is_positive: Optional[bool] = None  # Whether the delta direction is good


@dataclass
class ClientProfile:
    """Basic client information."""
    client_id: str
    name: str
    age: int
    retirement_age: int
    risk_tolerance: RiskLevel
    dependents: int
    marital_status: str
    state: str


@dataclass
class IncomeData:
    """Client income information."""
    annual_salary: float
    bonus: float
    other_income: float
    rental_income: float
    investment_income: float
    
    @property
    def total_annual_income(self) -> float:
        return (self.annual_salary + self.bonus + self.other_income + 
                self.rental_income + self.investment_income)
    
    @property
    def monthly_income(self) -> float:
        return self.total_annual_income / 12


@dataclass
class ExpenseData:
    """Client expense breakdown."""
    housing: float  # Monthly
    utilities: float
    transportation: float
    groceries: float
    healthcare: float
    insurance_premiums: float
    debt_payments: float
    childcare: float
    entertainment: float
    dining_out: float
    subscriptions: float
    shopping: float
    travel: float
    other: float
    
    @property
    def total_monthly_expenses(self) -> float:
        return sum([
            self.housing, self.utilities, self.transportation,
            self.groceries, self.healthcare, self.insurance_premiums,
            self.debt_payments, self.childcare, self.entertainment,
            self.dining_out, self.subscriptions, self.shopping,
            self.travel, self.other
        ])
    
    @property
    def fixed_expenses(self) -> float:
        """Fixed/essential expenses that are harder to reduce."""
        return sum([
            self.housing, self.utilities, self.transportation,
            self.groceries, self.healthcare, self.insurance_premiums,
            self.debt_payments, self.childcare
        ])
    
    @property
    def discretionary_expenses(self) -> float:
        """Variable/discretionary expenses."""
        return sum([
            self.entertainment, self.dining_out, self.subscriptions,
            self.shopping, self.travel, self.other
        ])


@dataclass
class AssetData:
    """Client assets breakdown."""
    # Liquid Assets
    checking_accounts: float
    savings_accounts: float
    money_market: float
    cds: float
    
    # Investment Accounts
    brokerage_taxable: float
    ira_traditional: float
    ira_roth: float
    retirement_401k: float
    hsa: float
    
    # Company Stock
    company_stock_vested: float
    rsu_unvested: float
    stock_options_value: float
    
    # Other Assets
    real_estate_primary: float
    real_estate_investment: float
    business_equity: float
    crypto: float
    collectibles: float
    other_assets: float
    
    @property
    def liquid_assets(self) -> float:
        return (self.checking_accounts + self.savings_accounts + 
                self.money_market + self.cds)
    
    @property
    def investment_assets(self) -> float:
        return (self.brokerage_taxable + self.ira_traditional + 
                self.ira_roth + self.retirement_401k + self.hsa)
    
    @property
    def company_stock_total(self) -> float:
        return (self.company_stock_vested + self.rsu_unvested + 
                self.stock_options_value)
    
    @property
    def illiquid_assets(self) -> float:
        return (self.real_estate_primary + self.real_estate_investment +
                self.business_equity + self.crypto + self.collectibles +
                self.other_assets)
    
    @property
    def total_assets(self) -> float:
        return (self.liquid_assets + self.investment_assets + 
                self.company_stock_total + self.illiquid_assets)


@dataclass
class LiabilityData:
    """Client liabilities breakdown."""
    mortgage_primary: float
    mortgage_investment: float
    auto_loans: float
    student_loans: float
    credit_cards: float
    personal_loans: float
    heloc: float
    other_debt: float
    
    @property
    def total_liabilities(self) -> float:
        return sum([
            self.mortgage_primary, self.mortgage_investment,
            self.auto_loans, self.student_loans, self.credit_cards,
            self.personal_loans, self.heloc, self.other_debt
        ])
    
    @property
    def high_interest_debt(self) -> float:
        """Credit cards and personal loans typically have high interest."""
        return self.credit_cards + self.personal_loans


@dataclass
class InsuranceData:
    """Client insurance coverage."""
    life_insurance_coverage: float
    life_insurance_type: str  # "term", "whole", "universal"
    disability_coverage_monthly: float
    disability_coverage_type: str  # "short-term", "long-term", "both"
    umbrella_coverage: float
    long_term_care: bool


@dataclass
class PortfolioAllocation:
    """Investment portfolio allocation."""
    us_stocks: float  # Percentage
    international_stocks: float
    bonds: float
    real_estate: float
    commodities: float
    cash: float
    alternatives: float
    crypto: float
    
    @property
    def total_equity(self) -> float:
        return self.us_stocks + self.international_stocks
    
    @property
    def total_fixed_income(self) -> float:
        return self.bonds + self.cash


@dataclass
class PortfolioMetrics:
    """Additional portfolio metrics."""
    weighted_expense_ratio: float
    annual_turnover: float
    tax_efficiency_score: float  # 0-100
    concentration_score: float  # 0-100 (100 = well diversified)
    trades_last_12_months: int


@dataclass
class GoalData:
    """Financial goals."""
    goal_id: str
    name: str
    target_amount: float
    current_amount: float
    target_date: date
    priority: int  # 1-5
    monthly_contribution: float


@dataclass
class EstateData:
    """Estate planning information."""
    has_will: bool
    will_last_updated: Optional[date]
    has_trust: bool
    has_poa_financial: bool
    has_poa_healthcare: bool
    has_healthcare_directive: bool
    beneficiaries_updated: bool
    beneficiaries_last_reviewed: Optional[date]
    digital_estate_documented: bool


@dataclass
class ClientData:
    """Complete client financial data."""
    profile: ClientProfile
    income: IncomeData
    expenses: ExpenseData
    assets: AssetData
    liabilities: LiabilityData
    insurance: InsuranceData
    portfolio_allocation: PortfolioAllocation
    portfolio_metrics: PortfolioMetrics
    goals: List[GoalData]
    estate: EstateData
    
    @property
    def net_worth(self) -> float:
        return self.assets.total_assets - self.liabilities.total_liabilities
    
    @property
    def liquid_net_worth(self) -> float:
        return (self.assets.liquid_assets + self.assets.investment_assets - 
                self.liabilities.high_interest_debt)
