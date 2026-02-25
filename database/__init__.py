"""
Database package for LLM Advisor application.
Provides SQLite database connection and query utilities.
"""

from .db import (
    get_connection,
    init_database,
    database_exists,
    execute_query,
    fetch_one,
    fetch_all,
    insert_record,
    update_record,
    delete_record,
    get_all_clients,
    get_client_by_id,
    get_primary_clients,
    get_client_accounts,
    get_account_holdings,
    get_client_liabilities,
    get_client_income,
    get_client_goals,
    get_client_insurance,
    get_client_estate_planning,
    get_client_portfolio_metrics,
    get_client_transactions,
    get_document_content,
)

__all__ = [
    "get_connection",
    "init_database",
    "database_exists",
    "execute_query",
    "fetch_one",
    "fetch_all",
    "insert_record",
    "update_record",
    "delete_record",
    "get_all_clients",
    "get_client_by_id",
    "get_primary_clients",
    "get_client_accounts",
    "get_account_holdings",
    "get_client_liabilities",
    "get_client_income",
    "get_client_goals",
    "get_client_insurance",
    "get_client_estate_planning",
    "get_client_portfolio_metrics",
    "get_client_transactions",
    "get_document_content",
]
