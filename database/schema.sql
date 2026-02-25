-- LLM Advisor Database Schema
-- SQLite DDL Statements

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- ============================================
-- CLIENTS TABLE
-- Core table for storing client information
-- ============================================
CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    gender_at_birth TEXT CHECK(gender_at_birth IN ('male', 'female')) NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT TRUE,
    primary_uuid TEXT REFERENCES clients(id),
    retirement_age INTEGER,
    risk_tolerance TEXT CHECK(risk_tolerance IN ('low', 'moderate', 'high', 'critical')),
    marital_status TEXT,
    state TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- ACCOUNT TYPES TABLE
-- Reference table for account classifications
-- ============================================
CREATE TABLE IF NOT EXISTS account_types (
    account_type_name TEXT PRIMARY KEY,
    tax_advantaged BOOLEAN NOT NULL DEFAULT FALSE,
    is_roth BOOLEAN NOT NULL DEFAULT FALSE,
    is_liquid BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT
);

-- ============================================
-- ACCOUNTS TABLE
-- Financial accounts held by clients
-- ============================================
CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    account_name TEXT NOT NULL,
    account_type_name TEXT NOT NULL REFERENCES account_types(account_type_name),
    institution TEXT,
    account_number_masked TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- ACCOUNT OWNERS TABLE
-- Links clients to accounts with ownership type
-- ============================================
CREATE TABLE IF NOT EXISTS account_owners (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    account_id TEXT NOT NULL REFERENCES accounts(id),
    ownership_type TEXT CHECK(ownership_type IN ('sole', 'joint', 'beneficiary', 'custodian')) NOT NULL DEFAULT 'sole'
);

-- ============================================
-- SECURITIES TABLE
-- Investment securities reference data
-- ============================================
CREATE TABLE IF NOT EXISTS securities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    security_type TEXT CHECK(security_type IN ('stock', 'etf', 'mutual_fund', 'bond', 'cash', 'crypto', 'real_estate', 'other')) NOT NULL,
    expense_ratio REAL
);

-- ============================================
-- HOLDINGS TABLE
-- Current positions in accounts
-- ============================================
CREATE TABLE IF NOT EXISTS holdings (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL REFERENCES accounts(id),
    security_id TEXT NOT NULL REFERENCES securities(id),
    quantity REAL NOT NULL,
    cost_basis REAL,
    as_of_date DATE NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TRANSACTIONS TABLE
-- Financial transactions history
-- ============================================
CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    account_id TEXT REFERENCES accounts(id),
    date DATE NOT NULL,
    type TEXT NOT NULL,
    amount REAL NOT NULL,
    direction TEXT CHECK(direction IN ('debit', 'credit')) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- LIABILITIES TABLE
-- Client debts and loans
-- ============================================
CREATE TABLE IF NOT EXISTS liabilities (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    liability_type TEXT CHECK(liability_type IN ('mortgage_primary', 'mortgage_investment', 'auto_loan', 'student_loan', 'credit_card', 'personal_loan', 'heloc', 'other')) NOT NULL,
    description TEXT,
    balance REAL NOT NULL,
    interest_rate REAL,
    minimum_payment REAL,
    as_of_date DATE NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INCOME TABLE
-- Client income sources
-- ============================================
CREATE TABLE IF NOT EXISTS income (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    income_type TEXT CHECK(income_type IN ('salary', 'bonus', 'rental', 'investment', 'other')) NOT NULL,
    amount REAL NOT NULL,
    frequency TEXT CHECK(frequency IN ('annual', 'monthly', 'one_time')) NOT NULL DEFAULT 'annual',
    effective_date DATE NOT NULL,
    end_date DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INSURANCE COVERAGE TABLE
-- Client insurance policies
-- ============================================
CREATE TABLE IF NOT EXISTS insurance_coverage (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    effective_date DATE NOT NULL,
    life_insurance_coverage REAL DEFAULT 0,
    life_insurance_type TEXT CHECK(life_insurance_type IN ('term', 'whole', 'universal')),
    disability_coverage_monthly REAL DEFAULT 0,
    disability_coverage_type TEXT CHECK(disability_coverage_type IN ('short_term', 'long_term', 'both')),
    umbrella_coverage REAL DEFAULT 0,
    long_term_care BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- PORTFOLIO METRICS TABLE
-- Calculated portfolio statistics
-- ============================================
CREATE TABLE IF NOT EXISTS portfolio_metrics (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    snapshot_date DATE NOT NULL,
    weighted_expense_ratio REAL,
    annual_turnover REAL,
    tax_efficiency_score INTEGER,
    concentration_score INTEGER,
    trades_last_12_months INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- GOALS TABLE
-- Financial goals for clients
-- ============================================
CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    name TEXT NOT NULL,
    target_amount REAL NOT NULL,
    target_date DATE NOT NULL,
    priority INTEGER CHECK(priority BETWEEN 1 AND 5),
    monthly_contribution REAL DEFAULT 0,
    status TEXT CHECK(status IN ('active', 'completed', 'paused')) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- GOAL ACCOUNT ALLOCATIONS TABLE
-- Links goals to accounts with allocation percentages
-- ============================================
CREATE TABLE IF NOT EXISTS goal_account_allocations (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL REFERENCES goals(id),
    account_id TEXT NOT NULL REFERENCES accounts(id),
    allocation_percentage REAL NOT NULL CHECK(allocation_percentage BETWEEN 0 AND 100)
);

-- ============================================
-- ESTATE PLANNING TABLE
-- Estate planning status for clients
-- ============================================
CREATE TABLE IF NOT EXISTS estate_planning (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    has_will BOOLEAN DEFAULT FALSE,
    will_last_updated DATE,
    has_trust BOOLEAN DEFAULT FALSE,
    has_poa_financial BOOLEAN DEFAULT FALSE,
    has_poa_healthcare BOOLEAN DEFAULT FALSE,
    has_healthcare_directive BOOLEAN DEFAULT FALSE,
    beneficiaries_updated BOOLEAN DEFAULT FALSE,
    beneficiaries_last_reviewed DATE,
    digital_estate_documented BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- DOCUMENTS TABLE
-- Document storage metadata
-- ============================================
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    document_type TEXT CHECK(document_type IN ('will', 'trust', 'poa', 'statement', 'tax_return', 'insurance_policy', 'disability_insurance', 'other')) NOT NULL,
    file_name TEXT NOT NULL,
    file_hash TEXT,
    storage_path TEXT,
    file_content BLOB,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by TEXT
);

-- ============================================
-- DEPENDENTS TABLE
-- Client dependents (children, elderly parents, etc.)
-- ============================================
CREATE TABLE IF NOT EXISTS dependents (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL REFERENCES clients(id),
    name TEXT NOT NULL,
    relationship TEXT CHECK(relationship IN ('child', 'spouse', 'parent', 'sibling', 'other')) NOT NULL,
    date_of_birth DATE,
    is_financially_dependent BOOLEAN DEFAULT TRUE,
    special_needs BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX IF NOT EXISTS idx_clients_primary_uuid ON clients(primary_uuid);
CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(account_type_name);
CREATE INDEX IF NOT EXISTS idx_account_owners_client ON account_owners(client_id);
CREATE INDEX IF NOT EXISTS idx_account_owners_account ON account_owners(account_id);
CREATE INDEX IF NOT EXISTS idx_holdings_account ON holdings(account_id);
CREATE INDEX IF NOT EXISTS idx_holdings_security ON holdings(security_id);
CREATE INDEX IF NOT EXISTS idx_transactions_client ON transactions(client_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_liabilities_client ON liabilities(client_id);
CREATE INDEX IF NOT EXISTS idx_income_client ON income(client_id);
CREATE INDEX IF NOT EXISTS idx_insurance_client ON insurance_coverage(client_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_metrics_client ON portfolio_metrics(client_id);
CREATE INDEX IF NOT EXISTS idx_goals_client ON goals(client_id);
CREATE INDEX IF NOT EXISTS idx_goal_allocations_goal ON goal_account_allocations(goal_id);
CREATE INDEX IF NOT EXISTS idx_goal_allocations_account ON goal_account_allocations(account_id);
CREATE INDEX IF NOT EXISTS idx_estate_planning_client ON estate_planning(client_id);
CREATE INDEX IF NOT EXISTS idx_documents_client ON documents(client_id);
CREATE INDEX IF NOT EXISTS idx_dependents_client ON dependents(client_id);
