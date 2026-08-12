from pymongo import MongoClient
from app.config.settings import MONGODB_URL, DATABASE_NAME


# ======================================================
# MongoDB Connection
# ======================================================

client = MongoClient(MONGODB_URL)

db = client[DATABASE_NAME]


# ======================================================
# Collections
# ======================================================

# Main analysis history
analysis_collection = db["analysis"]
analyses_collection = analysis_collection

# OCR history
ocr_collection = db["ocr_history"]
ocr_history_collection = ocr_collection

# Reports
reports_collection = db["reports"]

# Spread prediction history
prediction_collection = db["spread_predictions"]
spread_predictions_collection = prediction_collection


# ======================================================
# Database Getter
# ======================================================

def get_database():
    return db