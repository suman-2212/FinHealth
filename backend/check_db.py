import sqlite3
from pathlib import Path

def check_database():
    """Check current database state"""
    db_path = Path(__file__).parent / "financial_health.db"
    
    if not db_path.exists():
        print("Database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if industry_benchmarks table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='industry_benchmarks'
        """)
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("industry_benchmarks table exists")
            
            # Get table schema
            cursor.execute("PRAGMA table_info(industry_benchmarks)")
            columns = cursor.fetchall()
            print("Current columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Check if we have the correct columns
            column_names = [col[1] for col in columns]
            if 'industry_type' in column_names and 'metric_name' in column_names:
                print("✓ Table has correct schema")
                
                # Count records
                cursor.execute("SELECT COUNT(*) FROM industry_benchmarks")
                count = cursor.fetchone()[0]
                print(f"✓ Table has {count} records")
                
                # Show sample data
                cursor.execute("SELECT industry_type, metric_name, industry_avg FROM industry_benchmarks LIMIT 5")
                sample = cursor.fetchall()
                print("Sample data:")
                for row in sample:
                    print(f"  {row[0]} - {row[1]}: {row[2]}")
            else:
                print("✗ Table has incorrect schema")
        else:
            print("industry_benchmarks table does not exist")
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()
