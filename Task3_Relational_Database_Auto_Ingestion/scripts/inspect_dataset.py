
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. DEFINE FILE PATH
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data" / "raw" / "Online Retail.xlsx"

REPORT_FILE = BASE_DIR / "data" / "processed" / "dataset_inspection.txt"


# --------------------------------------------------
# 2. READ DATASET
# --------------------------------------------------

def load_dataset():

    print("\nReading Online Retail dataset...")

    df = pd.read_excel(
        INPUT_FILE,
        dtype={
            "InvoiceNo": "string",
            "StockCode": "string",
            "CustomerID": "string"
        }
    )

    print("Dataset loaded successfully.")

    return df


# --------------------------------------------------
# 3. DATASET BASIC INFORMATION
# --------------------------------------------------

def inspect_basic_information(df):

    print("\n" + "=" * 55)
    print("BASIC DATASET INFORMATION")
    print("=" * 55)

    print("Total Records:", len(df))
    print("Total Columns:", len(df.columns))

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nFirst 10 Records:")
    print(df.head(10))


# --------------------------------------------------
# 4. DATA QUALITY INVESTIGATION
# --------------------------------------------------

def investigate_dataset(df):

    print("\n" + "=" * 55)
    print("DATA QUALITY INVESTIGATION")
    print("=" * 55)

    # Unique customers
    unique_customers = df["CustomerID"].nunique()

    # Unique products
    unique_products = df["StockCode"].nunique()

    # Unique invoices
    unique_invoices = df["InvoiceNo"].nunique()

    # Missing CustomerID
    missing_customers = df["CustomerID"].isnull().sum()

    # Negative Quantity
    negative_quantity = (df["Quantity"] < 0).sum()

    # Duplicate records
    duplicate_records = df.duplicated().sum()

    # Total rows involved in duplicate groups
    duplicate_rows = df.duplicated(keep=False).sum()

    # Display results
    results = {
        "Total Records": len(df),
        "Unique Customers": unique_customers,
        "Unique Products": unique_products,
        "Unique Invoices": unique_invoices,
        "Missing CustomerID Records": missing_customers,
        "Negative Quantity Records": negative_quantity,
        "Duplicate Occurrences": duplicate_records,
        "Rows Involved in Duplicate Groups": duplicate_rows
    }

    for description, value in results.items():

        print(f"{description}: {value}")

    return results


# --------------------------------------------------
# 5. DISPLAY RECORDS REQUIRING INVESTIGATION
# --------------------------------------------------

def inspect_problematic_records(df):

    print("\n" + "=" * 55)
    print("RECORD-LEVEL INVESTIGATION")
    print("=" * 55)

    print("\nMissing CustomerID Records:")

    print(
        df[df["CustomerID"].isnull()].head(10)
    )

    print("\nNegative Quantity Records:")

    print(
        df[df["Quantity"] < 0].head(10)
    )

    print("\nDuplicate Records:")

    print(
        df[df.duplicated(keep=False)].head(20)
    )


# --------------------------------------------------
# 6. GENERATE INSPECTION REPORT
# --------------------------------------------------

def generate_report(results):

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(REPORT_FILE, "w", encoding="utf-8") as file:

        file.write("ONLINE RETAIL DATASET INSPECTION REPORT\n")

        file.write("=" * 55 + "\n\n")

        for description, value in results.items():

            file.write(f"{description}: {value}\n")

    print("\nInspection report saved successfully.")

    print("Report location:", REPORT_FILE)


# --------------------------------------------------
# 7. MAIN EXECUTION
# --------------------------------------------------

def main():

    print("\nStarting Dataset Inspection...")

    df = load_dataset()

    inspect_basic_information(df)

    results = investigate_dataset(df)

    inspect_problematic_records(df)

    generate_report(results)

    print("\nDataset Inspection Completed Successfully.")


if __name__ == "__main__":
    main()
