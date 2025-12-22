"""
Data module initialization.
"""

from .sample_clients import (
    get_sample_client_1,
    get_sample_client_2,
    get_sample_client_3,
    get_all_sample_clients,
    get_historical_expenses,
    HISTORICAL_EXPENSES
)

__all__ = [
    'get_sample_client_1',
    'get_sample_client_2', 
    'get_sample_client_3',
    'get_all_sample_clients',
    'get_historical_expenses',
    'HISTORICAL_EXPENSES'
]
