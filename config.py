"""Central configuration for the consumer transaction analysis project."""

import logging
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
RAW_DATA_FILE = PROJECT_DIR / "transactions.csv"
CLEAN_DATA_FILE = PROJECT_DIR / "transactions_clean.csv"
DASHBOARD_FILE = PROJECT_DIR / "transaction_dashboard.png"
EXCEL_FILE = PROJECT_DIR / "transaction_analysis.xlsx"

RANDOM_SEED = 42
ROW_COUNT = 500
TXN_ID_START = 10001
CUSTOMER_ID_MIN = 1000
CUSTOMER_ID_MAX = 5000
START_DATE = pd.Timestamp("2025-12-01")
END_DATE = pd.Timestamp("2026-04-30")
CURRENCY_CODE = "USD"
AMOUNT_MIN = 100.0
AMOUNT_MAX = 3000.0
CATEGORIES = ["Electronics", "Clothing", "Home & Kitchen", "Books"]
CATEGORY_WEIGHTS = [0.35, 0.30, 0.20, 0.15]
STATUS_VALUES = ["COMPLETED", "PENDING", "CANCELLED"]
STATUS_WEIGHTS = [0.70, 0.20, 0.10]
VALID_STATUSES = set(STATUS_VALUES)
PERCENTILE_THRESHOLD = 0.99
Z_SCORE_THRESHOLD = 3.0
DASHBOARD_NAVY = "#1F3864"
DASHBOARD_PALETTE = ["#1F3864", "#4472C4", "#70AD47", "#ED7D31", "#A5A5A5"]


def get_logger(name: str) -> logging.Logger:
    """Return an INFO-level logger with a consistent project format."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    return logging.getLogger(name)
