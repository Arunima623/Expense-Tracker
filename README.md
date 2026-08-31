# 💰 Python Expense Tracker & Budget Manager

A full-featured, modular **Personal Expense Tracker and Financial Management System** written in Python. It includes a robust SQLite persistence layer, category budget thresholds, analytics, and **3 user interfaces** (Modern Desktop GUI, Interactive Web Dashboard, and Command-Line Interface).

---

## ✨ Features

- **Transaction Management**:
  - Add, edit, delete, and view expenses with Amount, Category, Date, Payment Method, and Notes.
  - Filter & search by keyword, category, payment method, amount range, and date range.
- **Budget Tracking & Smart Alerts**:
  - Set monthly category spending limits.
  - Real-time warnings when reaching 80% and alerts when exceeding 100% of the budget.
- **Visual Analytics & Reports**:
  - Monthly spending totals and daily spending trends.
  - Category breakdown charts (Canvas bar charts in GUI, Altair donut charts in Web app).
  - Key financial metrics: Total spent, Daily average, Total budget, Transaction counts.
- **Data Portability**:
  - One-click export to CSV / JSON format.
  - Bulk import transactions from CSV.
- **Multiple Interfaces**:
  - **🖥️ Desktop GUI (`gui.py`)**: Built with standard Tkinter/ttk with tabbed navigation, responsive cards, and Canvas charts.
  - **🌐 Web App (`app.py`)**: Interactive Streamlit web dashboard with KPI cards and interactive charts.
  - **📟 Terminal CLI (`cli.py`)**: Color-coded ANSI terminal interface for quick logging from the command prompt.

---

## 🚀 Quick Start

### 1. Installation

Ensure you have Python 3.9+ installed. Install the dependencies for the Web App:

```bash
pip install -r requirements.txt
```

> **Note**: The Desktop GUI and CLI run with standard Python libraries alone (no extra pip packages required!).

### 2. Run the Application

You can launch any interface using the unified launcher:

```bash
# Interactive Launcher
python main.py

# Launch Desktop GUI directly
python main.py --gui
# or
python gui.py

# Launch Streamlit Web Dashboard
python main.py --web
# or
streamlit run app.py

# Launch Command-Line Interface
python main.py --cli
# or
python cli.py
```

### 3. Load Sample Demo Data (Optional)

To pre-populate realistic sample transactions across recent months:

```bash
python sample_data.py
# or
python main.py --seed
```

### 4. Running Unit Tests

Run the automated test suite:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
# or
python main.py --test
```

---

## 📁 Project Architecture

```
Python project 2/
│
├── core/
│   ├── __init__.py           # Package exports
│   ├── models.py             # Dataclasses (Expense, Budget, CategorySummary, MonthlyReport)
│   ├── database.py           # SQLite connection & schema management with indexed queries
│   └── expense_manager.py    # Business logic, budget alerts, analytics & CSV/JSON handlers
│
├── cli.py                    # ANSI colorized interactive terminal interface
├── gui.py                    # Modern Tkinter/ttk desktop GUI with custom Canvas charts
├── app.py                    # Streamlit web dashboard with interactive Altair charts
├── main.py                   # Unified CLI/GUI launcher
├── sample_data.py            # Demo transaction generator
├── requirements.txt          # Web app dependencies
│
├── tests/
│   └── test_tracker.py       # Unit tests covering CRUD, filters, budgets, and file I/O
│
└── README.md                 # Project documentation
```

---

## 📊 Interfaces Overview

### 1. Modern Desktop GUI (`gui.py`)
- **Overview & Dashboard**: Summary KPI cards, horizontal bar chart of top spending categories, and breakdown table.
- **Transactions & History**: Searchable, filterable table with column sorting and double-click to edit.
- **Budgets & Categories**: Set category limits and manage custom category tags.

### 2. Web App (`app.py`)
- Live KPI cards with color-coded budget indicators.
- Interactive donut and line charts for daily/monthly spending trends.
- Real-time transaction filtering and direct CSV download/upload.

### 3. Terminal CLI (`cli.py`)
- Clean ASCII tables and structured interactive menus for lightweight and remote terminal environments.
