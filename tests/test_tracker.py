"""
Unit test suite for Expense Tracker core engine.
"""
import unittest
import os
import tempfile
import shutil
from datetime import date
from core.models import Expense, Budget
from core.database import Database
from core.expense_manager import ExpenseManager


class TestExpenseTracker(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for test database and files
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_expenses.db")
        self.manager = ExpenseManager(db_path=self.db_path)

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_add_and_get_expense(self):
        exp_id = self.manager.add_expense(
            title="Grocery Shopping",
            amount=85.50,
            category="Groceries",
            expense_date="2026-08-15",
            payment_method="Credit Card",
            notes="Weekly vegetables and fruits"
        )
        self.assertIsInstance(exp_id, int)
        self.assertGreater(exp_id, 0)

        expense = self.manager.get_expense(exp_id)
        self.assertIsNotNone(expense)
        self.assertEqual(expense.title, "Grocery Shopping")
        self.assertEqual(expense.amount, 85.50)
        self.assertEqual(expense.category, "Groceries")
        self.assertEqual(expense.date, "2026-08-15")
        self.assertEqual(expense.payment_method, "Credit Card")
        self.assertEqual(expense.notes, "Weekly vegetables and fruits")

    def test_invalid_expense_data(self):
        # Empty title
        with self.assertRaises(ValueError):
            self.manager.add_expense(title="", amount=10, category="Food", expense_date="2026-08-15")

        # Negative amount
        with self.assertRaises(ValueError):
            self.manager.add_expense(title="Coffee", amount=-5.0, category="Food", expense_date="2026-08-15")

        # Invalid date format
        with self.assertRaises(ValueError):
            self.manager.add_expense(title="Coffee", amount=5.0, category="Food", expense_date="15-08-2026")

    def test_update_expense(self):
        exp_id = self.manager.add_expense(
            title="Old Title",
            amount=20.0,
            category="Food & Dining",
            expense_date="2026-08-10"
        )
        updated = self.manager.update_expense(
            expense_id=exp_id,
            title="New Title",
            amount=25.0,
            category="Food & Dining",
            expense_date="2026-08-11",
            payment_method="Cash",
            notes="Updated note"
        )
        self.assertTrue(updated)
        expense = self.manager.get_expense(exp_id)
        self.assertEqual(expense.title, "New Title")
        self.assertEqual(expense.amount, 25.0)
        self.assertEqual(expense.date, "2026-08-11")
        self.assertEqual(expense.notes, "Updated note")

    def test_delete_expense(self):
        exp_id = self.manager.add_expense(
            title="To be deleted",
            amount=12.0,
            category="Entertainment",
            expense_date="2026-08-01"
        )
        self.assertTrue(self.manager.delete_expense(exp_id))
        self.assertIsNone(self.manager.get_expense(exp_id))

    def test_filter_expenses(self):
        self.manager.add_expense("Lunch", 15.0, "Food & Dining", "2026-08-01", "Cash")
        self.manager.add_expense("Dinner", 45.0, "Food & Dining", "2026-08-05", "Credit Card")
        self.manager.add_expense("Metro Pass", 30.0, "Transportation", "2026-08-10", "UPI / Online Transfer")
        self.manager.add_expense("Movie Ticket", 18.0, "Entertainment", "2026-08-12", "Debit Card")

        # Filter by category
        food_items = self.manager.filter_expenses(category="Food & Dining")
        self.assertEqual(len(food_items), 2)

        # Filter by date range
        range_items = self.manager.filter_expenses(start_date="2026-08-05", end_date="2026-08-11")
        self.assertEqual(len(range_items), 2)

        # Filter by search query
        search_items = self.manager.filter_expenses(search_query="Metro")
        self.assertEqual(len(search_items), 1)
        self.assertEqual(search_items[0].title, "Metro Pass")

        # Filter by amount range
        amount_items = self.manager.filter_expenses(min_amount=20.0, max_amount=40.0)
        self.assertEqual(len(amount_items), 1)
        self.assertEqual(amount_items[0].amount, 30.0)

    def test_budget_management_and_alerts(self):
        self.manager.set_budget("Food & Dining", "2026-08", 200.0)
        self.manager.set_budget("Shopping", "2026-08", 100.0)

        # Add expenses
        self.manager.add_expense("Dining Out", 170.0, "Food & Dining", "2026-08-05")  # 85% -> Warning
        self.manager.add_expense("Clothes", 120.0, "Shopping", "2026-08-06")        # 120% -> Exceeded

        alerts = self.manager.check_budget_alerts(month="2026-08", warning_threshold=80.0)
        self.assertEqual(len(alerts), 2)

        exceeded = [a for a in alerts if a["status"] == "EXCEEDED"]
        warnings = [a for a in alerts if a["status"] == "WARNING"]

        self.assertEqual(len(exceeded), 1)
        self.assertEqual(exceeded[0]["category"], "Shopping")

        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["category"], "Food & Dining")

    def test_monthly_report_and_breakdown(self):
        self.manager.add_expense("Rent", 1000.0, "Housing & Rent", "2026-08-01")
        self.manager.add_expense("Electricity", 150.0, "Utilities", "2026-08-05")
        self.manager.add_expense("Internet", 50.0, "Utilities", "2026-08-10")

        report = self.manager.generate_monthly_report(month="2026-08")
        self.assertEqual(report.total_spent, 1200.0)
        self.assertEqual(report.top_category, "Housing & Rent")
        self.assertEqual(report.transaction_count, 3)

        breakdown = self.manager.get_category_breakdown(month="2026-08")
        self.assertEqual(len(breakdown), 2)
        housing = next(b for b in breakdown if b.category == "Housing & Rent")
        self.assertEqual(housing.total_amount, 1000.0)
        self.assertAlmostEqual(housing.percentage, 83.3, places=1)

    def test_csv_export_and_import(self):
        self.manager.add_expense("Item A", 25.0, "Groceries", "2026-08-01", "Cash", "Note A")
        self.manager.add_expense("Item B", 75.0, "Utilities", "2026-08-02", "Credit Card", "Note B")

        csv_file = os.path.join(self.test_dir, "exported_expenses.csv")
        count = self.manager.export_to_csv(csv_file)
        self.assertEqual(count, 2)
        self.assertTrue(os.path.exists(csv_file))

        # Test importing into a fresh database instance
        new_db_path = os.path.join(self.test_dir, "imported_expenses.db")
        new_manager = ExpenseManager(db_path=new_db_path)

        success, errors, msgs = new_manager.import_from_csv(csv_file)
        self.assertEqual(success, 2)
        self.assertEqual(errors, 0)
        self.assertEqual(len(new_manager.get_all_expenses()), 2)

    def test_category_management(self):
        self.assertTrue(self.manager.add_category("Gym & Fitness"))
        self.assertIn("Gym & Fitness", self.manager.get_categories())
        # Duplicate should return False
        self.assertFalse(self.manager.add_category("Gym & Fitness"))
        # Delete category
        self.assertTrue(self.manager.delete_category("Gym & Fitness"))
        self.assertNotIn("Gym & Fitness", self.manager.get_categories())


if __name__ == "__main__":
    unittest.main()
