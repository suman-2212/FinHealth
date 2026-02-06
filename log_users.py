#!/usr/bin/env python3
"""
Script to log all user details from the database
"""

import sys
import os
from sqlalchemy import text

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import SessionLocal

def log_all_users():
    """Log all user details from the database"""
    session = SessionLocal()
    try:
        print("📋 Fetching all user details...")
        print("=" * 60)
        
        # Get all users
        users_query = session.execute(text("""
            SELECT 
                id, 
                email, 
                full_name, 
                phone, 
                role, 
                is_active, 
                last_login_at, 
                created_at, 
                updated_at,
                preferred_language,
                timezone,
                two_fa_enabled
            FROM users 
            ORDER BY created_at DESC
        """))
        
        users = users_query.fetchall()
        
        if not users:
            print("📭 No users found in database")
            return
        
        print(f"👥 Found {len(users)} user(s):")
        print("-" * 60)
        
        for i, user in enumerate(users, 1):
            print(f"\n👤 User #{i}")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.full_name}")
            print(f"   Phone: {user.phone or 'N/A'}")
            print(f"   Role: {user.role}")
            print(f"   Active: {'Yes' if user.is_active else 'No'}")
            print(f"   Language: {user.preferred_language}")
            print(f"   Timezone: {user.timezone}")
            print(f"   2FA Enabled: {'Yes' if user.two_fa_enabled else 'No'}")
            print(f"   Last Login: {user.last_login_at or 'Never'}")
            print(f"   Created: {user.created_at}")
            print(f"   Updated: {user.updated_at}")
        
        # Get user-company relationships
        print(f"\n🏢 User-Company Relationships:")
        print("-" * 60)
        
        companies_query = session.execute(text("""
            SELECT 
                uc.user_id,
                u.email as user_email,
                uc.company_id,
                c.name as company_name,
                uc.role,
                uc.is_default,
                uc.created_at
            FROM user_companies uc
            JOIN users u ON uc.user_id = u.id
            JOIN companies c ON uc.company_id = c.id
            ORDER BY uc.created_at DESC
        """))
        
        relationships = companies_query.fetchall()
        
        if not relationships:
            print("📭 No user-company relationships found")
        else:
            for rel in relationships:
                print(f"   {rel.user_email} → {rel.company_name} (Role: {rel.role}, Default: {'Yes' if rel.is_default else 'No'})")
        
        # Get companies
        print(f"\n🏢 Companies:")
        print("-" * 60)
        
        companies_list_query = session.execute(text("""
            SELECT 
                id,
                name,
                industry,
                registration_number,
                financial_year_start,
                currency,
                gst_number,
                created_at
            FROM companies 
            ORDER BY created_at DESC
        """))
        
        companies = companies_list_query.fetchall()
        
        if not companies:
            print("📭 No companies found")
        else:
            for i, company in enumerate(companies, 1):
                print(f"\n   Company #{i}")
                print(f"   ID: {company.id}")
                print(f"   Name: {company.name}")
                print(f"   Industry: {company.industry}")
                print(f"   Registration: {company.registration_number or 'N/A'}")
                print(f"   Financial Year Start: Month {company.financial_year_start}")
                print(f"   Currency: {company.currency}")
                print(f"   GST Number: {company.gst_number or 'N/A'}")
                print(f"   Created: {company.created_at}")
        
        print("\n" + "=" * 60)
        print(f"📊 Summary: {len(users)} users, {len(companies)} companies, {len(relationships)} relationships")
        
    except Exception as e:
        print(f"❌ Error fetching user details: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    log_all_users()
