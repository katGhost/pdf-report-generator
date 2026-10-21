from datetime import date
from html import escape
from typing import Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from database.database import engine
from playwright.sync_api import sync_playwright
from seed import BASE_DIR


REPORTS_DIR = BASE_DIR / "reports"

# Total revenue
def get_report() -> dict[str, Any]:
    with Session(engine) as session:
        
        # Total revenue
        total_revenue = session.execute(
            text("SELECT COALESCE(SUM(price), 0) FROM books")
        ).scalar_one()

        # Total number of books
        book_count = session.execute(
            text("SELECT COUNT(*) FROM books")
        ).scalar_one()
        
        # Average price -> per book?
        average_price = session.execute(
            text("SELECT AVG(price) FROM books")
        ).scalar_one()
        
        # Top five most expensive books
        most_expensive = session.execute(
            text("""
                SELECT id, title, url, price, rating
                FROM books
                ORDER BY price DESC
                LIMIT 5
            """)
        ).mappings().all()
        
        # Number of books per star rating
        books_per_rating = session.execute(
            text("""
                SELECT rating, COUNT(*) AS book_count
                FROM books
                GROUP BY rating
                ORDER BY rating
            """)
        ).mappings().all()
        

        results = {
            "total_revenue": total_revenue,
            "total_books": book_count,
            "average_book_price": average_price,
            "top_five_most_expensive": [dict(row) for row in most_expensive],
            "books_per_rating": [dict(row) for row in books_per_rating],
        }

        return results
    
# Save aggregated report results to pdf
def build_report_html(report_data: dict) -> str:
    
    with Session(engine) as session:
        all_books = list(session.execute(
            text("""
                SELECT *
                FROM books
            """)
        ).mappings())
    
    today = date.today().strftime("%B %d, %Y")

    totals = {
        "Total revenue": f"£{report_data['total_revenue']:.2f}",
        "Total books": str(report_data["total_books"]),
        "Average book price": f"£{report_data['average_book_price']:.2f}",
    }

    total_cards = "\n".join(
        f"<article class=\"total-card\"><h2>{escape(label)}</h2>"
        f"<p>{escape(value)}</p></article>"
        for label, value in totals.items()
    )

    expensive_rows = "\n".join(
        f"<tr><td>{escape(book['title'])}</td><td>£{book['price']:.2f}</td>"
        f"<td>{'★' * int(book['rating'])}</td></tr>"
        for book in report_data["top_five_most_expensive"]
    )

    rating_rows = "\n".join(
        f"<tr><td>{'★' * int(row['rating'])}</td><td>{row['book_count']}</td></tr>"
        for row in report_data["books_per_rating"]
    )

    all_book_rows = "\n".join(
        f"<tr><td>{escape(book['title'])}</td><td>{escape(book['url'])}</td>"
        f"<td>£{book['price']:.2f}</td><td>{'★' * int(book['rating'])}</td></tr>"
        for book in all_books
    )

    return f"""<!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Book Report — {today}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2rem; color: #222; }}

            h1 {{ font-size: 1.5rem; margin-bottom: 0.25rem; }}
            .report-date {{ color: #666; font-size: 0.875rem; margin-bottom: 2rem; }}

            .totals {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 2rem; }}
            .total-card {{ padding: 1rem; min-width: 12rem; background: #f1f5f9; border-radius: 8px; }}
            .total-card h2 {{ font-size: 0.875rem; margin: 0 0 .5rem; color: #555; }}
            .total-card p {{ font-size: 1.5rem; margin: 0; font-weight: bold; }}

            table {{ width: 100%; border-collapse: collapse; margin-bottom: 2rem; }}
            thead {{ background: #1e293b; color: #fff; }}
            th, td {{ padding: 0.5rem 0.75rem; text-align: left; border-bottom: 1px solid #e2e8f0; }}
            tr {{ break-inside: avoid; }}

            @media print {{
                body {{ margin: 1rem; }}
            }}
        </style>
    </head>
    <body>
        <h1>Book Report</h1>
        <p class="report-date">{today}</p>

        <section class="totals">{total_cards}</section>

        <h2>Top 5 Most Expensive Books</h2>
        <table>
            <thead><tr><th>Title</th><th>Price</th><th>Rating</th></tr></thead>
            <tbody>{expensive_rows}</tbody>
        </table>

        <h2>Books per Star Rating</h2>
        <table>
            <thead><tr><th>Rating</th><th>Count</th></tr></thead>
            <tbody>{rating_rows}</tbody>
        </table>

        <h2>All Books</h2>
        <table>
            <thead><tr><th>Title</th><th>URL</th><th>Price</th><th>Rating</th></tr></thead>
            <tbody>{all_book_rows}</tbody>
        </table>
    </body>
    </html>"""
    

def generate_pdf():
    html_content = build_report_html(get_report())
    
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.set_content(html=html_content)
        page.pdf(
            path=f'{REPORTS_DIR}/test.pdf',
            format='A4',
            margin={
                "top": "20mm",
                "bottom": "20mm"
            },
            print_background=True,
        )

if __name__ == "__main__":
    generate_pdf()
