"""Create a polished three-panel transaction dashboard."""

import matplotlib.pyplot as plt
import pandas as pd

import config

LOGGER = config.get_logger(__name__)


def load_dashboard_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load cleaned data and return monthly and category dashboard tables."""
    data = pd.read_csv(config.CLEAN_DATA_FILE, parse_dates=["order_date"])
    data["month"] = data["order_date"].dt.to_period("M").astype(str)
    monthly = data.groupby("month")["amount"].agg(revenue="sum", transactions="size")
    category_revenue = data.groupby("category")["amount"].sum().sort_values(ascending=False)
    return monthly, category_revenue


def annotate_highest(axis, labels: list[str], values: pd.Series, prefix: str = "") -> None:
    """Annotate the highest value in a chart."""
    highest_index = values.argmax()
    axis.annotate(
        f"Highest\n{prefix}{values.iloc[highest_index]:,.0f}",
        xy=(highest_index, values.iloc[highest_index]),
        xytext=(0, 22),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        fontweight="bold",
        color=config.DASHBOARD_NAVY,
        arrowprops={"arrowstyle": "->", "color": config.DASHBOARD_NAVY},
    )


def add_bar_labels(axis, bars: object, values: pd.Series) -> None:
    """Add readable value labels above monthly revenue bars."""
    for bar, value in zip(bars, values):
        axis.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"${value:,.0f}",
                  ha="center", va="bottom", fontsize=8)


def create_dashboard(monthly: pd.DataFrame, category_revenue: pd.Series) -> None:
    """Render and save the revenue, category, and volume charts."""
    figure, axes = plt.subplots(1, 3, figsize=(18, 6))
    figure.suptitle("Consumer Transaction Dashboard", fontsize=18, fontweight="bold", color=config.DASHBOARD_NAVY)

    revenue_bars = axes[0].bar(monthly.index, monthly["revenue"], color=config.DASHBOARD_NAVY)
    axes[0].set(title="Monthly Revenue", xlabel="Order Month", ylabel="Revenue ($)")
    axes[0].grid(axis="y", alpha=0.3)
    axes[0].tick_params(axis="x", rotation=45)
    add_bar_labels(axes[0], revenue_bars, monthly["revenue"])
    annotate_highest(axes[0], list(monthly.index), monthly["revenue"], prefix="$" )

    wedges, _, _ = axes[1].pie(category_revenue, labels=category_revenue.index,
                                autopct="%1.1f%%", startangle=90,
                                colors=config.DASHBOARD_PALETTE[:len(category_revenue)])
    axes[1].set_title("Category Revenue Mix", color=config.DASHBOARD_NAVY, fontweight="bold")
    axes[1].legend(wedges, [f"${value:,.0f}" for value in category_revenue],
                   title="Revenue", loc="lower center", fontsize=8)
    axes[1].annotate(f"Highest\n{category_revenue.index[0]}", xy=(0, 0), xytext=(0, -1.35),
                     ha="center", color=config.DASHBOARD_NAVY, fontweight="bold")

    axes[2].plot(monthly.index, monthly["transactions"], marker="o", linewidth=2.5,
                 color=config.DASHBOARD_NAVY)
    axes[2].set(title="Monthly Transaction Volume", xlabel="Order Month", ylabel="Transactions")
    axes[2].grid(axis="y", alpha=0.3)
    axes[2].tick_params(axis="x", rotation=45)
    for index, value in enumerate(monthly["transactions"]):
        axes[2].annotate(str(value), (index, value), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)
    annotate_highest(axes[2], list(monthly.index), monthly["transactions"])

    figure.tight_layout()
    figure.savefig(config.DASHBOARD_FILE, dpi=150, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    """Load dashboard data, create the figure, and log completion."""
    try:
        monthly, category_revenue = load_dashboard_data()
        create_dashboard(monthly, category_revenue)
        LOGGER.info("Dashboard saved to %s.", config.DASHBOARD_FILE.name)
    except (OSError, ValueError, KeyError) as error:
        LOGGER.error("Could not create dashboard: %s", error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
"""Create a three-panel transaction dashboard."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


INPUT_FILE = Path(__file__).with_name("transactions_clean.csv")
OUTPUT_FILE = Path(__file__).with_name("transaction_dashboard.png")


def add_bar_labels(axis, bars, values, prefix: str = "") -> None:
    for bar, value in zip(bars, values):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{prefix}{value:,.0f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )


def main() -> None:
    data = pd.read_csv(INPUT_FILE, parse_dates=["order_date"])
    data["month"] = data["order_date"].dt.to_period("M").astype(str)

    monthly = data.groupby("month")["amount"].agg(revenue="sum", transactions="size")
    category_revenue = data.groupby("category")["amount"].sum().sort_values(ascending=False)

    figure, axes = plt.subplots(1, 3, figsize=(18, 6))
    figure.suptitle("Consumer Transaction Dashboard", fontsize=16, fontweight="bold")

    revenue_bars = axes[0].bar(monthly.index, monthly["revenue"], color="#1f77b4")
    axes[0].set_title("Monthly Revenue")
    axes[0].set_xlabel("Month")
    axes[0].set_ylabel("Revenue ($)")
    axes[0].tick_params(axis="x", rotation=45)
    add_bar_labels(axes[0], revenue_bars, monthly["revenue"], prefix="$" )

    wedges, _, _ = axes[1].pie(
        category_revenue,
        labels=category_revenue.index,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 8},
    )
    axes[1].set_title("Category Revenue Split")
    axes[1].legend(wedges, [f"${value:,.0f}" for value in category_revenue], loc="lower center", fontsize=8)

    axes[2].plot(
        monthly.index,
        monthly["transactions"],
        marker="o",
        linewidth=2,
        color="#ff7f0e",
    )
    axes[2].set_title("Monthly Transaction Volume")
    axes[2].set_xlabel("Month")
    axes[2].set_ylabel("Transactions")
    axes[2].tick_params(axis="x", rotation=45)
    for month, value in monthly["transactions"].items():
        axes[2].annotate(str(value), (month, value), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)

    figure.tight_layout()
    figure.savefig(OUTPUT_FILE, dpi=150, bbox_inches="tight")
    plt.close(figure)
    print(f"Dashboard saved to {OUTPUT_FILE.name}.")


if __name__ == "__main__":
    main()
