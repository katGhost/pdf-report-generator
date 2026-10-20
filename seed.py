"""Load the books.json from database/ extracting required fields
   and seed into the database.
"""
import json
import os
from pathlib import Path
from typing import Any
try:
    from .utils import parse_price, text2number
except ImportError:
    from utils import parse_price, text2number
from models import Book


# Declare base path -> data
BASE_DIR = Path(__file__).resolve().parent
BOOKS_FILE = BASE_DIR / "database" / "books.json"


def get_books() -> list[dict[str, Any]]:
    """Load books from JSON and extract the required fields."""
    with BOOKS_FILE.open("r", encoding="utf-8") as file:
        books_list = json.load(file)

    extracted: list[dict[str, Any]] = []

    # extract required fields
    for book in books_list:
        title = book.get("title")
        price = book.get("price_text")
        rating = book.get("rating_text")
        url = book.get("product_url")

        # clean the data
        extracted.append({
            "title": title,
            "price": parse_price(price),
            "rating": text2number(rating),
            "product_url": url,
        })
    return extracted


#  seeding the JSON data to a database
def initialize_table(target, connection, **kw):
    """Seed records when the SQLAlchemy table is created."""
    books = get_books()

    if not books:
        return

    connection.execute(target.insert(), books)


__all__ = ["get_books", "initialize_table"]

