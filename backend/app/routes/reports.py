from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.services.reports.report_service import ReportService
from app.services.reports.pdf_generator import PDFGenerator
from app.services.reports.csv_generator import CSVGenerator
from app.services.reports.report_storage import ReportStorage

router = APIRouter()

report_service = ReportService()
pdf_generator = PDFGenerator()
csv_generator = CSVGenerator()
storage = ReportStorage()


@router.get("/")
def list_reports():

    return {
        "reports": storage.list_reports(),
    }


@router.get("/{report_id}")
def get_report(report_id: str):

    filename = f"{report_id}.json"

    if not storage.exists(filename):
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    return storage.load_json(filename)


@router.delete("/{report_id}")
def delete_report(report_id: str):

    filename = f"{report_id}.json"

    if not storage.exists(filename):
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    storage.delete(filename)

    return {
        "message": "Report deleted successfully."
    }


@router.get("/{report_id}/pdf")
def generate_pdf(report_id: str):

    filename = f"{report_id}.json"

    if not storage.exists(filename):
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    report = storage.load_json(filename)

    pdf_path = Path("reports") / f"{report_id}.pdf"

    pdf_generator.generate(
        report,
        str(pdf_path),
    )

    return {
        "file": str(pdf_path)
    }


@router.get("/{report_id}/csv")
def generate_csv(report_id: str):

    filename = f"{report_id}.json"

    if not storage.exists(filename):
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    report = storage.load_json(filename)

    csv_path = Path("reports") / f"{report_id}.csv"

    csv_generator.generate(
        report,
        str(csv_path),
    )

    return {
        "file": str(csv_path)
    }