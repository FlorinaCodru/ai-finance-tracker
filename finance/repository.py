import re
import datetime as dt
import pandas as pd
from typing import Optional, Tuple, List
from .db import FinanceDb

def safe_str(s: str, max_len: int = 120) -> str:
    if s is None:
        return ""
    s = re.sub(r"\s+", " ", s.strip())
    return s[:max_len]

def is_date_valid(s: str) -> bool:
    try:
        dt.date.fromisoformat(s); return True
    except Exception:
        return False

class FinanceRep:
    def __init__(self, db: FinanceDb):
        self.db = db

    # ---------- Categories ----------
    def add_category(self, name: str, typ: str) -> Tuple[bool, str]:
        name = safe_str(name, 50); typ = (typ or "").upper()
        if not name or typ not in ("INCOME","EXPENSE"):
            return False, "Invalid category name/type."
        try:
            with self.db.connect() as conn:
                conn.execute("INSERT INTO categories (name, type) VALUES (?, ?);", (name, typ))
            return True, "Category added."
        except Exception as e:
            msg = "Category already exists." if "UNIQUE" in str(e).upper() else str(e)
            return False, msg

    def list_categories(self, typ: Optional[str] = None) -> pd.DataFrame:
        q = "SELECT id, name, type FROM categories"
        params = ()
        if typ in ("INCOME","EXPENSE"):
            q += " WHERE type=?"; params = (typ,)
        with self.db.connect() as conn:
            return pd.read_sql_query(q, conn, params=params)

    # ---------- Budgets ----------
    def add_budget(self, category_id: int, monthly_limit: float):
        if monthly_limit < 0: return False, "Monthly limit must be ≥ 0."
        with self.db.connect() as conn:
            conn.execute("""
                INSERT INTO budgets (category_id, monthly_limit)
                VALUES (?, ?)
                ON CONFLICT(category_id) DO UPDATE SET monthly_limit=excluded.monthly_limit;
            """, (category_id, monthly_limit))
        return True, "Budget saved."

    def get_budgets(self) -> pd.DataFrame:
        with self.db.connect() as conn:
            return pd.read_sql_query("""
                SELECT b.id, c.name as category, c.id as category_id, c.type, b.monthly_limit
                FROM budgets b JOIN categories c ON c.id=b.category_id
                ORDER BY c.type, c.name;
            """, conn)

    # ---------- Transactions ----------
    def add_trans(self, date: str, description: str, amount: float, category_id: int, typ: str):
        if not is_date_valid(date): return False, "Invalid date. Use YYYY-MM-DD."
        description = safe_str(description, 120)
        if amount <= 0: return False, "Amount must be greater than 0."
        typ = (typ or "").upper()
        if typ not in ("INCOME","EXPENSE"): return False, "Invalid transaction type."
        try:
            with self.db.connect() as conn:
                conn.execute("""
                    INSERT INTO transactions (date, description, amount, category_id, type)
                    VALUES (?, ?, ?, ?, ?);
                """, (date, description, amount, category_id, typ))
            return True, "Transaction added."
        except Exception as e:
            return False, str(e)

    def update_trans(self, txn_id: int, date: str, description: str, amount: float, category_id: int, typ: str):
        if txn_id <= 0: return False, "Invalid transaction."
        if not is_date_valid(date): return False, "Invalid date."
        description = safe_str(description, 120)
        if amount <= 0: return False, "Amount must be greater than 0."
        typ = (typ or "").upper()
        if typ not in ("INCOME","EXPENSE"): return False, "Invalid type."
        with self.db.connect() as conn:
            conn.execute("""
                UPDATE transactions
                   SET date=?, description=?, amount=?, category_id=?, type=?
                 WHERE id=?;
            """, (date, description, amount, category_id, typ, txn_id))
        return True, "Transaction updated."

    def delete_trans(self, txn_id: int):
        with self.db.connect() as conn:
            conn.execute("DELETE FROM transactions WHERE id=?;", (txn_id,))

    def get_trans(self, start: Optional[str], end: Optional[str],
                           typ: Optional[str], category_ids: Optional[List[int]]) -> pd.DataFrame:
        q = """
            SELECT t.id, t.date, t.description, t.amount, t.category_id, t.type, c.name as category
            FROM transactions t JOIN categories c ON c.id=t.category_id WHERE 1=1
        """
        params: List = []
        if start and is_date_valid(start):
            q += " AND t.date >= ?"; params.append(start)
        if end and is_date_valid(end):
            q += " AND t.date <= ?"; params.append(end)
        if typ in ("INCOME","EXPENSE"):
            q += " AND t.type = ?"; params.append(typ)
        if category_ids:
            q += f" AND t.category_id IN ({','.join('?'*len(category_ids))})"
            params.extend(category_ids)
        q += " ORDER BY t.date DESC, t.id DESC;"
        with self.db.connect() as conn:
            df = pd.read_sql_query(q, conn, params=params)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df["amount"] = pd.to_numeric(df["amount"])
        return df

    # ---------- Seed ----------
    def seed_defaults(self):
        cats = self.list_categories()
        if cats.empty:
            self.add_category("Salary", "INCOME")
            self.add_category("Freelance", "INCOME")
            self.add_category("Rent", "EXPENSE")
           
            self.add_category("Dining", "EXPENSE")
            self.add_category("Transport", "EXPENSE")
            self.add_category("Groceries", "EXPENSE")
