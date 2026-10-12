
import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = Path("data/processed/supply_chain.db")
SQL_PATH = Path("sql/marts/daily_performance.sql")
OUTPUT_PATH = Path("data/processed/daily_performance.csv")


def main():
    query = SQL_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DB_PATH) as connection:
        report = pd.read_sql_query(query, connection)

    report.to_csv(OUTPUT_PATH, index=False)

    print("Daily performance report created.")
    print(report.head(10).to_string(index=False))
    print(f"\nSaved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
