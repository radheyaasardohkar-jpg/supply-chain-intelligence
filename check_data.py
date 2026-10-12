
import pandas as pd

from src.supply_chain.validation.validate_data import validate_data

DATA_PATH = "data/raw/retail_store_inventory.csv"

df = pd.read_csv(DATA_PATH)
report = validate_data(df)

print("VALIDATION REPORT")
print("=================")
print("Valid structure:", report["valid"])

print("\nErrors:")
for error in report["errors"]:
    print("-", error)

print("\nWarnings:")
if report["warnings"]:
    for warning in report["warnings"]:
        print("-", warning)
else:
    print("No warnings found.")
