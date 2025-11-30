# check_db.py
import sqlite3

# Connect to your local SQLite DB
conn = sqlite3.connect('sovereign_kingdom.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("TABLES:", tables)

conn.close()
