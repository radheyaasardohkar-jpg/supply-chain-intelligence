
import pandas as pd


REQUIRED_COLUMNS = [
    "Date",
    "Store ID",
    "Product ID",
    "Category",
    "Region",
    "Inventory Level",
    "Units Sold",
    "Units Ordered",
    "Demand Forecast",
    "Price",
    "Discount",
    "Weather Condition",
    "Holiday/Promotion",
    "Competitor Pricing",
    "Seasonality",
]


def validate_data(df: pd.DataFrame) -> dict:
    """Check required columns and basic data quality."""

    errors = []
    warnings = []

    # Check required columns
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")

    if errors:
        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
        }

    # Check duplicate records
    duplicate_count = int(df.duplicated().sum())

    if duplicate_count:
        warnings.append(f"Found {duplicate_count} duplicate rows.")

    # Check missing values
    missing_values = df.isnull().sum()
    missing_values = missing_values[missing_values > 0]

    if not missing_values.empty:
        warnings.append(
            f"Missing values found: {missing_values.to_dict()}"
        )

    # Check date parsing
    parsed_dates = pd.to_datetime(df["Date"], errors="coerce")
    invalid_dates = int(parsed_dates.isna().sum())

    if invalid_dates:
        warnings.append(f"Found {invalid_dates} invalid or missing dates.")

    # Check non-negative numeric values
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
        values = pd.to_numeric(df[column], errors="coerce")

        invalid_count = int(values.isna().sum())

        if invalid_count:
            warnings.append(
                f"{column}: {invalid_count} missing or non-numeric values."
            )

        negative_count = int((values < 0).sum())

        if negative_count:
            warnings.append(
                f"{column}: {negative_count} negative values."
            )

    return {
        "valid": True,
        "errors": errors,
        "warnings": warnings,
    }
