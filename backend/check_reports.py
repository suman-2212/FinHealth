import sqlite3
from pathlib import Path

def check_reports_data():
    """Check if summary tables have data"""
    db_path = Path(__file__).parent / "financial_health.db"
    
    if not db_path.exists():
        print("Database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check FinancialHealthSummary
        cursor.execute("SELECT COUNT(*) FROM financial_health_summaries")
        health_count = cursor.fetchone()[0]
        print(f"FinancialHealthSummary records: {health_count}")
        
        if health_count > 0:
            cursor.execute("SELECT company_id, health_score, health_category FROM financial_health_summaries LIMIT 1")
            health_data = cursor.fetchone()
            print(f"Sample health data: {health_data}")
        
        # Check RiskSummary
        cursor.execute("SELECT COUNT(*) FROM risk_summaries")
        risk_count = cursor.fetchone()[0]
        print(f"RiskSummary records: {risk_count}")
        
        if risk_count > 0:
            cursor.execute("SELECT company_id, overall_risk_score, overall_risk_level FROM risk_summaries LIMIT 1")
            risk_data = cursor.fetchone()
            print(f"Sample risk data: {risk_data}")
        
        # Check CreditScoreSummary
        cursor.execute("SELECT COUNT(*) FROM credit_score_summaries")
        credit_count = cursor.fetchone()[0]
        print(f"CreditScoreSummary records: {credit_count}")
        
        if credit_count > 0:
            cursor.execute("SELECT company_id, credit_score, credit_rating FROM credit_score_summaries LIMIT 1")
            credit_data = cursor.fetchone()
            print(f"Sample credit data: {credit_data}")
        
        # Check Reports
        cursor.execute("SELECT COUNT(*) FROM reports")
        reports_count = cursor.fetchone()[0]
        print(f"Reports records: {reports_count}")
        
        if reports_count > 0:
            cursor.execute("SELECT company_id, health_score, risk_score, credit_score FROM reports LIMIT 1")
            report_data = cursor.fetchone()
            print(f"Sample report data: {report_data}")
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_reports_data()
