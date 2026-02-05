import sqlite3
from pathlib import Path

db_path = Path('financial_health.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if audit_logs table exists
cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="audit_logs"')
audit_table = cursor.fetchall()
print('Audit logs table exists:', len(audit_table) > 0)

if audit_table:
    cursor.execute('PRAGMA table_info(audit_logs)')
    columns = cursor.fetchall()
    print('Audit logs table schema:')
    for col in columns:
        print(f'  {col[1]} ({col[2]})')

conn.close()
