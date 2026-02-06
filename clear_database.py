#!/usr/bin/env python3
"""
Script to clear all user data from the database
This will delete:
- All users
- All user-company relationships
- All companies
- All financial data
- All reports
- All audit logs
"""

import sys
import os
from sqlalchemy import text

# Add the backend directory to the path so we can import database modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import engine, SessionLocal
from backend.models import Base

def clear_all_user_data():
    """Clear all user-related data from the database"""
    print("⚠️  WARNING: This will delete ALL user data from the database!")
    print("This includes:")
    print("- All users")
    print("- All companies")
    print("- All financial data")
    print("- All reports")
    print("- All audit logs")
    print("- All user-company relationships")
    
    confirm = input("\nType 'DELETE ALL' to confirm: ")
    if confirm != 'DELETE ALL':
        print("Operation cancelled.")
        return
    
    session = SessionLocal()
    try:
        print("\n🗑️  Clearing database...")
        
        # Get all table names
        tables_to_clear = [
            'audit_logs',
            'financial_metrics',
            'financial_data',
            'user_companies',
            'companies',
            'users'
        ]
        
        # Clear tables in order of dependencies (child tables first)
        for table in tables_to_clear:
            try:
                result = session.execute(text(f"DELETE FROM {table}"))
                print(f"✅ Cleared {table}: {result.rowcount} rows deleted")
                session.commit()
            except Exception as e:
                print(f"❌ Error clearing {table}: {e}")
                session.rollback()
        
        # Reset sequences
        print("\n🔄 Resetting auto-increment sequences...")
        try:
            session.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1"))
            session.execute(text("ALTER SEQUENCE companies_id_seq RESTART WITH 1"))
            session.commit()
            print("✅ Sequences reset")
        except Exception as e:
            print(f"⚠️  Note: Could not reset sequences (may not exist): {e}")
        
        print("\n✅ Database cleared successfully!")
        print("All user data has been removed.")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        session.rollback()
    finally:
        session.close()

def reset_database():
    """Alternative: Drop and recreate all tables"""
    print("⚠️  WARNING: This will drop and recreate ALL tables!")
    
    confirm = input("\nType 'RESET DB' to confirm: ")
    if confirm != 'RESET DB':
        print("Operation cancelled.")
        return
    
    print("\n🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tables dropped")
    
    print("\n🔄 Recreating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables recreated")
    
    print("\n✅ Database reset complete!")

if __name__ == "__main__":
    print("FinHealth Database Cleaner")
    print("=" * 40)
    print("1. Clear user data (keeps table structure)")
    print("2. Reset entire database (drops and recreates tables)")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == "1":
        clear_all_user_data()
    elif choice == "2":
        reset_database()
    else:
        print("Invalid choice. Exiting.")
