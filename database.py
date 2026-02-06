# database.py
import sqlite3

# Create a connection to the database
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT, role TEXT)')
    conn.commit()

# Run this once to ensure table exists
create_usertable()







