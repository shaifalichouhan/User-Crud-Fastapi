import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Show all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in DB:", tables)

# Show columns of 'users' table
print("\n Columns in 'users' table:")
cursor.execute("PRAGMA table_info(users);")
columns = cursor.fetchall()
for col in columns:
    print(col)

conn.close()
