"""
Modern Desktop Graphical User Interface (GUI) for the Expense Tracker.
Built with Python's standard Tkinter & TTK.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import calendar
from typing import Optional, List
from core.expense_manager import ExpenseManager
from core.models import Expense


# Modern Theme Color Constants
COLOR_BG = "#F4F6F9"
COLOR_CARD = "#FFFFFF"
COLOR_PRIMARY = "#2563EB"       # Vibrant Blue
COLOR_PRIMARY_HOVER = "#1D4ED8"
COLOR_SUCCESS = "#10B981"       # Emerald Green
COLOR_WARNING = "#F59E0B"       # Amber
COLOR_DANGER = "#EF4444"        # Red
COLOR_TEXT = "#1E293B"          # Slate 800
COLOR_TEXT_MUTED = "#64748B"    # Slate 500
COLOR_BORDER = "#E2E8F0"        # Slate 200

# Distinct category colors for visual charts
PALETTE = [
    "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
    "#EC4899", "#14B8A6", "#F97316", "#6366F1", "#84CC16",
    "#06B6D4", "#D946EF", "#A855F7"
]


class ModernExpenseApp(tk.Tk):
    """Main Tkinter Application Window."""

    def __init__(self, db_path: str = "expenses.db"):
        super().__init__()
        self.manager = ExpenseManager(db_path=db_path)

        self.title("💰 Expense Tracker & Budget Manager")
        self.geometry("1050x700")
        self.minsize(900, 600)
        self.configure(bg=COLOR_BG)

        # Apply modern TTK styling
        self._configure_styles()

        # Build UI layout
        self._build_header()
        self._build_tabs()

        # Initial data load
        self.refresh_all_views()

    def _configure_styles(self):
        """Configure ttk widget styles."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure General Notebook
        self.style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#E2E8F0", foreground=COLOR_TEXT,
                             padding=[18, 8], font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab",
                       background=[("selected", COLOR_PRIMARY)],
                       foreground=[("selected", "#FFFFFF")])

        # Treeview Styling
        self.style.configure("Treeview",
                             background="#FFFFFF",
                             foreground=COLOR_TEXT,
                             rowheight=28,
                             font=("Segoe UI", 9),
                             fieldbackground="#FFFFFF",
                             bordercolor=COLOR_BORDER)
        self.style.configure("Treeview.Heading",
                             background="#E2E8F0",
                             foreground=COLOR_TEXT,
                             font=("Segoe UI", 9, "bold"),
                             padding=[6, 6])
        self.style.map("Treeview",
                       background=[("selected", "#DBEAFE")],
                       foreground=[("selected", COLOR_PRIMARY)])

        # Buttons
        self.style.configure("Primary.TButton",
                             background=COLOR_PRIMARY,
                             foreground="#FFFFFF",
                             font=("Segoe UI", 9, "bold"),
                             padding=[12, 6])
        self.style.map("Primary.TButton",
                       background=[("active", COLOR_PRIMARY_HOVER)])

        self.style.configure("Danger.TButton",
                             background=COLOR_DANGER,
                             foreground="#FFFFFF",
                             font=("Segoe UI", 9, "bold"),
                             padding=[12, 6])

    def _build_header(self):
        """Create the top application banner."""
        header_frame = tk.Frame(self, bg=COLOR_PRIMARY, height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="Personal Expense Tracker",
            font=("Segoe UI", 16, "bold"),
            fg="#FFFFFF",
            bg=COLOR_PRIMARY
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=12)

        subtitle_label = tk.Label(
            header_frame,
            text="Budget Management & Financial Analytics",
            font=("Segoe UI", 10),
            fg="#BFDBFE",
            bg=COLOR_PRIMARY
        )
        subtitle_label.pack(side=tk.LEFT, padx=5, pady=16)

        # Quick Refresh Button
        refresh_btn = tk.Button(
            header_frame,
            text="🔄 Refresh Data",
            font=("Segoe UI", 9, "bold"),
            bg="#1D4ED8",
            fg="#FFFFFF",
            activebackground="#1E40AF",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self.refresh_all_views
        )
        refresh_btn.pack(side=tk.RIGHT, padx=20, pady=12)

    def _build_tabs(self):
        """Construct the tabbed navigation."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        # Tab 1: Dashboard / Overview
        self.tab_dashboard = tk.Frame(self.notebook, bg=COLOR_BG)
        self.notebook.add(self.tab_dashboard, text="  📊 Overview & Dashboard  ")
        self._build_dashboard_tab()

        # Tab 2: Transactions / History
        self.tab_expenses = tk.Frame(self.notebook, bg=COLOR_BG)
        self.notebook.add(self.tab_expenses, text="  💳 Transactions & History  ")
        self._build_transactions_tab()

        # Tab 3: Budgets & Categories
        self.tab_budgets = tk.Frame(self.notebook, bg=COLOR_BG)
        self.notebook.add(self.tab_budgets, text="  🎯 Budgets & Categories  ")
        self._build_budgets_tab()

    # =========================================================================
    # TAB 1: DASHBOARD
    # =========================================================================
    def _build_dashboard_tab(self):
        # Month Selector Bar
        top_bar = tk.Frame(self.tab_dashboard, bg=COLOR_BG)
        top_bar.pack(fill=tk.X, padx=10, pady=(10, 5))

        tk.Label(top_bar, text="Select Month:", font=("Segoe UI", 10, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(side=tk.LEFT, padx=(0, 8))
        
        self.dash_month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
        self.dash_month_entry = ttk.Combobox(top_bar, textvariable=self.dash_month_var, width=12, state="readonly")
        # Populate available months
        self._update_month_combobox()
        self.dash_month_entry.pack(side=tk.LEFT, padx=5)
        self.dash_month_entry.bind("<<ComboboxSelected>>", lambda e: self.refresh_dashboard())

        # KPI Summary Cards Container
        self.kpi_frame = tk.Frame(self.tab_dashboard, bg=COLOR_BG)
        self.kpi_frame.pack(fill=tk.X, padx=10, pady=8)

        # KPI Cards (Total Spent, Total Budget, Daily Avg, Transactions)
        self.card_spent_val = tk.StringVar(value="$0.00")
        self.card_budget_val = tk.StringVar(value="$0.00")
        self.card_daily_val = tk.StringVar(value="$0.00")
        self.card_count_val = tk.StringVar(value="0")

        self._create_kpi_card(self.kpi_frame, "Total Spent", self.card_spent_val, COLOR_PRIMARY, 0)
        self._create_kpi_card(self.kpi_frame, "Total Budgeted", self.card_budget_val, COLOR_SUCCESS, 1)
        self._create_kpi_card(self.kpi_frame, "Daily Average", self.card_daily_val, COLOR_WARNING, 2)
        self._create_kpi_card(self.kpi_frame, "Transactions", self.card_count_val, "#8B5CF6", 3)

        # Alert Banner
        self.alert_frame = tk.Frame(self.tab_dashboard, bg="#FEF2F2", highlightbackground="#F87171", highlightthickness=1)
        self.alert_label = tk.Label(self.alert_frame, text="", font=("Segoe UI", 9, "bold"), fg=COLOR_DANGER, bg="#FEF2F2", wraplength=800, justify=tk.LEFT)
        self.alert_label.pack(side=tk.LEFT, padx=12, pady=6)

        # Middle Content: Left = Category Breakdown Canvas Chart, Right = Category List
        content_frame = tk.Frame(self.tab_dashboard, bg=COLOR_BG)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Chart Frame
        chart_card = tk.Frame(content_frame, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1)
        chart_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6), pady=5)

        tk.Label(chart_card, text="Spending by Category", font=("Segoe UI", 11, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT).pack(anchor="w", padx=12, pady=(10, 5))
        self.chart_canvas = tk.Canvas(chart_card, bg=COLOR_CARD, highlightthickness=0)
        self.chart_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Category Table Frame
        table_card = tk.Frame(content_frame, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1, width=380)
        table_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(6, 0), pady=5)
        table_card.pack_propagate(False)

        tk.Label(table_card, text="Category Breakdown", font=("Segoe UI", 11, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT).pack(anchor="w", padx=12, pady=(10, 5))

        self.dash_tree = ttk.Treeview(
            table_card,
            columns=("cat", "amount", "pct"),
            show="headings",
            height=8
        )
        self.dash_tree.heading("cat", text="Category")
        self.dash_tree.heading("amount", text="Amount")
        self.dash_tree.heading("pct", text="% Total")
        self.dash_tree.column("cat", width=140)
        self.dash_tree.column("amount", width=90, anchor="e")
        self.dash_tree.column("pct", width=70, anchor="e")

        dash_scroll = ttk.Scrollbar(table_card, orient="vertical", command=self.dash_tree.yview)
        self.dash_tree.configure(yscrollcommand=dash_scroll.set)
        self.dash_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        dash_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

    def _create_kpi_card(self, parent, title: str, var: tk.StringVar, accent_color: str, col_idx: int):
        card = tk.Frame(parent, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=12, pady=10)
        card.grid(row=0, column=col_idx, sticky="nsew", padx=5)
        parent.grid_columnconfigure(col_idx, weight=1)

        # Accent top bar
        bar = tk.Frame(card, bg=accent_color, height=3)
        bar.pack(fill=tk.X, side=tk.TOP, pady=(0, 6))

        tk.Label(card, text=title.upper(), font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD).pack(anchor="w")
        tk.Label(card, textvariable=var, font=("Segoe UI", 15, "bold"), fg=COLOR_TEXT, bg=COLOR_CARD).pack(anchor="w", pady=(2, 0))

    def _update_month_combobox(self):
        trends = self.manager.get_monthly_trends()
        months = [t["month"] for t in trends] if trends else []
        curr = date.today().strftime("%Y-%m")
        if curr not in months:
            months.append(curr)
        months.sort(reverse=True)
        self.dash_month_entry["values"] = months
        if self.dash_month_var.get() not in months and months:
            self.dash_month_var.set(months[0])

    def refresh_dashboard(self):
        target_month = self.dash_month_var.get() or date.today().strftime("%Y-%m")
        report = self.manager.generate_monthly_report(target_month)

        # Update KPI Cards
        self.card_spent_val.set(f"${report.total_spent:,.2f}")
        self.card_budget_val.set(f"${report.total_budget:,.2f}")
        self.card_daily_val.set(f"${report.daily_average:,.2f}/d")
        self.card_count_val.set(str(report.transaction_count))

        # Check Alerts
        alerts = self.manager.check_budget_alerts(target_month)
        if alerts:
            msg = "⚠️ Budget Alerts: " + " | ".join([a["message"] for a in alerts[:2]])
            self.alert_label.config(text=msg)
            self.alert_frame.pack(fill=tk.X, padx=10, pady=(0, 8), before=self.kpi_frame)
        else:
            self.alert_frame.pack_forget()

        # Update Category Table
        for row in self.dash_tree.get_children():
            self.dash_tree.delete(row)

        for summary in report.category_summaries:
            self.dash_tree.insert("", "end", values=(
                summary.category,
                f"${summary.total_amount:,.2f}",
                f"{summary.percentage:.1f}%"
            ))

        # Draw Category Horizontal Bar Chart on Canvas
        self._draw_category_chart(report.category_summaries)

    def _draw_category_chart(self, summaries: List):
        self.chart_canvas.delete("all")
        width = self.chart_canvas.winfo_width() or 400
        height = self.chart_canvas.winfo_height() or 220

        if not summaries:
            self.chart_canvas.create_text(
                width / 2, height / 2,
                text="No expenses recorded for this month.",
                font=("Segoe UI", 10), fill=COLOR_TEXT_MUTED
            )
            return

        # Top 6 categories
        top_cats = summaries[:6]
        max_amt = max(s.total_amount for s in top_cats) if top_cats else 1.0

        bar_height = 20
        gap = 14
        start_y = 15
        label_width = 110
        chart_width = width - label_width - 90

        for i, s in enumerate(top_cats):
            y = start_y + i * (bar_height + gap)
            color = PALETTE[i % len(PALETTE)]

            # Category Name
            cat_label = s.category if len(s.category) <= 14 else s.category[:12] + ".."
            self.chart_canvas.create_text(
                10, y + bar_height / 2,
                text=cat_label, anchor="w",
                font=("Segoe UI", 8, "bold"), fill=COLOR_TEXT
            )

            # Bar background
            bar_w = (s.total_amount / max_amt) * chart_width if max_amt > 0 else 0
            self.chart_canvas.create_rectangle(
                label_width, y,
                label_width + max(4, bar_w), y + bar_height,
                fill=color, outline="", width=0
            )

            # Value text
            self.chart_canvas.create_text(
                label_width + bar_w + 8, y + bar_height / 2,
                text=f"${s.total_amount:,.1f} ({s.percentage:.0f}%)",
                anchor="w", font=("Segoe UI", 8), fill=COLOR_TEXT_MUTED
            )

    # =========================================================================
    # TAB 2: TRANSACTIONS / HISTORY
    # =========================================================================
    def _build_transactions_tab(self):
        # Filter & Action Toolbar
        toolbar = tk.Frame(self.tab_expenses, bg=COLOR_BG)
        toolbar.pack(fill=tk.X, padx=10, pady=8)

        # Search Bar
        tk.Label(toolbar, text="🔍 Search:", font=("Segoe UI", 9, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(side=tk.LEFT, padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.apply_expense_filters())
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=18)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Category Filter
        tk.Label(toolbar, text="Category:", font=("Segoe UI", 9, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(side=tk.LEFT, padx=(0, 4))
        self.filter_cat_var = tk.StringVar(value="All")
        self.filter_cat_cb = ttk.Combobox(toolbar, textvariable=self.filter_cat_var, state="readonly", width=14)
        self.filter_cat_cb.pack(side=tk.LEFT, padx=(0, 10))
        self.filter_cat_cb.bind("<<ComboboxSelected>>", lambda e: self.apply_expense_filters())

        # Payment Method Filter
        tk.Label(toolbar, text="Payment:", font=("Segoe UI", 9, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(side=tk.LEFT, padx=(0, 4))
        self.filter_pm_var = tk.StringVar(value="All")
        pm_options = ["All"] + self.manager.get_payment_methods()
        self.filter_pm_cb = ttk.Combobox(toolbar, textvariable=self.filter_pm_var, values=pm_options, state="readonly", width=12)
        self.filter_pm_cb.pack(side=tk.LEFT, padx=(0, 10))
        self.filter_pm_cb.bind("<<ComboboxSelected>>", lambda e: self.apply_expense_filters())

        # Clear Filters Button
        clear_btn = ttk.Button(toolbar, text="Clear Filters", command=self._clear_filters)
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Action Buttons on the Right
        btn_add = tk.Button(
            toolbar, text="+ Add Expense",
            font=("Segoe UI", 9, "bold"), bg=COLOR_PRIMARY, fg="#FFFFFF",
            relief=tk.FLAT, padx=10, pady=4, command=self.open_add_expense_dialog
        )
        btn_add.pack(side=tk.RIGHT, padx=4)

        btn_edit = tk.Button(
            toolbar, text="✏️ Edit",
            font=("Segoe UI", 9), bg="#FFFFFF", fg=COLOR_TEXT,
            relief=tk.SOLID, bd=1, padx=8, pady=4, command=self.edit_selected_expense
        )
        btn_edit.pack(side=tk.RIGHT, padx=4)

        btn_del = tk.Button(
            toolbar, text="🗑️ Delete",
            font=("Segoe UI", 9), bg="#FFFFFF", fg=COLOR_DANGER,
            relief=tk.SOLID, bd=1, padx=8, pady=4, command=self.delete_selected_expense
        )
        btn_del.pack(side=tk.RIGHT, padx=4)

        # Table Container
        table_container = tk.Frame(self.tab_expenses, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1)
        table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        columns = ("id", "date", "title", "amount", "category", "payment", "notes")
        self.tx_tree = ttk.Treeview(table_container, columns=columns, show="headings", selectmode="browse")
        
        self.tx_tree.heading("id", text="ID", command=lambda: self._sort_column("id", False))
        self.tx_tree.heading("date", text="Date", command=lambda: self._sort_column("date", True))
        self.tx_tree.heading("title", text="Title / Description", command=lambda: self._sort_column("title", False))
        self.tx_tree.heading("amount", text="Amount ($)", command=lambda: self._sort_column("amount", True))
        self.tx_tree.heading("category", text="Category", command=lambda: self._sort_column("category", False))
        self.tx_tree.heading("payment", text="Payment Method", command=lambda: self._sort_column("payment", False))
        self.tx_tree.heading("notes", text="Notes", command=lambda: self._sort_column("notes", False))

        self.tx_tree.column("id", width=45, anchor="center")
        self.tx_tree.column("date", width=90, anchor="center")
        self.tx_tree.column("title", width=220, anchor="w")
        self.tx_tree.column("amount", width=100, anchor="e")
        self.tx_tree.column("category", width=140, anchor="w")
        self.tx_tree.column("payment", width=130, anchor="w")
        self.tx_tree.column("notes", width=180, anchor="w")

        v_scroll = ttk.Scrollbar(table_container, orient="vertical", command=self.tx_tree.yview)
        h_scroll = ttk.Scrollbar(table_container, orient="horizontal", command=self.tx_tree.xview)
        self.tx_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tx_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.tx_tree.bind("<Double-1>", lambda e: self.edit_selected_expense())

        # Bottom Bar: Summary & Export/Import
        bottom_bar = tk.Frame(self.tab_expenses, bg=COLOR_BG)
        bottom_bar.pack(fill=tk.X, padx=10, pady=5)

        self.status_label = tk.Label(bottom_bar, text="", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT, bg=COLOR_BG)
        self.status_label.pack(side=tk.LEFT)

        btn_export = ttk.Button(bottom_bar, text="📥 Export CSV", command=self.export_csv)
        btn_export.pack(side=tk.RIGHT, padx=5)

        btn_import = ttk.Button(bottom_bar, text="📤 Import CSV", command=self.import_csv)
        btn_import.pack(side=tk.RIGHT, padx=5)

    def _clear_filters(self):
        self.search_var.set("")
        self.filter_cat_var.set("All")
        self.filter_pm_var.set("All")
        self.apply_expense_filters()

    def _sort_column(self, col: str, reverse: bool):
        items = [(self.tx_tree.set(k, col), k) for k in self.tx_tree.get_children("")]
        
        # Sort logic (numbers vs strings)
        if col in ("amount", "id"):
            def try_float(val):
                try:
                    return float(val.replace("$", "").replace(",", ""))
                except ValueError:
                    return 0.0
            items.sort(key=lambda t: try_float(t[0]), reverse=reverse)
        else:
            items.sort(reverse=reverse)

        for index, (_, k) in enumerate(items):
            self.tx_tree.move(k, "", index)

        # Toggle heading command for next click
        self.tx_tree.heading(col, command=lambda: self._sort_column(col, not reverse))

    def apply_expense_filters(self):
        query = self.search_var.get().strip()
        cat = self.filter_cat_var.get()
        pm = self.filter_pm_var.get()

        expenses = self.manager.filter_expenses(
            category=None if cat == "All" else cat,
            payment_method=None if pm == "All" else pm,
            search_query=query if query else None
        )

        for row in self.tx_tree.get_children():
            self.tx_tree.delete(row)

        total = sum(e.amount for e in expenses)
        for e in expenses:
            self.tx_tree.insert("", "end", values=(
                e.id,
                e.date,
                e.title,
                f"${e.amount:,.2f}",
                e.category,
                e.payment_method,
                e.notes
            ))

        self.status_label.config(
            text=f"Showing {len(expenses)} transactions | Total: ${total:,.2f}"
        )

    # =========================================================================
    # TAB 3: BUDGETS & CATEGORIES
    # =========================================================================
    def _build_budgets_tab(self):
        container = tk.Frame(self.tab_budgets, bg=COLOR_BG)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Column: Manage Budgets
        left_card = tk.Frame(container, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1)
        left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        tk.Label(left_card, text="Monthly Category Budgets", font=("Segoe UI", 11, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT).pack(anchor="w", padx=12, pady=10)

        # Budget Form
        form_frame = tk.Frame(left_card, bg=COLOR_CARD)
        form_frame.pack(fill=tk.X, padx=12, pady=5)

        tk.Label(form_frame, text="Category:", font=("Segoe UI", 9), bg=COLOR_CARD).grid(row=0, column=0, sticky="w", pady=4)
        self.budget_cat_cb = ttk.Combobox(form_frame, state="readonly", width=18)
        self.budget_cat_cb.grid(row=0, column=1, sticky="w", padx=5, pady=4)

        tk.Label(form_frame, text="Month (YYYY-MM):", font=("Segoe UI", 9), bg=COLOR_CARD).grid(row=1, column=0, sticky="w", pady=4)
        self.budget_month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
        ttk.Entry(form_frame, textvariable=self.budget_month_var, width=20).grid(row=1, column=1, sticky="w", padx=5, pady=4)

        tk.Label(form_frame, text="Monthly Limit ($):", font=("Segoe UI", 9), bg=COLOR_CARD).grid(row=2, column=0, sticky="w", pady=4)
        self.budget_limit_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.budget_limit_var, width=20).grid(row=2, column=1, sticky="w", padx=5, pady=4)

        save_b_btn = tk.Button(form_frame, text="Save Budget", font=("Segoe UI", 9, "bold"), bg=COLOR_PRIMARY, fg="#FFFFFF",
                               relief=tk.FLAT, padx=10, pady=3, command=self.save_budget)
        save_b_btn.grid(row=3, column=1, sticky="w", padx=5, pady=8)

        # Budget Table
        self.budget_tree = ttk.Treeview(left_card, columns=("id", "month", "cat", "limit"), show="headings", height=8)
        self.budget_tree.heading("id", text="ID")
        self.budget_tree.heading("month", text="Month")
        self.budget_tree.heading("cat", text="Category")
        self.budget_tree.heading("limit", text="Limit ($)")
        self.budget_tree.column("id", width=35, anchor="center")
        self.budget_tree.column("month", width=80, anchor="center")
        self.budget_tree.column("cat", width=140, anchor="w")
        self.budget_tree.column("limit", width=100, anchor="e")
        self.budget_tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        del_b_btn = tk.Button(left_card, text="Delete Selected Budget", font=("Segoe UI", 8), fg=COLOR_DANGER, bg="#FFFFFF",
                              relief=tk.SOLID, bd=1, padx=8, pady=2, command=self.delete_budget)
        del_b_btn.pack(anchor="e", padx=12, pady=(0, 10))

        # Right Column: Manage Categories
        right_card = tk.Frame(container, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1, width=320)
        right_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(6, 0))
        right_card.pack_propagate(False)

        tk.Label(right_card, text="Manage Categories", font=("Segoe UI", 11, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT).pack(anchor="w", padx=12, pady=10)

        cat_add_frame = tk.Frame(right_card, bg=COLOR_CARD)
        cat_add_frame.pack(fill=tk.X, padx=12, pady=5)

        self.new_cat_var = tk.StringVar()
        ttk.Entry(cat_add_frame, textvariable=self.new_cat_var, width=16).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(cat_add_frame, text="+ Add", font=("Segoe UI", 9, "bold"), bg=COLOR_SUCCESS, fg="#FFFFFF",
                  relief=tk.FLAT, padx=8, pady=2, command=self.add_custom_category).pack(side=tk.LEFT)

        self.cat_listbox = tk.Listbox(right_card, font=("Segoe UI", 9), bd=1, relief=tk.SOLID, highlightthickness=0)
        self.cat_listbox.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        tk.Button(right_card, text="Remove Category", font=("Segoe UI", 8), fg=COLOR_DANGER, bg="#FFFFFF",
                  relief=tk.SOLID, bd=1, padx=8, pady=2, command=self.delete_custom_category).pack(anchor="e", padx=12, pady=(0, 10))

    def refresh_budgets_and_categories(self):
        # Refresh category dropdowns & listbox
        cats = self.manager.get_categories()
        self.budget_cat_cb["values"] = cats
        if cats and not self.budget_cat_cb.get():
            self.budget_cat_cb.set(cats[0])

        self.filter_cat_cb["values"] = ["All"] + cats

        self.cat_listbox.delete(0, tk.END)
        for c in cats:
            self.cat_listbox.insert(tk.END, c)

        # Refresh Budgets table
        for row in self.budget_tree.get_children():
            self.budget_tree.delete(row)

        for b in self.manager.get_all_budgets():
            self.budget_tree.insert("", "end", values=(
                b.id,
                b.month,
                b.category,
                f"${b.monthly_limit:,.2f}"
            ))

    def save_budget(self):
        cat = self.budget_cat_cb.get().strip()
        month = self.budget_month_var.get().strip()
        limit_str = self.budget_limit_var.get().strip().replace("$", "")

        if not cat or not month or not limit_str:
            messagebox.showwarning("Incomplete Fields", "Please select category, month, and budget limit.")
            return

        try:
            limit = float(limit_str)
            self.manager.set_budget(cat, month, limit)
            self.budget_limit_var.set("")
            self.refresh_all_views()
            messagebox.showinfo("Success", f"Budget for '{cat}' set to ${limit:,.2f} for {month}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_budget(self):
        selected = self.budget_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a budget row to delete.")
            return
        b_id = self.budget_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm Delete", f"Delete budget #{b_id}?"):
            self.manager.delete_budget(int(b_id))
            self.refresh_all_views()

    def add_custom_category(self):
        name = self.new_cat_var.get().strip()
        if not name:
            return
        if self.manager.add_category(name):
            self.new_cat_var.set("")
            self.refresh_all_views()
        else:
            messagebox.showwarning("Duplicate", f"Category '{name}' already exists.")

    def delete_custom_category(self):
        selected = self.cat_listbox.curselection()
        if not selected:
            return
        cat_name = self.cat_listbox.get(selected[0])
        if messagebox.askyesno("Confirm Delete", f"Delete category '{cat_name}'?"):
            self.manager.delete_category(cat_name)
            self.refresh_all_views()

    # =========================================================================
    # EXPENSE CRUD & DIALOGS
    # =========================================================================
    def open_add_expense_dialog(self, expense: Optional[Expense] = None):
        """Open modal dialog to add or edit an expense."""
        dialog = tk.Toplevel(self)
        dialog.title("Edit Expense" if expense else "Add New Expense")
        dialog.geometry("440x480")
        dialog.resizable(False, False)
        dialog.configure(bg=COLOR_BG)
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 220
        y = self.winfo_y() + (self.winfo_height() // 2) - 240
        dialog.geometry(f"+{x}+{y}")

        form = tk.Frame(dialog, bg=COLOR_BG, padx=20, pady=15)
        form.pack(fill=tk.BOTH, expand=True)

        # Title
        tk.Label(form, text="Title / Description *", font=("Segoe UI", 9, "bold"), bg=COLOR_BG).pack(anchor="w", pady=(0, 2))
        title_entry = ttk.Entry(form, font=("Segoe UI", 10))
        title_entry.pack(fill=tk.X, pady=(0, 10))
        if expense:
            title_entry.insert(0, expense.title)

        # Amount
        tk.Label(form, text="Amount ($) *", font=("Segoe UI", 9, "bold"), bg=COLOR_BG).pack(anchor="w", pady=(0, 2))
        amount_entry = ttk.Entry(form, font=("Segoe UI", 10))
        amount_entry.pack(fill=tk.X, pady=(0, 10))
        if expense:
            amount_entry.insert(0, str(expense.amount))

        # Category
        tk.Label(form, text="Category *", font=("Segoe UI", 9, "bold"), bg=COLOR_BG).pack(anchor="w", pady=(0, 2))
        cats = self.manager.get_categories()
        cat_cb = ttk.Combobox(form, values=cats, state="readonly", font=("Segoe UI", 10))
        cat_cb.pack(fill=tk.X, pady=(0, 10))
        cat_cb.set(expense.category if expense else (cats[0] if cats else "Other"))

        # Date
        tk.Label(form, text="Date (YYYY-MM-DD) *", font=("Segoe UI", 9, "bold"), bg=COLOR_BG).pack(anchor="w", pady=(0, 2))
        date_frame = tk.Frame(form, bg=COLOR_BG)
        date_frame.pack(fill=tk.X, pady=(0, 10))
        date_entry = ttk.Entry(date_frame, font=("Segoe UI", 10))
        date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        date_entry.insert(0, expense.date if expense else date.today().strftime("%Y-%m-%d"))

        def set_today():
            date_entry.delete(0, tk.END)
            date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        tk.Button(date_frame, text="Today", font=("Segoe UI", 8), command=set_today).pack(side=tk.RIGHT, padx=(5, 0))

        # Payment Method
        tk.Label(form, text="Payment Method", font=("Segoe UI", 9, "bold"), bg=COLOR_BG).pack(anchor="w", pady=(0, 2))
        pm_cb = ttk.Combobox(form, values=self.manager.get_payment_methods(), state="readonly", font=("Segoe UI", 10))
        pm_cb.pack(fill=tk.X, pady=(0, 10))
        pm_cb.set(expense.payment_method if expense else "Cash")

        # Notes
        tk.Label(form, text="Notes / Tags", font=("Segoe UI", 9), bg=COLOR_BG).pack(anchor="w", pady=(0, 2))
        notes_entry = ttk.Entry(form, font=("Segoe UI", 10))
        notes_entry.pack(fill=tk.X, pady=(0, 15))
        if expense and expense.notes:
            notes_entry.insert(0, expense.notes)

        # Save Button
        def on_save():
            title = title_entry.get().strip()
            amount_str = amount_entry.get().strip().replace("$", "")
            cat = cat_cb.get().strip()
            exp_date = date_entry.get().strip()
            pm = pm_cb.get().strip()
            notes = notes_entry.get().strip()

            if not title or not amount_str or not cat or not exp_date:
                messagebox.showwarning("Missing Fields", "Please fill in all required fields.", parent=dialog)
                return

            try:
                amt = float(amount_str)
                if expense:
                    self.manager.update_expense(
                        expense_id=expense.id,
                        title=title,
                        amount=amt,
                        category=cat,
                        expense_date=exp_date,
                        payment_method=pm,
                        notes=notes
                    )
                else:
                    self.manager.add_expense(
                        title=title,
                        amount=amt,
                        category=cat,
                        expense_date=exp_date,
                        payment_method=pm,
                        notes=notes
                    )
                self.refresh_all_views()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dialog)

        save_btn = tk.Button(
            form,
            text="Save Changes" if expense else "Add Expense",
            font=("Segoe UI", 10, "bold"),
            bg=COLOR_PRIMARY,
            fg="#FFFFFF",
            relief=tk.FLAT,
            pady=6,
            command=on_save
        )
        save_btn.pack(fill=tk.X)

    def edit_selected_expense(self):
        selected = self.tx_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an expense to edit.")
            return
        exp_id = int(self.tx_tree.item(selected[0])["values"][0])
        expense = self.manager.get_expense(exp_id)
        if expense:
            self.open_add_expense_dialog(expense)

    def delete_selected_expense(self):
        selected = self.tx_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an expense to delete.")
            return
        exp_id = int(self.tx_tree.item(selected[0])["values"][0])
        title = self.tx_tree.item(selected[0])["values"][2]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{title}'?"):
            self.manager.delete_expense(exp_id)
            self.refresh_all_views()

    def export_csv(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"expenses_export_{date.today().strftime('%Y%m%d')}.csv"
        )
        if filename:
            count = self.manager.export_to_csv(filename)
            messagebox.showinfo("Export Successful", f"Successfully exported {count} transactions to:\n{filename}")

    def import_csv(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            success, errors, msgs = self.manager.import_from_csv(filename)
            self.refresh_all_views()
            msg = f"Successfully imported {success} transactions."
            if errors > 0:
                msg += f"\n\n{errors} rows failed to import."
            messagebox.showinfo("Import Results", msg)

    def refresh_all_views(self):
        self._update_month_combobox()
        self.refresh_dashboard()
        self.apply_expense_filters()
        self.refresh_budgets_and_categories()


if __name__ == "__main__":
    app = ModernExpenseApp()
    app.mainloop()
