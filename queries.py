from sqlalchemy import text
from sqlalchemy.orm import Session
from database.database import engine
import json

# Total revenue
def get_report():
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
            text("SELECT * FROM books ORDER BY price DESC LIMIT 5")
        ).all()
        
        # Number of books per star rating
        books_per_rating = session.execute(
            text("SELECT rating, COUNT(*) FROM books GROUP BY rating ORDER BY rating")
        ).all()
        

        results = {
            "total_revenue": total_revenue,
            "total_books": book_count,
            "average_book_price": average_price,
            "top_five_most_expensive": most_expensive,
            "books_per_rating": books_per_rating,
        }
        
        return results


