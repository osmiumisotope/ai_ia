"""
Database module for LLM Advisor application.
Provides SQLite database connection and query utilities.
"""

import sqlite3
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager
import uuid
from datetime import datetime

# Database file path
DB_DIR = Path(__file__).parent
DB_PATH = DB_DIR / "advisor.db"
SCHEMA_PATH = DB_DIR / "schema.sql"
SEED_DATA_PATH = DB_DIR / "seed_data.sql"


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Get a database connection with foreign keys enabled.
    
    Args:
        db_path: Optional path to the database file. Defaults to advisor.db
        
    Returns:
        sqlite3.Connection: Database connection object
    """
    path = db_path or str(DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db_context(db_path: Optional[str] = None):
    """
    Context manager for database connections.
    Automatically handles commit/rollback and connection closing.
    
    Args:
        db_path: Optional path to the database file
        
    Yields:
        sqlite3.Connection: Database connection object
    """
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database(db_path: Optional[str] = None, seed_data: bool = False) -> bool:
    """
    Initialize the database with schema and optionally seed data.
    
    Args:
        db_path: Optional path to the database file
        seed_data: Whether to populate with seed data
        
    Returns:
        bool: True if initialization was successful
    """
    try:
        with get_db_context(db_path) as conn:
            # Read and execute schema
            with open(SCHEMA_PATH, 'r') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            
            # --- Migrations: add columns that may be missing on older DBs ---
            _run_migrations(conn)
            
            # Optionally load seed data
            if seed_data and SEED_DATA_PATH.exists():
                with open(SEED_DATA_PATH, 'r') as f:
                    seed_sql = f.read()
                conn.executescript(seed_sql)
                
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False


def _run_migrations(conn):
    """Apply any missing schema migrations to an existing database."""
    # Migration: add file_content BLOB to documents table
    cursor = conn.execute("PRAGMA table_info(documents)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'file_content' not in columns:
        conn.execute("ALTER TABLE documents ADD COLUMN file_content BLOB")


def execute_query(
    query: str, 
    params: Optional[Tuple] = None, 
    db_path: Optional[str] = None
) -> int:
    """
    Execute a query that modifies data (INSERT, UPDATE, DELETE).
    
    Args:
        query: SQL query string
        params: Optional tuple of parameters
        db_path: Optional path to the database file
        
    Returns:
        int: Number of rows affected
    """
    with get_db_context(db_path) as conn:
        cursor = conn.execute(query, params or ())
        return cursor.rowcount


def fetch_one(
    query: str, 
    params: Optional[Tuple] = None, 
    db_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Fetch a single row from a SELECT query.
    
    Args:
        query: SQL SELECT query string
        params: Optional tuple of parameters
        db_path: Optional path to the database file
        
    Returns:
        Optional[Dict]: Row as dictionary or None if not found
    """
    with get_db_context(db_path) as conn:
        cursor = conn.execute(query, params or ())
        row = cursor.fetchone()
        return dict(row) if row else None


def fetch_all(
    query: str, 
    params: Optional[Tuple] = None, 
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch all rows from a SELECT query.
    
    Args:
        query: SQL SELECT query string
        params: Optional tuple of parameters
        db_path: Optional path to the database file
        
    Returns:
        List[Dict]: List of rows as dictionaries
    """
    with get_db_context(db_path) as conn:
        cursor = conn.execute(query, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def generate_uuid() -> str:
    """Generate a new UUID string for use as primary key."""
    return str(uuid.uuid4())


def insert_record(
    table: str, 
    data: Dict[str, Any], 
    db_path: Optional[str] = None
) -> str:
    """
    Insert a record into a table.
    
    Args:
        table: Table name
        data: Dictionary of column names and values
        db_path: Optional path to the database file
        
    Returns:
        str: The ID of the inserted record
    """
    # Generate UUID if id not provided
    if 'id' not in data:
        data['id'] = generate_uuid()
    
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
    with get_db_context(db_path) as conn:
        conn.execute(query, tuple(data.values()))
        
    return data['id']


def update_record(
    table: str, 
    record_id: str, 
    data: Dict[str, Any], 
    db_path: Optional[str] = None
) -> int:
    """
    Update a record in a table.
    
    Args:
        table: Table name
        record_id: ID of the record to update
        data: Dictionary of column names and values to update
        db_path: Optional path to the database file
        
    Returns:
        int: Number of rows affected
    """
    # Add updated_at timestamp if the table has it
    data['updated_at'] = datetime.now().isoformat()
    
    set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
    params = tuple(data.values()) + (record_id,)
    
    return execute_query(query, params, db_path)


def delete_record(
    table: str, 
    record_id: str, 
    db_path: Optional[str] = None
) -> int:
    """
    Delete a record from a table.
    
    Args:
        table: Table name
        record_id: ID of the record to delete
        db_path: Optional path to the database file
        
    Returns:
        int: Number of rows affected
    """
    query = f"DELETE FROM {table} WHERE id = ?"
    return execute_query(query, (record_id,), db_path)


# ============================================
# Client-specific queries
# ============================================

def get_all_clients(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all clients."""
    return fetch_all("SELECT * FROM clients ORDER BY name", db_path=db_path)


def get_client_by_id(client_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get a client by ID."""
    return fetch_one("SELECT * FROM clients WHERE id = ?", (client_id,), db_path)


def get_primary_clients(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all primary clients (not dependents/spouses linked to another)."""
    return fetch_all(
        "SELECT * FROM clients WHERE is_primary = TRUE ORDER BY name", 
        db_path=db_path
    )


# ============================================
# Account-specific queries
# ============================================

def get_client_accounts(client_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all accounts for a client."""
    query = """
        SELECT a.*, ao.ownership_type, at.tax_advantaged, at.is_roth, at.is_liquid
        FROM accounts a
        JOIN account_owners ao ON a.id = ao.account_id
        JOIN account_types at ON a.account_type_name = at.account_type_name
        WHERE ao.client_id = ?
        ORDER BY a.account_name
    """
    return fetch_all(query, (client_id,), db_path)


def get_account_holdings(account_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all holdings for an account."""
    query = """
        SELECT h.*, s.name as security_name, s.security_type, s.expense_ratio
        FROM holdings h
        JOIN securities s ON h.security_id = s.id
        WHERE h.account_id = ?
        ORDER BY s.name
    """
    return fetch_all(query, (account_id,), db_path)


# ============================================
# Financial data queries
# ============================================

def get_client_liabilities(client_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all liabilities for a client."""
    return fetch_all(
        "SELECT * FROM liabilities WHERE client_id = ? ORDER BY balance DESC",
        (client_id,),
        db_path
    )


def get_client_income(client_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all income sources for a client."""
    return fetch_all(
        "SELECT * FROM income WHERE client_id = ? ORDER BY amount DESC",
        (client_id,),
        db_path
    )


def get_client_goals(client_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all goals for a client."""
    return fetch_all(
        "SELECT * FROM goals WHERE client_id = ? ORDER BY priority, target_date",
        (client_id,),
        db_path
    )


def get_client_insurance(client_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get insurance coverage for a client."""
    return fetch_one(
        "SELECT * FROM insurance_coverage WHERE client_id = ? ORDER BY effective_date DESC LIMIT 1",
        (client_id,),
        db_path
    )


def get_client_estate_planning(client_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get estate planning status for a client."""
    return fetch_one(
        "SELECT * FROM estate_planning WHERE client_id = ?",
        (client_id,),
        db_path
    )


def get_client_portfolio_metrics(client_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get latest portfolio metrics for a client."""
    return fetch_one(
        "SELECT * FROM portfolio_metrics WHERE client_id = ? ORDER BY snapshot_date DESC LIMIT 1",
        (client_id,),
        db_path
    )


def get_client_transactions(
    client_id: str, 
    limit: int = 50, 
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get recent transactions for a client."""
    return fetch_all(
        "SELECT * FROM transactions WHERE client_id = ? ORDER BY date DESC LIMIT ?",
        (client_id, limit),
        db_path
    )


# ============================================
# Profile update queries
# ============================================

def update_client_profile(
    client_id: str,
    data: Dict[str, Any],
    db_path: Optional[str] = None
) -> int:
    """Update a client's profile information."""
    return update_record('clients', client_id, data, db_path)


# ============================================
# Dependents queries
# ============================================

def get_client_dependents(client_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all dependents for a client."""
    return fetch_all(
        "SELECT * FROM dependents WHERE client_id = ? ORDER BY name",
        (client_id,),
        db_path
    )


def add_dependent(
    client_id: str,
    data: Dict[str, Any],
    db_path: Optional[str] = None
) -> str:
    """Add a new dependent for a client."""
    data['client_id'] = client_id
    return insert_record('dependents', data, db_path)


def update_dependent(
    dependent_id: str,
    data: Dict[str, Any],
    db_path: Optional[str] = None
) -> int:
    """Update a dependent's information."""
    return update_record('dependents', dependent_id, data, db_path)


def delete_dependent(dependent_id: str, db_path: Optional[str] = None) -> int:
    """Delete a dependent."""
    return delete_record('dependents', dependent_id, db_path)


# ============================================
# Document queries
# ============================================

def get_client_documents(client_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all documents for a client."""
    return fetch_all(
        "SELECT * FROM documents WHERE client_id = ? ORDER BY upload_time DESC",
        (client_id,),
        db_path
    )


def get_document_by_id(document_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get a document by ID."""
    return fetch_one("SELECT * FROM documents WHERE id = ?", (document_id,), db_path)


def add_document(
    client_id: str,
    data: Dict[str, Any],
    db_path: Optional[str] = None
) -> str:
    """Add a new document for a client."""
    data['client_id'] = client_id
    return insert_record('documents', data, db_path)


def delete_document(document_id: str, db_path: Optional[str] = None) -> int:
    """Delete a document record."""
    return delete_record('documents', document_id, db_path)


def get_document_by_hash(file_hash: str, client_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Check if a document with the same hash already exists for a client."""
    return fetch_one(
        "SELECT * FROM documents WHERE file_hash = ? AND client_id = ?",
        (file_hash, client_id),
        db_path
    )


def get_document_content(document_id: str, db_path: Optional[str] = None) -> Optional[bytes]:
    """Retrieve the binary file content for a document from the database."""
    with get_db_context(db_path) as conn:
        cursor = conn.execute(
            "SELECT file_content FROM documents WHERE id = ?",
            (document_id,)
        )
        row = cursor.fetchone()
        if row and row['file_content']:
            return bytes(row['file_content'])
    return None


# ============================================
# Aggregation queries
# ============================================

def get_client_total_assets(client_id: str, db_path: Optional[str] = None) -> float:
    """Calculate total assets for a client across all accounts."""
    query = """
        SELECT COALESCE(SUM(h.cost_basis), 0) as total_assets
        FROM holdings h
        JOIN accounts a ON h.account_id = a.id
        JOIN account_owners ao ON a.id = ao.account_id
        WHERE ao.client_id = ?
    """
    result = fetch_one(query, (client_id,), db_path)
    return result['total_assets'] if result else 0.0


def get_client_total_liabilities(client_id: str, db_path: Optional[str] = None) -> float:
    """Calculate total liabilities for a client."""
    query = """
        SELECT COALESCE(SUM(balance), 0) as total_liabilities
        FROM liabilities
        WHERE client_id = ?
    """
    result = fetch_one(query, (client_id,), db_path)
    return result['total_liabilities'] if result else 0.0


def get_client_net_worth(client_id: str, db_path: Optional[str] = None) -> float:
    """Calculate net worth for a client."""
    assets = get_client_total_assets(client_id, db_path)
    liabilities = get_client_total_liabilities(client_id, db_path)
    return assets - liabilities


def get_client_annual_income(client_id: str, db_path: Optional[str] = None) -> float:
    """Calculate total annual income for a client."""
    query = """
        SELECT COALESCE(SUM(
            CASE 
                WHEN frequency = 'annual' THEN amount
                WHEN frequency = 'monthly' THEN amount * 12
                ELSE 0
            END
        ), 0) as annual_income
        FROM income
        WHERE client_id = ?
        AND (end_date IS NULL OR end_date >= date('now'))
    """
    result = fetch_one(query, (client_id,), db_path)
    return result['annual_income'] if result else 0.0


# ============================================
# Utility functions
# ============================================

def database_exists(db_path: Optional[str] = None) -> bool:
    """Check if the database file exists."""
    path = db_path or str(DB_PATH)
    return os.path.exists(path)


def reset_database(db_path: Optional[str] = None) -> bool:
    """
    Reset the database by deleting and recreating it.
    WARNING: This will delete all data!
    
    Args:
        db_path: Optional path to the database file
        
    Returns:
        bool: True if reset was successful
    """
    path = db_path or str(DB_PATH)
    try:
        if os.path.exists(path):
            os.remove(path)
        return init_database(db_path)
    except Exception as e:
        print(f"Error resetting database: {e}")
        return False


if __name__ == "__main__":
    # Initialize database when run directly
    print("Initializing database...")
    if init_database():
        print(f"Database created successfully at {DB_PATH}")
    else:
        print("Failed to create database")
