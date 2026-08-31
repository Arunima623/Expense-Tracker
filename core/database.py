"""
SQLite Database management layer for the Expense Tracker.
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import List, Optional, Dict, Any, Generator
from datetime import datetime
from .models import Expense, Budget, CategorySummary, DEFAULT_CATEGORIES


class Database:
    """Handles all SQLite database connections and queries."""

    def __init__(self, db_path: str = "expenses.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Create and yield a new SQLite database connection, ensuring proper closure."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize database schema and tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Expenses Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    amount REAL NOT NULL CHECK(amount > 0),
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    payment_method TEXT DEFAULT 'Cash',
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Budgets Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    month TEXT NOT NULL,
                    monthly_limit REAL NOT NULL CHECK(monthly_limit > 0),
                    UNIQUE(category, month)
                );
            """)

            # Categories Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                );
            """)

            # Create Indices for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_expense_date ON expenses(date);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_expense_category ON expenses(category);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_budget_month ON budgets(month);")

            # Seed default categories if empty
            cursor.execute("SELECT COUNT(*) FROM categories;")
            if cursor.fetchone()[0] == 0:
                for cat in DEFAULT_CATEGORIES:
                    cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?);", (cat,))
            
            conn.commit()

    # ==========================================
    # EXPENSE CRUD OPERATIONS
    # ==========================================

    def add_expense(self, expense: Expense) -> int:
        """Insert a new expense into the database and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO expenses (title, amount, category, date, payment_method, notes)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (
                expense.title,
                expense.amount,
                expense.category,
                expense.date,
                expense.payment_method,
                expense.notes
            ))
            conn.commit()
            return cursor.lastrowid

    def get_expense_by_id(self, expense_id: int) -> Optional[Expense]:
        """Fetch a single expense by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses WHERE id = ?;", (expense_id,))
            row = cursor.fetchone()
            if row:
                return Expense(
                    id=row["id"],
                    title=row["title"],
                    amount=row["amount"],
                    category=row["category"],
                    date=row["date"],
                    payment_method=row["payment_method"],
                    notes=row["notes"] or "",
                    created_at=row["created_at"]
                )
            return None

    def update_expense(self, expense: Expense) -> bool:
        """Update an existing expense."""
        if expense.id is None:
            raise ValueError("Expense ID cannot be None for update operation.")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE expenses
                SET title = ?, amount = ?, category = ?, date = ?, payment_method = ?, notes = ?
                WHERE id = ?;
            """, (
                expense.title,
                expense.amount,
                expense.category,
                expense.date,
                expense.payment_method,
                expense.notes,
                expense.id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?;", (expense_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_all_expenses(self, order_by: str = "date DESC, id DESC") -> List[Expense]:
        """Fetch all expenses sorted by specified order."""
        allowed_orders = ["date DESC, id DESC", "date ASC", "amount DESC", "amount ASC", "category ASC"]
        order_clause = order_by if order_by in allowed_orders else "date DESC, id DESC"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM expenses ORDER BY {order_clause};")
            rows = cursor.fetchall()
            return [
                Expense(
                    id=row["id"],
                    title=row["title"],
                    amount=row["amount"],
                    category=row["category"],
                    date=row["date"],
                    payment_method=row["payment_method"],
                    notes=row["notes"] or "",
                    created_at=row["created_at"]
                ) for row in rows
            ]

    def filter_expenses(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        payment_method: Optional[str] = None,
        search_query: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[Expense]:
        """Filter expenses with multiple dynamic criteria."""
        query = "SELECT * FROM expenses WHERE 1=1"
        params: List[Any] = []

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if category and category != "All":
            query += " AND category = ?"
            params.append(category)
        if payment_method and payment_method != "All":
            query += " AND payment_method = ?"
            params.append(payment_method)
        if min_amount is not None:
            query += " AND amount >= ?"
            params.append(min_amount)
        if max_amount is not None:
            query += " AND amount <= ?"
            params.append(max_amount)
        if search_query and search_query.strip():
            query += " AND (title LIKE ? OR notes LIKE ?)"
            wildcard = f"%{search_query.strip()}%"
            params.extend([wildcard, wildcard])

        query += " ORDER BY date DESC, id DESC;"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                Expense(
                    id=row["id"],
                    title=row["title"],
                    amount=row["amount"],
                    category=row["category"],
                    date=row["date"],
                    payment_method=row["payment_method"],
                    notes=row["notes"] or "",
                    created_at=row["created_at"]
                ) for row in rows
            ]

    # ==========================================
    # BUDGET OPERATIONS
    # ==========================================

    def set_budget(self, category: str, month: str, monthly_limit: float) -> int:
        """Create or update a budget for a category in a specific month (YYYY-MM)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO budgets (category, month, monthly_limit)
                VALUES (?, ?, ?)
                ON CONFLICT(category, month) DO UPDATE SET monthly_limit = excluded.monthly_limit;
            """, (category, month, monthly_limit))
            conn.commit()
            return cursor.lastrowid

    def get_budgets_for_month(self, month: str) -> Dict[str, float]:
        """Fetch all category budgets for a given month as a {category: limit} mapping."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT category, monthly_limit FROM budgets WHERE month = ?;", (month,))
            rows = cursor.fetchall()
            return {row["category"]: row["monthly_limit"] for row in rows}

    def get_all_budgets(self) -> List[Budget]:
        """Fetch all budgets sorted by month descending."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM budgets ORDER BY month DESC, category ASC;")
            rows = cursor.fetchall()
            return [
                Budget(
                    id=row["id"],
                    category=row["category"],
                    month=row["month"],
                    monthly_limit=row["monthly_limit"]
                ) for row in rows
            ]

    def delete_budget(self, budget_id: int) -> bool:
        """Delete a budget entry by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM budgets WHERE id = ?;", (budget_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ==========================================
    # CATEGORY OPERATIONS
    # ==========================================

    def get_categories(self) -> List[str]:
        """Return a sorted list of all active categories."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories ORDER BY name ASC;")
            rows = cursor.fetchall()
            return [row["name"] for row in rows]

    def add_category(self, name: str) -> bool:
        """Add a new category if it doesn't already exist."""
        clean_name = name.strip()
        if not clean_name:
            return False
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO categories (name) VALUES (?);", (clean_name,))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def delete_category(self, name: str) -> bool:
        """Delete a category from the categories list."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE name = ?;", (name.strip(),))
            conn.commit()
            return cursor.rowcount > 0

    # ==========================================
    # ANALYTICS & AGGREGATIONS
    # ==========================================

    def get_category_breakdown(self, month: Optional[str] = None) -> List[CategorySummary]:
        """
        Calculate total spent and transaction counts per category.
        If month (YYYY-MM) is provided, filter for that month.
        """
        query = """
            SELECT category, SUM(amount) as total_amount, COUNT(*) as tx_count
            FROM expenses
        """
        params = []
        if month:
            query += " WHERE strftime('%Y-%m', date) = ?"
            params.append(month)
        
        query += " GROUP BY category ORDER BY total_amount DESC;"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            total_sum = sum(row["total_amount"] for row in rows)
            budgets = self.get_budgets_for_month(month) if month else {}

            summaries = []
            for row in rows:
                cat = row["category"]
                spent = row["total_amount"]
                pct = (spent / total_sum * 100.0) if total_sum > 0 else 0.0
                budget_limit = budgets.get(cat)
                used_pct = (spent / budget_limit * 100.0) if budget_limit and budget_limit > 0 else None

                summaries.append(CategorySummary(
                    category=cat,
                    total_amount=round(spent, 2),
                    transaction_count=row["tx_count"],
                    percentage=round(pct, 1),
                    budget_limit=budget_limit,
                    budget_used_percent=round(used_pct, 1) if used_pct is not None else None
                ))
            return summaries

    def get_monthly_totals(self) -> List[Dict[str, Any]]:
        """Fetch total expenditure grouped by month (YYYY-MM)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT strftime('%Y-%m', date) as month, SUM(amount) as total, COUNT(*) as count
                FROM expenses
                GROUP BY strftime('%Y-%m', date)
                ORDER BY month ASC;
            """)
            rows = cursor.fetchall()
            return [{"month": row["month"], "total": round(row["total"], 2), "count": row["count"]} for row in rows]

    def get_daily_spending(self, month: str) -> List[Dict[str, Any]]:
        """Fetch daily spending for a specific month (YYYY-MM)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date, SUM(amount) as total, COUNT(*) as count
                FROM expenses
                WHERE strftime('%Y-%m', date) = ?
                GROUP BY date
                ORDER BY date ASC;
            """, (month,))
            rows = cursor.fetchall()
            return [{"date": row["date"], "total": round(row["total"], 2), "count": row["count"]} for row in rows]

    def get_overall_stats(self) -> Dict[str, Any]:
        """Fetch global summary metrics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_count,
                    COALESCE(SUM(amount), 0) as total_spent,
                    COALESCE(AVG(amount), 0) as avg_expense,
                    COALESCE(MAX(amount), 0) as max_expense,
                    MIN(date) as first_date,
                    MAX(date) as last_date
                FROM expenses;
            """)
            row = cursor.fetchone()
            return {
                "total_count": row["total_count"],
                "total_spent": round(row["total_spent"], 2),
                "avg_expense": round(row["avg_expense"], 2),
                "max_expense": round(row["max_expense"], 2),
                "first_date": row["first_date"],
                "last_date": row["last_date"]
            }
