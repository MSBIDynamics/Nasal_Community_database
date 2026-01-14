import sqlite3

conn = sqlite3.connect('./db.sqlite3')

# Create a cursor object
cursor = conn.cursor()

# Example: Create a table (uncomment if needed)
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY,
#         name TEXT NOT NULL,
#         email TEXT NOT NULL
#     )
# ''')

# Example: Insert sample data (uncomment if needed)
# cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@example.com"))
# cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Bob", "bob@example.com"))
# conn.commit()

# Query the database
cursor.execute("DELETE FROM disease_species;")
conn.commit()
rows = cursor.fetchall()

# Print results
for row in rows:
    print(row)

# Close the connection
conn.close()