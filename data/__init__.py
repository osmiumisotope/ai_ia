"""
Data module initialization.
Provides functions to load client data from the database.
"""

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
    """Get all clients from the database."""
    try:
        if not database_exists():
            init_database(seed_data=True)
        
        db_clients = get_all_clients_from_db()
        
        if db_clients:
            return db_clients
    except Exception as e:
        print(f"Warning: Could not load clients from database: {e}")
    
    return {}


def get_historical_expenses(client_id: str) -> list:
    """Get historical expenses from the database."""
    try:
        if database_exists():
            db_expenses = get_historical_expenses_from_db(client_id)
            if db_expenses and len(db_expenses) > 0:
                return db_expenses
    except Exception as e:
        print(f"Warning: Could not load historical expenses from database: {e}")
    
    return []


__all__ = [
    'get_all_sample_clients',
    'get_historical_expenses',
    'load_client_data',
    'get_all_clients_from_db',
    'get_historical_expenses_from_db'
]
