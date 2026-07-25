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

# Member 1 owned collections only

analyses_collection = db["analyses"]

ocr_history_collection = db["ocr_history"]

reports_collection = db["reports"]

spread_predictions_collection = db["spread_predictions"]


def get_database():
    return db