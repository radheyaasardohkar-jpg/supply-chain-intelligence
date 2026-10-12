
from pathlib import Path
import pandas as pd

from src.supply_chain.validation.validate_data import validate_data
from src.supply_chain.validation.clean_data import clean_data


RAW_PATH = Path("data/raw/retail_store_inventory.csv")
PROCESSED_PATH = Path("data/processed/retail_store_inventory_clean.csv")


def main():
    print("Loading raw data...")
    raw_df = pd.read_csv(RAW_PATH)

    print(f"Raw rows: {len(raw_df):,}")

    print("\nValidating raw data...")
    report = validate_data(raw_df)

    print("Required structure valid:", report["valid"])

    for error in report["errors"]:
        print("ERROR:", error)

    for warning in report["warnings"]:
        print("WARNING:", warning)

    if not report["valid"]:
        raise ValueError("Required columns are missing. Cleaning stopped.")

    print("\nCleaning data...")
    cleaned_df = clean_data(raw_df)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(PROCESSED_PATH, index=False)

    print(f"Clean rows: {len(cleaned_df):,}")
    print(f"Rows removed: {len(raw_df) - len(cleaned_df):,}")
    print(f"Cleaned data saved to: {PROCESSED_PATH}")

    print(
        "Negative demand forecasts remaining:",
        int((cleaned_df["Demand Forecast"] < 0).sum())
    )
    print(
        "Missing demand forecasts after cleaning:",
        int(cleaned_df["Demand Forecast"].isna().sum())
    )


if __name__ == "__main__":
    main()
