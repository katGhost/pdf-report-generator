
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from database.database import engine, Base
from sqlalchemy.orm import Session
from models import Book
from seed import get_books
from reports import get_report, build_report_html


def seed_books():
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        existing_book = session.scalar(select(Book.id).limit(1))

        if existing_book is not None:
            return

        books = get_books()
        if books:
            session.add_all([Book(**book) for book in books])
            session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_books()
    yield


app = FastAPI(lifespan=lifespan)



@app.get("/reports")
async def reports() -> HTMLResponse:
    report_data = get_report()
    html = build_report_html(report_data)
    Path(__file__).with_name("report.html").write_text(html, encoding="utf-8")
    return HTMLResponse(content=html)

@app.get("/health")
async def health():
    return {"status": "ok"}
