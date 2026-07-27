from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://127.0.0.1:27017"
)

client = MongoClient(MONGO_URI)

db = client["misinformation_db"]

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


def get_database():
    return db