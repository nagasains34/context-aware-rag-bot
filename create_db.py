import sqlite3

# Connect to SQLite database (creates users.db if it doesn't exist)
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create the users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    membership_tier TEXT NOT NULL
)
""")

# Insert the sample users
cursor.execute("""
INSERT OR REPLACE INTO users (user_id, name, membership_tier)
VALUES
(101, 'Riya Sharma', 'Gold'),
(102, 'Aman Verma', 'Silver'),
(103, 'Neha Iyer', 'Platinum');
""")

# Save changes and close connection
conn.commit()
conn.close()

print("Database created successfully.")