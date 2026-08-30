from fastapi import APIRouter, Depends
from datetime import datetime, timedelta

from app.database.mongodb import (
    analysis_collection,
    reports_collection
)

from app.auth.dependencies import get_current_user


router = APIRouter()


def normalize_verdict(verdict):
    """
    Convert all possible database verdict formats
    into dashboard-friendly values.
    """

    if not verdict:
        return "Unknown"

    verdict = str(verdict).lower().strip()


    # TRUE cases
    if verdict in [
        "true",
        "verified true",
        "verified information",
        "verified",
        "real",
        "correct"
    ]:
        return "Verified True"


    # FALSE cases
    if verdict in [
        "false",
        "verified false",
        "false information",
        "misinformation",
        "fake information",
        "fake",
        "misleading"
    ]:
        return "Verified False"


    return "Unknown"



# =====================================================
# DASHBOARD STATS
# =====================================================

@router.get("/stats")
def get_dashboard_stats(current_user=Depends(get_current_user)):

    user_filter = {
        "email": current_user["email"]
    }

    total = analysis_collection.count_documents(user_filter)

    analyses = list(
        analysis_collection.find(
            user_filter,
            {
                "fact_verification.verdict": 1,
                "detection.confidence": 1,
                "analysis.ocr.used": 1,
                "ocr.used": 1
            }
        )
    )
    
    verified_true = 0
    verified_false = 0
    confidence_values = []
    ocr_uploads = 0

    for analysis in analyses:

        verdict = normalize_verdict(
            analysis.get("fact_verification", {}).get("verdict", "")
        )

        if verdict == "Verified True":
            verified_true += 1
        elif verdict == "Verified False":
            verified_false += 1

        confidence = analysis.get("detection", {}).get("confidence")

        if isinstance(confidence, (int, float)):
            confidence_values.append(confidence)

        # OCR Count
        ocr_used = (
            analysis.get("ocr", {}).get("used")
            or
            analysis.get("analysis", {}).get("ocr", {}).get("used")
        )

        if ocr_used:
            ocr_uploads += 1

    avg_confidence = (
        round(sum(confidence_values) / len(confidence_values), 2)
        if confidence_values
        else 0
    )

    today = datetime.utcnow()
    start_of_week = today - timedelta(days=today.weekday())

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekly_analysis = []

    for i in range(7):

        current_day = start_of_week + timedelta(days=i)

        start = current_day.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
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
            "day": days[i],
            "count": count
        })

    return {
        "totalAnalyses": total,
        "verifiedTrue": verified_true,
        "verifiedFalse": verified_false,
        "ocrUploads": ocr_uploads,
        "avgConfidence": avg_confidence,
        "weeklyAnalysis": weekly_analysis
    }

# =====================================================
# RECENT ACTIVITY
# =====================================================

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

        .sort(
            "analysis_time",
            -1
        )

        .limit(5)

    )

    recent = []

    for doc in analyses:
    
        analysis = doc.get("analysis", {})

        verdict = normalize_verdict(
            analysis.get("fact_verification", {}).get("verdict", "")
        )

        if verdict == "Verified True":
            verified_true += 1
        elif verdict == "Verified False":
            verified_false += 1

        confidence = analysis.get("detection", {}).get("confidence")

        if isinstance(confidence, (int, float)):
            confidence_values.append(confidence)

        vision = analysis.get("vision", {})

        if vision.get("used"):
            ocr_uploads += 1

    return recent