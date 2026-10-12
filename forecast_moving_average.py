
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.supply_chain.forecasting.prepare_forecast_data import (
    prepare_daily_demand,
)

RAW_PATH = Path("data/raw/retail_store_inventory.csv")
OUTPUT_PATH = Path("data/processed/moving_average_forecast.csv")
WINDOW = 7


def main():
    df = pd.read_csv(RAW_PATH)
    daily = prepare_daily_demand(df)

    if len(daily) < WINDOW + 14:
        raise ValueError("Not enough daily observations.")

    split_index = int(len(daily) * 0.8)
    train = daily.iloc[:split_index].copy()
    test = daily.iloc[split_index:].copy()

    # Use only observations available before each forecast day.
    combined = pd.concat([train, test], ignore_index=True)
    combined["Moving Average Forecast"] = (
        combined["Units Sold"]
        .shift(1)
        .rolling(window=WINDOW)
        .mean()
    )

    test_forecasts = combined.iloc[split_index:].copy()
    test_forecasts = test_forecasts.dropna(
        subset=["Moving Average Forecast"]
    )

    mae = mean_absolute_error(
        test_forecasts["Units Sold"],
        test_forecasts["Moving Average Forecast"],
    )
    rmse = np.sqrt(
        mean_squared_error(
            test_forecasts["Units Sold"],
            test_forecasts["Moving Average Forecast"],
        )
    )

    print("7-DAY MOVING AVERAGE FORECAST")
    print("=" * 40)
    print("Training days:", len(train))
    print("Testing days:", len(test_forecasts))
    print(f"MAE: {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    test_forecasts.to_csv(OUTPUT_PATH, index=False)
    print(f"Forecast saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
