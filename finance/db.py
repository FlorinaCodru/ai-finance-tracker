import sqlite3
from .config import DB_PATH

class FinanceDb:
    def __init__(self, path: str = DB_PATH):
        self.path = path

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('INCOME', 'EXPENSE'))
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    description TEXT,
                    amount REAL NOT NULL CHECK (amount > 0),
                    category_id INTEGER NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('INCOME', 'EXPENSE')),
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER UNIQUE NOT NULL,
                    monthly_limit REAL NOT NULL CHECK (monthly_limit >= 0),
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                );
            """)
            conn.commit()
