
import requests
from bs4 import BeautifulSoup

url = "https://books.toscrape.com/"

headers = {
    "User-Agent": "LearningWebScraper/1.0"
}

response = requests.get(
    url,
    headers=headers,
    timeout=20
)

response.raise_for_status()

print("HTTP status:", response.status_code)

soup = BeautifulSoup(response.content, "html.parser")

# 1. Find all book containers
books = soup.select("article.product_pod")
print("Book containers:", len(books))

# 2. Inspect the first book
if books:
    book = books[0]

    title_element = book.select_one("h3 a")
    price_element = book.select_one(".price_color")
    availability_element = book.select_one(".availability")
    rating_element = book.select_one(".star-rating")

    print("Title:", title_element.get("title")
          if title_element else None)

    print("Price:", price_element.get_text(strip=True)
          if price_element else None)

    print("Availability:",
          availability_element.get_text(" ", strip=True)
          if availability_element else None)

    print("Rating classes:",
          rating_element.get("class")
          if rating_element else None)

# 3. Inspect the next-page link
next_link = soup.select_one("li.next a")

print("Next page:",
      next_link.get("href") if next_link else None)
