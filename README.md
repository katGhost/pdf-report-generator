# PDF Report Generator

A FastAPI API that queries a SQLite book dataset, aggregates it with SQL, renders the results into a styled PDF report using
[Playwright](https://playwright.dev) and headless Chromium, and serves the file by link.

## Dataset

Books dataset scraped from [books.toscrape.com](http://books.toscrape.com) — 1000 books with title, price, rating, and URL. Cleaned to floats on price and integers on rating.

## Project Structure

```plaintext
pdf-report-generator/
├── database/
│   ├── books.json       # Source dataset from previous scraper task
│   ├── database.py      # Database engine and session management
│   └── reports.db       # Generated — not committed to Git
├── reports/             # Generated PDFs — not committed to Git
├── main.py              # FastAPI app and endpoints
├── models.py            # SQLAlchemy models (Book, Report)
├── reports.py           # SQL queries and HTML/PDF generation
├── schemas.py           # Pydantic schemas
├── seed.py              # Seeds books.json into the database
├── utils.py             # Price and rating cleaning helpers
├── requirements.txt
└── README.md
```

## How to Run

```bash
git clone https://github.com/katghost/pdf-report-generator
cd pdf-report-generator

# Create and activate virtual environment
python -m venv .venv
source .venv/Scripts/activate      # bash
.\.venv\Scripts\Activate.ps1       # PowerShell

# Install dependencies
pip install -r requirements.txt

# Install Playwright's Chromium browser
playwright install chromium

# Start the API (books are seeded automatically on startup)
uvicorn main:app --reload
```

## Aggregation SQL

```sql
-- Total revenue
SELECT COALESCE(SUM(price), 0) FROM books;

-- Total number of books
SELECT COUNT(*) FROM books;

-- Average book price
SELECT AVG(price) FROM books;

-- Top 5 most expensive books
SELECT id, title, url, price, rating
FROM books
ORDER BY price DESC
LIMIT 5;

-- Books per star rating
SELECT rating, COUNT(*) AS book_count
FROM books
GROUP BY rating
ORDER BY rating;
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/reports` | Generate a new PDF report (idempotent — one per day) |
| `POST` | `/reports?force=true` | Force a fresh report regardless of today's existing one |
| `GET` | `/reports/{id}` | Get report record by ID |
| `GET` | `/reports/{id}/file` | Download the PDF file |

## POST → Download Proof

```bash
# Generate a report
curl -X POST http://localhost:8000/reports
# {"id":1,"file":"/reports/1/file"}

# Download the PDF
curl -o my-report.pdf http://localhost:8000/reports/1/file
```

## Idempotency

**What the check protects against:**
Duplicate report generation from the same request being sent twice — whether from a double-click, a network retry, or an impatient user refreshing the page.

**Real-World Example:**
A payment processor missing this check could charge a customer twice for one transaction — every duplicate costs the business a refund, a dispute fee, and customer trust.

## When to Move This Out of the Request

The PDF generation pipeline runs synchronously inside the endpoint and takes 2–3 seconds per request. This is acceptable for a single user — but under load, or for larger datasets, this would be moved into a background job queue so the endpoint returns immediately with a job ID, and the client polls for completion.

## Author

**Andries N Mogashoa** | Backend AI Engineer Intern @ FlyRank.ai | CS50AI Student
