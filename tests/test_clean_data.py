
import pandas as pd

from src.supply_chain.validation.clean_data import clean_data


def sample_data():
    return pd.DataFrame({
        "Date": ["2025-01-01", "2025-01-02", "2025-01-02", "invalid"],
        "Store ID": ["S001", "S001", "S001", "S002"],
        "Product ID": ["P001", "P001", "P001", "P002"],
        "Inventory Level": [20, 15, 15, 10],
        "Units Sold": [5, 6, 6, 2],
        "Units Ordered": [10, 10, 10, 5],
        "Demand Forecast": [7.0, -2.0, -2.0, 3.0],
        "Price": [20.0, 20.0, 20.0, 15.0],
        "Discount": [0, 5, 5, 0],
        "Competitor Pricing": [19.0, 19.0, 19.0, 14.0],
    })


def test_clean_data_removes_exact_duplicates():
    result = clean_data(sample_data())
    assert not result.duplicated().any()


def test_clean_data_removes_invalid_dates():
    result = clean_data(sample_data())
    assert result["Date"].notna().all()


def test_clean_data_marks_negative_forecasts_missing():
    result = clean_data(sample_data())
    assert not (result["Demand Forecast"].dropna() < 0).any()
    assert result["Demand Forecast"].isna().sum() == 1


def test_clean_data_does_not_modify_raw_data():
    raw = sample_data()
    original = raw.copy(deep=True)

    clean_data(raw)

    pd.testing.assert_frame_equal(raw, original)
