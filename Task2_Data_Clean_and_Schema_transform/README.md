# Task 2: Data Cleaning and Schema Transformation

## 1. Project Overview

This project implements a Python-based data cleaning and schema validation pipeline using the UCI Online Retail dataset.

The objective is to transform raw retail transaction data into a cleaner, consistent, and structured dataset. The pipeline identifies invalid records, removes exact duplicates, validates required columns and data types, and generates data-quality reports.

## 2. Dataset Information

**Dataset:** Online Retail

**Source:** UCI Machine Learning Repository

**Dataset URL:** https://archive.ics.uci.edu/dataset/352/online+retail

**Format:** Excel (`.xlsx`)

The dataset contains retail transaction records, including invoice details, product codes, descriptions, quantities, transaction dates, unit prices, customer identifiers, and country information.

### Input File

The scripts expect the input file to be named:

`Online Retail.xlsx`

Place the file in the `Task2_Data_Clean_and_Schema_transform/` folder before running either script.

Download the dataset from the source above if it is not already available locally.

## 3. Technologies and Dependencies

- Python
- Pandas
- OpenPyXL
- Python logging
- CSV and JSON file handling

Install the required packages using:

```bash
python -m pip install -r requirements.txt
```

## 4. Project Structure

```text
Task2_Data_Clean_and_Schema_transform/
│
├── .gitignore
├── clean_data_v2.py
├── check_output.py
├── clean_data_v1_single_function.py
├── README.md
├── requirements.txt
├── requirements-lock.txt
├── dataset/Online Retail.xlsx
│
└── output/
    ├── cleaned_retail_data.csv
    ├── rejected_records.csv
    ├── data_quality_report.json
    └── cleaning.log
```

The `output/` directory and its files are generated when the pipeline runs successfully. Their exact presence depends on whether processing has been executed.

## 5. Implementation

Two implementations are provided.

### A. Single-Function Implementation — `clean_data_v1_single_function.py`

This version presents the workflow in a single main function, with progress messages and logging to make the sequence of processing steps easier to follow

### B. Modular Implementation — `clean_data_v2.py`

This version organizes the data-cleaning workflow into separate functions. This structure makes individual processing stages easier to read, maintain, and extend.

Both scripts are designed to perform the same general data-cleaning workflow.

## 6. Data Cleaning Workflow

The pipeline performs the following stages:

1. **Load the source data:** Read the Excel dataset and check that the expected input structure is available.
2. **Validate the source schema:** Check the required columns and identify structural issues.
3. **Standardize text fields:** Clean relevant text values to improve consistency.
4. **Convert data types:** Convert fields such as quantity, unit price, and invoice date to suitable data types.
5. **Identify invalid records:** Separate records that fail the implemented data-quality rules.
6. **Remove exact duplicates:** Remove duplicate rows according to the script's duplicate-removal logic.
7. **Validate the cleaned dataset:** Check required columns, missing values in key fields, duplicate rows, and other implemented quality rules.
8. **Export results:** Save the cleaned dataset, rejected records, data-quality report, and processing logs.

The scripts preserve negative quantities where they represent returns or credit transactions. Invalid values are handled according to the cleaning rules implemented in the code.

## 7. How to Run the Project

### Step 1: Open CMD in the Task 2 folder

```bat
cd /d "E:\Python_for_Data_Engineering_&_Automation_Internship\Task2_Data_Clean_and_Schema_transform"
```

### Step 2: Install dependencies

```bat
python -m pip install -r requirements.txt
```

### Step 3: Run the modular pipeline

```bat
python clean_data_v2.py
```

### Step 4: Run the single-function implementation (optional)

```bat
python clean_data_v1_single_function.py
```

Run each script separately. Both scripts use the same expected input filename and may write to the same output paths, so running one after the other may overwrite earlier output files.

## 8. Output Files

The pipeline generates the following files under the `output/` directory:

| File | Purpose |
|---|---|
| `cleaned_retail_data.csv` | Contains the cleaned dataset after the implemented transformations and validation steps. |
| `rejected_records.csv` | Contains records rejected by the implemented cleaning rules, where applicable. |
| `data_quality_report.json` | Summarizes data-quality checks and processing results. |
| `cleaning.log` | Records pipeline execution messages, progress, and errors. |

The exact counts of cleaned and rejected records depend on the input dataset and the cleaning rules.

## 9. Data Validation

The pipeline checks key aspects of data quality, including:

- Expected number and names of columns.
- Required fields and missing values.
- Appropriate data types for relevant fields.
- Duplicate records.
- Compliance with the validation rules implemented in the scripts.

These checks help identify potential data-quality issues before the processed dataset is used for further analysis.

## 10. Error Handling and Logging

The pipeline uses progress messages and logging to make execution easier to monitor.

The log file helps identify:
- Which processing stage was reached.
- Whether a stage completed successfully.
- Data-processing errors and exceptions.
- Relevant processing and validation results.

## 11. Notes and Limitations

- The input Excel dataset must be available locally before execution.
- Install the dependencies listed in `requirements.txt`.
- Review the cleaning rules before applying the pipeline to a different dataset.
- Rejected records should be reviewed before being permanently excluded from downstream analysis.
- A successful run does not guarantee that every possible data-quality issue has been detected.

## 12. References

Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository.

Dataset: https://doi.org/10.24432/C5BW33
