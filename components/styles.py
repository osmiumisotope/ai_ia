"""
Custom CSS styles for the Financial Advisor Dashboard.
Professional dark theme with teal and gold accents.
"""

def get_custom_css() -> str:
    """Return custom CSS for the dashboard."""
    return """
    <style>
    /* ===== GLOBAL STYLES ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #0F172A;
        --bg-secondary: #1E293B;
        --bg-card: #1E293B;
        --bg-card-hover: #334155;
        --text-primary: #F1F5F9;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --accent-teal: #10B981;
        --accent-teal-light: #34D399;
        --accent-gold: #F59E0B;
        --accent-gold-light: #FBBF24;
        --status-excellent: #10B981;
        --status-good: #3B82F6;
        --status-fair: #F59E0B;
        --status-poor: #F97316;
        --status-critical: #EF4444;
        --border-color: #334155;
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }
    
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ===== HIDE STREAMLIT BRANDING ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ===== MAIN CONTAINER ===== */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* ===== HEADER STYLES ===== */
    .dashboard-header {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, #0F172A 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-lg);
    }
    
    .dashboard-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .dashboard-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        margin-top: 0.5rem;
    }
    
    .client-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: var(--accent-teal);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-top: 1rem;
    }
    
    /* ===== SECTION STYLES ===== */
    .section-container {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow);
        transition: all 0.2s ease;
    }
    
    .section-container:hover {
        border-color: var(--accent-teal);
        box-shadow: var(--shadow-lg);
    }
    
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }
    
    .section-question {
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-style: italic;
        margin-top: 0.25rem;
    }
    
    /* ===== METRIC CARD STYLES ===== */
    .metric-card {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, rgba(30, 41, 59, 0.8) 100%);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid var(--border-color);
        transition: all 0.2s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: var(--accent-teal);
        box-shadow: var(--shadow);
    }
    
    .metric-label {
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
    }
    
    .metric-description {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 0.5rem;
    }
    
    .metric-benchmark {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid var(--border-color);
    }
    
    /* ===== STATUS INDICATORS ===== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .status-excellent {
        background: rgba(16, 185, 129, 0.15);
        color: var(--status-excellent);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .status-good {
        background: rgba(59, 130, 246, 0.15);
        color: var(--status-good);
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    
    .status-fair {
        background: rgba(245, 158, 11, 0.15);
        color: var(--status-fair);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .status-poor {
        background: rgba(249, 115, 22, 0.15);
        color: var(--status-poor);
        border: 1px solid rgba(249, 115, 22, 0.3);
    }
    
    .status-critical {
        background: rgba(239, 68, 68, 0.15);
        color: var(--status-critical);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* ===== SCORE RING ===== */
    .score-ring-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }
    
    .score-ring {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary);
        position: relative;
    }
    
    .score-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-align: center;
    }
    
    /* ===== PROGRESS BARS ===== */
    .progress-container {
        margin-top: 0.75rem;
    }
    
    .progress-bar-bg {
        height: 6px;
        background: var(--border-color);
        border-radius: 3px;
        overflow: hidden;
    }
    
    .progress-bar-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.5s ease;
    }
    
    /* ===== RECOMMENDATION CARDS ===== */
    .recommendation-item {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.75rem;
        background: rgba(16, 185, 129, 0.05);
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 3px solid var(--accent-teal);
    }
    
    .recommendation-icon {
        color: var(--accent-teal);
        font-size: 1rem;
        flex-shrink: 0;
    }
    
    .recommendation-text {
        font-size: 0.875rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    /* ===== NET WORTH SUMMARY ===== */
    .networth-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .networth-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .networth-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--accent-teal);
        margin: 0.5rem 0;
    }
    
    .networth-breakdown {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border-color);
    }
    
    .breakdown-item {
        text-align: center;
    }
    
    .breakdown-value {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .breakdown-label {
        font-size: 0.75rem;
        color: var(--text-muted);
    }
    
    /* ===== SIDEBAR STYLES ===== */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: var(--bg-secondary);
    }
    
    [data-testid="stSidebar"] .block-container {
        padding: 2rem 1rem;
    }
    
    /* ===== NAVIGATION BUTTON STYLES ===== */
    [data-testid="stSidebar"] button {
        width: 100%;
        background: linear-gradient(135deg, #1E293B 0%, rgba(30, 41, 59, 0.9) 100%) !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 0.875rem 1rem !important;
        margin-bottom: 0.5rem !important;
        text-align: left !important;
        font-weight: 500 !important;
        color: #E2E8F0 !important;
        font-size: 0.875rem !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #334155 0%, rgba(51, 65, 85, 0.9) 100%) !important;
        border-color: #475569 !important;
        transform: translateX(4px);
    }
    
    [data-testid="stSidebar"] button[kind="primary"] {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.08) 100%) !important;
        border-color: rgba(16, 185, 129, 0.4) !important;
        color: #10B981 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] button[kind="primary"]:hover {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(16, 185, 129, 0.1) 100%) !important;
        border-color: rgba(16, 185, 129, 0.5) !important;
    }
    
    [data-testid="stSidebar"] button p {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* ===== TABS STYLING ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--bg-secondary);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--accent-teal) !important;
        color: white !important;
    }
    
    /* ===== EXPANDER STYLES ===== */
    .streamlit-expanderHeader {
        background: var(--bg-secondary);
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* ===== CHART CONTAINERS ===== */
    .chart-container {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid var(--border-color);
    }
    
    /* ===== GOAL CARDS ===== */
    .goal-card {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid var(--border-color);
        margin-bottom: 1rem;
    }
    
    .goal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .goal-name {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .goal-priority {
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
        background: var(--accent-gold);
        color: var(--bg-primary);
        border-radius: 4px;
        font-weight: 600;
    }
    
    .goal-amounts {
        display: flex;
        justify-content: space-between;
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin-top: 0.5rem;
    }
    
    /* ===== CUSTOM SELECTBOX ===== */
    .stSelectbox > div > div {
        background: var(--bg-secondary);
        border-color: var(--border-color);
    }
    
    /* ===== ANIMATIONS ===== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* ===== RESPONSIVE ADJUSTMENTS ===== */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .dashboard-title {
            font-size: 1.5rem;
        }
        
        .metric-value {
            font-size: 1.25rem;
        }
        
        .networth-value {
            font-size: 1.75rem;
        }
    }
    </style>
    """


def get_status_color(status: str) -> str:
    """Get color for a health status."""
    colors = {
        "excellent": "#10B981",
        "good": "#3B82F6",
        "fair": "#F59E0B",
        "poor": "#F97316",
        "critical": "#EF4444"
    }
    return colors.get(status.lower(), "#94A3B8")


def get_status_class(status: str) -> str:
    """Get CSS class for a health status."""
    return f"status-{status.lower()}"
