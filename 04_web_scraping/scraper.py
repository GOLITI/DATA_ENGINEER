import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone


BASE_URL = "http://books.toscrape.com/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

DELAY_BETWEEN_REQUESTS = 0.5


def fetch_page(url: str) -> str:
    """Télécharge le HTML d'une page."""
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.text


def parse_rating(article) -> int | None:
    """Extrait la note (1-5) depuis la classe CSS."""
    rating_class = article.select_one("p.star-rating")["class"]
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    return next((rating_map[c] for c in rating_class if c in rating_map), None)


def parse_catalogue_page(html: str, page_url: str) -> list[dict]:
    """Extrait les livres d'une page catalogue."""
    soup = BeautifulSoup(html, "lxml")
    books = []
    scraped_at = datetime.now(timezone.utc)

    for article in soup.select("article.product_pod"):
        title = article.select_one("h3 a")["title"]

        price_text = article.select_one("p.price_color").text
        price_match = re.search(r"[\d.]+", price_text)
        price = float(price_match.group()) if price_match else 0.0

        rating = parse_rating(article)
        stock = article.select_one("p.instock.availability").text.strip()

        relative_url = article.select_one("h3 a")["href"]
        product_url = urljoin(page_url, relative_url)

        match = re.search(r"catalogue/([^/]+)/", product_url)
        book_id = match.group(1) if match else product_url

        books.append({
            "book_id": book_id,
            "title": title,
            "price": price,
            "rating": rating,
            "stock": stock,
            "product_url": product_url,
            "source": "books.toscrape.com",
            "scraped_at": scraped_at,
        })

    return books


def scrape_catalogue(max_pages: int = 25) -> list[dict]:
    """Scrape N pages du catalogue (25 pages = 500 livres)."""
    all_books = []
    url = BASE_URL
    page = 1

    while page <= max_pages:
        print(f"  Page {page} : {url}")
        try:
            html = fetch_page(url)
        except Exception as e:
            print(f"    Erreur : {e}")
            break

        books = parse_catalogue_page(html, url)
        all_books.extend(books)
        print(f"    {len(books)} livres (cumul : {len(all_books)})")

        soup = BeautifulSoup(html, "lxml")
        next_link = soup.select_one("li.next a")
        if not next_link:
            print("    Pas de page suivante.")
            break

        url = urljoin(url, next_link["href"])
        page += 1
        time.sleep(DELAY_BETWEEN_REQUESTS)

    return all_books


if __name__ == "__main__":
    print("=== Scraping de 500 livres ===")
    start = time.time()

    books = scrape_catalogue(max_pages=25)
    print(f"\n{len(books)} livres extraits.")

    print("\n--- Aperçu ---")
    for b in books[:5]:
        print(f"  {b['title'][:45]:<45} | £{b['price']:>6.2f} | {b['rating']}★")

    # Stockage MongoDB
    print("\n=== Stockage MongoDB ===")
    from database import insert_books, count_books
    result = insert_books(books)
    print(f"  {result['inserted']} insérés, {result['duplicates']} doublons ignorés.")
    print(f"  Total en base : {count_books()} livres.")

    duration = time.time() - start
    print(f"\nTerminé en {duration:.1f} secondes.")