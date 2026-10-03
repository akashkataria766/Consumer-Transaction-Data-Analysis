"""Generate a reproducible sample consumer transaction dataset."""

import numpy as np
import pandas as pd

import config

LOGGER = config.get_logger(__name__)


def generate_transactions() -> pd.DataFrame:
    """Create the configured number of synthetic consumer transactions."""
    rng = np.random.default_rng(config.RANDOM_SEED)
    date_range = (config.END_DATE - config.START_DATE).days + 1

    transactions = pd.DataFrame(
        {
            "txn_id": [f"TXN-{config.TXN_ID_START + index}" for index in range(config.ROW_COUNT)],
            "customer_id": [
                f"C_{value}"
                for value in rng.integers(
                    config.CUSTOMER_ID_MIN,
                    config.CUSTOMER_ID_MAX + 1,
                    config.ROW_COUNT,
                )
            ],
            "category": rng.choice(
                config.CATEGORIES,
                size=config.ROW_COUNT,
                p=config.CATEGORY_WEIGHTS,
            ),
            "amount": np.round(
                rng.uniform(config.AMOUNT_MIN, config.AMOUNT_MAX, config.ROW_COUNT), 2
            ),
            "currency": config.CURRENCY_CODE,
            "status": rng.choice(
                config.STATUS_VALUES,
                size=config.ROW_COUNT,
                p=config.STATUS_WEIGHTS,
            ),
            "order_date": config.START_DATE
            + pd.to_timedelta(rng.integers(0, date_range, config.ROW_COUNT), unit="D"),
        }
    )
    return transactions


def save_transactions(transactions: pd.DataFrame) -> None:
    """Save generated transactions to the configured CSV path."""
    transactions.to_csv(config.RAW_DATA_FILE, index=False, date_format="%Y-%m-%d")


def main() -> None:
    """Generate the source dataset and report completion."""
    try:
        transactions = generate_transactions()
        save_transactions(transactions)
        LOGGER.info("Generated %s transactions and saved %s.", len(transactions), config.RAW_DATA_FILE.name)
    except (OSError, ValueError, KeyError) as error:
        LOGGER.error("Could not generate transaction data: %s", error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
