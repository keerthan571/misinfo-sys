from fastapi import APIRouter, Depends
from datetime import datetime, timedelta

from app.database.mongodb import (
    analysis_collection,
    reports_collection
)

from app.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(
    current_user=Depends(get_current_user)
):

    # Logged-in user's filter
    user_filter = {
        "email": current_user["email"]
    }

    # ---------------- DEBUG ----------------
    print("\n========== DASHBOARD DEBUG ==========")
    print("Current User :", current_user["email"])
    print("Database     :", analysis_collection.database.name)
    print("Collection   :", analysis_collection.name)
    # ---------------------------------------

    # Total analyses
    total = analysis_collection.count_documents(user_filter)

    # Verified False
    fake = analysis_collection.count_documents({
        **user_filter,
        "fact_verification.verdict": "False"
    })

    # Verified True
    real = analysis_collection.count_documents({
        **user_filter,
        "fact_verification.verdict": "True"
    })

    # OCR uploads
    ocr = analysis_collection.count_documents({
        **user_filter,
        "ocr.used": True
    })

    # Reports
    reports = reports_collection.count_documents(user_filter)

    # -----------------------------
    # Average AI Confidence
    # -----------------------------
    analyses = list(
        analysis_collection.find(
            user_filter,
            {
                "detection.confidence": 1
            }
        )
    )

    confidence_values = []

    for analysis in analyses:

        confidence = (
            analysis
            .get("detection", {})
            .get("confidence")
        )

        if isinstance(confidence, (int, float)) and confidence > 0:
            confidence_values.append(confidence)

    if confidence_values:
        avg = round(
            sum(confidence_values) /
            len(confidence_values),
            2
        )
    else:
        avg = 0

    # -----------------------------
    # Weekly Analysis
    # -----------------------------
    today = datetime.utcnow()

    start_of_week = today - timedelta(days=today.weekday())

    week_days = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun"
    ]

    weekly_analysis = []

    for i in range(7):

        current_day = start_of_week + timedelta(days=i)

        start = current_day.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        end = start + timedelta(days=1)

        count = analysis_collection.count_documents({
            **user_filter,
            "analysis_time": {
                "$gte": start.isoformat(),
                "$lt": end.isoformat()
            }
        })

        weekly_analysis.append({
            "day": week_days[i],
            "count": count
        })

    # ---------------- DEBUG ----------------
    print("Total Analyses      :", total)
    print("Verified False      :", fake)
    print("Verified True       :", real)
    print("OCR Uploads         :", ocr)
    print("Reports             :", reports)
    print("Average Confidence  :", avg)
    print("=====================================\n")
    # ---------------------------------------

    return {
        "totalAnalyses": total,
        "verifiedTrue": real,
        "verifiedFalse": fake,
        "ocrUploads": ocr,
        "reports": reports,
        "avgConfidence": avg,
        "weeklyAnalysis": weekly_analysis
    }


@router.get("/recent")
def get_recent_activity(
    current_user=Depends(get_current_user)
):

    user_filter = {
        "email": current_user["email"]
    }

    analyses = list(
        analysis_collection.find(
            user_filter,
            {
                "_id": 0,
                "text": 1,
                "analysis_time": 1,
                "fact_verification.verdict": 1,
                "detection.confidence": 1
            }
        )
        .sort("analysis_time", -1)
        .limit(5)
    )

    recent = []

    for analysis in analyses:

        text = analysis.get("text", "")

        if len(text) > 60:
            text = text[:60] + "..."

        recent.append({
            "text": text,
            "verdict": analysis.get("fact_verification", {}).get("verdict", "Unknown"),
            "confidence": analysis.get("detection", {}).get("confidence", 0),
            "analysis_time": analysis.get("analysis_time")
        })

    return recent