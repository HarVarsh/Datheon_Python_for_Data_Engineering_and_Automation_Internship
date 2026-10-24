# Python for Data Engineering & Automation Internship

## Project: Autonomous Web Scraper & Data Extractor

### Overview

A Python web-scraping project that extracts structured product data from a paginated website using Requests and Beautiful Soup. The project cleans and validates the extracted records and exports the results to CSV and JSON.

### Objectives

- Retrieve HTML from multiple pages using HTTP requests.
- Parse HTML elements using CSS selectors.
- Extract product titles, prices, ratings, availability, and URLs.
- Handle HTTP failures, retries, and incomplete records.
- Remove duplicate records and normalize data.
- Export structured datasets in CSV and JSON formats.

### Technologies

- Python 3.10+
- Requests
- Beautiful Soup 4
- CSV and JSON
- Git and GitHub

### Data Source

[Books to Scrape](https://books.toscrape.com/), a website designed for scraping practice.

### Project Structure

```text
.
├── scraper.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   ├── books.csv
│   └── books.json
├── logs/
│   └── scraper.log
└── tests/
    └── test_scraper.py
```

### Installation

1. Clone this repository.
2. Create a virtual environment.
3. Install the dependencies.

```bash
python -m venv .venv
```

On Windows:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
```

### Usage

Run the scraper from the project root:

```bash
python scraper.py
```

The output files are written to the `data/` directory.


Run the test scraper from the project root:

```bash
python -m unittest discover -s tests -v
```


### Dataset Fields

| Field        | Description         |
| ------------ | ------------------- |
| title        | Product title       |
| price        | Numeric price       |
| currency     | Currency code       |
| rating       | Rating from 1 to 5  |
| availability | Availability text   |
| product_url  | URL of the product  |
| source_page  | Listing page number |

### Error Handling and Data Quality

The scraper uses request timeouts, retries for selected transient HTTP errors, logging, duplicate detection, field validation, and a minimum record-count check.

### Results

- Unique records collected: 100
- CSV output: `data/books-list.csv`
- JSON output: `data/books-list.json`


### Limitations

The scraper targets a specific HTML structure. Website changes may require selector updates. This project is designed for static HTML and does not handle JavaScript-rendered pages.

### Responsible Scraping

Use the project only against sources that permit automated access. Respect applicable terms, access restrictions, rate limits, and privacy requirements.

### Future Improvements

- Automated unit tests
- Configurable target URL and page limit
- Structured error reports
- Data-quality summary
- Support for additional permitted data sources

