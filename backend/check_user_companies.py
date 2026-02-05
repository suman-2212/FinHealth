#!/usr/bin/env python3
import sys
sys.path.append('backend')

from database import get_db
from models import User, UserCompany, Company

def check_user_companies():
    db = next(get_db())
    
    # Check user
    user = db.query(User).filter(User.email == 'deepak@gmail.com').first()
    if not user:
        print("User not found")
        return
    
    print(f"User found: {user.id} - {user.email}")
    
    # Check user companies
    user_companies = db.query(UserCompany).filter(UserCompany.user_id == user.id).all()
    print(f"User companies count: {len(user_companies)}")
    
    for uc in user_companies:
        company = db.query(Company).filter(Company.id == uc.company_id).first()
        if company:
            print(f"  - {company.name} ({company.id})")
        else:
            print(f"  - Company not found for ID: {uc.company_id}")
    
    # Check all companies
    all_companies = db.query(Company).all()
    print(f"Total companies in database: {len(all_companies)}")
    
    db.close()

if __name__ == "__main__":
    check_user_companies()
