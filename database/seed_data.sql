-- LLM Advisor Seed Data
-- Sample INSERT statements for initial data population
-- Single client: John Michael Smith

-- ============================================
-- ACCOUNT TYPES (Reference Data)
-- ============================================
INSERT INTO account_types (account_type_name, tax_advantaged, is_roth, is_liquid, description) VALUES
('checking', FALSE, FALSE, TRUE, 'Standard checking account'),
('savings', FALSE, FALSE, TRUE, 'Standard savings account'),
('brokerage', FALSE, FALSE, TRUE, 'Taxable investment account'),
('401k', TRUE, FALSE, TRUE, 'Employer-sponsored retirement plan'),
('roth_401k', TRUE, TRUE, TRUE, 'Roth employer-sponsored retirement plan'),
('traditional_ira', TRUE, FALSE, TRUE, 'Traditional Individual Retirement Account'),
('roth_ira', TRUE, TRUE, TRUE, 'Roth Individual Retirement Account'),
('hsa', TRUE, FALSE, TRUE, 'Health Savings Account'),
('529', TRUE, FALSE, TRUE, 'Education savings plan'),
('real_estate', FALSE, FALSE, FALSE, 'Real estate holdings'),
('crypto', FALSE, FALSE, TRUE, 'Cryptocurrency accounts');

-- ============================================
-- CLIENTS
-- ============================================
INSERT INTO clients (id, name, date_of_birth, gender_at_birth, is_primary, primary_uuid, retirement_age, risk_tolerance, marital_status, state) VALUES
('client-001-john-smith', 'John Michael Smith', '1978-03-15', 'male', TRUE, NULL, 65, 'moderate', 'married', 'California');

-- ============================================
-- ACCOUNTS
-- ============================================
INSERT INTO accounts (id, account_name, account_type_name, institution, account_number_masked) VALUES
('acc-001-checking', 'Primary Checking', 'checking', 'Chase Bank', '****4521'),
('acc-002-savings', 'Emergency Fund Savings', 'savings', 'Chase Bank', '****4522'),
('acc-003-brokerage', 'Individual Brokerage', 'brokerage', 'Fidelity', '****7891'),
('acc-004-401k', 'Company 401(k)', '401k', 'Vanguard', '****3345'),
('acc-005-roth-ira', 'Roth IRA', 'roth_ira', 'Fidelity', '****7892'),
('acc-006-hsa', 'Health Savings Account', 'hsa', 'HealthEquity', '****2234'),
('acc-007-529', 'College Savings 529', '529', 'Vanguard', '****5567');

-- ============================================
-- ACCOUNT OWNERS
-- ============================================
INSERT INTO account_owners (id, client_id, account_id, ownership_type) VALUES
('ao-001', 'client-001-john-smith', 'acc-001-checking', 'sole'),
('ao-002', 'client-001-john-smith', 'acc-002-savings', 'sole'),
('ao-003', 'client-001-john-smith', 'acc-003-brokerage', 'sole'),
('ao-004', 'client-001-john-smith', 'acc-004-401k', 'sole'),
('ao-005', 'client-001-john-smith', 'acc-005-roth-ira', 'sole'),
('ao-006', 'client-001-john-smith', 'acc-006-hsa', 'sole'),
('ao-007', 'client-001-john-smith', 'acc-007-529', 'sole');

-- ============================================
-- SECURITIES
-- ============================================
INSERT INTO securities (id, name, security_type, expense_ratio) VALUES
('sec-001-vti', 'Vanguard Total Stock Market ETF (VTI)', 'etf', 0.03),
('sec-002-vxus', 'Vanguard Total International Stock ETF (VXUS)', 'etf', 0.07),
('sec-003-bnd', 'Vanguard Total Bond Market ETF (BND)', 'etf', 0.03),
('sec-004-vgt', 'Vanguard Information Technology ETF (VGT)', 'etf', 0.10),
('sec-005-aapl', 'Apple Inc. (AAPL)', 'stock', NULL),
('sec-006-msft', 'Microsoft Corporation (MSFT)', 'stock', NULL),
('sec-007-googl', 'Alphabet Inc. (GOOGL)', 'stock', NULL),
('sec-008-vfiax', 'Vanguard 500 Index Fund Admiral (VFIAX)', 'mutual_fund', 0.04),
('sec-009-cash', 'Cash & Money Market', 'cash', NULL),
('sec-010-btc', 'Bitcoin (BTC)', 'crypto', NULL);

-- ============================================
-- HOLDINGS
-- ============================================
-- Checking Account
INSERT INTO holdings (id, account_id, security_id, quantity, cost_basis, as_of_date) VALUES
('hold-001', 'acc-001-checking', 'sec-009-cash', 15000.00, 15000.00, '2024-12-20');

-- Savings Account
INSERT INTO holdings (id, account_id, security_id, quantity, cost_basis, as_of_date) VALUES
('hold-002', 'acc-002-savings', 'sec-009-cash', 45000.00, 45000.00, '2024-12-20');

-- Brokerage Account
INSERT INTO holdings (id, account_id, security_id, quantity, cost_basis, as_of_date) VALUES
('hold-003', 'acc-003-brokerage', 'sec-001-vti', 250.00, 52500.00, '2024-12-20'),
('hold-004', 'acc-003-brokerage', 'sec-005-aapl', 100.00, 15000.00, '2024-12-20'),
('hold-005', 'acc-003-brokerage', 'sec-006-msft', 75.00, 22500.00, '2024-12-20'),
('hold-006', 'acc-003-brokerage', 'sec-010-btc', 0.5, 20000.00, '2024-12-20');

-- 401(k) Account
INSERT INTO holdings (id, account_id, security_id, quantity, cost_basis, as_of_date) VALUES
('hold-007', 'acc-004-401k', 'sec-008-vfiax', 1500.00, 375000.00, '2024-12-20'),
('hold-008', 'acc-004-401k', 'sec-002-vxus', 500.00, 27500.00, '2024-12-20'),
('hold-009', 'acc-004-401k', 'sec-003-bnd', 300.00, 22500.00, '2024-12-20');

-- Roth IRA
INSERT INTO holdings (id, account_id, security_id, quantity, cost_basis, as_of_date) VALUES
('hold-010', 'acc-005-roth-ira', 'sec-001-vti', 200.00, 42000.00, '2024-12-20'),
('hold-011', 'acc-005-roth-ira', 'sec-004-vgt', 100.00, 45000.00, '2024-12-20');

-- HSA
INSERT INTO holdings (id, account_id, security_id, quantity, cost_basis, as_of_date) VALUES
('hold-012', 'acc-006-hsa', 'sec-001-vti', 50.00, 10500.00, '2024-12-20'),
('hold-013', 'acc-006-hsa', 'sec-009-cash', 2500.00, 2500.00, '2024-12-20');

-- 529 Account
INSERT INTO holdings (id, account_id, security_id, quantity, cost_basis, as_of_date) VALUES
('hold-014', 'acc-007-529', 'sec-001-vti', 150.00, 31500.00, '2024-12-20'),
('hold-015', 'acc-007-529', 'sec-003-bnd', 50.00, 3750.00, '2024-12-20');

-- ============================================
-- TRANSACTIONS
-- ============================================
INSERT INTO transactions (id, client_id, account_id, date, type, amount, direction, description) VALUES
('txn-001', 'client-001-john-smith', 'acc-001-checking', '2024-12-15', 'payroll', 8500.00, 'credit', 'Bi-weekly salary deposit'),
('txn-002', 'client-001-john-smith', 'acc-001-checking', '2024-12-01', 'payroll', 8500.00, 'credit', 'Bi-weekly salary deposit'),
('txn-003', 'client-001-john-smith', 'acc-001-checking', '2024-12-01', 'mortgage', 3200.00, 'debit', 'Monthly mortgage payment'),
('txn-004', 'client-001-john-smith', 'acc-001-checking', '2024-12-05', 'transfer', 2000.00, 'debit', 'Transfer to savings'),
('txn-005', 'client-001-john-smith', 'acc-002-savings', '2024-12-05', 'transfer', 2000.00, 'credit', 'Transfer from checking'),
('txn-006', 'client-001-john-smith', 'acc-004-401k', '2024-12-15', 'contribution', 1250.00, 'credit', '401k contribution'),
('txn-007', 'client-001-john-smith', 'acc-004-401k', '2024-12-15', 'employer_match', 625.00, 'credit', 'Employer 401k match'),
('txn-008', 'client-001-john-smith', 'acc-005-roth-ira', '2024-12-10', 'contribution', 583.33, 'credit', 'Monthly Roth IRA contribution'),
('txn-009', 'client-001-john-smith', 'acc-003-brokerage', '2024-11-20', 'buy', 5000.00, 'debit', 'Purchase VTI shares'),
('txn-010', 'client-001-john-smith', 'acc-006-hsa', '2024-12-15', 'contribution', 300.00, 'credit', 'HSA payroll contribution');

-- ============================================
-- LIABILITIES
-- ============================================
INSERT INTO liabilities (id, client_id, liability_type, description, balance, interest_rate, minimum_payment, as_of_date) VALUES
('liab-001', 'client-001-john-smith', 'mortgage_primary', '30-year fixed mortgage on primary residence', 485000.00, 3.75, 3200.00, '2024-12-20'),
('liab-002', 'client-001-john-smith', 'auto_loan', '2022 Tesla Model Y auto loan', 28500.00, 4.25, 550.00, '2024-12-20'),
('liab-003', 'client-001-john-smith', 'student_loan', 'MBA student loan - federal', 15000.00, 5.50, 350.00, '2024-12-20');

-- ============================================
-- INCOME
-- ============================================
INSERT INTO income (id, client_id, income_type, amount, frequency, effective_date, end_date) VALUES
('inc-001', 'client-001-john-smith', 'salary', 220000.00, 'annual', '2024-01-01', NULL),
('inc-002', 'client-001-john-smith', 'bonus', 35000.00, 'annual', '2024-01-01', NULL),
('inc-003', 'client-001-john-smith', 'investment', 8500.00, 'annual', '2024-01-01', NULL);

-- ============================================
-- INSURANCE COVERAGE
-- ============================================
INSERT INTO insurance_coverage (id, client_id, effective_date, life_insurance_coverage, life_insurance_type, disability_coverage_monthly, disability_coverage_type, umbrella_coverage, long_term_care) VALUES
('ins-001', 'client-001-john-smith', '2024-01-01', 1000000.00, 'term', 12000.00, 'long_term', 2000000.00, FALSE);

-- ============================================
-- PORTFOLIO METRICS
-- ============================================
INSERT INTO portfolio_metrics (id, client_id, snapshot_date, weighted_expense_ratio, annual_turnover, tax_efficiency_score, concentration_score, trades_last_12_months) VALUES
('pm-001', 'client-001-john-smith', '2024-12-20', 0.045, 8.5, 82, 75, 24);

-- ============================================
-- GOALS
-- ============================================
INSERT INTO goals (id, client_id, name, target_amount, target_date, priority, monthly_contribution, status) VALUES
('goal-001', 'client-001-john-smith', 'Retirement at 65', 3500000.00, '2043-03-15', 1, 2458.33, 'active'),
('goal-002', 'client-001-john-smith', 'Emergency Fund (6 months)', 75000.00, '2025-06-01', 2, 2000.00, 'active'),
('goal-003', 'client-001-john-smith', 'College Fund for Kids', 250000.00, '2035-09-01', 3, 1000.00, 'active'),
('goal-004', 'client-001-john-smith', 'Vacation Home Down Payment', 150000.00, '2028-01-01', 4, 1500.00, 'active');

-- ============================================
-- GOAL ACCOUNT ALLOCATIONS
-- ============================================
INSERT INTO goal_account_allocations (id, goal_id, account_id, allocation_percentage) VALUES
('gaa-001', 'goal-001', 'acc-004-401k', 70.0),
('gaa-002', 'goal-001', 'acc-005-roth-ira', 30.0),
('gaa-003', 'goal-002', 'acc-002-savings', 100.0),
('gaa-004', 'goal-003', 'acc-007-529', 100.0),
('gaa-005', 'goal-004', 'acc-003-brokerage', 100.0);

-- ============================================
-- ESTATE PLANNING
-- ============================================
INSERT INTO estate_planning (id, client_id, has_will, will_last_updated, has_trust, has_poa_financial, has_poa_healthcare, has_healthcare_directive, beneficiaries_updated, beneficiaries_last_reviewed, digital_estate_documented) VALUES
('ep-001', 'client-001-john-smith', TRUE, '2023-06-15', FALSE, TRUE, TRUE, TRUE, TRUE, '2024-01-10', FALSE);

-- ============================================
-- DOCUMENTS
-- ============================================
INSERT INTO documents (id, client_id, document_type, file_name, file_hash, storage_path, uploaded_by) VALUES
('doc-001', 'client-001-john-smith', 'will', 'john_smith_will_2023.pdf', 'a1b2c3d4e5f6', '/documents/client-001/will/', 'advisor'),
('doc-002', 'client-001-john-smith', 'poa', 'john_smith_poa_financial.pdf', 'b2c3d4e5f6g7', '/documents/client-001/poa/', 'advisor'),
('doc-003', 'client-001-john-smith', 'statement', 'fidelity_statement_dec2024.pdf', 'c3d4e5f6g7h8', '/documents/client-001/statements/', 'client'),
('doc-004', 'client-001-john-smith', 'tax_return', '2023_tax_return.pdf', 'd4e5f6g7h8i9', '/documents/client-001/tax/', 'advisor'),
('doc-005', 'client-001-john-smith', 'insurance_policy', 'term_life_policy.pdf', 'e5f6g7h8i9j0', '/documents/client-001/insurance/', 'advisor');
