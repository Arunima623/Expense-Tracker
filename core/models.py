"""
Data models and constants for the Expense Tracker.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List, Dict


DEFAULT_CATEGORIES = [
    "Food & Dining",
    "Groceries",
    "Transportation",
    "Housing & Rent",
    "Utilities",
    "Entertainment",
    "Shopping",
    "Healthcare",
    "Education",
    "Investments",
    "Personal Care",
    "Travel",
    "Other"
]

DEFAULT_PAYMENT_METHODS = [
    "Cash",
    "Credit Card",
    "Debit Card",
    "UPI / Online Transfer",
    "Net Banking",
    "Other"
]


@dataclass
class Expense:
    """Represents a single expense record."""
    title: str
    amount: float
    category: str
    date: str  # Format: YYYY-MM-DD
    payment_method: str = "Cash"
    notes: str = ""
    id: Optional[int] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        if not self.title or not self.title.strip():
            raise ValueError("Expense title cannot be empty.")
        if self.amount <= 0:
            raise ValueError("Expense amount must be greater than zero.")
        if not self.category or not self.category.strip():
            raise ValueError("Expense category cannot be empty.")
        
        # Validate date format YYYY-MM-DD
        try:
            datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: '{self.date}'. Expected YYYY-MM-DD.")
        
        self.title = self.title.strip()
        self.category = self.category.strip()
        self.payment_method = self.payment_method.strip() if self.payment_method else "Cash"
        self.notes = self.notes.strip() if self.notes else ""

    def to_dict(self) -> dict:
        """Convert expense to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "payment_method": self.payment_method,
            "notes": self.notes,
            "created_at": self.created_at
        }


@dataclass
class Budget:
    """Represents a monthly category budget."""
    category: str
    month: str  # Format: YYYY-MM
    monthly_limit: float
    id: Optional[int] = None

    def __post_init__(self):
        if not self.category or not self.category.strip():
            raise ValueError("Category cannot be empty.")
        if self.monthly_limit <= 0:
            raise ValueError("Monthly budget limit must be positive.")
        try:
            datetime.strptime(self.month, "%Y-%m")
        except ValueError:
            raise ValueError(f"Invalid month format: '{self.month}'. Expected YYYY-MM.")
        self.category = self.category.strip()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "month": self.month,
            "monthly_limit": self.monthly_limit
        }


@dataclass
class CategorySummary:
    """Summary of spending in a single category."""
    category: str
    total_amount: float
    transaction_count: int
    percentage: float = 0.0
    budget_limit: Optional[float] = None
    budget_used_percent: Optional[float] = None


@dataclass
class MonthlyReport:
    """Consolidated financial report for a month."""
    month: str  # YYYY-MM
    total_spent: float
    total_budget: float
    daily_average: float
    category_summaries: List[CategorySummary] = field(default_factory=list)
    top_category: Optional[str] = None
    transaction_count: int = 0
