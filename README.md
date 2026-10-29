# Python for Data Engineering & Automation Internship

## Overview

This repository contains the Python tasks completed as part of the Python for Data Engineering & Automation Internship. The projects focus on practical data collection, data cleaning, data validation, automation, and reproducible data-processing workflows.

The repository organizes each assignment into a separate task folder to make the code, dependencies, documentation, and outputs easier to understand and maintain.

## Repository Structure

```text
Python_for_Data_Engineering_&_Automation_Internship/
│
├── README.md
├── .gitignore
│
├── Task1_Web_Scraping/
│   └── README.md and scraper project files
│
├── Task2_Data_Clean_and_Schema_transform/
│   ├── clean_data.py
│   ├── clean_data_single_function.py
│   ├── README.md
│   └── requirements.txt
│
├── Task3_...
└── Task4_...
```


## Tasks

### Task 1: Web Scraping and Data Extraction

**Objective:** Collect structured information from web pages and export it into machine-readable formats.

Key components include:
- Sending HTTP requests and parsing HTML using Python.
- Extracting structured information with Requests and Beautiful Soup.
- Handling pagination, request errors, and exceptions.
- Exporting collected records to CSV and JSON files.
- Organizing the scraper code, dependencies, and tests.

See the `Task1_Web_Scraping/` folder for the implementation and task-specific instructions.

### Task 2: Data Cleaning and Schema Transformation

**Objective:** Build a Python data-cleaning pipeline that improves data quality and validates the output schema.

The current implementation uses the UCI Online Retail dataset and Pandas.

Key components include:
- Loading and validating the source dataset.
- Standardizing text fields and converting data types.
- Identifying invalid records and separating rejected rows.
- Removing exact duplicate records.
- Checking required columns and data-quality rules.
- Exporting cleaned data, rejected records, and a JSON quality report.
- Recording processing progress and errors in logs.

Two implementations are included:
- `clean_data.py` — modular pipeline organized into separate functions.
- `clean_data_single_function.py` — single-function implementation for comparison and learning.

See `Task2_Data_Clean_and_Schema_transform/README.md` for setup instructions and details.

### Task 3: To Be Documented

Add the official task title, objective, implementation details, dependencies, and output files when the task is added.

### Task 4: To Be Documented

Add the official task title, objective, implementation details, dependencies, and output files when the task is added.

## Technologies Used

- Python
- Requests
- Beautiful Soup
- Pandas
- CSV and JSON
- Git and GitHub
- Unit testing and logging

Additional libraries may be required for individual tasks. Refer to each task's `requirements.txt` file where available.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/HarVarsh/Datheon_Python_for_Data_Engineering_-_Automation_Internship.git
cd Datheon_Python_for_Data_Engineering_-_Automation_Internship
```

### 2. Set up Python

Use a compatible Python version for the task you want to run. Creating a virtual environment is recommended.

```bash
python -m venv .venv
```

On Windows CMD:

```bat
.venv\Scripts\activate
```

### 3. Install dependencies

Install the dependencies listed in the relevant task's `requirements.txt` file.

For example, for Task 2:

```bash
cd Task2_Data_Clean_and_Schema_transform
python -m pip install -r requirements.txt
```

### 4. Run a task

Follow the instructions in that task's README. Some tasks may require a source dataset or other input files before execution.

## Data and Reproducibility

- Follow the dataset source and usage instructions documented in each task.
- Do not commit credentials, API keys, virtual environments, or unnecessary generated files.
- Keep task-specific setup and execution instructions in the corresponding folder.
- Document assumptions, validation rules, dependencies, and output locations.

## Learning Objectives

This repository demonstrates practical experience with Python scripting, data extraction, data transformation, data quality checks, error handling, logging, testing, and version control.

