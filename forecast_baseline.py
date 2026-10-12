
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.supply_chain.forecasting.prepare_forecast_data import (
    prepare_daily_demand,
)

RAW_PATH = Path("data/raw/retail_store_inventory.csv")
OUTPUT_PATH = Path("data/processed/baseline_forecast.csv")


def main():
    df = pd.read_csv(RAW_PATH)
    daily = prepare_daily_demand(df)

    if len(daily) < 14:
        raise ValueError("Not enough daily observations to evaluate.")

    split_index = int(len(daily) * 0.8)
    train = daily.iloc[:split_index].copy()
    test = daily.iloc[split_index:].copy()

    # Predict using the previous day's actual sales.
    combined = pd.concat([train, test], ignore_index=True)
    combined["Baseline Forecast"] = combined["Units Sold"].shift(1)

    test_forecasts = combined.iloc[split_index:].copy()
    test_forecasts = test_forecasts.dropna(
        subset=["Baseline Forecast"]
    )

    mae = mean_absolute_error(
        test_forecasts["Units Sold"],
        test_forecasts["Baseline Forecast"],
    )
    rmse = np.sqrt(
        mean_squared_error(
            test_forecasts["Units Sold"],
            test_forecasts["Baseline Forecast"],
        )
    )

    print("DAILY DEMAND BASELINE")
    print("=" * 40)
    print("Training days:", len(train))
    print("Testing days:", len(test_forecasts))
    print(f"MAE: {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    test_forecasts.to_csv(OUTPUT_PATH, index=False)
    print(f"Forecast evaluation saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
