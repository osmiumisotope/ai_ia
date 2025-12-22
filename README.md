# Financial Advisor Dashboard

A comprehensive financial health dashboard built with Streamlit, designed for financial advisors and DIY investors.

## Features

### 5 Key Sections

1. **Financial Foundation & Safety Net** - Emergency funds, liquid net worth, insurance coverage, debt-to-income ratio
2. **Cash Flow & Spending Behavior** - Savings rate, fixed costs, discretionary spending, lifestyle creep tracking
3. **Investment & Portfolio Health** - Allocation appropriateness, concentration risk, expense ratios, tax efficiency
4. **Future Planning & Projections** - Retirement projections, stress testing, goal tracking, scenario analysis
5. **Legacy & Estate Readiness** - Estate planning checklist, beneficiary status, digital estate

## Project Structure

```
LLM Advisor/
├── app.py                    # Main Streamlit application
├── .streamlit/
│   └── config.toml          # Streamlit theme configuration
├── logic/                    # Pure Python business logic (framework-agnostic)
│   ├── __init__.py
│   ├── models.py            # Data models and type definitions
│   ├── foundation.py        # Financial foundation calculations
│   ├── cashflow.py          # Cash flow & spending calculations
│   ├── portfolio.py         # Portfolio health calculations
│   ├── planning.py          # Future planning calculations
│   └── estate.py            # Estate readiness calculations
├── components/               # UI rendering components
│   ├── __init__.py
│   ├── styles.py            # Custom CSS styles
│   └── ui_components.py     # Reusable UI components
├── data/                     # Data layer
│   ├── __init__.py
│   └── sample_clients.py    # Sample client data
└── requirements.txt
```

## Architecture

The project is designed with a **clean separation of concerns**:

- **Logic Layer** (`logic/`): Pure Python calculations with no UI dependencies. Can be easily ported to any frontend (React, Vue, etc.)
- **Components Layer** (`components/`): Streamlit-specific UI rendering
- **Data Layer** (`data/`): Sample data and data access

This architecture makes it straightforward to:
1. Build a React frontend using the same logic
2. Create an API layer on top of the logic
3. Test business logic independently of UI

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the dashboard:
```bash
streamlit run app.py
```

## Sample Clients

The dashboard includes 3 sample clients with different financial profiles:

1. **Sarah Chen** - High-earning tech professional (age 38)
2. **Marcus Williams** - Mid-career professional (age 45)  
3. **Jennifer & David Park** - Pre-retirees (age 58)

## Customization

### Adding New Metrics

1. Add the calculation method to the appropriate logic class (e.g., `logic/foundation.py`)
2. Update the `get_section_summary()` method to include the new metric
3. The UI will automatically render it

### Adding New Sections

1. Create a new calculator class in `logic/`
2. Add UI rendering function in `app.py`
3. Update navigation in the sidebar

### Styling

Custom styles are defined in `components/styles.py`. The theme uses:
- Dark background (#0F172A)
- Teal accent (#10B981)
- Gold secondary (#F59E0B)
- Clean typography with Inter font

## Future Development

- [ ] Connect to real data sources (Plaid, Yodlee)
- [ ] Add user authentication
- [ ] Implement data persistence
- [ ] Create React frontend
- [ ] Add PDF report generation
- [ ] Monte Carlo simulation engine
- [ ] Tax optimization recommendations

## License

MIT License
