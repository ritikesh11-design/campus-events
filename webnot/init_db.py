import sqlite3

# Create (or connect) the database file
conn = sqlite3.connect("app.db")

# Run schema
with open("schema.sql", "r") as f:
    conn.executescript(f.read())

# Run seed
with open("seed.sql", "r") as f:
    conn.executescript(f.read())

conn.commit()
conn.close()
print("Database initialized and seeded successfully ✅")
