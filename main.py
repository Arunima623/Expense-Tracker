"""
Unified Launcher for the Python Expense Tracker Application.
"""
import sys
import os
import argparse
import subprocess


def launch_gui():
    """Launch the Tkinter Desktop GUI."""
    from gui import ModernExpenseApp
    app = ModernExpenseApp()
    app.mainloop()


def launch_cli():
    """Launch the Command-Line Interface."""
    from cli import ExpenseCLI
    cli = ExpenseCLI()
    cli.run()


def launch_web():
    """Launch the Streamlit Web Application."""
    print("Launching Streamlit Web Dashboard...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])


def seed_data():
    """Seed sample data."""
    from sample_data import seed_sample_data
    seed_sample_data()


def run_tests():
    """Execute unit test suite."""
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])


def interactive_launcher():
    """Interactive launcher menu if no flags provided."""
    print("=" * 60)
    print("       💰 PYTHON EXPENSE TRACKER & BUDGET MANAGER 💰        ")
    print("=" * 60)
    print("Choose how you would like to run the Expense Tracker:")
    print("  [1] Modern Desktop GUI (Tkinter Desktop App)")
    print("  [2] Interactive Web Dashboard (Streamlit Browser App)")
    print("  [3] Command-Line Interface (CLI Terminal)")
    print("  [4] Populate Sample Demo Data")
    print("  [5] Run Automated Test Suite")
    print("  [0] Exit")
    print("-" * 60)

    choice = input("Enter choice [1-5, 0 to exit] (Default: 1): ").strip()

    if choice == "2":
        launch_web()
    elif choice == "3":
        launch_cli()
    elif choice == "4":
        seed_data()
    elif choice == "5":
        run_tests()
    elif choice == "0":
        sys.exit(0)
    else:
        # Default to GUI
        launch_gui()


def main():
    parser = argparse.ArgumentParser(description="Python Expense Tracker & Budget Manager")
    parser.add_argument("--gui", action="store_true", help="Launch Desktop GUI")
    parser.add_argument("--web", action="store_true", help="Launch Streamlit Web App")
    parser.add_argument("--cli", action="store_true", help="Launch Terminal CLI")
    parser.add_argument("--seed", action="store_true", help="Populate sample demo data")
    parser.add_argument("--test", action="store_true", help="Run automated test suite")

    args = parser.parse_args()

    if args.gui:
        launch_gui()
    elif args.web:
        launch_web()
    elif args.cli:
        launch_cli()
    elif args.seed:
        seed_data()
    elif args.test:
        run_tests()
    else:
        interactive_launcher()


if __name__ == "__main__":
    main()
