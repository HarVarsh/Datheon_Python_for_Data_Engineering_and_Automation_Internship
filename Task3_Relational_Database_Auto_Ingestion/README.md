# Task 3 – Relational Database Auto-Ingestion & Upsert Engine

## 1. Project Overview

This project implements an automated database ingestion system using Python, SQLAlchemy, and SQLite.

The system reads structured retail transaction data, transforms and prepares the records, and loads them into relational database tables.

It supports batch insertion, UPSERT operations, primary key constraints, foreign key relationships, and transaction safety.

## 2. Project Objective

The main objectives are:

- Establish a connection to a relational database.
- Create structured database tables with primary keys and foreign key constraints.
- Read and prepare retail transaction data for database ingestion.
- Insert records using batch processing.
- Implement UPSERT functionality to handle existing records.
- Maintain transaction consistency using database transactions.
- Verify database records using SQL queries.

## 3. Dataset Information

**Dataset:** Online Retail

**Source:** UCI Machine Learning Repository

**Dataset URL:** https://archive.ics.uci.edu/dataset/352/online+retail

The dataset contains retail transaction information, including:

- InvoiceNo
- StockCode
- Description
- Quantity
- InvoiceDate
- UnitPrice
- CustomerID
- Country

The source dataset contains missing customer identifiers and negative quantities. These records are handled according to the transformation rules rather than automatically discarded.

## 4. Technologies Used

- Python
- SQLite
- SQLAlchemy
- Pandas
- OpenPyXL
- Logging
- DB Browser for SQLite
- GitHub Desktop

## 5. Project Structure

```text
Task3_Relational_Database_Auto_Ingestion/
│
├── config/
│
├── data/
│   ├── raw/
│   │   └── Online Retail.xlsx
│   │
│   └── processed/
│       ├── dataset_inspection.txt
│       ├── rejected_rows.csv
│       └── database_verification.txt
│
├── database/
│   └── retail.db
│
├── logs/
│   └── ingestion.log
│
├── scripts/
│   ├── database.py
│   ├── schema.py
│   ├── inspect_dataset.py
│   ├── transform.py
│   ├── ingest.py
│   ├── verify.py
│   └── test_rollback.py
│
├── README.md
└── requirements.txt
```

## 6. Database Schema Design

The database contains three relational tables.

### 6.1 Customers

Stores unique customer identifiers.

| Column | Description |
|---|---|
| customer_id | Primary key |

### 6.2 Products

Stores product identifiers and descriptions.

| Column | Description |
|---|---|
| stock_code | Primary key |
| description | Product description |

### 6.3 Sales Transactions

Stores retail transaction details.

| Column | Description |
|---|---|
| source_row_id | Primary key |
| invoice_no | Invoice identifier |
| stock_code | Foreign key referencing products |
| customer_id | Nullable foreign key referencing customers |
| quantity | Transaction quantity |
| invoice_date | Transaction date and time |
| unit_price | Product unit price |
| country | Customer country |

## 7. Data Preparation

The transformation process prepares the source dataset before database insertion.

The process includes:

- Reading the Excel dataset.
- Validating required fields.
- Converting numeric and date columns into appropriate data types.
- Preserving source row identifiers.
- Handling missing customer identifiers.
- Retaining negative quantities representing returns or cancellations.
- Separating rejected records for review.

Missing customer identifiers are represented as SQL NULL in the database.

## 8. Database Ingestion and UPSERT

The ingestion module loads the prepared records into the three database tables.

### Batch Processing

Records are divided into batches to support controlled database insertion.

### UPSERT Implementation

The system uses SQLite UPSERT functionality through SQLAlchemy.

| Table | Conflict key | Conflict handling |
|---|---|---|
| customers | customer_id | Do nothing if the record already exists |
| products | stock_code | Update the product description |
| sales_transactions | source_row_id | Update transaction details |

This approach prevents duplicate records when the same source dataset is ingested repeatedly.

## 9. Transaction Safety

All three table ingestion operations are executed within a single SQLAlchemy transaction.

The transaction uses:

`with engine.begin() as connection:`

If an error occurs during ingestion, the transaction is rolled back to prevent partially committed database changes.

## 10. Execution Instructions

Run the following commands from the Task 3 project directory.

### Step 1 – Activate the virtual environment

```cmd
.venv\Scripts\activate
```

### Step 2 – Create the database schema

```cmd
python scripts\schema.py
```

### Step 3 – Inspect the dataset

```cmd
python scripts\inspect_dataset.py
```

### Step 4 – Execute the ingestion process

```cmd
python scripts\ingest.py
```

### Step 5 – Verify database records

```cmd
python scripts\verify.py
```

### Step 6 – Test transaction rollback

```cmd
python scripts\test_rollback.py
```

## 11. Database Verification

The database was checked using DB Browser for SQLite.

The following checks were performed:

1. Verification of customer, product, and sales transaction record counts.
2. Duplicate transaction verification using source_row_id.
3. Foreign key constraint verification using PRAGMA foreign_key_check.
4. Verification of missing customer identifiers.
5. Verification of negative transaction quantities.
6. Idempotency testing through repeated ingestion.
7. Transaction rollback testing.

### Verification Results

| Verification | Actual result |
|---|---|
| Customer records | [4372] |
| Product records | [4070] |
| Sales transactions | [541909] |
| Duplicate transaction IDs | [0] |
| Foreign key violations | [0] |
| Idempotency | [Pass] |
| Transaction rollback | [Pass] |

## 12. Idempotency Testing

The ingestion script was executed twice using the same source dataset.

The record counts of all three tables were compared before and after the second execution.

The expected result is that customer, product, and sales transaction counts remain unchanged.

This verifies that the UPSERT implementation handles repeated ingestion without creating duplicate records.

## 13. Conclusion

The project demonstrates an automated relational database ingestion workflow using Python, SQLAlchemy, and SQLite.

It implements structured database schemas, batch processing, UPSERT functionality, transaction safety, and SQL-based verification.

The system is designed to support reliable and repeatable ingestion of structured retail transaction data.