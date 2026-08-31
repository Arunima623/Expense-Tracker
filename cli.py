"""
Interactive Command-Line Interface (CLI) for the Expense Tracker.
"""
import sys
import os
from datetime import datetime, date
from typing import List, Optional
from core.expense_manager import ExpenseManager
from core.models import Expense


# ANSI Color Codes for beautiful terminal styling
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def clear_screen():
    """Clear terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 64)
    print("        💰 PERSONAL EXPENSE TRACKER & BUDGET MANAGER 💰        ")
    print("=" * 64)
    print(f"{Colors.END}")


def print_table(headers: List[str], rows: List[List[str]], alignments: Optional[List[str]] = None):
    """Print an aligned ASCII table."""
    if not rows:
        print(f"{Colors.YELLOW}No records found.{Colors.END}\n")
        return

    num_cols = len(headers)
    aligns = alignments or ["left"] * num_cols
    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    # Separator line
    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"

    # Print header
    print(sep)
    header_cells = []
    for h, w in zip(headers, col_widths):
        header_cells.append(f"{h:<{w}}")
    print(f"| {Colors.BOLD}" + " | ".join(header_cells) + f"{Colors.END} |")
    print(sep)

    # Print rows
    for row in rows:
        cells = []
        for i, (val, w) in enumerate(zip(row, col_widths)):
            val_str = str(val)
            if aligns[i] == "right":
                cells.append(f"{val_str:>{w}}")
            else:
                cells.append(f"{val_str:<{w}}")
        print("| " + " | ".join(cells) + " |")

    print(sep + "\n")


class ExpenseCLI:
    def __init__(self, db_path: str = "expenses.db"):
        self.manager = ExpenseManager(db_path=db_path)

    def run(self):
        """Main CLI loop."""
        while True:
            print_banner()
            self._display_quick_summary()
            print(f"{Colors.BOLD}Select an Option:{Colors.END}")
            print(f"  [{Colors.GREEN}1{Colors.END}] Add New Expense")
            print(f"  [{Colors.GREEN}2{Colors.END}] View Recent Expenses")
            print(f"  [{Colors.GREEN}3{Colors.END}] Search & Filter Expenses")
            print(f"  [{Colors.GREEN}4{Colors.END}] Edit / Delete an Expense")
            print(f"  [{Colors.GREEN}5{Colors.END}] Monthly Analytics & Category Breakdown")
            print(f"  [{Colors.GREEN}6{Colors.END}] Manage Category Budgets & Alerts")
            print(f"  [{Colors.GREEN}7{Colors.END}] Manage Categories")
            print(f"  [{Colors.GREEN}8{Colors.END}] Export / Import CSV")
            print(f"  [{Colors.GREEN}9{Colors.END}] Load Sample Demo Data")
            print(f"  [{Colors.RED}0{Colors.END}] Exit")
            print("-" * 64)

            choice = input(f"{Colors.BOLD}Enter your choice [0-9]: {Colors.END}").strip()

            if choice == "1":
                self.add_expense_menu()
            elif choice == "2":
                self.view_expenses_menu()
            elif choice == "3":
                self.filter_expenses_menu()
            elif choice == "4":
                self.edit_delete_menu()
            elif choice == "5":
                self.monthly_analytics_menu()
            elif choice == "6":
                self.budget_menu()
            elif choice == "7":
                self.category_menu()
            elif choice == "8":
                self.export_import_menu()
            elif choice == "9":
                self.load_sample_data_menu()
            elif choice == "0":
                print(f"\n{Colors.GREEN}Thank you for using Expense Tracker! Goodbye! 👋{Colors.END}\n")
                sys.exit(0)
            else:
                input(f"{Colors.RED}Invalid choice. Press Enter to continue...{Colors.END}")

    def _display_quick_summary(self):
        """Display quick spending stats and budget alerts on home screen."""
        current_month = date.today().strftime("%Y-%m")
        report = self.manager.generate_monthly_report(current_month)
        alerts = self.manager.check_budget_alerts(current_month)

        print(f"📅 Current Month: {Colors.BOLD}{current_month}{Colors.END} | Total Spent: {Colors.BOLD}${report.total_spent:,.2f}{Colors.END} ({report.transaction_count} transactions)")
        if report.top_category:
            print(f"🔥 Top Category: {Colors.CYAN}{report.top_category}{Colors.END} | Daily Avg: ${report.daily_average:,.2f}/day")
        
        if alerts:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  BUDGET ALERTS ({len(alerts)}):{Colors.END}")
            for a in alerts:
                color = Colors.RED if a["status"] == "EXCEEDED" else Colors.YELLOW
                print(f"  {color}• {a['message']}{Colors.END}")
        print("-" * 64)

    def add_expense_menu(self):
        """Prompt user to add an expense."""
        print(f"\n{Colors.BOLD}{Colors.GREEN}--- Add New Expense ---{Colors.END}")
        title = input("Enter Title / Description: ").strip()
        if not title:
            print(f"{Colors.RED}Title cannot be empty.{Colors.END}")
            input("Press Enter to return...")
            return

        while True:
            amount_str = input("Enter Amount ($): ").strip().replace("$", "")
            try:
                amount = float(amount_str)
                if amount <= 0:
                    print(f"{Colors.RED}Amount must be greater than 0.{Colors.END}")
                    continue
                break
            except ValueError:
                print(f"{Colors.RED}Invalid number. Please enter a valid amount.{Colors.END}")

        # Choose Category
        categories = self.manager.get_categories()
        print("\nSelect Category:")
        for idx, cat in enumerate(categories, 1):
            print(f"  [{idx}] {cat}")
        while True:
            cat_choice = input(f"Enter category number [1-{len(categories)}] (or type custom name): ").strip()
            if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                category = categories[int(cat_choice) - 1]
                break
            elif cat_choice:
                category = cat_choice
                self.manager.add_category(category)
                break

        # Date
        today_str = date.today().strftime("%Y-%m-%d")
        exp_date = input(f"Enter Date (YYYY-MM-DD) [Default: {today_str}]: ").strip()
        if not exp_date:
            exp_date = today_str
        else:
            try:
                datetime.strptime(exp_date, "%Y-%m-%d")
            except ValueError:
                print(f"{Colors.RED}Invalid date format. Using today's date.{Colors.END}")
                exp_date = today_str

        # Payment Method
        pm_list = self.manager.get_payment_methods()
        print("\nSelect Payment Method:")
        for idx, pm in enumerate(pm_list, 1):
            print(f"  [{idx}] {pm}")
        pm_choice = input(f"Enter payment method [1-{len(pm_list)}] [Default: 1]: ").strip()
        if pm_choice.isdigit() and 1 <= int(pm_choice) <= len(pm_list):
            payment_method = pm_list[int(pm_choice) - 1]
        else:
            payment_method = pm_list[0]

        notes = input("Enter Notes / Tags (optional): ").strip()

        try:
            exp_id = self.manager.add_expense(
                title=title,
                amount=amount,
                category=category,
                expense_date=exp_date,
                payment_method=payment_method,
                notes=notes
            )
            print(f"\n{Colors.GREEN}✓ Expense recorded successfully! (ID: {exp_id}){Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}Error adding expense: {e}{Colors.END}")
        
        input("\nPress Enter to return to main menu...")

    def view_expenses_menu(self):
        """Display recent expenses."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}--- Recent Expenses ---{Colors.END}")
        expenses = self.manager.get_all_expenses()
        self._render_expense_table(expenses)
        input("Press Enter to return to main menu...")

    def filter_expenses_menu(self):
        """Filter expenses by date, category, search term."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}--- Search & Filter Expenses ---{Colors.END}")
        print("Leave any field blank to skip filtering.")
        
        start_date = input("Start Date (YYYY-MM-DD): ").strip() or None
        end_date = input("End Date (YYYY-MM-DD): ").strip() or None
        category = input("Category: ").strip() or None
        search_query = input("Search Keyword (title/notes): ").strip() or None

        results = self.manager.filter_expenses(
            start_date=start_date,
            end_date=end_date,
            category=category,
            search_query=search_query
        )

        total_filtered = sum(e.amount for e in results)
        print(f"\nFound {len(results)} transactions | Total: {Colors.BOLD}${total_filtered:,.2f}{Colors.END}\n")
        self._render_expense_table(results)
        input("Press Enter to return to main menu...")

    def edit_delete_menu(self):
        """Edit or delete an existing expense."""
        print(f"\n{Colors.BOLD}{Colors.YELLOW}--- Edit / Delete Expense ---{Colors.END}")
        id_str = input("Enter Expense ID to modify: ").strip()
        if not id_str.isdigit():
            print(f"{Colors.RED}Invalid ID.{Colors.END}")
            input("Press Enter...")
            return

        exp_id = int(id_str)
        expense = self.manager.get_expense(exp_id)
        if not expense:
            print(f"{Colors.RED}Expense with ID {exp_id} not found.{Colors.END}")
            input("Press Enter...")
            return

        print(f"\nSelected Expense: ID {expense.id} | {expense.title} | ${expense.amount:.2f} | {expense.category} | {expense.date}")
        print("  [1] Edit Expense")
        print("  [2] Delete Expense")
        print("  [0] Cancel")
        action = input("Select action [0-2]: ").strip()

        if action == "2":
            confirm = input(f"{Colors.RED}Are you sure you want to delete ID {exp_id}? (y/N): {Colors.END}").strip().lower()
            if confirm == "y":
                if self.manager.delete_expense(exp_id):
                    print(f"{Colors.GREEN}✓ Expense deleted successfully.{Colors.END}")
                else:
                    print(f"{Colors.RED}Failed to delete expense.{Colors.END}")
        elif action == "1":
            print("\nEnter new values (press Enter to keep current value):")
            new_title = input(f"Title [{expense.title}]: ").strip() or expense.title
            
            amount_input = input(f"Amount [${expense.amount:.2f}]: ").strip().replace("$", "")
            new_amount = float(amount_input) if amount_input else expense.amount

            new_cat = input(f"Category [{expense.category}]: ").strip() or expense.category
            new_date = input(f"Date [{expense.date}]: ").strip() or expense.date
            new_pm = input(f"Payment Method [{expense.payment_method}]: ").strip() or expense.payment_method
            new_notes = input(f"Notes [{expense.notes}]: ").strip() or expense.notes

            try:
                self.manager.update_expense(
                    expense_id=exp_id,
                    title=new_title,
                    amount=new_amount,
                    category=new_cat,
                    expense_date=new_date,
                    payment_method=new_pm,
                    notes=new_notes
                )
                print(f"{Colors.GREEN}✓ Expense updated successfully!{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}Error updating expense: {e}{Colors.END}")

        input("\nPress Enter to continue...")

    def monthly_analytics_menu(self):
        """Show monthly spending analysis and category distribution."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}--- Monthly Financial Analytics ---{Colors.END}")
        month_str = input(f"Enter Month (YYYY-MM) [Default: {date.today().strftime('%Y-%m')}]: ").strip()
        target_month = month_str or date.today().strftime("%Y-%m")

        report = self.manager.generate_monthly_report(target_month)
        print(f"\n{Colors.BOLD}📊 Report for {report.month}:{Colors.END}")
        print(f"  • Total Spent: {Colors.BOLD}${report.total_spent:,.2f}{Colors.END}")
        print(f"  • Total Budgeted: ${report.total_budget:,.2f}")
        print(f"  • Total Transactions: {report.transaction_count}")
        print(f"  • Daily Spending Average: ${report.daily_average:,.2f}/day\n")

        # Category Breakdown Table
        headers = ["Category", "Spent ($)", "% Total", "Budget ($)", "Budget Used %"]
        rows = []
        for cat in report.category_summaries:
            budget_str = f"${cat.budget_limit:,.2f}" if cat.budget_limit else "-"
            used_str = f"{cat.budget_used_percent:.1f}%" if cat.budget_used_percent is not None else "-"
            rows.append([
                cat.category,
                f"${cat.total_amount:,.2f}",
                f"{cat.percentage:.1f}%",
                budget_str,
                used_str
            ])

        print(f"{Colors.BOLD}Category Distribution:{Colors.END}")
        print_table(headers, rows, alignments=["left", "right", "right", "right", "right"])
        input("Press Enter to return...")

    def budget_menu(self):
        """Manage category budgets."""
        print(f"\n{Colors.BOLD}{Colors.YELLOW}--- Category Budgets & Alerts ---{Colors.END}")
        target_month = date.today().strftime("%Y-%m")
        budgets = self.manager.get_all_budgets()

        if budgets:
            headers = ["ID", "Category", "Month", "Limit ($)"]
            rows = [[str(b.id), b.category, b.month, f"${b.monthly_limit:,.2f}"] for b in budgets]
            print_table(headers, rows)
        else:
            print("No budgets configured yet.\n")

        print("Options: [1] Set/Update Budget  [2] Delete Budget  [0] Back")
        b_choice = input("Select option [0-2]: ").strip()
        if b_choice == "1":
            cat = input("Enter Category: ").strip()
            month = input(f"Enter Month (YYYY-MM) [Default: {target_month}]: ").strip() or target_month
            amount_str = input("Enter Monthly Budget Limit ($): ").strip().replace("$", "")
            try:
                limit = float(amount_str)
                self.manager.set_budget(cat, month, limit)
                print(f"{Colors.GREEN}✓ Budget saved for {cat} ({month}): ${limit:,.2f}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}Error setting budget: {e}{Colors.END}")
        elif b_choice == "2":
            b_id = input("Enter Budget ID to delete: ").strip()
            if b_id.isdigit() and self.manager.delete_budget(int(b_id)):
                print(f"{Colors.GREEN}✓ Budget deleted.{Colors.END}")
            else:
                print(f"{Colors.RED}Failed to delete budget.{Colors.END}")

        input("\nPress Enter to continue...")

    def category_menu(self):
        """Manage categories."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}--- Manage Categories ---{Colors.END}")
        categories = self.manager.get_categories()
        for idx, cat in enumerate(categories, 1):
            print(f"  {idx}. {cat}")
        
        print("\nOptions: [1] Add Category  [2] Delete Category  [0] Back")
        c_choice = input("Select option [0-2]: ").strip()
        if c_choice == "1":
            name = input("New category name: ").strip()
            if self.manager.add_category(name):
                print(f"{Colors.GREEN}✓ Category '{name}' added.{Colors.END}")
            else:
                print(f"{Colors.RED}Category already exists or is invalid.{Colors.END}")
        elif c_choice == "2":
            name = input("Category name to remove: ").strip()
            if self.manager.delete_category(name):
                print(f"{Colors.GREEN}✓ Category '{name}' removed.{Colors.END}")
            else:
                print(f"{Colors.RED}Category not found.{Colors.END}")
        input("\nPress Enter to continue...")

    def export_import_menu(self):
        """Export or import CSV files."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}--- Export / Import CSV ---{Colors.END}")
        print("  [1] Export expenses to CSV")
        print("  [2] Import expenses from CSV")
        print("  [0] Back")
        opt = input("Select option [0-2]: ").strip()

        if opt == "1":
            default_path = f"expenses_export_{date.today().strftime('%Y%m%d')}.csv"
            filepath = input(f"Enter output file path [Default: {default_path}]: ").strip() or default_path
            count = self.manager.export_to_csv(filepath)
            print(f"{Colors.GREEN}✓ Successfully exported {count} transactions to '{filepath}'.{Colors.END}")
        elif opt == "2":
            filepath = input("Enter path to CSV file to import: ").strip()
            if os.path.exists(filepath):
                success, errors, msgs = self.manager.import_from_csv(filepath)
                print(f"{Colors.GREEN}✓ Successfully imported {success} transactions.{Colors.END}")
                if errors > 0:
                    print(f"{Colors.RED}⚠️ {errors} rows failed to import:{Colors.END}")
                    for m in msgs[:5]:
                        print(f"  • {m}")
            else:
                print(f"{Colors.RED}File not found.{Colors.END}")
        input("\nPress Enter to continue...")

    def load_sample_data_menu(self):
        """Seed sample demo transactions."""
        from sample_data import seed_sample_data
        seed_sample_data(self.manager.db.db_path)
        input("\nPress Enter to continue...")

    def _render_expense_table(self, expenses: List[Expense]):
        """Helper to render a formatted table of expenses."""
        headers = ["ID", "Date", "Title", "Amount ($)", "Category", "Payment", "Notes"]
        rows = [
            [
                str(e.id),
                e.date,
                e.title[:25] + ("..." if len(e.title) > 25 else ""),
                f"${e.amount:,.2f}",
                e.category,
                e.payment_method,
                e.notes[:20] + ("..." if len(e.notes) > 20 else "")
            ] for e in expenses
        ]
        print_table(headers, rows, alignments=["left", "left", "left", "right", "left", "left", "left"])


if __name__ == "__main__":
    cli = ExpenseCLI()
    cli.run()
