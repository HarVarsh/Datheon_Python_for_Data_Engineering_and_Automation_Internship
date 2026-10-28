from pathlib import Path
import json
import logging

import pandas as pd

# 1. CONFIGURATION

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "dataset/Online Retail.xlsx"
OUTPUT_DIR = BASE_DIR / "output"

CLEAN_FILE = OUTPUT_DIR / "cleaned_retail_data.csv"
REJECTED_FILE = OUTPUT_DIR / "rejected_records.csv"
REPORT_FILE = OUTPUT_DIR / "data_quality_report.json"
LOG_FILE = OUTPUT_DIR / "cleaning.log"

EXPECTED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
    ]

REQUIRED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s -%(message)s",
    force=True,
)

# 2. LOAD AND CHECK THE RAW DATA

def clean_data():
    report = {
        "input_file": INPUT_FILE.name,
        "currency":"GBP",
        "steps":{},
        "validation_errors":[],
    }


    if not INPUT_FILE.exists():
        raise FileNotFoundError( 
            f"Dataset not found: {INPUT_FILE}\n"
            "Place Online Retail.xlsx beside clean_data.py." 
       )

    df = pd.read_excel(INPUT_FILE, sheet_name=0)

    #Standardize column names
    df.columns = df.columns.astype(str).str.strip()

    if df.columns.duplicated().any():
        raise ValueError("Duplicate column names found.")

    missing_columns = sorted (
        set(EXPECTED_COLUMNS) - set(df.columns) 
    )

    extra_columns = sorted (
        set(df.columns) - set(EXPECTED_COLUMNS)
    )

    if missing_columns:
        raise ValueError(
            f"Required dataset columns are missing: "
            f"{missing_columns}"
        )

    #Keep only the documented output schema
    df = df[EXPECTED_COLUMNS].copy()

    report["unexpected_columns_removed"] = extra_columns
    report["rows_before_cleaning"] = int(len(df))
    report["columns"] = EXPECTED_COLUMNS
    report["nulls_berfore_cleaning"]={
        str(k) : int(v)
        for k,v in df.isna().sum().items()
    }

    logging.info("Loaded %s rows.",len(df))


    # 3. STANDARDIZE TEXT FIELDS

    text_columns = [
        "InvoiceNo",
        "StockCode",
        "Description",
        "CustomerID",
        "Country",
    ]

    for col in text_columns:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace("",pd.NA)


    # Remove the trailing .0 from Excel-style customer IDs.
    # Preserve missing IDs and do not turn IDs into floats.
    df["CustomerID"] = df["CustomerID"].str.replace(
        r"\.0$","",regex=True
    )

    report["steps"]["text_standardization"] = "completed"


    # 4.NORMALIZE NUMERIC VALUES AND DATES

    # Convert quantity to numeric
    quantity = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )

    # Normalize currency text such as £1,234.50.
    # The original dataset normally stores UnitPrice as numeric.
    price_text=(
        df["UnitPrice"].astype("string")
        .str.replace(r"[£,\s]","",regex=True)   
    )

    price = pd.to_numeric(price_text, errors = "coerce")

    # Dataset dates may already be Excel datetime values.
    # Day-first parsing also supports strings like 01/12/2010.
    dates = pd.to_datetime(
        df["InvoiceDate"],
        errors = "coerce",
        dayfirst =True,
    )

    # Numeric fields must be valid; quantity must be an integer.
    invalid_quantity = (
        quantity.isna() | (quantity % 1 != 0)
    )

    invalid_price = (
        price.isna() | 
        ~price.map(lambda x : pd.notna(x) and x >= 0)
    )

    invalid_date = dates.isna()

    # Essential identifiers cannot be blank.
    missing_identifier = (
        df["InvoiceNo"].isna()
        | df ["StockCode"].isna()
    )

    invalid_mask = (
        invalid_quantity | 
        invalid_price |
        invalid_date | 
        missing_identifier
    )

    rejected = df.loc[invalid_mask].copy()
    rejected["RejectReason"] = ""

    rejected.loc[
        invalid_quantity[invalid_mask],
        "RejectReason",
    ] += "Invalid Quantity; "

    rejected.loc[
        invalid_price[invalid_mask],
        "RejectReason",
    ] += "Invalid UnitPrice; "

    rejected.loc[
        invalid_date[invalid_mask],
        "RejectReason",
    ] += "Invalid InvoiceDate; "

    rejected.loc[
        missing_identifier[invalid_mask],
        "RejectReason",
    ] += "Missing InvoiceNo or StockCode; "

    # Keep valid records for transformation.
    df = df.loc[~invalid_mask].copy()

    quantity = quantity.loc[~invalid_mask]
    price = price.loc[~invalid_mask]
    dates = dates.loc[~invalid_mask]

    df["Quantity"] = quantity.astype("int64")
    df["UnitPrice"] = price.astype("float64")
    df["InvoiceDate"] = dates


    # Missing customer IDs are allowed: some transactions
    # do not identify a customer
    # Missing descriptions/countries are retained as unknown.
    df["Description"] = df["Description"].fillna("UNKNOWN")
    df["Country"] = df["Country"].fillna("UNKNOWN")

    # CustomerID remains a string identifier, not a number
    # Missing IDs remain blank in the CSV.
    report["steps"]["numeric_and_date_conversion"] = {
        "invalid_quantity_rows" : int(invalid_quantity.sum()),
        "invalid_price_rows" : int(invalid_price.sum()),
        "invalid_date_rows" : int(invalid_date.sum()),
        "missing_identifier_rows" : int(missing_identifier.sum()),
        "rows_rejected" : int(invalid_mask.sum()),
    } 

    logging.info(
        "Rejected %s invalid rows.",
        invalid_mask.sum(),
    )


    # 5. REMOVE EXACT DUPLICATES

    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    report["exact_duplicate_rows_removed"] = duplicate_count

    logging.info("Rejected %s exact duplicate rows.", duplicate_count,)


    # 6. FINAL SCHEMA TRANSFORMATION

    df["InvoiceNo"] = df["InvoiceNo"].astype("string")
    df["StockCode"] = df["StockCode"].astype("string")
    df["Description"] = df["Description"].astype("string")
    df["CustomerID"] = df["CustomerID"].astype("string")
    df["Country"] = df["Country"].astype("string")

    df["Quantity"] = df["Quantity"].astype("int64")
    df["UnitPrice"] = df["UnitPrice"].astype("float64")

    # Store dates in a consistent, unambiguous format.
    df["InvoiceDate"] = df["InvoiceDate"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    # Currency is documented as GBP; do not perform an exchange-rate conversion
    df = df[EXPECTED_COLUMNS].reset_index(drop = True)


    # 7. VALIDATE THE CLEANED DATA

    validation_errors = []

    if list(df.columns) != EXPECTED_COLUMNS:
        validation_errors.append("Output column order is incorrect.")

    if df[REQUIRED_COLUMNS].isna().any().any():
        validation_errors.append("Required fields contain null values.")

    if not pd.api.types.is_integer_dtype(df["Quantity"]):
        validation_errors.append("Quantity is not an integer.")

    if not pd.api.types.is_numeric_dtype(df["UnitPrice"]):
        validation_errors.append("UnitPrice is not numeric.")
    

    parsed_dates = pd.to_datetime(
        df["InvoiceDate"],
        format = "%Y-%m-%d %H:%M:%S",
        errors = "coerce",
    )

    if parsed_dates.isna().any():
        validation_errors.append("Invalid output dates found.")

    if df.duplicated().any():
        validation_errors.append("Exact duplicate rows remain.")

    if (df["UnitPrice"] < 0).any():
        validation_errors.append("Negative prices remain.")

    report["validation_errors"] = validation_errors
    report["schema_validation"] = (
        "PASS" if not validation_errors else "FAIL"
    )

    if validation_errors:
        logging.error("Validation failed: %s", validation_errors)
        raise ValueError("Output validation failed. Check the quality report.")

    # 8. EXPORT DATA AND QUALITY REPORT
    df.to_csv(CLEAN_FILE, index=False)

    # Export rejected rows for investigation
    rejected.to_csv(REJECTED_FILE, index=False)

    report["rows_after_cleaning"] = int(len(df))
    report["rows_rejected"] = int(len(rejected))
    report["rows_removed_as_duplicates"] = duplicate_count
    report["nulls_after_cleaning"] = {
        str(k) : int(v)
        for k,v in df.isna().sum().items()
    }
    report["output_file"] = CLEAN_FILE.name
    report["rejected_file"] = REJECTED_FILE.name
    report["output_dtypes"] = {
        str(k): str(v) for k,v in df.dtypes.items()
    }
    report["output_currency"] = "GBP"
    report["status"] = "SUCCESS"

    with open(REPORT_FILE, "w", encoding = "utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    logging.info("Cleaning completed successfully.")
    logging.info("Output saved to %s", CLEAN_FILE)

    print("\nDATA CLEANING COMPLETED")
    print("-" * 40)
    print("Input rows:", report["rows_before_cleaning"])
    print("Cleaned rows:", report["rows_after_cleaning"])
    print("Rejected rows:", report["rows_rejected"])
    print("Duplicates removed:", duplicate_count)
    print("Schema validation:", report["schema_validation"])
    print("Cleaned data:", CLEAN_FILE)
    print("Rejected records:", REJECTED_FILE)
    print("Quality report:", REPORT_FILE)
    print("Log File:", LOG_FILE)


if __name__ == "__main__":
    try:
        clean_data()
    except Exception:
        logging.exception("Data Cleaning failed.")
        raise
