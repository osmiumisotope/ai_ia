"""
Financial Advisor Dashboard - Main Application
A comprehensive financial health dashboard built with Streamlit.

This dashboard is designed with a clean separation between:
- Logic layer (logic/) - Pure Python calculations, framework-agnostic
- Components layer (components/) - UI rendering components  
- Data layer (data/) - Sample data and data access

This separation makes it easy to port to React or any other frontend.
"""

import streamlit as st
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import logic calculators
from logic import (
    FinancialFoundation,
    CashFlowBehavior,
    PortfolioHealth,
    FuturePlanning,
    EstateReadiness,
    HealthStatus
)

# Import UI components
from components import (
    get_custom_css,
    render_header,
    render_net_worth_summary,
    render_section_header,
    render_metric_card,
    render_metric_grid,
    render_allocation_chart,
    render_goal_progress,
    render_expense_breakdown,
    render_retirement_projection_chart,
    render_asset_breakdown_chart,
    render_health_score_gauge
)

# Import sample data
from data import get_all_sample_clients, get_historical_expenses

# Page configuration
st.set_page_config(
    page_title="Financial Health Dashboard",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


def main():
    """Main application entry point."""
    
    # Sidebar for client selection and navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem; border-bottom: 1px solid #334155;">
            <h2 style="color: #10B981; margin: 0; font-size: 1.25rem;">WealthView</h2>
            <p style="color: #94A3B8; font-size: 0.75rem; margin-top: 0.25rem;">Financial Advisory Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Client selector
        st.markdown("<p style='font-size: 0.875rem; color: #94A3B8; margin-bottom: 0.5rem;'>Select Client</p>", unsafe_allow_html=True)
        clients = get_all_sample_clients()
        client_options = {
            f"{data.profile.name} ({cid})": cid 
            for cid, data in clients.items()
        }
        
        selected_display = st.selectbox(
            "Client",
            options=list(client_options.keys()),
            label_visibility="collapsed"
        )
        selected_client_id = client_options[selected_display]
        client_data = clients[selected_client_id]
        
        # Display client quick info - clean design without icons
        st.markdown(f"""
        <div style="background: #1E293B; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
            <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">Client Profile</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; font-size: 0.8rem;">
                <div>
                    <div style="color: #64748B; font-size: 0.7rem;">Age</div>
                    <div style="color: #F1F5F9; font-weight: 500;">{client_data.profile.age}</div>
                </div>
                <div>
                    <div style="color: #64748B; font-size: 0.7rem;">Retirement</div>
                    <div style="color: #F1F5F9; font-weight: 500;">{client_data.profile.retirement_age}</div>
                </div>
                <div>
                    <div style="color: #64748B; font-size: 0.7rem;">Dependents</div>
                    <div style="color: #F1F5F9; font-weight: 500;">{client_data.profile.dependents}</div>
                </div>
                <div>
                    <div style="color: #64748B; font-size: 0.7rem;">State</div>
                    <div style="color: #F1F5F9; font-weight: 500;">{client_data.profile.state}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        # Navigation with clickable cards
        st.markdown("<p style='font-size: 0.7rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;'>Navigation</p>", unsafe_allow_html=True)
        
        # Initialize session state for selected section
        if 'selected_section' not in st.session_state:
            st.session_state.selected_section = "Overview"
        
        nav_items = [
            ("Overview", "Financial summary and health scores"),
            ("Financial Foundation", "Safety net and debt analysis"),
            ("Cash Flow & Spending", "Income, expenses, and savings"),
            ("Portfolio Health", "Investment allocation and risk"),
            ("Future Planning", "Retirement and goal tracking"),
            ("Estate Readiness", "Legacy and estate documents")
        ]
        
        for nav_name, nav_desc in nav_items:
            is_active = st.session_state.selected_section == nav_name
            if st.button(
                nav_name,
                key=f"nav_{nav_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.selected_section = nav_name
                st.rerun()
        
        selected_section = st.session_state.selected_section
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 0.7rem; color: #475569; text-align: center;">
            Dashboard v1.0
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    render_header(client_data.profile.name, selected_client_id)
    
    # Initialize calculators with client data
    foundation_calc = FinancialFoundation(client_data)
    cashflow_calc = CashFlowBehavior(client_data, get_historical_expenses(selected_client_id))
    portfolio_calc = PortfolioHealth(client_data)
    planning_calc = FuturePlanning(client_data)
    estate_calc = EstateReadiness(client_data)
    
    # Get all section summaries
    foundation_summary = foundation_calc.get_section_summary()
    cashflow_summary = cashflow_calc.get_section_summary()
    portfolio_summary = portfolio_calc.get_section_summary()
    planning_summary = planning_calc.get_section_summary()
    estate_summary = estate_calc.get_section_summary()
    
    # Calculate overall health score
    all_scores = [
        foundation_summary['overall_score'],
        cashflow_summary['overall_score'],
        portfolio_summary['overall_score'],
        planning_summary['overall_score'],
        estate_summary['overall_score']
    ]
    overall_health_score = sum(all_scores) / len(all_scores)
    
    # Display based on selected section
    if selected_section == "Overview":
        render_overview(
            client_data, 
            overall_health_score,
            foundation_summary,
            cashflow_summary,
            portfolio_summary,
            planning_summary,
            estate_summary
        )
    elif selected_section == "Financial Foundation":
        render_foundation_section(foundation_summary, client_data)
    elif selected_section == "Cash Flow & Spending":
        render_cashflow_section(cashflow_summary, client_data)
    elif selected_section == "Portfolio Health":
        render_portfolio_section(portfolio_summary, client_data)
    elif selected_section == "Future Planning":
        render_planning_section(planning_summary, planning_calc, client_data)
    elif selected_section == "Estate Readiness":
        render_estate_section(estate_summary, client_data)


def render_overview(client_data, overall_score, foundation, cashflow, portfolio, planning, estate):
    """Render the overview dashboard section."""
    
    # Net worth and overall health
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_net_worth_summary(client_data)
    
    with col2:
        render_health_score_gauge(overall_score, "Overall Financial Health")
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Section score cards
    st.markdown("### 📊 Section Health Scores")
    
    sections = [
        ("🛡️ Financial Foundation", foundation),
        ("💰 Cash Flow", cashflow),
        ("📊 Portfolio", portfolio),
        ("🎯 Planning", planning),
        ("📋 Estate", estate)
    ]
    
    cols = st.columns(5)
    for i, (title, summary) in enumerate(sections):
        with cols[i]:
            score = summary['overall_score']
            status = summary['overall_status']
            color = {
                HealthStatus.EXCELLENT: '#10B981',
                HealthStatus.GOOD: '#3B82F6',
                HealthStatus.FAIR: '#F59E0B',
                HealthStatus.POOR: '#F97316',
                HealthStatus.CRITICAL: '#EF4444'
            }.get(status, '#94A3B8')
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1E293B 0%, rgba(30, 41, 59, 0.8) 100%); 
                        padding: 1.25rem; border-radius: 12px; border: 1px solid #334155; text-align: center;">
                <div style="font-size: 0.75rem; color: #94A3B8; margin-bottom: 0.5rem;">{title}</div>
                <div style="font-size: 2rem; font-weight: 700; color: {color};">{score:.0f}</div>
                <div style="font-size: 0.75rem; color: {color}; text-transform: uppercase; margin-top: 0.25rem;">
                    {status.value}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Quick insights row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Asset Allocation")
        allocation_data = {
            'US Stocks': client_data.portfolio_allocation.us_stocks,
            'Int\'l Stocks': client_data.portfolio_allocation.international_stocks,
            'Bonds': client_data.portfolio_allocation.bonds,
            'Real Estate': client_data.portfolio_allocation.real_estate,
            'Cash': client_data.portfolio_allocation.cash,
            'Other': client_data.portfolio_allocation.commodities + 
                    client_data.portfolio_allocation.alternatives +
                    client_data.portfolio_allocation.crypto
        }
        # Filter out zeros
        allocation_data = {k: v for k, v in allocation_data.items() if v > 0}
        render_allocation_chart(allocation_data)
    
    with col2:
        st.markdown("### 🎯 Goal Progress")
        goals_data = [
            {
                'name': goal.name,
                'current': goal.current_amount,
                'target': goal.target_amount,
                'priority': goal.priority,
                'status': planning['metrics'].get(f'goal_{goal.goal_id}', 
                         planning['metrics'].get(list(planning['metrics'].keys())[0])).status.value
            }
            for goal in client_data.goals
        ]
        render_goal_progress(goals_data)
    
    # Key recommendations
    st.markdown("### 💡 Priority Recommendations")
    
    all_recommendations = []
    for summary in [foundation, cashflow, portfolio, planning, estate]:
        for metric_name, metric in summary['metrics'].items():
            if metric.status in [HealthStatus.POOR, HealthStatus.CRITICAL]:
                for rec in metric.recommendations[:1]:  # Top recommendation per poor metric
                    all_recommendations.append({
                        'text': rec,
                        'severity': 'critical' if metric.status == HealthStatus.CRITICAL else 'poor'
                    })
    
    if all_recommendations:
        for rec in all_recommendations[:5]:  # Show top 5
            color = '#EF4444' if rec['severity'] == 'critical' else '#F97316'
            st.markdown(f"""
            <div style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.75rem; 
                        background: rgba({239 if rec['severity'] == 'critical' else 249}, 
                                        {68 if rec['severity'] == 'critical' else 115}, 
                                        {68 if rec['severity'] == 'critical' else 22}, 0.1); 
                        border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid {color};">
                <span style="color: {color}; font-size: 1rem;">⚠️</span>
                <span style="font-size: 0.875rem; color: #F1F5F9;">{rec['text']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("🎉 No critical recommendations - financial health looks good!")


def render_foundation_section(summary, client_data):
    """Render Financial Foundation section."""
    render_section_header(
        summary['section_title'],
        summary['section_question'],
        summary['overall_score'],
        summary['overall_status']
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Metrics grid
    render_metric_grid(summary['metrics'], columns=3)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Additional visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Asset Distribution")
        asset_data = {
            'Liquid Cash': client_data.assets.liquid_assets,
            'Investments': client_data.assets.investment_assets,
            'Company Stock': client_data.assets.company_stock_total,
            'Real Estate': client_data.assets.real_estate_primary + client_data.assets.real_estate_investment,
            'Other': client_data.assets.business_equity + client_data.assets.crypto + 
                    client_data.assets.collectibles + client_data.assets.other_assets
        }
        asset_data = {k: v for k, v in asset_data.items() if v > 0}
        render_asset_breakdown_chart(asset_data, "Asset Distribution")
    
    with col2:
        st.markdown("### Liability Breakdown")
        liability_data = {
            'Primary Mortgage': client_data.liabilities.mortgage_primary,
            'Investment Property': client_data.liabilities.mortgage_investment,
            'Auto Loans': client_data.liabilities.auto_loans,
            'Student Loans': client_data.liabilities.student_loans,
            'Credit Cards': client_data.liabilities.credit_cards,
            'Other Debt': client_data.liabilities.personal_loans + 
                         client_data.liabilities.heloc + client_data.liabilities.other_debt
        }
        liability_data = {k: v for k, v in liability_data.items() if v > 0}
        if liability_data:
            render_asset_breakdown_chart(liability_data, "Liability Breakdown")
        else:
            st.info("No liabilities!")


def render_cashflow_section(summary, client_data):
    """Render Cash Flow & Spending section."""
    render_section_header(
        summary['section_title'],
        summary['section_question'],
        summary['overall_score'],
        summary['overall_status']
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Key metrics
    render_metric_grid(summary['metrics'], columns=3)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Expense breakdown
    col1, col2 = st.columns([3, 2])
    
    with col1:
        expense_categories = {
            'Housing': client_data.expenses.housing,
            'Childcare': client_data.expenses.childcare,
            'Transportation': client_data.expenses.transportation,
            'Groceries': client_data.expenses.groceries,
            'Healthcare': client_data.expenses.healthcare,
            'Insurance': client_data.expenses.insurance_premiums,
            'Debt Payments': client_data.expenses.debt_payments,
            'Entertainment': client_data.expenses.entertainment,
            'Dining Out': client_data.expenses.dining_out,
            'Travel': client_data.expenses.travel,
            'Shopping': client_data.expenses.shopping,
            'Subscriptions': client_data.expenses.subscriptions,
            'Other': client_data.expenses.other + client_data.expenses.utilities
        }
        expense_categories = {k: v for k, v in expense_categories.items() if v > 0}
        render_expense_breakdown(expense_categories, client_data.income.monthly_income)
    
    with col2:
        st.markdown("### 💵 Income vs Expenses")
        monthly_income = client_data.income.monthly_income
        monthly_expenses = client_data.expenses.total_monthly_expenses
        monthly_savings = monthly_income - monthly_expenses
        
        st.markdown(f"""
        <div style="background: #1E293B; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155;">
            <div style="margin-bottom: 1.5rem;">
                <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Monthly Income</div>
                <div style="font-size: 1.75rem; font-weight: 700; color: #10B981;">${monthly_income:,.0f}</div>
            </div>
            <div style="margin-bottom: 1.5rem;">
                <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Monthly Expenses</div>
                <div style="font-size: 1.75rem; font-weight: 700; color: #F97316;">${monthly_expenses:,.0f}</div>
            </div>
            <div style="padding-top: 1rem; border-top: 1px solid #334155;">
                <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Monthly Savings</div>
                <div style="font-size: 1.75rem; font-weight: 700; color: {'#10B981' if monthly_savings > 0 else '#EF4444'};">
                    ${monthly_savings:,.0f}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Expense breakdown by type
        fixed = client_data.expenses.fixed_expenses
        discretionary = client_data.expenses.discretionary_expenses
        
        st.markdown(f"""
        <div style="background: #1E293B; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; margin-top: 1rem;">
            <div style="font-size: 0.875rem; color: #F1F5F9; margin-bottom: 1rem; font-weight: 600;">Expense Split</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                <span style="color: #94A3B8;">Fixed/Essential</span>
                <span style="color: #3B82F6; font-weight: 600;">${fixed:,.0f}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #94A3B8;">Discretionary</span>
                <span style="color: #F59E0B; font-weight: 600;">${discretionary:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_portfolio_section(summary, client_data):
    """Render Portfolio Health section."""
    render_section_header(
        summary['section_title'],
        summary['section_question'],
        summary['overall_score'],
        summary['overall_status']
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Metrics grid
    render_metric_grid(summary['metrics'], columns=3)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Current Allocation")
        allocation = {
            'US Stocks': client_data.portfolio_allocation.us_stocks,
            'Int\'l Stocks': client_data.portfolio_allocation.international_stocks,
            'Bonds': client_data.portfolio_allocation.bonds,
            'Real Estate': client_data.portfolio_allocation.real_estate,
            'Commodities': client_data.portfolio_allocation.commodities,
            'Cash': client_data.portfolio_allocation.cash,
            'Alternatives': client_data.portfolio_allocation.alternatives,
            'Crypto': client_data.portfolio_allocation.crypto
        }
        allocation = {k: v for k, v in allocation.items() if v > 0}
        render_allocation_chart(allocation)
    
    with col2:
        st.markdown("### 📈 Portfolio Metrics")
        metrics = client_data.portfolio_metrics
        
        st.markdown(f"""
        <div style="background: #1E293B; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #334155;">
                <div>
                    <div style="font-size: 0.75rem; color: #94A3B8;">Expense Ratio</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: {'#10B981' if metrics.weighted_expense_ratio < 0.3 else '#F59E0B'};">
                        {metrics.weighted_expense_ratio:.2f}%
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #94A3B8;">Annual Turnover</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: {'#10B981' if metrics.annual_turnover < 30 else '#F59E0B'};">
                        {metrics.annual_turnover:.0f}%
                    </div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #334155;">
                <div>
                    <div style="font-size: 0.75rem; color: #94A3B8;">Tax Efficiency</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: {'#10B981' if metrics.tax_efficiency_score > 70 else '#F59E0B'};">
                        {metrics.tax_efficiency_score}/100
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #94A3B8;">Diversification</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: {'#10B981' if metrics.concentration_score > 70 else '#F59E0B'};">
                        {metrics.concentration_score}/100
                    </div>
                </div>
            </div>
            <div>
                <div style="font-size: 0.75rem; color: #94A3B8;">Trades (12 months)</div>
                <div style="font-size: 1.25rem; font-weight: 600; color: {'#10B981' if metrics.trades_last_12_months < 24 else '#F59E0B'};">
                    {metrics.trades_last_12_months}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Company stock exposure
        if client_data.assets.company_stock_total > 0:
            total_inv = client_data.assets.investment_assets + client_data.assets.company_stock_total
            company_pct = (client_data.assets.company_stock_total / total_inv * 100) if total_inv > 0 else 0
            
            st.markdown(f"""
            <div style="background: {'rgba(239, 68, 68, 0.1)' if company_pct > 20 else 'rgba(245, 158, 11, 0.1)'}; 
                        padding: 1rem; border-radius: 8px; margin-top: 1rem; 
                        border: 1px solid {'rgba(239, 68, 68, 0.3)' if company_pct > 20 else 'rgba(245, 158, 11, 0.3)'};">
                <div style="font-size: 0.875rem; color: #F1F5F9; font-weight: 600;">⚠️ Company Stock Exposure</div>
                <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.5rem;">
                    ${client_data.assets.company_stock_total:,.0f} ({company_pct:.1f}% of portfolio)
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_planning_section(summary, planning_calc, client_data):
    """Render Future Planning section."""
    render_section_header(
        summary['section_title'],
        summary['section_question'],
        summary['overall_score'],
        summary['overall_status']
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Retirement metrics
    col1, col2 = st.columns(2)
    
    with col1:
        if 'retirement_projection' in summary['metrics']:
            render_metric_card("Retirement Readiness", summary['metrics']['retirement_projection'], show_recommendations=True)
    
    with col2:
        if 'stress_test' in summary['metrics']:
            render_metric_card("Stress Test", summary['metrics']['stress_test'], show_recommendations=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Retirement projection chart
    retirement_assets = (
        client_data.assets.retirement_401k +
        client_data.assets.ira_traditional +
        client_data.assets.ira_roth +
        client_data.assets.brokerage_taxable * 0.8
    )
    
    # Calculate projected savings (simplified)
    years_to_ret = client_data.profile.retirement_age - client_data.profile.age
    annual_savings = client_data.income.total_annual_income * 0.15
    projected = retirement_assets * (1.06 ** years_to_ret) + annual_savings * ((1.06 ** years_to_ret - 1) / 0.06)
    
    target = client_data.expenses.total_monthly_expenses * 12 * 0.75 / 0.04  # 4% rule
    
    render_retirement_projection_chart(
        client_data.profile.age,
        client_data.profile.retirement_age,
        retirement_assets,
        projected,
        target
    )
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Goal progress
    st.markdown("### 🎯 Financial Goals")
    
    cols = st.columns(len(client_data.goals)) if len(client_data.goals) <= 3 else st.columns(3)
    
    for i, goal in enumerate(client_data.goals):
        col_idx = i % 3
        with cols[col_idx]:
            goal_key = f'goal_{goal.goal_id}'
            metric = summary['metrics'].get(goal_key)
            if metric:
                render_metric_card(goal.name, metric, show_recommendations=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Scenario analysis
    st.markdown("### 🔮 What-If Scenarios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Adjust Parameters")
        
        income_change = st.slider(
            "Income Change (%)",
            min_value=-30,
            max_value=50,
            value=0,
            step=5
        )
        
        expense_change = st.slider(
            "Expense Change (%)",
            min_value=-30,
            max_value=30,
            value=0,
            step=5
        )
        
        retirement_age_change = st.slider(
            "Retirement Age Change (years)",
            min_value=-5,
            max_value=10,
            value=0,
            step=1
        )
    
    with col2:
        st.markdown("#### Scenario Result")
        scenario = planning_calc.scenario_analysis(
            income_change_pct=income_change,
            expense_change_pct=expense_change,
            retirement_age_change=retirement_age_change
        )
        
        render_metric_card("Projected Outcome", scenario, show_recommendations=True)
        
        if scenario.trend:
            change_color = '#10B981' if scenario.trend > 0 else '#EF4444'
            st.markdown(f"""
            <div style="text-align: center; margin-top: 1rem; padding: 1rem; background: rgba({16 if scenario.trend > 0 else 239}, 
                        {185 if scenario.trend > 0 else 68}, {129 if scenario.trend > 0 else 68}, 0.1); 
                        border-radius: 8px;">
                <span style="font-size: 1.5rem; color: {change_color};">
                    {'+' if scenario.trend > 0 else ''}{scenario.trend:.1f}%
                </span>
                <div style="font-size: 0.75rem; color: #94A3B8;">vs Base Case</div>
            </div>
            """, unsafe_allow_html=True)


def render_estate_section(summary, client_data):
    """Render Estate Readiness section."""
    render_section_header(
        summary['section_title'],
        summary['section_question'],
        summary['overall_score'],
        summary['overall_status']
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Metrics grid
    render_metric_grid(summary['metrics'], columns=2)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Estate planning checklist
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Document Checklist")
        
        estate = client_data.estate
        documents = [
            ("Will", estate.has_will, "Essential for asset distribution"),
            ("Trust", estate.has_trust, "Recommended for estates > $1M"),
            ("Financial POA", estate.has_poa_financial, "Manages finances if incapacitated"),
            ("Healthcare POA", estate.has_poa_healthcare, "Makes medical decisions if unable"),
            ("Healthcare Directive", estate.has_healthcare_directive, "Specifies end-of-life wishes"),
            ("Digital Estate Plan", estate.digital_estate_documented, "Passwords, crypto, digital assets")
        ]
        
        for doc_name, has_doc, description in documents:
            icon = "✅" if has_doc else "❌"
            color = "#10B981" if has_doc else "#EF4444"
            bg_color = "rgba(16, 185, 129, 0.1)" if has_doc else "rgba(239, 68, 68, 0.1)"
            
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; 
                        background: {bg_color}; border-radius: 8px; margin-bottom: 0.5rem;">
                <span style="font-size: 1.25rem;">{icon}</span>
                <div>
                    <div style="font-size: 0.875rem; color: {color}; font-weight: 600;">{doc_name}</div>
                    <div style="font-size: 0.75rem; color: #94A3B8;">{description}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 👥 Beneficiary Status")
        
        if estate.beneficiaries_updated:
            status_icon = "✅"
            status_text = "Up to date"
            status_color = "#10B981"
        else:
            status_icon = "⚠️"
            status_text = "Review needed"
            status_color = "#F59E0B"
        
        last_review = estate.beneficiaries_last_reviewed
        review_text = last_review.strftime("%B %d, %Y") if last_review else "Never"
        
        st.markdown(f"""
        <div style="background: #1E293B; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">{status_icon}</span>
                <div>
                    <div style="font-size: 1rem; color: {status_color}; font-weight: 600;">{status_text}</div>
                    <div style="font-size: 0.75rem; color: #94A3B8;">Last reviewed: {review_text}</div>
                </div>
            </div>
            <div style="padding-top: 1rem; border-top: 1px solid #334155;">
                <div style="font-size: 0.75rem; color: #94A3B8; margin-bottom: 0.5rem;">Accounts to Review:</div>
                <div style="font-size: 0.8rem; color: #F1F5F9;">
        """, unsafe_allow_html=True)
        
        accounts = []
        if client_data.assets.retirement_401k > 0:
            accounts.append(f"• 401(k): ${client_data.assets.retirement_401k:,.0f}")
        if client_data.assets.ira_traditional > 0:
            accounts.append(f"• Traditional IRA: ${client_data.assets.ira_traditional:,.0f}")
        if client_data.assets.ira_roth > 0:
            accounts.append(f"• Roth IRA: ${client_data.assets.ira_roth:,.0f}")
        if client_data.insurance.life_insurance_coverage > 0:
            accounts.append(f"• Life Insurance: ${client_data.insurance.life_insurance_coverage:,.0f}")
        
        for acc in accounts:
            st.markdown(f"<div>{acc}</div>", unsafe_allow_html=True)
        
        st.markdown("</div></div></div>", unsafe_allow_html=True)
        
        # Will status
        if estate.has_will and estate.will_last_updated:
            years_old = (client_data.estate.will_last_updated.today() - estate.will_last_updated).days / 365
            
            if years_old > 5:
                will_status = "⚠️ Will may need review"
                will_color = "#F59E0B"
            elif years_old > 3:
                will_status = "📝 Consider reviewing will"
                will_color = "#3B82F6"
            else:
                will_status = "✅ Will recently updated"
                will_color = "#10B981"
            
            st.markdown(f"""
            <div style="background: rgba({245 if years_old > 3 else 16}, {158 if years_old > 3 else 185}, {11 if years_old > 3 else 129}, 0.1); 
                        padding: 1rem; border-radius: 8px; margin-top: 1rem; 
                        border: 1px solid rgba({245 if years_old > 3 else 16}, {158 if years_old > 3 else 185}, {11 if years_old > 3 else 129}, 0.3);">
                <div style="font-size: 0.875rem; color: {will_color}; font-weight: 600;">{will_status}</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 0.25rem;">
                    Last updated: {estate.will_last_updated.strftime("%B %Y")} ({years_old:.1f} years ago)
                </div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
