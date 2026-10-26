import sqlite3
from datetime import datetime
from config import BASE_DIR

DB_PATH = BASE_DIR / "bot.db"

def _conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with _conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            joined_at TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            charge_id TEXT,
            created_at TEXT
        )""")

def add_user(user_id: int, username: str | None):
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?)",
                  (user_id, username, datetime.now().isoformat()))

def has_access(user_id: int) -> bool:
    with _conn() as c:
        r = c.execute("SELECT 1 FROM purchases WHERE user_id=? LIMIT 1", (user_id,)).fetchone()
    return r is not None

def add_purchase(user_id: int, amount: int, charge_id: str):
    with _conn() as c:
        c.execute("INSERT INTO purchases (user_id, amount, charge_id, created_at) VALUES (?,?,?,?)",
                  (user_id, amount, charge_id, datetime.now().isoformat()))

def stats() -> tuple[int, int, int]:
    with _conn() as c:
        users = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        buyers = c.execute("SELECT COUNT(DISTINCT user_id) FROM purchases").fetchone()[0]
        total = c.execute("SELECT COALESCE(SUM(amount),0) FROM purchases").fetchone()[0]
    return users, buyers, total
