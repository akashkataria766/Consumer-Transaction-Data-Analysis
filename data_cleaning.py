"""Clean the generated consumer transaction data."""

import pandas as pd

import config

LOGGER = config.get_logger(__name__)


def log_summary(step: str, data: pd.DataFrame) -> None:
    """Log the row and null-value counts after a cleaning step."""
    LOGGER.info("%s | rows=%s | null_values=%s", step, len(data), int(data.isna().sum().sum()))


def clean_transactions(data: pd.DataFrame) -> pd.DataFrame:
    """Apply validation, type conversion, and business-rule filters."""
    log_summary("1. Loaded source data", data)

    missing_amounts = int(data["amount"].isna().sum())
    amount_median = data["amount"].median()
    data["amount"] = data["amount"].fillna(amount_median)
    LOGGER.info("Filled %s missing amount value(s) with median %.2f.", missing_amounts, amount_median)
    log_summary("2. Filled missing amounts", data)

    missing_statuses = int(data["status"].isna().sum())
    data["status"] = data["status"].fillna("UNKNOWN")
    LOGGER.info("Filled %s missing status value(s) with UNKNOWN.", missing_statuses)
    log_summary("3. Filled missing statuses", data)

    before_drop = len(data)
    data = data.dropna(subset=["customer_id"])
    LOGGER.info("Dropped %s row(s) with missing customer_id.", before_drop - len(data))
    log_summary("4. Dropped missing customer IDs", data)

    before_duplicates = len(data)
    data = data.drop_duplicates(subset=["txn_id"], keep="first")
    LOGGER.info("Removed %s duplicate txn_id row(s).", before_duplicates - len(data))
    log_summary("5. Removed duplicate transaction IDs", data)

    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce")
    log_summary("6. Converted order_date to datetime", data)

    data["amount"] = pd.to_numeric(data["amount"], errors="coerce").round(2)
    log_summary("7. Converted amount to float and rounded to 2 decimals", data)

    before_positive_filter = len(data)
    data = data[data["amount"] > 0]
    LOGGER.info("Removed %s row(s) with amount <= 0.", before_positive_filter - len(data))
    log_summary("8. Filtered positive amounts", data)

    before_status_filter = len(data)
    data = data[data["status"].isin(config.VALID_STATUSES)].copy()
    LOGGER.info("Removed %s row(s) with invalid status.", before_status_filter - len(data))
    log_summary("9. Filtered valid statuses", data)
    return data


def main() -> None:
    """Load, clean, save, and report the cleaned transaction dataset."""
    try:
        data = pd.read_csv(config.RAW_DATA_FILE)
        cleaned_data = clean_transactions(data)
        cleaned_data.to_csv(config.CLEAN_DATA_FILE, index=False, date_format="%Y-%m-%d")
        LOGGER.info("Cleaned data saved to %s.", config.CLEAN_DATA_FILE.name)
    except (OSError, ValueError, KeyError) as error:
        LOGGER.error("Could not clean transaction data: %s", error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
