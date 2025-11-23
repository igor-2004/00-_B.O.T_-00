import sqlite3
import time
from typing import List, Dict

def get_conn(path):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(path):
    conn = get_conn(path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submitter_id INTEGER,
        kind TEXT, -- 'single' or 'album'
        file_ids TEXT, -- join with '|'
        comment TEXT,
        created_at INTEGER
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY
    );
    """)
    conn.commit()
    conn.close()

def add_submission(path, submitter_id:int, kind:str, file_ids:List[str], comment:str):
    now = int(time.time())
    conn = get_conn(path)
    cur = conn.cursor()
    cur.execute("INSERT INTO submissions (submitter_id, kind, file_ids, comment, created_at) VALUES (?,?,?,?,?)",
                (submitter_id, kind, "|".join(file_ids), comment or "", now))
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid

def get_submissions_last_seconds(path, seconds:int):
    cutoff = int(time.time()) - seconds
    conn = get_conn(path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM submissions WHERE created_at >= ? ORDER BY created_at DESC", (cutoff,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_admin(path, user_id:int):
    conn = get_conn(path)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def remove_admin(path, user_id:int):
    conn = get_conn(path)
    cur = conn.cursor()
    cur.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def list_admins(path):
    conn = get_conn(path)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM admins")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows

def is_admin(path, user_id:int):
    conn = get_conn(path)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
    r = cur.fetchone()
    conn.close()
    return bool(r)

def ensure_owner_admin(owner_id:int, db_path:str=None):
    """
    Ensure owner (OWNER_ID) is present in admins table.
    Если db_path не задан, функция ничего не делает.
    """
    if not owner_id:
        return
    # DB path may be assigned globally in bot module; try common path
    # For safety, try /data/bot_database.db if not passed
    path = db_path or "/data/bot_database.db"
    try:
        conn = get_conn(path)
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (owner_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print("ensure_owner_admin failed:", e)
