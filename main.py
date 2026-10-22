import os
import asyncio
import sys
from functools import partial
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from sqlalchemy import select
from database.database import engine, Base
from sqlalchemy.orm import Session
from models import Book, Report
from seed import get_books
from reports import get_report, build_report_html, generate_pdf
from reports import REPORTS_DIR


# if sys.platform == "win32":
#     asyncio.set_event_loop_policy(
#         asyncio.WindowsProactorEventLoopPolicy()
#     )

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

"""

    
    Path(__file__).with_name("report.html").write_text(html, encoding="utf-8")
    return HTMLResponse(content=html)
"""

@app.post("/reports", status_code=201)
async def create_report():
    report_data = get_report()
    html = build_report_html(report_data)

    # Insert row first to get the auto-generated ID
    with Session(engine) as session:
        report = Report(path="")  # temporary placeholder
        session.add(report)
        session.flush()  # writes to DB, gets ID, without committing yet
        report_id = report.id

        # Got the ID, build the real path
        pdf_path = REPORTS_DIR / f"{report_id}.pdf"
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        # await generate_pdf(html, pdf_path)
        await asyncio.get_event_loop().run_in_executor(
            None, partial(generate_pdf, html, pdf_path)
        )

        # Update the path now that the file exists
        report.path = str(pdf_path)
        session.commit()

    return JSONResponse(
        status_code=201,
        content={
            "id": report_id,
            "file": f"/reports/{report_id}/file",
        }
    )

# report per id
@app.get("/reports/{id}")
async def get_report_by_id(id: int):
    with Session(engine) as session:
        report = session.get(Report, id)

    # 404 for non-existence id
    if report is None:
        return JSONResponse(status_code=404, content={"detail": "Report not found"})

    return {"id": report.id, "path": report.path}

# Serve the PDF file from disk 
@app.get("/reports/{id}/file")
async def serve_from_disk(id: int):
    with Session(engine) as session:
        report = session.get(Report, id)

    # 404 for non-existence id
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        path=report.path,
        media_type="application/pdf",
        filename=f"report_{id}.pdf",
    )
 

# Health status
@app.get("/health")
async def health():
    return {"status": "ok"}
