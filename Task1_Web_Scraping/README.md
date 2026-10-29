# Task 1: Autonomous Web Scraper & Data Extractor

## 1. Project Overview

This project implements a Python-based web scraper to extract structured information from a multi-page website and export the collected data into CSV and JSON formats.

The project uses the Books to Scrape website as the data source. It demonstrates web requests, HTML parsing, pagination, data extraction, exception handling, logging, and structured data storage.

## 2. Objectives

- Automate the extraction of book information from web pages.
- Navigate multiple pages using pagination.
- Parse HTML content and convert it into structured records.
- Export extracted information into CSV and JSON files.
- Handle request failures and unexpected errors.
- Maintain logs to help monitor scraping activity and troubleshoot issues.

## 3. Technologies Used

- **Python 3** — Core programming language.
- **Requests** — Sending HTTP requests to the website.
- **Beautiful Soup 4** — Parsing HTML content and extracting information.
- **CSV and JSON** — Storing extracted records in structured formats.
- **Logging** — Recording execution information and errors.
- **Unittest** — Test files are maintained in the project’s `tests` directory.

## 4. Data Source

**Website:** [Books to Scrape](https://books.toscrape.com/)

Books to Scrape is a sample website intended for practising web scraping.

The scraper collects book-related information from the website. The exact fields depend on the implementation in `scraper.py`.

## 5. Project Structure

```text
Task1_Web_Scraping/
├── data/
│   ├── books-list.csv
│   └── books-list.json
├── logs/
│   └── scraper.log
├── tests/
│   ├── __init__.py
│   └── test_scraper.py
├── inspect_page.py
├── scraper.py
├── requirements.txt
└── README.md
```

## 6. Key Features

- **Automated data extraction:** Retrieves book information from web pages.
- **HTML parsing:** Uses Beautiful Soup to locate and extract relevant data.
- **Pagination:** Supports navigating multiple pages to collect records across the website.
- **HTTP request configuration:** Uses request headers to identify the client.
- **Error handling:** Handles request or parsing failures where implemented.
- **Logging:** Records relevant execution events and errors.
- **Multiple export formats:** Saves collected data in CSV and JSON formats.

## 7. Installation and Setup

### Prerequisites

- Python 3 installed on the system.
- Git, if cloning the repository.
- Internet connectivity to access the source website.

### Step 1: Navigate to the project directory

From the internship repository root, run:

```cmd
cd Task1_Web_Scraping
```

### Step 2: Create a virtual environment

```cmd
python -m venv .venv
```

### Step 3: Activate the virtual environment

```cmd
.venv\Scripts\activate
```

### Step 4: Install dependencies

```cmd
python -m pip install -r requirements.txt
```

## 8. Execution

Run the main scraper:

```cmd
python scraper.py
```

The scraper should retrieve the configured data from the website and save the output files according to the paths defined in the script.

To inspect the source page structure, run:

```cmd
python inspect_page.py
```

## 9. Output Files

| File | Purpose |
|---|---|
| `data/books-list.csv` | Stores extracted book records in CSV format. |
| `data/books-list.json` | Stores extracted book records in JSON format. |
| `logs/scraper.log` | Stores execution logs, depending on the logging configuration. |

The output files can be opened with spreadsheet software or processed further using Python.

## 10. Error Handling and Logging

The project includes logging and request/error-handling logic to support troubleshooting. These mechanisms help identify issues that may occur during website access, HTML parsing, or data extraction.

The actual errors handled and retry behaviour depend on the implementation in `scraper.py`.

## 11. Learning Outcomes

This project provides practical experience with:

- HTTP requests and response handling.
- HTML structure inspection and parsing.
- Web scraping across multiple pages.
- Structured data extraction and export.
- Python project organization and dependency management.
- Logging and exception handling.
- Maintaining a reusable project with source code, output data, and test files.

## 12. Limitations

- Scraping depends on the availability and structure of the source website.
- Changes to the website’s HTML may require updates to the extraction logic.
- Network connectivity and HTTP errors may affect execution.
- The accuracy and number of extracted records depend on the pages visited and the fields implemented in the scraper.

## 13. Future Improvements

- Add configurable scraping parameters.
- Improve validation of extracted records.
- Expand automated test coverage.
- Add summary reports for extracted data.
- Improve retry and timeout configuration where necessary.

## 14. Author

Developed as part of the **Python for Data Engineering & Automation Internship**.
