from pathlib import Path
import json
import pandas as pd

output_dir = Path(__file__).resolve().parent / "output"

data = pd.read_csv(output_dir / "cleaned_retail_data.csv")

with open( 
    output_dir / "data_quality_report.json",
    encoding = "utf-8",
) as file:
    report = json.load(file)

print("\nFirse five rows:")
print(data.head())

print("\nDataset shape:")
print(data.shape)

print("\nData types:")
print(data.dtypes)

print("\nMissing values:")
print(data.isna().sum())

print("\nQuality report:")
print(json.dumps(report, indent=4))

assert len(data.columns) == 8
assert not data.duplicated().any()
assert data["InvoiceNo"].notna().all()
assert data["StockCode"].notna().all()
assert data["Quantity"].notna().all()
assert data["UnitPrice"].notna().all()

print("\nBasic output checks passed.")

