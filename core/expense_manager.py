"""
Business logic and high-level manager for the Expense Tracker.
"""
import csv
import json
import os
from datetime import datetime, date
import calendar
from typing import List, Optional, Dict, Any, Tuple
from .models import Expense, Budget, CategorySummary, MonthlyReport, DEFAULT_CATEGORIES, DEFAULT_PAYMENT_METHODS
from .database import Database


class ExpenseManager:
    """Provides high-level business operations, analytics, budget alerting, and file I/O."""

    def __init__(self, db_path: str = "expenses.db"):
        self.db = Database(db_path=db_path)

    # -------------------------------------------------------------
    # Expense Operations
    # -------------------------------------------------------------
    def add_expense(
        self,
        title: str,
        amount: float,
        category: str,
        expense_date: Optional[str] = None,
        payment_method: str = "Cash",
        notes: str = ""
    ) -> int:
        """Validate and add a new expense."""
        if expense_date is None or not expense_date.strip():
            expense_date = date.today().strftime("%Y-%m-%d")

        expense = Expense(
            title=title,
            amount=float(amount),
            category=category,
            date=expense_date,
            payment_method=payment_method,
            notes=notes
        )
        return self.db.add_expense(expense)

    def update_expense(
        self,
        expense_id: int,
        title: str,
        amount: float,
        category: str,
        expense_date: str,
        payment_method: str = "Cash",
        notes: str = ""
    ) -> bool:
        """Update an existing expense by ID."""
        expense = Expense(
            id=expense_id,
            title=title,
            amount=float(amount),
            category=category,
            date=expense_date,
            payment_method=payment_method,
            notes=notes
        )
        return self.db.update_expense(expense)

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense by ID."""
        return self.db.delete_expense(expense_id)

    def get_expense(self, expense_id: int) -> Optional[Expense]:
        """Fetch an expense by ID."""
        return self.db.get_expense_by_id(expense_id)

    def get_all_expenses(self, order_by: str = "date DESC, id DESC") -> List[Expense]:
        """Retrieve all expenses."""
        return self.db.get_all_expenses(order_by=order_by)

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
        """Filter transactions based on criteria."""
        return self.db.filter_expenses(
            start_date=start_date,
            end_date=end_date,
            category=category,
            payment_method=payment_method,
            search_query=search_query,
            min_amount=min_amount,
            max_amount=max_amount
        )

    # -------------------------------------------------------------
    # Categories & Budgets
    # -------------------------------------------------------------
    def get_categories(self) -> List[str]:
        """Get all available expense categories."""
        return self.db.get_categories()

    def add_category(self, name: str) -> bool:
        """Add a custom category."""
        return self.db.add_category(name)

    def delete_category(self, name: str) -> bool:
        """Delete a category."""
        return self.db.delete_category(name)

    def get_payment_methods(self) -> List[str]:
        """Get standard payment methods."""
        return DEFAULT_PAYMENT_METHODS

    def set_budget(self, category: str, month: str, limit_amount: float) -> int:
        """Set or update budget for a category in month YYYY-MM."""
        return self.db.set_budget(category, month, float(limit_amount))

    def get_budgets_for_month(self, month: str) -> Dict[str, float]:
        """Get budget limit map for month."""
        return self.db.get_budgets_for_month(month)

    def get_all_budgets(self) -> List[Budget]:
        """Get all configured budgets."""
        return self.db.get_all_budgets()

    def delete_budget(self, budget_id: int) -> bool:
        """Delete a budget entry."""
        return self.db.delete_budget(budget_id)

    def check_budget_alerts(self, month: Optional[str] = None, warning_threshold: float = 80.0) -> List[Dict[str, Any]]:
        """
        Check which categories have reached or exceeded budget limits for a given month.
        Returns a list of alert dicts with category, spent, limit, percentage, status.
        """
        target_month = month or date.today().strftime("%Y-%m")
        summaries = self.db.get_category_breakdown(month=target_month)
        alerts = []

        for summary in summaries:
            if summary.budget_limit and summary.budget_limit > 0:
                used_pct = (summary.total_amount / summary.budget_limit) * 100.0
                if used_pct >= 100.0:
                    alerts.append({
                        "category": summary.category,
                        "spent": summary.total_amount,
                        "limit": summary.budget_limit,
                        "percentage": round(used_pct, 1),
                        "status": "EXCEEDED",
                        "severity": "danger",
                        "message": f"Budget exceeded for {summary.category}! Spent ${summary.total_amount:.2f} of ${summary.budget_limit:.2f} ({used_pct:.1f}%)"
                    })
                elif used_pct >= warning_threshold:
                    alerts.append({
                        "category": summary.category,
                        "spent": summary.total_amount,
                        "limit": summary.budget_limit,
                        "percentage": round(used_pct, 1),
                        "status": "WARNING",
                        "severity": "warning",
                        "message": f"Approaching budget limit for {summary.category}. Spent ${summary.total_amount:.2f} of ${summary.budget_limit:.2f} ({used_pct:.1f}%)"
                    })
        return alerts

    # -------------------------------------------------------------
    # Reports and Analytics
    # -------------------------------------------------------------
    def generate_monthly_report(self, month: Optional[str] = None) -> MonthlyReport:
        """Generate a complete financial report for the specified month (YYYY-MM)."""
        target_month = month or date.today().strftime("%Y-%m")
        year, month_num = map(int, target_month.split("-"))
        _, days_in_month = calendar.monthrange(year, month_num)

        summaries = self.db.get_category_breakdown(month=target_month)
        total_spent = sum(s.total_amount for s in summaries)
        tx_count = sum(s.transaction_count for s in summaries)
        budgets = self.db.get_budgets_for_month(target_month)
        total_budget = sum(budgets.values())

        # Calculate daily average
        today = date.today()
        if today.year == year and today.month == month_num:
            days_passed = max(1, today.day)
        else:
            days_passed = days_in_month
        daily_average = round(total_spent / days_passed, 2) if days_passed > 0 else 0.0

        # Top category
        top_category = summaries[0].category if summaries else None

        return MonthlyReport(
            month=target_month,
            total_spent=round(total_spent, 2),
            total_budget=round(total_budget, 2),
            daily_average=daily_average,
            category_summaries=summaries,
            top_category=top_category,
            transaction_count=tx_count
        )

    def get_monthly_trends(self) -> List[Dict[str, Any]]:
        """Get monthly spending totals."""
        return self.db.get_monthly_totals()

    def get_category_breakdown(self, month: Optional[str] = None) -> List[CategorySummary]:
        """Get category breakdown for a month or all-time."""
        return self.db.get_category_breakdown(month=month)

    def get_daily_spending(self, month: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get daily spending for a month."""
        target_month = month or date.today().strftime("%Y-%m")
        return self.db.get_daily_spending(month=target_month)

    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall metrics."""
        return self.db.get_overall_stats()

    # -------------------------------------------------------------
    # Data Import & Export (CSV & JSON)
    # -------------------------------------------------------------
    def export_to_csv(self, filepath: str, expenses: Optional[List[Expense]] = None) -> int:
        """Export expenses list to a CSV file. Returns number of rows exported."""
        items = expenses if expenses is not None else self.get_all_expenses()
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Title", "Amount", "Category", "Date", "Payment Method", "Notes", "Created At"])
            for e in items:
                writer.writerow([
                    e.id,
                    e.title,
                    f"{e.amount:.2f}",
                    e.category,
                    e.date,
                    e.payment_method,
                    e.notes,
                    e.created_at or ""
                ])
        return len(items)

    def import_from_csv(self, filepath: str) -> Tuple[int, int, List[str]]:
        """
        Import expenses from a CSV file.
        Expected headers (case-insensitive): Title, Amount, Category, Date (optional: Payment Method, Notes).
        Returns: (success_count, error_count, error_messages)
        """
        if not os.path.exists(filepath):
            return 0, 1, [f"File '{filepath}' not found."]

        success_count = 0
        error_count = 0
        errors: List[str] = []

        with open(filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return 0, 1, ["CSV file is empty or has no header row."]

            # Normalize headers
            headers = {h.strip().lower(): h for h in reader.fieldnames if h}

            title_col = headers.get("title")
            amount_col = headers.get("amount")
            cat_col = headers.get("category")
            date_col = headers.get("date")
            pm_col = headers.get("payment method") or headers.get("payment_method") or headers.get("payment")
            notes_col = headers.get("notes") or headers.get("description")

            if not (title_col and amount_col and cat_col):
                return 0, 1, ["CSV must contain at least 'Title', 'Amount', and 'Category' columns."]

            for row_idx, row in enumerate(reader, start=2):
                try:
                    title = row.get(title_col, "").strip()
                    amount_str = row.get(amount_col, "").strip()
                    category = row.get(cat_col, "").strip()
                    exp_date = row.get(date_col, "").strip() if date_col else date.today().strftime("%Y-%m-%d")
                    payment_method = row.get(pm_col, "Cash").strip() if pm_col else "Cash"
                    notes = row.get(notes_col, "").strip() if notes_col else ""

                    if not title or not amount_str or not category:
                        raise ValueError("Missing title, amount, or category.")

                    amount = float(amount_str.replace("$", "").replace(",", ""))
                    
                    # Normalize date if necessary
                    if not exp_date:
                        exp_date = date.today().strftime("%Y-%m-%d")
                    else:
                        # Attempt common date formats
                        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
                            try:
                                dt = datetime.strptime(exp_date, fmt)
                                exp_date = dt.strftime("%Y-%m-%d")
                                break
                            except ValueError:
                                pass

                    self.add_expense(
                        title=title,
                        amount=amount,
                        category=category,
                        expense_date=exp_date,
                        payment_method=payment_method or "Cash",
                        notes=notes
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {row_idx}: {str(e)}")

        return success_count, error_count, errors

    def export_to_json(self, filepath: str) -> int:
        """Export all expenses to a JSON file."""
        expenses = self.get_all_expenses()
        data = [e.to_dict() for e in expenses]
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return len(data)
