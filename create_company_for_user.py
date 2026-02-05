#!/usr/bin/env python3
import sys
sys.path.append('backend')

from database import get_db
from models import User, Company, UserCompany
from sqlalchemy.orm import Session
import uuid

def create_company_for_user():
    db = next(get_db())
    
    try:
        # Find the user
        user = db.query(User).filter(User.email == 'deepak@gmail.com').first()
        if not user:
            print("User not found")
            return
        
        print(f"Found user: {user.email} ({user.id})")
        
        # Create a company for the user
        company = Company(
            id=str(uuid.uuid4()),
            name="Deepak's Company",
            industry="Technology",
            description="Sample company for testing",
            created_by=user.id
        )
        
        db.add(company)
        db.commit()
        print(f"Created company: {company.name} ({company.id})")
        
        # Link user to company
        user_company = UserCompany(
            user_id=user.id,
            company_id=company.id,
            role="owner"
        )
        
        db.add(user_company)
        db.commit()
        print(f"Linked user to company")
        
        print("✅ Company created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_company_for_user()
