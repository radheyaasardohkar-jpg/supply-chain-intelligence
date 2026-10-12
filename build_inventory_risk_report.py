
from pathlib import Path

import pandas as pd

from src.supply_chain.inventory.inventory_risk import (
    assess_inventory_risk,
)

ROOT = Path(__file__).resolve().parent
INPUT_PATH = ROOT / "data" / "processed" / "retail_store_inventory_clean.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "inventory_risk_report.csv"


def main():
    df = pd.read_csv(INPUT_PATH)
    risk_report = assess_inventory_risk(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    risk_report.to_csv(OUTPUT_PATH, index=False)

    print("INVENTORY RISK REPORT")
    print("=" * 45)
    print("Store-product pairs:", len(risk_report))
    print("\nRisk summary:")

    print(
        risk_report["Risk Status"]
        .value_counts()
        .to_string()
    )

    print("\nHighest-priority inventory records:")
    print(risk_report.head(10).to_string(index=False))

    print(f"\nReport saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
