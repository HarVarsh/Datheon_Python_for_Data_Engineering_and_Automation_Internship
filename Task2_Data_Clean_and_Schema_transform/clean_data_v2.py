from __future__ import annotations

import json
import logging
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


# ============================================================
# 1. CONFIGURATION
# ============================================================

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

TEXT_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "CustomerID",
    "Country",
]


# ============================================================
# 2. LOGGING AND PROGRESS UTILITIES
# ============================================================

def configure_logging() -> logging.Logger:
    """Configure logging to both the console and a persistent log file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("retail_data_cleaning")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def log_step(logger: logging.Logger, step_number: int, message: str) -> None:
    """Log and print a consistent step marker."""
    logger.info("STEP %02d | %s", step_number, message)


def print_run_header(run_id: str, started_at: datetime) -> None:
    """Print a clear visual boundary for each execution."""
    print("\n" + "=" * 72)
    print("DATA CLEANING RUN STARTED")
    print(f"Run ID   : {run_id}")
    print(f"Started  : {started_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 72, flush=True)


def print_run_footer(
    run_id: str,
    status: str,
    elapsed_seconds: float,
) -> None:
    """Print a clear completion/failure marker for each execution."""
    print("-" * 72)
    print(f"DATA CLEANING RUN {status}")
    print(f"Run ID          : {run_id}")
    print(f"Total duration  : {elapsed_seconds:.2f} seconds")
    print("=" * 72 + "\n", flush=True)


# ============================================================
# 3. DATA LOADING AND SOURCE SCHEMA CHECKS
# ============================================================

def load_source_data(logger: logging.Logger) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load the Excel source and confirm that expected columns exist."""
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}\n"
            "Place 'Online Retail.xlsx' beside clean_data.py."
        )

    logger.info("Reading source file: %s", INPUT_FILE.name)
    df = pd.read_excel(INPUT_FILE, sheet_name=0)
    df.columns = df.columns.astype(str).str.strip()

    if df.columns.duplicated().any():
        duplicate_names = df.columns[df.columns.duplicated()].tolist()
        raise ValueError(f"Duplicate column names found: {duplicate_names}")

    missing_columns = sorted(set(EXPECTED_COLUMNS) - set(df.columns))
    extra_columns = sorted(set(df.columns) - set(EXPECTED_COLUMNS))

    if missing_columns:
        raise ValueError(
            f"Required columns are missing from the source: {missing_columns}"
        )

    df = df[EXPECTED_COLUMNS].copy()

    source_info = {
        "input_file": INPUT_FILE.name,
        "rows_before_cleaning": int(len(df)),
        "columns": EXPECTED_COLUMNS,
        "unexpected_columns_removed": extra_columns,
        "nulls_before_cleaning": {
            str(column): int(count)
            for column, count in df.isna().sum().items()
        },
    }

    logger.info(
        "Source loaded successfully: %s rows, %s columns.",
        f"{len(df):,}",
        len(df.columns),
    )
    if extra_columns:
        logger.warning("Unexpected source columns ignored: %s", extra_columns)

    return df, source_info


# ============================================================
# 4. TEXT STANDARDIZATION
# ============================================================

def standardize_text(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """Trim whitespace and standardize empty text values to missing values."""
    result = df.copy()

    for column in TEXT_COLUMNS:
        result[column] = result[column].astype("string").str.strip()
        result[column] = result[column].replace("", pd.NA)

    # IDs are identifiers, so preserve them as strings rather than numbers.
    result["CustomerID"] = result["CustomerID"].str.replace(
        r"\.0$", "", regex=True
    )

    logger.info("Text fields standardized; surrounding whitespace removed.")
    return result


# ============================================================
# 5. TYPE CONVERSION AND INVALID-ROW SEPARATION
# ============================================================

def normalize_types_and_reject_invalid_rows(
    df: pd.DataFrame,
    logger: logging.Logger,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    """Normalize quantity, price and date fields; separate invalid rows."""
    result = df.copy()

    quantity = pd.to_numeric(result["Quantity"], errors="coerce")

    # Accept values such as £1,234.50 if currency-formatted text is supplied.
    price_text = (
        result["UnitPrice"]
        .astype("string")
        .str.replace(r"[£,\s]", "", regex=True)
    )
    price = pd.to_numeric(price_text, errors="coerce")

    dates = pd.to_datetime(
        result["InvoiceDate"],
        errors="coerce",
        dayfirst=True,
    )

    invalid_quantity = quantity.isna() | (quantity % 1 != 0)
    invalid_price = price.isna() | (price < 0)
    invalid_date = dates.isna()
    missing_identifier = (
        result["InvoiceNo"].isna() | result["StockCode"].isna()
    )

    invalid_mask = (
        invalid_quantity
        | invalid_price
        | invalid_date
        | missing_identifier
    )

    rejected = result.loc[invalid_mask].copy()
    rejected["RejectReason"] = ""

    # Add every applicable reason, so a row with multiple problems
    # contains all of its reasons in the rejection report.
    reason_masks = [
        (invalid_quantity, "Invalid Quantity; "),
        (invalid_price, "Invalid UnitPrice; "),
        (invalid_date, "Invalid InvoiceDate; "),
        (missing_identifier, "Missing InvoiceNo or StockCode; "),
    ]

    for mask, reason in reason_masks:
        rejected.loc[mask.loc[invalid_mask], "RejectReason"] += reason

    valid_index = result.index[~invalid_mask]
    cleaned = result.loc[valid_index].copy()
    cleaned["Quantity"] = quantity.loc[valid_index].astype("int64")
    cleaned["UnitPrice"] = price.loc[valid_index].astype("float64")
    cleaned["InvoiceDate"] = dates.loc[valid_index]

    # Missing optional fields are retained but made explicit.
    cleaned["Description"] = cleaned["Description"].fillna("UNKNOWN")
    cleaned["Country"] = cleaned["Country"].fillna("UNKNOWN")
    # Missing CustomerID is allowed because the source may not identify a customer.

    counts = {
        "invalid_quantity_rows": int(invalid_quantity.sum()),
        "invalid_price_rows": int(invalid_price.sum()),
        "invalid_date_rows": int(invalid_date.sum()),
        "missing_identifier_rows": int(missing_identifier.sum()),
        "rows_rejected": int(invalid_mask.sum()),
    }

    logger.info(
        "Type conversion complete: %s invalid rows separated for review.",
        f"{counts['rows_rejected']:,}",
    )
    logger.info(
        "Invalid-condition counts (overlap is possible): quantity=%s, price=%s, date=%s, identifiers=%s.",
        counts["invalid_quantity_rows"],
        counts["invalid_price_rows"],
        counts["invalid_date_rows"],
        counts["missing_identifier_rows"],
    )

    return cleaned, rejected, counts


# ============================================================
# 6. DUPLICATE REMOVAL
# ============================================================

def remove_exact_duplicates(
    df: pd.DataFrame,
    logger: logging.Logger,
) -> tuple[pd.DataFrame, int]:
    """Remove exact duplicate records while preserving distinct invoice lines."""
    duplicate_count = int(df.duplicated().sum())
    cleaned = df.drop_duplicates().copy()

    logger.info(
        "Exact duplicate removal complete: %s duplicate rows removed.",
        f"{duplicate_count:,}",
    )
    return cleaned, duplicate_count


# ============================================================
# 7. FINAL SCHEMA TRANSFORMATION
# ============================================================

def enforce_output_schema(
    df: pd.DataFrame,
    logger: logging.Logger,
) -> pd.DataFrame:
    """Enforce output column order and intended column data types."""
    result = df.copy()

    for column in TEXT_COLUMNS:
        result[column] = result[column].astype("string")

    result["Quantity"] = result["Quantity"].astype("int64")
    result["UnitPrice"] = result["UnitPrice"].astype("float64")

    # Standardized, unambiguous text format for CSV output.
    result["InvoiceDate"] = result["InvoiceDate"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    result = result[EXPECTED_COLUMNS].reset_index(drop=True)
    logger.info("Output schema transformation complete.")
    return result


# ============================================================
# 8. FINAL DATA QUALITY VALIDATION
# ============================================================

def validate_cleaned_data(
    df: pd.DataFrame,
    logger: logging.Logger,
) -> list[str]:
    """Return validation errors; an empty list means all checks passed."""
    errors: list[str] = []

    if list(df.columns) != EXPECTED_COLUMNS:
        errors.append("Output column names or order do not match the schema.")

    if df[REQUIRED_COLUMNS].isna().any().any():
        errors.append("Required fields contain missing values.")

    if not pd.api.types.is_integer_dtype(df["Quantity"]):
        errors.append("Quantity is not an integer dtype.")

    if not pd.api.types.is_numeric_dtype(df["UnitPrice"]):
        errors.append("UnitPrice is not numeric.")

    if df["UnitPrice"].isna().any():
        errors.append("UnitPrice contains missing values.")

    if (df["UnitPrice"] < 0).any():
        errors.append("UnitPrice contains negative values.")

    parsed_dates = pd.to_datetime(
        df["InvoiceDate"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce",
    )
    if parsed_dates.isna().any():
        errors.append("InvoiceDate contains invalid output dates.")

    if df.duplicated().any():
        errors.append("Exact duplicate rows remain.")

    if errors:
        logger.error("Schema/data validation FAILED: %s", "; ".join(errors))
    else:
        logger.info("Schema/data validation PASSED.")

    return errors


# ============================================================
# 9. OUTPUT FILES AND QUALITY REPORT
# ============================================================

def write_outputs(
    cleaned: pd.DataFrame,
    rejected: pd.DataFrame,
    report: dict[str, Any],
    logger: logging.Logger,
) -> None:
    """Write cleaned data, rejected rows and JSON quality report."""
    cleaned.to_csv(CLEAN_FILE, index=False)
    logger.info("Cleaned dataset saved: %s", CLEAN_FILE)

    rejected.to_csv(REJECTED_FILE, index=False)
    logger.info("Rejected-records file saved: %s", REJECTED_FILE)

    report["rows_after_cleaning"] = int(len(cleaned))
    report["rows_rejected"] = int(len(rejected))
    report["nulls_after_cleaning"] = {
        str(column): int(count)
        for column, count in cleaned.isna().sum().items()
    }
    report["output_file"] = CLEAN_FILE.name
    report["rejected_file"] = REJECTED_FILE.name
    report["output_dtypes"] = {
        str(column): str(dtype)
        for column, dtype in cleaned.dtypes.items()
    }
    report["output_currency"] = "GBP"

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    logger.info("Data quality report saved: %s", REPORT_FILE)


# ============================================================
# 10. PIPELINE ORCHESTRATION
# ============================================================

def run_pipeline(logger: logging.Logger, run_id: str) -> None:
    """Coordinate the pipeline stages in a readable, maintainable order."""
    report: dict[str, Any] = {
        "run_id": run_id,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "currency": "GBP",
        "steps": {},
        "validation_errors": [],
    }

    log_step(logger, 1, "Load source data and check required columns")
    df, source_info = load_source_data(logger)
    report.update(source_info)
    report["steps"]["load_and_source_schema_check"] = "completed"

    log_step(logger, 2, "Standardize text fields")
    df = standardize_text(df, logger)
    report["steps"]["text_standardization"] = "completed"

    log_step(logger, 3, "Normalize types and separate invalid rows")
    df, rejected, conversion_counts = normalize_types_and_reject_invalid_rows(
        df, logger
    )
    report["steps"]["type_conversion_and_rejection"] = conversion_counts

    log_step(logger, 4, "Remove exact duplicate records")
    df, duplicate_count = remove_exact_duplicates(df, logger)
    report["exact_duplicate_rows_removed"] = duplicate_count
    report["steps"]["duplicate_removal"] = "completed"

    log_step(logger, 5, "Enforce output schema")
    df = enforce_output_schema(df, logger)
    report["steps"]["output_schema_transformation"] = "completed"

    log_step(logger, 6, "Validate cleaned data")
    validation_errors = validate_cleaned_data(df, logger)
    report["validation_errors"] = validation_errors
    report["schema_validation"] = "PASS" if not validation_errors else "FAIL"

    if validation_errors:
        # Save a report even when final validation fails.
        report["status"] = "VALIDATION_FAILED"
        report["rows_after_cleaning"] = int(len(df))
        report["rows_rejected"] = int(len(rejected))
        report["output_file"] = CLEAN_FILE.name
        report["rejected_file"] = REJECTED_FILE.name
        with open(REPORT_FILE, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=4, ensure_ascii=False)
        raise ValueError(
            "Output validation failed. Review output/data_quality_report.json "
            "and output/cleaning.log."
        )

    log_step(logger, 7, "Write cleaned data, rejected rows and quality report")
    report["status"] = "SUCCESS"
    write_outputs(df, rejected, report, logger)
    report["steps"]["output_export"] = "completed"

    # Rewrite the report to include the final step status.
    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    logger.info(
        "Run summary: input=%s, cleaned=%s, rejected=%s, duplicates_removed=%s.",
        f"{report['rows_before_cleaning']:,}",
        f"{report['rows_after_cleaning']:,}",
        f"{report['rows_rejected']:,}",
        f"{report['exact_duplicate_rows_removed']:,}",
    )


def main() -> int:
    """Application entry point; controls run boundaries and exit status."""
    run_id = uuid.uuid4().hex[:8].upper()
    started_at = datetime.now()
    start_time = time.perf_counter()
    logger = configure_logging()

    print_run_header(run_id, started_at)
    logger.info("=" * 24 + " RUN START | ID=%s " + "=" * 24, run_id)

    try:
        run_pipeline(logger, run_id)
        elapsed = time.perf_counter() - start_time
        logger.info(
            "RUN COMPLETED SUCCESSFULLY | ID=%s | duration=%.2f seconds",
            run_id,
            elapsed,
        )
        print_run_footer(run_id, "COMPLETED SUCCESSFULLY", elapsed)
        logger.info("RUN END | ID=%s\n", run_id)
        return 0

    except Exception:
        elapsed = time.perf_counter() - start_time
        logger.exception("RUN FAILED | ID=%s", run_id)
        print_run_footer(run_id, "FAILED", elapsed)
        logger.info("RUN END (FAILED) | ID=%s\n", run_id)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
