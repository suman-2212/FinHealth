import sqlite3
from pathlib import Path

def check_v2_table():
    """Check the industry_benchmarks_v2 table"""
    db_path = Path(__file__).parent / "financial_health.db"
    
    if not db_path.exists():
        print("Database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if v2 table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='industry_benchmarks_v2'
        """)
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("industry_benchmarks_v2 table exists")
            
            # Get table schema
            cursor.execute("PRAGMA table_info(industry_benchmarks_v2)")
            columns = cursor.fetchall()
            print("Current columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM industry_benchmarks_v2")
            count = cursor.fetchone()[0]
            print(f"Table has {count} records")
            
            if count > 0:
                # Show sample data
                cursor.execute("SELECT industry_type, metric_name, industry_avg FROM industry_benchmarks_v2 LIMIT 5")
                sample = cursor.fetchall()
                print("Sample data:")
                for row in sample:
                    print(f"  {row[0]} - {row[1]}: {row[2]}")
        else:
            print("industry_benchmarks_v2 table does not exist")
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_v2_table()
