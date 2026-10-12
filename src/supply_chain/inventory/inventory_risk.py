
import numpy as np
import pandas as pd


def assess_inventory_risk(df: pd.DataFrame) -> pd.DataFrame:
    """Assess inventory risk using the latest record for each store-product pair."""

    required = {
        "Date",
        "Store ID",
        "Product ID",
        "Category",
        "Region",
        "Inventory Level",
        "Demand Forecast",
    }

    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    data = df.copy()

    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data["Inventory Level"] = pd.to_numeric(
        data["Inventory Level"], errors="coerce"
    )
    data["Demand Forecast"] = pd.to_numeric(
        data["Demand Forecast"], errors="coerce"
    )

    data = data.dropna(
        subset=["Date", "Store ID", "Product ID"]
    )

    # Use the most recent inventory snapshot for each store-product pair.
    data = (
        data.sort_values("Date")
        .drop_duplicates(
            subset=["Store ID", "Product ID"],
            keep="last",
        )
        .copy()
    )

    valid_forecast = data["Demand Forecast"] > 0

    data["Stock Cover Days"] = np.where(
        valid_forecast,
        data["Inventory Level"] / data["Demand Forecast"],
        np.nan,
    )

    data["Risk Status"] = np.select(
        [
            data["Inventory Level"].isna(),
            ~valid_forecast,
            data["Stock Cover Days"] < 1,
            data["Stock Cover Days"] < 3,
        ],
        [
            "Data issue",
            "Forecast unavailable",
            "Critical",
            "Reorder soon",
        ],
        default="Healthy",
    )

    columns = [
        "Date",
        "Store ID",
        "Product ID",
        "Category",
        "Region",
        "Inventory Level",
        "Demand Forecast",
        "Stock Cover Days",
        "Risk Status",
    ]

    return data[columns].sort_values(
        ["Risk Status", "Stock Cover Days"],
        na_position="last",
    ).reset_index(drop=True)
