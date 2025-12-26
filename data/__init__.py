"""
Data module initialization.
Provides functions to load client data from database or fallback to sample data.
"""

from .sample_clients import (
    get_sample_client_1,
    get_sample_client_2,
    get_sample_client_3,
    get_all_sample_clients as get_all_sample_clients_legacy,
    get_historical_expenses as get_historical_expenses_legacy,
    HISTORICAL_EXPENSES
)

from .client_loader import (
    load_client_data,
    get_all_clients_from_db,
    get_historical_expenses_from_db
)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import database_exists, init_database


def get_all_sample_clients():
    """Get all clients - from database if available, otherwise from sample data."""
    try:
        if not database_exists():
            init_database(seed_data=True)
        
        db_clients = get_all_clients_from_db()
        
        if db_clients:
            # Database clients override sample clients with same ID
            sample_clients = get_all_sample_clients_legacy()
            sample_clients.update(db_clients)
            return sample_clients
    except Exception as e:
        print(f"Warning: Could not load clients from database: {e}")
    
    return get_all_sample_clients_legacy()


def get_historical_expenses(client_id: str) -> list:
    """Get historical expenses - database first, then sample fallback."""
    try:
        if database_exists():
            db_expenses = get_historical_expenses_from_db(client_id)
            if db_expenses and len(db_expenses) > 0:
                return db_expenses
    except Exception as e:
        print(f"Warning: Could not load historical expenses from database: {e}")
    
    return get_historical_expenses_legacy(client_id)


__all__ = [
    'get_all_sample_clients',
    'get_historical_expenses',
    'load_client_data',
    'get_all_clients_from_db',
    'get_historical_expenses_from_db',
    'get_sample_client_1',
    'get_sample_client_2', 
    'get_sample_client_3',
    'HISTORICAL_EXPENSES'
]
