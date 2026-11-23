# Python for Data Engineering & Automation Internship

## Overview

This repository contains the Python projects and assignments completed as part of the Data Engineering & Automation Internship.

The projects focus on developing practical skills in Python programming, web scraping, data cleaning, data transformation, relational database management, automated data ingestion, validation and data processing workflows.

Each task is organized into a separate directory containing its implementation files, documentation and relevant project resources.

## Internship Tasks

### Task 1 – Autonomous Web Scraper & Data Extractor

**Objective:** Develop an automated web scraping system to collect structured information from web pages and export the extracted data into CSV and JSON formats.

**Key Implementations:**
- Web scraping using Python, Requests and BeautifulSoup.
- Automated pagination and data extraction.
- Data extraction and structuring.
- Exception handling and logging.
- Exporting extracted records into CSV and JSON.
- Basic unit testing.

**Technologies:** Python, Requests, BeautifulSoup4, CSV, JSON.

[View Task 1](./Task1_Web_Scraping/README.md)

---

### Task 2 – Data Cleaning & Schema Transformation

**Objective:** Develop a Python-based data cleaning and transformation workflow to process raw datasets, validate data quality and prepare structured data for downstream analysis.

**Key Implementations:**
- Data quality validation.
- Missing-value handling.
- Data type validation and transformation.
- Duplicate detection.
- Invalid data identification and rejection.
- Data quality reporting.
- Cleaned dataset generation.

**Technologies:** Python, Pandas.

[View Task 2](./Task2_Data_Clean_and_Schema_transform/README.md)

---

### Task 3 – Relational Database Auto-Ingestion Pipeline

**Objective:** Develop an automated relational database ingestion pipeline to transform a raw dataset into structured relational tables and load data into a SQLite database using batch processing and UPSERT operations.

**Key Implementations:**
- Dataset inspection and data transformation.
- Relational database schema creation.
- Table relationships and primary/foreign key management.
- Automated database ingestion.
- Batch processing and UPSERT operations.
- Data verification and validation.
- Transaction management and rollback testing.
- Duplicate prevention through idempotent ingestion.

**Technologies:** Python, Pandas, SQLite, SQLAlchemy, SQL.

[View Task 3](./Task3_Relational_Database_Auto_Ingestion/README.md)

---

## Repository Structure

```text
Python_for_Data_Engineering_&_Automation_Internship/
│
├── README.md
├── .gitignore
│
├── Task1_Web_Scraping/
│   ├── scraper.py
│   ├── inspect_page.py
│   ├── requirements.txt
│   ├── data/
│   ├── logs/
│   └── tests/
│
├── Task2_Data_Clean_and_Schema_transform/
│   ├── README.md
│   ├── clean_data.py
│   ├── requirements.txt
│   └── clean_data_single_function.py
│
└── Task3_Relational_Database_Auto_Ingestion/
    ├── README.md
    ├── requirements.txt
    ├── config/
    ├── data/
    ├── database/
    ├── logs/
    └── scripts/
        ├── database.py
        ├── schema.py
        ├── inspect_dataset.py
        ├── transform.py
        ├── ingest.py
        ├── verify.py
        └── test_rollback.py
```

*Note: The structure above is an illustrative overview. Actual files and folders may differ depending on the implementation and repository exclusions.*

## Skills Developed

- Python programming and automation.
- Web scraping and structured data extraction.
- Data cleaning and schema transformation.
- Data quality validation.
- SQL and relational database concepts.
- SQLite database management.
- Automated data ingestion.
- Batch processing and UPSERT logic.
- Logging and exception handling.
- Git and GitHub version control.
- Project documentation and workflow development.

## Repository

All internship assignments are maintained in a single GitHub repository, with individual task directories containing project-specific implementation and documentation.


