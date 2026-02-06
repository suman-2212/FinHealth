#!/usr/bin/env python3
"""
Script to clear all user data from the database
"""

import sys
import os
from sqlalchemy import text

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import engine, SessionLocal
from backend.models import Base

def clear_all_user_data():
    """Clear all user-related data from the database"""
    session = SessionLocal()
    try:
        print("🗑️  Clearing database...")
        
        # Clear tables in order of dependencies
        tables_to_clear = [
            'audit_logs',
            'financial_metrics', 
            'financial_data',
            'user_companies',
            'companies',
            'users'
        ]
        
        for table in tables_to_clear:
            try:
                result = session.execute(text(f"DELETE FROM {table}"))
                print(f"✅ Cleared {table}: {result.rowcount} rows deleted")
                session.commit()
            except Exception as e:
                print(f"⚠️  Table {table} may not exist or is already empty: {e}")
                session.rollback()
        
        print("\n✅ Database cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    clear_all_user_data()
