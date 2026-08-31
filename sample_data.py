"""
Utility script to seed demo data into the Expense Tracker database.
"""
from datetime import date, timedelta
import random
from core.expense_manager import ExpenseManager


def seed_sample_data(db_path: str = "expenses.db"):
    """Populate realistic sample expenses and budgets."""
    manager = ExpenseManager(db_path=db_path)
    
    # Check if there are already records
    existing = manager.get_all_expenses()
    if len(existing) > 0:
        print(f"Database '{db_path}' already contains {len(existing)} records.")
        return

    print("Generating sample expenses and budgets...")
    today = date.today()
    current_month = today.strftime("%Y-%m")

    # Set some budgets for current month
    manager.set_budget("Food & Dining", current_month, 400.0)
    manager.set_budget("Groceries", current_month, 500.0)
    manager.set_budget("Entertainment", current_month, 150.0)
    manager.set_budget("Shopping", current_month, 250.0)
    manager.set_budget("Utilities", current_month, 300.0)
    manager.set_budget("Transportation", current_month, 200.0)

    sample_items = [
        # (title, min_price, max_price, category, payment_methods, notes)
        ("Whole Foods Market", 45.0, 120.0, "Groceries", ["Credit Card", "Debit Card"], "Weekly grocery shopping"),
        ("Trader Joe's", 25.0, 75.0, "Groceries", ["Credit Card", "Cash"], "Snacks and produce"),
        ("Starbucks Coffee", 4.5, 9.5, "Food & Dining", ["UPI / Online Transfer", "Credit Card"], "Morning latte & muffin"),
        ("Italian Bistro Dinner", 45.0, 95.0, "Food & Dining", ["Credit Card"], "Dinner with friends"),
        ("Chipotle Mexican Grill", 12.0, 18.0, "Food & Dining", ["Debit Card", "Cash"], "Lunch burrito bowl"),
        ("Apartment Rent", 1200.0, 1200.0, "Housing & Rent", ["Net Banking", "UPI / Online Transfer"], "Monthly apartment rent"),
        ("Electricity Bill", 65.0, 110.0, "Utilities", ["UPI / Online Transfer", "Net Banking"], "Monthly power utility"),
        ("Water & Sewage", 30.0, 45.0, "Utilities", ["UPI / Online Transfer"], "Municipal water bill"),
        ("High-Speed Internet", 60.0, 60.0, "Utilities", ["Credit Card"], "Fiber internet subscription"),
        ("Gas Station Fill-up", 35.0, 60.0, "Transportation", ["Credit Card", "Debit Card"], "Gasoline for commute"),
        ("Subway / Metro Pass", 40.0, 70.0, "Transportation", ["Debit Card"], "Monthly transit pass"),
        ("Uber / Lyft Ride", 14.0, 32.0, "Transportation", ["Credit Card"], "Airport commute"),
        ("Cinema Movie Tickets", 24.0, 36.0, "Entertainment", ["Credit Card"], "Weekend IMAX movie"),
        ("Netflix & Spotify", 25.0, 25.0, "Entertainment", ["Credit Card"], "Monthly streaming services"),
        ("Amazon Online Purchase", 20.0, 110.0, "Shopping", ["Credit Card"], "Household essentials"),
        ("Pharmacy / Medicines", 15.0, 45.0, "Healthcare", ["Debit Card", "Cash"], "Vitamins and prescription"),
        ("Books & Online Course", 29.0, 85.0, "Education", ["Credit Card", "UPI / Online Transfer"], "Python & Data mastery course"),
    ]

    total_added = 0
    # Generate transactions over the past 45 days
    for days_ago in range(45, -1, -1):
        tx_date = today - timedelta(days=days_ago)
        date_str = tx_date.strftime("%Y-%m-%d")

        # Rent on 1st of each month
        if tx_date.day == 1:
            manager.add_expense(
                title="Monthly Apartment Rent",
                amount=1200.0,
                category="Housing & Rent",
                expense_date=date_str,
                payment_method="Net Banking",
                notes="Primary residence rent"
            )
            total_added += 1

        # Random transactions for the day
        num_tx = random.choices([0, 1, 2, 3], weights=[0.3, 0.4, 0.2, 0.1])[0]
        for _ in range(num_tx):
            item = random.choice(sample_items)
            if item[0] == "Apartment Rent":
                continue  # Handled above
            amount = round(random.uniform(item[1], item[2]), 2)
            payment = random.choice(item[4])
            manager.add_expense(
                title=item[0],
                amount=amount,
                category=item[3],
                expense_date=date_str,
                payment_method=payment,
                notes=item[5]
            )
            total_added += 1

    print(f"Successfully seeded {total_added} sample transactions into '{db_path}'!")


if __name__ == "__main__":
    seed_sample_data()
