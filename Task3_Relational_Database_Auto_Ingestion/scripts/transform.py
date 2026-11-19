import pandas as pd
from pathlib import Path
from decimal import Decimal

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data" / "raw" / "Online Retail.xlsx"
REJECT_FILE = BASE_DIR / "data" / "processed" / "rejected_rows.csv"


def transform_data():

    print("Reading source dataset...")

    df = pd.read_excel(
        INPUT_FILE,
        dtype={
            "InvoiceNo": "string",
            "StockCode": "string",
            "CustomerID": "string"
        }
    )

    print("Original records:", len(df))

    # Preserve original Excel row identity
    df["source_row_id"] = df.index + 2

    # Standardize text columns
    for col in ["InvoiceNo", "StockCode", "CustomerID"]:
        df[col] = df[col].str.strip()

    df["Description"] = df["Description"].str.strip()
    df["Country"] = df["Country"].str.strip()

    # Convert numeric columns
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")

    df["UnitPrice"] = pd.to_numeric( df["UnitPrice"], errors="coerce")

    # Convert invoice date
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    # Identify invalid records
    invalid_mask = (
        df["InvoiceNo"].isna() | (df["InvoiceNo"] == "")
        | df["StockCode"].isna() | (df["StockCode"] == "")
        | df["Quantity"].isna()
        | df["UnitPrice"].isna()
        | df["InvoiceDate"].isna()
    )

    rejected = df[invalid_mask]

    rejected.to_csv(REJECT_FILE, index=False)

    # Retain valid records
    df = df[~invalid_mask].copy()

    # Convert data types
    df["Quantity"] = df["Quantity"].astype(int)

    df["UnitPrice"] = df["UnitPrice"].map(
        lambda value: Decimal(str(value)).quantize(Decimal("0.01"))
    )

    # Normalize missing customer IDs
    df["CustomerID"] = df["CustomerID"].replace("", pd.NA)

    df = df.where(pd.notna(df), None)

    print("Valid records:", len(df))
    print("Rejected records:", len(rejected))

    return df


if __name__ == "__main__":
    transform_data()