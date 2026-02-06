#!/usr/bin/env python3
"""
Script to monitor database for user activity
"""

import sys
import os
import time
from sqlalchemy import text

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import SessionLocal

def monitor_users():
    """Monitor database for user activity"""
    print("👀 Monitoring database for user activity...")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 60)
    
    last_count = 0
    
    try:
        while True:
            session = SessionLocal()
            try:
                # Get current user count
                count_result = session.execute(text("SELECT COUNT(*) FROM users"))
                user_count = count_result.scalar()
                
                # Get latest user if any
                if user_count > 0:
                    latest_query = session.execute(text("""
                        SELECT email, full_name, created_at 
                        FROM users 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    """))
                    latest_user = latest_query.fetchone()
                    
                    if user_count != last_count:
                        print(f"\n🆕 New user detected!")
                        print(f"   Email: {latest_user.email}")
                        print(f"   Name: {latest_user.full_name}")
                        print(f"   Created: {latest_user.created_at}")
                        print(f"   Total users: {user_count}")
                        print("-" * 40)
                        last_count = user_count
                else:
                    if last_count > 0:
                        print(f"\n🗑️  All users cleared!")
                        print(f"   Total users: 0")
                        print("-" * 40)
                        last_count = 0
                
                # Show company count too
                company_result = session.execute(text("SELECT COUNT(*) FROM companies"))
                company_count = company_result.scalar()
                
                print(f"\r📊 Users: {user_count} | Companies: {company_count} | Monitoring...", end="", flush=True)
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
            finally:
                session.close()
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")

if __name__ == "__main__":
    monitor_users()
