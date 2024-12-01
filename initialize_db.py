import sqlite3
import os

# Ensure database directory exists
os.makedirs('database', exist_ok=True)

# Database path
DATABASE_PATH = 'database/educational_resources.db'

# Create database and table
connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    path TEXT NOT NULL
)
""")
connection.commit()
connection.close()
print("Database initialized successfully!")
