"""
Components module initialization.
"""

from .styles import get_custom_css, get_status_color, get_status_class
from .ui_components import (
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
    render_health_score_gauge,
    render_section_container_start,
    render_section_container_end
)

__all__ = [
    'get_custom_css',
    'get_status_color',
    'get_status_class',
    'render_header',
    'render_net_worth_summary',
    'render_section_header',
    'render_metric_card',
    'render_metric_grid',
    'render_allocation_chart',
    'render_goal_progress',
    'render_expense_breakdown',
    'render_retirement_projection_chart',
    'render_asset_breakdown_chart',
    'render_health_score_gauge',
    'render_section_container_start',
    'render_section_container_end'
]
