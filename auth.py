# auth.py
import hashlib
from database import c, conn  # This import is OK now


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False


def create_user(username, password, role):
    try:
        c.execute('SELECT * FROM userstable WHERE username = ?', (username,))
        if c.fetchone():
            return False

        c.execute('INSERT INTO userstable(username, password, role) VALUES (?,?,?)',
                  (username, make_hashes(password), role))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False


def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username = ?', (username,))
    data = c.fetchall()

    # Verify password if user exists
    if data:
        for user in data:
            if check_hashes(password, user[1]):  # user[1] is the hashed password
                return user
    return False