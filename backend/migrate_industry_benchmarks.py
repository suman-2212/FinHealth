import sqlite3
import sys
from pathlib import Path

def migrate_industry_benchmarks():
    """Migrate industry_benchmarks table to new schema"""
    
    # Path to database
    db_path = Path(__file__).parent / "financial_health.db"
    
    if not db_path.exists():
        print("Database not found. Please run the application first to create the database.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='industry_benchmarks'
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Table industry_benchmarks does not exist. Creating new table...")
            # Create new table with correct schema
            cursor.execute("""
                CREATE TABLE industry_benchmarks (
                    id TEXT PRIMARY KEY,
                    industry_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    industry_avg REAL,
                    top_quartile REAL,
                    bottom_quartile REAL,
                    percentile_distribution TEXT,
                    sample_size INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(industry_type, metric_name)
                )
            """)
            conn.commit()
            print("Created new industry_benchmarks table")
            return
        
        # Check if new columns exist
        cursor.execute("PRAGMA table_info(industry_benchmarks)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Check if we need to migrate
        if 'industry_type' in columns and 'metric_name' in columns:
            print("Table already has correct schema. No migration needed.")
            return
        
        print("Migrating industry_benchmarks table...")
        
        # Create backup of existing data
        cursor.execute("SELECT * FROM industry_benchmarks")
        existing_data = cursor.fetchall()
        existing_columns = [description[0] for description in cursor.description]
        print(f"Found {len(existing_data)} existing records")
        
        # Drop old table
        cursor.execute("DROP TABLE industry_benchmarks")
        
        # Create new table with correct schema
        cursor.execute("""
            CREATE TABLE industry_benchmarks (
                id TEXT PRIMARY KEY,
                industry_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                industry_avg REAL,
                top_quartile REAL,
                bottom_quartile REAL,
                percentile_distribution TEXT,
                sample_size INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(industry_type, metric_name)
            )
        """)
        
        # Insert default benchmark data
        default_benchmarks = [
            # Retail benchmarks
            ('retail', 'net_profit_margin', 0.03, 0.06, 0.01),
            ('retail', 'gross_margin', 0.35, 0.45, 0.25),
            ('retail', 'current_ratio', 1.5, 2.0, 1.0),
            ('retail', 'debt_to_equity', 1.2, 0.8, 2.0),
            ('retail', 'revenue_growth_rate', 0.08, 0.15, 0.02),
            ('retail', 'operating_margin', 0.06, 0.10, 0.03),
            ('retail', 'quick_ratio', 0.8, 1.2, 0.5),
            ('retail', 'cash_conversion_cycle', 45, 30, 60),
            
            # Manufacturing benchmarks
            ('manufacturing', 'net_profit_margin', 0.05, 0.08, 0.02),
            ('manufacturing', 'gross_margin', 0.30, 0.40, 0.20),
            ('manufacturing', 'current_ratio', 1.8, 2.5, 1.2),
            ('manufacturing', 'debt_to_equity', 1.5, 1.0, 2.5),
            ('manufacturing', 'revenue_growth_rate', 0.06, 0.12, 0.01),
            ('manufacturing', 'operating_margin', 0.10, 0.15, 0.05),
            ('manufacturing', 'quick_ratio', 1.0, 1.5, 0.7),
            ('manufacturing', 'cash_conversion_cycle', 60, 45, 90),
            
            # Services benchmarks
            ('services', 'net_profit_margin', 0.12, 0.18, 0.06),
            ('services', 'gross_margin', 0.55, 0.65, 0.45),
            ('services', 'current_ratio', 1.6, 2.2, 1.1),
            ('services', 'debt_to_equity', 0.8, 0.5, 1.5),
            ('services', 'revenue_growth_rate', 0.10, 0.20, 0.03),
            ('services', 'operating_margin', 0.15, 0.22, 0.08),
            ('services', 'quick_ratio', 1.2, 1.8, 0.8),
            ('services', 'cash_conversion_cycle', 30, 20, 45),
            
            # Technology benchmarks
            ('technology', 'net_profit_margin', 0.15, 0.25, 0.08),
            ('technology', 'gross_margin', 0.65, 0.75, 0.55),
            ('technology', 'current_ratio', 2.0, 3.0, 1.3),
            ('technology', 'debt_to_equity', 0.6, 0.3, 1.2),
            ('technology', 'revenue_growth_rate', 0.25, 0.40, 0.10),
            ('technology', 'operating_margin', 0.20, 0.30, 0.10),
            ('technology', 'quick_ratio', 1.5, 2.5, 1.0),
            ('technology', 'cash_conversion_cycle', 25, 15, 40),
            
            # General benchmarks
            ('general', 'net_profit_margin', 0.08, 0.12, 0.04),
            ('general', 'gross_margin', 0.40, 0.50, 0.30),
            ('general', 'current_ratio', 1.7, 2.3, 1.2),
            ('general', 'debt_to_equity', 1.0, 0.7, 1.8),
            ('general', 'revenue_growth_rate', 0.08, 0.15, 0.02),
            ('general', 'operating_margin', 0.12, 0.18, 0.06),
            ('general', 'quick_ratio', 1.0, 1.5, 0.7),
            ('general', 'cash_conversion_cycle', 40, 30, 60),
        ]
        
        import uuid
        for industry, metric, avg, top, bottom in default_benchmarks:
            cursor.execute("""
                INSERT INTO industry_benchmarks 
                (id, industry_type, metric_name, industry_avg, top_quartile, bottom_quartile, sample_size)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), industry, metric, avg, top, bottom, 1000))
        
        conn.commit()
        print(f"Successfully migrated industry_benchmarks table with {len(default_benchmarks)} benchmark records")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_industry_benchmarks()
