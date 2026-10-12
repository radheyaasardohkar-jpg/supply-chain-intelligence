
import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = Path("data/processed/supply_chain.db")
SQL_PATH = Path("sql/marts/category_performance.sql")
OUTPUT_PATH = Path("data/processed/category_performance.csv")


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    if not SQL_PATH.exists():
        raise FileNotFoundError(
            f"SQL query not found: {SQL_PATH}"
        )

    query = SQL_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DB_PATH) as connection:
        report = pd.read_sql_query(query, connection)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(OUTPUT_PATH, index=False)

    print("\nCATEGORY PERFORMANCE REPORT")
    print("=" * 60)
    print(report.to_string(index=False))
    print(f"\nReport saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
