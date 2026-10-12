
import pandas as pd


def prepare_daily_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate retail records into a daily demand time series."""

    required = {"Date", "Units Sold"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    data = df[["Date", "Units Sold"]].copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data["Units Sold"] = pd.to_numeric(
        data["Units Sold"], errors="coerce"
    )

    data = data.dropna(subset=["Date", "Units Sold"])

    daily = (
        data.groupby("Date", as_index=False)["Units Sold"]
        .sum()
        .sort_values("Date")
        .reset_index(drop=True)
    )

    return daily
