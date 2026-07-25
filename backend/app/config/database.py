from pymongo import MongoClient
from app.config.settings import MONGODB_URL, DATABASE_NAME

client = MongoClient(MONGODB_URL)

db = client[DATABASE_NAME]

users_collection = db["users"]
analysis_collection = db["analysis"]