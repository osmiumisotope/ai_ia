"""
Client data loader module.
Loads client data from the database and converts to ClientData models.
"""

from datetime import date, datetime
from typing import Dict, List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import (
    init_database,
    database_exists,
    get_primary_clients,
    get_client_by_id,
    get_client_accounts,
    get_account_holdings,
    get_client_liabilities,
    get_client_income,
    get_client_goals,
    get_client_insurance,
    get_client_estate_planning,
    get_client_portfolio_metrics,
    get_client_transactions,
    fetch_all
)

from logic.models import (
    ClientProfile, IncomeData, ExpenseData, AssetData, LiabilityData,
    InsuranceData, PortfolioAllocation, PortfolioMetrics, GoalData,
    EstateData, ClientData, RiskLevel
)


def _parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse a date string to a date object."""
    if not date_str:
        return None
    try:
        if isinstance(date_str, date):
            return date_str
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def _calculate_age(date_of_birth: str) -> int:
    """Calculate age from date of birth."""
    if not date_of_birth:
        return 0
    try:
        dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except (ValueError, TypeError):
        return 0


def _get_risk_level(risk_str: Optional[str]) -> RiskLevel:
    """Convert risk tolerance string to RiskLevel enum."""
    mapping = {
        'low': RiskLevel.LOW,
        'moderate': RiskLevel.MODERATE,
        'high': RiskLevel.HIGH,
        'critical': RiskLevel.CRITICAL
    }
    return mapping.get(risk_str, RiskLevel.MODERATE)


def _load_client_profile(client_row: Dict) -> ClientProfile:
    """Load client profile from database row."""
    return ClientProfile(
        client_id=client_row['id'],
        name=client_row['name'],
        age=_calculate_age(client_row['date_of_birth']),
        retirement_age=client_row.get('retirement_age', 65) or 65,
        risk_tolerance=_get_risk_level(client_row.get('risk_tolerance')),
        dependents=0,
        marital_status=client_row.get('marital_status', 'single') or 'single',
        state=client_row.get('state', 'CA') or 'CA'
    )


def _load_income_data(client_id: str) -> IncomeData:
    """Load income data for a client from database."""
    income_rows = get_client_income(client_id)
    
    annual_salary = 0.0
    bonus = 0.0
    other_income = 0.0
    rental_income = 0.0
    investment_income = 0.0
    
    for row in income_rows:
        amount = row.get('amount', 0) or 0
        frequency = row.get('frequency', 'annual')
        income_type = row.get('income_type', 'other')
        
        # Convert monthly to annual
        if frequency == 'monthly':
            amount = amount * 12
        
        if income_type == 'salary':
            annual_salary += amount
        elif income_type == 'bonus':
            bonus += amount
        elif income_type == 'rental':
            rental_income += amount
        elif income_type == 'investment':
            investment_income += amount
        else:
            other_income += amount
    
    return IncomeData(
        annual_salary=annual_salary,
        bonus=bonus,
        other_income=other_income,
        rental_income=rental_income,
        investment_income=investment_income
    )


def _load_expense_data(client_id: str, income_data: IncomeData) -> ExpenseData:
    """
    Load expense data for a client.
    Estimates based on transactions and liabilities.
    """
    transactions = get_client_transactions(client_id, limit=100)
    
    # Calculate monthly totals from transactions
    monthly_debits = {}
    for txn in transactions:
        if txn.get('direction') == 'debit':
            txn_type = txn.get('type', 'other')
            amount = txn.get('amount', 0) or 0
            monthly_debits[txn_type] = monthly_debits.get(txn_type, 0) + amount
    
    # Get liabilities to determine debt payments
    liabilities = get_client_liabilities(client_id)
    total_minimum_payments = sum(
        (l.get('minimum_payment', 0) or 0) for l in liabilities
    )
    
    # Estimate expenses based on income and typical ratios
    monthly_income = income_data.monthly_income
    
    # Use transaction data if available, otherwise estimate
    housing = monthly_debits.get('mortgage', monthly_income * 0.25)
    
    return ExpenseData(
        housing=housing,
        utilities=monthly_income * 0.02,
        transportation=monthly_income * 0.08,
        groceries=monthly_income * 0.06,
        healthcare=monthly_income * 0.03,
        insurance_premiums=monthly_income * 0.04,
        debt_payments=total_minimum_payments if total_minimum_payments > 0 else monthly_income * 0.05,
        childcare=0,
        entertainment=monthly_income * 0.03,
        dining_out=monthly_income * 0.03,
        subscriptions=200,
        shopping=monthly_income * 0.03,
        travel=monthly_income * 0.02,
        other=monthly_income * 0.02
    )


def _load_asset_data(client_id: str) -> AssetData:
    """Load asset data for a client from database."""
    accounts = get_client_accounts(client_id)
    
    # Initialize asset values
    checking_accounts = 0.0
    savings_accounts = 0.0
    money_market = 0.0
    cds = 0.0
    brokerage_taxable = 0.0
    ira_traditional = 0.0
    ira_roth = 0.0
    retirement_401k = 0.0
    hsa = 0.0
    company_stock_vested = 0.0
    rsu_unvested = 0.0
    stock_options_value = 0.0
    real_estate_primary = 0.0
    real_estate_investment = 0.0
    crypto = 0.0
    
    for account in accounts:
        account_id = account['id']
        account_type = account.get('account_type_name', '')
        
        # Get holdings for this account
        holdings = get_account_holdings(account_id)
        account_value = sum((h.get('cost_basis', 0) or 0) for h in holdings)
        
        # Check for crypto holdings
        crypto_value = sum(
            (h.get('cost_basis', 0) or 0) 
            for h in holdings 
            if h.get('security_type') == 'crypto'
        )
        crypto += crypto_value
        
        # Categorize by account type
        if account_type == 'checking':
            checking_accounts += account_value
        elif account_type == 'savings':
            savings_accounts += account_value
        elif account_type == 'brokerage':
            brokerage_taxable += account_value - crypto_value
        elif account_type == '401k' or account_type == 'roth_401k':
            retirement_401k += account_value
        elif account_type == 'traditional_ira':
            ira_traditional += account_value
        elif account_type == 'roth_ira':
            ira_roth += account_value
        elif account_type == 'hsa':
            hsa += account_value
        elif account_type == '529':
            brokerage_taxable += account_value
        elif account_type == 'real_estate':
            real_estate_primary += account_value
    
    return AssetData(
        checking_accounts=checking_accounts,
        savings_accounts=savings_accounts,
        money_market=money_market,
        cds=cds,
        brokerage_taxable=brokerage_taxable,
        ira_traditional=ira_traditional,
        ira_roth=ira_roth,
        retirement_401k=retirement_401k,
        hsa=hsa,
        company_stock_vested=company_stock_vested,
        rsu_unvested=rsu_unvested,
        stock_options_value=stock_options_value,
        real_estate_primary=real_estate_primary,
        real_estate_investment=real_estate_investment,
        business_equity=0,
        crypto=crypto,
        collectibles=0,
        other_assets=0
    )


def _load_liability_data(client_id: str) -> LiabilityData:
    """Load liability data for a client from database."""
    liabilities = get_client_liabilities(client_id)
    
    mortgage_primary = 0.0
    mortgage_investment = 0.0
    auto_loans = 0.0
    student_loans = 0.0
    credit_cards = 0.0
    personal_loans = 0.0
    heloc = 0.0
    other_debt = 0.0
    
    for liability in liabilities:
        balance = liability.get('balance', 0) or 0
        liability_type = liability.get('liability_type', 'other')
        
        if liability_type == 'mortgage_primary':
            mortgage_primary += balance
        elif liability_type == 'mortgage_investment':
            mortgage_investment += balance
        elif liability_type == 'auto_loan':
            auto_loans += balance
        elif liability_type == 'student_loan':
            student_loans += balance
        elif liability_type == 'credit_card':
            credit_cards += balance
        elif liability_type == 'personal_loan':
            personal_loans += balance
        elif liability_type == 'heloc':
            heloc += balance
        else:
            other_debt += balance
    
    return LiabilityData(
        mortgage_primary=mortgage_primary,
        mortgage_investment=mortgage_investment,
        auto_loans=auto_loans,
        student_loans=student_loans,
        credit_cards=credit_cards,
        personal_loans=personal_loans,
        heloc=heloc,
        other_debt=other_debt
    )


def _load_insurance_data(client_id: str) -> InsuranceData:
    """Load insurance data for a client from database."""
    insurance = get_client_insurance(client_id)
    
    if not insurance:
        return InsuranceData(
            life_insurance_coverage=0,
            life_insurance_type="none",
            disability_coverage_monthly=0,
            disability_coverage_type="none",
            umbrella_coverage=0,
            long_term_care=False
        )
    
    disability_type = insurance.get('disability_coverage_type', 'none')
    if disability_type == 'short_term':
        disability_type = 'short-term'
    elif disability_type == 'long_term':
        disability_type = 'long-term'
    
    return InsuranceData(
        life_insurance_coverage=insurance.get('life_insurance_coverage', 0) or 0,
        life_insurance_type=insurance.get('life_insurance_type', 'none') or 'none',
        disability_coverage_monthly=insurance.get('disability_coverage_monthly', 0) or 0,
        disability_coverage_type=disability_type,
        umbrella_coverage=insurance.get('umbrella_coverage', 0) or 0,
        long_term_care=insurance.get('long_term_care', False) or False
    )


def _load_portfolio_allocation(client_id: str) -> PortfolioAllocation:
    """Calculate portfolio allocation from holdings."""
    accounts = get_client_accounts(client_id)
    
    us_stocks = 0.0
    international_stocks = 0.0
    bonds = 0.0
    real_estate = 0.0
    commodities = 0.0
    cash = 0.0
    alternatives = 0.0
    crypto = 0.0
    total_value = 0.0
    
    for account in accounts:
        account_id = account['id']
        holdings = get_account_holdings(account_id)
        
        for holding in holdings:
            value = holding.get('cost_basis', 0) or 0
            total_value += value
            security_type = holding.get('security_type', 'other')
            security_name = (holding.get('security_name', '') or '').lower()
            
            if security_type == 'cash':
                cash += value
            elif security_type == 'crypto':
                crypto += value
            elif security_type == 'bond':
                bonds += value
            elif security_type == 'real_estate':
                real_estate += value
            elif security_type in ['stock', 'etf', 'mutual_fund']:
                if 'bond' in security_name or 'bnd' in security_name:
                    bonds += value
                elif 'international' in security_name or 'vxus' in security_name or 'intl' in security_name:
                    international_stocks += value
                elif 'real estate' in security_name or 'reit' in security_name:
                    real_estate += value
                else:
                    us_stocks += value
            else:
                alternatives += value
    
    if total_value > 0:
        return PortfolioAllocation(
            us_stocks=round(us_stocks / total_value * 100, 1),
            international_stocks=round(international_stocks / total_value * 100, 1),
            bonds=round(bonds / total_value * 100, 1),
            real_estate=round(real_estate / total_value * 100, 1),
            commodities=round(commodities / total_value * 100, 1),
            cash=round(cash / total_value * 100, 1),
            alternatives=round(alternatives / total_value * 100, 1),
            crypto=round(crypto / total_value * 100, 1)
        )
    
    return PortfolioAllocation(
        us_stocks=60, international_stocks=15, bonds=15,
        real_estate=5, commodities=0, cash=5, alternatives=0, crypto=0
    )


def _load_portfolio_metrics(client_id: str) -> PortfolioMetrics:
    """Load portfolio metrics for a client from database."""
    metrics = get_client_portfolio_metrics(client_id)
    
    if not metrics:
        return PortfolioMetrics(
            weighted_expense_ratio=0.5,
            annual_turnover=20,
            tax_efficiency_score=70,
            concentration_score=70,
            trades_last_12_months=12
        )
    
    return PortfolioMetrics(
        weighted_expense_ratio=metrics.get('weighted_expense_ratio', 0.5) or 0.5,
        annual_turnover=metrics.get('annual_turnover', 20) or 20,
        tax_efficiency_score=metrics.get('tax_efficiency_score', 70) or 70,
        concentration_score=metrics.get('concentration_score', 70) or 70,
        trades_last_12_months=metrics.get('trades_last_12_months', 12) or 12
    )


def _calculate_goal_current_amount(goal_id: str) -> float:
    """Calculate the current amount saved towards a goal."""
    query = """
        SELECT gaa.allocation_percentage, a.id as account_id
        FROM goal_account_allocations gaa
        JOIN accounts a ON gaa.account_id = a.id
        WHERE gaa.goal_id = ?
    """
    allocations = fetch_all(query, (goal_id,))
    
    total = 0.0
    for allocation in allocations:
        account_id = allocation['account_id']
        percentage = allocation.get('allocation_percentage', 100) or 100
        holdings = get_account_holdings(account_id)
        account_value = sum((h.get('cost_basis', 0) or 0) for h in holdings)
        total += account_value * (percentage / 100)
    
    return total


def _load_goals(client_id: str) -> List[GoalData]:
    """Load goals for a client from database."""
    goals = get_client_goals(client_id)
    
    result = []
    for goal in goals:
        current_amount = _calculate_goal_current_amount(goal['id'])
        
        result.append(GoalData(
            goal_id=goal['id'],
            name=goal.get('name', 'Unnamed Goal'),
            target_amount=goal.get('target_amount', 0) or 0,
            current_amount=current_amount,
            target_date=_parse_date(goal.get('target_date')) or date.today(),
            priority=goal.get('priority', 3) or 3,
            monthly_contribution=goal.get('monthly_contribution', 0) or 0
        ))
    
    return result


def _load_estate_data(client_id: str) -> EstateData:
    """Load estate planning data for a client from database."""
    estate = get_client_estate_planning(client_id)
    
    if not estate:
        return EstateData(
            has_will=False, will_last_updated=None, has_trust=False,
            has_poa_financial=False, has_poa_healthcare=False,
            has_healthcare_directive=False, beneficiaries_updated=False,
            beneficiaries_last_reviewed=None, digital_estate_documented=False
        )
    
    return EstateData(
        has_will=estate.get('has_will', False) or False,
        will_last_updated=_parse_date(estate.get('will_last_updated')),
        has_trust=estate.get('has_trust', False) or False,
        has_poa_financial=estate.get('has_poa_financial', False) or False,
        has_poa_healthcare=estate.get('has_poa_healthcare', False) or False,
        has_healthcare_directive=estate.get('has_healthcare_directive', False) or False,
        beneficiaries_updated=estate.get('beneficiaries_updated', False) or False,
        beneficiaries_last_reviewed=_parse_date(estate.get('beneficiaries_last_reviewed')),
        digital_estate_documented=estate.get('digital_estate_documented', False) or False
    )


def load_client_data(client_id: str) -> Optional[ClientData]:
    """Load complete client data from database."""
    if not database_exists():
        init_database(seed_data=True)
    
    client_row = get_client_by_id(client_id)
    if not client_row:
        return None
    
    profile = _load_client_profile(client_row)
    income = _load_income_data(client_id)
    expenses = _load_expense_data(client_id, income)
    assets = _load_asset_data(client_id)
    liabilities = _load_liability_data(client_id)
    insurance = _load_insurance_data(client_id)
    portfolio_allocation = _load_portfolio_allocation(client_id)
    portfolio_metrics = _load_portfolio_metrics(client_id)
    goals = _load_goals(client_id)
    estate = _load_estate_data(client_id)
    
    return ClientData(
        profile=profile, income=income, expenses=expenses,
        assets=assets, liabilities=liabilities, insurance=insurance,
        portfolio_allocation=portfolio_allocation,
        portfolio_metrics=portfolio_metrics, goals=goals, estate=estate
    )


def get_all_clients_from_db() -> Dict[str, ClientData]:
    """Load all primary clients from database."""
    if not database_exists():
        init_database(seed_data=True)
    
    clients = get_primary_clients()
    result = {}
    
    for client_row in clients:
        client_id = client_row['id']
        client_data = load_client_data(client_id)
        if client_data:
            result[client_id] = client_data
    
    return result


def get_historical_expenses_from_db(client_id: str) -> List[float]:
    """Get historical expense data for lifestyle creep analysis."""
    transactions = get_client_transactions(client_id, limit=500)
    
    monthly_expenses = {}
    for txn in transactions:
        if txn.get('direction') == 'debit':
            date_str = txn.get('date', '')
            if date_str:
                try:
                    txn_date = datetime.strptime(date_str, '%Y-%m-%d')
                    month_key = txn_date.strftime('%Y-%m')
                    monthly_expenses[month_key] = monthly_expenses.get(month_key, 0) + (txn.get('amount', 0) or 0)
                except (ValueError, TypeError):
                    pass
    
    sorted_months = sorted(monthly_expenses.keys())[-24:]
    
    if len(sorted_months) < 24:
        income_data = _load_income_data(client_id)
        estimated_monthly = income_data.monthly_income * 0.65
        
        result = []
        for i in range(24):
            if i < len(sorted_months):
                result.append(monthly_expenses[sorted_months[i]])
            else:
                variation = 1 + (i % 5 - 2) * 0.02
                result.append(estimated_monthly * variation)
        return result
    
    return [monthly_expenses[m] for m in sorted_months]
