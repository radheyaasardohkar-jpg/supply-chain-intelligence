
import sqlite3
from pathlib import Path

import pandas as pd


DATA_PATH = Path("data/processed/retail_store_inventory_clean.csv")
DB_PATH = Path("data/processed/supply_chain.db")


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {DATA_PATH}. "
            "Run python clean_pipeline.py first."
        )

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH, parse_dates=["Date"])

    with sqlite3.connect(DB_PATH) as connection:
        df.to_sql(
            "retail_inventory",
            connection,
            if_exists="replace",
            index=False,
        )

        row_count = pd.read_sql_query(
            "SELECT COUNT(*) AS total_rows FROM retail_inventory",
            connection,
        ).iloc[0, 0]

    print(f"Database created: {DB_PATH}")
    print(f"Rows loaded: {row_count:,}")


if __name__ == "__main__":
    main()
