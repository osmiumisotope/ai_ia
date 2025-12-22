"""
Sample client data for demonstration purposes.
This module provides realistic dummy data for the dashboard.
"""

from datetime import date, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.models import (
    ClientProfile, IncomeData, ExpenseData, AssetData, LiabilityData,
    InsuranceData, PortfolioAllocation, PortfolioMetrics, GoalData,
    EstateData, ClientData, RiskLevel
)


def get_sample_client_1() -> ClientData:
    """
    Sample Client: Sarah Chen - High-earning tech professional
    Age 38, married, 2 kids, good savings but some gaps
    """
    profile = ClientProfile(
        client_id="SC001",
        name="Sarah Chen",
        age=38,
        retirement_age=60,
        risk_tolerance=RiskLevel.MODERATE,
        dependents=2,
        marital_status="married",
        state="CA"
    )
    
    income = IncomeData(
        annual_salary=285000,
        bonus=45000,
        other_income=0,
        rental_income=2400 * 12,  # Investment property
        investment_income=8500
    )
    
    expenses = ExpenseData(
        housing=4200,  # Mortgage
        utilities=350,
        transportation=850,  # Car payments + gas
        groceries=1200,
        healthcare=400,
        insurance_premiums=650,
        debt_payments=800,  # Student loans
        childcare=2800,
        entertainment=400,
        dining_out=600,
        subscriptions=180,
        shopping=500,
        travel=800,
        other=300
    )
    
    assets = AssetData(
        checking_accounts=25000,
        savings_accounts=45000,
        money_market=30000,
        cds=0,
        brokerage_taxable=185000,
        ira_traditional=75000,
        ira_roth=62000,
        retirement_401k=420000,
        hsa=18000,
        company_stock_vested=145000,
        rsu_unvested=280000,
        stock_options_value=95000,
        real_estate_primary=1250000,
        real_estate_investment=485000,
        business_equity=0,
        crypto=12000,
        collectibles=0,
        other_assets=25000
    )
    
    liabilities = LiabilityData(
        mortgage_primary=680000,
        mortgage_investment=320000,
        auto_loans=28000,
        student_loans=42000,
        credit_cards=4500,
        personal_loans=0,
        heloc=0,
        other_debt=0
    )
    
    insurance = InsuranceData(
        life_insurance_coverage=1500000,
        life_insurance_type="term",
        disability_coverage_monthly=12000,
        disability_coverage_type="long-term",
        umbrella_coverage=2000000,
        long_term_care=False
    )
    
    portfolio = PortfolioAllocation(
        us_stocks=52,
        international_stocks=18,
        bonds=15,
        real_estate=8,
        commodities=2,
        cash=3,
        alternatives=0,
        crypto=2
    )
    
    portfolio_metrics = PortfolioMetrics(
        weighted_expense_ratio=0.35,
        annual_turnover=28,
        tax_efficiency_score=72,
        concentration_score=58,  # Company stock concentration
        trades_last_12_months=18
    )
    
    goals = [
        GoalData(
            goal_id="college_1",
            name="College Fund - Child 1",
            target_amount=250000,
            current_amount=85000,
            target_date=date.today() + timedelta(days=365*10),
            priority=1,
            monthly_contribution=1200
        ),
        GoalData(
            goal_id="college_2",
            name="College Fund - Child 2",
            target_amount=250000,
            current_amount=45000,
            target_date=date.today() + timedelta(days=365*13),
            priority=2,
            monthly_contribution=1000
        ),
        GoalData(
            goal_id="vacation_home",
            name="Vacation Home Down Payment",
            target_amount=200000,
            current_amount=65000,
            target_date=date.today() + timedelta(days=365*5),
            priority=3,
            monthly_contribution=2000
        )
    ]
    
    estate = EstateData(
        has_will=True,
        will_last_updated=date.today() - timedelta(days=365*4),
        has_trust=False,
        has_poa_financial=True,
        has_poa_healthcare=True,
        has_healthcare_directive=False,
        beneficiaries_updated=True,
        beneficiaries_last_reviewed=date.today() - timedelta(days=365*2),
        digital_estate_documented=False
    )
    
    return ClientData(
        profile=profile,
        income=income,
        expenses=expenses,
        assets=assets,
        liabilities=liabilities,
        insurance=insurance,
        portfolio_allocation=portfolio,
        portfolio_metrics=portfolio_metrics,
        goals=goals,
        estate=estate
    )


def get_sample_client_2() -> ClientData:
    """
    Sample Client: Marcus Williams - Mid-career professional
    Age 45, single, moderate income, needs work on savings
    """
    profile = ClientProfile(
        client_id="MW002",
        name="Marcus Williams",
        age=45,
        retirement_age=65,
        risk_tolerance=RiskLevel.MODERATE,
        dependents=0,
        marital_status="single",
        state="TX"
    )
    
    income = IncomeData(
        annual_salary=125000,
        bonus=15000,
        other_income=5000,  # Side consulting
        rental_income=0,
        investment_income=3200
    )
    
    expenses = ExpenseData(
        housing=2200,
        utilities=200,
        transportation=600,
        groceries=600,
        healthcare=250,
        insurance_premiums=300,
        debt_payments=450,
        childcare=0,
        entertainment=350,
        dining_out=500,
        subscriptions=120,
        shopping=300,
        travel=400,
        other=200
    )
    
    assets = AssetData(
        checking_accounts=8000,
        savings_accounts=15000,
        money_market=5000,
        cds=10000,
        brokerage_taxable=45000,
        ira_traditional=120000,
        ira_roth=35000,
        retirement_401k=185000,
        hsa=8500,
        company_stock_vested=25000,
        rsu_unvested=0,
        stock_options_value=0,
        real_estate_primary=380000,
        real_estate_investment=0,
        business_equity=0,
        crypto=3000,
        collectibles=15000,
        other_assets=5000
    )
    
    liabilities = LiabilityData(
        mortgage_primary=245000,
        mortgage_investment=0,
        auto_loans=18000,
        student_loans=12000,
        credit_cards=8500,
        personal_loans=0,
        heloc=15000,
        other_debt=0
    )
    
    insurance = InsuranceData(
        life_insurance_coverage=250000,
        life_insurance_type="term",
        disability_coverage_monthly=5000,
        disability_coverage_type="short-term",
        umbrella_coverage=0,
        long_term_care=False
    )
    
    portfolio = PortfolioAllocation(
        us_stocks=45,
        international_stocks=10,
        bonds=25,
        real_estate=5,
        commodities=0,
        cash=12,
        alternatives=2,
        crypto=1
    )
    
    portfolio_metrics = PortfolioMetrics(
        weighted_expense_ratio=0.72,
        annual_turnover=45,
        tax_efficiency_score=55,
        concentration_score=75,
        trades_last_12_months=32
    )
    
    goals = [
        GoalData(
            goal_id="emergency",
            name="Emergency Fund Top-up",
            target_amount=50000,
            current_amount=28000,
            target_date=date.today() + timedelta(days=365*2),
            priority=1,
            monthly_contribution=800
        ),
        GoalData(
            goal_id="early_retire",
            name="Early Retirement Fund",
            target_amount=1500000,
            current_amount=385000,
            target_date=date.today() + timedelta(days=365*20),
            priority=2,
            monthly_contribution=1500
        )
    ]
    
    estate = EstateData(
        has_will=False,
        will_last_updated=None,
        has_trust=False,
        has_poa_financial=False,
        has_poa_healthcare=False,
        has_healthcare_directive=False,
        beneficiaries_updated=False,
        beneficiaries_last_reviewed=None,
        digital_estate_documented=False
    )
    
    return ClientData(
        profile=profile,
        income=income,
        expenses=expenses,
        assets=assets,
        liabilities=liabilities,
        insurance=insurance,
        portfolio_allocation=portfolio,
        portfolio_metrics=portfolio_metrics,
        goals=goals,
        estate=estate
    )


def get_sample_client_3() -> ClientData:
    """
    Sample Client: Jennifer & David Park - Pre-retirees
    Age 58, married, high net worth, approaching retirement
    """
    profile = ClientProfile(
        client_id="JDP003",
        name="Jennifer & David Park",
        age=58,
        retirement_age=62,
        risk_tolerance=RiskLevel.LOW,
        dependents=0,  # Adult children
        marital_status="married",
        state="WA"
    )
    
    income = IncomeData(
        annual_salary=195000,  # Combined
        bonus=25000,
        other_income=15000,  # Board positions
        rental_income=36000,
        investment_income=42000
    )
    
    expenses = ExpenseData(
        housing=3500,  # Mortgage almost paid off
        utilities=400,
        transportation=700,
        groceries=900,
        healthcare=800,
        insurance_premiums=1200,
        debt_payments=0,
        childcare=0,
        entertainment=500,
        dining_out=700,
        subscriptions=150,
        shopping=400,
        travel=1500,
        other=400
    )
    
    assets = AssetData(
        checking_accounts=45000,
        savings_accounts=120000,
        money_market=85000,
        cds=50000,
        brokerage_taxable=680000,
        ira_traditional=850000,
        ira_roth=220000,
        retirement_401k=1150000,
        hsa=45000,
        company_stock_vested=85000,
        rsu_unvested=0,
        stock_options_value=0,
        real_estate_primary=950000,
        real_estate_investment=620000,
        business_equity=150000,
        crypto=0,
        collectibles=45000,
        other_assets=30000
    )
    
    liabilities = LiabilityData(
        mortgage_primary=125000,
        mortgage_investment=280000,
        auto_loans=0,
        student_loans=0,
        credit_cards=0,
        personal_loans=0,
        heloc=0,
        other_debt=0
    )
    
    insurance = InsuranceData(
        life_insurance_coverage=500000,
        life_insurance_type="whole",
        disability_coverage_monthly=8000,
        disability_coverage_type="long-term",
        umbrella_coverage=3000000,
        long_term_care=True
    )
    
    portfolio = PortfolioAllocation(
        us_stocks=35,
        international_stocks=12,
        bonds=35,
        real_estate=10,
        commodities=3,
        cash=5,
        alternatives=0,
        crypto=0
    )
    
    portfolio_metrics = PortfolioMetrics(
        weighted_expense_ratio=0.22,
        annual_turnover=12,
        tax_efficiency_score=88,
        concentration_score=90,
        trades_last_12_months=8
    )
    
    goals = [
        GoalData(
            goal_id="retire_comfort",
            name="Retirement Lifestyle Fund",
            target_amount=4000000,
            current_amount=2945000,
            target_date=date.today() + timedelta(days=365*4),
            priority=1,
            monthly_contribution=8000
        ),
        GoalData(
            goal_id="grandkids",
            name="Grandchildren Education Fund",
            target_amount=300000,
            current_amount=125000,
            target_date=date.today() + timedelta(days=365*15),
            priority=2,
            monthly_contribution=800
        ),
        GoalData(
            goal_id="charity",
            name="Charitable Giving Fund",
            target_amount=500000,
            current_amount=180000,
            target_date=date.today() + timedelta(days=365*10),
            priority=3,
            monthly_contribution=2000
        )
    ]
    
    estate = EstateData(
        has_will=True,
        will_last_updated=date.today() - timedelta(days=365*1),
        has_trust=True,
        has_poa_financial=True,
        has_poa_healthcare=True,
        has_healthcare_directive=True,
        beneficiaries_updated=True,
        beneficiaries_last_reviewed=date.today() - timedelta(days=180),
        digital_estate_documented=True
    )
    
    return ClientData(
        profile=profile,
        income=income,
        expenses=expenses,
        assets=assets,
        liabilities=liabilities,
        insurance=insurance,
        portfolio_allocation=portfolio,
        portfolio_metrics=portfolio_metrics,
        goals=goals,
        estate=estate
    )


# Historical expense data for lifestyle creep tracking (monthly expenses for 24 months)
HISTORICAL_EXPENSES = {
    "SC001": [
        11800, 12100, 11900, 12300, 12000, 12200, 12400, 12100, 12500, 12300, 12600, 12400,
        12800, 12600, 12900, 13100, 12800, 13200, 13000, 13300, 13100, 13500, 13200, 14030
    ],
    "MW002": [
        5800, 5900, 6000, 5850, 6100, 6050, 6200, 6150, 6300, 6250, 6400, 6350,
        6500, 6450, 6600, 6550, 6700, 6650, 6800, 6750, 6900, 6850, 7000, 6670
    ],
    "JDP003": [
        10500, 10600, 10400, 10700, 10500, 10800, 10600, 10900, 10700, 11000, 10800, 11100,
        10900, 11200, 11000, 11300, 11100, 11150, 11050, 11200, 11100, 11250, 11150, 11150
    ]
}


def get_all_sample_clients() -> dict:
    """Return all sample clients keyed by ID."""
    return {
        "SC001": get_sample_client_1(),
        "MW002": get_sample_client_2(),
        "JDP003": get_sample_client_3()
    }


def get_historical_expenses(client_id: str) -> list:
    """Get historical expenses for a client."""
    return HISTORICAL_EXPENSES.get(client_id, [])
