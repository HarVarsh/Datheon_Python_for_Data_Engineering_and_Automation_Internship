
import logging
from pathlib import Path
from decimal import Decimal

import pandas as pd

from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from database import engine
from schema import (
    metadata,
    customers,
    products,
    sales_transactions
)
from transform import transform_data


# --------------------------------------------------
# 1. PROJECT PATHS AND CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "ingestion.log"

BATCH_SIZE = 100


# --------------------------------------------------
# 2. LOGGING CONFIGURATION
# --------------------------------------------------

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# --------------------------------------------------
# 3. CONVERT PANDAS VALUES INTO SQLITE VALUES
# --------------------------------------------------

def convert_value(value):
    """
    Convert Pandas and NumPy values into standard
    Python values supported by SQLite.
    """

    # Convert missing values into SQL NULL
    if value is None or pd.isna(value):
        return None

    # Convert Pandas Timestamp into Python datetime
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    # Convert NumPy scalar values into Python values
    if hasattr(value, "item"):
        value = value.item()

    return value


def normalize_identifier(value):
    """
    Convert identifiers into strings without
    unwanted decimal suffixes.
    """

    value = convert_value(value)

    if value is None:
        return None

    if isinstance(value, float) and value.is_integer():
        value = int(value)

    return str(value).strip()


def dataframe_to_records(dataframe):
    """
    Convert a DataFrame into a list of dictionaries.
    Replace Pandas missing values with Python None.
    """

    records = dataframe.to_dict(orient="records")

    clean_records = []

    for record in records:
        clean_record = {
            column: convert_value(value)
            for column, value in record.items()
        }

        clean_records.append(clean_record)

    return clean_records


# --------------------------------------------------
# 4. BATCH UPSERT FUNCTION
# --------------------------------------------------

def batch_upsert(
    connection,
    table,
    records,
    key,
    update_columns
):
    """
    Insert records in batches.

    If the primary key already exists:
    - Update specified columns, or
    - Do nothing when update_columns is empty.
    """

    total_records = len(records)

    for start in range(0, total_records, BATCH_SIZE):

        batch = records[start:start + BATCH_SIZE]

        if not batch:
            continue

        statement = sqlite_insert(table).values(batch)

        if update_columns:

            statement = statement.on_conflict_do_update(
                index_elements=[key],
                set_={
                    column: getattr(statement.excluded, column)
                    for column in update_columns
                }
            )

        else:

            statement = statement.on_conflict_do_nothing(
                index_elements=[key]
            )

        connection.execute(statement)

        logging.info(
            "Processed batch: %s records",
            len(batch)
        )


# --------------------------------------------------
# 5. PREPARE CUSTOMER, PRODUCT AND SALES RECORDS
# --------------------------------------------------

def prepare_records(dataframe):

    required_columns = [
        "source_row_id",
        "InvoiceNo",
        "StockCode",
        "CustomerID",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "Country",
        "Description"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # ------------------------------
    # CUSTOMER RECORDS
    # ------------------------------

    customer_df = dataframe.loc[
        dataframe["CustomerID"].notna(),
        ["CustomerID"]
    ].copy()

    customer_df["customer_id"] = customer_df[
        "CustomerID"
    ].apply(normalize_identifier)

    customer_df = customer_df[
        ["customer_id"]
    ].drop_duplicates()

    customer_records = dataframe_to_records(customer_df)

    # ------------------------------
    # PRODUCT RECORDS
    # ------------------------------

    product_df = dataframe[
        ["StockCode", "Description"]
    ].copy()

    product_df["stock_code"] = product_df[
        "StockCode"
    ].apply(normalize_identifier)

    product_df = product_df[
        ["stock_code", "Description"]
    ].rename(
        columns={"Description": "description"}
    )

    product_df = product_df.drop_duplicates(
        subset=["stock_code"],
        keep="last"
    )

    product_records = dataframe_to_records(product_df)

    # ------------------------------
    # SALES TRANSACTION RECORDS
    # ------------------------------

    sales_df = dataframe[
        [
            "source_row_id",
            "InvoiceNo",
            "StockCode",
            "CustomerID",
            "Quantity",
            "InvoiceDate",
            "UnitPrice",
            "Country"
        ]
    ].copy()

    sales_df = sales_df.rename(
        columns={
            "InvoiceNo": "invoice_no",
            "StockCode": "stock_code",
            "CustomerID": "customer_id",
            "Quantity": "quantity",
            "InvoiceDate": "invoice_date",
            "UnitPrice": "unit_price",
            "Country": "country"
        }
    )

    sales_df["stock_code"] = sales_df[
        "stock_code"
    ].apply(normalize_identifier)

    sales_df["customer_id"] = sales_df[
        "customer_id"
    ].apply(normalize_identifier)

    sales_df["invoice_no"] = sales_df[
        "invoice_no"
    ].apply(normalize_identifier)

    sales_records = dataframe_to_records(sales_df)

    return (
        customer_records,
        product_records,
        sales_records
    )


# --------------------------------------------------
# 6. MAIN INGESTION PROCESS
# --------------------------------------------------

def run_ingestion():

    try:

        logging.info("INGESTION STARTED")
        print("Starting database ingestion...")

        # Create tables if they do not already exist
        metadata.create_all(engine)

        # Read and transform the source dataset
        print("Preparing dataset...")

        dataframe = transform_data()

        if dataframe is None or dataframe.empty:
            raise ValueError(
                "No valid records available for ingestion."
            )

        logging.info(
            "Total valid records: %s",
            len(dataframe)
        )

        # Prepare all three sets of records
        print("Preparing customer, product and sales records...")

        (
            customer_records,
            product_records,
            sales_records
        ) = prepare_records(dataframe)

        print(f"Customer records: {len(customer_records)}")
        print(f"Product records: {len(product_records)}")
        print(f"Sales records: {len(sales_records)}")

        logging.info(
            "Customer records prepared: %s",
            len(customer_records)
        )

        logging.info(
            "Product records prepared: %s",
            len(product_records)
        )

        logging.info(
            "Sales records prepared: %s",
            len(sales_records)
        )

        # One transaction for all three tables.
        # If any operation fails, all changes are rolled back.
        with engine.begin() as connection:

            print("Inserting customer records...")

            batch_upsert(
                connection,
                customers,
                customer_records,
                "customer_id",
                []
            )

            print("Inserting product records...")

            batch_upsert(
                connection,
                products,
                product_records,
                "stock_code",
                ["description"]
            )

            print("Inserting sales transaction records...")

            batch_upsert(
                connection,
                sales_transactions,
                sales_records,
                "source_row_id",
                [
                    "invoice_no",
                    "stock_code",
                    "customer_id",
                    "quantity",
                    "invoice_date",
                    "unit_price",
                    "country"
                ]
            )

        logging.info("INGESTION COMPLETED SUCCESSFULLY")

        print("\nDatabase ingestion completed successfully.")

    except Exception:

        logging.exception("INGESTION FAILED")

        print(
            "\nDatabase ingestion failed. "
            "Check logs/ingestion.log for details."
        )

        raise

    finally:

        engine.dispose()


# --------------------------------------------------
# 7. SCRIPT EXECUTION
# --------------------------------------------------

if __name__ == "__main__":
    run_ingestion()
