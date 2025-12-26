"""
Reusable UI components for the Financial Advisor Dashboard.
These components render metrics and data using Streamlit.
"""

import streamlit as st
from typing import List, Optional, Dict, Any
import plotly.graph_objects as go

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.models import MetricResult, HealthStatus, ClientData
from components.styles import get_status_color, get_status_class


def render_header(client_name: str, client_id: str):
    """Render the dashboard header."""
    st.markdown(f"""
    <div class="dashboard-header">
        <h1 class="dashboard-title">Financial Health Dashboard</h1>
        <p class="dashboard-subtitle">Comprehensive financial wellness analysis and insights</p>
        <div class="client-badge">
            <span>{client_name}</span>
            <span style="opacity: 0.7">({client_id})</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_net_worth_summary(client_data: ClientData):
    """Render the net worth summary card."""
    net_worth = client_data.net_worth
    liquid_nw = client_data.liquid_net_worth
    total_assets = client_data.assets.total_assets
    total_liabilities = client_data.liabilities.total_liabilities
    
    st.markdown(f"""
    <div class="networth-card animate-fade-in">
        <div class="networth-label">Total Net Worth</div>
        <div class="networth-value">${net_worth:,.0f}</div>
        <div class="networth-breakdown">
            <div class="breakdown-item">
                <div class="breakdown-value" style="color: #059669;">${total_assets:,.0f}</div>
                <div class="breakdown-label">Total Assets</div>
            </div>
            <div class="breakdown-item">
                <div class="breakdown-value" style="color: #DC2626;">${total_liabilities:,.0f}</div>
                <div class="breakdown-label">Total Liabilities</div>
            </div>
            <div class="breakdown-item">
                <div class="breakdown-value" style="color: #0284C7;">${liquid_nw:,.0f}</div>
                <div class="breakdown-label">Liquid Net Worth</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str, question: str, score: float, status: HealthStatus):
    """Render a section header with score."""
    status_class = get_status_class(status.value)
    status_color = get_status_color(status.value)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"""
        <div style="margin-bottom: 0.5rem;">
            <h2 style="font-size: 1.25rem; font-weight: 600; color: #1E293B; margin: 0;">{title}</h2>
            <p style="font-size: 0.875rem; color: #475569; font-style: italic; margin-top: 0.25rem;">"{question}"</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="score-ring-container">
            <div class="score-ring" style="background: conic-gradient({status_color} {score * 3.6}deg, #E2E8F0 0deg);">
                <div style="background: #FFFFFF; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #1E293B; border: 1px solid #E2E8F0;">
                    {score:.0f}
                </div>
            </div>
            <span class="score-label">Section Score</span>
        </div>
        """, unsafe_allow_html=True)


def render_metric_card(label: str, metric: MetricResult, show_recommendations: bool = False):
    """Render a single metric card."""
    status_class = get_status_class(metric.status.value)
    status_color = get_status_color(metric.status.value)
    
    # Progress calculation for visual indicator
    if metric.benchmark and metric.benchmark > 0:
        if metric.status in [HealthStatus.EXCELLENT, HealthStatus.GOOD]:
            progress = min(100, (metric.value / metric.benchmark) * 100)
        else:
            progress = min(100, max(0, (metric.value / metric.benchmark) * 100))
    else:
        progress = 50  # Default if no benchmark
    
    # Build delta HTML if available
    delta_html = ""
    if metric.delta is not None and metric.delta_is_positive is not None:
        arrow = "↑" if metric.delta_is_positive else "↓"
        arrow_color = "#059669" if metric.delta_is_positive else "#DC2626"
        # Format delta based on the metric type (percentage vs absolute)
        if '%' in metric.display_value:
            delta_display = f"{metric.delta:.1f}%"
        elif '$' in metric.display_value:
            delta_display = f"${metric.delta:,.0f}"
        else:
            delta_display = f"{metric.delta:.1f}"
        delta_html = f'<span style="font-size: 0.875rem; color: {arrow_color}; margin-left: 0.5rem; font-weight: 500;">{arrow} {delta_display}</span>'
    
    html = f"""
    <div class="metric-card animate-fade-in">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div class="metric-label">{label}</div>
            <span class="status-badge {status_class}">{metric.status.value}</span>
        </div>
        <div class="metric-value" style="display: flex; align-items: baseline;">{metric.display_value}{delta_html}</div>
        {f'<div class="metric-description">{metric.description}</div>' if metric.description else ''}
        <div class="progress-container">
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: {progress}%; background: {status_color};"></div>
            </div>
        </div>
        {f'<div class="metric-benchmark">{metric.benchmark_label}</div>' if metric.benchmark_label else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
    if show_recommendations and metric.recommendations:
        with st.expander("💡 Recommendations", expanded=False):
            for rec in metric.recommendations:
                st.markdown(f"""
                <div class="recommendation-item">
                    <span class="recommendation-icon">→</span>
                    <span class="recommendation-text">{rec}</span>
                </div>
                """, unsafe_allow_html=True)


def render_metric_grid(metrics: Dict[str, MetricResult], columns: int = 3):
    """Render metrics in a grid layout."""
    metric_items = list(metrics.items())
    
    for i in range(0, len(metric_items), columns):
        cols = st.columns(columns)
        for j, col in enumerate(cols):
            if i + j < len(metric_items):
                key, metric = metric_items[i + j]
                with col:
                    # Convert key to readable label
                    label = key.replace("_", " ").title()
                    render_metric_card(label, metric, show_recommendations=True)


def render_allocation_chart(allocation: Dict[str, float], title: str = "Portfolio Allocation"):
    """Render a portfolio allocation donut chart."""
    labels = list(allocation.keys())
    values = list(allocation.values())
    
    # Custom colors for categories - vibrant for light theme
    colors = [
        '#059669',  # US Stocks - Green
        '#0284C7',  # International Stocks - Blue
        '#7C3AED',  # Bonds - Purple
        '#D97706',  # Real Estate - Gold
        '#DB2777',  # Commodities - Pink
        '#64748B',  # Cash - Gray
        '#0D9488',  # Alternatives - Teal
        '#EA580C',  # Crypto - Orange
    ]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker_colors=colors[:len(labels)],
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=12, color='#1E293B'),
        hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='#1E293B'),
            x=0.5
        ),
        showlegend=False,
        paper_bgcolor='rgba(255,255,255,0)',
        plot_bgcolor='rgba(255,255,255,0)',
        margin=dict(t=50, b=20, l=20, r=20),
        height=350,
        annotations=[dict(
            text='Allocation',
            x=0.5, y=0.5,
            font=dict(size=14, color='#475569'),
            showarrow=False
        )]
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_goal_progress(goals: List[Dict], title: str = ""):
    """Render goal progress cards."""
    if title:
        st.markdown(f"""
        <div style="margin-bottom: 0.75rem;">
            <h3 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0;">{title}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    for goal in goals:
        progress = (goal['current'] / goal['target']) * 100 if goal['target'] > 0 else 0
        status_color = get_status_color(goal.get('status', 'fair'))
        
        st.markdown(f"""
        <div class="goal-card">
            <div class="goal-header">
                <span class="goal-name">{goal['name']}</span>
                <span class="goal-priority">Priority {goal.get('priority', '-')}</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar-bg" style="height: 8px;">
                    <div class="progress-bar-fill" style="width: {min(100, progress)}%; background: {status_color};"></div>
                </div>
            </div>
            <div class="goal-amounts">
                <span>${goal['current']:,.0f} saved</span>
                <span>{progress:.0f}% of ${goal['target']:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_expense_breakdown(expenses: Dict[str, float], income: float):
    """Render expense breakdown chart."""
    # Sort by value descending
    sorted_expenses = dict(sorted(expenses.items(), key=lambda x: x[1], reverse=True))
    
    fig = go.Figure()
    
    # Create horizontal bar chart
    fig.add_trace(go.Bar(
        y=list(sorted_expenses.keys()),
        x=list(sorted_expenses.values()),
        orientation='h',
        marker_color='#059669',
        text=[f'${v:,.0f}' for v in sorted_expenses.values()],
        textposition='outside',
        textfont=dict(color='#1E293B', size=11),
        hovertemplate='<b>%{y}</b><br>$%{x:,.0f}<br>%{customdata:.1f}% of income<extra></extra>',
        customdata=[v/income*100 for v in sorted_expenses.values()]
    ))
    
    fig.update_layout(
        title=dict(
            text='Monthly Expense Breakdown',
            font=dict(size=16, color='#1E293B'),
            x=0
        ),
        xaxis=dict(
            title='Amount ($)',
            title_font=dict(color='#475569'),
            tickfont=dict(color='#475569'),
            gridcolor='#E2E8F0',
            showgrid=True
        ),
        yaxis=dict(
            tickfont=dict(color='#1E293B', size=11),
            autorange='reversed'
        ),
        paper_bgcolor='rgba(255,255,255,0)',
        plot_bgcolor='rgba(255,255,255,0)',
        margin=dict(t=50, b=40, l=120, r=80),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_retirement_projection_chart(
    current_age: int,
    retirement_age: int,
    current_savings: float,
    projected_savings: float,
    target_amount: float
):
    """Render retirement projection chart."""
    years = list(range(current_age, retirement_age + 10))
    years_to_retirement = retirement_age - current_age
    
    # Simplified growth calculation
    growth_rate = 0.06  # Real return after inflation
    projected_values = []
    
    for i, year in enumerate(years):
        if i <= years_to_retirement:
            # Accumulation phase
            growth_factor = (1 + growth_rate) ** i
            projected_values.append(current_savings * growth_factor + 
                                   (projected_savings - current_savings) * (i / years_to_retirement) if years_to_retirement > 0 else current_savings)
        else:
            # Withdrawal phase (simplified)
            years_in_retirement = i - years_to_retirement
            projected_values.append(projected_savings * (1 - 0.04 * years_in_retirement))
    
    fig = go.Figure()
    
    # Projected savings line
    fig.add_trace(go.Scatter(
        x=years,
        y=projected_values,
        mode='lines',
        name='Projected Savings',
        line=dict(color='#059669', width=3),
        fill='tozeroy',
        fillcolor='rgba(5, 150, 105, 0.1)'
    ))
    
    # Target line
    fig.add_trace(go.Scatter(
        x=[years[0], years[-1]],
        y=[target_amount, target_amount],
        mode='lines',
        name='Target',
        line=dict(color='#D97706', width=2, dash='dash')
    ))
    
    # Retirement marker
    fig.add_vline(
        x=retirement_age,
        line=dict(color='#DC2626', width=2, dash='dot'),
        annotation_text='Retirement',
        annotation_position='top'
    )
    
    fig.update_layout(
        title=dict(
            text='Retirement Projection',
            font=dict(size=16, color='#1E293B'),
            x=0
        ),
        xaxis=dict(
            title='Age',
            title_font=dict(color='#475569'),
            tickfont=dict(color='#475569'),
            gridcolor='#E2E8F0'
        ),
        yaxis=dict(
            title='Portfolio Value ($)',
            title_font=dict(color='#475569'),
            tickfont=dict(color='#475569'),
            gridcolor='#E2E8F0',
            tickformat='$,.0f'
        ),
        paper_bgcolor='rgba(255,255,255,0)',
        plot_bgcolor='rgba(255,255,255,0)',
        legend=dict(
            font=dict(color='#1E293B'),
            bgcolor='rgba(255,255,255,0)'
        ),
        margin=dict(t=50, b=40, l=80, r=40),
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_asset_breakdown_chart(assets: Dict[str, float], title: str = "Asset Breakdown"):
    """Render asset/liability breakdown as a pie chart."""
    # Prepare data
    categories = list(assets.keys())
    values = list(assets.values())
    
    # Filter out zero values
    data = [(c, v) for c, v in zip(categories, values) if v > 0]
    if not data:
        st.info("No data to display")
        return
    
    categories, values = zip(*data)
    
    # Custom colors for categories - vibrant for light theme
    colors = [
        '#059669',  # Green
        '#0284C7',  # Blue
        '#7C3AED',  # Purple
        '#D97706',  # Gold
        '#DB2777',  # Pink
        '#0D9488',  # Teal
        '#EA580C',  # Orange
        '#4F46E5',  # Indigo
        '#65A30D',  # Lime
        '#DC2626',  # Red
    ]
    
    # Calculate total for percentage display
    total = sum(values)
    
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=values,
        hole=0.5,
        marker_colors=colors[:len(categories)],
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=11, color='#1E293B'),
        hovertemplate='<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='#1E293B'),
            x=0.5
        ),
        showlegend=False,
        paper_bgcolor='rgba(255,255,255,0)',
        plot_bgcolor='rgba(255,255,255,0)',
        margin=dict(t=50, b=20, l=20, r=20),
        height=400,
        annotations=[dict(
            text=f'${total:,.0f}',
            x=0.5, y=0.5,
            font=dict(size=16, color='#1E293B', weight=600),
            showarrow=False
        )]
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_health_score_gauge(score: float, label: str = "Overall Financial Health"):
    """Render a gauge chart for overall health score."""
    if score >= 85:
        color = '#059669'
    elif score >= 65:
        color = '#0284C7'
    elif score >= 45:
        color = '#D97706'
    elif score >= 25:
        color = '#EA580C'
    else:
        color = '#DC2626'
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': label, 'font': {'size': 16, 'color': '#1E293B'}},
        number={'font': {'size': 40, 'color': '#1E293B'}},
        gauge={
            'axis': {'range': [0, 100], 'tickfont': {'color': '#475569'}},
            'bar': {'color': color},
            'bgcolor': '#E2E8F0',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 25], 'color': 'rgba(220, 38, 38, 0.15)'},
                {'range': [25, 45], 'color': 'rgba(234, 88, 12, 0.15)'},
                {'range': [45, 65], 'color': 'rgba(217, 119, 6, 0.15)'},
                {'range': [65, 85], 'color': 'rgba(2, 132, 199, 0.15)'},
                {'range': [85, 100], 'color': 'rgba(5, 150, 105, 0.15)'}
            ]
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(255,255,255,0)',
        plot_bgcolor='rgba(255,255,255,0)',
        margin=dict(t=80, b=40, l=40, r=40),
        height=280
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_section_container_start(section_id: str):
    """Start a section container div."""
    st.markdown(f'<div class="section-container" id="{section_id}">', unsafe_allow_html=True)


def render_section_container_end():
    """End a section container div."""
    st.markdown('</div>', unsafe_allow_html=True)
