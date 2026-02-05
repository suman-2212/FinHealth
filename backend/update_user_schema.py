import sqlite3
from pathlib import Path

db_path = Path('financial_health.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add new columns to users table
new_columns = [
    ('phone', 'VARCHAR'),
    ('role', 'VARCHAR DEFAULT "viewer"'),
    ('profile_image_url', 'VARCHAR'),
    ('preferred_language', 'VARCHAR DEFAULT "en"'),
    ('timezone', 'VARCHAR DEFAULT "UTC"'),
    ('notification_preferences', 'JSON'),
    ('two_fa_enabled', 'BOOLEAN DEFAULT 0'),
    ('two_fa_secret', 'VARCHAR'),
    ('last_login_at', 'DATETIME')
]

for column_name, column_def in new_columns:
    try:
        cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_def}')
        print(f'Added {column_name} column')
    except sqlite3.OperationalError as e:
        print(f'Column {column_name} already exists: {e}')

conn.commit()
conn.close()
print('User schema updated successfully')
