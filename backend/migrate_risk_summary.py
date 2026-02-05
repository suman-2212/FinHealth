import sqlite3
import os

# Path to database
db_path = 'financial_health.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if new columns exist
        cursor.execute("PRAGMA table_info(risk_summaries)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add new columns if they don't exist
        new_columns = [
            ('overall_risk_score', 'NUMERIC(5, 2)'),
            ('leverage_risk_score', 'NUMERIC(5, 2)'),
            ('liquidity_risk_score', 'NUMERIC(5, 2)'),
            ('profitability_risk_score', 'NUMERIC(5, 2)'),
            ('cash_flow_risk_score', 'NUMERIC(5, 2)'),
            ('leverage_risk_level', 'VARCHAR(20)'),
            ('liquidity_risk_level', 'VARCHAR(20)'),
            ('profitability_risk_level', 'VARCHAR(20)'),
            ('cash_flow_risk_level', 'VARCHAR(20)'),
            ('current_ratio', 'NUMERIC(8, 4)'),
            ('quick_ratio', 'NUMERIC(8, 4)'),
            ('net_margin', 'NUMERIC(5, 4)'),
            ('net_income', 'NUMERIC(15, 2)'),
            ('cash_flow_stability', 'NUMERIC(5, 2)'),
            ('negative_cash_flow_months', 'INTEGER'),
            ('mitigation_actions', 'JSON')
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in columns:
                print(f"Adding column: {col_name}")
                cursor.execute(f"ALTER TABLE risk_summaries ADD COLUMN {col_name} {col_type}")
        
        # Rename existing columns if needed
        if 'risk_level' in columns and 'overall_risk_level' not in columns:
            print("Renaming risk_level to overall_risk_level")
            cursor.execute("ALTER TABLE risk_summaries RENAME COLUMN risk_level TO overall_risk_level")
        
        conn.commit()
        print("Migration completed successfully")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()
else:
    print("Database file not found")
