from pymongo import MongoClient
from app.config.settings import MONGODB_URL, DATABASE_NAME

print("MONGODB_URL STATUS:",
      "SET" if MONGODB_URL else "MISSING")

if MONGODB_URL:
    print("MONGODB_URL PREFIX:", MONGODB_URL[:14])

client = MongoClient(MONGODB_URL)

db = client[DATABASE_NAME]

users_collection = db["users"]
analysis_collection = db["analysis"]