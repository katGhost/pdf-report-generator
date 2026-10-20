from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from database.database import Base


# book class
class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    product_url: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)
    rating: Mapped[float] = mapped_column(Float)