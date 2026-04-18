import sqlite3
from config import Config
import uuid


DB_PATH = Config.DB_CONFIG["db_path"]

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # return dict-like rows
    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def create_session(username):
    conn = get_connection()
    cursor = conn.cursor()

    session_id = str(uuid.uuid4())
    from datetime import datetime, date
    today = date.today()

    cursor.execute(
        "INSERT INTO sessions (session, username,created) VALUES (?, ?, ?)",
        (session_id, username, today)
    )

    conn.commit()
    conn.close()

    return session_id

def insert_user(data):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        print("Inserting user:", data, flush=True)

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (data["username"], data["password"])
        )

        conn.commit()

        print("Insert SUCCESS", flush=True)
        return True

    except Exception as e:
        print("Insert ERROR:", e, flush=True)   # 🔥 IMPORTANT
        return False

    finally:
        conn.close()

def get_user(username):
    conn = get_connection()
    cursor = conn.cursor()

    print("Searching for:", username)

    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    row = cursor.fetchone()
    conn.close()
    print("Row fetched:", row)

    if row:
        return dict(row)

    return None

def update_user_in_db(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (data["password"], data["username"])
    )

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return False

    conn.close()
    return True

def delete_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM users where username = ?",(username,)
    )

    conn.commit()
    rows_deleted = cursor.rowcount 
    print(rows_deleted)

    if rows_deleted ==  0:
        return False

    conn.close()
    return True


def patch_user_in_db(username, data):
    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    values = []

    for key, value in data.items():
        fields.append(f"{key} = ?")
        values.append(value)

    values.append(username)

    query = f"UPDATE users SET {', '.join(fields)} WHERE username = ?"

    cursor.execute(query, values)
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return False

    conn.close()
    return True

def get_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM sessions WHERE session = ?",
        (session_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)

    return None

