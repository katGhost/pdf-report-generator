from database.database import engine
from sqlalchemy.orm import Session
from sqlalchemy import text
from models import Report



def reset_db():
    with Session(engine) as session:
        session.execute(text("DELETE FROM reports"))
        session.commit()


if __name__ == "__main__":
    reset_db()