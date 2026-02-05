import sqlite3
from pathlib import Path

db_path = Path('financial_health.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current companies data
cursor.execute('SELECT * FROM companies')
companies = cursor.fetchall()
print('Current companies data:', companies)

# Check available tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Available tables:', [table[0] for table in tables])

conn.close()
