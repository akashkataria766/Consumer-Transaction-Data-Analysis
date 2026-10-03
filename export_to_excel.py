"""Export transaction analysis summaries to a multi-sheet Excel workbook."""

import pandas as pd

import config

LOGGER = config.get_logger(__name__)


def prepare_analysis_tables(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build overall, category, and monthly summary tables for export."""
    overall = pd.DataFrame(
        {
            "metric": ["Total transactions", "Total revenue", "Average order", "Maximum order", "Minimum order"],
            "value": [
                len(data),
                data["amount"].sum(),
                data["amount"].mean(),
                data["amount"].max(),
                data["amount"].min(),
            ],
        }
    )
    category = (
        data.groupby("category")["amount"]
        .agg(total_orders="size", total_revenue="sum", average_order="mean")
        .sort_values("total_revenue", ascending=False)
        .reset_index()
    )
    monthly = (
        data.assign(month=data["order_date"].dt.to_period("M").astype(str))
        .groupby("month")["amount"]
        .agg(total_orders="size", total_revenue="sum")
        .sort_index()
        .reset_index()
    )
    return overall, category, monthly


def export_workbook(data: pd.DataFrame) -> None:
    """Write the three analysis tables to separate Excel sheets."""
    overall, category, monthly = prepare_analysis_tables(data)
    with pd.ExcelWriter(config.EXCEL_FILE, engine="openpyxl") as writer:
        overall.to_excel(writer, sheet_name="Analysis Summary", index=False)
        category.to_excel(writer, sheet_name="Category Breakdown", index=False)
        monthly.to_excel(writer, sheet_name="Monthly Trend", index=False)


def main() -> None:
    """Load cleaned data and export the Excel workbook."""
    try:
        data = pd.read_csv(config.CLEAN_DATA_FILE, parse_dates=["order_date"])
        export_workbook(data)
        LOGGER.info("Excel workbook saved to %s.", config.EXCEL_FILE.name)
    except (OSError, ValueError, KeyError, ImportError) as error:
        LOGGER.error("Could not export Excel workbook: %s", error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
