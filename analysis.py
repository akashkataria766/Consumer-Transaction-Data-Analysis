"""Analyze cleaned consumer transaction data with two outlier methods."""

import numpy as np
import pandas as pd

import config

LOGGER = config.get_logger(__name__)


def load_transactions() -> pd.DataFrame:
    """Load the cleaned transaction file and add a reporting month."""
    data = pd.read_csv(config.CLEAN_DATA_FILE, parse_dates=["order_date"])
    data["month"] = data["order_date"].dt.to_period("M").astype(str)
    return data


def build_summaries(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build category, monthly, status, and customer summary tables."""
    category = data.groupby("category")["amount"].agg(
        total_orders="size", total_revenue="sum", average_order="mean"
    ).sort_values("total_revenue", ascending=False)
    monthly = data.groupby("month")["amount"].agg(
        total_orders="size", total_revenue="sum"
    ).sort_index()
    status = data["status"].value_counts().to_frame("orders")
    status["percentage"] = status["orders"] / len(data) * 100
    customers = data.groupby("customer_id")["amount"].agg(
        total_spend="sum", total_orders="size"
    ).sort_values("total_spend", ascending=False).head(5)
    return category, monthly, status, customers


def detect_outliers(data: pd.DataFrame) -> tuple[float, pd.DataFrame, float, pd.DataFrame]:
    """Detect high-value orders using percentile and Z-score thresholds."""
    percentile_cutoff = data["amount"].quantile(config.PERCENTILE_THRESHOLD)
    percentile_outliers = data[data["amount"] > percentile_cutoff].sort_values("amount", ascending=False)
    amount_mean = data["amount"].mean()
    amount_std = data["amount"].std()
    z_scores = (data["amount"] - amount_mean) / amount_std
    z_score_outliers = data[np.abs(z_scores) > config.Z_SCORE_THRESHOLD].sort_values(
        "amount", ascending=False
    )
    return percentile_cutoff, percentile_outliers, config.Z_SCORE_THRESHOLD, z_score_outliers


def log_report(data: pd.DataFrame) -> None:
    """Log overall metrics, summaries, and anomaly results."""
    category, monthly, status, customers = build_summaries(data)
    percentile_cutoff, percentile_outliers, z_threshold, z_score_outliers = detect_outliers(data)
    LOGGER.info("Overall metrics: transactions=%s, revenue=$%.2f, average=$%.2f, max=$%.2f, min=$%.2f",
                len(data), data["amount"].sum(), data["amount"].mean(), data["amount"].max(), data["amount"].min())
    LOGGER.info("Revenue by category:\n%s", category.to_string(float_format=lambda value: f"${value:,.2f}"))
    LOGGER.info("Monthly trend:\n%s", monthly.to_string(float_format=lambda value: f"${value:,.2f}"))
    LOGGER.info("Status breakdown:\n%s", status.to_string(float_format=lambda value: f"{value:.2f}%"))
    LOGGER.info("Top 5 customers:\n%s", customers.to_string(float_format=lambda value: f"${value:,.2f}"))
    LOGGER.info("Percentile outliers: cutoff=$%.2f, count=%s", percentile_cutoff, len(percentile_outliers))
    LOGGER.info("Z-score outliers: threshold=%.1f, count=%s", z_threshold, len(z_score_outliers))
    LOGGER.info("Analysis completed successfully.")


def main() -> None:
    """Load data, calculate results, and log the complete analysis."""
    try:
        log_report(load_transactions())
    except (OSError, ValueError, KeyError, ZeroDivisionError) as error:
        LOGGER.error("Could not complete transaction analysis: %s", error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
