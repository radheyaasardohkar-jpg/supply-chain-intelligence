from pathlib import Path
import sqlite3

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"

CLEANED_CSV = PROCESSED_DIR / "retail_store_inventory_clean.csv"
DATABASE_PATH = PROCESSED_DIR / "supply_chain.db"
TABLE_NAME = "retail_inventory"


def build_database() -> None:
    """Load the cleaned retail dataset into a SQLite database."""
    if not CLEANED_CSV.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {CLEANED_CSV}\n"
            "Run 'python clean_pipeline.py' first."
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(CLEANED_CSV)

    with sqlite3.connect(DATABASE_PATH) as connection:
        df.to_sql(TABLE_NAME, connection, if_exists="replace", index=False)

        row_count = connection.execute(
            f'SELECT COUNT(*) FROM "{TABLE_NAME}"'
        ).fetchone()[0]

    print("DATABASE BUILD COMPLETE")
    print("=" * 32)
    print(f"Rows loaded: {row_count:,}")
    print(f"Table: {TABLE_NAME}")
    print(f"Database: {DATABASE_PATH}")


if __name__ == "__main__":
    build_database()