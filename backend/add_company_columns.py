import sqlite3
from pathlib import Path

db_path = Path('financial_health.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add missing columns to companies table
try:
    cursor.execute('ALTER TABLE companies ADD COLUMN financial_year_start INTEGER DEFAULT 1')
    print('Added financial_year_start column')
except sqlite3.OperationalError as e:
    print(f'financial_year_start column already exists: {e}')

try:
    cursor.execute('ALTER TABLE companies ADD COLUMN currency VARCHAR(10) DEFAULT "USD"')
    print('Added currency column')
except sqlite3.OperationalError as e:
    print(f'currency column already exists: {e}')

try:
    cursor.execute('ALTER TABLE companies ADD COLUMN gst_number VARCHAR(50) DEFAULT ""')
    print('Added gst_number column')
except sqlite3.OperationalError as e:
    print(f'gst_number column already exists: {e}')

# Update existing company with GST number if registration_number looks like GST
cursor.execute('SELECT id, registration_number FROM companies')
companies = cursor.fetchall()
for company_id, reg_number in companies:
    if reg_number and len(reg_number) > 10:  # Assume long registration numbers are GST
        cursor.execute('UPDATE companies SET gst_number = ? WHERE id = ?', (reg_number, company_id))
        print(f'Updated GST number for company {company_id}: {reg_number}')

conn.commit()
conn.close()
print('Database schema updated successfully')
