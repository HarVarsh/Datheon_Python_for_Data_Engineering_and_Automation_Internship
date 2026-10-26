
import csv
import json
import logging
import re
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urljoin
import logging

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Create the logs directory if it does not exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "scraper.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ],
    force=True
)


# -------------------- Configuration --------------------

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
OUTPUT_DIR = Path("data")
MIN_RECORDS = 100
MAX_PAGES = 10
REQUEST_DELAY = 1

HEADERS = {
    "User-Agent": "LearningWebScraper/1.0 (educational project)"
}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# -------------------- HTTP Session --------------------

def create_session():
    session = requests.Session()
    session.headers.update(HEADERS)

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


# -------------------- Data Cleaning --------------------

def clean_price(price_text):
    """Convert a price such as '£51.77' to a numeric value."""
    if not price_text:
        return None

    cleaned = re.sub(r"[^\d.]", "", price_text)

    try:
        return float(Decimal(cleaned))
    except (InvalidOperation, ValueError):
        logging.exception("Unexpected error - Invalid Operation or Value Error")
        return None


def get_rating(card):
    """Convert a star-rating CSS class to a number."""
    rating_element = card.select_one(".star-rating")

    if not rating_element:
        return None

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    for word, score in rating_map.items():
        if word in rating_element.get("class", []):
            return score

    return None


# -------------------- Page Extraction --------------------

def scrape_page(session, page_number):
    url = BASE_URL.format(page_number)

    response = session.get(url, timeout=(5, 20))
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    cards = soup.select("article.product_pod")

    if not cards:
        raise ValueError(
            f"No product cards found on page {page_number}. "
            "Check the URL and HTML selectors."
        )

    records = []

    for card in cards:
        title_element = card.select_one("h3 a")
        price_element = card.select_one(".price_color")
        availability_element = card.select_one(".availability")

        if not title_element or not price_element:
            logging.warning(
                "Skipping incomplete record on page %s",
                page_number
            )
            continue

        title = title_element.get("title", "").strip()

        product_url = urljoin(
            url, title_element.get("href", "")
        )

        price = clean_price(
            price_element.get_text(strip=True)
        )

        if not title or price is None:
            logging.warning("Skipping invalid record: %s", title)
            continue

        availability = (
            availability_element.get_text(" ", strip=True)
            if availability_element else None
        )

        records.append({
            "title": title,
            "price": price,
            "currency": "GBP",
            "rating": get_rating(card),
            "availability": availability,
            "product_url": product_url,
            "source_page": page_number
        })

    return records


# -------------------- Pagination --------------------

def scrape_catalogue():
    session = create_session()
    all_records = []
    seen_urls = set()

    try:
        for page_number in range(1, MAX_PAGES + 1):
            logging.info("Scraping page %s", page_number)

            try:
                page_records = scrape_page(
                    session, page_number
                )
            except (requests.RequestException, ValueError) as exc:
                logging.error(
                    "Stopping at page %s: %s",
                    page_number, exc
                )
                break

            new_count = 0

            for record in page_records:
                key = record["product_url"]

                if key not in seen_urls:
                    seen_urls.add(key)
                    all_records.append(record)
                    new_count += 1

            logging.info(
                "Page %s: %s records; %s new unique records",
                page_number, len(page_records), new_count
            )

            # Stop if the page contains no new records.
            if new_count == 0:
                logging.warning("No new records; stopping.")
                break

            if len(all_records) >= MIN_RECORDS:
                break

            time.sleep(REQUEST_DELAY)

    finally:
        session.close()

    return all_records


# -------------------- Export --------------------

def export_data(records):
    if not records:
        raise RuntimeError("No records collected; nothing to export.")

    csv_path = OUTPUT_DIR / "books-list.csv"
    json_path = OUTPUT_DIR / "books-list.json"

    fieldnames = list(records[0].keys())

    with csv_path.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(records)

    with json_path.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(
            records, file, indent=4, ensure_ascii=False
        )

    logging.info("CSV saved: %s", csv_path)
    logging.info("JSON saved: %s", json_path)


# -------------------- Main Program --------------------

def main():
    records = scrape_catalogue()

    logging.info("Total unique records: %s", len(records))

    if len(records) < MIN_RECORDS:
        logging.error(
            "Target not met: collected %s of at least %s records.",
            len(records), MIN_RECORDS
        )
        if records:
            export_data(records)
        raise SystemExit(1)

    export_data(records)

    logging.info("SUCCESS: minimum record target achieved.")
    logging.info("CSV and JSON exports are ready.")
    logging.info("================= Scraping Task Completed ===================\n")

if __name__ == "__main__":
    main()
