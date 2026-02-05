import sqlite3
from pathlib import Path

db_path = Path('financial_health.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if timestamp column exists and rename it to created_at
try:
    cursor.execute('ALTER TABLE audit_logs RENAME COLUMN timestamp TO created_at')
    print('Renamed timestamp column to created_at')
except sqlite3.OperationalError as e:
    print(f'Column rename failed (might already exist): {e}')

# Verify the change
cursor.execute('PRAGMA table_info(audit_logs)')
columns = cursor.fetchall()
print('Updated audit logs table schema:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

conn.commit()
conn.close()
print('Audit table fixed successfully')
