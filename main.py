
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select
from database.database import engine, Base
from sqlalchemy.orm import Session
from models import Book
from seed import get_books


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


@app.get("/health")
async def health():
    return {"status": "ok"}
