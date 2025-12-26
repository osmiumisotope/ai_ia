"""
Custom CSS styles for the Financial Advisor Dashboard.
Professional light theme with green and black accents.
"""

def get_custom_css() -> str:
    """Return custom CSS for the dashboard."""
    return """
    <style>
    /* ===== GLOBAL STYLES ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #FAF9F6;
        --bg-secondary: #F5F4F0;
        --bg-card: #FFFFFF;
        --bg-card-hover: #F5F4F0;
        --text-primary: #1E293B;
        --text-secondary: #475569;
        --text-muted: #64748B;
        --accent-green: #059669;
        --accent-green-light: #10B981;
        --accent-green-dark: #047857;
        --accent-gold: #D97706;
        --accent-gold-light: #F59E0B;
        --status-excellent: #059669;
        --status-good: #0284C7;
        --status-fair: #D97706;
        --status-poor: #EA580C;
        --status-critical: #DC2626;
        --border-color: #E2E8F0;
        --border-color-dark: #CBD5E1;
        --shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: var(--bg-primary) !important;
    }
    
    /* Hide the black header bar */
    header[data-testid="stHeader"] {
        background-color: var(--bg-primary) !important;
        border-bottom: none !important;
    }
    
    /* Force beige background on all main areas */
    .stApp > header + div {
        background-color: var(--bg-primary) !important;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: var(--bg-primary) !important;
    }
    
    [data-testid="stMain"] {
        background-color: var(--bg-primary) !important;
    }
    
    .main {
        background-color: var(--bg-primary) !important;
    }
    
    /* ===== HIDE STREAMLIT BRANDING ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background-color: var(--bg-primary) !important;}
    
    /* ===== MAIN CONTAINER ===== */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
        background-color: var(--bg-primary);
    }
    
    /* ===== HEADER STYLES ===== */
    .dashboard-header {
        background: #FFFFFF;
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-lg);
    }
    
    .dashboard-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent-green);
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .dashboard-subtitle {
        display: none;
    }
    
    .client-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(5, 150, 105, 0.1);
        color: var(--accent-green);
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-top: 1rem;
        border: 1px solid rgba(5, 150, 105, 0.2);
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
        border-color: var(--accent-green);
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
        background: var(--bg-card);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid var(--border-color);
        transition: all 0.2s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: var(--accent-green);
        box-shadow: var(--shadow-lg);
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
        background: rgba(5, 150, 105, 0.1);
        color: var(--status-excellent);
        border: 1px solid rgba(5, 150, 105, 0.3);
    }
    
    .status-good {
        background: rgba(2, 132, 199, 0.1);
        color: var(--status-good);
        border: 1px solid rgba(2, 132, 199, 0.3);
    }
    
    .status-fair {
        background: rgba(217, 119, 6, 0.1);
        color: var(--status-fair);
        border: 1px solid rgba(217, 119, 6, 0.3);
    }
    
    .status-poor {
        background: rgba(234, 88, 12, 0.1);
        color: var(--status-poor);
        border: 1px solid rgba(234, 88, 12, 0.3);
    }
    
    .status-critical {
        background: rgba(220, 38, 38, 0.1);
        color: var(--status-critical);
        border: 1px solid rgba(220, 38, 38, 0.3);
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
        background: rgba(5, 150, 105, 0.05);
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 3px solid var(--accent-green);
    }
    
    .recommendation-icon {
        color: var(--accent-green);
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
        background: linear-gradient(135deg, rgba(5, 150, 105, 0.08) 0%, rgba(217, 119, 6, 0.08) 100%);
        border: 1px solid rgba(5, 150, 105, 0.2);
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
        color: var(--accent-green);
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
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: var(--bg-secondary) !important;
    }
    
    [data-testid="stSidebarContent"] {
        background: var(--bg-secondary) !important;
    }
    
    [data-testid="stSidebar"] .block-container {
        padding: 1rem 0;
    }
    
    /* ===== SIDEBAR COLLAPSE BUTTON - ALWAYS VISIBLE ===== */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 0.75rem !important;
        left: 0.75rem !important;
        z-index: 999999 !important;
        background: var(--accent-green) !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        box-shadow: var(--shadow-lg) !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="collapsedControl"]:hover {
        background: var(--accent-green-dark) !important;
        transform: scale(1.05) !important;
    }
    
    [data-testid="collapsedControl"] svg {
        width: 20px !important;
        height: 20px !important;
        color: white !important;
        fill: white !important;
    }
    
    /* Sidebar expand/collapse button when sidebar is open */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
        background: rgba(5, 150, 105, 0.1) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(5, 150, 105, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]:hover {
        background: rgba(5, 150, 105, 0.15) !important;
        border-color: rgba(5, 150, 105, 0.3) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg {
        color: var(--accent-green) !important;
    }
    
    /* ===== NAVIGATION SECTION STYLES (Compact line-divided list) ===== */
    [data-testid="stSidebar"] .stButton {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    [data-testid="stSidebar"] button {
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        border-bottom: 1px solid var(--border-color) !important;
        border-radius: 0 !important;
        padding: 0.75rem 1rem !important;
        margin: 0 !important;
        text-align: left !important;
        font-weight: 500 !important;
        color: var(--text-primary) !important;
        font-size: 0.875rem !important;
        transition: all 0.15s ease !important;
        box-shadow: none !important;
        min-height: unset !important;
        height: auto !important;
        line-height: 1.4 !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background: rgba(5, 150, 105, 0.08) !important;
        color: var(--accent-green) !important;
    }
    
    [data-testid="stSidebar"] button[kind="primary"] {
        background: rgba(5, 150, 105, 0.1) !important;
        color: var(--accent-green) !important;
        font-weight: 600 !important;
        border-left: 3px solid var(--accent-green) !important;
    }
    
    [data-testid="stSidebar"] button[kind="primary"]:hover {
        background: rgba(5, 150, 105, 0.15) !important;
    }
    
    [data-testid="stSidebar"] button p {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.4 !important;
    }
    
    /* Remove extra spacing between button containers */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        gap: 0 !important;
    }
    
    [data-testid="stSidebar"] .element-container {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* ===== TABS STYLING ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--bg-secondary);
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--accent-green) !important;
        color: white !important;
    }
    
    /* ===== EXPANDER STYLES ===== */
    .streamlit-expanderHeader {
        background: var(--bg-secondary);
        border-radius: 8px;
        font-weight: 500;
        color: var(--text-primary);
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
        background: var(--bg-card);
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
        color: white;
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
        background: var(--bg-card) !important;
        border-color: var(--border-color) !important;
        color: var(--text-primary) !important;
    }
    
    /* Selectbox dropdown menu */
    [data-baseweb="select"] > div {
        background-color: var(--bg-card) !important;
        border-color: var(--border-color) !important;
    }
    
    [data-baseweb="popover"] {
        background-color: var(--bg-card) !important;
    }
    
    [data-baseweb="popover"] > div {
        background-color: var(--bg-card) !important;
    }
    
    /* Dropdown menu list */
    [data-baseweb="menu"] {
        background-color: var(--bg-card) !important;
    }
    
    [data-baseweb="menu"] li {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    
    [data-baseweb="menu"] li:hover {
        background-color: var(--bg-secondary) !important;
    }
    
    /* Selected option in dropdown */
    [data-baseweb="menu"] [aria-selected="true"] {
        background-color: rgba(5, 150, 105, 0.1) !important;
    }
    
    /* Selectbox text */
    [data-baseweb="select"] span {
        color: var(--text-primary) !important;
    }
    
    /* Selectbox icon */
    [data-baseweb="select"] svg {
        fill: var(--text-secondary) !important;
    }
    
    /* ===== TEXT COLORS FOR LIGHT THEME ===== */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
    }
    
    p, span, div {
        color: var(--text-primary);
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
        "excellent": "#059669",
        "good": "#0284C7",
        "fair": "#D97706",
        "poor": "#EA580C",
        "critical": "#DC2626"
    }
    return colors.get(status.lower(), "#64748B")


def get_status_class(status: str) -> str:
    """Get CSS class for a health status."""
    return f"status-{status.lower()}"
