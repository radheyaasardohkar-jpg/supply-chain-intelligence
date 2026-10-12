
import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean retail inventory data without modifying the raw source."""

    cleaned = df.copy()

    # Standardize column names by trimming accidental whitespace
    cleaned.columns = cleaned.columns.str.strip()

    # Parse dates
    cleaned["Date"] = pd.to_datetime(
        cleaned["Date"], errors="coerce"
    )

    # Convert expected numeric columns
    numeric_columns = [
        "Inventory Level",
        "Units Sold",
        "Units Ordered",
        "Demand Forecast",
        "Price",
        "Discount",
        "Competitor Pricing",
    ]

    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(
            cleaned[column], errors="coerce"
        )

    # Remove exact duplicate records
    cleaned = cleaned.drop_duplicates().copy()

    # Remove rows without essential identifiers or valid dates
    cleaned = cleaned.dropna(
        subset=["Date", "Store ID", "Product ID"]
    ).copy()

    # Negative demand forecasts are invalid for expected unit demand.
    # Replace them with missing values rather than inventing forecasts.
    cleaned.loc[
        cleaned["Demand Forecast"] < 0,
        "Demand Forecast"
    ] = float("nan")

    return cleaned
